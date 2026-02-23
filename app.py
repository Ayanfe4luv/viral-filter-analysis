import streamlit as st
from utils.minimal_i18n import init_translations, T

# App initialization
st.set_page_config(
    page_title="Vir-Seq-Sift International", 
    page_icon="🦠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Startup Translations
init_translations()

# Set up page routing using the new st.navigation
observatory = st.Page("pages/01_observatory.py", title=T("observatory"), icon="🌍", default=True)
workspace = st.Page("pages/02_workspace.py", title=T("workspace"), icon="📁")
filter_lab = st.Page("pages/03_filter_lab.py", title=T("filter_lab"), icon="🧬")
analytics = st.Page("pages/04_analytics.py", title=T("analytics"), icon="📊")
export = st.Page("pages/05_export.py", title=T("export"), icon="📋")

pg = st.navigation([observatory, workspace, filter_lab, analytics, export])

# Render the application
pg.run()
