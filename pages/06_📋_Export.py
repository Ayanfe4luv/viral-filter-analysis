# -*- coding: utf-8 -*-
"""
pages/06_📋_Export.py — Consolidated Outputs & Reporting

Features (adapted from fasta_analysis_app_final.py Export tab):
  • Quick Downloads  — FASTA, CSV, methodology JSON, ZIP bundle
  • Split & Export   — groupby any metadata column → per-group FASTAs → ZIP
  • Accession List   — extract all EPI_ISL IDs to .txt
  • Session Log      — download action_logs as CSV or JSON
"""

import io
import json
import zipfile

import pandas as pd
import streamlit as st

from utils.gisaid_parser import convert_df_to_fasta
from utils.minimal_i18n import T

st.title(f"\U0001f4cb {T('export_header')}")

_active_df:   pd.DataFrame = st.session_state.get("active_df",   pd.DataFrame())
_filtered_df: pd.DataFrame = st.session_state.get("filtered_df", pd.DataFrame())

if _active_df.empty:
    st.warning(T("error_no_active_df"))
    st.stop()

# Export source: filtered preferred, else active
_export_df = _filtered_df if not _filtered_df.empty else _active_df
_src_label  = T("export_split_filtered") if not _filtered_df.empty else T("export_split_active")

st.caption(
    f"**{T('export_source_label')}:** {_src_label} "
    f"— {len(_export_df):,} sequences ready for export."
)
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Quick Downloads
# ─────────────────────────────────────────────────────────────────────────────
st.subheader(f"⬇ {T('export_quick_header')}")
st.caption(T("export_quick_caption"))

ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M")

q1, q2, q3, q4 = st.columns(4)

# — FASTA
with q1:
    fasta_str = convert_df_to_fasta(_export_df)
    st.download_button(
        label=T("export_fasta_btn", n=f"{len(_export_df):,}"),
        data=fasta_str.encode("utf-8"),
        file_name=f"virsift_{ts}.fasta",
        mime="text/plain",
        type="primary",
        use_container_width=True,
        help=T("download_tooltip_fasta"),
    )

# — CSV (metadata, no sequence)
with q2:
    csv_bytes = (
        _export_df.drop(columns=["sequence"], errors="ignore")
        .to_csv(index=False)
        .encode("utf-8")
    )
    st.download_button(
        label=T("export_csv_btn", n=f"{len(_export_df):,}"),
        data=csv_bytes,
        file_name=f"virsift_metadata_{ts}.csv",
        mime="text/csv",
        use_container_width=True,
        help=T("download_tooltip_csv"),
    )

# — Methodology JSON
with q3:
    action_logs = st.session_state.get("action_logs", [])
    methodology = {
        "tool":       "Vir-Seq-Sift v2.1",
        "exported":   ts,
        "source":     _src_label,
        "sequences":  len(_export_df),
        "operations": action_logs,
        "columns":    [c for c in _export_df.columns if c != "sequence"],
    }
    st.download_button(
        label=T("export_json_btn"),
        data=json.dumps(methodology, indent=2, default=str).encode("utf-8"),
        file_name=f"virsift_methodology_{ts}.json",
        mime="application/json",
        use_container_width=True,
        help=T("download_tooltip_json"),
    )

# — ZIP Bundle (FASTA + CSV + JSON)
with q4:
    @st.cache_data(show_spinner=False)
    def _make_bundle(fasta: str, csv: bytes, meta_json: str,
                     ts_key: str) -> bytes:  # noqa: ARG001
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"virsift_{ts_key}.fasta",            fasta.encode("utf-8"))
            zf.writestr(f"virsift_metadata_{ts_key}.csv",     csv)
            zf.writestr(f"virsift_methodology_{ts_key}.json", meta_json.encode("utf-8"))
        buf.seek(0)
        return buf.getvalue()

    bundle = _make_bundle(
        fasta_str, csv_bytes,
        json.dumps(methodology, indent=2, default=str),
        ts,
    )
    st.download_button(
        label=T("export_bundle_zip_btn"),
        data=bundle,
        file_name=f"virsift_bundle_{ts}.zip",
        mime="application/zip",
        use_container_width=True,
        help=T("download_tooltip_zip"),
    )

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — Split & Export by Metadata (star feature from original)
# ─────────────────────────────────────────────────────────────────────────────
st.subheader(f"🗂 {T('export_split_header')}")
st.caption(T("export_split_caption"))

