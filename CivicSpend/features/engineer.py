"""Feature engineering for ML anomaly detection."""
import numpy as np
import pandas as pd
from civicspend.db.connection import get_connection

class FeatureEngineer:
    """Engineer features for ML models."""
    
    def __init__(self):
        self.conn = get_connection()
    
    def engineer_features(self, run_id: str) -> pd.DataFrame:
        """Create 18 features for ML detection."""
        query = """
            SELECT 
                mvs.vendor_id,
                mvs.year_month,
                mvs.obligation_sum,
                mvs.award_count,
                mvs.avg_award_size,
                mvs.rolling_3m_mean,
                mvs.rolling_3m_mad,
                ve.canonical_name
            FROM monthly_vendor_spend mvs
            JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
            WHERE mvs.run_id = ?
            ORDER BY mvs.vendor_id, mvs.year_month
        """
        
        df = pd.read_sql_query(query, self.conn, params=[run_id])
        
        if df.empty:
            return df
        
        # 1-3: Log transforms (handle zeros)
        df['log_obligation'] = np.log1p(df['obligation_sum'])
        df['log_award_count'] = np.log1p(df['award_count'])
        df['log_avg_size'] = np.log1p(df['avg_award_size'])
        
        # 4-6: Rolling features (already computed)
        df['log_rolling_3m_mean'] = np.log1p(df['rolling_3m_mean'])
        df['log_rolling_3m_mad'] = np.log1p(df['rolling_3m_mad'])
        
        # 7: Month-over-month change
        df['mom_pct_change'] = df.groupby('vendor_id')['obligation_sum'].pct_change()
        df['mom_pct_change'] = df['mom_pct_change'].fillna(0).replace([np.inf, -np.inf], 0)
        
        # 8-9: Cyclical month encoding
        df['month'] = pd.to_datetime(df['year_month'] + '-01').dt.month
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # 10: Vendor tenure (months since first award)
        df['vendor_tenure'] = df.groupby('vendor_id').cumcount() + 1
        
        # 11: Deviation from vendor median
        df['deviation_from_median'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: (x - x.median()) / (x.std() + 1e-6)
        )
        
        # 12: Coefficient of variation (stability measure)
        df['cv'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: x.std() / (x.mean() + 1e-6)
        )
        
        # 13: Award size concentration (largest award / total)
        df['size_concentration'] = df['avg_award_size'] / (df['obligation_sum'] + 1e-6)
        
        # 14-15: Trend features
        df['rolling_trend'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: x.rolling(3, min_periods=1).apply(lambda y: np.polyfit(range(len(y)), y, 1)[0] if len(y) > 1 else 0)
        )
        
        # 16: Volatility (rolling std)
        df['volatility'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: x.rolling(3, min_periods=1).std()
        ).fillna(0)
        
        # 17-18: Relative position in distribution
        df['percentile_rank'] = df.groupby('vendor_id')['obligation_sum'].rank(pct=True)
        df['z_score_vendor'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-6)
        )
        
        return df
    
    def get_feature_columns(self) -> list:
        """Get list of feature columns for ML."""
        return [
            'log_obligation', 'log_award_count', 'log_avg_size',
            'log_rolling_3m_mean', 'log_rolling_3m_mad',
            'mom_pct_change', 'month_sin', 'month_cos',
            'vendor_tenure', 'deviation_from_median', 'cv',
            'size_concentration', 'rolling_trend', 'volatility',
            'percentile_rank', 'z_score_vendor'
        ]
