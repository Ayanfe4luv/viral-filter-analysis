# -*- coding: utf-8 -*-
"""
pages/04_🧬_Molecular_Timeline.py — Molecular Timeline Tracker

MISSION: Track the persistence of identical sequences across time.
Answer the question: "How long did specific viral clones survive in circulation?"

Works with ANY respiratory virus FASTA data including:
  - Influenza A/B (H3N2, H1N1, H5N1, etc.)
  - RSV (Respiratory Syncytial Virus) A and B
  - SARS-CoV-2 and other coronaviruses
  - Any pathogen with pipe-delimited GISAID-style headers

Architecture follows Molecular_Timeline_Tracker_Architecture_Plan.docx:
  Phase 1: Dataset Diagnostics (read-only overview)
  Phase 2: Configuration (cluster threshold + representative selection)
  Phase 3: Interactive Timeline Matrix (st.data_editor)
  Phase 4: Impact Preview & Export
"""

import hashlib
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.minimal_i18n import T

# ─────────────────────────────────────────────────────────────────────────────
# State — respect global Data Mode toggle (sidebar)
# ─────────────────────────────────────────────────────────────────────────────
_active_df: pd.DataFrame   = st.session_state.get("active_df",   pd.DataFrame())
_filtered_df: pd.DataFrame = st.session_state.get("filtered_df", pd.DataFrame())
_data_mode = st.session_state.get("data_mode", "current")

if _data_mode == "original":
    # Original mode: always use the raw activation snapshot
    _display_df = _active_df
    _mode_badge = "🟡 Original"
else:
    # Current mode: prefer filtered, fall back to active
    _display_df = _filtered_df if not _filtered_df.empty else _active_df
    _mode_badge = "🔵 Current" if not _filtered_df.empty else "🔵 Current (Active)"

# ─────────────────────────────────────────────────────────────────────────────
# Chart colour scheme — user-selectable from sidebar, stored in session state
# ─────────────────────────────────────────────────────────────────────────────
_TIMELINE_PALETTES: dict = {
    "🔵 Ocean Blue": {"seq": "Blues",   "accent": "#0ea5e9", "fill": "rgba(14,165,233,0.22)"},
    "🟣 Aurora":     {"seq": "Plasma",  "accent": "#a855f7", "fill": "rgba(168,85,247,0.22)"},
    "🟢 Forest":     {"seq": "Greens",  "accent": "#10b981", "fill": "rgba(16,185,129,0.22)"},
    "🟠 Heatwave":   {"seq": "Oranges", "accent": "#f97316", "fill": "rgba(249,115,22,0.22)"},
    "🔴 Crimson":    {"seq": "Reds",    "accent": "#ef4444", "fill": "rgba(239,68,68,0.22)"},
    "⚫ Neutral":    {"seq": "Greys",   "accent": "#64748b", "fill": "rgba(100,116,139,0.22)"},
}
_tl_scheme_name = st.session_state.get("timeline_chart_scheme", "🔵 Ocean Blue")
_tl_pal = _TIMELINE_PALETTES.get(_tl_scheme_name, _TIMELINE_PALETTES["🔵 Ocean Blue"])

# ─────────────────────────────────────────────────────────────────────────────
# Page header
# ─────────────────────────────────────────────────────────────────────────────
st.title(f"🧬 {T('timeline_title')}")
st.caption(T("timeline_caption"))

# ── Workflow guide (bold, always visible) ────────────────────────────────────
st.markdown(f"""
**{T('timeline_workflow_header')}**

**{T('timeline_workflow_step1')}**

**{T('timeline_workflow_step2')}**

**{T('timeline_workflow_step3')}**
""")
st.divider()

# ── Per-file scope selector ───────────────────────────────────────────────────
# When multiple files were loaded and activated, the user can restrict ALL phases
# (diagnostics, configuration, matrix, preview/export) to a single source file.
# This lets you compare cluster behaviour across different datasets side-by-side
# by toggling between files without re-uploading.
_tl_raw_files = st.session_state.get("raw_files", [])
_tl_act_logs  = st.session_state.get("action_logs", [])
_tl_last_act  = next(
    (lg for lg in reversed(_tl_act_logs) if lg.get("action") == "activate"),
    None,
)
_tl_act_names = _tl_last_act.get("files", []) if _tl_last_act else []
_tl_contrib   = [rf for rf in _tl_raw_files if rf["name"] in _tl_act_names]

if len(_tl_contrib) > 1:
    _scope_opts = [T("timeline_scope_all")] + [rf["name"] for rf in _tl_contrib]
    _tl_scope = st.radio(
        T("timeline_scope_label"),
        options=_scope_opts,
        index=st.session_state.get("tl_scope_idx", 0),
        horizontal=True,
        key="tl_file_scope",
        help=T("timeline_scope_help"),
    )
    # Store index for next rerun to preserve selection
    st.session_state["tl_scope_idx"] = _scope_opts.index(_tl_scope)

    if _tl_scope != T("timeline_scope_all"):
        # Override _display_df with the chosen file's raw data
        _scope_rf = next(rf for rf in _tl_contrib if rf["name"] == _tl_scope)
        _display_df = pd.DataFrame(_scope_rf["parsed"])
        # Ensure sequence_hash is present (parse_gisaid_fasta adds it, but safeguard)
        if "sequence_hash" not in _display_df.columns and "sequence" in _display_df.columns:
            _display_df = _display_df.copy()
            _display_df["sequence_hash"] = (
                _display_df["sequence"]
                .fillna("")
                .apply(lambda s: hashlib.md5(s.upper().encode()).hexdigest()[:12])
            )
        _mode_badge = f"📁 {_tl_scope[:30]}"
        st.success(T("timeline_scope_file_badge",
                     file=_tl_scope, n=len(_display_df)))
    else:
        st.caption(T("timeline_scope_all_caption", n=len(_tl_contrib)))

    st.divider()

