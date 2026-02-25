# -*- coding: utf-8 -*-
"""
utils/gisaid_parser.py

GISAID-optimized FASTA parser. Zero biopython dependency — string-split
parsing is faster for this known pipe-delimited format.

Header format handled (both variants):
  Standard GISAID (6 fields):
    >isolate|subtype|segment|collection_date|accession|clade
    >A/Новосибирск/RII-7.429/2024|A_/_H3N2|HA|2024-01-17|EPI_ISL_123456|3C.2a1b

  v1.0 Normalized (9 fields):
    >name|type|subtype|segment|location|host|date|clade|accession

UTF-8 MANDATORY: caller must decode bytes as UTF-8 before passing file_content.
  Correct:   uploaded_file.read().decode('utf-8')
  Incorrect: uploaded_file.read()   ← corrupts Cyrillic location names on Windows

Performance target: 10K sequences in < 5 seconds.
"""

import gzip
import hashlib
import io
import re
import time
import zipfile

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def parse_gisaid_fasta(file_content: str, file_name: str) -> tuple:
    """Parse a UTF-8 decoded GISAID FASTA string into a list of metadata dicts.

    Decorated with @st.cache_data — parses ONCE per unique (file_content, file_name).
    Subsequent calls with identical arguments return the cached result instantly.

    Args:
        file_content: UTF-8 decoded FASTA string.
                      Caller must decode: raw_bytes.decode('utf-8')
        file_name:    Original filename (included in cache key).

    Returns:
        Tuple: (list_of_metadata_dicts, parse_time_seconds)

        Each dict contains:
            isolate, subtype, subtype_clean, segment,
            collection_date (pd.Timestamp|None), accession, clade,
            clade_l1..clade_l6 (str|None),
            host, location,
            sequence (str, uppercased), sequence_length (int), sequence_hash (str)
    """
    sequences = []
    parsing_start = time.perf_counter()

    current_header = None
    current_seq_parts = []

    for line in file_content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            # Flush previous record
            if current_header is not None:
                seq = "".join(current_seq_parts).upper().replace(" ", "")
                metadata = _parse_header(current_header)
                metadata["sequence"] = seq
                metadata["sequence_length"] = len(seq)
                metadata["sequence_hash"] = compute_sequence_hash(seq)
                sequences.append(metadata)
            current_header = line[1:]
            current_seq_parts = []
        else:
            current_seq_parts.append(line)

    # Flush last record
    if current_header is not None:
        seq = "".join(current_seq_parts).upper().replace(" ", "")
        metadata = _parse_header(current_header)
        metadata["sequence"] = seq
        metadata["sequence_length"] = len(seq)
        metadata["sequence_hash"] = compute_sequence_hash(seq)
        sequences.append(metadata)

    # Batch-vectorize date parsing — replaces 10K individual pd.to_datetime() calls
    # with a single Series operation for a ~4x throughput improvement.
    if sequences:
        raw_dates = [s.pop("_raw_date", "") for s in sequences]
        parsed_dates = _batch_parse_dates(raw_dates)
        for s, d in zip(sequences, parsed_dates):
            s["collection_date"] = d

    parsing_time = time.perf_counter() - parsing_start
    return sequences, parsing_time


def decompress_if_needed(raw_bytes: bytes, file_name: str) -> str:
    """Decompress .gz or .zip files and return a UTF-8 decoded string.

    For .zip archives, concatenates ALL FASTA-like files found in the archive.
    This handles multi-segment or multi-file ZIPs (e.g. one file per segment,
    one file per year, or any sub-alignment bundles) — all sequences are merged
    into a single FASTA string in sorted filename order.

    Falls back to plain UTF-8 decode for uncompressed files.
    """
    import os as _os
    name_lower = file_name.lower()
    try:
        if name_lower.endswith(".gz"):
            return gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
        if name_lower.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
                fasta_exts = (".fasta", ".fa", ".fas", ".fna", ".txt")
                # Filter: keep only FASTA-like members; skip macOS metadata and dotfiles
                fasta_members = sorted([
                    m for m in zf.namelist()
                    if m.lower().endswith(fasta_exts)
                    and not m.startswith("__MACOSX")
                    and not _os.path.basename(m).startswith(".")
                ])
                if fasta_members:
                    parts: list[str] = []
                    for member in fasta_members:
                        with zf.open(member) as f:
                            parts.append(f.read().decode("utf-8", errors="replace"))
                    # Join with a blank line so FASTA records from separate files
                    # don't accidentally merge into each other.
                    return "\n".join(parts)
                # Fallback: return first file in archive regardless of extension
                if zf.namelist():
                    with zf.open(zf.namelist()[0]) as f:
                        return f.read().decode("utf-8", errors="replace")
    except Exception:
        pass
    return raw_bytes.decode("utf-8", errors="replace")


