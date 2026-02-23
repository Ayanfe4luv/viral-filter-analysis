# -*- coding: utf-8 -*-
"""
pages/04_📊_Analytics.py — Vectorized Visualizations

All charts:
  - Use vectorized df.groupby().size() — no iterrows
  - Render only on Generate button click (lazy load)
  - Labels and titles via T() — Cyrillic renders correctly
  - Color palettes adapted from original fasta_analysis_app_final.py
"""

import colorsys
import json
import random

import pandas as pd
import streamlit as st

from utils.minimal_i18n import T
from utils.peak_detector import EpiWaveDetector

try:
    import plotly.express as px
    import plotly.graph_objects as go
    _PLOTLY = True
except ImportError:
    _PLOTLY = False

st.title(f"\U0001f4ca {T('analytics_header')}")

if not _PLOTLY:
    st.error("plotly is required for Analytics. Run: `pip install plotly`")
    st.stop()

_active_df: pd.DataFrame = st.session_state.get("active_df", pd.DataFrame())
_filtered_df: pd.DataFrame = st.session_state.get("filtered_df", pd.DataFrame())
_df = _filtered_df if not _filtered_df.empty else _active_df
_src = T("analytics_filtered_badge") if not _filtered_df.empty else T("analytics_active_badge")

if _df.empty:
    st.warning(T("error_no_active_df"))
    st.stop()

st.caption(T("analytics_dataset_label", n=f"{len(_df):,}", src=_src))

# ---------------------------------------------------------------------------
# Pre-built color palettes (adapted from fasta_analysis_app_final.py)
# ---------------------------------------------------------------------------

_SCHEMES = {
    "bar": {
        "Nature Journal":  ["#E64B35","#4DBBD5","#00A087","#3C5488","#F39B7F","#8491B4","#91D1C2","#B09C85"],
        "Spike Surge":     ["#8dd3c7","#ffffb3","#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5"],
        "Epi Alert":       px.colors.sequential.Reds,
        "Genomic Helix":   px.colors.sequential.Viridis_r,
    },
    "pie": {
        "Viral Mosaic":    px.colors.qualitative.Set1,
        "Journal Crisp":   ["#00A087","#3C5488","#F39B7F","#8491B4","#D55E00","#CC79A7","#0072B2","#009E73"],
        "Nebula Burst":    px.colors.qualitative.Set2,
        "Outbreak Slices": ["#7fcdbb","#2c7fb8","#41b6c4","#a63603","#f03b20","#fee0d2","#fcbba1","#fc9272"],
    },
    "line": {
        "Journal Timeline":["#E31A1C","#1F78B4","#33A02C","#FF7F00","#6A3A4C"],
        "Pandemic Wave":   px.colors.diverging.Spectral,
        "Bio Rhythm":      px.colors.sequential.Oranges,
        "Evo Path":        px.colors.sequential.Greens,
    },
    "heatmap": {
        "Global Outbreak": px.colors.sequential.Reds,
        "Eco Layers":      px.colors.sequential.YlGnBu,
        "Helix Intensity": px.colors.sequential.Inferno,
        "Genomic Density": px.colors.diverging.RdBu_r,
    },
    "stacked": {
        "Host Stacks":     ["#8c510a","#d8b365","#f6e8c3","#c7eae5","#5ab4ac","#01665e","#f03b20","#fee0d2"],
        "Pub Stack":       ["#D55E00","#0072B2","#009E73","#CC79A7","#E69F00","#F0E442","#56B4E9","#00A087"],
        "Layered Genomes": px.colors.qualitative.Set2,
        "Outbreak Build":  px.colors.sequential.OrRd,
    },
}

_FIELD_MAP = {
    T("analytics_field_subtype"):  "subtype_clean",
    T("analytics_field_host"):     "host",
    T("analytics_field_segment"):  "segment",
    T("analytics_field_location"): "location",
    T("analytics_field_clade"):    "clade_l1",
    T("analytics_field_year"):     "_year",
}

_CHART_TYPES = {
    T("analytics_chart_type_dist"):    "dist",
    T("analytics_chart_type_temporal"): "temporal",
    T("analytics_chart_type_stacked"): "stacked",
    T("analytics_chart_type_epi"):     "epi",
}

_INTERVALS = {
    T("analytics_interval_month"):   "M",
    T("analytics_interval_quarter"): "Q",
    T("analytics_interval_year"):    "Y",
}

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=55, b=30, l=25, r=25),
    title_font_size=18,
    font=dict(family="Inter, Arial, sans-serif"),
)


