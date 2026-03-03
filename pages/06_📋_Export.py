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
import re
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

# ── Filename prefix — editable on this page (mirrors sidebar control) ────────
_pfx_default = st.session_state.get("export_prefix", "virsift") or "virsift"
_pfx_col, _ = st.columns([2, 3])
with _pfx_col:
    _pfx_input = st.text_input(
        T("sidebar_export_prefix_label"),
        value=_pfx_default,
        max_chars=40,
        key="export_pg_prefix",
        help=T("sidebar_export_prefix_help"),
        placeholder="virsift",
    )
_pfx = re.sub(r"[^\w\-]", "_", (_pfx_input or "virsift").strip())[:40] or "virsift"
if _pfx != _pfx_default:
    st.session_state["export_prefix"] = _pfx

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — Quick Downloads
# ─────────────────────────────────────────────────────────────────────────────
st.subheader(f"⬇ {T('export_quick_header')}")
st.caption(T("export_quick_caption"))

q1, q2, q3, q4 = st.columns(4)

# — FASTA
with q1:
    fasta_str = convert_df_to_fasta(_export_df)
    st.download_button(
        label=T("export_fasta_btn", n=f"{len(_export_df):,}"),
        data=fasta_str.encode("utf-8"),
        file_name=f"{_pfx}_sequences.fasta",
        mime="text/plain",
        type="primary",
        use_container_width=True,
        help=f"📄 {_pfx}_sequences.fasta · rename prefix in sidebar",
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
        file_name=f"{_pfx}_metadata.csv",
        mime="text/csv",
        use_container_width=True,
        help=f"📄 {_pfx}_metadata.csv · rename prefix in sidebar",
    )

# — Methodology JSON
with q3:
    action_logs = st.session_state.get("action_logs", [])
    methodology = {
        "tool":       "Vir-Seq-Sift v2.1",
        "prefix":     _pfx,
        "source":     _src_label,
        "sequences":  len(_export_df),
        "operations": action_logs,
        "columns":    [c for c in _export_df.columns if c != "sequence"],
    }
    st.download_button(
        label=T("export_json_btn"),
        data=json.dumps(methodology, indent=2, default=str).encode("utf-8"),
        file_name=f"{_pfx}_methodology.json",
        mime="application/json",
        use_container_width=True,
        help=f"📄 {_pfx}_methodology.json · rename prefix in sidebar",
    )

# — ZIP Bundle (FASTA + CSV + JSON)
with q4:
    @st.cache_data(show_spinner=False)
    def _make_bundle(fasta: str, csv: bytes, meta_json: str,
                     pfx_key: str) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{pfx_key}_sequences.fasta",   fasta.encode("utf-8"))
            zf.writestr(f"{pfx_key}_metadata.csv",      csv)
            zf.writestr(f"{pfx_key}_methodology.json",  meta_json.encode("utf-8"))
        buf.seek(0)
        return buf.getvalue()

    bundle = _make_bundle(
        fasta_str, csv_bytes,
        json.dumps(methodology, indent=2, default=str),
        _pfx,
    )
    st.download_button(
        label=T("export_bundle_zip_btn"),
        data=bundle,
        file_name=f"{_pfx}_bundle.zip",
        mime="application/zip",
        use_container_width=True,
        help=f"📄 {_pfx}_bundle.zip (FASTA + CSV + JSON) · rename prefix in sidebar",
    )

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1b — Per-File Downloads (shown when multiple source files loaded)
# ─────────────────────────────────────────────────────────────────────────────
_raw_files_ex = st.session_state.get("raw_files", [])
_act_logs_ex  = st.session_state.get("action_logs", [])
_last_act_ex  = next(
    (lg for lg in reversed(_act_logs_ex) if lg.get("action") == "activate"),
    None,
)
_act_names_ex = _last_act_ex.get("files", []) if _last_act_ex else []
_contrib_ex   = [rf for rf in _raw_files_ex if rf["name"] in _act_names_ex]

