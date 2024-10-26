import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..services.weather_service import WeatherService
from ..config import settings

logger = logging.getLogger(__name__)

class BackgroundService:
    def __init__(self):
        self.running = False
        self.update_interval = settings.UPDATE_INTERVAL

    async def start(self):
        self.running = True
        while self.running:
            try:
                self._process_weather_updates()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in background service: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying

    def stop(self):
        self.running = False

    def _process_weather_updates(self):
        db = SessionLocal()
        try:
            weather_service = WeatherService(db)
            
            # Update weather data for all cities
            logger.info("Fetching weather updates...")
            for city in settings.CITIES:
                try:
                    weather_data = weather_service.fetch_city_weather(city)
                    logger.info(f"Updated weather data for {city['name']}: {weather_data.temperature}°C")
                except Exception as e:
                    logger.error(f"Error updating weather for {city['name']}: {str(e)}")

            # Generate daily summaries if needed
            current_hour = datetime.now().hour
            if current_hour == 0:  # Generate summaries at midnight
                logger.info("Generating daily summaries...")
                for city in settings.CITIES:
                    try:
                        weather_service.generate_daily_summary(city["name"])
                    except Exception as e:
                        logger.error(f"Error generating summary for {city['name']}: {str(e)}")

        finally:
            db.close()