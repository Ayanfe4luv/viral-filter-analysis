# -*- coding: utf-8 -*-
"""
pages/03_🔬_Sequence_Refinery.py — Pre-Processing, Filtering & HITL Sampling

CRITICAL STATE RULE:
  All filtering writes to session_state['filtered_df'] ONLY.
  Never read from or write to session_state['active_df'] here.
  Visual Lasso chart MUST use aggregated bar counts — never raw dots.
"""

import json

import pandas as pd
import streamlit as st

from utils.gisaid_parser import convert_df_to_fasta
from utils.minimal_i18n import T
from utils.vectorized_filters import VectorizedFilterEngine

st.title(f"🧬 {T('nav_filter_lab')}")

_active_df: pd.DataFrame = st.session_state.get("active_df", pd.DataFrame())

if _active_df.empty:
    st.warning(T("error_no_active_df"))
    st.stop()

engine = VectorizedFilterEngine()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _working_df() -> pd.DataFrame:
    """Return filtered_df if non-empty, else active_df — the current working set."""
    fdf = st.session_state.get("filtered_df", pd.DataFrame())
    return fdf if not fdf.empty else _active_df.copy()


def _save_filtered(df: pd.DataFrame, action: str) -> None:
    """Write result to session_state['filtered_df'] and append action log."""
    st.session_state["filtered_df"] = df
    st.session_state["action_logs"].append({
        "action":    action,
        "sequences": len(df),
        "timestamp": pd.Timestamp.now().isoformat(),
    })


def _download_row(df: pd.DataFrame, label_prefix: str) -> None:
    """Render primary FASTA + secondary CSV download buttons side-by-side."""
    if df.empty:
        return
    _pfx = st.session_state.get("export_prefix", "virsift") or "virsift"
    _slug = label_prefix.lower().replace(" ", "_")
    c1, c2 = st.columns(2)
    fasta_str = convert_df_to_fasta(df)
    c1.download_button(
        label=f"⬇ {label_prefix} — FASTA ({len(df):,} seqs)",
        data=fasta_str.encode("utf-8"),
        file_name=f"{_pfx}_{_slug}.fasta",
        mime="text/plain",
        type="primary",
        use_container_width=True,
        help=f"📄 {_pfx}_{_slug}.fasta · rename prefix in sidebar",
    )
    csv_bytes = df.drop(columns=["sequence"], errors="ignore").to_csv(index=False).encode("utf-8")
    c2.download_button(
        label=f"⬇ {label_prefix} — CSV ({len(df):,} rows)",
        data=csv_bytes,
        file_name=f"{_pfx}_{_slug}.csv",
        mime="text/csv",
        use_container_width=True,
        help=f"📄 {_pfx}_{_slug}.csv · rename prefix in sidebar",
    )


# ---------------------------------------------------------------------------
# Per-file scope selector (multi-file datasets only)
# ---------------------------------------------------------------------------

_ref_raw_files: list = st.session_state.get("raw_files", [])
_ref_action_logs: list = st.session_state.get("action_logs", [])
_ref_last_act = next(
    (lg for lg in reversed(_ref_action_logs) if lg.get("action") == "activate"), None
)
_ref_act_names: list = (
    _ref_last_act.get("files", []) if _ref_last_act
    else ([_ref_raw_files[0]["name"]] if _ref_raw_files else [])
)
_ref_contrib = [rf for rf in _ref_raw_files if rf["name"] in _ref_act_names]

if len(_ref_contrib) > 1:
    _ref_scope_opts = [T("timeline_scope_all")] + [rf["name"] for rf in _ref_contrib]
    _ref_scope = st.radio(
        T("timeline_scope_label"),
        options=_ref_scope_opts,
        index=st.session_state.get("ref_scope_idx", 0),
        horizontal=True,
        key="ref_file_scope",
        help=T("timeline_scope_help"),
    )
    st.session_state["ref_scope_idx"] = _ref_scope_opts.index(_ref_scope)
    if _ref_scope != T("timeline_scope_all"):
        _ref_rf = next(rf for rf in _ref_contrib if rf["name"] == _ref_scope)
        _active_df = pd.DataFrame(_ref_rf["parsed"])
        st.success(T("timeline_scope_file_badge", file=_ref_scope, n=len(_active_df)))
    else:
        st.caption(T("timeline_scope_all_caption", n=len(_ref_contrib)))
    st.divider()


