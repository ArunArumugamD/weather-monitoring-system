# Weather Monitoring System

A real-time weather monitoring system for major Indian metropolitan cities, providing weather updates, alerts, and visualizations.

## Features Implemented
- Real-time monitoring of 6 Indian metros (Delhi, Mumbai, Chennai, Bangalore, Kolkata, Hyderabad)
- Automated data collection every 5 minutes
- Daily weather summaries with statistics
- Temperature threshold alerts
- Interactive visualizations
- Bonus: Additional weather parameters and forecasts

## Quick Setup

1. Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose
- OpenWeatherMap API key (from https://openweathermap.org/)

2. Installation Steps:
```bash
# Clone repository
git clone <repository-url>
cd weather-monitoring

# Update API key in app/config.py
# Replace 'your_api_key_here' with your actual OpenWeatherMap API key

# Start application (Recommended Method)
python start.py

# OR use Docker directly
docker-compose up --build
```

3. Access the Application:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure
```
weather_monitoring/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── schemas/         # Data schemas
│   ├── services/        # Business logic
│   ├── static/          # Frontend files
│   ├── config.py        # Configuration
│   └── main.py         # Application entry
├── tests/              # Test suite
├── start.py           # Startup script
└── docker-compose.yml # Docker config
```

## Key API Endpoints
- GET /api/current-weather - Current weather for all cities
- GET /api/daily-summary/{city} - Daily weather summary
- GET /api/alerts - Active weather alerts
- GET /api/forecast/{city} - Weather forecasts (Bonus)

## Running Tests
```bash
pytest tests/
```

## Shutting Down
- If using start.py: Press Ctrl+C
- If using docker-compose: Run `docker-compose down`

## Troubleshooting
1. API Key Issues:
   - Verify key in config.py
   - New keys need 2 hours to activate

2. No Data Showing:
   - Check Docker containers: `docker ps`
   - View logs: `docker logs weather_monitoring-web-1`

3. Cannot Access Application:
   - Verify http://localhost:8000 is accessible
   - Check if all containers are running