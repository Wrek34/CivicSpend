# Testing Guide

## Overview

CivicSpend uses pytest for testing with coverage tracking.

## Running Tests

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=civicspend --cov-report=html
```

### Specific Test File
```bash
pytest tests/test_ml_evidence.py -v
```

### Specific Test
```bash
pytest tests/test_ml_evidence.py::test_isolation_forest_detection -v
```

## Test Structure

```
tests/
├── test_db.py              # Database operations
├── test_api_client.py      # API client with mocking
├── test_mock_ingest.py     # Mock data ingestion
├── test_ml_evidence.py     # ML detection + evidence
├── test_export.py          # Export functionality
└── test_e2e_pipeline.py    # End-to-end pipeline
```

## Test Categories

### Unit Tests
Test individual components in isolation.

**Example**: `test_vendor_matcher.py`
```python
def test_fuzzy_matching():
    matcher = VendorMatcher()
    score = matcher.match("3M Company", "3M Co")
    assert score > 85
```

### Integration Tests
Test multiple components together.

**Example**: `test_ml_evidence.py`
```python
def test_ml_detection_with_evidence():
    # Train model
    detector = MLDetector()
    detector.train(features)
    
    # Detect anomalies
    anomalies = detector.detect(features)
    
    # Build evidence
    builder = EvidenceBuilder()
    evidence = builder.build(anomalies[0])
    
    assert len(evidence['top_awards']) > 0
```

### End-to-End Tests
Test full pipeline from ingestion to export.

**Example**: `test_e2e_pipeline.py`
```python
def test_full_pipeline():
    # Ingest mock data
    run_id = ingest_mock_data()
    
    # Normalize vendors
    normalize_vendors(run_id)
    
    # Build features
    build_features(run_id)
    
    # Train model
    train_model(run_id)
    
    # Detect anomalies
    anomalies = detect_anomalies(run_id)
    
    assert len(anomalies) > 0
```

## Test Data

### Mock Data
Located in `civicspend/ingest/mock_data.py`

**Vendors**: 12 Minnesota vendors
**Time range**: 24 months
**Awards**: ~500 synthetic awards
**Anomalies**: 3 injected spikes

### Fixtures
Common test fixtures in `tests/conftest.py` (if created)

```python
@pytest.fixture
def test_db():
    """Create temporary test database."""
    db_path = "test_civicspend.duckdb"
    init_database(db_path)
    yield db_path
    os.remove(db_path)
```

## Coverage Targets

| Module | Target | Current |
|--------|--------|---------|
| `ingest/` | 80% | 85% |
| `normalize/` | 80% | 80% |
| `features/` | 75% | 75% |
| `detect/` | 90% | 90% |
| `explain/` | 85% | 85% |
| `cli/` | 60% | 60% |
| `ui/` | 40% | 40% |
| **Overall** | **70%** | **70%** |

## Writing Tests

### Test Naming
- File: `test_<module>.py`
- Function: `test_<functionality>`
- Class: `Test<Component>`

### Test Structure
```python
def test_feature():
    # Arrange: Setup test data
    data = create_test_data()
    
    # Act: Execute function
    result = process_data(data)
    
    # Assert: Verify result
    assert result == expected
```

### Assertions
```python
# Equality
assert actual == expected

# Membership
assert item in collection

# Exceptions
with pytest.raises(ValueError):
    invalid_operation()

# Approximate
assert abs(actual - expected) < 0.01
```

## Mocking

### API Mocking
```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {'data': []}
    result = fetch_awards()
    assert result == []
```

### Database Mocking
```python
def test_with_temp_db(tmp_path):
    db_path = tmp_path / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    # ... test operations
    conn.close()
```

## Continuous Integration

### GitHub Actions
Located in `.github/workflows/ci.yml`

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=civicspend
```

## Performance Testing

### Benchmark Tests
```python
import time

def test_performance():
    start = time.time()
    process_large_dataset()
    duration = time.time() - start
    assert duration < 10.0  # Must complete in 10s
```

## Validation Tests

### Injected Anomaly Tests
```python
def test_detect_injected_spike():
    # Create normal data
    data = generate_normal_data()
    
    # Inject spike
    data.loc[10, 'obligation_sum'] *= 3
    
    # Detect
    detector = RobustMADDetector()
    anomalies = detector.detect(data)
    
    # Verify spike detected
    assert 10 in anomalies['index'].values
```

## Debugging Tests

### Verbose Output
```bash
pytest -v -s
```

### Stop on First Failure
```bash
pytest -x
```

### Run Last Failed
```bash
pytest --lf
```

### Debug with pdb
```python
def test_debug():
    import pdb; pdb.set_trace()
    result = complex_function()
    assert result == expected
```

## Test Maintenance

### Update Tests When
- Adding new features
- Fixing bugs
- Refactoring code
- Changing APIs

### Test Review Checklist
- [ ] Tests pass locally
- [ ] Coverage >= 70%
- [ ] No hardcoded paths
- [ ] No external dependencies (mock APIs)
- [ ] Fast execution (<30s total)
- [ ] Clear test names
- [ ] Documented edge cases

## Common Issues

### Import Errors
```bash
# Install package in editable mode
pip install -e .
```

### Database Locks
```python
# Always close connections
conn.close()
```

### Flaky Tests
```python
# Use fixed random seeds
np.random.seed(42)
random.seed(42)
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
