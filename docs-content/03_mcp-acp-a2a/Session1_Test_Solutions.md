# Session 1: Building Your First MCP Server - Test Solutions

## 📝 Multiple Choice Test - Answer Key

### Question 1: MCP Capabilities
**What are the three core capabilities that MCP servers can expose?**  

A) APIs, Databases, and Services  
B) Functions, Classes, and Modules  
C) Tools, Resources, and Prompts ✅  
D) Inputs, Outputs, and Errors  
**Correct Answer: C) Tools, Resources, and Prompts**

**Explanation:** MCP servers expose three types of capabilities: Tools (executable functions that can be called), Resources (data sources that can be queried), and Prompts (reusable templates for common tasks).

---

### Question 2: Tool Decorator
**Which decorator is used to expose a function as an MCP tool?**  

A) `@tool()`  
B) `@mcp.tool()` ✅  
C) `@server.tool()`  
D) `@expose_tool()`  
**Correct Answer: B) `@mcp.tool()`**

**Explanation:** The `@mcp.tool()` decorator is the FastMCP framework's way to register a function as an MCP tool that can be called by AI agents.

---

### Question 3: MCP Inspector Purpose
**What is the primary purpose of MCP Inspector?**  

A) To deploy MCP servers to production  
B) To test, debug, and validate MCP servers ✅  
C) To monitor server performance  
D) To manage server configurations  
**Correct Answer: B) To test, debug, and validate MCP servers**

**Explanation:** MCP Inspector is a developer tool (like Postman for MCP) that provides an interactive interface to explore MCP server capabilities, test tools, debug issues, and validate that servers follow the protocol correctly.

---

### Question 4: Transport Mechanism
**Which transport mechanism is commonly used for local MCP server testing?**  

A) HTTP  
B) WebSocket  
C) stdio (standard input/output) ✅  
D) TCP  
**Correct Answer: C) stdio (standard input/output)**

**Explanation:** MCP servers communicate over stdio (standard input/output) by default for local development, which allows them to work as subprocess-based tools.

---

### Question 5: Type Hints Importance
**Why are type hints important in MCP server functions?**  

A) They improve code readability only  
B) They enable automatic schema generation for AI clients ✅  
C) They are required by Python  
D) They reduce memory usage  
**Correct Answer: B) They enable automatic schema generation for AI clients**

**Explanation:** Type hints are used by the MCP framework to automatically generate JSON schemas that describe the tool's parameters and return values to AI clients, enabling proper validation and usage.

---

### Question 6: Error Handling
**What should MCP tools return when encountering invalid input?**  

A) Raise an exception  
B) Return None  
C) Return structured error messages with helpful information ✅  
D) Log the error silently  
**Correct Answer: C) Return structured error messages with helpful information**

**Explanation:** MCP tools should return structured error messages with helpful information rather than raising exceptions, which provides better error handling for clients.

---

### Question 7: Resources vs Tools
**How do MCP resources differ from tools?**  

A) Resources are executable functions, tools are data sources  
B) Resources provide read-only data access, tools are executable functions ✅  
C) Resources are faster than tools  
D) Resources require authentication, tools do not  
**Correct Answer: B) Resources provide read-only data access, tools are executable functions**

**Explanation:** Resources are read-only data endpoints that provide information (like file contents or database records), while tools are executable functions that can perform actions or computations.

---

### Question 8: MCP Inspector Command
**What command is used to launch MCP Inspector?**  

A) `mcp-inspector`  
B) `npm start inspector`  
C) `npx @modelcontextprotocol/inspector` ✅  
D) `python -m mcp.inspector`  
**Correct Answer: C) `npx @modelcontextprotocol/inspector`**

**Explanation:** MCP Inspector can be launched using the `npx @modelcontextprotocol/inspector` command, which runs the inspector without requiring a global installation.

---

### Question 9: Industry Adoption
**Which company reported 60% faster AI integration development using MCP?**  

A) Microsoft  
B) Google  
C) Block Inc. ✅  
D) OpenAI  
**Correct Answer: C) Block Inc.**

**Explanation:** Block Inc. reported significant development speed improvements when using MCP for their AI integrations, demonstrating the protocol's real-world benefits in enterprise environments.

---

### Question 10: MCP Advantages
**What is the main advantage of MCP over custom API integrations?**  

A) Better performance  
B) Standardized protocol with automatic schema validation ✅  
C) Lower cost  
D) Easier to learn  
**Correct Answer: B) Standardized protocol with automatic schema validation**

**Explanation:** MCP provides a standardized protocol that includes automatic schema validation, discovery mechanisms, and consistent error handling, reducing the complexity of custom integrations.

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

---

## Scoring Guide

- **9-10 correct**: Excellent understanding of MCP server fundamentals
- **7-8 correct**: Good grasp of the core concepts, review specific areas where questions were missed
- **5-6 correct**: Basic understanding present, recommend reviewing the session content before proceeding
- **Below 5**: Recommend thoroughly reviewing Session 1 content and hands-on exercises

## Key Concepts Review

If you missed questions in these areas, review the corresponding sections:

**MCP Architecture (Questions 1, 7, 10):**
- Review "MCP Server Capabilities" section
- Focus on the difference between tools, resources, and prompts
- Study the advantages of standardized protocols

**Implementation Details (Questions 2, 5, 6):**
- Review the FastMCP framework syntax
- Focus on type hints and their importance
- Study error handling best practices

**Development Tools (Questions 3, 8):**
- Review the MCP Inspector section
- Practice using the inspector tool
- Study debugging and validation workflows

**Industry Context (Questions 4, 9):**
- Review transport mechanisms
- Study real-world adoption cases
- Focus on enterprise benefits

---

[← Return to Session 1](Session1_Basic_MCP_Server.md)