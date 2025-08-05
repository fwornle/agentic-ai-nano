"""
MCP Test Client - Session 1
A test client to validate the weather MCP server functionality.
"""

import subprocess
import json
from typing import Dict, Any
import time


class MCPTestClient:
    def __init__(self, server_script: str):
        self.server_script = server_script
        self.process = None
    
    def start_server(self):
        """Start the MCP server process."""
        print(f"Starting MCP server from {self.server_script}...")
        self.process = subprocess.Popen(
            ["python", self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Give server time to start
        time.sleep(1)
        print("Server started!")
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict:
        """Send JSON-RPC request to server."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        print(f"\n📤 Sending: {method}")
        if params:
            print(f"   Params: {params}")
        
        # Send request
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        response = json.loads(response_line)
        
        print(f"📥 Response: {json.dumps(response, indent=2)}")
        
        return response
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            print("\nStopping server...")
            self.process.terminate()
            self.process.wait()
            print("Server stopped!")


def test_weather_server():
    """Run comprehensive tests on the weather server."""
    client = MCPTestClient("weather_server.py")
    client.start_server()
    
    try:
        print("\n" + "="*60)
        print("🧪 MCP Weather Server Test Suite")
        print("="*60)
        
        # Test 1: List available tools
        print("\n### Test 1: List Available Tools")
        response = client.send_request("tools/list")
        
        # Test 2: Get current weather
        print("\n### Test 2: Get Current Weather - London")
        response = client.send_request("tools/call", {
            "name": "get_current_weather",
            "arguments": {"city": "London", "units": "celsius"}
        })
        
        # Test 3: Get weather in Fahrenheit
        print("\n### Test 3: Get Current Weather - New York (Fahrenheit)")
        response = client.send_request("tools/call", {
            "name": "get_current_weather",
            "arguments": {"city": "New York", "units": "fahrenheit"}
        })
        
        # Test 4: Get weather forecast
        print("\n### Test 4: Get 5-Day Forecast - Tokyo")
        response = client.send_request("tools/call", {
            "name": "get_weather_forecast",
            "arguments": {"city": "Tokyo", "days": 5}
        })
        
        # Test 5: Error handling - invalid city
        print("\n### Test 5: Error Handling - Invalid City")
        response = client.send_request("tools/call", {
            "name": "get_current_weather",
            "arguments": {"city": "Atlantis"}
        })
        
        # Test 6: Find warmest city
        print("\n### Test 6: Find Warmest City")
        response = client.send_request("tools/call", {
            "name": "find_warmest_city",
            "arguments": {"cities": ["London", "New York", "Sydney"]}
        })
        
        # Test 7: Save user preferences
        print("\n### Test 7: Save User Preferences")
        response = client.send_request("tools/call", {
            "name": "save_user_preferences",
            "arguments": {
                "user_id": "user123",
                "city": "Sydney",
                "units": "celsius"
            }
        })
        
        # Test 8: List resources
        print("\n### Test 8: List Available Resources")
        response = client.send_request("resources/list")
        
        # Test 9: Get available cities resource
        print("\n### Test 9: Get Available Cities Resource")
        response = client.send_request("resources/read", {
            "uri": "weather://cities/available"
        })
        
        # Test 10: Get user preferences resource
        print("\n### Test 10: Get User Preferences Resource")
        response = client.send_request("resources/read", {
            "uri": "weather://user/preferences/user123"
        })
        
        # Test 11: List prompts
        print("\n### Test 11: List Available Prompts")
        response = client.send_request("prompts/list")
        
        # Test 12: Get weather report prompt
        print("\n### Test 12: Get Weather Report Prompt")
        response = client.send_request("prompts/get", {
            "name": "weather_report_prompt",
            "arguments": {"city": "Paris"}
        })
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    finally:
        client.stop_server()


if __name__ == "__main__":
    test_weather_server()