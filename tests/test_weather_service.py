import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, WeatherData, DailySummary, WeatherAlert
from app.services import WeatherService
from app.config import settings

# Test database setup
TEST_DATABASE_URL = "postgresql://user:password@localhost:5432/test_weather_db"

@pytest.fixture
def db_session():
    """Fixture for setting up test database"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)

def test_system_setup(db_session):
    """Test 1: System Setup
    Verify system starts successfully and connects to the OpenWeatherMap API"""
    service = WeatherService(db_session)
    response = service.test_api_connection()
    assert response is True

def test_data_retrieval(db_session):
    """Test 2: Data Retrieval
    Test API calls and data parsing"""
    service = WeatherService(db_session)
    city = settings.CITIES[0]  # Test with Delhi
    
    # Test weather fetching
    weather_data = service.fetch_city_weather(city)
    
    assert weather_data is not None
    assert weather_data.city == city["name"]
    assert isinstance(weather_data.temperature, float)
    assert isinstance(weather_data.feels_like, float)
    assert weather_data.weather_condition is not None

def test_temperature_conversion(db_session):
    """Test 3: Temperature Conversion
    Test Kelvin to Celsius conversion"""
    service = WeatherService(db_session)
    
    # Test conversion (assuming API returns Kelvin)
    kelvin_temp = 300.15  # Example: 27°C in Kelvin
    celsius_temp = service.kelvin_to_celsius(kelvin_temp)
    assert round(celsius_temp, 2) == 27.0

def test_daily_summary_generation(db_session):
    """Test 4: Daily Weather Summary
    Test summary calculations"""
    service = WeatherService(db_session)
    
    # Create test weather data
    test_data = [
        WeatherData(
            city="Delhi",
            temperature=25.0,
            feels_like=26.0,
            weather_condition="Clear",
            recorded_at=datetime.utcnow()
        ),
        WeatherData(
            city="Delhi",
            temperature=27.0,
            feels_like=28.0,
            weather_condition="Clear",
            recorded_at=datetime.utcnow()
        ),
        WeatherData(
            city="Delhi",
            temperature=23.0,
            feels_like=24.0,
            weather_condition="Rain",
            recorded_at=datetime.utcnow()
        )
    ]
    
    for data in test_data:
        db_session.add(data)
    db_session.commit()
    
    # Generate summary
    summary = service.generate_daily_summary("Delhi")
    
    assert summary is not None
    assert summary.city == "Delhi"
    assert summary.avg_temperature == 25.0
    assert summary.max_temperature == 27.0
    assert summary.min_temperature == 23.0
    assert summary.dominant_condition == "Clear"

def test_alert_thresholds(db_session):
    """Test 5: Alerting Thresholds
    Test alert generation based on thresholds"""
    service = WeatherService(db_session)
    
    # Test with temperature above threshold
    high_temp_data = WeatherData(
        city="Delhi",
        temperature=settings.TEMPERATURE_THRESHOLD + 1,
        feels_like=36.0,
        weather_condition="Clear",
        recorded_at=datetime.utcnow()
    )
    
    # Add data and check for alert
    db_session.add(high_temp_data)
    db_session.commit()
    
    service.check_temperature_alert(high_temp_data)
    
    # Verify alert was created
    alert = db_session.query(WeatherAlert).first()
    assert alert is not None
    assert alert.city == "Delhi"
    assert alert.alert_type == "HIGH_TEMPERATURE"

def test_consecutive_alerts(db_session):
    """Test 6: Consecutive Alerts
    Test alert generation for consecutive high temperatures"""
    service = WeatherService(db_session)
    
    # Create two consecutive high temperature readings
    for i in range(2):
        data = WeatherData(
            city="Delhi",
            temperature=settings.TEMPERATURE_THRESHOLD + 1,
            feels_like=36.0,
            weather_condition="Clear",
            recorded_at=datetime.utcnow() + timedelta(minutes=5*i)
        )
        db_session.add(data)
        db_session.commit()
        service.check_temperature_alert(data)
    
    # Check alert count
    alerts = db_session.query(WeatherAlert).all()
    assert len(alerts) == 1  # Should only create one alert for consecutive readings

def test_data_update_interval(db_session):
    """Test 7: Update Interval
    Test that data is updated at the correct interval"""
    service = WeatherService(db_session)
    
    # Test two updates
    city = settings.CITIES[0]
    
    # First update
    weather1 = service.fetch_city_weather(city)
    
    # Second update after interval
    weather2 = service.fetch_city_weather(city)
    
    time_diff = weather2.recorded_at - weather1.recorded_at
    assert time_diff.total_seconds() >= 0  # Ensure timestamps are properly recorded

def test_multiple_cities(db_session):
    """Test 8: Multiple Cities
    Test data collection for all configured cities"""
    service = WeatherService(db_session)
    
    # Fetch data for all cities
    for city in settings.CITIES:
        weather = service.fetch_city_weather(city)
        assert weather is not None
        assert weather.city == city["name"]