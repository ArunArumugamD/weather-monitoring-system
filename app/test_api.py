import requests
from config import settings

def test_api_connection():
    # Test with Delhi's coordinates
    city = settings.CITIES[0]
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": city["lat"],
        "lon": city["lon"],
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    print(f"Testing API connection for {city['name']}...")
    print(f"Using API key: {settings.OPENWEATHER_API_KEY}")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:200]}...")  # Print first 200 chars of response
        
        response.raise_for_status()
        data = response.json()
        
        print(f"\nSuccess! Connected to OpenWeather API")
        print(f"Current weather in {city['name']}:")
        print(f"Temperature: {data['main']['temp']}°C")
        print(f"Weather: {data['weather'][0]['main']}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"\nError: HTTP {e.response.status_code}")
        print("Common issues:")
        if e.response.status_code == 401:
            print("1. The API key might need some time to activate (up to 2 hours)")
            print("2. You might need to verify your email address")
        elif e.response.status_code == 429:
            print("You've exceeded the API call limit")
        print(f"\nFull error message: {str(e)}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_connection()