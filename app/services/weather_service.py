import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict
from ..models.weather import WeatherData, DailySummary, WeatherAlert
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.OPENWEATHER_API_KEY

    def get_current_weather_all_cities(self) -> List[Dict]:
        """Get current weather for all configured cities"""
        weather_data = []
        for city in settings.CITIES:
            try:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "lat": city["lat"],
                    "lon": city["lon"],
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Create weather data object with explicit city name
                weather = {
                    "name": city["name"],
                    "city": city["name"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "weather_condition": data["weather"][0]["main"],
                    "recorded_at": datetime.utcnow().isoformat()
                }
                logger.info(f"Weather data for {city['name']}: {weather}")
                weather_data.append(weather)
                
                # Store in database
                db_weather = WeatherData(
                    city=city["name"],
                    temperature=data["main"]["temp"],
                    feels_like=data["main"]["feels_like"],
                    weather_condition=data["weather"][0]["main"],
                    recorded_at=datetime.utcnow()
                )
                self.db.add(db_weather)
                
                # Check for temperature alerts
                if data["main"]["temp"] > settings.TEMPERATURE_THRESHOLD:
                    alert = WeatherAlert(
                        city=city["name"],
                        alert_type="HIGH_TEMPERATURE",
                        message=f"Temperature {data['main']['temp']}°C exceeds threshold of {settings.TEMPERATURE_THRESHOLD}°C"
                    )
                    self.db.add(alert)
                
            except Exception as e:
                logger.error(f"Error fetching weather for {city['name']}: {str(e)}")
                continue
                
        self.db.commit()
        return weather_data

    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts from the last 24 hours"""
        yesterday = datetime.utcnow() - timedelta(days=1)
        alerts = self.db.query(WeatherAlert).filter(
            WeatherAlert.created_at >= yesterday
        ).order_by(WeatherAlert.created_at.desc()).all()
        
        return [{
            "city": alert.city,
            "type": alert.alert_type,
            "message": alert.message,
            "created_at": alert.created_at.isoformat()
        } for alert in alerts]

    def get_daily_summary(self, city: str) -> Dict:
        """Generate daily summary for a city"""
        today = datetime.utcnow().date()
        weather_data = self.db.query(WeatherData).filter(
            WeatherData.city == city,
            WeatherData.recorded_at >= today
        ).all()
        
        if not weather_data:
            # If no data today, get current weather
            try:
                city_config = next((c for c in settings.CITIES if c["name"] == city), None)
                if city_config:
                    url = "https://api.openweathermap.org/data/2.5/weather"
                    params = {
                        "lat": city_config["lat"],
                        "lon": city_config["lon"],
                        "appid": self.api_key,
                        "units": "metric"
                    }
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    weather_data = [WeatherData(
                        city=city,
                        temperature=data["main"]["temp"],
                        feels_like=data["main"]["feels_like"],
                        weather_condition=data["weather"][0]["main"],
                        recorded_at=datetime.utcnow()
                    )]
                    self.db.add(weather_data[0])
                    self.db.commit()
            except Exception as e:
                logger.error(f"Error getting current weather for {city}: {str(e)}")
                return None
        
        if not weather_data:
            return None
            
        temperatures = [w.temperature for w in weather_data]
        conditions = [w.weather_condition for w in weather_data]
        
        summary = {
            "city": city,
            "avg_temperature": sum(temperatures) / len(temperatures),
            "max_temperature": max(temperatures),
            "min_temperature": min(temperatures),
            "dominant_condition": max(set(conditions), key=conditions.count),
            "date": today.isoformat()
        }
        
        return summary

    def get_statistics(self, city: str, days: int = 7) -> Dict:
        """Get weather statistics for a city"""
        start_date = datetime.utcnow() - timedelta(days=days)
        data = self.db.query(WeatherData).filter(
            WeatherData.city == city,
            WeatherData.recorded_at >= start_date
        ).all()
        
        if not data:
            return None
            
        temperatures = [d.temperature for d in data]
        conditions = [d.weather_condition for d in data]
        
        return {
            "city": city,
            "period_days": days,
            "avg_temperature": sum(temperatures) / len(temperatures),
            "max_temperature": max(temperatures),
            "min_temperature": min(temperatures),
            "readings_count": len(temperatures),
            "dominant_condition": max(set(conditions), key=conditions.count)
        }