# Session 1: Building Your First MCP Server - A Hands-On Introduction

## 🎯 Learning Outcomes

By the end of this session, you will be able to:
- **Understand** the Model Context Protocol (MCP) architecture and its role in solving the M×N integration problem
- **Build** a functional MCP server that exposes tools, resources, and prompts
- **Implement** proper error handling and logging for production-ready code
- **Test** your MCP server using the stdio transport mechanism
- **Debug** common issues that arise when building MCP servers

## 📚 Chapter Overview

In this hands-on session, we'll build a weather information MCP server from scratch. This server will demonstrate all three core MCP capabilities:
- **Tools**: Functions that can be called by AI agents (getting weather, forecasts)
- **Resources**: Data endpoints that can be queried (available cities, user preferences)
- **Prompts**: Pre-configured templates for common queries

![MCP Architecture](images/mcp-architecture.png)

The diagram above shows how MCP acts as a bridge between AI applications (like Claude or ChatGPT) and various data sources, solving the M×N problem where M applications need to connect to N data sources.

---

## Part 1: Understanding MCP and Environment Setup (15 minutes)

### The M×N Problem

Before we dive into coding, let's understand why MCP exists. Imagine you have:
- 5 different AI applications (Claude, ChatGPT, Gemini, etc.)
- 10 different data sources (databases, APIs, file systems, etc.)

Without MCP, you'd need to write 50 different integrations! MCP solves this by providing a single protocol that any AI can use to talk to any data source.

### Step 1.1: Create Project Structure

Let's start by setting up our development environment. We'll create a dedicated project folder and virtual environment to keep our dependencies isolated.

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

**What's happening here:**
- We create a project directory to organize our code
- A virtual environment isolates our Python dependencies
- FastMCP is our framework for building MCP servers quickly
- Requests will help us make HTTP calls (for future API integration)
- Python-dotenv manages environment variables securely

### Step 1.2: Project Structure

After setup, your project should look like this:

```
mcp-weather-server/
├── weather_server.py      # Main server implementation
├── test_client.py         # Client for testing our server
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables (API keys, etc.)
```

### Step 1.3: Create requirements.txt

Let's document our dependencies for easy reproduction:

```txt
fastmcp==0.1.0
requests==2.31.0
python-dotenv==1.0.0
```

---

## Part 2: Building Your First MCP Server (30 minutes)

Now comes the exciting part - let's build our MCP server! We'll start simple and gradually add more features.

### Step 2.1: Basic Server Structure

First, let's create the foundation of our server. This establishes the basic imports and server initialization.

```python
# weather_server.py
from mcp.server.fastmcp import FastMCP
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional

# Initialize MCP server with a descriptive name
# This name will be shown to AI agents when they discover your server
mcp = FastMCP("Weather Information Server")

# In-memory storage for user preferences
# In production, you'd use a proper database like PostgreSQL or Redis
user_preferences = {}
```

**Key points:**
- `FastMCP` simplifies MCP server creation with decorators
- The server name helps AI agents understand what your server does
- We're using in-memory storage for simplicity (data won't persist between restarts)

### Step 2.2: Implement Your First Tool

Tools are the heart of MCP - they're functions that AI agents can call. Let's create a weather lookup tool:

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
    # In a real implementation, you'd call a weather API like OpenWeatherMap
    # For this tutorial, we'll use simulated data to avoid API key requirements
    
    # Simulated weather database
    weather_data = {
        "London": {"temp": 15, "condition": "Cloudy", "humidity": 75},
        "New York": {"temp": 22, "condition": "Sunny", "humidity": 60},
        "Tokyo": {"temp": 18, "condition": "Rainy", "humidity": 85},
        "Sydney": {"temp": 25, "condition": "Clear", "humidity": 55},
    }
    
    # Check if we have data for this city
    if city not in weather_data:
        return {
            "error": f"Weather data not available for {city}",
            "available_cities": list(weather_data.keys())
        }
    
    # Get the weather data and make a copy to avoid modifying the original
    data = weather_data[city].copy()
    
    # Convert temperature if Fahrenheit is requested
    if units == "fahrenheit":
        data["temp"] = (data["temp"] * 9/5) + 32
        data["units"] = "°F"
    else:
        data["units"] = "°C"
    
    # Add metadata to the response
    data["city"] = city
    data["timestamp"] = datetime.now().isoformat()
    
    return data
```

**Important concepts:**
- The `@mcp.tool()` decorator registers this function as an MCP tool
- Type hints are crucial - they tell AI agents how to use your tool
- Docstrings become tool descriptions visible to AI agents
- Always return structured data (dictionaries) with clear error messages

### Step 2.3: Add a More Complex Tool - Weather Forecasting

Let's add a forecasting tool that demonstrates working with more complex parameters:

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
    # Validate input parameters
    if days < 1 or days > 7:
        return [{"error": "Days must be between 1 and 7"}]
    
    # Simulated forecast generation
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    forecast = []
    
    # Generate forecast for each day
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "date": (datetime.now().date()).isoformat(),
            "high": 20 + (i * 2),  # Simulated temperature variation
            "low": 10 + i,
            "condition": conditions[i % len(conditions)],
            "precipitation_chance": (i * 15) % 100
        })
    
    return forecast
```

**Key insights:**
- Input validation prevents errors and guides users
- Return type `List[Dict]` tells agents to expect multiple items
- Consistent data structure makes the API predictable

### Step 2.4: Implement Resources

Resources are different from tools - they're data endpoints that can be queried but don't perform actions. Think of them as read-only data sources.

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
    # Check if we have saved preferences for this user
    if user_id in user_preferences:
        return user_preferences[user_id]
    
    # Return default preferences if user not found
    return {
        "user_id": user_id,
        "default_city": "London",
        "units": "celsius",
        "notifications": True
    }
