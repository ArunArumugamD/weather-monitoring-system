import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from ..models.weather import WeatherForecast
from ..config import settings

logger = logging.getLogger(__name__)

class ForecastService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.OPENWEATHER_API_KEY

    def fetch_forecast(self, city: Dict) -> List[WeatherForecast]:
        """Fetch 5-day weather forecast for a city"""
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": city["lat"],
                "lon": city["lon"],
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            forecasts = []
            for item in data["list"]:
                forecast = WeatherForecast(
                    city=city["name"],
                    forecast_time=datetime.fromtimestamp(item["dt"]),
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item["wind"]["speed"],
                    weather_condition=item["weather"][0]["main"],
                    probability_precipitation=item.get("pop", 0) * 100
                )
                forecasts.append(forecast)
                self.db.add(forecast)
            
            self.db.commit()
            return forecasts
            
        except Exception as e:
            logger.error(f"Error fetching forecast for {city['name']}: {str(e)}")
            raise

    def get_daily_forecast_summary(self, city: str, days: int = 5) -> List[Dict]:
        """Get daily summary of forecasts"""
        end_date = datetime.utcnow() + timedelta(days=days)
        forecasts = self.db.query(WeatherForecast).filter(
            WeatherForecast.city == city,
            WeatherForecast.forecast_time <= end_date
        ).all()
        
        # Group forecasts by day
        daily_summaries = {}
        for forecast in forecasts:
            day = forecast.forecast_time.date()
            if day not in daily_summaries:
                daily_summaries[day] = {
                    "temperatures": [],
                    "humidity": [],
                    "wind_speed": [],
                    "conditions": []
                }
            
            daily_summaries[day]["temperatures"].append(forecast.temperature)
            daily_summaries[day]["humidity"].append(forecast.humidity)
            daily_summaries[day]["wind_speed"].append(forecast.wind_speed)
            daily_summaries[day]["conditions"].append(forecast.weather_condition)
        
        # Calculate summaries
        result = []
        for day, data in daily_summaries.items():
            result.append({
                "date": day.strftime("%Y-%m-%d"),
                "avg_temperature": sum(data["temperatures"]) / len(data["temperatures"]),
                "max_temperature": max(data["temperatures"]),
                "min_temperature": min(data["temperatures"]),
                "avg_humidity": sum(data["humidity"]) / len(data["humidity"]),
                "avg_wind_speed": sum(data["wind_speed"]) / len(data["wind_speed"]),
                "dominant_condition": max(set(data["conditions"]), key=data["conditions"].count)
            })
        
        return result