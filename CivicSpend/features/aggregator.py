"""Monthly aggregation and feature engineering."""
import pandas as pd
from civicspend.db.connection import get_connection

class MonthlyAggregator:
    """Aggregate spending by vendor and month."""
    
    def __init__(self):
        self.conn = get_connection()
    
    def aggregate_run(self, run_id: str):
        """Aggregate monthly spend for a run."""
        # Get awards with vendor mapping
        query = """
            SELECT 
                avm.vendor_id,
                strftime('%Y-%m', ra.action_date) as year_month,
                ra.obligation_amount
            FROM raw_awards ra
            JOIN award_vendor_map avm ON ra.run_id = avm.run_id AND ra.award_id = avm.award_id
            WHERE ra.run_id = ?
            AND ra.action_date IS NOT NULL
        """
        
        df = pd.read_sql_query(query, self.conn, params=[run_id])
        
        if df.empty:
            return 0
        
        # Monthly aggregation
        monthly = df.groupby(['vendor_id', 'year_month']).agg({
            'obligation_amount': ['sum', 'count', 'mean']
        }).reset_index()
        
        monthly.columns = ['vendor_id', 'year_month', 'obligation_sum', 'award_count', 'avg_award_size']
        
        # Rolling features (3-month window)
        monthly = monthly.sort_values(['vendor_id', 'year_month'])
        monthly['rolling_3m_mean'] = monthly.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
        monthly['rolling_3m_mad'] = monthly.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: (x - x.rolling(3, min_periods=1).median()).abs().rolling(3, min_periods=1).median()
        )
        
        # Insert into database
        for _, row in monthly.iterrows():
            self.conn.execute("""
                INSERT OR REPLACE INTO monthly_vendor_spend (
                    run_id, vendor_id, year_month, obligation_sum, award_count,
                    avg_award_size, rolling_3m_mean, rolling_3m_mad
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                run_id, row['vendor_id'], row['year_month'],
                float(row['obligation_sum']), int(row['award_count']),
                float(row['avg_award_size']), float(row['rolling_3m_mean']),
                float(row['rolling_3m_mad'])
            ])
        
        return len(monthly)