# Candidate split columns
_SPLIT_FIELDS = {
    T("obs_col_subtype"):  "subtype_clean",
    T("obs_col_host"):     "host",
    T("obs_col_segment"):  "segment",
    T("obs_col_location"): "location",
    T("obs_col_clade"):    "clade",
    "Year":                "_year",
    "Month":               "_month",
}
# Keep only columns that actually exist
_available_split = {
    label: col for label, col in _SPLIT_FIELDS.items()
    if col.startswith("_") or col in _export_df.columns
}

sp1, sp2 = st.columns([2, 1])
with sp1:
    split_label = st.selectbox(
        T("export_split_field_label"),
        options=list(_available_split.keys()),
        help=T("export_split_field_help"),
    )
with sp2:
    split_source = st.radio(
        T("export_source_label"),
        options=[T("export_split_filtered"), T("export_split_active")],
        horizontal=True,
        key="split_source_radio",
    )

_split_df = (
    _filtered_df if (split_source == T("export_split_filtered") and not _filtered_df.empty)
    else _active_df
)

# Build the field — handle virtual _year/_month columns
def _get_split_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col == "_year":
        return pd.to_datetime(df.get("collection_date", pd.Series(dtype=str)),
                              errors="coerce").dt.year.astype("Int64").astype(str)
    if col == "_month":
        return pd.to_datetime(df.get("collection_date", pd.Series(dtype=str)),
                              errors="coerce").dt.strftime("%Y-%m")
    return df.get(col, pd.Series(["Unknown"] * len(df), index=df.index)).astype(str)


if st.button(T("export_split_preview_btn"), use_container_width=True):
    field_col = _available_split[split_label]
    series = _get_split_series(_split_df, field_col).replace("nan", pd.NA).dropna()
    groups = _split_df.loc[series.index].copy()
    groups["_split_key"] = series.values

    group_summary = (
        groups.groupby("_split_key")
        .size().reset_index(name="Sequences")
        .sort_values("Sequences", ascending=False)
        .rename(columns={"_split_key": split_label})
    )
    st.session_state["split_groups_df"] = groups
    st.session_state["split_field_col"]  = field_col
    st.session_state["split_label"]      = split_label
    st.session_state["split_summary"]    = group_summary

