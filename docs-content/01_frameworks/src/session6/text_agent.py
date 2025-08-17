"""
Text Processing Agent

Specialized ACP agent for text analysis including summarization and keyword extraction.
Shows how to implement natural language processing capabilities in ACP.
"""

from acp_agent import ACPAgent, AgentCapability
import re
from collections import Counter


class TextProcessingAgent(ACPAgent):
    """Agent specialized in text processing and analysis"""
    
    def __init__(self, port: int = 8002):
        capabilities = [
            AgentCapability(
                name="summarize_text",
                description="Summarize text content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "max_sentences": {"type": "integer", "default": 3}
                    },
                    "required": ["text"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "original_length": {"type": "integer"},
                        "summary_length": {"type": "integer"}
                    }
                }
            ),
            AgentCapability(
                name="extract_keywords",
                description="Extract key terms from text",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "top_k": {"type": "integer", "default": 10}
                    },
                    "required": ["text"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "array"},
                        "word_count": {"type": "integer"}
                    }
                }
            )
        ]
        
        super().__init__("TextProcessor", port, capabilities)

    async def execute_capability(self, capability_name: str, payload: dict) -> dict:
        """Implement text processing capabilities"""
        
        if capability_name == "summarize_text":
            return await self._summarize_text(payload)
        elif capability_name == "extract_keywords":
            return await self._extract_keywords(payload)
        else:
            return {"error": f"Unknown capability: {capability_name}"}

    async def _summarize_text(self, payload: dict) -> dict:
        """Create a summary of the input text"""
        text = payload["text"]
        max_sentences = payload.get("max_sentences", 3)
        
        try:
            # Simple extractive summarization
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return {"error": "No sentences found in text"}
            
            # Take first N sentences as summary (basic approach)
            summary_sentences = sentences[:max_sentences]
            summary = '. '.join(summary_sentences)
            if summary and not summary.endswith('.'):
                summary += '.'
            
            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            }
            
        except Exception as e:
            return {"error": f"Text summarization failed: {str(e)}"}

    async def _extract_keywords(self, payload: dict) -> dict:
        """Extract important keywords from text"""
        text = payload["text"]
        top_k = payload.get("top_k", 10)
        
        try:
            # Simple keyword extraction using word frequency
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = Counter(words)
            
            # Define basic stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
                'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 
                'will', 'would', 'could', 'should', 'can', 'may', 'might'
            }
            
            # Filter and rank keywords
            keywords = [
                {"word": word, "frequency": freq}
                for word, freq in word_freq.most_common(top_k * 2)
                if word not in stop_words and len(word) > 2
            ][:top_k]
            
            return {
                "keywords": keywords,
                "word_count": len(words)
            }
            
        except Exception as e:
            return {"error": f"Keyword extraction failed: {str(e)}"}


if __name__ == "__main__":
    agent = TextProcessingAgent()
    agent.run()