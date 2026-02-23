import pandas as pd

class VectorizedFilterEngine:
    @staticmethod
    def apply_filters(df, filters_dict):
        """
        O(n) boolean masking
        filters_dict = {
            'location': 'Новосибирск',
            'subtype_in': ['H3N2', 'H1N1'],
            'date_range': (start_date, end_date),
            'global_search': 'keyword'
        }
        """
        if df.empty or not filters_dict:
            return df
            
        mask = pd.Series(True, index=df.index)
        
        for k, v in filters_dict.items():
            if not v:
                continue
                
            if k == 'location':
                mask &= df['location'].str.contains(v, case=False, na=False)
                
            elif k == 'global_search':
                # Search across raw header
                mask &= df['raw_header'].str.contains(v, case=False, na=False)
                
            elif k == 'subtype_in':
                if isinstance(v, list) and len(v) > 0:
                    mask &= df['subtype'].isin(v)
                    
            elif k == 'date_range':
                start, end = v
                if start:
                    mask &= (df['collection_date'] >= pd.to_datetime(start))
                if end:
                    mask &= (df['collection_date'] <= pd.to_datetime(end))

        return df[mask]
