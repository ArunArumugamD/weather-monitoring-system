from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ... (keep existing schemas) ...

class ForecastResponse(BaseModel):
    city: str
    forecast_time: datetime
    temperature: float
    feels_like: float
    humidity: float
    wind_speed: float
    weather_condition: str
    probability_precipitation: float

    class Config:
        from_attributes = True

class DailyForecastSummary(BaseModel):
    date: str
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    avg_humidity: float
    avg_wind_speed: float
    dominant_condition: str