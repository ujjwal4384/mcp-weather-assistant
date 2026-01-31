import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import sys
import json


# Load environment variables from .env file
load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# Initialize the FastMCP server
mcp = FastMCP("WeatherAssistant")

@mcp.tool()
def get_weather(location: str) -> dict:
    """
    Fetches the current weather for a specified location using the OpenWeatherMap API.
location: The city name and optional country code (e.g., "London,uk").

    Returns:
    A dictionary containing weather info or an error message.
    """
    if not OPENWEATHERMAP_API_KEY:
          return {"error": "OpenWeatherMap API key is not set."}
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        print("temperature:", temperature, file=sys.stderr)
    
    except Exception as e:
        if e is requests.exceptions.HTTPError:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.reason}"}
        elif e is requests.exceptions.RequestException:
            return {"error": f"Request error occurred: {e}"}
        return {"error": f"An unexpected error occurred: {e}"}
        
    return {
            "location": data["name"],
            "weather": weather_description,
            "temperature_celsius": f"{temperature}°C",
            "feels_like_celsius": f"{feels_like}°C",
            "humidity": f"{humidity}%",
            "wind_speed_mps": f"{wind_speed} m/s"
    }


if __name__ == "__main__":
        print("Server is running...")
        mcp.run(transport="stdio")