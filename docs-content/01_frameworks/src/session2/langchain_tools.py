# src/session2/langchain_tools.py
"""
Tool implementations for LangChain agents.
"""

from langchain.tools import BaseTool, StructuredTool, tool
from langchain.tools.file_management import ReadFileTool, WriteFileTool
from langchain.tools import DuckDuckGoSearchResults
from typing import Optional, Type
from pydantic import BaseModel, Field
import requests
import json
import math


class CalculatorTool(BaseTool):
    """Enhanced calculator tool for LangChain"""
    name: str = "calculator"
    description: str = "Perform mathematical calculations and expressions"

    def _run(self, expression: str) -> str:
        """Execute the tool"""
        try:
            # Safe evaluation of mathematical expressions
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _arun(self, expression: str):
        """Async version (if needed)"""
        raise NotImplementedError("Calculator doesn't support async")


@tool
def weather_tool(city: str) -> str:
    """Get current weather for a city"""
    # Simulate weather API call
    try:
        # In real implementation, call actual weather API
        weather_data = {
            "temperature": 72,
            "condition": "sunny",
            "humidity": 45
        }
        return f"Weather in {city}: {weather_data['temperature']}°F, {weather_data['condition']}, {weather_data['humidity']}% humidity"
    except Exception as e:
        return f"Error getting weather for {city}: {str(e)}"


class EmailInput(BaseModel):
    """Input schema for email tool"""
    recipient: str = Field(description="Email recipient address")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")


def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email"""
    # Simulate email sending
    return f"Email sent to {recipient} with subject '{subject}'"


# Structured tool creation
email_tool = StructuredTool.from_function(
    func=send_email,
    name="send_email",
    description="Send an email to specified recipient",
    args_schema=EmailInput
)


class NewsAPITool(BaseTool):
    """Tool for fetching news from NewsAPI"""
    name: str = "news_search"
    description: str = "Search for recent news articles on a given topic"
    api_key: str
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(self, query: str, num_articles: int = 5) -> str:
        """Fetch news articles"""
        try:
            # Simulate news API call
            articles = [
                {
                    "title": f"Article about {query} #{i+1}",
                    "url": f"https://news.example.com/article-{i+1}",
                    "description": f"This is a news article about {query}"
                }
                for i in range(num_articles)
            ]

            result = f"Found {len(articles)} articles about '{query}':\n"
            for article in articles:
                result += f"- {article['title']}\n  {article['description']}\n  {article['url']}\n\n"
            
            return result
        except Exception as e:
            return f"Error fetching news: {str(e)}"

    def _arun(self, query: str, num_articles: int = 5):
        """Async version (if needed)"""
        raise NotImplementedError("NewsAPI doesn't support async")