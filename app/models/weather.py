from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True)
    city = Column(String)
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Float)  # Added
    wind_speed = Column(Float)  # Added
    wind_direction = Column(Float)  # Added
    pressure = Column(Float)  # Added
    weather_condition = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id = Column(Integer, primary_key=True)
    city = Column(String)
    date = Column(DateTime(timezone=True))
    avg_temperature = Column(Float)
    max_temperature = Column(Float)
    min_temperature = Column(Float)
    avg_humidity = Column(Float)  # Added
    avg_wind_speed = Column(Float)  # Added
    dominant_condition = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherAlert(Base):
    __tablename__ = "weather_alerts"

    id = Column(Integer, primary_key=True)
    city = Column(String)
    alert_type = Column(String)
    message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherForecast(Base):  # New model for forecasts
    __tablename__ = "weather_forecasts"

    id = Column(Integer, primary_key=True)
    city = Column(String)
    forecast_time = Column(DateTime(timezone=True))
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    weather_condition = Column(String)
    probability_precipitation = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())