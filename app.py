# -*- coding: utf-8 -*-
"""
app.py — Vir-Seq-Sift International v2.1
Multilingual entry point + minimal sidebar + st.navigation() wiring.

This file is the ONLY place that:
  - Calls init_translations() (once per session)
  - Initializes the full session_state schema
  - Renders the persistent sidebar
  - Wires st.navigation()

No business logic lives here. All analysis logic is in utils/.
All page content is in pages/.
"""

import pandas as pd
import streamlit as st

from utils.minimal_i18n import T, init_translations

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call in the script
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Vir-Seq-Sift International",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Vir-Seq-Sift International v2.1 — Zero-Lag Epidemiological Surveillance",
    },
)

# ---------------------------------------------------------------------------
# Step 1: Initialize translations (must precede all T() calls)
# ---------------------------------------------------------------------------
init_translations()


# ---------------------------------------------------------------------------
# Step 2: Initialize session state schema (idempotent — safe on every rerun)
# ---------------------------------------------------------------------------
def _init_session_state() -> None:
    """Initialize all session state keys to their defaults.

    Keys are only set if not already present, preserving state across reruns.
    Schema defined in roadmap Section 3.
    """
    defaults: dict = {
        # --- I18N & Regional ---
        "language": "en",
        "region": "RU",
        "translation_cache": {},
        "user_terminology": {},     # Custom Rospotrebnadzor / institutional overrides

        # --- Data Pipeline ---
        "raw_files": [],            # Unicode-safe uploaded file objects
        "active_df": pd.DataFrame(),    # Written ONCE on Activate — never mutated after
        "filtered_df": pd.DataFrame(),  # All filtering writes here only

        # --- Filter State ---
        "global_filters": [],       # List of filter rule dicts (sidebar badge count)
        "selected_peaks": [],       # HITL: Peak Checklist selections
        "lasso_zones": [],          # HITL: Visual Lasso selected ranges
        "checkpoint_targets": [],   # HITL: Custom Time Checkpoint month strings

        # --- Investigation Context ---
        "investigation_mode": "surveillance",  # 'surveillance' | 'research'
        "temporal_baseline": "epi_season",     # Calendar mode for temporal grouping
        "strain_hashes": {},                   # Identity tracking across sessions

        # --- Logging ---
        "action_logs": [],          # Filter operation records for export

        # --- Theme ---
        "theme": "light",           # 'light' | 'dark'
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


_init_session_state()


# ---------------------------------------------------------------------------
# Step 3: Wire navigation pages
# ---------------------------------------------------------------------------
_PAGES = [
    st.Page("pages/01_🌍_Observatory.py",  title=T("nav_observatory"), icon="🌍"),
    st.Page("pages/02_📁_Workspace.py",    title=T("nav_workspace"),   icon="📁"),
    st.Page("pages/03_🧬_Filter_Lab.py",   title=T("nav_filter_lab"),  icon="🧬"),
    st.Page("pages/04_📊_Analytics.py",    title=T("nav_analytics"),   icon="📊"),
    st.Page("pages/05_📋_Export.py",       title=T("nav_export"),      icon="📋"),
]

pg = st.navigation(_PAGES)


# ---------------------------------------------------------------------------
# CSS Theme constants (adapted from fasta_analysis_app_final.py)
# ---------------------------------------------------------------------------
_LIGHT_CSS = """
<style>
/* ── Typography: only html/body — never override Streamlit icon spans ── */
html, body {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}
p, label, .stMarkdown, .stCaption, .stText,
[data-testid="stMarkdownContainer"] {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}

/* ── Sidebar background ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0c4a6e 100%) !important;
    padding: 1rem;
}

/* ── Sidebar text — targeted, never wildcard * ── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stText"],
[data-testid="stSidebar"] [data-testid="stCaption"] {
    color: #cbd5e1 !important;
    font-size: 0.88rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 { color: #bae6fd !important; }
[data-testid="stSidebar"] hr { border-color: #1e40af !important; }

/* ── Sidebar selectbox / radio labels ── */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stCheckbox label {
    color: #e0f2fe !important;
    font-weight: 600;
}

/* ── Sidebar selectbox dropdown text ── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] div {
    color: #0c4a6e !important;
}

/* ── Sidebar buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255, 255, 255, 0.15) !important;
    color: #e0f2fe !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.28) !important;
    border-color: rgba(255, 255, 255, 0.60) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:focus {
    background-color: rgba(255, 255, 255, 0.38) !important;
    box-shadow: 0 0 0 2px #7dd3fc !important;
    color: #ffffff !important;
}
/* Primary buttons inside sidebar */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #0369a1 0%, #0891b2 100%) !important;
    color: #ffffff !important;
    border: none !important;
}

/* ── Sidebar download button ── */
[data-testid="stSidebar"] .stDownloadButton > button {
    background-color: rgba(255, 255, 255, 0.10) !important;
    color: #7dd3fc !important;
    border: 1.5px solid #38bdf8 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background-color: rgba(56, 189, 248, 0.20) !important;
    color: #ffffff !important;
}

/* ── Sidebar metrics ── */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 10px !important;
    padding: 0.6rem 0.8rem !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: #e0f2fe !important; font-size: 0.85rem !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #ffffff !important; }

/* ── Main content metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    padding: 0.9rem 1.1rem;
    border-radius: 12px;
    border-left: 4px solid #0ea5e9;
    box-shadow: 0 2px 10px rgba(3,105,161,0.10);
}
[data-testid="metric-container"] > div:first-child { color: #64748b !important; font-size: 0.82rem; }
[data-testid="metric-container"] > div:last-child  { color: #0c4a6e !important; font-weight: 700; }

/* ── Primary buttons (main area) ── */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #0369a1 0%, #0891b2 100%) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(3,105,161,0.30) !important;
    transition: all 0.18s ease !important;
}
[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(3,105,161,0.45) !important;
}

/* ── Download buttons (main area) ── */
.stDownloadButton > button {
    border-radius: 8px !important;
    border: 1.5px solid #0ea5e9 !important;
    color: #0369a1 !important; font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
.stDownloadButton > button:hover { background: #e0f2fe !important; border-color: #0369a1 !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}

hr { border-color: #e2e8f0 !important; }
[data-testid="stDataFrame"] thead th {
    background: #f1f5f9 !important; color: #1e3a8a !important; font-weight: 600 !important;
}
</style>
"""

_DARK_CSS = """
<style>
/* ── Typography: only html/body — never override Streamlit icon spans ── */
html, body {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}
p, label, .stMarkdown, .stCaption, .stText,
[data-testid="stMarkdownContainer"] {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}

.stApp { background: #0f172a !important; color: #e2e8f0 !important; }

/* ── Sidebar background ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%) !important;
    padding: 1rem;
}

/* ── Sidebar text — targeted, never wildcard * ── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stText"],
[data-testid="stSidebar"] [data-testid="stCaption"] {
    color: #94a3b8 !important;
    font-size: 0.88rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 { color: #93c5fd !important; }
[data-testid="stSidebar"] hr { border-color: #1e293b !important; }

/* ── Sidebar selectbox / radio / checkbox labels ── */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stCheckbox label {
    color: #e0f2fe !important;
    font-weight: 600;
}

/* ── Sidebar buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255, 255, 255, 0.12) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.50) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:focus {
    background-color: rgba(255, 255, 255, 0.30) !important;
    box-shadow: 0 0 0 2px #60a5fa !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #1d4ed8 0%, #0891b2 100%) !important;
    color: #ffffff !important;
    border: none !important;
}

/* ── Sidebar download button ── */
[data-testid="stSidebar"] .stDownloadButton > button {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #7dd3fc !important;
    border: 1.5px solid #38bdf8 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background-color: rgba(56, 189, 248, 0.18) !important;
    color: #ffffff !important;
}

/* ── Sidebar metrics ── */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    padding: 0.6rem 0.8rem !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.85rem !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #7dd3fc !important; }

/* ── Main content metrics ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    border-left: 4px solid #38bdf8 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.40) !important;
}
[data-testid="metric-container"] > div:first-child { color: #94a3b8 !important; }
[data-testid="metric-container"] > div:last-child  { color: #7dd3fc !important; }

/* ── Primary buttons (main area) ── */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #1d4ed8 0%, #0891b2 100%) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(29,78,216,0.40) !important;
}

/* ── Download buttons (main area) ── */
.stDownloadButton > button {
    border-radius: 8px !important;
    border: 1.5px solid #38bdf8 !important;
    color: #7dd3fc !important; font-weight: 500 !important;
}
.stDownloadButton > button:hover { background: #1e293b !important; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    border-radius: 10px !important;
    border: 1px solid #1e293b !important;
    background: #1e293b !important;
}

hr { border-color: #1e293b !important; }
[data-testid="stDataFrame"] thead th {
    background: #1e293b !important; color: #93c5fd !important; font-weight: 600 !important;
}
</style>
"""


# ---------------------------------------------------------------------------
# Step 4: Render persistent sidebar
# ---------------------------------------------------------------------------
def _render_sidebar() -> None:
    """Minimal sidebar — language toggle (top), filter badge, dataset status, quick actions."""
    with st.sidebar:
        # ── Language & Theme — TOP of sidebar, always visible ──────────────
        _lang_map = {"🇬🇧 English": "en", "🇷🇺 Русский": "ru"}
        _current = st.session_state.get("language", "en")
        _selected = st.selectbox(
            T("sidebar_language"),
            options=list(_lang_map.keys()),
            index=0 if _current == "en" else 1,
            key="language_selector",
            label_visibility="visible",
        )
        if _lang_map[_selected] != _current:
            st.session_state["language"] = _lang_map[_selected]
            st.rerun()

        _current_theme = st.session_state.get("theme", "light")
        _theme_selected = st.radio(
            T("sidebar_theme"),
            options=[T("theme_light"), T("theme_dark")],
            index=0 if _current_theme == "light" else 1,
            horizontal=True,
            key="theme_selector",
        )
        _new_theme = "light" if _theme_selected == T("theme_light") else "dark"
        if _new_theme != _current_theme:
            st.session_state["theme"] = _new_theme
            st.rerun()

        st.divider()

        # ── App branding ─────────────────────────────────────────────────────
        st.markdown(f"### 🧬 {T('app_title')}")
        st.markdown(f"*{T('app_subtitle')}*")
        st.divider()

        # --- Global Filter Badge ---
        _active_filters = st.session_state.get("global_filters", [])
        _filter_count = len(_active_filters)
        with st.expander(T("sidebar_global_filters", count=_filter_count), expanded=False):
            if _active_filters:
                for _f in _active_filters:
                    st.write(f"• {_f.get('field', '')} {_f.get('operator', '')} {_f.get('value', '')}")
                if st.button(T("sidebar_clear_filters"), use_container_width=True):
                    st.session_state["global_filters"] = []
                    st.rerun()
            else:
                st.caption(T("sidebar_no_filters"))

        st.divider()

        # --- Dataset Status ---
        st.markdown(f"**{T('sidebar_dataset_status')}**")
        _active_df = st.session_state.get("active_df", pd.DataFrame())
        _filtered_df = st.session_state.get("filtered_df", pd.DataFrame())

        if not _active_df.empty:
            st.metric(T("sidebar_active_seqs"), f"{len(_active_df):,}")
            if not _filtered_df.empty:
                st.metric(T("sidebar_filtered_seqs"), f"{len(_filtered_df):,}")
            if "sequence_length" in _active_df.columns:
                st.metric(
                    T("sidebar_avg_length"),
                    f"{_active_df['sequence_length'].mean():.0f} bp",
                )
            if len(_active_df) > 10_000:
                st.warning(T("sidebar_large_dataset_warning"))
        else:
            st.info(T("sidebar_no_dataset"))

        st.divider()

        # --- Quick Actions ---
        st.markdown(f"**{T('sidebar_quick_actions')}**")

        # Quick FASTA export (only when filtered data is available)
        if not _filtered_df.empty:
            try:
                from utils.gisaid_parser import convert_df_to_fasta
                _fasta_out = convert_df_to_fasta(_filtered_df)
                st.download_button(
                    label=T("download_fasta_label", count=len(_filtered_df)),
                    data=_fasta_out,
                    file_name=f"vss_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.fasta",
                    mime="text/plain",
                    use_container_width=True,
                    type="primary",
                    help=T("download_tooltip_fasta"),
                )
            except Exception:
                pass  # Parser not yet implemented — silently skip

        if st.button(T("sidebar_reset_session"), use_container_width=True):
            for _key in list(st.session_state.keys()):
                del st.session_state[_key]
            st.rerun()

        st.divider()
        st.caption(f"{T('app_title')} {T('app_version')}")
        st.caption("Zero-Lag Architecture")


# ---------------------------------------------------------------------------
# Step 4b: Inject CSS theme
# ---------------------------------------------------------------------------
_active_theme = st.session_state.get("theme", "light")
st.markdown(_DARK_CSS if _active_theme == "dark" else _LIGHT_CSS, unsafe_allow_html=True)

_render_sidebar()

# ---------------------------------------------------------------------------
# Step 5: Run the current page
# ---------------------------------------------------------------------------
pg.run()
