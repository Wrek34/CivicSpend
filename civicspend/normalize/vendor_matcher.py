"""Vendor normalization using fuzzy matching."""
import uuid
from rapidfuzz import fuzz
from civicspend.db.connection import get_connection

class VendorMatcher:
    """Match and normalize vendor names."""
    
    def __init__(self, threshold: float = 85.0):
        self.threshold = threshold
        self.conn = get_connection()
    
    def normalize_name(self, name: str) -> str:
        """Normalize vendor name for matching."""
        if not name:
            return ""
        return name.upper().strip().replace(",", "").replace(".", "")
    
    def find_match(self, name: str, vendor_id: str = None) -> str:
        """Find matching vendor or create new one."""
        normalized = self.normalize_name(name)
        
        # Check existing vendors
        vendors = self.conn.execute("""
            SELECT vendor_id, canonical_name FROM vendor_entities
        """).fetchall()
        
        for vid, canonical in vendors:
            score = fuzz.ratio(normalized, self.normalize_name(canonical))
            if score >= self.threshold:
                return vid
        
        # Create new vendor
        new_id = vendor_id or str(uuid.uuid4())
        self.conn.execute("""
            INSERT OR IGNORE INTO vendor_entities (vendor_id, canonical_name)
            VALUES (?, ?)
        """, [new_id, name])
        
        return new_id
    
    def normalize_run(self, run_id: str):
        """Normalize all vendors in a run."""
        awards = self.conn.execute("""
            SELECT award_id, recipient_name, recipient_duns
            FROM raw_awards
            WHERE run_id = ?
        """, [run_id]).fetchall()
        
        vendor_map = {}
        
        for award_id, name, duns in awards:
            # Use DUNS as strong identifier
            if duns and duns in vendor_map:
                vendor_id = vendor_map[duns]
            else:
                vendor_id = self.find_match(name)
                if duns:
                    vendor_map[duns] = vendor_id
            
            # Insert mapping
            self.conn.execute("""
                INSERT OR IGNORE INTO award_vendor_map (run_id, award_id, vendor_id)
                VALUES (?, ?, ?)
            """, [run_id, award_id, vendor_id])
        
        return len(set(vendor_map.values()))