# ---------------------------------------------------------------------------
# Helper: build a field-enriched copy of df
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _enrich(df_hash: str, df: pd.DataFrame) -> pd.DataFrame:  # noqa: ARG001
    out = df.copy()
    if "collection_date" in out.columns:
        dates = pd.to_datetime(out["collection_date"], errors="coerce")
        out["_year"] = dates.dt.year.astype("Int64").astype(str).where(dates.notna(), other=None)
    return out


_df_enriched = _enrich(str(len(_df)) + str(_df.columns.tolist()), _df)


# ---------------------------------------------------------------------------
# Chart generation functions (all vectorized)
# ---------------------------------------------------------------------------

def _make_distribution(df: pd.DataFrame, field: str, chart_sub: str,
                        top_n: int, scheme) -> go.Figure:
    col = df[field].dropna().replace("", pd.NA).dropna()
    counts = col.value_counts().nlargest(top_n)
    if counts.empty:
        return _empty_fig(T("analytics_no_data"))

    labels = counts.index.tolist()
    values = counts.values.tolist()

    if chart_sub == "pie":
        colors = scheme if isinstance(scheme, list) else None
        fig = px.pie(
            names=labels, values=values,
            color_discrete_sequence=colors,
            hole=0.35,
        )
        fig.update_traces(
            textposition="inside", textinfo="percent+label",
            pull=[0.04] * len(labels),
        )
    else:  # bar (horizontal)
        data_df = pd.DataFrame({"Category": labels, "Count": values})
        if isinstance(scheme, list):
            fig = px.bar(
                data_df.sort_values("Count"),
                y="Category", x="Count",
                orientation="h", text_auto=True,
                color="Category", color_discrete_sequence=scheme,
            )
            fig.update_layout(showlegend=False)
        else:
            fig = px.bar(
                data_df.sort_values("Count"),
                y="Category", x="Count",
                orientation="h", text_auto=True,
                color="Count", color_continuous_scale=scheme,
            )
            fig.update_layout(coloraxis_showscale=False)
        fig.update_yaxes(categoryorder="total ascending", title=None)
        fig.update_xaxes(title=T("obs_col_count"))

    fig.update_layout(**_LAYOUT)
    return fig


def _make_temporal(df: pd.DataFrame, interval_code: str, scheme) -> go.Figure:
    if "collection_date" not in df.columns:
        return _empty_fig(T("analytics_no_data"))

    dates = pd.to_datetime(df["collection_date"], errors="coerce").dropna()
    if dates.empty:
        return _empty_fig(T("analytics_no_data"))

    freq_map = {"M": "%Y-%m", "Q": None, "Y": "%Y"}

    if interval_code == "Q":
        periods = dates.dt.to_period("Q").astype(str)
    else:
        periods = dates.dt.strftime(freq_map[interval_code])

    counts = periods.value_counts().sort_index()
    data_df = pd.DataFrame({"Period": counts.index, "Count": counts.values})

    line_color = scheme[0] if isinstance(scheme, list) and scheme else "#3b82f6"

    fig = px.line(
        data_df, x="Period", y="Count",
        markers=True, text="Count",
    )
    fig.update_traces(
        line=dict(color=line_color, width=2.5),
        marker=dict(size=7, color=line_color),
        textposition="top center",
    )
    fig.update_xaxes(title=T("analytics_period_label"), tickangle=45)
    fig.update_yaxes(title=T("obs_col_count"))
    fig.update_layout(**_LAYOUT)
    return fig


def _make_stacked(df: pd.DataFrame, cat1_field: str, cat2_field: str,
                  top_n: int, scheme) -> go.Figure:
    if cat1_field not in df.columns or cat2_field not in df.columns:
        return _empty_fig(T("analytics_no_data"))

    sub = df[[cat1_field, cat2_field]].dropna()
    if sub.empty:
        return _empty_fig(T("analytics_no_data"))

    top_cats = sub[cat1_field].value_counts().nlargest(top_n).index
    sub = sub[sub[cat1_field].isin(top_cats)]

    pivot = sub.groupby([cat1_field, cat2_field]).size().reset_index(name="Count")
    colors = scheme if isinstance(scheme, list) else None

    fig = px.bar(
        pivot, x=cat1_field, y="Count", color=cat2_field,
        barmode="stack", text_auto=".2s",
        color_discrete_sequence=colors,
        category_orders={cat1_field: top_cats.tolist()},
    )
    fig.update_traces(textfont_size=10, textangle=0,
                      textposition="inside", cliponaxis=False)
    fig.update_xaxes(tickangle=40, title=None)
    fig.update_yaxes(title=T("obs_col_count"))
    fig.update_layout(**_LAYOUT, legend_title=cat2_field)
    return fig


