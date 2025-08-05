"""
MCP Weather Server - Session 1
A basic MCP server that provides weather information through tools, resources, and prompts.
"""

from mcp.server.fastmcp import FastMCP
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server with a descriptive name
mcp = FastMCP("Weather Information Server")

# In-memory storage for user preferences
# In production, you'd use a proper database
user_preferences = {}

# Simulated weather database
WEATHER_DATA = {
    "London": {"temp": 15, "condition": "Cloudy", "humidity": 75},
    "New York": {"temp": 22, "condition": "Sunny", "humidity": 60},
    "Tokyo": {"temp": 18, "condition": "Rainy", "humidity": 85},
    "Sydney": {"temp": 25, "condition": "Clear", "humidity": 55},
}


@mcp.tool()
def get_current_weather(city: str, units: str = "celsius") -> Dict:
    """
    Get current weather for a city.
    
    Args:
        city: Name of the city
        units: Temperature units - "celsius" or "fahrenheit"
    
    Returns:
        Dictionary with weather information
    """
    logger.info(f"Weather request for {city} in {units}")
    
    # Check if we have data for this city
    if city not in WEATHER_DATA:
        logger.warning(f"Weather data not available for {city}")
        return {
            "error": f"Weather data not available for {city}",
            "available_cities": list(WEATHER_DATA.keys())
        }
    
    # Get the weather data and make a copy
    data = WEATHER_DATA[city].copy()
    
    # Convert temperature if Fahrenheit is requested
    if units == "fahrenheit":
        data["temp"] = (data["temp"] * 9/5) + 32
        data["units"] = "°F"
    else:
        data["units"] = "°C"
    
    # Add metadata
    data["city"] = city
    data["timestamp"] = datetime.now().isoformat()
    
    logger.info(f"Successfully retrieved weather for {city}")
    return data


@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> List[Dict]:
    """
    Get weather forecast for multiple days.
    
    Args:
        city: Name of the city
        days: Number of days to forecast (1-7)
    
    Returns:
        List of daily forecasts
    """
    # Validate input parameters
    if days < 1 or days > 7:
        return [{"error": "Days must be between 1 and 7"}]
    
    # Check if city exists
    if city not in WEATHER_DATA:
        return [{"error": f"Weather data not available for {city}"}]
    
    # Simulated forecast generation
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    forecast = []
    
    # Generate forecast for each day
    for i in range(days):
        forecast.append({
            "city": city,
            "day": i + 1,
            "date": (datetime.now().date()).isoformat(),
            "high": 20 + (i * 2),
            "low": 10 + i,
            "condition": conditions[i % len(conditions)],
            "precipitation_chance": (i * 15) % 100
        })
    
    return forecast


@mcp.tool()
def save_user_preferences(user_id: str, city: str, units: str = "celsius") -> Dict:
    """
    Save user weather preferences.
    
    Args:
        user_id: Unique user identifier
        city: Preferred city
        units: Preferred temperature units
    
    Returns:
        Saved preferences
    """
    # Validate units parameter
    if units not in ["celsius", "fahrenheit"]:
        return {"error": "Units must be 'celsius' or 'fahrenheit'"}
    
    # Validate city
    if city not in WEATHER_DATA:
        return {"error": f"City {city} not available"}
    
    # Save preferences
    user_preferences[user_id] = {
        "user_id": user_id,
        "default_city": city,
        "units": units,
        "notifications": True,
        "updated_at": datetime.now().isoformat()
    }
    
    logger.info(f"Saved preferences for user {user_id}")
    return user_preferences[user_id]


@mcp.tool()
def find_warmest_city(cities: List[str]) -> Dict:
    """
    Find the warmest city from a list.
    
    Args:
        cities: List of city names to compare
        
    Returns:
        Dictionary with the warmest city and its temperature
    """
    if not cities:
        return {"error": "Cities list cannot be empty"}
    
    warmest = None
    max_temp = float('-inf')
    
    for city in cities:
        weather = get_current_weather(city)
        if "error" not in weather:
            temp = weather["temp"]
            if temp > max_temp:
                max_temp = temp
                warmest = {
                    "city": city,
                    "temperature": temp,
                    "units": weather["units"],
                    "condition": weather["condition"]
                }
    
    if warmest is None:
        return {"error": "No valid weather data found for any city"}
    
    return warmest


@mcp.resource("weather://cities/available")
def get_available_cities() -> Dict:
    """Get list of cities with weather data available."""
    return {
        "cities": list(WEATHER_DATA.keys()),
        "last_updated": datetime.now().isoformat(),
        "total_count": len(WEATHER_DATA)
    }


@mcp.resource("weather://user/preferences/{user_id}")
def get_user_preferences(user_id: str) -> Dict:
    """Get weather preferences for a specific user."""
    # Check if we have saved preferences
    if user_id in user_preferences:
        return user_preferences[user_id]
    
    # Return default preferences
    return {
        "user_id": user_id,
        "default_city": "London",
        "units": "celsius",
        "notifications": True
    }


@mcp.prompt()
def weather_report_prompt(city: str = "London") -> str:
    """Generate a weather report prompt."""
    return f"""Please provide a detailed weather report for {city} including:
    1. Current temperature and conditions
    2. 3-day forecast
    3. Any weather alerts or recommendations
    4. Best times for outdoor activities
    
    Use the available weather tools to gather this information."""


@mcp.prompt()
def travel_weather_prompt(cities: List[str]) -> str:
    """Generate a travel weather comparison prompt."""
    cities_str = ", ".join(cities)
    return f"""Compare weather conditions for the following cities: {cities_str}
    
    For each city, provide:
    - Current weather
    - 3-day forecast
    - Travel recommendations based on weather
    - Best city to visit based on weather conditions
    
    Use the find_warmest_city tool to identify the best destination."""


if __name__ == "__main__":
    # Run the server
    print("Starting Weather MCP Server...")
    print("Available cities:", ", ".join(WEATHER_DATA.keys()))
    print("Server is ready to accept connections!")
    mcp.run()