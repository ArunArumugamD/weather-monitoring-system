from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_get_current_weather():
    response = client.get("/api/current-weather")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_daily_summary():
    response = client.get("/api/daily-summary")
    assert response.status_code == 200
    assert isinstance(response.json(), list)