# ── Mission statement ─────────────────────────────────────────────────────────
st.info(f"""
{T('timeline_mission_header')}

**{T('timeline_use_this_when')}**
- {T('timeline_use1')}
- {T('timeline_use2')}
- {T('timeline_use3')}
- {T('timeline_use4')}

**{T('timeline_use_refinery_instead')}**
- {T('timeline_refinery1')}
- {T('timeline_refinery2')}
- {T('timeline_refinery3')}

**{T('timeline_virus_support')}** Influenza A/B, RSV A/B, SARS-CoV-2, and any FASTA with date metadata.
""")

# ─────────────────────────────────────────────────────────────────────────────
# No data guard
# ─────────────────────────────────────────────────────────────────────────────
if _display_df.empty:
    st.warning(T("timeline_no_data"))
    try:
        st.page_link("pages/02_📁_Workspace.py",
                     label="📁 Go to Workspace to load a dataset →",
                     use_container_width=False)
    except AttributeError:
        st.markdown("[📁 Load a dataset first](pages/02_📁_Workspace.py)")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Helper: compute sequence hash if not present
# ─────────────────────────────────────────────────────────────────────────────
if "sequence_hash" not in _display_df.columns and "sequence" in _display_df.columns:
    _display_df = _display_df.copy()
    _display_df["sequence_hash"] = (
        _display_df["sequence"]
        .fillna("")
        .apply(lambda s: hashlib.md5(s.upper().encode()).hexdigest()[:12])
    )

