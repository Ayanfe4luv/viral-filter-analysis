import streamlit as st
from utils.gisaid_parser import parse_gisaid_fasta
from utils.minimal_i18n import T

st.title(f"📁 {T('workspace')}")

uploaded_file = st.file_uploader(T('upload_fasta'), type=['fasta'])

if uploaded_file is not None:
    # Read bytes for caching
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    
    with st.spinner("Processing zero-lag parser..."):
        result = parse_gisaid_fasta(file_bytes, file_name)
        
    st.success(T('parsing_success', count=result['count'], time=result['time']))
    
    # Store in session state exactly once
    st.session_state['active_df'] = result['df']
    st.session_state['file_name'] = result['file_name']
    
st.divider()

if 'active_df' in st.session_state:
    st.subheader(T('total_sequences') + f": {len(st.session_state['active_df'])}")
    st.dataframe(st.session_state['active_df'].head(50))
