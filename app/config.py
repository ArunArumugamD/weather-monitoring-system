import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Settings:
    # Get API key from environment variable
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
    
    # Database configuration
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "db")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_USER: str = os.getenv("POSTGRES_USER", "user")
    DATABASE_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    DATABASE_NAME: str = os.getenv("POSTGRES_DB", "weather_db")
    
    # Rest of your settings...
    TEMPERATURE_THRESHOLD: float = 35.0
    UPDATE_INTERVAL: int = 300

    CITIES: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
        {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867}
    ])

settings = Settings()