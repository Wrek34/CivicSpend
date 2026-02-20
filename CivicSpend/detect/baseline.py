"""Baseline anomaly detection using Robust MAD."""
import numpy as np
import pandas as pd
from civicspend.db.connection import get_connection

class RobustMADDetector:
    """Detect anomalies using Modified Z-score (Robust MAD)."""
    
    def __init__(self, threshold: float = 3.5):
        self.threshold = threshold
        self.conn = get_connection()
    
    def compute_robust_z(self, series: np.ndarray) -> np.ndarray:
        """Compute robust z-scores using MAD."""
        median = np.median(series)
        mad = np.median(np.abs(series - median))
        
        if mad == 0:
            return np.zeros_like(series)
        
        return 0.6745 * (series - median) / mad
    
    def detect_run(self, run_id: str, min_months: int = 3):
        """Detect anomalies for a run."""
        # Get monthly spend data
        query = """
            SELECT vendor_id, year_month, obligation_sum
            FROM monthly_vendor_spend
            WHERE run_id = ?
            ORDER BY vendor_id, year_month
        """
        
        df = pd.read_sql_query(query, self.conn, params=[run_id])
        
        if df.empty:
            return []
        
        anomalies = []
        
        # Detect per vendor
        for vendor_id, group in df.groupby('vendor_id'):
            if len(group) < min_months:
                continue
            
            values = group['obligation_sum'].values
            robust_z = self.compute_robust_z(values)
            
            # Find anomalies
            for idx, (z_score, row) in enumerate(zip(robust_z, group.itertuples())):
                if abs(z_score) > self.threshold:
                    severity = self._get_severity(abs(z_score))
                    anomalies.append({
                        'vendor_id': vendor_id,
                        'year_month': row.year_month,
                        'z_score': float(z_score),
                        'severity': severity,
                        'value': float(row.obligation_sum)
                    })
        
        return anomalies
    
    def _get_severity(self, z_score: float) -> str:
        """Map z-score to severity."""
        if z_score > 4.0:
            return 'critical'
        elif z_score > 3.5:
            return 'high'
        elif z_score > 3.0:
            return 'medium'
        else:
            return 'low'
