import pandas as pd

class HITLExtractor:
    @staticmethod
    def extract_from_checklist(df, selected_peaks):
        """
        Extracts representative sequences from selected automatic peaks + Absolute First/Last
        selected_peaks: list of dicts with 'date' and 'count'
        """
        if df.empty or 'collection_date' not in df.columns:
            return df
            
        valid_df = df.dropna(subset=['collection_date']).sort_values('collection_date')
        if valid_df.empty:
            return df
            
        representatives = []
        
        # 1. Absolute First
        representatives.append(valid_df.iloc[0])
        
        # 2. Selected Peaks
        for peak in selected_peaks:
            period_start = pd.to_datetime(peak['date'])
            period_end = period_start + pd.Timedelta(days=7) # using weekly peaks
            
            mask = (valid_df['collection_date'] >= period_start) & (valid_df['collection_date'] < period_end)
            peak_df = valid_df[mask]
            
            if not peak_df.empty:
                # Take the first sequence of this peak burst
                representatives.append(peak_df.iloc[0])
                
        # 3. Absolute Last
        representatives.append(valid_df.iloc[-1])
        
        result_df = pd.DataFrame(representatives)
        
        if 'seq_hash' in result_df.columns:
             result_df = result_df.drop_duplicates(subset=['seq_hash'])
        else:
             result_df = result_df.drop_duplicates()
             
        # Sort chronologically
        return result_df.sort_values('collection_date')

    @staticmethod
    def extract_from_custom_checkpoints(df, checkpoint_months):
        """
        Extracts representative sequence from custom user defined months (e.g. overwintering sentinels).
        checkpoint_months: list of strings (e.g., '2024-03', '2024-12')
        """
        if df.empty or 'collection_date' not in df.columns:
            return df
            
        valid_df = df.dropna(subset=['collection_date']).sort_values('collection_date')
        if valid_df.empty:
            return df
            
        representatives = []
        
        representatives.append(valid_df.iloc[0])
        
        for month_str in checkpoint_months:
            start_date = pd.to_datetime(month_str)
            end_date = start_date + pd.DateOffset(months=1)
            
            mask = (valid_df['collection_date'] >= start_date) & (valid_df['collection_date'] < end_date)
            month_df = valid_df[mask]
            
            if not month_df.empty:
                representatives.append(month_df.iloc[0])
                
        representatives.append(valid_df.iloc[-1])
        
        result_df = pd.DataFrame(representatives)
        if 'seq_hash' in result_df.columns:
             result_df = result_df.drop_duplicates(subset=['seq_hash'])
        else:
             result_df = result_df.drop_duplicates()
             
        return result_df.sort_values('collection_date')
