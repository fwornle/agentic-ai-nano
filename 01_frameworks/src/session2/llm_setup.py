# src/session2/llm_setup.py
"""
LLM factory for creating language model instances with different providers.
"""

from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.llms import OpenAI
import os


class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    def create_llm(provider: str, **kwargs):
        """Create LLM instance based on provider"""
        
        if provider == "openai":
            return ChatOpenAI(
                model="gpt-4",
                temperature=kwargs.get("temperature", 0.7),
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        
        elif provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=kwargs.get("temperature", 0.7),
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# Usage example
if __name__ == "__main__":
    llm = LLMFactory.create_llm("openai", temperature=0.1)
    print(f"Created LLM: {llm}")