if "sequence_hash" not in _display_df.columns:
    st.error(T("timeline_no_sequence_col"))
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — Dataset Diagnostics
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"🔍 {T('timeline_diagnostics_header')}", expanded=True):
    total_seqs    = len(_display_df)
    unique_hashes = _display_df["sequence_hash"].nunique()
    dup_mask      = _display_df.duplicated(subset=["sequence_hash"], keep=False)
    in_clusters   = dup_mask.sum()

    d1, d2, d3 = st.columns(3)
    d1.metric(T("timeline_total_sequences"),    f"{total_seqs:,}")
    d2.metric(T("timeline_unique_clones"),      f"{unique_hashes:,}")
    d3.metric(T("timeline_in_dup_clusters"),    f"{in_clusters:,}")

    # Caption about source — use translated terms so they render in current language
    _src = T("timeline_src_filtered") if not _filtered_df.empty else T("timeline_src_active")
    st.caption(T("timeline_data_source", src=_src))

    # Top duplicate clusters preview
    if unique_hashes < total_seqs:
        # Build full cluster summary (all sizes) for sunburst + top-N for bar
        _has_dates_d   = "collection_date" in _display_df.columns
        _has_subtype_d = "subtype" in _display_df.columns
        _has_isolate_d = "isolate" in _display_df.columns

        _has_clade_d  = "clade" in _display_df.columns

        _agg_spec: dict = {
            "count":          ("sequence_hash", "size"),
            "representative": ("isolate", "first") if _has_isolate_d else ("sequence_hash", "first"),
        }
        if _has_dates_d:
            _agg_spec["first_date"] = ("collection_date", "min")
            _agg_spec["last_date"]  = ("collection_date", "max")
        if _has_subtype_d:
            _agg_spec["subtype"] = ("subtype", "first")
        if _has_clade_d:
            _agg_spec["clade"] = ("clade", "first")

        cluster_summary = (
            _display_df.groupby("sequence_hash")
            .agg(**_agg_spec)
            .sort_values("count", ascending=False)
            .reset_index(drop=True)
        )

        st.subheader(T("timeline_top_clusters"))

        # ── Inline colour + view + top-N controls ─────────────────────────────
        _total_diag = len(cluster_summary)
        _ctrl_c, _ctrl_v, _ctrl_sp = st.columns([1, 1, 2])
        with _ctrl_c:
            _sb_scheme_opts2 = list(_TIMELINE_PALETTES.keys())
            st.selectbox(
                T("timeline_chart_colour"),
                options=_sb_scheme_opts2,
                index=_sb_scheme_opts2.index(_tl_scheme_name)
                       if _tl_scheme_name in _sb_scheme_opts2 else 0,
                key="timeline_chart_scheme",
                help=T("timeline_chart_colour_help"),
            )
            # Re-read palette after widget (takes effect next rerun but swatch is live)
            _tl_pal = _TIMELINE_PALETTES.get(
                st.session_state.get("timeline_chart_scheme", _tl_scheme_name),
                _TIMELINE_PALETTES["🔵 Ocean Blue"],
            )
        with _ctrl_v:
            _right_view = st.radio(
                T("timeline_view_mode"),
                options=[T("timeline_view_sunburst"),
                         T("timeline_view_treemap"),
                         T("timeline_view_table")],
                horizontal=False,
                key="tl_diag_view",
                label_visibility="visible",
            )

        with _ctrl_sp:
            # Top-N slider — controls bar chart rows and table rows.
            # Setting to max includes singletons (count = 1).
            _top_n_diag = st.slider(
                T("timeline_top_n_label"),
                min_value=1,
                max_value=max(_total_diag, 1),
                value=min(12, max(_total_diag, 1)),
                help=T("timeline_top_n_help"),
                key="tl_diag_top_n",
            )

        try:
            import plotly.express as _px_diag

            _col_bar, _col_sun = st.columns([2, 1])

            # ── Left: horizontal bar — top N clusters by count (includes singletons
            #    when slider is dragged all the way right) ──────────────────────────
            with _col_bar:
                _diag_plot = cluster_summary.head(_top_n_diag).sort_values("count").copy()

                if _has_dates_d and "first_date" in _diag_plot.columns and "last_date" in _diag_plot.columns:
                    try:
                        _diag_plot["_duration"] = (
                            pd.to_datetime(_diag_plot["last_date"],  errors="coerce") -
                            pd.to_datetime(_diag_plot["first_date"], errors="coerce")
                        ).dt.days.fillna(0).clip(lower=0).astype(int)
                        _diag_plot["_pct"] = (_diag_plot["count"] / max(total_seqs, 1) * 100).round(1)
                        _color_col  = "_duration"
                        _cbar_title = T("timeline_diag_duration_hardcode")
                        _cdata      = ["first_date", "last_date", "_duration", "_pct",
                                       "subtype" if "subtype" in _diag_plot.columns else "count"]
                        _hover_tmpl = (
                            "<b>%{y}</b><br>"
                            f"{T('timeline_diag_axis_count')}: %{{x}}"
                            " (%{customdata[3]:.1f}% of dataset)<br>"
                            f"{T('timeline_col_first')}: %{{customdata[0]}}<br>"
                            f"{T('timeline_col_last')}: %{{customdata[1]}}<br>"
                            f"{T('timeline_diag_duration_days')}: %{{customdata[2]}} days"
                            "<extra></extra>"
                        )
                    except Exception:
                        _color_col  = "count"
                        _cbar_title = T("timeline_diag_axis_count")
                        _cdata      = []
                        _hover_tmpl = "<b>%{y}</b><br>Sequences: %{x}<extra></extra>"
                else:
                    _color_col  = "count"
                    _cbar_title = T("timeline_diag_axis_count")
                    _cdata      = []
                    _hover_tmpl = "<b>%{y}</b><br>Sequences: %{x}<extra></extra>"

                _fig_diag = _px_diag.bar(
                    _diag_plot,
                    x="count",
                    y="representative",
                    orientation="h",
                    color=_color_col,
                    color_continuous_scale=_tl_pal["seq"],
                    custom_data=_cdata,
                )
                _fig_diag.update_traces(
                    hovertemplate=_hover_tmpl,
                    marker_line_width=0,
                )
                _fig_diag.update_layout(
                    margin=dict(t=10, b=0, l=0, r=10),
                    height=max(280, len(_diag_plot) * 38 + 60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=True,
                    coloraxis_colorbar=dict(title=_cbar_title, thickness=12, len=0.7),
                    yaxis_title=None,
                    xaxis_title=T("timeline_diag_axis_count"),
                )
                st.plotly_chart(_fig_diag, use_container_width=True)

            # ── Right: sunburst / treemap / table (user-selectable) ───────────
            with _col_sun:
                st.caption(T("timeline_cluster_dist_title"))

                def _size_bucket(n: int) -> str:
                    if n == 1:  return T("timeline_cluster_singletons")
                    if n <= 4:  return T("timeline_cluster_small")
                    if n <= 9:  return T("timeline_cluster_medium")
                    if n <= 19: return T("timeline_cluster_large")
                    return T("timeline_cluster_major")

                _sun_df = cluster_summary.copy()
                _sun_df["size_bucket"] = _sun_df["count"].apply(_size_bucket)

                # Categorical color map — each size tier gets a distinct colour
                # that is visually harmonious with the selected palette accent
                _BUCKET_COLORS = {
                    T("timeline_cluster_singletons"): "#94a3b8",
                    T("timeline_cluster_small"):      _tl_pal["accent"],
                    T("timeline_cluster_medium"):     "#f59e0b",
                    T("timeline_cluster_large"):      "#dc2626",
                    T("timeline_cluster_major"):      "#7c3aed",
                }

                _has_clade_sun = "clade" in _sun_df.columns and _sun_df["clade"].notna().any()
                if _has_subtype_d and "subtype" in _sun_df.columns and _has_clade_sun:
                    # 3-level hierarchy: size bucket → subtype → clade
                    _sun_df["clade"] = _sun_df["clade"].fillna("Unknown")
                    _sun_agg = (
                        _sun_df.groupby(["size_bucket", "subtype", "clade"], dropna=False)
                        .agg(total=("count", "sum"))
                        .reset_index()
                    )
                    _sun_path = ["size_bucket", "subtype", "clade"]
                elif _has_subtype_d and "subtype" in _sun_df.columns:
                    _sun_agg = (
                        _sun_df.groupby(["size_bucket", "subtype"], dropna=False)
                        .agg(total=("count", "sum"))
                        .reset_index()
                    )
                    _sun_path = ["size_bucket", "subtype"]
                else:
                    _sun_agg = (
                        _sun_df.groupby("size_bucket")
                        .agg(total=("count", "sum"))
                        .reset_index()
                    )
                    _sun_path = ["size_bucket"]

                _sun_height = max(280, len(_diag_plot) * 38 + 60)

                _view_sun = T("timeline_view_sunburst")
                _view_tm  = T("timeline_view_treemap")
                _view_tbl = T("timeline_view_table")

                if _right_view == _view_tbl:
                    # Detailed sortable table — top N rows (includes singletons
                    # when slider reaches them; no count >= 2 filter here)
                    _tbl = cluster_summary.head(_top_n_diag).copy()
                    _tbl["_pct"] = (_tbl["count"] / max(total_seqs, 1) * 100).round(1)
                    if _has_dates_d and "first_date" in _tbl.columns:
                        _tbl["_days"] = (
                            pd.to_datetime(_tbl["last_date"],  errors="coerce") -
                            pd.to_datetime(_tbl["first_date"], errors="coerce")
                        ).dt.days.fillna(0).astype(int)
                    _tbl_rename = {
                        "representative": T("timeline_col_clone"),
                        "count":          T("timeline_col_total"),
                        "_pct":           T("timeline_diag_pct_dataset"),
                        "_days":          T("timeline_diag_duration_days"),
                        "subtype":        T("obs_col_subtype"),
                        "clade":          T("obs_col_clade"),
                        "first_date":     T("timeline_col_first"),
                        "last_date":      T("timeline_col_last"),
                    }
                    _tbl = _tbl.rename(columns={k: v for k, v in _tbl_rename.items()
                                                if k in _tbl.columns})
                    st.dataframe(_tbl, use_container_width=True,
                                 hide_index=True, height=_sun_height)

                elif _right_view == _view_tm:
                    _fig_tm = _px_diag.treemap(
                        _sun_agg, path=_sun_path, values="total",
                        color="size_bucket",
                        color_discrete_map=_BUCKET_COLORS,
                    )
                    _fig_tm.update_traces(
                        textinfo="label+value+percent parent",
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Sequences: %{value}<br>"
                            "%{percentParent:.1%} of parent<extra></extra>"
                        ),
                    )
                    _fig_tm.update_layout(
                        margin=dict(t=0, b=0, l=0, r=0),
                        height=_sun_height,
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(_fig_tm, use_container_width=True)

                else:  # Sunburst (default)
                    _fig_sun = _px_diag.sunburst(
                        _sun_agg,
                        path=_sun_path,
                        values="total",
                        color="size_bucket",
                        color_discrete_map=_BUCKET_COLORS,
                        branchvalues="total",
                    )
                    _fig_sun.update_traces(
                        textinfo="label+percent entry",
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Sequences: %{value}<br>"
                            "%{percentEntry:.1%} of this level"
                            "<extra></extra>"
                        ),
                        insidetextorientation="radial",
                    )
                    _fig_sun.update_layout(
                        margin=dict(t=0, b=0, l=0, r=0),
                        height=_sun_height,
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(_fig_sun, use_container_width=True)

        except Exception:
            st.dataframe(
                cluster_summary.query("count >= 2").head(15),
                use_container_width=True, hide_index=True,
            )

        # ── Downloads row: raw cluster CSV + annotated interpretation CSV ─────
        _pfx_p1 = st.session_state.get("export_prefix", "virsift") or "virsift"
        _dl_c1, _dl_c2 = st.columns(2)

        with _dl_c1:
            st.download_button(
                label=T("timeline_download_cluster_csv"),
                data=cluster_summary.to_csv(index=False).encode("utf-8"),
                file_name=f"{_pfx_p1}_cluster_summary.csv",
                mime="text/csv",
                use_container_width=True,
                help=f"📄 {_pfx_p1}_cluster_summary.csv · rename prefix in sidebar",
            )

        with _dl_c2:
            # Annotated interpretation CSV — adds a Size Bucket and Implication column
            # explaining what each cluster size means epidemiologically.
            _interp_rows = []
            _BUCKET_IMPLS = [
                (T("timeline_cluster_singletons"), "×1",    T("timeline_cluster_implication_singleton")),
                (T("timeline_cluster_small"),      "×2–4",  T("timeline_cluster_implication_small")),
                (T("timeline_cluster_medium"),     "×5–9",  T("timeline_cluster_implication_medium")),
                (T("timeline_cluster_large"),      "×10–19",T("timeline_cluster_implication_large")),
                (T("timeline_cluster_major"),      "×20+",  T("timeline_cluster_implication_major")),
            ]
            def _bucket_for_n(n: int) -> str:
                if n == 1:  return T("timeline_cluster_singletons")
                if n <= 4:  return T("timeline_cluster_small")
                if n <= 9:  return T("timeline_cluster_medium")
                if n <= 19: return T("timeline_cluster_large")
                return T("timeline_cluster_major")
            _impl_map = {row[0]: row[2] for row in _BUCKET_IMPLS}
            _annot = cluster_summary.copy()
            _annot[T("timeline_cluster_size_bucket")] = _annot["count"].apply(_bucket_for_n)
            _annot[T("timeline_cluster_implication")] = _annot[T("timeline_cluster_size_bucket")].map(_impl_map)
            # Append the interpretation guide rows at the bottom, separated by a blank
            _guide_df = pd.DataFrame([
                {T("timeline_cluster_size_bucket"): b, T("timeline_cluster_size_range"): r,
                 T("timeline_cluster_implication"): imp}
                for b, r, imp in _BUCKET_IMPLS
            ])
            _annot_csv = (
                _annot.to_csv(index=False)
                + "\n\n"
                + f"# {T('timeline_cluster_dist_csv_title')}\n"
                + _guide_df.to_csv(index=False)
            )
            st.download_button(
                label=T("timeline_cluster_dist_download"),
                data=_annot_csv.encode("utf-8"),
                file_name=f"{_pfx_p1}_cluster_distribution.csv",
                mime="text/csv",
                use_container_width=True,
                help=f"📄 {_pfx_p1}_cluster_distribution.csv — includes size bucket explanations · rename prefix in sidebar",
            )
    else:
        st.info(T("timeline_all_singletons"))

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 — Configuration
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"⚙️ {T('timeline_config_header')}", expanded=True):

    cfg1, cfg2 = st.columns(2)

    with cfg1:
        min_cluster = st.slider(
            T("timeline_min_cluster_size"),
            min_value=1, max_value=500, value=3,
            help=T("timeline_min_cluster_help"),
            key="tl_min_cluster",
        )

    with cfg2:
        rep_logic = st.radio(
            T("timeline_rep_logic_label"),
            options=[
                T("timeline_rep_earliest"),
                T("timeline_rep_latest"),
                T("timeline_rep_quality"),
                T("timeline_rep_random"),
            ],
            index=0,  # default: Earliest sequence (first collected that month)
            key="tl_rep_logic",
            help=T("timeline_rep_logic_help"),
        )

    # Max sequences per month — shown when multiple occurrences exist in a month
    _max_per_month_opts = [
        T("timeline_max1"),
        T("timeline_max2"),
        T("timeline_maxn"),
        T("timeline_maxall"),
    ]
    st.selectbox(
        T("timeline_max_per_month"),
        options=_max_per_month_opts,
        index=0,
        key="tl_max_per_month",
        help=T("timeline_max_per_month_help"),
    )

    # Custom N input — shown only when "N — Custom count" is selected
    if st.session_state.get("tl_max_per_month") == T("timeline_maxn"):
        st.number_input(
            T("timeline_maxn_input"),
            min_value=3,
            max_value=1000,
            value=5,
            step=1,
            key="tl_max_n_custom",
            help="Applies per calendar month per clone. Values of 3–10 are typical.",
        )

    # Sequence identity guarantee info
    st.info(f"""
🧬 **{T('timeline_identity_guarantee_header')}**

{T('timeline_identity_guarantee_body')}
""")

