from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..models.weather import WeatherData, DailySummary, WeatherAlert
from ..schemas.weather import (
    WeatherDataResponse, 
    DailySummaryResponse, 
    AlertResponse,
    CityWeatherResponse,
    WeatherStatsResponse
)
from ..services.weather_service import WeatherService

router = APIRouter(prefix="/api", tags=["weather"])

@router.get("/current-weather", response_model=List[WeatherDataResponse])
def get_current_weather(db: Session = Depends(get_db)):
    """Get current weather for all cities"""
    weather_service = WeatherService(db)
    return weather_service.get_current_weather_all_cities()

@router.get("/weather/{city}", response_model=CityWeatherResponse)
def get_city_weather(city: str, db: Session = Depends(get_db)):
    """Get detailed weather information for a specific city"""
    weather_service = WeatherService(db)
    
    current_weather = weather_service.get_current_weather(city)
    if not current_weather:
        raise HTTPException(status_code=404, detail="City not found")
    
    daily_summary = weather_service.get_latest_summary(city)
    alerts = weather_service.get_active_alerts(city)
    
    return CityWeatherResponse(
        current_weather=current_weather,
        daily_summary=daily_summary,
        active_alerts=alerts
    )

@router.get("/daily-summary/{city}", response_model=DailySummaryResponse)
def get_daily_summary(city: str, db: Session = Depends(get_db)):
    """Get daily weather summary for a specific city"""
    weather_service = WeatherService(db)
    summary = weather_service.get_latest_summary(city)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    """Get all active weather alerts"""
    weather_service = WeatherService(db)
    return weather_service.get_active_alerts()

@router.get("/statistics/{city}", response_model=WeatherStatsResponse)
def get_city_statistics(
    city: str, 
    days: int = 7, 
    db: Session = Depends(get_db)
):
    """Get statistical analysis of weather data for a city"""
    weather_service = WeatherService(db)
    return weather_service.calculate_statistics(city, days)