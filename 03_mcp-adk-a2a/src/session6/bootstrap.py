"""
ACP Network Bootstrap

Utility script to start and manage the complete ACP agent network.
Demonstrates network orchestration and management.
"""

import asyncio
import subprocess
import time
import sys
import signal
import os


class ACPNetworkManager:
    """Manages the ACP agent network lifecycle"""
    
    def __init__(self):
        self.agents = [
            {"script": "data_agent.py", "port": 8001, "name": "DataProcessor"},
            {"script": "text_agent.py", "port": 8002, "name": "TextProcessor"},
            {"script": "coordinator_agent.py", "port": 8000, "name": "Coordinator"}
        ]
        self.processes = []

    async def start_network(self):
        """Start all agents in the network"""
        print("🚀 Starting ACP Agent Network...")
        print()
        
        try:
            # Start each agent in a separate process
            for agent in self.agents:
                print(f"   🔧 Starting {agent['name']} on port {agent['port']}...")
                
                process = subprocess.Popen([
                    sys.executable, agent["script"]
                ], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                self.processes.append({
                    'process': process,
                    'agent': agent
                })
                
                # Give each agent time to start
                time.sleep(2)
            
            print("\\n✅ All agents started successfully!")
            await self._display_network_info()
            
            # Monitor the network
            await self._monitor_network()
            
        except KeyboardInterrupt:
            print("\\n🛑 Shutdown requested...")
            await self._shutdown_network()
            
        except Exception as e:
            print(f"\\n❌ Network startup failed: {e}")
            await self._shutdown_network()

    async def _display_network_info(self):
        """Display network status information"""
        print("\\n🔍 ACP Network Status:")
        print("-" * 40)
        
        for proc_info in self.processes:
            agent = proc_info['agent']
            status = "🟢 Running" if proc_info['process'].poll() is None else "🔴 Stopped"
            print(f"  {agent['name']:<15} | Port {agent['port']} | {status}")
        
        print("\\n📋 Available Endpoints:")
        print("-" * 40)
        for port in [8000, 8001, 8002]:
            print(f"  http://localhost:{port}/metadata     (Agent info)")
            print(f"  http://localhost:{port}/discover     (Discover peers)")
            print(f"  http://localhost:{port}/status       (Health check)")
        
        print("\\n🧪 Testing Commands:")
        print("-" * 40)
        print("  python test_client.py                 (Run test suite)")
        print("  curl http://localhost:8000/status     (Check coordinator)")
        print("  curl http://localhost:8000/discover   (List discovered agents)")

    async def _monitor_network(self):
        """Monitor network health and handle shutdown"""
        print("\\n⏳ Network is running... Press Ctrl+C to stop")
        print("   Monitoring agent health...")
        
        try:
            while True:
                # Check if all processes are still running
                running_count = 0
                for proc_info in self.processes:
                    if proc_info['process'].poll() is None:
                        running_count += 1
                    else:
                        agent_name = proc_info['agent']['name']
                        print(f"\\n⚠️  {agent_name} stopped unexpectedly")
                
                if running_count == 0:
                    print("\\n❌ All agents stopped")
                    break
                
                # Wait before next check
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            print("\\n🛑 Shutdown signal received")

    async def _shutdown_network(self):
        """Gracefully shutdown all agents"""
        print("\\n🔄 Shutting down agent network...")
        
        for i, proc_info in enumerate(self.processes):
            agent = proc_info['agent']
            process = proc_info['process']
            
            if process.poll() is None:  # Still running
                print(f"   🛑 Stopping {agent['name']}...")
                
                try:
                    # Try graceful termination first
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"   ✅ {agent['name']} stopped gracefully")
                    
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination fails
                    print(f"   ⚡ Force killing {agent['name']}...")
                    process.kill()
                    process.wait()
                    
                except Exception as e:
                    print(f"   ⚠️  Error stopping {agent['name']}: {e}")
        
        print("\\n✅ All agents stopped successfully")
        print("   Network shutdown complete")

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        required_packages = ["fastapi", "uvicorn", "aiohttp", "pandas", "pydantic"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print("❌ Missing required packages:")
            for package in missing_packages:
                print(f"   - {package}")
            print("\\nInstall missing packages with:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        return True


async def main():
    """Main entry point"""
    print("ACP Agent Network Bootstrap")
    print("==========================")
    
    manager = ACPNetworkManager()
    
    # Check dependencies
    if not manager.check_dependencies():
        print("\\n❌ Cannot start network - missing dependencies")
        return
    
    print("✅ All dependencies found")
    print()
    
    # Start the network
    await manager.start_network()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")