# ─────────────────────────────────────────────────────────────────────────────
# Build clusters for matrix
# ─────────────────────────────────────────────────────────────────────────────
_has_dates = "collection_date" in _display_df.columns

if not _has_dates:
    st.warning(T("timeline_no_date_col"))

# Build major clusters above threshold
@st.cache_data(show_spinner=False)
def _build_clusters(df: pd.DataFrame, min_n: int) -> pd.DataFrame:
    """Cache on df content + threshold — avoids recompute on every widget interaction.

    df is passed directly so @st.cache_data hashes it as the cache key.
    Do NOT read from st.session_state inside cached functions — session state
    changes are invisible to the cache key and cause stale results across datasets.
    """
    if df.empty or "sequence_hash" not in df.columns:
        return pd.DataFrame()

    grp = (
        df.groupby("sequence_hash")
        .agg(
            count=("sequence_hash", "size"),
            representative=("isolate", "first") if "isolate" in df.columns else ("sequence_hash", "first"),
        )
        .query(f"count >= {min_n}")
        .sort_values("count", ascending=False)
    )
    if "collection_date" in df.columns:
        date_grp = df.groupby("sequence_hash")["collection_date"].agg(["min", "max"])
        grp = grp.join(date_grp)
    return grp.reset_index()


_major_clusters = _build_clusters(_display_df, min_cluster)

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3 — Interactive Timeline Matrix
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"📅 {T('timeline_matrix_header')}", expanded=True):

    st.info(f"""
**{T('timeline_matrix_how_header')}**
- {T('timeline_matrix_how1')}
- {T('timeline_matrix_how2')}
- {T('timeline_matrix_how3')}
- {T('timeline_matrix_how4')}
""")

    if _major_clusters.empty:
        st.warning(T("timeline_no_clusters", n=min_cluster))
    elif not _has_dates:
        st.error(T("timeline_matrix_needs_dates"))
    else:
        _n_clusters = len(_major_clusters)
        st.write(f"**{T('timeline_showing_clusters', n=_n_clusters, threshold=min_cluster)}**")

        if _n_clusters > 50:
            st.warning(T("timeline_too_many_clusters"))

        # Build matrix rows: one row per sequence hash cluster
        matrix_rows = []
        for _, row in _major_clusters.iterrows():
            seq_hash = row["sequence_hash"]
            cluster_seqs = _display_df[_display_df["sequence_hash"] == seq_hash].copy()

            rep_name = row.get("representative", seq_hash)
            display_name = f"{rep_name}-like (n={int(row['count'])})"

            # Months present — strftime avoids Period NaT comparison issues
            # that silently empty the list in pandas 2.x.
            try:
                _dt_col = pd.to_datetime(cluster_seqs["collection_date"], errors="coerce")
                months = sorted({dt.strftime("%Y-%m") for dt in _dt_col if pd.notna(dt)})
            except Exception:
                months = []

            if len(months) < 1:
                continue

            first_m = str(months[0])
            last_m  = str(months[-1]) if len(months) > 1 else None

            mrow = {
                "sequence_clone":  display_name,
                "sequence_hash":   seq_hash,
                "total_sequences": int(row["count"]),
                "first_seen":      first_m,
                "last_seen":       last_m or first_m,
                "months_active":   len(months),
            }

            # One checkbox column per month (intermediate months only — first/last auto-selected)
            for m in months:
                ms = str(m)
                is_anchor = (ms == first_m or ms == last_m)
                mrow[ms] = True if is_anchor else False

            matrix_rows.append(mrow)

        if matrix_rows:
            _matrix_df = pd.DataFrame(matrix_rows)

            # Identify month columns (exclude metadata columns)
            _meta_cols = ["sequence_clone", "sequence_hash", "total_sequences",
                          "first_seen", "last_seen", "months_active"]
            _month_cols = [c for c in _matrix_df.columns if c not in _meta_cols]

            # ── CSS: make checked data-editor checkboxes visually distinct ──────
            st.markdown("""
<style>
/* Blue accent for ticked month-column checkboxes in the timeline matrix */
[data-testid="stDataEditor"] .ag-cell [data-testid="glideCell-1-4"],
[data-testid="stDataEditor"] .ag-checkbox-cell-renderer .ag-icon-checkbox-checked {
    color: #0ea5e9 !important;
}
[data-testid="stDataEditor"] .ag-checkbox-cell-renderer .ag-icon-checkbox-checked::before {
    color: #0ea5e9 !important;
}
</style>
""", unsafe_allow_html=True)

            # ── Matrix guide banner ───────────────────────────────────────────
            st.info(T("timeline_matrix_guide"))

            # ── Colour-coded legend ───────────────────────────────────────────
            st.markdown(
                f"""<div style="font-size:0.85rem;margin-bottom:4px;">
<span style="display:inline-block;background:#0ea5e9;color:#fff;
      border-radius:4px;padding:1px 7px;margin-right:6px;">🔵</span>
<strong>{T('timeline_matrix_legend_anchor')}</strong>
&nbsp;&nbsp;
<span style="display:inline-block;border:1px solid #94a3b8;border-radius:4px;
      padding:1px 7px;margin-right:6px;">☐</span>
<span style="color:#64748b;">{T('timeline_matrix_legend_optional')}</span>
&nbsp;&nbsp;
<span style="display:inline-block;background:#22c55e;color:#fff;
      border-radius:4px;padding:1px 7px;margin-right:6px;">✅</span>
<strong>{T('timeline_matrix_legend_checked')}</strong>
</div>""",
                unsafe_allow_html=True,
            )

            # ── Column configuration ──────────────────────────────────────────
            _col_config = {
                "sequence_clone": st.column_config.TextColumn(
                    T("timeline_col_clone"),
                    help=T("timeline_col_clone_help"),
                    disabled=True, width="large",
                ),
                "sequence_hash":   None,  # hidden
                "total_sequences": st.column_config.NumberColumn(
                    T("timeline_col_total"),
                    help=T("timeline_col_total_help"),
                    disabled=True,
                ),
                "first_seen": st.column_config.TextColumn(
                    T("timeline_col_first"),
                    help=T("timeline_col_first_help"),
                    disabled=True,
                ),
                "last_seen": st.column_config.TextColumn(
                    T("timeline_col_last"),
                    help=T("timeline_col_last_help"),
                    disabled=True,
                ),
                "months_active": st.column_config.NumberColumn(
                    T("timeline_col_months"),
                    help=T("timeline_col_months_help"),
                    disabled=True,
                ),
            }
            for mc in _month_cols:
                _col_config[mc] = st.column_config.CheckboxColumn(
                    mc,
                    help=T("timeline_month_col_help", month=mc),
                    default=False,
                )

            _display_matrix = _matrix_df.drop(columns=["sequence_hash"])

            # Sparse matrix: absent months produce NaN — coerce to bool False.
            for _mc in _month_cols:
                if _mc in _display_matrix.columns:
                    _display_matrix[_mc] = _display_matrix[_mc].fillna(False).astype(bool)

            edited = st.data_editor(
                _display_matrix,
                use_container_width=True,
                hide_index=True,
                column_config=_col_config,
                key="timeline_matrix_editor",
                num_rows="fixed",
            )

            # Store edited matrix + hash map back into session
            st.session_state["_tl_edited_matrix"] = edited
            st.session_state["_tl_matrix_df"]     = _matrix_df
            st.session_state["_tl_month_cols"]    = _month_cols

            # Download the matrix as CSV
            _pfx_mat = st.session_state.get("export_prefix", "virsift") or "virsift"
            _dl1, _dl2 = st.columns(2)
            with _dl1:
                st.download_button(
                    label=T("timeline_download_matrix_csv"),
                    data=edited.to_csv(index=False).encode("utf-8"),
                    file_name=f"{_pfx_mat}_timeline_matrix.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help=f"📄 {_pfx_mat}_timeline_matrix.csv · rename prefix in sidebar",
                )

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 — Impact Preview & Export
# ─────────────────────────────────────────────────────────────────────────────
_matrix_is_ready = "_tl_matrix_df" in st.session_state
_has_seq_col     = "sequence" in _display_df.columns