def _make_epi_curve(df: pd.DataFrame, sensitivity: float, scheme) -> go.Figure:
    detector = EpiWaveDetector()
    ts = detector._build_weekly_counts(df)
    if ts.empty:
        return _empty_fig(T("analytics_no_data"))

    bar_color = (scheme[0] if isinstance(scheme, list) and scheme
                 else ("steelblue" if not isinstance(scheme, list) else "steelblue"))

    fig = go.Figure()

    # Epidemic bars (aggregated counts — never raw dots)
    fig.add_trace(go.Bar(
        x=ts.index.tolist(),
        y=ts.values.tolist(),
        marker_color=bar_color,
        name=T("analytics_epi_curve"),
        opacity=0.85,
    ))

    # Peak annotations
    waves = detector.detect_epi_waves(df, sensitivity=sensitivity)
    if waves["peaks"]:
        px_list, py_list = zip(*waves["peaks"])
        fig.add_trace(go.Scatter(
            x=list(px_list), y=list(py_list),
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=14, color="#E64B35",
                        line=dict(width=1.5, color="white")),
            text=[f"▲{c}" for c in py_list],
            textposition="top center",
            textfont=dict(size=10, color="#E64B35"),
            name=T("analytics_wave_peaks"),
        ))

    if waves["troughs"]:
        tx_list, ty_list = zip(*waves["troughs"])
        fig.add_trace(go.Scatter(
            x=list(tx_list), y=list(ty_list),
            mode="markers",
            marker=dict(symbol="triangle-down", size=10, color="#4DBBD5",
                        line=dict(width=1.5, color="white")),
            name=T("analytics_wave_troughs"),
        ))

    fig.update_xaxes(title=T("obs_epi_x"), tickangle=45)
    fig.update_yaxes(title=T("obs_epi_y"))
    n_waves = waves["wave_count"]
    fig.update_layout(
        **_LAYOUT,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=[dict(
            text=T("analytics_wave_count", n=n_waves),
            xref="paper", yref="paper", x=0.01, y=0.97,
            showarrow=False, font=dict(size=12, color="#888"),
        )],
    )
    return fig


def _empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        **_LAYOUT,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        annotations=[dict(
            text=msg, xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#888"),
        )],
    )
    return fig


# ---------------------------------------------------------------------------
# UI — Chart controls
# ---------------------------------------------------------------------------

ctrl_col, palette_col = st.columns([3, 2])

with ctrl_col:
    chart_type_label = st.radio(
        T("analytics_chart_type_label"),
        options=list(_CHART_TYPES.keys()),
        horizontal=True,
        key="an_chart_type",
    )
    chart_type = _CHART_TYPES[chart_type_label]

    if chart_type == "dist":
        c1, c2, c3 = st.columns([2, 1, 1])
        field_label = c1.selectbox(
            T("analytics_field"),
            options=[k for k, v in _FIELD_MAP.items() if v in _df_enriched.columns],
            key="an_field",
        )
        chart_sub = c2.radio(
            T("analytics_dist_mode"),
            options=["bar", "pie"],
            horizontal=True,
            key="an_dist_mode",
        )
        top_n = c3.number_input(T("analytics_top_n"), min_value=3, max_value=50,
                                 value=10, step=1, key="an_top_n")

    elif chart_type == "temporal":
        interval_label = st.selectbox(
            T("analytics_interval"),
            options=list(_INTERVALS.keys()),
            key="an_interval",
        )

    elif chart_type == "stacked":
        ca, cb, cc = st.columns([2, 2, 1])
        available = [k for k, v in _FIELD_MAP.items() if v in _df_enriched.columns]
        cat1_label = ca.selectbox(T("analytics_cat1"), options=available, key="an_cat1",
                                   index=0)
        cat2_label = cb.selectbox(T("analytics_cat2"), options=available, key="an_cat2",
                                   index=min(1, len(available)-1))
        top_n_s = cc.number_input(T("analytics_top_n"), min_value=3, max_value=30,
                                    value=10, step=1, key="an_top_n_s")
        if cat1_label == cat2_label:
            st.warning(T("analytics_same_category_warning"))

    elif chart_type == "epi":
        sensitivity = st.slider(
            T("analytics_sensitivity"),
            min_value=0.1, max_value=1.0, value=0.5, step=0.05,
            key="an_sensitivity",
        )

    # Color scheme for current chart type
    scheme_key_map = {"dist": chart_sub if chart_type == "dist" else "bar",
                      "temporal": "line", "stacked": "stacked", "epi": "bar"}
    _skey = scheme_key_map.get(chart_type, "bar")
    _skey = chart_sub if chart_type == "dist" else _skey

    palette_names = list(_SCHEMES.get(_skey, _SCHEMES["bar"]).keys())
    scheme_name = st.selectbox(
        T("analytics_color_scheme"),
        options=palette_names,
        key=f"an_scheme_{_skey}",
    )
    active_scheme = (
        st.session_state.get("custom_palette") or
        _SCHEMES.get(_skey, _SCHEMES["bar"])[scheme_name]
    )

    if st.session_state.get("custom_palette"):
        st.caption(f"🎨 {T('analytics_using_custom_palette')}")


