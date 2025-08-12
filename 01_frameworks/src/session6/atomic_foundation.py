# From src/session6/atomic_foundation.py
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, validator
from abc import ABC, abstractmethod
from datetime import datetime
import uuid

class AtomicContext(BaseModel):
    """Context container for atomic agent execution."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration for JSON serialization."""
        json_encoders = {datetime: lambda v: v.isoformat()}

# Schema foundation for type-safe operations
T_Input = TypeVar('T_Input', bound=BaseModel)
T_Output = TypeVar('T_Output', bound=BaseModel)

class AtomicAgent(Generic[T_Input, T_Output], ABC):
    """Base class for all atomic agents with type-safe I/O."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.agent_id = str(uuid.uuid4())
        self._execution_count = 0
        
    @abstractmethod
    async def execute(self, input_data: T_Input, context: AtomicContext) -> T_Output:
        """Execute the atomic operation with type-safe inputs and outputs."""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> type[T_Input]:
        """Return the input schema class."""
        pass
    
    @abstractmethod  
    def get_output_schema(self) -> type[T_Output]:
        """Return the output schema class."""
        pass

class AtomicError(Exception):
    """Base exception for atomic agent errors."""
    
    def __init__(
        self, 
        message: str, 
        agent_name: str,
        context: Optional[AtomicContext] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.agent_name = agent_name
        self.context = context
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class ValidationError(AtomicError):
    """Schema validation error."""
    pass

class ExecutionError(AtomicError):
    """Runtime execution error."""
    pass