# ---------------------------------------------------------------------------
# Status banner
# ---------------------------------------------------------------------------

current = _working_df()
c1, c2, c3 = st.columns(3)
c1.metric(T("filter_status_active"), f"{len(_active_df):,}")
c2.metric(T("filter_status_after"),  f"{len(current):,}")
delta = len(current) - len(_active_df)
c3.metric(T("filter_status_delta"),  f"{delta:+,}", delta_color="inverse")

if not st.session_state.get("filtered_df", pd.DataFrame()).empty:
    if st.button(T("filter_reset_btn"), type="secondary"):
        st.session_state["filtered_df"] = pd.DataFrame()
        st.rerun()

st.divider()


# ===========================================================================
# PHASE 2 — SECTION A: Quality Filters
# ===========================================================================

with st.expander(f"🔬 {T('filter_quality_header')}", expanded=True):
    st.caption(T("filter_quality_caption"))

    col_len, col_n = st.columns(2)

    with col_len:
        default_min = 100
        max_len = 5000
        if "sequence_length" in _active_df.columns:
            p5 = int(_active_df["sequence_length"].quantile(0.05))
            default_min = max(100, p5)
            max_len = int(_active_df["sequence_length"].max())
        min_len = st.slider(
            T("filter_min_length"),
            min_value=0,
            max_value=max_len,
            value=default_min,
            step=50,
            help=T("filter_min_length_help"),
        )

    with col_n:
        max_n_run = st.slider(
            T("filter_max_n_run"),
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help=T("filter_max_n_run_help"),
        )

    dedup_mode = st.radio(
        T("filter_dedup_label"),
        options=["None", "sequence", "seq+subtype"],
        horizontal=True,
        help=T("filter_dedup_help"),
    )

    std_headers = st.toggle(T("filter_std_headers"), value=False,
                            help=T("filter_std_headers_help"))

    if st.button(T("filter_apply_quality"), type="primary", use_container_width=True):
        result = _active_df.copy()

        with st.spinner(T("filter_applying")):
            result = engine.filter_min_length(result, min_len)
            result = engine.filter_max_n_run(result, max_n_run)
            if dedup_mode != "None":
                result = engine.deduplicate(result, mode=dedup_mode)
            if std_headers and "isolate" in result.columns:
                result["isolate"] = result["isolate"].str.strip()

        _save_filtered(result, "quality_filter")
        removed = len(_active_df) - len(result)
        st.success(
            f"{T('filter_quality_header')} — {len(result):,} sequences retained "
            f"({removed:,} removed)."
        )
        _download_row(result, "Quality Filtered")
        st.rerun()


# ===========================================================================
# PHASE 2 — SECTION B: Header Component Filters (VectorizedFilterEngine)
# ===========================================================================

