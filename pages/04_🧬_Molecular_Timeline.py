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

    # Caption about source
    _src = "filtered" if not _filtered_df.empty else "active"
    st.caption(T("timeline_data_source", src=_src))

    # Top duplicate clusters preview
    if unique_hashes < total_seqs:
        # Build full cluster summary (all sizes) for sunburst + top-N for bar
        _has_dates_d   = "collection_date" in _display_df.columns
        _has_subtype_d = "subtype" in _display_df.columns
        _has_isolate_d = "isolate" in _display_df.columns

        _agg_spec: dict = {
            "count":          ("sequence_hash", "size"),
            "representative": ("isolate", "first") if _has_isolate_d else ("sequence_hash", "first"),
        }
        if _has_dates_d:
            _agg_spec["first_date"] = ("collection_date", "min")
            _agg_spec["last_date"]  = ("collection_date", "max")
        if _has_subtype_d:
            _agg_spec["subtype"] = ("subtype", "first")

        cluster_summary = (
            _display_df.groupby("sequence_hash")
            .agg(**_agg_spec)
            .sort_values("count", ascending=False)
            .reset_index(drop=True)
        )

        st.subheader(T("timeline_top_clusters"))
        try:
            import plotly.express as _px_diag

            _col_bar, _col_sun = st.columns([2, 1])

            # ── Left: enhanced horizontal bar (top 12 multi-sequence clusters) ──
            with _col_bar:
                _diag_plot = cluster_summary.query("count >= 2").head(12).sort_values("count").copy()

                # Color by circulation duration (days) when dates are available
                if _has_dates_d and "first_date" in _diag_plot.columns and "last_date" in _diag_plot.columns:
                    try:
                        _diag_plot["_duration"] = (
                            pd.to_datetime(_diag_plot["last_date"],  errors="coerce") -
                            pd.to_datetime(_diag_plot["first_date"], errors="coerce")
                        ).dt.days.fillna(0).clip(lower=0).astype(int)
                        _color_col  = "_duration"
                        _cbar_title = "Days in circulation"
                        _cdata      = ["first_date", "last_date"]
                        _hover_tmpl = (
                            "<b>%{y}</b><br>"
                            "Sequences: %{x}<br>"
                            "First seen: %{customdata[0]}<br>"
                            "Last seen: %{customdata[1]}<extra></extra>"
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
                _fig_diag.update_traces(hovertemplate=_hover_tmpl)
                _fig_diag.update_layout(
                    margin=dict(t=10, b=0, l=0, r=10),
                    height=max(240, len(_diag_plot) * 34 + 60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=True,
                    coloraxis_colorbar=dict(title=_cbar_title, thickness=12, len=0.7),
                    yaxis_title=None,
                    xaxis_title=T("timeline_diag_axis_count"),
                )
                st.plotly_chart(_fig_diag, use_container_width=True)

            # ── Right: multi-level sunburst (size bucket × subtype) ─────────────
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

                if _has_subtype_d and "subtype" in _sun_df.columns:
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

                _fig_sun = _px_diag.sunburst(
                    _sun_agg,
                    path=_sun_path,
                    values="total",
                    color="total",
                    color_continuous_scale=_tl_pal["seq"],
                )
                _fig_sun.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=max(240, len(_diag_plot) * 34 + 60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                )
                st.plotly_chart(_fig_sun, use_container_width=True)

        except Exception:
            st.dataframe(
                cluster_summary.query("count >= 2").head(15),
                use_container_width=True, hide_index=True,
            )

        # CSV download of full cluster summary (duplicate clusters only)
        st.download_button(
            label=T("timeline_download_cluster_csv"),
            data=cluster_summary.query("count >= 2").to_csv(index=False).encode("utf-8"),
            file_name=f"timeline_clusters_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
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
            min_value=2, max_value=20, value=3,
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
            index=2,  # default: highest quality
            key="tl_rep_logic",
            help=T("timeline_rep_logic_help"),
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
def _build_clusters(_df_hash: str, min_n: int) -> pd.DataFrame:
    """Cache on df hash + threshold — avoids recompute on every widget interaction.

    _df_hash is an intentional @st.cache_data discriminator: Streamlit uses it
    as a cache key so the function re-runs when the underlying DataFrame changes.
    The leading underscore suppresses the unused-parameter linter hint.
    """
    df = st.session_state.get("active_df", pd.DataFrame())
    if st.session_state.get("filtered_df") is not None and not st.session_state["filtered_df"].empty:
        df = st.session_state["filtered_df"]
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


_df_hash = hashlib.md5(pd.util.hash_pandas_object(_display_df, index=True).values.tobytes()).hexdigest()[:12]
_major_clusters = _build_clusters(_df_hash, min_cluster)

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

            # Months present
            try:
                cluster_seqs["_month"] = pd.to_datetime(
                    cluster_seqs["collection_date"], errors="coerce"
                ).dt.to_period("M")
                months = sorted(cluster_seqs["_month"].dropna().unique())
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

            # Build column config for data_editor
            _col_config = {
                "sequence_clone":  st.column_config.TextColumn(T("timeline_col_clone"),    disabled=True, width="large"),
                "sequence_hash":   None,  # hidden
                "total_sequences": st.column_config.NumberColumn(T("timeline_col_total"),  disabled=True),
                "first_seen":      st.column_config.TextColumn(T("timeline_col_first"),    disabled=True),
                "last_seen":       st.column_config.TextColumn(T("timeline_col_last"),     disabled=True),
                "months_active":   st.column_config.NumberColumn(T("timeline_col_months"), disabled=True),
            }
            # First and last month of each row are locked (always selected, not editable)
            # We handle this by setting anchor months as disabled checkboxes
            for mc in _month_cols:
                _col_config[mc] = st.column_config.CheckboxColumn(
                    mc,
                    help=T("timeline_month_col_help", month=mc),
                    default=False,
                )

            _display_matrix = _matrix_df.drop(columns=["sequence_hash"])

            # Sparse matrix: clusters that don't span a given month get NaN.
            # CheckboxColumn requires bool — coerce NaN → False.
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
            _dl1, _dl2 = st.columns(2)
            with _dl1:
                st.download_button(
                    label=T("timeline_download_matrix_csv"),
                    data=edited.to_csv(index=False).encode("utf-8"),
                    file_name=f"timeline_matrix_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 — Impact Preview & Export
# ─────────────────────────────────────────────────────────────────────────────
with st.expander(f"🔬 {T('timeline_preview_header')}", expanded=False):

    if "sequence" not in _display_df.columns:
        st.warning(T("timeline_no_sequence_for_extraction"))
    elif "_tl_matrix_df" not in st.session_state:
        st.info(T("timeline_configure_matrix_first"))
    else:
        if st.button(T("timeline_generate_preview_btn"), type="secondary", key="tl_preview_btn"):

            matrix_df  = st.session_state["_tl_matrix_df"]
            edited_mat = st.session_state.get("_tl_edited_matrix", pd.DataFrame())
            month_cols = st.session_state.get("_tl_month_cols", [])

            # Determine representative selection function
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
                            target_period = pd.Period(mc, freq="M")
                            month_seqs = cluster_seqs[
                                pd.to_datetime(cluster_seqs["collection_date"], errors="coerce")
                                .dt.to_period("M") == target_period
                            ]
                            if not month_seqs.empty:
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
                        file_name=f"timeline_curated_{datetime.now().strftime('%Y%m%d_%H%M')}.fasta",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True,
                        help=T("download_tooltip_fasta"),
                    )

                with ex2:
                    # Metadata CSV
                    meta_cols = [c for c in result_df.columns if c != "sequence"]
                    st.download_button(
                        label=T("download_csv_label"),
                        data=result_df[meta_cols].to_csv(index=False).encode("utf-8"),
                        file_name=f"timeline_metadata_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help=T("download_tooltip_csv"),
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
                        file_name=f"timeline_methodology_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json",
                        use_container_width=True,
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

    # ── Chart colour scheme ────────────────────────────────────────────────
    st.markdown("**Chart Colour**")
    _sb_scheme_opts = list(_TIMELINE_PALETTES.keys())
    st.selectbox(
        "Chart Colour",
        options=_sb_scheme_opts,
        index=_sb_scheme_opts.index(_tl_scheme_name) if _tl_scheme_name in _sb_scheme_opts else 0,
        key="timeline_chart_scheme",
        label_visibility="collapsed",
        help="Applies to the cluster bar, sunburst and epidemic curve.",
    )
    # Live colour swatch
    _sb_accent = _TIMELINE_PALETTES.get(
        st.session_state.get("timeline_chart_scheme", "🔵 Ocean Blue"),
        _TIMELINE_PALETTES["🔵 Ocean Blue"],
    )["accent"]
    st.markdown(
        f"<div style='height:7px;border-radius:3px;margin-top:4px;"
        f"background:linear-gradient(90deg,{_sb_accent}55,{_sb_accent})'></div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Inter-page navigation
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
_tl_n1, _tl_n2 = st.columns(2)
try:
    _tl_n1.page_link("pages/03_🔬_Sequence_Refinery.py",
                     label="← 🔬 Sequence Refinery",
                     use_container_width=True)
    _tl_n2.page_link("pages/05_📊_Analytics.py",
                     label="📊 Analytics →",
                     use_container_width=True)
except AttributeError:
    _tl_n1.markdown("[← 🔬 Sequence Refinery](pages/03_🔬_Sequence_Refinery.py)")
    _tl_n2.markdown("[📊 Analytics →](pages/05_📊_Analytics.py)")
