# -*- coding: utf-8 -*-
"""
utils/vectorized_filters.py

Single-pass boolean mask filtering engine. O(n) not O(n²).
Zero iterrows — all operations via Pandas boolean indexing.

Supported operators: contains, equals, not_equals, starts_with, regex, in_list, date_range
"""

import re

import pandas as pd


class VectorizedFilterEngine:
    """Boolean mask filter combinator for GISAID sequence DataFrames.

    All filter rules are combined into a single boolean mask and applied
    in one DataFrame operation — never in a loop over rows.
    """

    # Supported operators and their arities (for UI validation)
    OPERATORS = {
        "equals":      "scalar",
        "not_equals":  "scalar",
        "contains":    "scalar",
        "not_contains":"scalar",
        "starts_with": "scalar",
        "regex":       "scalar",
        "in_list":     "list",
        "date_range":  "pair",   # value=[start, end] as pd.Timestamp
    }

    def apply_header_component_filters(
        self, df: pd.DataFrame, filter_rules: list
    ) -> pd.DataFrame:
        """Apply a list of filter rules in a single vectorized pass.

        Args:
            df: Active sequence DataFrame.
            filter_rules: List of dicts with keys:
                field    — column name (str)
                operator — one of OPERATORS keys (str)
                value    — scalar | list | [start, end]

        Returns:
            Filtered DataFrame (copy). Input is never modified.
        """
        if df.empty or not filter_rules:
            return df

        # Start with all-True mask
        mask = pd.Series(True, index=df.index)

        for rule in filter_rules:
            field    = rule.get("field", "")
            operator = rule.get("operator", "equals")
            value    = rule.get("value")

            if field not in df.columns:
                continue  # Skip unknown fields silently

            col = df[field]
            rule_mask = self._build_mask(col, operator, value, field)
            if rule_mask is not None:
                mask &= rule_mask

        return df[mask].copy()

    # ------------------------------------------------------------------
    # Individual operator helpers
    # ------------------------------------------------------------------

    def _build_mask(
        self,
        col: pd.Series,
        operator: str,
        value,
        field: str,
    ) -> "pd.Series | None":
        """Build a boolean mask for one filter rule."""

        if operator == "equals":
            return col.astype(str).str.strip() == str(value).strip()

        if operator == "not_equals":
            return col.astype(str).str.strip() != str(value).strip()

        if operator == "contains":
            return col.astype(str).str.contains(
                re.escape(str(value)), case=False, na=False
            )

        if operator == "not_contains":
            return ~col.astype(str).str.contains(
                re.escape(str(value)), case=False, na=False
            )

        if operator == "starts_with":
            return col.astype(str).str.startswith(str(value), na=False)

        if operator == "regex":
            try:
                return col.astype(str).str.contains(
                    str(value), case=False, na=False, regex=True
                )
            except re.error:
                return None  # Invalid regex — skip rule

        if operator == "in_list":
            values = [str(v).strip() for v in (value or [])]
            return col.astype(str).str.strip().isin(values)

        if operator == "date_range":
            try:
                start, end = value[0], value[1]
                dates = pd.to_datetime(col, errors="coerce")
                return (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))
            except Exception:
                return None

        return None  # Unknown operator

    # ------------------------------------------------------------------
    # Field discovery
    # ------------------------------------------------------------------

    def auto_detect_available_fields(
        self, df: pd.DataFrame, sample_size: int = 100
    ) -> dict:
        """Identify which metadata columns are >10% populated.

        Returns dict: {field_name: {populated_pct, n_unique, sample_values}}
        Only populated fields should be shown in the filter UI.
        """
        if df.empty:
            return {}

        result = {}
        sample = df.head(sample_size) if len(df) > sample_size else df

        for col in df.columns:
            if col in ("sequence", "sequence_hash"):
                continue  # Never filter-UI candidates

            non_null = df[col].replace({"Unknown": None, "": None}).dropna()
            populated_pct = 100 * len(non_null) / len(df)

            if populated_pct < 10:
                continue

            sample_vals = (
                sample[col]
                .replace({"Unknown": None, "": None})
                .dropna()
                .astype(str)
                .unique()[:5]
                .tolist()
            )

            result[col] = {
                "populated_pct": round(populated_pct, 1),
                "n_unique":      int(df[col].nunique()),
                "sample_values": sample_vals,
            }

        return result

    # ------------------------------------------------------------------
    # Convenience filters
    # ------------------------------------------------------------------

    def create_hierarchical_clade_filter(
        self, df: pd.DataFrame, clade_pattern: str, level: int = None
    ) -> pd.DataFrame:
        """Filter by clade hierarchy level or prefix match.

        Args:
            clade_pattern: Pattern string, e.g. "3C.2a1b".
            level: If given (1–6), filters on df[f'clade_l{level}'].
                   If None, filters rows where any clade_l* starts with the pattern.
        """
        if df.empty or not clade_pattern:
            return df

        if level is not None:
            col_name = f"clade_l{level}"
            if col_name not in df.columns:
                return df
            mask = df[col_name].astype(str) == clade_pattern
        else:
            # Match against the raw clade column (prefix)
            clade_col = "clade" if "clade" in df.columns else None
            if clade_col is None:
                return df
            mask = df[clade_col].astype(str).str.startswith(clade_pattern, na=False)

        return df[mask].copy()

    def create_subtype_filter(
        self, df: pd.DataFrame, subtype_patterns: list
    ) -> pd.DataFrame:
        """Filter on subtype_clean (preferred) or raw subtype column.

        Args:
            subtype_patterns: List of HxNx strings, e.g. ["H3N2", "H1N1"].
        """
        if df.empty or not subtype_patterns:
            return df

        col = "subtype_clean" if "subtype_clean" in df.columns else "subtype"
        if col not in df.columns:
            return df

        mask = df[col].astype(str).str.strip().isin(
            [p.strip() for p in subtype_patterns]
        )
        return df[mask].copy()

    # ------------------------------------------------------------------
    # Quality filters (called directly from Filter Lab UI)
    # ------------------------------------------------------------------

    def filter_min_length(self, df: pd.DataFrame, min_len: int) -> pd.DataFrame:
        """Keep only sequences >= min_len bases."""
        if "sequence_length" in df.columns:
            return df[df["sequence_length"] >= min_len].copy()
        if "sequence" in df.columns:
            return df[df["sequence"].str.len() >= min_len].copy()
        return df

    def filter_max_n_run(self, df: pd.DataFrame, max_n_run: int) -> pd.DataFrame:
        """Remove sequences containing a run of N >= max_n_run."""
        if "sequence" not in df.columns:
            return df
        pattern = "N" * max_n_run
        mask = ~df["sequence"].str.contains(pattern, case=False, na=False)
        return df[mask].copy()

    def deduplicate(
        self, df: pd.DataFrame, mode: str = "sequence"
    ) -> pd.DataFrame:
        """Remove duplicate sequences.

        Args:
            mode: 'sequence'  — deduplicate on sequence_hash only.
                  'seq+subtype' — deduplicate on (sequence_hash, subtype_clean).
        """
        if df.empty:
            return df

        if mode == "seq+subtype":
            cols = [c for c in ("sequence_hash", "subtype_clean") if c in df.columns]
        else:
            cols = ["sequence_hash"] if "sequence_hash" in df.columns else []

        if not cols:
            return df

        return df.drop_duplicates(subset=cols, keep="first").copy()

    def filter_accessions(
        self, df: pd.DataFrame, accession_list: list
    ) -> pd.DataFrame:
        """Keep only rows whose EPI_ISL accession is in accession_list."""
        if "accession" not in df.columns or not accession_list:
            return df
        clean = [a.strip() for a in accession_list if a.strip()]
        return df[df["accession"].isin(clean)].copy()
