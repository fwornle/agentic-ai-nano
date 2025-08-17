# From src/session6/context_providers.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from atomic_foundation import AtomicContext

class ContextProvider(ABC):
    """Abstract base class for context providers."""
    
    @abstractmethod
    async def provide(self, context: AtomicContext) -> Dict[str, Any]:
        """Provide context-specific resources."""
        pass
    
    @abstractmethod
    def get_provider_type(self) -> str:
        """Return the type of context this provider supplies."""
        pass

class DatabaseContextProvider(ContextProvider):
    """Provides database connections and queries."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection_pool = None
        
    async def provide(self, context: AtomicContext) -> Dict[str, Any]:
        """Provide database connection with user context."""
        # Initialize connection pool if needed
        if self._connection_pool is None:
            self._connection_pool = await self._create_pool()
        
        return {
            "db_connection": self._connection_pool.get_connection(),
            "user_id": context.user_id,
            "session_id": context.session_id,
            "query_timeout": 30
        }
    
    def get_provider_type(self) -> str:
        return "database"
    
    async def _create_pool(self):
        """Create database connection pool (simplified implementation)."""
        # In production, use proper connection pooling
        return MockConnectionPool(self.connection_string)

class MockConnectionPool:
    """Mock connection pool for demonstration."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def get_connection(self):
        return MockDatabaseConnection(self.connection_string)

class MockDatabaseConnection:
    """Mock database connection."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string