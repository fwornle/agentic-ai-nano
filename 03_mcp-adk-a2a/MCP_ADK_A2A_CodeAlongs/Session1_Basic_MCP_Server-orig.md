# Session 1: Basic MCP Server - Code-Along Tutorial

## 🎯 Learning Objectives
- Understand MCP server architecture
- Implement basic tools, resources, and prompts
- Test MCP server locally with stdio transport
- Debug common MCP server issues

## 📚 Pre-Session Reading
- [MCP Specification - Core Concepts](https://modelcontextprotocol.io/introduction)
- [FastMCP Quick Start](https://github.com/jlowin/fastmcp)

---

## Part 1: Environment Setup (15 minutes)

### Step 1.1: Create Project Structure
```bash
# Create project directory
mkdir mcp-weather-server
cd mcp-weather-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastmcp requests python-dotenv
```

### Step 1.2: Project Structure
```
mcp-weather-server/
├── weather_server.py
├── test_client.py
├── requirements.txt
└── .env
```

### Step 1.3: Create requirements.txt
```txt
fastmcp==0.1.0
requests==2.31.0
python-dotenv==1.0.0
```

---

## Part 2: Building Your First MCP Server (30 minutes)

### Step 2.1: Basic Server Structure
```python
# weather_server.py
from mcp.server.fastmcp import FastMCP
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional

# Initialize MCP server
mcp = FastMCP("Weather Information Server")

# Store for user preferences (in production, use proper database)
user_preferences = {}
```

### Step 2.2: Implement Your First Tool
```python
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
    # In a real implementation, you'd use a weather API
    # For demo purposes, we'll simulate weather data
    
    # Simulated weather data
    weather_data = {
        "London": {"temp": 15, "condition": "Cloudy", "humidity": 75},
        "New York": {"temp": 22, "condition": "Sunny", "humidity": 60},
        "Tokyo": {"temp": 18, "condition": "Rainy", "humidity": 85},
        "Sydney": {"temp": 25, "condition": "Clear", "humidity": 55},
    }
    
    if city not in weather_data:
        return {
            "error": f"Weather data not available for {city}",
            "available_cities": list(weather_data.keys())
        }
    
    data = weather_data[city].copy()
    
    # Convert temperature if needed
    if units == "fahrenheit":
        data["temp"] = (data["temp"] * 9/5) + 32
        data["units"] = "°F"
    else:
        data["units"] = "°C"
    
    data["city"] = city
    data["timestamp"] = datetime.now().isoformat()
    
    return data
```

### Step 2.3: Add a More Complex Tool
```python
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
    if days < 1 or days > 7:
        return [{"error": "Days must be between 1 and 7"}]
    
    # Simulated forecast
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    forecast = []
    
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "date": (datetime.now().date()).isoformat(),
            "high": 20 + (i * 2),
            "low": 10 + i,
            "condition": conditions[i % len(conditions)],
            "precipitation_chance": (i * 15) % 100
        })
    
    return forecast
```

### Step 2.4: Implement Resources
```python
@mcp.resource("weather://cities/available")
def get_available_cities() -> Dict:
    """Get list of cities with weather data available."""
    return {
        "cities": ["London", "New York", "Tokyo", "Sydney"],
        "last_updated": datetime.now().isoformat(),
        "total_count": 4
    }

@mcp.resource("weather://user/preferences/{user_id}")
def get_user_preferences(user_id: str) -> Dict:
    """Get weather preferences for a specific user."""
    if user_id in user_preferences:
        return user_preferences[user_id]
    
    # Default preferences
    return {
        "user_id": user_id,
        "default_city": "London",
        "units": "celsius",
        "notifications": True
    }
```

### Step 2.5: Add Prompts
```python
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
    - Best city to visit based on weather conditions"""
```

### Step 2.6: Add State Management Tool
```python
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
    user_preferences[user_id] = {
        "user_id": user_id,
        "default_city": city,
        "units": units,
        "notifications": True,
        "updated_at": datetime.now().isoformat()
    }
    
    return user_preferences[user_id]
```

---

## Part 3: Testing Your MCP Server (15 minutes)

### Step 3.1: Create Test Client
```python
# test_client.py
import subprocess
import json
from typing import Dict, Any

class MCPTestClient:
    def __init__(self, server_script: str):
        self.server_script = server_script
        self.process = None
    
    def start_server(self):
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            ["python", self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict:
        """Send JSON-RPC request to server."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        # Send request
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        return json.loads(response_line)
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            self.process.wait()

# Test the server
if __name__ == "__main__":
    client = MCPTestClient("weather_server.py")
    client.start_server()
    
    try:
        # Test tool listing
        print("Testing tool listing...")
        response = client.send_request("tools/list")
        print(f"Available tools: {response}")
        
        # Test weather tool
        print("\nTesting weather tool...")
        response = client.send_request("tools/call", {
            "name": "get_current_weather",
            "arguments": {"city": "London", "units": "celsius"}
        })
        print(f"Weather response: {response}")
        
    finally:
        client.stop_server()
```

### Step 3.2: Run the Complete Server
```python
# Add this to the end of weather_server.py
if __name__ == "__main__":
    # Run the server
    mcp.run()
```

---

## Part 4: Debugging and Best Practices (15 minutes)

### Step 4.1: Add Logging
```python
# Add to weather_server.py
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@mcp.tool()
def get_current_weather_v2(city: str, units: str = "celsius") -> Dict:
    """Enhanced weather tool with logging."""
    logger.info(f"Weather request for {city} in {units}")
    
    try:
        # Previous implementation...
        result = get_current_weather(city, units)
        logger.info(f"Successfully retrieved weather for {city}")
        return result
    except Exception as e:
        logger.error(f"Error getting weather for {city}: {str(e)}")
        return {"error": str(e)}
```

### Step 4.2: Error Handling
```python
@mcp.tool()
def get_weather_with_validation(city: str, units: str = "celsius") -> Dict:
    """Weather tool with input validation."""
    # Validate inputs
    if not city or not isinstance(city, str):
        return {"error": "City must be a non-empty string"}
    
    if units not in ["celsius", "fahrenheit"]:
        return {"error": "Units must be 'celsius' or 'fahrenheit'"}
    
    # Sanitize city name
    city = city.strip().title()
    
    return get_current_weather(city, units)
```

---

## 🧪 Testing Your Understanding

### Quick Check Questions

1. **What is the correct decorator to define an MCP tool?**
   - A) `@mcp.function()`
   - B) `@mcp.tool()`
   - C) `@mcp.method()`
   - D) `@mcp.action()`

