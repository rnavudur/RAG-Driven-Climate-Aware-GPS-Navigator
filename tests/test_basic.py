"""
Basic tests for Climate-Aware GPS Navigator
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Climate-Aware GPS Navigator" in data["service"]


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Climate-Aware GPS Navigator"
    assert "docs" in data


def test_api_docs_available():
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_routing_endpoints_exist():
    """Test that routing endpoints are accessible."""
    # Test routing endpoint structure
    response = client.get("/api/v1/routing/")
    # This should either return 200 or 405 (Method Not Allowed)
    assert response.status_code in [200, 405]


def test_hazards_endpoints_exist():
    """Test that hazards endpoints are accessible."""
    # Test hazards endpoint structure
    response = client.get("/api/v1/hazards/")
    # This should either return 200 or 405 (Method Not Allowed)
    assert response.status_code in [200, 405]


def test_explanations_endpoints_exist():
    """Test that explanations endpoints are accessible."""
    # Test explanations endpoint structure
    response = client.get("/api/v1/explanations/")
    # This should either return 200 or 405 (Method Not Allowed)
    assert response.status_code in [200, 405]


if __name__ == "__main__":
    pytest.main([__file__]) 