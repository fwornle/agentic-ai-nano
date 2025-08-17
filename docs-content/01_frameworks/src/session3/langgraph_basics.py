# src/session3/langgraph_basics.py
"""
Basic LangGraph components and state management.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import operator
from datetime import datetime


# 1. State Definition - What data flows between nodes
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_task: str
    results: dict
    iteration_count: int


# Enhanced state for synchronization
class SynchronizedState(TypedDict):
    """State with synchronization tracking"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    results: dict
    completion_status: dict  # Track which branches are complete
    required_branches: list  # Which branches must complete