with st.expander(f"🏷 {T('filter_header_comp_header')}"):
    st.caption(T("filter_header_comp_caption"))

    available_fields = engine.auto_detect_available_fields(current)

    if not available_fields:
        st.info("No populated metadata fields detected in the current dataset.")
    else:
        if "filter_rules" not in st.session_state:
            st.session_state["filter_rules"] = []

        rules: list = st.session_state["filter_rules"]

        st.markdown(f"**{T('filter_add_rule_header')}**")
        ra, rb, rc, rd = st.columns([2, 2, 3, 1])
        with ra:
            new_field = st.selectbox(
                T("filter_field_label"), options=list(available_fields.keys()), key="new_field"
            )
        with rb:
            new_op = st.selectbox(
                T("filter_operator_label"),
                options=["equals", "not_equals", "contains", "not_contains",
                         "starts_with", "in_list", "date_range", "regex"],
                key="new_op",
            )
        with rc:
            new_val = st.text_input(
                T("filter_value_label"),
                key="new_val",
                placeholder=T("filter_value_placeholder"),
            )
        with rd:
            st.write("")
            st.write("")
            if st.button(T("filter_add_rule_btn"), use_container_width=True):
                if new_val.strip():
                    value = new_val.strip()
                    if new_op == "in_list":
                        value = [v.strip() for v in new_val.split(",")]
                    elif new_op == "date_range":
                        parts = [v.strip() for v in new_val.split(",")]
                        try:
                            value = [pd.Timestamp(parts[0]),
                                     pd.Timestamp(parts[1] if len(parts) > 1 else parts[0])]
                        except Exception:
                            st.error(T("filter_date_error"))
                            value = None
                    if value is not None:
                        rules.append({"field": new_field, "operator": new_op, "value": value})
                        st.session_state["filter_rules"] = rules
                        st.rerun()

        if rules:
            st.markdown(f"**{T('filter_active_rules')}**")
            for i, rule in enumerate(rules):
                col_r, col_del = st.columns([5, 1])
                col_r.code(f"{rule['field']}  {rule['operator']}  {rule['value']}")
                if col_del.button(T("filter_remove_rule"), key=f"del_rule_{i}"):
                    rules.pop(i)
                    st.session_state["filter_rules"] = rules
                    st.rerun()

            if st.button(T("filter_apply_header"), type="primary", use_container_width=True):
                with st.spinner(T("filter_applying")):
                    result = engine.apply_header_component_filters(current, rules)
                _save_filtered(result, "header_component_filter")
                st.success(T("filter_header_success", n=f"{len(result):,}"))
                _download_row(result, "Filtered")
                st.rerun()
        else:
            st.info(T("filter_no_rules_info"))


# ===========================================================================
# PHASE 2 — SECTION C: EPI_ISL Accession Filter
# ===========================================================================

with st.expander(f"🔑 {T('filter_accession_header')}"):
    st.caption(T("filter_accession_caption"))

    acc_text = st.text_area(
        T("filter_accession_input"),
        height=120,
        placeholder="EPI_ISL_123456\nEPI_ISL_789012\n...",
        help=T("filter_accession_help"),
    )

    if st.button(T("filter_apply_accession"), disabled=not acc_text.strip(),
                 use_container_width=True):
        acc_list = [a.strip() for a in acc_text.replace(",", "\n").splitlines() if a.strip()]
        with st.spinner(T("filter_applying")):
            result = engine.filter_accessions(current, acc_list)
        _save_filtered(result, "accession_filter")
        st.success(T("filter_acc_success", n=f"{len(result):,}", total=len(acc_list)))
        _download_row(result, "Accession Filtered")
        st.rerun()


# ===========================================================================
# PHASE 3 — SECTION D: Smart Phylogenetic Down-sampling (HITL)
# ===========================================================================

