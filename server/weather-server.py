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
        print("Fetching weather data...", file=sys.stderr)
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


@mcp.prompt()
def compare_weather_prompt(location_1: str, location_2: str) -> str:
    """
    Generates a clear, comparative summary of the weather between two specified locations.
    This is the best choice when a user asks to compare, contrast, or see the difference in weather between two places.
    
    Args:
        location_a: The first city for comparison (e.g., "London").
        location_b: The second city for comparison (e.g., "Paris").
    """
    refined_prompt = f"""
    You are acting as a helpful weather analyst. Your goal is to provide a clear and easy-to-read comparison of the weather in two different locations for a user.

    The user wants to compare the weather between "{location_1}" and "{location_2}".

    To accomplish this, follow these steps:
    1.  First, gather the necessary weather data for both "{location_1}" and "{location_1}".
    2.  Once you have the weather data for both locations, DO NOT simply list the raw results.
    3.  Instead, synthesize the information into a concise summary. Your final response should highlight the key differences, focusing on temperature, the general conditions (e.g., 'sunny' vs 'rainy'), and wind speed.
    4.  Present the comparison in a structured format, like a markdown table or a clear bulleted list, to make it easy for the user to understand at a glance.
    """

    return refined_prompt

if __name__ == "__main__":
        print("Server is running...")
        mcp.run(transport="stdio")