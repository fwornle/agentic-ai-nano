# Session 1: Basic MCP Server - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **What is the correct decorator to define an MCP tool?**
   - A) `@mcp.function()`
   - B) `@mcp.tool()` ✅ **CORRECT**
   - C) `@mcp.method()`
   - D) `@mcp.action()`

   **Explanation:** The `@mcp.tool()` decorator is the FastMCP framework's way to register a function as an MCP tool that can be called by AI agents.

2. **Which transport mechanism are we using in this session?**
   - A) HTTP
   - B) WebSocket
   - C) stdio ✅ **CORRECT**
   - D) gRPC

   **Explanation:** MCP servers communicate over stdio (standard input/output) by default, which allows them to work as subprocess-based tools.

3. **What format do MCP servers use for communication?**
   - A) REST
   - B) GraphQL
   - C) JSON-RPC ✅ **CORRECT**
   - D) Protocol Buffers

   **Explanation:** MCP is built on JSON-RPC 2.0 protocol for structured communication between clients and servers.

4. **When defining a resource, what URI scheme did we use?**
   - A) http://
   - B) mcp://
   - C) weather:// ✅ **CORRECT**
   - D) resource://

   **Explanation:** We used custom URI schemes like `weather://cities/available` to organize our resources logically within our domain.

5. **What should a tool return when encountering an error?**
   - A) Raise an exception
   - B) Return None
   - C) Return a dict with an "error" key ✅ **CORRECT**
   - D) Return False

   **Explanation:** MCP tools should return structured error responses as dictionaries with an "error" key rather than raising exceptions, which provides better error handling for clients.

---

## 💡 Practical Exercise Solution

**Challenge:** Create a tool that finds the warmest city from a list.

### Complete Solution:

```python
@mcp.tool()
def find_warmest_city(cities: List[str]) -> Dict:
    """
    Find the warmest city from a list.
    
    Args:
        cities: List of city names to compare
        
    Returns:
        Dictionary with the warmest city and its temperature
    """
    # Input validation
    if not cities:
        return {"error": "Cities list cannot be empty"}
    
    if not isinstance(cities, list):
        return {"error": "Cities must be provided as a list"}
    
    warmest = None
    max_temp = float('-inf')
    valid_cities_checked = 0
    
    # Check each city's temperature
    for city in cities:
        if not isinstance(city, str):
            continue  # Skip invalid city names
            
        weather = get_current_weather(city)
        if "error" not in weather:
            temp = weather["temp"]
            valid_cities_checked += 1
            
            if temp > max_temp:
                max_temp = temp
                warmest = {
                    "city": city,
                    "temperature": temp,
                    "units": weather["units"],
                    "condition": weather["condition"],
                    "timestamp": weather["timestamp"]
                }
    
    # Check if we found any valid cities
    if warmest is None:
        return {
            "error": "No valid weather data found for any city",
            "checked_cities": len(cities),
            "valid_responses": valid_cities_checked
        }
    
    # Add comparison metadata
    warmest["comparison"] = {
        "total_cities": len(cities),
        "valid_cities": valid_cities_checked,
        "temperature_advantage": f"{max_temp - (-10):.1f}° warmer than baseline"
    }
    
    return warmest
```

### Key Learning Points:

1. **Input Validation:** Always check for empty lists and invalid input types
2. **Error Handling:** Gracefully handle cases where weather data isn't available
3. **Data Structure:** Return consistent, structured responses
4. **Metadata:** Include useful information about the comparison process
5. **Type Safety:** Use proper type hints and validate input types

### Test Cases You Should Consider:

```python
# Test with valid cities
result = find_warmest_city(["London", "New York", "Sydney"])

# Test with empty list
result = find_warmest_city([])

# Test with invalid city
result = find_warmest_city(["Atlantis", "Wakanda"])

# Test with mixed valid/invalid cities  
result = find_warmest_city(["London", "Atlantis", "Tokyo"])
```

---

## 🎯 Extension Challenges

Once you've mastered the basic solution, try these additional challenges:

1. **Add Temperature Units Conversion:** Modify the function to accept a `units` parameter and convert all temperatures to the same unit before comparison.

2. **Find Coldest City:** Create a companion function `find_coldest_city()` that finds the city with the lowest temperature.

3. **Weather Ranking:** Create a function that returns all cities sorted by temperature from warmest to coldest.

4. **Condition Filtering:** Add the ability to filter cities by weather condition (e.g., only consider cities with "Sunny" weather).

5. **Advanced Comparison:** Include additional factors like humidity or precipitation chance in the comparison logic.