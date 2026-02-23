import streamlit as st
import pandas as pd
import plotly.express as px
from utils.vectorized_filters import VectorizedFilterEngine
from utils.adaptive_sampler import AdaptiveBiologicalSampler
from utils.peak_detector import EpiWaveDetector
from utils.hitl_extractor import HITLExtractor
from utils.gisaid_parser import convert_df_to_fasta
from utils.minimal_i18n import T
from datetime import datetime

st.title(f"🧬 {T('filter_lab')}")

if 'active_df' not in st.session_state:
    st.warning("Please upload a file in the Workspace first.")
    st.stop()
    
df = st.session_state['active_df']

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"### {T('active_filters')}")
    # Sidebar style vectorized filters
    loc_filter = st.text_input("Location (Contains)", "")
    
    subtypes = df['subtype'].unique() if 'subtype' in df.columns else []
    subtype_filter = st.multiselect("Subtypes", options=subtypes)
    
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)
    
    # Pack dictionary
    filters_dict = {
        'location': loc_filter,
        'subtype_in': subtype_filter,
        'date_range': (start_date, end_date) if start_date or end_date else None
    }
    
with col2:
    st.empty() # Placeholder for stats
    
# FAST Boolean indexing
filtered_df = VectorizedFilterEngine.apply_filters(df, filters_dict)
st.session_state['filtered_df'] = filtered_df

st.info(f"Filtered Dataset Size: {len(filtered_df)}")

# Biological Down-Sampling Engine Expander
with st.expander("🧬 Smart Phylogenetic Down-sampling", expanded=True):
    strategy = st.radio(T('bridging_strategy'), [
        T('hitl_auto_sentinel'),
        T('hitl_auto_peaks'),
        T('hitl_manual_checklist'),
        T('hitl_manual_visual'),
        T('hitl_manual_custom')
    ])
    
    representative_df = pd.DataFrame()
    
    if strategy == T('hitl_auto_sentinel'):
        lifespan = AdaptiveBiologicalSampler.calculate_lifespan_category(filtered_df)
        st.write(f"Detected Lifespan Profile: **{lifespan}**")
        representative_df = AdaptiveBiologicalSampler.apply_proportionality_rule(filtered_df, lifespan)
        st.success(f"Chronological sentinel extraction yielded {len(representative_df)} sequences.")
        
    elif strategy == T('hitl_manual_checklist'):
        wave_data = EpiWaveDetector.detect_epi_waves(filtered_df)
        peaks = wave_data['peaks']
        
        st.markdown("### Selection Checklist")
        st.checkbox(T('absolute_first'), value=True, disabled=True)
        
        selected_peaks = []
        for i, peak in enumerate(peaks):
            if st.checkbox(T('peak_detected', num=i+1, date=peak['period_str'], count=peak['count']), value=True):
                selected_peaks.append(peak)
                
        st.checkbox(T('absolute_last'), value=True, disabled=True)
        
        if st.button(T('extract_hitl')):
            representative_df = HITLExtractor.extract_from_checklist(filtered_df, selected_peaks)
            st.success(f"HITL extraction yielded {len(representative_df)} sequences.")
            
    elif strategy == T('hitl_manual_visual'):
        # Streamlit 1.35 native interactions
        st.write(T('visual_lasso_help'))
        
        if not filtered_df.empty and 'collection_date' in filtered_df.columns:
            plot_df = filtered_df.dropna(subset=['collection_date']).copy()
            counts = plot_df.groupby(plot_df['collection_date'].dt.to_period('W')).size().reset_index(name='count')
            counts['collection_date'] = counts['collection_date'].dt.start_time
            
            fig = px.bar(counts, x='collection_date', y='count', title="Epidemic Curve")
            # The 'rerun' triggers streamlit to capture the user's drag-selection
            event = st.plotly_chart(fig, on_select="rerun", selection_mode=("box", "lasso"))
            
            if event and 'selection' in event and event['selection']['points']:
                # The user selected specific bars
                selected_indices = [p['point_index'] for p in event['selection']['points']]
                selected_counts = counts.iloc[selected_indices]
                
                synthetic_peaks = [{'date': row['collection_date'], 'count': row['count']} for _, row in selected_counts.iterrows()]
                
                if st.button("Extract Representatives from Highlighted Zones"):
                     representative_df = HITLExtractor.extract_from_checklist(filtered_df, synthetic_peaks)
                     st.success(f"Extracted {len(representative_df)} sequences from highlighted zones.")
                     
    elif strategy == T('hitl_manual_custom'):
        custom_dates_str = st.text_input("Enter Target Months (YYYY-MM, comma separated):", "2024-03, 2024-12")
        targets = [x.strip() for x in custom_dates_str.split(',') if x.strip()]
        if st.button("Extract from Target Months"):
            representative_df = HITLExtractor.extract_from_custom_checkpoints(filtered_df, targets)
            st.success(f"Extracted {len(representative_df)} overwintering sentinels.")
            
    # Always make result available for download
    if not representative_df.empty:
        fasta_output = convert_df_to_fasta(representative_df)
        st.download_button(
            label=T('download_filtered_count', count=len(representative_df)),
            data=fasta_output,
            file_name=f"vir_seq_sift_{datetime.now().strftime('%Y%m%d_%H%M')}.fasta",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )
