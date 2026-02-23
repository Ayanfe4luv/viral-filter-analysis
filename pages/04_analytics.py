import streamlit as st
import plotly.express as px
from utils.minimal_i18n import T

st.title(f"📊 {T('analytics')}")

if 'filtered_df' not in st.session_state:
    st.warning("Please configure your filtering in the Filter Lab first.")
    st.stop()

df = st.session_state['filtered_df']

if df.empty:
    st.warning("No data to visualize. Adjust filters.")
    st.stop()

st.subheader("Subtype Distribution")
if 'subtype' in df.columns:
    subtype_counts = df['subtype'].value_counts().reset_index()
    subtype_counts.columns = ['Subtype', 'Count']
    fig_pie = px.pie(subtype_counts, values='Count', names='Subtype', hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Temporal Distribution")
if 'collection_date' in df.columns:
    temporal = df.dropna(subset=['collection_date'])
    if not temporal.empty:
        counts = temporal.groupby(temporal['collection_date'].dt.to_period('M')).size().reset_index(name='count')
        counts['month'] = counts['collection_date'].dt.start_time
        fig_bar = px.bar(counts, x='month', y='count')
        st.plotly_chart(fig_bar, use_container_width=True)