```

**Resource concepts:**
- Resources use URI-like paths (e.g., `weather://cities/available`)
- The `{user_id}` syntax creates dynamic routes
- Resources should be idempotent (safe to call multiple times)
- They're perfect for configuration, metadata, or reference data

### Step 2.5: Add Prompts

Prompts are pre-configured templates that help AI agents understand common use cases for your server:

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

**Prompt benefits:**
- Guide AI agents on how to use your tools effectively
- Provide consistent user experiences
- Enable complex workflows with multiple tool calls

### Step 2.6: Add State Management Tool

Let's add a tool that can modify state, demonstrating how MCP servers can maintain user preferences:

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
    # Validate units parameter
    if units not in ["celsius", "fahrenheit"]:
        return {"error": "Units must be 'celsius' or 'fahrenheit'"}
    
    # Save preferences to our in-memory store
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

Testing is crucial for ensuring your MCP server works correctly. Let's create a test client that simulates how AI agents will interact with your server.

### Step 3.1: Create Test Client

This test client demonstrates the JSON-RPC protocol that MCP uses under the hood:

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

**Testing insights:**
- MCP uses JSON-RPC 2.0 protocol for communication
- The stdio transport uses standard input/output streams
- Each request needs a unique ID for correlation
- Always clean up resources (stop the server) after testing

### Step 3.2: Run the Complete Server

Finally, let's add the main entry point to our server:

```python
# Add this to the end of weather_server.py
if __name__ == "__main__":
    # Run the server
    mcp.run()
```

Now you can run your server:
```bash
python weather_server.py
```

---

## Part 4: Debugging and Best Practices (15 minutes)

Professional MCP servers need proper logging and error handling. Let's enhance our server with production-ready features.

### Step 4.1: Add Logging

Logging helps you understand what's happening inside your server:

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
        # Call our original implementation
        result = get_current_weather(city, units)
        logger.info(f"Successfully retrieved weather for {city}")
        return result
    except Exception as e:
        logger.error(f"Error getting weather for {city}: {str(e)}")
        return {"error": str(e)}
```

**Logging best practices:**
- Log at appropriate levels (INFO for normal operations, ERROR for failures)
- Include relevant context in log messages
- Never log sensitive information (API keys, passwords, etc.)

### Step 4.2: Input Validation and Error Handling

Robust error handling prevents crashes and provides helpful feedback:

```python
@mcp.tool()
def get_weather_with_validation(city: str, units: str = "celsius") -> Dict:
    """Weather tool with comprehensive input validation."""
    # Validate city parameter
    if not city or not isinstance(city, str):
        return {"error": "City must be a non-empty string"}
    
    # Validate units parameter
    if units not in ["celsius", "fahrenheit"]:
        return {"error": "Units must be 'celsius' or 'fahrenheit'"}
    
    # Sanitize city name - remove extra spaces and capitalize properly
    city = city.strip().title()
    
    # Check for suspicious input (basic security)
    if len(city) > 100 or any(char in city for char in ['<', '>', ';', '&']):
        return {"error": "Invalid city name"}
    
    return get_current_weather(city, units)
```

---

## 📝 Chapter Summary

Congratulations! You've built your first MCP server. Let's recap what you've learned:

### Key Concepts Mastered:
1. **MCP Architecture**: Understanding how MCP solves the M×N integration problem
2. **Tools**: Created functions that AI agents can call with proper type hints and documentation
3. **Resources**: Implemented read-only data endpoints with URI-based routing
4. **Prompts**: Built templates to guide AI agents in using your server effectively
5. **Testing**: Learned how to test MCP servers using the JSON-RPC protocol
6. **Best Practices**: Added logging, error handling, and input validation

### Your Server Can Now:
- ✅ Provide current weather information for multiple cities
- ✅ Generate multi-day weather forecasts
- ✅ Store and retrieve user preferences
- ✅ Offer helpful prompts for common queries
- ✅ Handle errors gracefully with informative messages
- ✅ Log operations for debugging and monitoring

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

Create a new tool that finds the warmest city from a list:

```python
# Your implementation here
@mcp.tool()
def find_warmest_city(cities: List[str]) -> Dict:
    """
    Find the warmest city from a list.
    
    Args:
        cities: List of city names to compare
        
    Returns:
        Dictionary with the warmest city and its temperature
    """
    # TODO: Implement this function
    # Hints:
    # 1. Check if the list is empty
    # 2. Get temperature for each city
    # 3. Find the maximum temperature
    # 4. Return the result with proper error handling
    pass
```

**Solution** (try it yourself first!):
<details>
<summary>Click to see the solution</summary>

```python
@mcp.tool()
def find_warmest_city(cities: List[str]) -> Dict:
    """Find the warmest city from a list."""
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
```
</details>

---

## Next Session Preview

In Session 2, we'll build a more complex **File System MCP Server** that can:
- Browse directories securely with sandboxing
- Read and write files with proper permissions
- Search file contents using advanced patterns
- Implement security measures to prevent unauthorized access

### Homework

Before the next session, try these challenges:

1. **Extend the weather server** with a `compare_weather` tool that compares weather between two cities
2. **Add a resource** that tracks weather query history (last 10 queries)
3. **Create a prompt** for severe weather alerts
4. **Implement proper error handling** for all tools using try-except blocks

**💡 Hint:** Check the `Session1_Basic_MCP_Server-solution.md` file for answers and detailed explanations.

---

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/specification) - Official protocol documentation
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - Framework we're using
- [MCP Server Examples](https://github.com/modelcontextprotocol/servers) - Community servers for inspiration
- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification) - Protocol MCP is built on

Remember: The best way to learn is by doing. Experiment with the code, break things, and understand why they break. Happy coding! 🚀