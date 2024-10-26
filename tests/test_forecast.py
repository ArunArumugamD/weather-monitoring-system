import pytest
from datetime import datetime, timedelta
from app.services import ForecastService
from app.models import WeatherForecast
from app.config import settings

class TestForecastService:
    """Test suite for ForecastService"""

    def test_fetch_forecast(self, db_session):
        """Test forecast retrieval"""
        service = ForecastService(db_session)
        city = settings.CITIES[0]  # Test with Delhi
        
        forecasts = service.fetch_forecast(city)
        
        assert len(forecasts) > 0
        assert all(isinstance(f, WeatherForecast) for f in forecasts)
        assert all(f.city == city["name"] for f in forecasts)
        
        # Verify forecast data structure
        for forecast in forecasts:
            assert hasattr(forecast, 'temperature')
            assert hasattr(forecast, 'humidity')
            assert hasattr(forecast, 'wind_speed')
            assert hasattr(forecast, 'weather_condition')
            assert isinstance(forecast.temperature, float)
            assert isinstance(forecast.humidity, float)
            assert isinstance(forecast.wind_speed, float)

    def test_forecast_summary(self, db_session):
        """Test forecast summary generation"""
        service = ForecastService(db_session)
        city = "Delhi"
        
        # Create multiple test forecast entries
        test_data = [
            WeatherForecast(
                city=city,
                forecast_time=datetime.utcnow() + timedelta(hours=i),
                temperature=25.0 + i,
                feels_like=26.0 + i,
                humidity=60.0,
                wind_speed=10.0,
                weather_condition="Clear",
                probability_precipitation=20.0
            )
            for i in range(24)  # Create 24 hours of data
        ]
        
        for forecast in test_data:
            db_session.add(forecast)
        db_session.commit()
        
        summaries = service.get_daily_forecast_summary(city)
        assert len(summaries) > 0
        
        # Verify summary calculations
        first_summary = summaries[0]
        assert 'avg_temperature' in first_summary
        assert 'avg_humidity' in first_summary
        assert 'avg_wind_speed' in first_summary
        assert 'dominant_condition' in first_summary

    def test_multiple_cities_forecast(self, db_session):
        """Test forecast retrieval for multiple cities"""
        service = ForecastService(db_session)
        
        for city in settings.CITIES:
            forecasts = service.fetch_forecast(city)
            assert len(forecasts) > 0
            assert all(f.city == city["name"] for f in forecasts)

    def test_precipitation_probability(self, db_session):
        """Test precipitation probability handling"""
        service = ForecastService(db_session)
        city = settings.CITIES[0]
        
        forecasts = service.fetch_forecast(city)
        
        for forecast in forecasts:
            assert hasattr(forecast, 'probability_precipitation')
            assert 0 <= forecast.probability_precipitation <= 100

    def test_invalid_city_handling(self, db_session):
        """Test handling of invalid city"""
        service = ForecastService(db_session)
        
        with pytest.raises(Exception):
            service.get_daily_forecast_summary("InvalidCity")

    def test_future_forecast_dates(self, db_session):
        """Test that forecasts are for future dates"""
        service = ForecastService(db_session)
        city = settings.CITIES[0]
        
        forecasts = service.fetch_forecast(city)
        current_time = datetime.utcnow()
        
        for forecast in forecasts:
            assert forecast.forecast_time >= current_time

    def test_forecast_data_ranges(self, db_session):
        """Test that forecast data is within reasonable ranges"""
        service = ForecastService(db_session)
        city = settings.CITIES[0]
        
        forecasts = service.fetch_forecast(city)
        
        for forecast in forecasts:
            assert -50 <= forecast.temperature <= 60  # Reasonable temperature range
            assert 0 <= forecast.humidity <= 100     # Humidity percentage
            assert 0 <= forecast.wind_speed <= 200   # Reasonable wind speed in m/s