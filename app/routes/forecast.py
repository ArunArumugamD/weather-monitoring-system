from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..services.forecast_service import ForecastService
from ..schemas.weather import ForecastResponse, DailyForecastSummary
from ..config import settings  # Add this import

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

@router.get("/{city}", response_model=List[ForecastResponse])
def get_city_forecast(city: str, db: Session = Depends(get_db)):
    """Get 5-day forecast for a city"""
    forecast_service = ForecastService(db)
    
    # Find city configuration
    city_config = next((c for c in settings.CITIES if c["name"] == city), None)
    
    if not city_config:
        raise HTTPException(status_code=404, detail="City not found")
    
    try:
        forecasts = forecast_service.fetch_forecast(city_config)
        return forecasts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{city}", response_model=List[DailyForecastSummary])
def get_forecast_summary(
    city: str, 
    days: int = 5, 
    db: Session = Depends(get_db)
):
    """Get daily summary of forecasts"""
    # Verify city exists
    if not any(c["name"] == city for c in settings.CITIES):
        raise HTTPException(status_code=404, detail="City not found")
        
    forecast_service = ForecastService(db)
    try:
        return forecast_service.get_daily_forecast_summary(city, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))