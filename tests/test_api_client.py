"""Test API client."""
from civicspend.ingest.api_client import USAspendingClient

def test_client_creation():
    """Test client can be created."""
    client = USAspendingClient()
    assert client is not None
    assert client.session is not None

def test_rate_limiting():
    """Test rate limiting works."""
    import time
    client = USAspendingClient()
    
    start = time.time()
    client._rate_limit()
    client._rate_limit()
    elapsed = time.time() - start
    
    # Should take at least RATE_LIMIT_DELAY seconds
    assert elapsed >= 0.2