if "split_summary" in st.session_state:
    summary_df = st.session_state["split_summary"]
    groups_df  = st.session_state["split_groups_df"]
    n_groups   = len(summary_df)
    n_seqs     = int(summary_df["Sequences"].sum())

    st.markdown(
        f"**{n_groups} groups** — {n_seqs:,} sequences total "
        f"(split by **{st.session_state['split_label']}**):"
    )
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    exp_col, ind_col = st.columns([3, 2])

    # — ZIP of all groups
    with exp_col:
        if n_groups > 100:
            st.warning(T("export_split_large_warning", n=n_groups, seqs=n_seqs))

        if st.button(
            T("export_split_zip_btn", n=n_groups, seqs=f"{n_seqs:,}"),
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(T("export_split_generating", n=n_groups)):
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for key, grp in groups_df.groupby("_split_key"):
                        safe = (str(key)
                                .replace("/","_").replace("\\","_")
                                .replace("|","_").replace(" ","_")
                                .replace(":","_").replace("*","_")
                                .replace("?","_").replace('"','_')
                                .replace("<","_").replace(">","_"))
                        grp_clean = grp.drop(columns=["_split_key"])
                        content   = convert_df_to_fasta(grp_clean)
                        zf.writestr(
                            f"{st.session_state['split_label']}_{safe}.fasta",
                            content.encode("utf-8"),
                        )
                zip_buf.seek(0)
                st.download_button(
                    label=T("export_split_download_zip", n=n_groups),
                    data=zip_buf.getvalue(),
                    file_name=f"split_by_{st.session_state['split_label']}_{ts}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="dl_split_zip",
                )
                st.success(T("export_split_zip_success", n=n_groups))

    # — Individual downloads (top 5 groups)
    with ind_col:
        st.caption(T("export_split_individual_caption"))
        top5 = summary_df.head(5)[st.session_state["split_label"]].tolist()
        for key in top5:
            safe = (str(key)
                    .replace("/","_").replace("\\","_")
                    .replace("|","_").replace(" ","_"))
            grp   = groups_df[groups_df["_split_key"] == key].drop(columns=["_split_key"])
            n_g   = len(grp)
            disp  = str(key)[:28] + "…" if len(str(key)) > 28 else str(key)
            fasta_g = convert_df_to_fasta(grp)
            st.download_button(
                label=f"📄 {disp}  ({n_g} seqs)",
                data=fasta_g.encode("utf-8"),
                file_name=f"{st.session_state['split_label']}_{safe}.fasta",
                mime="text/plain",
                use_container_width=True,
                key=f"dl_grp_{safe[:40]}",
            )
        if n_groups > 5:
            st.caption(T("export_split_more", extra=n_groups - 5))

    if st.button(T("export_split_clear"), use_container_width=True):
        for k in ("split_groups_df","split_field_col","split_label","split_summary"):
            st.session_state.pop(k, None)
        st.rerun()

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — Accession Extraction
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"🔑 {T('export_accession_header')}"):
    st.caption(T("export_accession_caption"))

    if "accession" in _export_df.columns:
        acc_series = (
            _export_df["accession"]
            .dropna()
            .astype(str)
            .str.strip()
            .pipe(lambda s: s[s.str.startswith("EPI_ISL")])
            .unique()
        )
        acc_text = "\n".join(sorted(acc_series))
        st.code(
            acc_text[:800] + (f"\n… (+{len(acc_series)-20} more)" if len(acc_series) > 20 else ""),
            language=None,
        )
        st.caption(f"{len(acc_series):,} unique EPI_ISL accessions")
        st.download_button(
            label=T("export_accession_btn", n=len(acc_series)),
            data=acc_text.encode("utf-8"),
            file_name=f"virsift_accessions_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
            help=T("export_accession_help"),
        )
    else:
        st.info("No accession column found in this dataset.")

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — Session Action Log
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"📋 {T('export_log_header')}"):
    st.caption(T("export_log_tooltip"))

    logs = st.session_state.get("action_logs", [])
    if logs:
        _col_rename = {
            "action":    T("log_col_action"),
            "file":      T("log_col_file"),
            "sequences": T("log_col_sequences"),
            "time_s":    T("log_col_time_s"),
            "timestamp": T("log_col_timestamp"),
            "files":     T("log_col_files"),
        }
        log_df = pd.DataFrame(logs).rename(columns=_col_rename)
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        # Download uses original log (raw dict keys preserved for machine-readability)
        _raw_log_df = pd.DataFrame(logs)
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label=T("export_log_csv_btn"),
                data=_raw_log_df.to_csv(index=False).encode("utf-8"),
                file_name=f"virsift_log_{ts}.csv",
                mime="text/csv",
                use_container_width=True,
                help=T("export_log_tooltip"),
            )
        with dl2:
            st.download_button(
                label=T("export_log_json_btn"),
                data=json.dumps(logs, indent=2, default=str).encode("utf-8"),
                file_name=f"virsift_log_{ts}.json",
                mime="application/json",
                use_container_width=True,
                help=T("export_log_tooltip"),
            )
    else:
        st.info(T("export_no_ops_logged"))


# ---------------------------------------------------------------------------
# Per-page sidebar — export source info + quick stats
# ---------------------------------------------------------------------------

with st.sidebar:
    st.divider()
    st.markdown(f"**{T('sidebar_ex_source')}**")
    st.caption(f"{_src_label}")
    st.metric(T("obs_col_count"), f"{len(_export_df):,}")
    if not _filtered_df.empty and not _active_df.empty:
        pct = round(len(_filtered_df) / max(len(_active_df), 1) * 100, 1)
        st.caption(f"{pct}{T('export_pct_of_active')}")

# ---------------------------------------------------------------------------
# Inter-page navigation
# ---------------------------------------------------------------------------
st.divider()
_ex_nav1, _ex_nav2 = st.columns(2)
try:
    _ex_nav1.page_link("pages/05_📊_Analytics.py",
                       label=f"← 📊 {T('nav_analytics')}",
                       use_container_width=True)
except AttributeError:
    _ex_nav1.markdown(f"[← 📊 {T('nav_analytics')}](pages/05_📊_Analytics.py)")