with st.expander(f"🔬 {T('timeline_preview_header')}", expanded=True):

    # ── Smart contextual hint before the button ──────────────────────────────
    if not _has_seq_col:
        st.warning(T("timeline_no_sequence_for_extraction"))
    elif not _matrix_is_ready:
        st.info(T("timeline_configure_matrix_first"))
        st.caption(T("timeline_preview_do_steps_first"))

    # Button is always rendered — disabled (grey) when matrix isn't ready,
    # so users can see it exists and understand what they need to do first.
    _btn_disabled = not (_has_seq_col and _matrix_is_ready)
    if st.button(
        T("timeline_generate_preview_btn"),
        type="secondary" if _btn_disabled else "primary",
        key="tl_preview_btn",
        disabled=_btn_disabled,
        use_container_width=True,
        help=(T("timeline_preview_do_steps_first") if _btn_disabled
              else T("timeline_generate_preview_btn")),
    ):
        if True:  # indentation block to match original code structure

            matrix_df  = st.session_state["_tl_matrix_df"]
            edited_mat = st.session_state.get("_tl_edited_matrix", pd.DataFrame())
            month_cols = st.session_state.get("_tl_month_cols", [])

            # How many sequences to pull from a month that has multiple occurrences
            _max_opt = st.session_state.get("tl_max_per_month", T("timeline_max1"))

            # Determine single-representative selection function (used by max=1 mode)
            _rep_opt = st.session_state.get("tl_rep_logic", T("timeline_rep_quality"))
            if _rep_opt == T("timeline_rep_earliest"):
                def _pick_rep(grp):
                    return grp.sort_values("collection_date").iloc[[0]]
            elif _rep_opt == T("timeline_rep_latest"):
                def _pick_rep(grp):
                    return grp.sort_values("collection_date").iloc[[-1]]
            elif _rep_opt == T("timeline_rep_random"):
                def _pick_rep(grp):
                    return grp.sample(1)
            else:  # highest quality (fewest N's)
                def _pick_rep(grp):
                    if "sequence" in grp.columns:
                        n_counts = grp["sequence"].fillna("").str.upper().str.count("N")
                        return grp.iloc[[n_counts.argmin()]]
                    return grp.iloc[[0]]

            # Extract sequences from selected months
            selected_seqs = []

            for _, erow in edited_mat.iterrows():
                clone_name = erow["sequence_clone"]
                # find hash from matrix_df — sequence_clone IS the display_name
                seq_hash_rows = matrix_df[matrix_df["sequence_clone"] == clone_name]
                if seq_hash_rows.empty:
                    continue
                seq_hash = seq_hash_rows.iloc[0]["sequence_hash"]
                cluster_seqs = _display_df[_display_df["sequence_hash"] == seq_hash].copy()

                for mc in month_cols:
                    if mc in erow and erow[mc]:
                        try:
                            # Match by strftime string — consistent with how
                            # month keys were built (avoids Period NaT issues).
                            _dt_match = pd.to_datetime(
                                cluster_seqs["collection_date"], errors="coerce"
                            )
                            month_seqs = cluster_seqs[
                                _dt_match.apply(
                                    lambda d: d.strftime("%Y-%m") if pd.notna(d) else ""
                                ) == mc
                            ]
                            if not month_seqs.empty:
                                if _max_opt == T("timeline_maxall"):
                                    # All occurrences in this month
                                    selected_seqs.append(month_seqs)
                                elif _max_opt == T("timeline_maxn"):
                                    # Custom N: take the N earliest-collected sequences
                                    _custom_n = int(st.session_state.get("tl_max_n_custom", 5))
                                    try:
                                        _ms_sorted = month_seqs.sort_values("collection_date")
                                    except Exception:
                                        _ms_sorted = month_seqs
                                    selected_seqs.append(_ms_sorted.head(_custom_n))
                                elif _max_opt == T("timeline_max2") and len(month_seqs) >= 2:
                                    # First + Last within the month
                                    try:
                                        _ms_sorted = month_seqs.sort_values("collection_date")
                                    except Exception:
                                        _ms_sorted = month_seqs
                                    selected_seqs.append(_ms_sorted.iloc[[0]])   # earliest
                                    selected_seqs.append(_ms_sorted.iloc[[-1]])  # latest
                                else:
                                    # 1 best representative (default / max2 with only 1 seq)
                                    selected_seqs.append(_pick_rep(month_seqs))
                        except Exception:
                            pass

            if selected_seqs:
                result_df = pd.concat(selected_seqs).drop_duplicates()

                # Singleton pass-through: sequences below min_cluster are hidden from the
                # matrix UI but must still be auto-included (First + Last occurrence).
                _all_hash_counts = _display_df.groupby("sequence_hash").size()
                _small_hashes = _all_hash_counts[_all_hash_counts < min_cluster].index
                if len(_small_hashes) > 0:
                    _sing_parts = []
                    for _sh in _small_hashes:
                        _raw = _display_df[_display_df["sequence_hash"] == _sh]
                        try:
                            _sg = _raw.sort_values("collection_date")
                        except (TypeError, KeyError):
                            _sg = _raw
                        _sing_parts.append(_sg.iloc[[0]])      # first date
                        if len(_sg) > 1:
                            _sing_parts.append(_sg.iloc[[-1]])  # last date
                    if _sing_parts:
                        _sing_df = pd.concat(_sing_parts).drop_duplicates()
                        result_df = pd.concat([result_df, _sing_df]).drop_duplicates()
                        st.caption(T("timeline_singletons_included",
                                     n=len(_sing_df), total=len(_small_hashes)))

                # ── Overlaid epidemic curve: grey mountain (raw) + blue bars (curated) ──
                try:
                    import plotly.graph_objects as _go_imp

                    if "collection_date" in _display_df.columns:
                        _raw_ts = (
                            pd.to_datetime(_display_df["collection_date"], errors="coerce")
                            .dt.to_period("M").astype(str)
                            .value_counts().sort_index().reset_index()
                        )
                        _raw_ts.columns = ["Month", "Count"]

                        _cur_ts = (
                            pd.to_datetime(result_df["collection_date"], errors="coerce")
                            .dt.to_period("M").astype(str)
                            .value_counts().sort_index().reset_index()
                        ) if "collection_date" in result_df.columns else pd.DataFrame(columns=["Month", "Count"])
                        _cur_ts.columns = ["Month", "Count"] if not _cur_ts.empty else _cur_ts.columns

                        _all_months = sorted(set(_raw_ts["Month"]) | set(_cur_ts["Month"]))
                        _raw_lookup = dict(zip(_raw_ts["Month"], _raw_ts["Count"]))
                        _cur_lookup = dict(zip(_cur_ts["Month"], _cur_ts["Count"])) if not _cur_ts.empty else {}
                        _raw_y = [_raw_lookup.get(m, 0) for m in _all_months]
                        _cur_y = [_cur_lookup.get(m, 0) for m in _all_months]

                        _fig_imp = _go_imp.Figure()
                        # Grey filled mountain — raw / all sequences
                        _fig_imp.add_trace(_go_imp.Scatter(
                            x=_all_months, y=_raw_y,
                            fill="tozeroy",
                            mode="lines",
                            line=dict(color="#94a3b8", width=1.5),
                            fillcolor="rgba(148,163,184,0.25)",
                            name=T("timeline_raw_label"),
                            hovertemplate="%{x}<br>Raw: %{y:,}<extra></extra>",
                        ))
                        # Curated foreground bars — colour from sidebar scheme
                        _fig_imp.add_trace(_go_imp.Bar(
                            x=_all_months, y=_cur_y,
                            name=T("timeline_curated_label"),
                            marker_color=_tl_pal["accent"],
                            opacity=0.85,
                            hovertemplate="%{x}<br>Curated: %{y:,}<extra></extra>",
                        ))
                        _fig_imp.update_layout(
                            title=T("timeline_impact_chart_title"),
                            barmode="overlay",
                            margin=dict(t=40, b=0, l=0, r=0),
                            height=300,
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            legend=dict(orientation="h", y=1.14, x=0),
                            xaxis=dict(tickangle=-45),
                        )
                        st.plotly_chart(_fig_imp, use_container_width=True)
                except Exception:
                    pass

                # ── 4-card curation impact metrics ────────────────────────────────
                st.divider()
                st.subheader(T("timeline_curation_impact"))

                compression = (1 - len(result_df) / max(len(_display_df), 1)) * 100
                _seqs_removed = len(_display_df) - len(result_df)
                _coverage_str = "N/A"
                if "collection_date" in _display_df.columns and "collection_date" in result_df.columns:
                    _raw_periods = pd.to_datetime(_display_df["collection_date"], errors="coerce").dt.to_period("M").nunique()
                    _cur_periods = pd.to_datetime(result_df["collection_date"], errors="coerce").dt.to_period("M").nunique()
                    _coverage_str = f"{(_cur_periods / max(_raw_periods, 1) * 100):.0f}%"

                im1, im2, im3, im4 = st.columns(4)
                im1.metric(
                    T("timeline_total_sequences"),
                    f"{len(_display_df):,} → {len(result_df):,}",
                    help="Sequence count before and after timeline curation.",
                )
                im2.metric(T("timeline_compression"), f"{compression:.1f}%")
                im3.metric(T("timeline_seqs_removed"), f"{_seqs_removed:,}")
                im4.metric(T("timeline_coverage"), _coverage_str)

                # Store result
                st.session_state["filtered_df"] = result_df
                st.success(T("timeline_extraction_success", n=len(result_df)))

                # Export buttons
                st.divider()
                _pfx_ex = st.session_state.get("export_prefix", "virsift") or "virsift"
                ex1, ex2, ex3 = st.columns(3)

                with ex1:
                    # FASTA export
                    try:
                        from utils.gisaid_parser import convert_df_to_fasta
                        fasta_out = convert_df_to_fasta(result_df)
                    except Exception:
                        # Fallback FASTA builder
                        lines = []
                        for _, r in result_df.iterrows():
                            hdr = r.get("isolate", r.get("sequence_hash", "seq"))
                            seq = r.get("sequence", "")
                            lines.append(f">{hdr}")
                            lines.append(seq)
                        fasta_out = "\n".join(lines).encode("utf-8")
                    st.download_button(
                        label=T("download_fasta_label", count=len(result_df)),
                        data=fasta_out,
                        file_name=f"{_pfx_ex}_timeline_curated.fasta",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True,
                        help=f"📄 {_pfx_ex}_timeline_curated.fasta · rename prefix in sidebar",
                    )

                with ex2:
                    # Metadata CSV
                    meta_cols = [c for c in result_df.columns if c != "sequence"]
                    st.download_button(
                        label=T("download_csv_label"),
                        data=result_df[meta_cols].to_csv(index=False).encode("utf-8"),
                        file_name=f"{_pfx_ex}_timeline_metadata.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help=f"📄 {_pfx_ex}_timeline_metadata.csv · rename prefix in sidebar",
                    )

                with ex3:
                    # Methodology JSON snapshot
                    snapshot = {
                        "tool": "Vir-Seq-Sift v2.1 — Molecular Timeline Tracker",
                        "exported": datetime.now().isoformat(),
                        "representative_logic": _rep_opt,
                        "min_cluster_size": min_cluster,
                        "input_sequences": len(_display_df),
                        "output_sequences": len(result_df),
                        "compression_pct": round(compression, 2),
                    }
                    st.download_button(
                        label=T("download_json_label"),
                        data=json.dumps(snapshot, indent=2, ensure_ascii=False).encode("utf-8"),
                        file_name=f"{_pfx_ex}_timeline_methodology.json",
                        mime="application/json",
                        use_container_width=True,
                        help=f"📄 {_pfx_ex}_timeline_methodology.json · rename prefix in sidebar",
                    )
            else:
                st.warning(T("timeline_no_months_selected"))