if len(_contrib_ex) > 1:
    st.subheader(f"📂 {T('export_per_file_header')}")
    st.caption(T("export_per_file_caption"))

    import re as _re_ex

    for _pf_rf in _contrib_ex:
        _pf_df    = pd.DataFrame(_pf_rf["parsed"])
        _pf_n     = _pf_rf["n_sequences"]
        _pf_safe  = _re_ex.sub(r"[^\w\-]", "_", _pf_rf["name"])[:40]
        _pf_label = _pf_rf["name"][:55] + ("…" if len(_pf_rf["name"]) > 55 else "")

        _pf_c0, _pf_c1, _pf_c2 = st.columns([3, 1, 1])
        _pf_c0.markdown(f"**{_pf_label}** — {_pf_n:,} seqs")

        with _pf_c1:
            try:
                _pf_fasta = convert_df_to_fasta(_pf_df)
            except Exception:
                _lines = []
                for _, _r in _pf_df.iterrows():
                    _lines.append(f">{_r.get('isolate', _r.get('sequence_hash', 'seq'))}")
                    _lines.append(str(_r.get("sequence", "")))
                _pf_fasta = "\n".join(_lines)
            st.download_button(
                label=T("export_per_file_fasta"),
                data=_pf_fasta.encode("utf-8") if isinstance(_pf_fasta, str) else _pf_fasta,
                file_name=f"{_pfx}_{_pf_safe}.fasta",
                mime="text/plain",
                use_container_width=True,
                key=f"dl_pf_fasta_{_pf_safe}",
                help=f"📄 {_pfx}_{_pf_safe}.fasta",
            )

        with _pf_c2:
            _pf_csv = (
                _pf_df.drop(columns=["sequence"], errors="ignore")
                .to_csv(index=False)
                .encode("utf-8")
            )
            st.download_button(
                label=T("export_per_file_csv"),
                data=_pf_csv,
                file_name=f"{_pfx}_{_pf_safe}_meta.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"dl_pf_csv_{_pf_safe}",
                help=f"📄 {_pfx}_{_pf_safe}_meta.csv",
            )

    # Zip of all source files
    _pf_zip_col, _ = st.columns([2, 3])
    with _pf_zip_col:
        if st.button(
            T("export_per_file_zip_btn", n=len(_contrib_ex)),
            use_container_width=True,
            key="dl_pf_zip_all",
        ):
            with st.spinner("Building ZIP…"):
                _pf_zbuf = io.BytesIO()
                with zipfile.ZipFile(_pf_zbuf, "w", zipfile.ZIP_DEFLATED) as _pf_zf:
                    for _zrf in _contrib_ex:
                        _z_df   = pd.DataFrame(_zrf["parsed"])
                        _z_safe = _re_ex.sub(r"[^\w\-]", "_", _zrf["name"])[:40]
                        try:
                            _z_fa = convert_df_to_fasta(_z_df)
                        except Exception:
                            _zl = []
                            for _, _r in _z_df.iterrows():
                                _zl.append(f">{_r.get('isolate', 'seq')}")
                                _zl.append(str(_r.get("sequence", "")))
                            _z_fa = "\n".join(_zl)
                        _pf_zf.writestr(
                            f"{_pfx}_{_z_safe}.fasta",
                            _z_fa.encode("utf-8") if isinstance(_z_fa, str) else _z_fa,
                        )
                _pf_zbuf.seek(0)
                st.download_button(
                    label=f"⬇ {_pfx}_source_files.zip",
                    data=_pf_zbuf.getvalue(),
                    file_name=f"{_pfx}_source_files.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="dl_pf_zip_dl",
                )

    st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1c — Timeline & Curation Downloads (visible after Molecular Timeline run)
# ─────────────────────────────────────────────────────────────────────────────
_tl_result_df = st.session_state.get("_tl_result_df")
_tl_matrix    = st.session_state.get("_tl_edited_matrix")

