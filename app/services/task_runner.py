import time
import schedule
from threading import Thread
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .weather_service import WeatherService
from ..config import settings

def run_weather_update():
    """Update weather data for all cities"""
    db = SessionLocal()
    try:
        weather_service = WeatherService(db)
        weather_service.fetch_all_cities()
    finally:
        db.close()

def start_scheduler():
    """Start the scheduler in a separate thread"""
    schedule.every(settings.UPDATE_INTERVAL).seconds.do(run_weather_update)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    thread = Thread(target=run_scheduler, daemon=True)
    thread.start()
    
    # Run initial update
    run_weather_update()