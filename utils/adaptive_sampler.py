import pandas as pd

class AdaptiveBiologicalSampler:
    @staticmethod
    def calculate_lifespan_category(df):
        """Automatic strain lifespan classification based on collection dates."""
        if df.empty or 'collection_date' not in df.columns:
            return 'Unknown'
            
        valid_dates = df['collection_date'].dropna()
        if valid_dates.empty:
            return 'Unknown'
            
        total_days = (valid_dates.max() - valid_dates.min()).days
        if total_days < 90:      # < 3 months
            return 'Micro'
        elif total_days < 270:   # 3-9 months
            return 'Seasonal'
        else:                    # > 9 months
            return 'Endemic'

    @classmethod
    def apply_proportionality_rule(cls, df, category=None):
        """Dynamic sampling based on biological lifespan to solve temporal bias."""
        if df.empty or 'collection_date' not in df.columns:
            return df
            
        valid_df = df.dropna(subset=['collection_date']).copy()
        if valid_df.empty:
            return df
            
        if category is None:
            category = cls.calculate_lifespan_category(valid_df)
            
        if category == 'Micro':
            return cls._weekly_sentinel_sampling(valid_df)
        elif category == 'Seasonal':
            return cls._monthly_sentinel_sampling(valid_df)
        elif category == 'Endemic':
            return cls._quarterly_sentinel_sampling(valid_df)
        
        return valid_df

    @staticmethod
    def _weekly_sentinel_sampling(df):
        """Take first sequence of every week."""
        df_sorted = df.sort_values('collection_date')
        df_sorted['week_period'] = df_sorted['collection_date'].dt.to_period('W')
        # drop_duplicates keeps the first occurrence by default (Chronological Sentinel)
        return df_sorted.drop_duplicates(subset=['week_period']).drop(columns=['week_period'])

    @staticmethod
    def _monthly_sentinel_sampling(df):
        """Take first sequence of every month."""
        df_sorted = df.sort_values('collection_date')
        df_sorted['month_period'] = df_sorted['collection_date'].dt.to_period('M')
        return df_sorted.drop_duplicates(subset=['month_period']).drop(columns=['month_period'])

    @staticmethod
    def _quarterly_sentinel_sampling(df):
        """Take first sequence of every quarter."""
        df_sorted = df.sort_values('collection_date')
        df_sorted['quarter_period'] = df_sorted['collection_date'].dt.to_period('Q')
        return df_sorted.drop_duplicates(subset=['quarter_period']).drop(columns=['quarter_period'])
