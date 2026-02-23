import pandas as pd
from scipy.signal import find_peaks

class EpiWaveDetector:
    @staticmethod
    def detect_epi_waves(df, sensitivity=0.5, min_peak_height=5):
        """
        Find epidemic waves using signal processing over temporal sequence counts.
        Groups by week/month and finds local maxima mathematically.
        """
        if df.empty or 'collection_date' not in df.columns:
            return {'peaks': [], 'wave_count': 0}
            
        valid_df = df.dropna(subset=['collection_date'])
        if valid_df.empty:
            return {'peaks': [], 'wave_count': 0}

        # Analyze weekly counts as array signal
        temporal_counts = valid_df.groupby(valid_df['collection_date'].dt.to_period('W')).size()
        
        if len(temporal_counts) < 3:
            return {'peaks': [], 'wave_count': 0}
            
        # distance=2 ensures peaks are separated by at least 2 weeks to avoid noise grouping
        prominence = max(min_peak_height, min(temporal_counts) + sensitivity * 5)
        peaks, properties = find_peaks(temporal_counts.values, prominence=prominence, distance=2)
        
        peak_list = []
        for p in peaks:
            peak_date = temporal_counts.index[p]
            peak_count = temporal_counts.iloc[p]
            peak_list.append({
                'date': peak_date.start_time,
                'period_str': str(peak_date),
                'count': int(peak_count)
            })
            
        return {
            'peaks': peak_list,
            'wave_count': len(peaks)
        }