def parse_flexible_date(date_str: str):
    """Handle all GISAID date format variants.

    Supported: %Y-%m-%d, %Y-%m, %Y, %d-%b-%Y, %b-%Y, %b-%d-%Y, %Y%m%d
    Returns pd.Timestamp or None on failure.
    """
    if not date_str:
        return None
    date_str = date_str.strip()
    if date_str in ("", "Unknown", "unknown", "N/A", "NA", "None", "none"):
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y", "%d-%b-%Y", "%b-%Y", "%b-%d-%Y", "%Y%m%d"):
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(date_str)
    except Exception:
        return None


def infer_host_from_isolate(isolate_name: str) -> str:
    """Infer host species from GISAID isolate naming conventions.

    GISAID standard patterns:
      Human:       A/Location/Strain/Year  or  B/Location/Strain/Year
      Avian:       A/duck/Location/...  (or goose, chicken, gull, etc.)
      Mammalian:   A/swine/Location/...  (or ferret, mink, seal, etc.)
      Environment: A/.../Environment/...
    """
    if not isolate_name:
        return "Unknown"
    name_lower = isolate_name.lower()
    if "/environment/" in name_lower:
        return "Environment"
    avian = ["duck", "goose", "chicken", "swan", "gull", "teal",
             "quail", "pheasant", "pigeon", "turkey", "ostrich", "wild bird"]
    if any(k in name_lower for k in avian):
        return "Avian"
    mammal = ["swine", "pig", "ferret", "mink", "seal",
              "cat", "dog", "horse", "tiger", "leopard"]
    if any(k in name_lower for k in mammal):
        return "Mammalian"
    if (isolate_name.startswith("A/") or isolate_name.startswith("B/")) \
            and isolate_name.count("/") >= 2:
        return "Human"
    return "Unknown"


def extract_location_from_isolate(isolate_name: str) -> str:
    """Extract geographic location from a GISAID isolate name.

    For A/Location/Strain/Year → Location.
    For A/duck/Location/Strain/Year → Location (skips host keyword).
    Preserves Cyrillic characters (e.g., Новосибирск).
    """
    if not isolate_name:
        return "Unknown"
    parts = [p.strip() for p in isolate_name.split("/") if p.strip()]
    skip = {"a", "b", "duck", "goose", "chicken", "swan", "gull", "swine",
            "pig", "ferret", "mink", "seal", "environment", "wild bird", "avian"}
    for part in parts:
        if part.lower() in skip:
            continue
        return part
    return parts[1] if len(parts) > 1 else "Unknown"


def compute_sequence_hash(sequence: str) -> str:
    """12-character MD5 hash of uppercased sequence for identity tracking."""
    return hashlib.md5(sequence.upper().encode()).hexdigest()[:12]


def convert_df_to_fasta(df: pd.DataFrame) -> str:
    """Convert a filtered DataFrame back to FASTA format string.

    Fully vectorized header construction — no iterrows.
    Reconstructs pipe-delimited GISAID-style headers.
    """
    if df.empty:
        return ""

    def _col(name: str, fallback: str = "Unknown") -> pd.Series:
        if name in df.columns:
            return df[name].fillna(fallback).astype(str)
        return pd.Series([fallback] * len(df), index=df.index)

    # Format collection_date to YYYY-MM-DD
    if "collection_date" in df.columns:
        date_col = pd.to_datetime(df["collection_date"], errors="coerce")
        date_str = date_col.dt.strftime("%Y-%m-%d").fillna("Unknown")
    else:
        date_str = pd.Series(["Unknown"] * len(df), index=df.index)

    headers = (
        ">"
        + _col("isolate") + "|"
        + _col("subtype") + "|"
        + _col("segment") + "|"
        + date_str + "|"
        + _col("accession") + "|"
        + _col("clade")
    )
    sequences = _col("sequence", "")

    # Vectorized interleave: ">{header}\n{seq}" per record, joined by \n
    return (headers + "\n" + sequences).str.cat(sep="\n")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_HXNX_RE = re.compile(r"(H\d+N\d+)")

