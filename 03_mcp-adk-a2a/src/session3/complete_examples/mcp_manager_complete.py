# Complete MCP Manager Implementation
# This is the full implementation referenced in Session 3

import asyncio
import logging
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from langchain_mcp_adapters import MCPAdapter
from config import Config, MCPServerConfig

logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages multiple MCP servers with health checking and recovery."""
    
    def __init__(self, server_configs: List[MCPServerConfig]):
        self.server_configs = {config.name: config for config in server_configs}
        self.adapters: Dict[str, MCPAdapter] = {}
        self.health_status: Dict[str, bool] = {}
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """Start all configured MCP servers."""
        results = {}
        
        for name, config in self.server_configs.items():
            try:
                logger.info(f"Starting MCP server: {name}")
                adapter = MCPAdapter(
                    command=config.command,
                    args=config.args,
                    timeout=config.timeout
                )
                
                # Test the connection
                await adapter.start()
                tools = await adapter.list_tools()
                
                self.adapters[name] = adapter
                self.health_status[name] = True
                results[name] = True
                
                logger.info(f"MCP server '{name}' started successfully with {len(tools)} tools")
                
            except Exception as e:
                logger.error(f"Failed to start MCP server '{name}': {e}")
                self.health_status[name] = False
                results[name] = False
        
        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor())
        
        return results
    
    async def get_adapter(self, server_name: str) -> Optional[MCPAdapter]:
        """Get an adapter for a specific server, with health check."""
        if server_name not in self.adapters:
            logger.warning(f"Server '{server_name}' not found")
            return None
        
        if not self.health_status.get(server_name, False):
            logger.warning(f"Server '{server_name}' is unhealthy")
            # Try to restart the server
            await self._restart_server(server_name)
        
        return self.adapters.get(server_name)
    
    async def get_all_tools(self) -> Dict[str, List[str]]:
        """Get all available tools from all healthy servers."""
        all_tools = {}
        
        for name, adapter in self.adapters.items():
            if self.health_status.get(name, False):
                try:
                    tools = await adapter.list_tools()
                    all_tools[name] = [tool.name for tool in tools]
                except Exception as e:
                    logger.warning(f"Failed to list tools for server '{name}': {e}")
                    self.health_status[name] = False
        
        return all_tools
    
    async def _health_monitor(self):
        """Background task to monitor server health."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for name, adapter in self.adapters.items():
                    try:
                        # Simple health check - list tools
                        await asyncio.wait_for(adapter.list_tools(), timeout=5.0)
                        self.health_status[name] = True
                    except Exception as e:
                        logger.warning(f"Health check failed for server '{name}': {e}")
                        self.health_status[name] = False
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _restart_server(self, server_name: str) -> bool:
        """Attempt to restart a failed server."""
        if server_name not in self.server_configs:
            return False
        
        try:
            logger.info(f"Attempting to restart server: {server_name}")
            
            # Clean up old adapter
            if server_name in self.adapters:
                try:
                    await self.adapters[server_name].stop()
                except:
                    pass
                del self.adapters[server_name]
            
            # Start new adapter
            config = self.server_configs[server_name]
            adapter = MCPAdapter(
                command=config.command,
                args=config.args,
                timeout=config.timeout
            )
            
            await adapter.start()
            self.adapters[server_name] = adapter
            self.health_status[server_name] = True
            
            logger.info(f"Successfully restarted server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart server '{server_name}': {e}")
            self.health_status[server_name] = False
            return False
    
    async def stop_all_servers(self):
        """Stop all MCP servers and cleanup resources."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        for name, adapter in self.adapters.items():
            try:
                logger.info(f"Stopping MCP server: {name}")
                await adapter.stop()
            except Exception as e:
                logger.warning(f"Error stopping server '{name}': {e}")
        
        self.adapters.clear()
        self.health_status.clear()
    
    @asynccontextmanager
    async def managed_servers(self):
        """Context manager for automatic server lifecycle management."""
        try:
            results = await self.start_all_servers()
            healthy_count = sum(results.values())
            total_count = len(results)
            
            logger.info(f"Started {healthy_count}/{total_count} MCP servers")
            
            if healthy_count == 0:
                raise RuntimeError("No MCP servers started successfully")
            
            yield self
            
        finally:
            await self.stop_all_servers()