with st.expander(f"🧠 {T('hitl_header')}"):
    st.caption(T("hitl_caption"))

    from utils.adaptive_sampler import AdaptiveBiologicalSampler
    from utils.peak_detector import EpiWaveDetector

    sampler  = AdaptiveBiologicalSampler()
    detector = EpiWaveDetector()

    category = sampler.calculate_lifespan_category(current)
    st.info(
        f"**{T('filter_lifespan_label')}** {category}  "
        f"({'<90d' if category == 'Micro' else '90–270d' if category == 'Seasonal' else '>270d'})"
    )

    _lifespan_rec = {
        "Micro":    ("hitl_rec_micro",    "⚡"),
        "Seasonal": ("hitl_rec_seasonal", "📅"),
        "Endemic":  ("hitl_rec_endemic",  "🌍"),
    }
    _rec_key, _rec_icon = _lifespan_rec.get(category, ("hitl_rec_endemic", "🌍"))
    st.markdown(
        f"""<div style="background:rgba(14,165,233,.1);border-left:4px solid #0ea5e9;
        border-radius:4px;padding:8px 12px;margin:6px 0">
        {_rec_icon} <strong>{T('hitl_rec_label')}:</strong> {T(_rec_key)}</div>""",
        unsafe_allow_html=True,
    )

    strategy = st.radio(
        T("hitl_strategy_label"),
        options=[
            T("hitl_strategy_chronological"),
            T("hitl_strategy_volume"),
            T("hitl_strategy_checklist"),
            T("hitl_strategy_lasso"),
            T("hitl_strategy_checkpoints"),
        ],
        key="hitl_strategy",
        help=T("hitl_strategy_help"),
    )

    # -----------------------------------------------------------------------
    # Strategy 1 — Chronological Sentinel
    # -----------------------------------------------------------------------
    if strategy == T("hitl_strategy_chronological"):
        st.markdown(T("hitl_chron_desc"))
        st.info(T("hitl_chron_when_to_use"))
        if st.button(T("hitl_apply_chron"), type="primary", use_container_width=True):
            with st.spinner(T("hitl_sampling")):
                result = sampler.apply_proportionality_rule(current, category)
            _save_filtered(result, "adaptive_sampling")
            st.success(
                f"{T('hitl_strategy_chronological')} — "
                f"{len(result):,} sequences selected (from {len(current):,})."
            )
            _download_row(result, "Adaptive Sample")
            st.rerun()

    # -----------------------------------------------------------------------
    # Strategy 2 — Highest Volume Peaks
    # -----------------------------------------------------------------------
    elif strategy == T("hitl_strategy_volume"):
        st.markdown(T("hitl_volume_desc"))
        sensitivity = st.slider(
            T("hitl_sensitivity"), min_value=0.1, max_value=1.0, value=0.5, step=0.05
        )
        with st.expander(T("hitl_sensitivity_guide_header"), expanded=False):
            st.markdown(T("hitl_sensitivity_guide_body"))
        if st.button(T("hitl_apply_volume"), type="primary", use_container_width=True):
            with st.spinner(T("hitl_sampling")):
                waves = detector.detect_epi_waves(current, sensitivity=sensitivity)
                result = detector.extract_wave_representatives(current, waves)
            _save_filtered(result, "volume_peak_sampling")
            st.success(
                f"{T('hitl_strategy_volume')} — {waves['wave_count']} waves detected, "
                f"{len(result):,} representative sequences selected."
            )
            _download_row(result, "Volume Sample")
            st.rerun()

    # -----------------------------------------------------------------------
    # Strategy 3 — Manual Peak Checklist
    # -----------------------------------------------------------------------
    elif strategy == T("hitl_strategy_checklist"):
        st.markdown(T("hitl_checklist_desc"))
        sensitivity = st.slider(
            T("hitl_sensitivity"), min_value=0.1, max_value=1.0, value=0.5, step=0.05,
            key="checklist_sens"
        )
        with st.expander(T("hitl_sensitivity_guide_header"), expanded=False):
            st.markdown(T("hitl_sensitivity_guide_body"))
        candidates = detector.detect_candidate_peaks(current, sensitivity=sensitivity)

        if not candidates:
            st.warning(T("hitl_no_peaks"))
        else:
            st.markdown(f"**{len(candidates)} candidate periods detected:**")
            selected_periods = []
            for cand in candidates:
                label = (
                    f"{cand['date']}  —  {cand['count']:,} seqs  "
                    f"[{cand['type']}"
                    + (f", rank #{cand['rank']}" if cand.get("rank") else "")
                    + "]"
                )
                if st.checkbox(label, value=(cand["type"] == "Major Peak"),
                               key=f"ck_{cand['date']}"):
                    selected_periods.append(cand["date"])

            if st.button(T("hitl_apply_checklist"), type="primary",
                         disabled=not selected_periods, use_container_width=True):
                st.session_state["selected_peaks"] = selected_periods
                with st.spinner(T("hitl_sampling")):
                    df_work = current.copy()
                    df_work["_period"] = (
                        pd.to_datetime(df_work["collection_date"], errors="coerce")
                        .dt.to_period("W").astype(str)
                    )
                    result = (
                        df_work[df_work["_period"].isin(selected_periods)]
                        .drop(columns=["_period"])
                    )
                _save_filtered(result, "peak_checklist_sampling")
                st.success(
                    f"Checklist sampling — {len(result):,} sequences from "
                    f"{len(selected_periods)} selected periods."
                )
                _download_row(result, "Checklist Sample")
                st.rerun()

    # -----------------------------------------------------------------------
    # Strategy 4 — Visual Chart Lasso (aggregated bars ONLY)
    # -----------------------------------------------------------------------
    elif strategy == T("hitl_strategy_lasso"):
        try:
            import plotly.graph_objects as go

            st.markdown(T("hitl_lasso_desc"))
            st.caption(T("hitl_lasso_caption"))

            ts = detector._build_weekly_counts(current)
            if ts.empty:
                st.warning(T("hitl_no_dates"))
            else:
                fig = go.Figure(go.Bar(
                    x=ts.index.tolist(),
                    y=ts.values.tolist(),
                    marker_color="steelblue",
                    name="Weekly sequences",
                ))
                fig.update_layout(
                    title=T("hitl_lasso_chart_title"),
                    xaxis_title=T("hitl_lasso_x"),
                    yaxis_title=T("hitl_lasso_y"),
                    dragmode="select",
                    height=350,
                    margin=dict(t=40, b=40),
                )

                event = st.plotly_chart(
                    fig,
                    use_container_width=True,
                    on_select="rerun",
                    selection_mode="box",
                    key="lasso_chart",
                )

                sel = (event or {}).get("selection", {})
                box_list = sel.get("box", []) if sel else []
                x_range = box_list[0] if box_list else None

                if x_range and "x" in x_range:
                    x0, x1 = sorted(x_range["x"])
                    selected_periods = [p for p in ts.index if x0 <= p <= x1]
                    st.session_state["lasso_zones"] = selected_periods
                else:
                    selected_periods = st.session_state.get("lasso_zones", [])

                if selected_periods:
                    st.success(
                        f"Selected {len(selected_periods)} week(s): "
                        f"{selected_periods[0]} → {selected_periods[-1]}"
                    )
                    if st.button(T("hitl_apply_lasso"), type="primary",
                                 use_container_width=True):
                        df_work = current.copy()
                        df_work["_period"] = (
                            pd.to_datetime(df_work["collection_date"], errors="coerce")
                            .dt.to_period("W").astype(str)
                        )
                        result = (
                            df_work[df_work["_period"].isin(selected_periods)]
                            .drop(columns=["_period"])
                        )
                        _save_filtered(result, "lasso_sampling")
                        st.success(
                            f"Lasso sampling — {len(result):,} sequences "
                            f"from {len(selected_periods)} weeks."
                        )
                        _download_row(result, "Lasso Sample")
                        st.rerun()
                else:
                    st.info(T("hitl_lasso_no_selection"))

        except ImportError:
            st.error("plotly not installed. Run: pip install plotly")

    # -----------------------------------------------------------------------
    # Strategy 5 — Custom Time Checkpoints
    # -----------------------------------------------------------------------
    elif strategy == T("hitl_strategy_checkpoints"):
        st.markdown(T("hitl_checkpoints_desc"))

        checkpoint_text = st.text_area(
            T("hitl_checkpoints_input"),
            height=120,
            placeholder="2022-01\n2022-07\n2023-01\n...",
            help=T("hitl_checkpoints_help"),
        )

        _tol_presets = ["3D", "5D", "1W", "2W", "1M", "2M", "3M", T("hitl_tol_custom")]
        tolerance = st.selectbox(
            T("hitl_checkpoints_tolerance"),
            options=_tol_presets,
            index=3,
            help=T("hitl_checkpoints_tolerance_help"),
        )
        _tol_day_map = {"3D": 3, "5D": 5, "1W": 7, "2W": 14, "1M": 30, "2M": 60, "3M": 90}
        if tolerance == T("hitl_tol_custom"):
            tol_days = st.number_input(
                T("hitl_tol_custom_days"),
                min_value=1, max_value=365, value=10, step=1,
                key="hitl_custom_tol_days",
            )
        else:
            tol_days = _tol_day_map.get(tolerance, 14)
        st.caption(T("hitl_tol_preview", days=tol_days))
        tol = pd.Timedelta(f"{tol_days}D")

        if st.button(T("hitl_apply_checkpoints"), type="primary",
                     disabled=not checkpoint_text.strip(), use_container_width=True):
            checkpoints = [
                pd.Timestamp(c.strip())
                for c in checkpoint_text.splitlines()
                if c.strip()
            ]
            st.session_state["checkpoint_targets"] = [str(c) for c in checkpoints]

            df_work = current.copy()
            dates = pd.to_datetime(df_work["collection_date"], errors="coerce")

            selected_idx = set()
            for cp in checkpoints:
                diff = (dates - cp).abs()
                in_window = diff[diff <= tol].index
                selected_idx.update(in_window.tolist())

            result = df_work.loc[sorted(selected_idx)]
            _save_filtered(result, "checkpoint_sampling")
            st.success(
                f"Checkpoint sampling — {len(result):,} sequences "
                f"near {len(checkpoints)} checkpoints (\u00b1{tol_days}d)."
            )
            _download_row(result, "Checkpoint Sample")
            st.rerun()


