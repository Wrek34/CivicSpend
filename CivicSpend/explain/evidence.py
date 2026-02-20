"""Evidence builder - link anomalies to source awards."""
from civicspend.db.connection import get_connection

class EvidenceBuilder:
    """Build evidence trails for anomalies."""
    
    def __init__(self):
        self.conn = get_connection()
    
    def build_evidence(self, run_id: str, vendor_id: str, year_month: str, top_n: int = 5):
        """Get top contributing awards for an anomaly."""
        query = """
            SELECT 
                ra.award_id,
                ra.recipient_name,
                ra.awarding_agency_name,
                ra.obligation_amount,
                ra.action_date,
                CAST(ra.obligation_amount AS FLOAT) / 
                    (SELECT SUM(obligation_amount) 
                     FROM raw_awards ra2
                     JOIN award_vendor_map avm2 ON ra2.run_id = avm2.run_id AND ra2.award_id = avm2.award_id
                     WHERE avm2.vendor_id = ? 
                     AND strftime('%Y-%m', ra2.action_date) = ?
                     AND ra2.run_id = ?) as pct_of_total
            FROM raw_awards ra
            JOIN award_vendor_map avm ON ra.run_id = avm.run_id AND ra.award_id = avm.award_id
            WHERE avm.vendor_id = ?
            AND strftime('%Y-%m', ra.action_date) = ?
            AND ra.run_id = ?
            ORDER BY ra.obligation_amount DESC
            LIMIT ?
        """
        
        results = self.conn.execute(query, [
            vendor_id, year_month, run_id,
            vendor_id, year_month, run_id,
            top_n
        ]).fetchall()
        
        evidence = []
        for row in results:
            evidence.append({
                'award_id': row[0],
                'recipient_name': row[1],
                'agency': row[2],
                'amount': float(row[3]),
                'date': row[4],
                'pct_of_month': float(row[5]) * 100
            })
        
        return evidence
    
    def get_vendor_context(self, run_id: str, vendor_id: str):
        """Get vendor historical context."""
        query = """
            SELECT 
                ve.canonical_name,
                COUNT(DISTINCT mvs.year_month) as months_active,
                AVG(mvs.obligation_sum) as avg_monthly,
                MIN(mvs.obligation_sum) as min_monthly,
                MAX(mvs.obligation_sum) as max_monthly,
                SUM(mvs.obligation_sum) as total_spend
            FROM vendor_entities ve
            JOIN monthly_vendor_spend mvs ON ve.vendor_id = mvs.vendor_id
            WHERE ve.vendor_id = ? AND mvs.run_id = ?
            GROUP BY ve.canonical_name
        """
        
        result = self.conn.execute(query, [vendor_id, run_id]).fetchone()
        
        if not result:
            return None
        
        return {
            'name': result[0],
            'months_active': result[1],
            'avg_monthly': float(result[2]),
            'min_monthly': float(result[3]),
            'max_monthly': float(result[4]),
            'total_spend': float(result[5])
        }
    
    def generate_narrative(self, anomaly: dict, evidence: list, context: dict) -> str:
        """Generate factual narrative for transparency."""
        vendor_name = context['name']
        year_month = anomaly['year_month']
        current_value = anomaly['value']
        avg_value = context['avg_monthly']
        
        # Calculate change
        pct_change = ((current_value - avg_value) / avg_value) * 100
        direction = "increased" if pct_change > 0 else "decreased"
        
        # Build narrative
        narrative = f"{vendor_name} showed a {anomaly['severity']} spending anomaly in {year_month}.\n\n"
        narrative += f"Monthly spending {direction} to ${current_value:,.2f} "
        narrative += f"from a typical ${avg_value:,.2f} ({abs(pct_change):.1f}% change).\n\n"
        
        narrative += f"Key facts:\n"
        narrative += f"- Total awards this month: {anomaly['award_count']}\n"
        narrative += f"- Historical range: ${context['min_monthly']:,.2f} - ${context['max_monthly']:,.2f}\n"
        narrative += f"- Months active: {context['months_active']}\n\n"
        
        if evidence:
            narrative += f"Top contributing awards:\n"
            for i, e in enumerate(evidence[:3], 1):
                narrative += f"{i}. ${e['amount']:,.2f} from {e['agency']} ({e['pct_of_month']:.1f}% of month)\n"
        
        narrative += f"\nThis represents a significant deviation from normal spending patterns. "
        narrative += f"Further investigation may be warranted to understand the underlying causes."
        
        return narrative