with palette_col:
    with st.expander(f"\U0001f3a8 {T('analytics_palette_studio')}", expanded=False):
        num_colors = st.slider(T("analytics_num_colors"), 3, 12, 8,
                               key="an_num_colors")

        _defaults = ["#FF6B6B","#4ECDC4","#45B7D1","#96CEB4",
                     "#FFEAA7","#DDA0DD","#F39B7F","#8491B4",
                     "#91D1C2","#B09C85","#E64B35","#4DBBD5"]

        custom_colors = []
        cols_per_row = 4
        for row_i in range((num_colors + cols_per_row - 1) // cols_per_row):
            cols = st.columns(cols_per_row)
            for col_i in range(cols_per_row):
                ci = row_i * cols_per_row + col_i
                if ci < num_colors:
                    with cols[col_i]:
                        c = st.color_picker(
                            f"C{ci+1}",
                            value=_defaults[ci % len(_defaults)],
                            key=f"an_cp_{ci}",
                        )
                        custom_colors.append(c)

        st.markdown("---")
        qa1, qa2, qa3 = st.columns(3)

        with qa1:
            if st.button(T("analytics_apply_palette"), use_container_width=True,
                         key="an_apply_pal"):
                st.session_state["custom_palette"] = custom_colors
                st.success(T("analytics_palette_applied"))
                st.rerun()

        with qa2:
            if st.button(T("analytics_dna_colors"), use_container_width=True,
                         key="an_dna_pal"):
                # Build palette from A/T/G/C nucleotide proportions
                if "sequence" in _df.columns and len(_df) > 0:
                    sample_seq = str(_df["sequence"].iloc[0])[:200]
                    total = max(len(sample_seq), 1)
                    props = {
                        "A": sample_seq.count("A") / total,
                        "T": sample_seq.count("T") / total,
                        "G": sample_seq.count("G") / total,
                        "C": sample_seq.count("C") / total,
                    }
                    base_hues = {"A": 120, "T": 240, "G": 30, "C": 0}
                    dna_colors = []
                    for _ in range(num_colors):
                        base = random.choices(
                            list(base_hues.keys()),
                            weights=list(props.values()),
                        )[0]
                        hue = (base_hues[base] + random.randint(-20, 20)) % 360
                        s = random.uniform(0.6, 0.9)
                        l = random.uniform(0.45, 0.65)
                        r, g, b = colorsys.hls_to_rgb(hue/360, l, s)
                        dna_colors.append(
                            f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                        )
                    st.session_state["custom_palette"] = dna_colors
                    st.success(T("analytics_dna_applied"))
                    st.rerun()
                else:
                    st.warning(T("analytics_no_seq_for_dna"))

        with qa3:
            if st.button(T("analytics_randomize"), use_container_width=True,
                         key="an_rand_pal"):
                rand_colors = []
                for _ in range(num_colors):
                    h = random.randint(0, 360)
                    s = random.uniform(0.65, 0.95)
                    l = random.uniform(0.50, 0.70)
                    r, g, b = colorsys.hls_to_rgb(h/360, l, s)
                    rand_colors.append(
                        f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                    )
                st.session_state["custom_palette"] = rand_colors
                st.success(T("analytics_randomized"))
                st.rerun()

        # Palette preview swatches
        cur_pal = st.session_state.get("custom_palette")
        if cur_pal:
            st.markdown("---")
            st.markdown(f"**{T('analytics_current_palette')}**")
            swatch_cols = st.columns(min(8, len(cur_pal)))
            for si, sc in enumerate(cur_pal[:8]):
                with swatch_cols[si]:
                    st.markdown(
                        f"<div style='"
                        f"background:{sc};width:100%;height:60px;"
                        f"border-radius:8px;border:1px solid rgba(0,0,0,.15);"
                        f"box-shadow:0 2px 4px rgba(0,0,0,.1);"
                        f"display:flex;align-items:flex-end;"
                        f"justify-content:center;padding:4px'>"
                        f"<span style='background:rgba(255,255,255,.9);color:#333;"
                        f"padding:2px 4px;border-radius:4px;"
                        f"font-size:9px;font-family:monospace'>"
                        f"{sc.upper()}</span></div>",
                        unsafe_allow_html=True,
                    )
            if len(cur_pal) > 8:
                st.caption(f"+{len(cur_pal)-8} {T('analytics_more_colors')}")
            st.markdown("<br>", unsafe_allow_html=True)

            palette_json = json.dumps({
                "colors": cur_pal,
                "name": "VirSift Custom Palette",
                "count": len(cur_pal),
                "created": pd.Timestamp.now().isoformat(),
            }, indent=2)
            st.download_button(
                label=T("analytics_export_palette"),
                data=palette_json.encode("utf-8"),
                file_name="virsift_palette.json",
                mime="application/json",
                use_container_width=True,
                key="an_dl_palette",
            )

        if cur_pal:
            if st.button(T("analytics_clear_palette"), use_container_width=True,
                         key="an_clear_pal"):
                st.session_state.pop("custom_palette", None)
                st.rerun()

# ---------------------------------------------------------------------------
# Generate chart
# ---------------------------------------------------------------------------

st.divider()
gc1, gc2 = st.columns([3, 1])
with gc1:
    gen_btn = st.button(
        T("analytics_generate"),
        type="primary",
        use_container_width=True,
        key="an_generate",
    )
with gc2:
    if st.button(T("analytics_clear_chart"), use_container_width=True, key="an_clear"):
        st.session_state.pop("an_fig", None)
        st.session_state.pop("an_fig_title", None)
        st.rerun()

if gen_btn:
    with st.spinner(T("analytics_generating")):
        try:
            if chart_type == "dist":
                resolved_field = _FIELD_MAP.get(field_label, "")
                if resolved_field not in _df_enriched.columns:
                    st.error(T("analytics_no_data"))
                else:
                    fig = _make_distribution(
                        _df_enriched, resolved_field, chart_sub, int(top_n), active_scheme
                    )
                    title = f"{field_label} {T('analytics_dist_title')}"
                    fig.update_layout(title=title)
                    st.session_state["an_fig"] = fig
                    st.session_state["an_fig_title"] = title

            elif chart_type == "temporal":
                interval_code = _INTERVALS[interval_label]
                fig = _make_temporal(_df, interval_code, active_scheme)
                title = f"{T('analytics_temporal')} — {interval_label}"
                fig.update_layout(title=title)
                st.session_state["an_fig"] = fig
                st.session_state["an_fig_title"] = title

            elif chart_type == "stacked":
                if cat1_label == cat2_label:
                    st.error(T("analytics_same_category_warning"))
                else:
                    f1 = _FIELD_MAP.get(cat1_label, "")
                    f2 = _FIELD_MAP.get(cat2_label, "")
                    fig = _make_stacked(_df_enriched, f1, f2, int(top_n_s), active_scheme)
                    title = f"{cat2_label} \u00d7 {cat1_label}"
                    fig.update_layout(title=title)
                    st.session_state["an_fig"] = fig
                    st.session_state["an_fig_title"] = title

            elif chart_type == "epi":
                fig = _make_epi_curve(_df, sensitivity, active_scheme)
                title = T("analytics_epi_curve")
                fig.update_layout(title=title)
                st.session_state["an_fig"] = fig
                st.session_state["an_fig_title"] = title

        except Exception as e:
            st.error(f"{T('analytics_chart_error')}: {e}")

# ---------------------------------------------------------------------------
# Display chart + download
# ---------------------------------------------------------------------------

if "an_fig" in st.session_state:
    st.plotly_chart(st.session_state["an_fig"], use_container_width=True)
    title_slug = (st.session_state.get("an_fig_title", "chart")
                  .lower().replace(" ", "_")[:40])
    html_bytes = st.session_state["an_fig"].to_html(include_plotlyjs="cdn").encode("utf-8")
    st.download_button(
        label=T("analytics_download_html"),
        data=html_bytes,
        file_name=f"virsift_{title_slug}.html",
        mime="text/html",
        help=T("analytics_download_html_help"),
        key="an_dl_html",
    )