# ===========================================================================
# Download section — current filtered set
# ===========================================================================

filtered_df = st.session_state.get("filtered_df", pd.DataFrame())
if not filtered_df.empty:
    st.divider()
    st.subheader(T("download_section_header"))
    st.caption(f"{len(filtered_df):,} {T('download_current_label')}")

    _download_row(filtered_df, "Filtered")

    action_logs = st.session_state.get("action_logs", [])
    filter_logs = [a for a in action_logs if a.get("action") not in ("parse", "activate")]
    if filter_logs:
        methodology = {
            "tool":    "Vir-Seq-Sift v2.1",
            "filters": filter_logs,
            "result":  {
                "sequences":        len(filtered_df),
                "active_sequences": len(_active_df),
            },
        }
        st.download_button(
            label=T("download_methodology_label"),
            data=json.dumps(methodology, indent=2, default=str).encode("utf-8"),
            file_name=f"{st.session_state.get('export_prefix', 'virsift') or 'virsift'}_methodology.json",
            mime="application/json",
            help=T("download_methodology_help"),
        )


# ---------------------------------------------------------------------------
# Page navigation arrows
# ---------------------------------------------------------------------------

st.divider()
_pn1, _pn2 = st.columns(2)
try:
    _pn1.page_link("pages/02_📁_Workspace.py",
                   label=f"← 📁 {T('nav_workspace')}", use_container_width=True)
    _pn2.page_link("pages/05_📊_Analytics.py",
                   label=f"📊 {T('nav_analytics')} →", use_container_width=True)
except AttributeError:
    pass  # st.page_link available in Streamlit ≥ 1.29

# ---------------------------------------------------------------------------
# Per-page sidebar — quick FASTA download + filter badge
# ---------------------------------------------------------------------------

with st.sidebar:
    st.divider()
    _fl_filtered = st.session_state.get("filtered_df", pd.DataFrame())
    if not _fl_filtered.empty:
        st.metric(T("sidebar_fl_sequences"), f"{len(_fl_filtered):,}")
        _fl_fasta = convert_df_to_fasta(_fl_filtered)
        st.download_button(
            label=T("sidebar_fl_download", n=len(_fl_filtered)),
            data=_fl_fasta.encode("utf-8") if isinstance(_fl_fasta, str) else _fl_fasta,
            file_name=f"{st.session_state.get('export_prefix', 'virsift') or 'virsift'}_filtered.fasta",
            mime="text/plain",
            use_container_width=True,
            type="primary",
            key="fl_sb_download",
        )
    _fl_filters = st.session_state.get("global_filters", [])
    if _fl_filters:
        st.caption(f"{len(_fl_filters)} {T('sidebar_global_filters', count=len(_fl_filters)).split('(')[0].strip()}")
