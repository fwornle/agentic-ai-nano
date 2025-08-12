# From src/session6/text_processor_agent.py
from typing import List, Dict, Any
import re
from dataclasses import dataclass
from datetime import datetime

from atomic_foundation import (
    AtomicAgent, AtomicContext, AtomicError, ValidationError, ExecutionError,
    BaseModel, Field, validator
)

class TextInput(BaseModel):
    """Input schema for text processing operations."""
    content: str = Field(..., min_length=1, max_length=10000)
    operation: str = Field(..., pattern=r'^(summarize|extract_keywords|sentiment)$')
    options: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or just whitespace")
        return v.strip()

class TextOutput(BaseModel):
    """Output schema for text processing results."""
    result: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: int
    word_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TextProcessorAgent(AtomicAgent[TextInput, TextOutput]):
    """Atomic agent for text processing operations."""
    
    def __init__(self):
        super().__init__("TextProcessor", "1.0.0")
        
    def get_input_schema(self) -> type[TextInput]:
        """Return the input schema class."""
        return TextInput
    
    def get_output_schema(self) -> type[TextOutput]:
        """Return the output schema class."""
        return TextOutput
        
    async def execute(self, input_data: TextInput, context: AtomicContext) -> TextOutput:
        """Execute text processing with comprehensive error handling."""
        start_time = datetime.utcnow()
        
        try:
            # Validate input schema
            if not isinstance(input_data, TextInput):
                raise ValidationError(
                    f"Invalid input type: expected TextInput, got {type(input_data)}", 
                    self.name, 
                    context
                )
            
            # Process based on operation type
            result = await self._process_text(input_data.content, input_data.operation, input_data.options)
            
            # Calculate processing metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            word_count = len(input_data.content.split())
            
            # Update execution count
            self._execution_count += 1
            
            return TextOutput(
                result=result["text"],
                confidence=result["confidence"],
                processing_time_ms=int(processing_time),
                word_count=word_count,
                metadata={
                    "agent_id": self.agent_id,
                    "execution_count": self._execution_count,
                    "operation": input_data.operation
                }
            )
            
        except Exception as e:
            raise ExecutionError(
                f"Text processing failed: {str(e)}", 
                self.name, 
                context, 
                {"input_length": len(input_data.content)}
            )

    async def _process_text(self, content: str, operation: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Core text processing logic with operation switching."""
        
        if operation == "summarize":
            return await self._summarize(content, options)
        elif operation == "extract_keywords":
            return await self._extract_keywords(content, options)
        elif operation == "sentiment":
            return await self._analyze_sentiment(content, options)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _summarize(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simple extractive summarization."""
        sentences = content.split('. ')
        max_sentences = options.get('max_sentences', 3)
        
        # Simple heuristic: take first and last sentences, plus longest middle sentence
        if len(sentences) <= max_sentences:
            summary = content
        else:
            summary_sentences = [sentences[0]]  # First sentence
            
            # Add longest sentence from middle
            if len(sentences) > 2:
                middle_sentences = sentences[1:-1]
                longest = max(middle_sentences, key=len)
                summary_sentences.append(longest)
            
            # Add last sentence
            if max_sentences > 2:
                summary_sentences.append(sentences[-1])
            
            summary = '. '.join(summary_sentences)
        
        return {
            "text": summary,
            "confidence": 0.8  # Static confidence for demo
        }
    
    async def _extract_keywords(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simple keyword extraction using word frequency."""
        max_keywords = options.get('max_keywords', 5)
        
        # Simple word frequency analysis
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        word_freq = {}
        
        # Count word frequency
        for word in words:
            if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        keyword_list = [word for word, freq in keywords]
        
        return {
            "text": ", ".join(keyword_list),
            "confidence": 0.7  # Static confidence for demo
        }
    
    async def _analyze_sentiment(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Simple sentiment analysis using keyword matching."""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 'love', 'like', 'happy', 'pleased', 'satisfied']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry', 'frustrated', 'disappointed', 'sad', 'upset']
        
        words = content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.6 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "text": sentiment,
            "confidence": confidence
        }