if _tl_result_df is not None and not _tl_result_df.empty:
    st.subheader(f"📅 {T('export_timeline_header')}")
    st.caption(T("export_timeline_caption", n=f"{len(_tl_result_df):,}"))

    _tl_q1, _tl_q2, _tl_q3 = st.columns(3)

    with _tl_q1:
        _tl_fasta_str = convert_df_to_fasta(_tl_result_df)
        st.download_button(
            label=T("export_timeline_fasta_btn", n=f"{len(_tl_result_df):,}"),
            data=_tl_fasta_str.encode("utf-8"),
            file_name=f"{_pfx}_curated_timeline.fasta",
            mime="text/plain",
            type="primary",
            use_container_width=True,
            help=f"📄 {_pfx}_curated_timeline.fasta",
            key="ex_tl_fasta",
        )

    with _tl_q2:
        _tl_csv_bytes = (
            _tl_result_df.drop(columns=["sequence"], errors="ignore")
            .to_csv(index=False)
            .encode("utf-8")
        )
        st.download_button(
            label=T("export_timeline_csv_btn", n=f"{len(_tl_result_df):,}"),
            data=_tl_csv_bytes,
            file_name=f"{_pfx}_curated_timeline_metadata.csv",
            mime="text/csv",
            use_container_width=True,
            help=f"📄 {_pfx}_curated_timeline_metadata.csv",
            key="ex_tl_csv",
        )

    with _tl_q3:
        if _tl_matrix is not None:
            st.download_button(
                label=T("timeline_download_matrix_csv"),
                data=_tl_matrix.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"{_pfx}_timeline_matrix.csv",
                mime="text/csv",
                use_container_width=True,
                help=f"📄 {_pfx}_timeline_matrix.csv",
                key="ex_tl_matrix",
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
                _split_zip_name = f"{_pfx}_split_by_{st.session_state['split_label']}.zip"
                st.download_button(
                    label=T("export_split_download_zip", n=n_groups),
                    data=zip_buf.getvalue(),
                    file_name=_split_zip_name,
                    mime="application/zip",
                    use_container_width=True,
                    key="dl_split_zip",
                    help=f"📄 {_split_zip_name} · rename prefix in sidebar",
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
            _grp_fname = f"{_pfx}_{st.session_state['split_label']}_{safe}.fasta"
            st.download_button(
                label=f"📄 {disp}  ({n_g} seqs)",
                data=fasta_g.encode("utf-8"),
                file_name=_grp_fname,
                mime="text/plain",
                use_container_width=True,
                key=f"dl_grp_{safe[:40]}",
                help=f"📄 {_grp_fname} · rename prefix in sidebar",
            )
        if n_groups > 5:
            st.caption(T("export_split_more", extra=n_groups - 5))

    if st.button(T("export_split_clear"), use_container_width=True):
        for k in ("split_groups_df","split_field_col","split_label","split_summary"):
            st.session_state.pop(k, None)
        st.rerun()

st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2b — Segment Folder Structure
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"📁 {T('export_seg_folder_header')}", expanded=False):
    st.caption(T("export_seg_folder_caption"))

    _ALL_SEGMENTS = ["HA", "NA", "PB2", "PB1", "PA", "NP", "MP", "NS", "HE", "P3"]

    # ── ZIP name ──────────────────────────────────────────────────────────────
    _seg_zname_col, _ = st.columns([2, 3])
    with _seg_zname_col:
        _seg_zip_name = st.text_input(
            T("export_seg_folder_zip_name"),
            value=f"{_pfx}_segment_folders",
            max_chars=60,
            key="export_seg_zip_name",
            placeholder="project_name_segment_folders",
        )

    # ── Preset quick-selectors ────────────────────────────────────────────────
    st.caption(T("export_seg_presets_label"))
    _sp1, _sp2, _sp3, _sp4, _sp5 = st.columns(5)
    _preset_hit = None
    if _sp1.button(T("export_seg_preset_all"),      key="segp_all",  use_container_width=True):
        _preset_hit = _ALL_SEGMENTS[:]
    if _sp2.button(T("export_seg_preset_surface"),   key="segp_surf", use_container_width=True):
        _preset_hit = ["HA", "NA"]
    if _sp3.button(T("export_seg_preset_poly"),      key="segp_poly", use_container_width=True):
        _preset_hit = ["PB2", "PB1", "PA"]
    if _sp4.button(T("export_seg_preset_internal"),  key="segp_int",  use_container_width=True):
        _preset_hit = ["NP", "MP", "NS"]
    if _sp5.button(T("export_seg_preset_none"),      key="segp_none", use_container_width=True):
        _preset_hit = []
    if _preset_hit is not None:
        for _s in _ALL_SEGMENTS:
            st.session_state[f"seg_folder_{_s}"] = _s in _preset_hit

    # ── Per-segment checkboxes with sequence counts ───────────────────────────
    st.caption(T("export_seg_folder_select_segments"))
    _seg_counts: dict = {}
    if "segment" in _export_df.columns:
        _seg_counts = _export_df["segment"].str.upper().value_counts().to_dict()

    _seg_chk_cols = st.columns(5)
    _selected_segs = []
    for _si, _seg in enumerate(_ALL_SEGMENTS):
        _cnt = _seg_counts.get(_seg, 0)
        _lbl = f"{_seg}  ({_cnt:,})" if _cnt else _seg
        if _seg_chk_cols[_si % 5].checkbox(_lbl, value=True, key=f"seg_folder_{_seg}"):
            _selected_segs.append(_seg)

    # ── Content options ───────────────────────────────────────────────────────
    st.divider()
    _opt_col1, _opt_col2, _opt_col3 = st.columns(3)
    _split_into_segs = _opt_col1.checkbox(
        T("export_seg_folder_split_data"),
        value=False,
        key="export_seg_split_data",
        help=T("export_seg_folder_split_help"),
    )
    _include_readme = _opt_col2.checkbox(
        T("export_seg_include_readme"),
        value=True,
        key="export_seg_readme",
        help=T("export_seg_include_readme_help"),
    )
    _include_summary = _opt_col3.checkbox(
        T("export_seg_include_summary"),
        value=False,
        key="export_seg_summary",
        help=T("export_seg_include_summary_help"),
    )

    # ── Live folder-structure preview ─────────────────────────────────────────
    if _selected_segs:
        _preview_lines = [f"📦 {_seg_zip_name or 'segment_folders'}.zip"]
        for _s in _selected_segs:
            _cnt = _seg_counts.get(_s, 0)
            _preview_lines.append(f"  ├── 📁 {_s}/")
            if _split_into_segs and _cnt:
                _preview_lines.append(f"  │   ├── 🧬 {_pfx}_{_s}.fasta  ({_cnt:,} seqs)")
                _preview_lines.append(f"  │   └── 📊 {_pfx}_{_s}_metadata.csv")
            elif _split_into_segs:
                _preview_lines.append(f"  │   └── (no sequences for this segment)")
            if _include_readme:
                _preview_lines.append(f"  │   {'└' if not _split_into_segs else '   '}── 📄 README.txt")
        if _include_summary:
            _preview_lines.append(f"  └── 📋 dataset_summary.csv")
        st.code("\n".join(_preview_lines), language=None)

    if _split_into_segs:
        st.info(T("export_seg_folder_split_info"), icon="ℹ️")

    if st.button(T("export_seg_folder_generate"),
                 type="primary", use_container_width=False,
                 key="export_seg_gen"):
        if not _selected_segs:
            st.warning(T("export_seg_folder_none_selected"))
        else:
            _seg_zbuf = io.BytesIO()
            with zipfile.ZipFile(_seg_zbuf, "w", zipfile.ZIP_DEFLATED) as _seg_zf:
                for _seg in _selected_segs:
                    # Folder placeholder
                    _seg_zf.writestr(f"{_seg}/.gitkeep", "")

                    # Optional README per segment
                    if _include_readme:
                        _readme_cnt = _seg_counts.get(_seg, 0)
                        _readme_txt = (
                            f"Segment: {_seg}\n"
                            f"Project: {_pfx}\n"
                            f"Sequences in dataset: {_readme_cnt}\n"
                            f"Generated by VirSift\n"
                        )
                        _seg_zf.writestr(f"{_seg}/README.txt", _readme_txt)

                    # Optional FASTA + CSV data split
                    if _split_into_segs and "segment" in _export_df.columns:
                        _seg_subset = _export_df[
                            _export_df["segment"].str.upper() == _seg.upper()
                        ]
                        if not _seg_subset.empty:
                            try:
                                _seg_fasta = convert_df_to_fasta(_seg_subset)
                                _seg_zf.writestr(
                                    f"{_seg}/{_pfx}_{_seg}.fasta",
                                    _seg_fasta if isinstance(_seg_fasta, bytes)
                                    else _seg_fasta.encode("utf-8"),
                                )
                                _seg_zf.writestr(
                                    f"{_seg}/{_pfx}_{_seg}_metadata.csv",
                                    _seg_subset.drop(columns=["sequence"], errors="ignore")
                                    .to_csv(index=False),
                                )
                            except Exception:
                                pass

                # Optional top-level dataset summary CSV
                if _include_summary:
                    _sum_rows = []
                    for _seg in _selected_segs:
                        _cnt = _seg_counts.get(_seg, 0)
                        _sum_rows.append({"segment": _seg, "sequences": _cnt})
                    import csv as _csv, io as _io2
                    _sum_buf = _io2.StringIO()
                    _sum_writer = _csv.DictWriter(_sum_buf, fieldnames=["segment", "sequences"])
                    _sum_writer.writeheader()
                    _sum_writer.writerows(_sum_rows)
                    _seg_zf.writestr("dataset_summary.csv", _sum_buf.getvalue())

            _seg_zbuf.seek(0)
            _seg_fname = (
                re.sub(r"[^\w\-]", "_", (_seg_zip_name or "segment_folders").strip())[:60]
                or "segment_folders"
            ) + ".zip"
            st.download_button(
                label=T("export_seg_folder_download", n=len(_selected_segs)),
                data=_seg_zbuf.getvalue(),
                file_name=_seg_fname,
                mime="application/zip",
                use_container_width=False,
                key="dl_seg_folder_zip",
            )

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
            acc_text[:800] + (T("export_more_items", n=len(acc_series) - 20) if len(acc_series) > 20 else ""),
            language=None,
        )
        st.caption(T("export_epi_isl_count", n=f"{len(acc_series):,}"))
        st.download_button(
            label=T("export_accession_btn", n=len(acc_series)),
            data=acc_text.encode("utf-8"),
            file_name=f"{_pfx}_accessions.txt",
            mime="text/plain",
            use_container_width=True,
            help=f"📄 {_pfx}_accessions.txt · rename prefix in sidebar",
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
        _act_col = T("log_col_action")
        if _act_col in log_df.columns:
            log_df[_act_col] = log_df[_act_col].replace({
                "parse": T("log_action_parse"),
                "activate": T("log_action_activate"),
            })
        log_df = log_df.fillna("-")
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        # Download uses original log (raw dict keys preserved for machine-readability)
        _raw_log_df = pd.DataFrame(logs)
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label=T("export_log_csv_btn"),
                data=_raw_log_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{_pfx}_log.csv",
                mime="text/csv",
                use_container_width=True,
                help=f"📄 {_pfx}_log.csv · rename prefix in sidebar",
            )
        with dl2:
            st.download_button(
                label=T("export_log_json_btn"),
                data=json.dumps(logs, indent=2, default=str).encode("utf-8"),
                file_name=f"{_pfx}_log.json",
                mime="application/json",
                use_container_width=True,
                help=f"📄 {_pfx}_log.json · rename prefix in sidebar",
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
