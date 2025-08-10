# mcp_servers/weather_server.py
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import Dict, List

mcp = FastMCP("Weather Server")

# Simulated weather data
WEATHER_DATA = {
    "London": {"temp": 15, "condition": "Cloudy", "humidity": 75},
    "New York": {"temp": 22, "condition": "Sunny", "humidity": 60},
    "Tokyo": {"temp": 18, "condition": "Rainy", "humidity": 85},
    "Sydney": {"temp": 25, "condition": "Clear", "humidity": 55},
}

@mcp.tool()
def get_current_weather(city: str, units: str = "celsius") -> Dict:
    """Get current weather for a city."""
    if city not in WEATHER_DATA:
        return {"error": f"Weather data not available for {city}"}
    
    data = WEATHER_DATA[city].copy()
    if units == "fahrenheit":
        data["temp"] = (data["temp"] * 9/5) + 32
        data["units"] = "°F"
    else:
        data["units"] = "°C"
    
    data["city"] = city
    data["timestamp"] = datetime.now().isoformat()
    return data

@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> List[Dict]:
    """Get weather forecast for multiple days."""
    if days < 1 or days > 7:
        return [{"error": "Days must be between 1 and 7"}]
    
    if city not in WEATHER_DATA:
        return [{"error": f"Forecast not available for {city}"}]
    
    base_temp = WEATHER_DATA[city]["temp"]
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    
    forecast = []
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "city": city,
            "high": base_temp + (i * 2),
            "low": base_temp - 5 + i,
            "condition": conditions[i % len(conditions)],
            "precipitation_chance": (i * 10) % 80
        })
    
    return forecast

if __name__ == "__main__":
    mcp.run()