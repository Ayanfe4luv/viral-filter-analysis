import streamlit as st
import pandas as pd
import time
import hashlib
import io

@st.cache_data(show_spinner=False)
def parse_gisaid_fasta(file_bytes, file_name):
    """
    High-performance parser for GISAID formatted FASTA files.
    Safely decodes UTF-8 (Cyrillic), extracts pipe-delimited metadata, and returns a Pandas DataFrame.
    Target: 10K sequences in < 5 seconds.
    """
    start_time = time.time()
    
    # decode bytes assuming utf-8 (handles cyrillic)
    content = file_bytes.decode('utf-8')
    lines = content.split('\n')
    
    metadata = []
    sequences = []
    
    current_header = None
    current_seq = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if current_header is not None:
                metadata.append(current_header)
                sequences.append("".join(current_seq))
                current_seq = []
            current_header = line[1:]
        else:
            current_seq.append(line)
            
    if current_header is not None:
        metadata.append(current_header)
        sequences.append("".join(current_seq))
        
    df = pd.DataFrame({'raw_header': metadata, 'sequence': sequences})
    
    # Fast vectorized extraction of GISAID parts
    # Expected format: A/Новосибирск/RII-7.429/2024|A_/_H3N2|HA|2024-01-17
    
    parts = df['raw_header'].str.split('|', expand=True)
    
    df['strain_name'] = parts[0] if 0 in parts.columns else df['raw_header']
    df['subtype'] = parts[1].str.replace('_/_', '').str.strip() if 1 in parts.columns else 'Unknown'
    df['segment'] = parts[2].str.strip() if 2 in parts.columns else 'Unknown'
    
    # Dates
    if 3 in parts.columns:
        df['collection_date'] = pd.to_datetime(parts[3].str.strip(), errors='coerce')
    else:
        df['collection_date'] = pd.NaT

    # Location (e.g., A/Новосибирск/RII-7.429/2024 -> Новосибирск)
    location_parts = df['strain_name'].str.split('/', expand=True)
    df['location'] = location_parts[1] if 1 in location_parts.columns else 'Unknown'
    
    # Pre-compute hierarchical clades if needed, currently leaving space for L1-L6
    df['clade_l1'] = df['subtype']
    
    # Vectorized Hashing for Tracking
    # Although apply implies a loop, md5 on short strings is heavily optimized in C
    def fast_hash(s):
        return hashlib.md5(s.encode()).hexdigest()[:8]
    
    df['seq_hash'] = df['sequence'].apply(fast_hash)
    
    parse_time = time.time() - start_time
    
    return {
        'df': df,
        'count': len(df),
        'time': round(parse_time, 2),
        'file_name': file_name
    }

def convert_df_to_fasta(df):
    """Converts a filtered DataFrame back to FASTA format text for export."""
    buffer = io.StringIO()
    for _, row in df.iterrows():
        buffer.write(f">{row['raw_header']}\n")
        # Write sequence breaking every 80 chars for standard FASTA format
        seq = row['sequence']
        for i in range(0, len(seq), 80):
            buffer.write(f"{seq[i:i+80]}\n")
    return buffer.getvalue()