# ─────────────────────────────────────────────────────────────────────────────
# Per-page sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.divider()
    st.markdown(f"**{T('sidebar_timeline_controls')}**")
    if not _display_df.empty:
        _unique_clones = _display_df["sequence_hash"].nunique() if "sequence_hash" in _display_df.columns else 0
        st.metric(T("timeline_unique_clones"), f"{_unique_clones:,}")
        st.metric(T("timeline_total_sequences"), f"{len(_display_df):,}")
    st.caption(T("timeline_sidebar_tip"))

    # ── Chart colour scheme — live swatch (control is inline above cluster chart) ──
    st.markdown(f"**{T('timeline_chart_colour')}**")
    _sb_accent = _TIMELINE_PALETTES.get(
        st.session_state.get("timeline_chart_scheme", "🔵 Ocean Blue"),
        _TIMELINE_PALETTES["🔵 Ocean Blue"],
    )["accent"]
    st.markdown(
        f"<div style='height:7px;border-radius:3px;margin-top:4px;"
        f"background:linear-gradient(90deg,{_sb_accent}55,{_sb_accent})'></div>",
        unsafe_allow_html=True,
    )
    st.caption(T("timeline_chart_colour_help"))

# ─────────────────────────────────────────────────────────────────────────────
# Inter-page navigation
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
_tl_n1, _tl_n2 = st.columns(2)
try:
    _tl_n1.page_link("pages/03_🔬_Sequence_Refinery.py",
                     label=f"← 🔬 {T('nav_refinery')}",
                     use_container_width=True)
    _tl_n2.page_link("pages/05_📊_Analytics.py",
                     label=f"📊 {T('nav_analytics')} →",
                     use_container_width=True)
except AttributeError:
    _tl_n1.markdown(f"[← 🔬 {T('nav_refinery')}](pages/03_🔬_Sequence_Refinery.py)")
    _tl_n2.markdown(f"[📊 {T('nav_analytics')} →](pages/05_📊_Analytics.py)")
