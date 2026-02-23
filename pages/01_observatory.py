import streamlit as st
from utils.minimal_i18n import T

st.title(f"🌍 {T('observatory')}")

# Very simple KPI dashboard (no heavy processing)
st.markdown("### Global Epidemiological Surveillance & Trans-Eurasian Monitoring Platform")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Active Monitoring Regions", value="85", delta="2")
with col2:
    st.metric(label="Latest Epi-Season Start", value="Nov 2024")
with col3:
    st.metric(label="System Status", value="Zero-Lag Ready")
    
st.divider()

col4, _ = st.columns([1, 4])
with col4:
    if st.button(T('toggle_lang')):
        import utils.minimal_i18n as i18n
        i18n.toggle_language()
        st.rerun()