2. **Which transport mechanism are we using in this session?**
   - A) HTTP
   - B) WebSocket
   - C) stdio
   - D) gRPC

3. **What format do MCP servers use for communication?**
   - A) REST
   - B) GraphQL
   - C) JSON-RPC
   - D) Protocol Buffers

4. **When defining a resource, what URI scheme did we use?**
   - A) http://
   - B) mcp://
   - C) weather://
   - D) resource://

5. **What should a tool return when encountering an error?**
   - A) Raise an exception
   - B) Return None
   - C) Return a dict with an "error" key
   - D) Return False

### Practical Exercise

Create a new tool that:
1. Accepts a list of cities
2. Returns the warmest city
3. Includes error handling for empty lists
4. Logs the comparison operation

```python
# Your implementation here
@mcp.tool()
def find_warmest_city(cities: List[str]) -> Dict:
    """Find the warmest city from a list."""
    # TODO: Implement this function
    pass
```

---

## 📝 Session Summary

You've learned to:
- ✅ Create a basic MCP server with FastMCP
- ✅ Implement tools with proper type hints and documentation
- ✅ Define resources with URI patterns
- ✅ Create prompts for user interactions
- ✅ Test MCP servers using stdio transport
- ✅ Handle errors and add logging

### Next Session Preview
In Session 2, we'll build a more complex File System MCP Server that can:
- Browse directories
- Read/write files
- Search file contents
- Manage file permissions

### Homework
1. Extend the weather server with a `compare_weather` tool
2. Add a resource that tracks weather query history
3. Create a prompt for weather alerts
4. Implement proper error handling for all tools

### Answer Key
1. B) `@mcp.tool()`
2. C) stdio
3. C) JSON-RPC
4. C) weather://
5. C) Return a dict with an "error" key

---

## Additional Resources
- [MCP Python SDK Docs](https://modelcontextprotocol.io/docs/python)
- [FastMCP Examples](https://github.com/jlowin/fastmcp/tree/main/examples)
- [MCP Server Gallery](https://github.com/modelcontextprotocol/servers)