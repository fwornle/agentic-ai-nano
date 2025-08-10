# src/session2/langchain_basics.py
"""
Basic LangChain components and setup.
"""

# Core imports
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler