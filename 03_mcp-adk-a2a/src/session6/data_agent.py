"""
Data Processing Agent

A specialized ACP agent that handles CSV processing and data analysis tasks.
Demonstrates how to extend the base ACPAgent with domain-specific capabilities.
"""

from acp_agent import ACPAgent, AgentCapability
import pandas as pd
from io import StringIO


class DataProcessingAgent(ACPAgent):
    """Agent specialized in data processing and analysis"""
    
    def __init__(self, port: int = 8001):
        # Define what this agent can do
        capabilities = [
            AgentCapability(
                name="process_csv",
                description="Process CSV data with various operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "CSV data as string"},
                        "operation": {"type": "string", "enum": ["summary", "filter", "aggregate"]}
                    },
                    "required": ["data", "operation"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "result": {"type": "object"},
                        "rows_processed": {"type": "integer"}
                    }
                }
            ),
            AgentCapability(
                name="analyze_data",
                description="Perform statistical analysis on datasets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "array"},
                        "analysis_type": {"type": "string", "enum": ["mean", "median", "correlation"]}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "analysis_result": {"type": "object"}
                    }
                }
            )
        ]
        
        super().__init__("DataProcessor", port, capabilities)

    async def execute_capability(self, capability_name: str, payload: dict) -> dict:
        """Implement data processing capabilities"""
        
        if capability_name == "process_csv":
            return await self._process_csv(payload)
        elif capability_name == "analyze_data":
            return await self._analyze_data(payload)
        else:
            return {"error": f"Unknown capability: {capability_name}"}

    async def _process_csv(self, payload: dict) -> dict:
        """Process CSV data with the specified operation"""
        data_str = payload["data"]
        operation = payload["operation"]
        
        try:
            # Parse CSV data
            df = pd.read_csv(StringIO(data_str))
            
            if operation == "summary":
                result = {
                    "shape": list(df.shape),
                    "columns": df.columns.tolist(),
                    "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
                    "summary": {str(k): {str(k2): v2 for k2, v2 in v.items()} 
                               for k, v in df.describe().to_dict().items()}
                }
            elif operation == "filter":
                # Keep only numeric columns
                numeric_df = df.select_dtypes(include=['number'])
                result = {str(k): v.tolist() for k, v in numeric_df.to_dict('list').items()}
            else:  # aggregate
                if len(df.columns) > 0:
                    result = df.groupby(df.columns[0]).size().to_dict()
                    result = {str(k): int(v) for k, v in result.items()}
                else:
                    result = {}
            
            return {
                "result": result,
                "rows_processed": len(df)
            }
            
        except Exception as e:
            return {"error": f"CSV processing failed: {str(e)}"}

    async def _analyze_data(self, payload: dict) -> dict:
        """Perform statistical analysis on the provided data"""
        data = payload["data"]
        analysis_type = payload["analysis_type"]
        
        try:
            df = pd.DataFrame(data)
            
            if analysis_type == "mean":
                result = {str(k): float(v) for k, v in df.mean().to_dict().items()}
            elif analysis_type == "median":
                result = {str(k): float(v) for k, v in df.median().to_dict().items()}
            else:  # correlation
                corr_df = df.corr()
                result = {str(k): {str(k2): float(v2) for k2, v2 in v.items()} 
                         for k, v in corr_df.to_dict().items()}
            
            return {"analysis_result": result}
            
        except Exception as e:
            return {"error": f"Data analysis failed: {str(e)}"}


if __name__ == "__main__":
    agent = DataProcessingAgent()
    agent.run()