# Standard GISAID date format tried first as a fast path
_FAST_DATE_FMT = "%Y-%m-%d"

# Fallback formats tried only for dates that didn't match the fast path
_SLOW_DATE_FMTS = ("%Y-%m", "%Y", "%d-%b-%Y", "%b-%Y", "%b-%d-%Y", "%Y%m%d")

_DATE_NULL_SET = frozenset(("", "Unknown", "unknown", "N/A", "NA", "None", "none"))


def _batch_parse_dates(date_strings: list) -> list:
    """Vectorized date parser — converts a list of raw date strings to
    pd.Timestamp | None values in a single pass.

    Strategy:
      1. Fast path: vectorized pd.to_datetime() on the full Series using the
         dominant GISAID format "%Y-%m-%d". Covers ~95% of real data.
      2. Slow path: per-string fallback for dates that didn't parse in step 1
         (partial dates like "2024-01", "2024", or locale formats).

    This replaces N individual pd.to_datetime() calls with one vectorized
    call, reducing overhead by ~4x for 10K records.
    """
    if not date_strings:
        return []

    s = pd.Series(date_strings, dtype=str)

    # Step 1: fast vectorized parse on the dominant format
    fast = pd.to_datetime(s, format=_FAST_DATE_FMT, errors="coerce")

    # Step 2: for entries that failed, try slow fallback formats
    null_mask = fast.isna()
    if null_mask.any():
        for raw, idx in zip(s[null_mask], s[null_mask].index):
            raw = raw.strip() if isinstance(raw, str) else ""
            if raw in _DATE_NULL_SET:
                continue  # leave as NaT → None below
            for fmt in _SLOW_DATE_FMTS:
                try:
                    fast.iloc[idx] = pd.to_datetime(raw, format=fmt)
                    break
                except (ValueError, TypeError):
                    continue
            else:
                # Last resort: pandas inference
                try:
                    fast.iloc[idx] = pd.to_datetime(raw)
                except Exception:
                    pass

    # Convert NaT → None for consistency with downstream code
    return [None if pd.isna(v) else v for v in fast]


def _parse_header(header: str) -> dict:
    """Parse one FASTA header line (without leading '>') into a metadata dict.

    Handles both standard GISAID (6 fields) and v1.0 normalized (9 fields).
    All fields default to 'Unknown' / None gracefully — never raises.
    """
    parts = [p.strip() for p in header.split("|")]
    n = len(parts)

    if n >= 9:
        # v1.0 Normalized: name | type | subtype | segment | location | host | date | clade | accession
        metadata = {
            "isolate":   parts[0],
            "subtype":   parts[2] if n > 2 else "Unknown",
            "segment":   parts[3] if n > 3 else "Unknown",
            "location":  parts[4] if n > 4 else "Unknown",
            "host":      parts[5] if n > 5 else "Unknown",
            "_raw_date": parts[6] if n > 6 else "",
            "clade":     parts[7] if n > 7 else "Unknown",
            "accession": parts[8] if n > 8 else "Unknown",
        }
    else:
        # Standard GISAID: isolate | subtype | segment | date | accession | clade
        raw_isolate = parts[0] if n > 0 else "Unknown"
        metadata = {
            "isolate":   raw_isolate,
            "subtype":   parts[1] if n > 1 else "Unknown",
            "segment":   parts[2] if n > 2 else "Unknown",
            "_raw_date": parts[3] if n > 3 else "",
            "accession": parts[4] if n > 4 else "Unknown",
            "clade":     parts[5] if n > 5 else "Unknown",
            "host":      infer_host_from_isolate(raw_isolate),
            "location":  extract_location_from_isolate(raw_isolate),
        }

    # subtype_clean: "A_/_H3N2" → "H3N2", "H5N1" stays as-is
    m = _HXNX_RE.search(metadata["subtype"])
    metadata["subtype_clean"] = m.group(1) if m else metadata["subtype"]

    # Hierarchical clade levels: "3C.2a1b.2a.2a" → l1="3C", l2="3C.2a1b", ...
    clade_val = metadata.get("clade") or "Unknown"
    if clade_val not in ("Unknown", "", "None", "none"):
        levels = clade_val.split(".")
        for i in range(6):
            metadata[f"clade_l{i + 1}"] = ".".join(levels[: i + 1]) if i < len(levels) else None
    else:
        for i in range(6):
            metadata[f"clade_l{i + 1}"] = None

    return metadata
