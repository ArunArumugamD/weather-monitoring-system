import os
import sys
from pathlib import Path

# Add the application directory to the Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Import test modules
from .test_weather import *
from .test_forecast import *

__all__ = [
    'test_fetch_weather_data',
    'test_daily_summary',
    'test_weather_alerts',
    'test_fetch_forecast',
    'test_forecast_summary'
]