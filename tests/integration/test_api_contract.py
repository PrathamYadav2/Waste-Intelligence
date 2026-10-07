import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from src.api.main import create_app

client = TestClient(create_app())

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "components" in data

def test_request_id_header():
    res = client.get("/health")
    assert "X-Request-ID" in res.headers
    assert "X-Response-Time-ms" in res.headers

def test_models_endpoint_implemented():
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    assert "models" in res.json()

def test_regional_overview_endpoint():
    res = client.get("/api/v1/regional/overview")
    assert res.status_code == 200
    data = res.json()
    assert "regions" in data
    assert data["total_regions"] == 12

def test_forecast_endpoint():
    res = client.get("/api/v1/forecast")
    assert res.status_code == 200
    data = res.json()
    assert "forecasts" in data
    assert len(data["forecasts"]) == 48  # 12 regions * 4 years
