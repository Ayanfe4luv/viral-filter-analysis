import streamlit as st
from utils.minimal_i18n import T
from utils.gisaid_parser import convert_df_to_fasta
from datetime import datetime

st.title(f"📋 {T('export')}")

if 'filtered_df' not in st.session_state:
    st.warning("No data to export.")
    st.stop()

df = st.session_state['filtered_df']
st.write(f"Total sequences ready for export: **{len(df)}**")

col1, col2 = st.columns(2)

with col1:
    fasta_output = convert_df_to_fasta(df)
    st.download_button(
        label=T('download_filtered'),
        data=fasta_output,
        file_name=f"surveillance_{datetime.now().strftime('%Y%m%d')}.fasta",
        mime="text/plain",
        use_container_width=True
    )
    
with col2:
    csv_output = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=T('export_csv'),
        data=csv_output,
        file_name=f"metadata_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
