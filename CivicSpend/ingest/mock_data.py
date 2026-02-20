"""Mock data generator for testing."""
import random
from datetime import datetime, timedelta

VENDORS = [
    "3M Company", "Target Corporation", "Best Buy", "General Mills",
    "UnitedHealth Group", "US Bank", "Medtronic", "Land O'Lakes",
    "CHS Inc", "Ecolab", "Ameriprise Financial", "Xcel Energy"
]

AGENCIES = [
    "Department of Defense", "Department of Health and Human Services",
    "Department of Transportation", "Department of Agriculture",
    "Department of Energy", "Department of Veterans Affairs"
]

def generate_mock_awards(count: int = 100):
    """Generate mock award data."""
    awards = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(count):
        award = {
            "Award ID": f"CONT_AWD_MN_{i:06d}",
            "Recipient Name": random.choice(VENDORS),
            "Award Amount": round(random.uniform(10000, 5000000), 2),
            "Awarding Agency": random.choice(AGENCIES),
            "Start Date": (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "recipient_duns": f"{random.randint(100000000, 999999999)}",
            "recipient_uei": f"UEI{random.randint(10000, 99999)}"
        }
        awards.append(award)
    
    return {"results": awards, "page_metadata": {"total": count}}
