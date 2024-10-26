import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, WeatherData, DailySummary, WeatherAlert
from app.services import WeatherService
from app.config import settings

# Test database setup
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/test_weather_db"

@pytest.fixture
def db_session():
    """Fixture for database session"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)

def test_fetch_weather_data(db_session):
    """Test weather data fetching"""
    service = WeatherService(db_session)
    city = settings.CITIES[0]  # Test with Delhi
    
    weather_data = service.fetch_city_weather(city)
    
    assert weather_data is not None
    assert weather_data.city == city["name"]
    assert isinstance(weather_data.temperature, float)
    assert isinstance(weather_data.feels_like, float)
    assert weather_data.weather_condition is not None

def test_daily_summary(db_session):
    """Test daily summary generation"""
    service = WeatherService(db_session)
    
    # Create test weather data
    test_data = WeatherData(
        city="Delhi",
        temperature=25.0,
        feels_like=26.0,
        weather_condition="Clear",
        recorded_at=datetime.utcnow()
    )
    
    db_session.add(test_data)
    db_session.commit()
    
    summary = service.generate_daily_summary("Delhi")
    assert summary is not None
    assert summary.city == "Delhi"

def test_weather_alerts(db_session):
    """Test weather alert generation"""
    service = WeatherService(db_session)
    
    # Create weather data exceeding threshold
    test_data = WeatherData(
        city="Delhi",
        temperature=settings.TEMPERATURE_THRESHOLD + 1,
        feels_like=36.0,
        weather_condition="Clear",
        recorded_at=datetime.utcnow()
    )
    
    service.check_temperature_alert(test_data)
    
    alerts = db_session.query(WeatherAlert).all()
    assert len(alerts) > 0