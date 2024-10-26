from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
from datetime import datetime, timedelta
import uvicorn
import webbrowser
import threading
import time

from .database import get_db, init_db
from .models.weather import WeatherData, DailySummary, WeatherAlert
from .config import settings
from .services.weather_service import WeatherService

app = FastAPI(title="Weather Monitoring System")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Store active WebSocket connections
active_connections: List[WebSocket] = []

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:8000')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)

async def broadcast_weather(weather_data: dict):
    """Broadcast weather data to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(weather_data)
        except:
            if connection in active_connections:
                active_connections.remove(connection)

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background services"""
    init_db()
    print("\n")
    print("="*50)
    print("Weather Monitoring System is running!")
    print("Access the dashboard at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("="*50)
    print("\n")
    
    # Start periodic updates
    asyncio.create_task(periodic_weather_update())
    
    # Open browser automatically
    threading.Thread(target=open_browser).start()

@app.get("/")
async def root():
    """Serve the main application page"""
    return FileResponse("app/static/index.html")

@app.get("/api/current-weather")
async def get_current_weather(db: Session = Depends(get_db)):
    """Get current weather for all cities"""
    service = WeatherService(db)
    data = service.get_current_weather_all_cities()
    await broadcast_weather(data)
    return data

@app.get("/api/daily-summaries")
async def get_daily_summaries(db: Session = Depends(get_db)):
    """Get daily summaries for all cities"""
    service = WeatherService(db)
    summaries = []
    for city in settings.CITIES:
        try:
            data = service.get_daily_summary(city["name"])
            if data:
                summaries.append(data)
        except Exception as e:
            print(f"Error getting summary for {city['name']}: {str(e)}")
    return summaries

@app.get("/api/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    """Get active weather alerts"""
    service = WeatherService(db)
    return service.get_active_alerts()

async def periodic_weather_update():
    """Update weather data every UPDATE_INTERVAL seconds"""
    while True:
        try:
            db = next(get_db())
            service = WeatherService(db)
            data = service.get_current_weather_all_cities()
            await broadcast_weather(data)
        except Exception as e:
            print(f"Error in periodic update: {str(e)}")
        finally:
            if db:
                db.close()
        await asyncio.sleep(settings.UPDATE_INTERVAL)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)