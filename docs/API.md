# CivicSpend API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Root
```
GET /
```
Returns API information and available endpoints.

### 2. List Runs
```
GET /runs
```
Get all data ingestion runs.

**Response:**
```json
[
  {
    "run_id": "uuid",
    "created_at": "2024-01-01 00:00:00",
    "state": "MN",
    "record_count": 50000
  }
]
```

### 3. List Vendors
```
GET /vendors?run_id={run_id}&limit=100
```
Get vendors with spending data.

**Parameters:**
- `run_id` (optional): Filter by run
- `limit` (optional): Max results (default: 100, max: 1000)

**Response:**
```json
[
  {
    "vendor_id": "uuid",
    "canonical_name": "3M Company",
    "months_active": 24,
    "total_spending": 150000000.00
  }
]
```

### 4. Vendor Timeline
```
GET /vendors/{vendor_id}/timeline?run_id={run_id}
```
Get vendor spending over time.

**Response:**
```json
[
  {
    "month": "2024-01",
    "obligation_sum": 5000000.00,
    "award_count": 15,
    "rolling_3m_avg": 4500000.00
  }
]
```

### 5. Vendor History
```
GET /vendors/{vendor_id}/history?run_id={run_id}&limit=50
```
Get vendor award history.

**Parameters:**
- `run_id` (optional): Filter by run
- `limit` (optional): Max results (default: 50, max: 500)

**Response:**
```json
[
  {
    "award_id": "award123",
    "total_obligation": 1000000.00,
    "action_date": "2024-01-15",
    "awarding_agency_name": "Department of Defense",
    "award_description": "Contract description"
  }
]
```

### 6. List Anomalies
```
GET /anomalies?run_id={run_id}&limit=100
```
Get detected spending anomalies.

**Parameters:**
- `run_id` (optional): Filter by run
- `limit` (optional): Max results (default: 100, max: 1000)

**Response:**
```json
[
  {
    "vendor_id": "uuid",
    "vendor_name": "3M Company",
    "month": "2024-01",
    "obligation_sum": 15000000.00,
    "award_count": 25,
    "severity": "critical"
  }
]
```

### 7. Spending Summary
```
GET /spending/summary?run_id={run_id}
```
Get overall spending statistics.

**Response:**
```json
{
  "total_vendors": 500,
  "total_spending": 500000000.00,
  "avg_monthly_spending": 2000000.00,
  "total_awards": 5000
}
```

### 8. Spending Trends
```
GET /spending/trends?run_id={run_id}
```
Get spending trends over time.

**Response:**
```json
[
  {
    "month": "2024-01",
    "total_spending": 25000000.00,
    "active_vendors": 150
  }
]
```

### 9. Health Check
```
GET /health
```
Check API and database health.

**Response:**
```json
{
  "status": "healthy"
}
```

## Running the API

### Development
```bash
uvicorn civicspend.api.main:app --reload
```

### Production
```bash
uvicorn civicspend.api.main:app --host 0.0.0.0 --port 8000
```

## Interactive Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Python
```python
import requests

# Get vendors
response = requests.get("http://localhost:8000/vendors?limit=10")
vendors = response.json()

# Get vendor timeline
vendor_id = vendors[0]["vendor_id"]
timeline = requests.get(f"http://localhost:8000/vendors/{vendor_id}/timeline")
print(timeline.json())
```

### cURL
```bash
# Get spending summary
curl http://localhost:8000/spending/summary

# Get anomalies
curl "http://localhost:8000/anomalies?limit=20"
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Vendor not found"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Database error: connection failed"
}
```
