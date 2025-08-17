# src/session4/custom_tools.py
"""
Custom tools for CrewAI agents to extend their capabilities.
"""

from crewai.tools import BaseTool
from typing import Any, Type, Optional
from pydantic import BaseModel, Field
import requests
import json
import sqlite3
from datetime import datetime
import pandas as pd

class SearchInput(BaseModel):
    """Input schema for search tool."""
    query: str = Field(..., description="Search query")
    max_results: int = Field(default=5, description="Maximum number of results")

class DatabaseQueryInput(BaseModel):
    """Input schema for database query tool."""
    query: str = Field(..., description="SQL query to execute")
    database: str = Field(default="analytics.db", description="Database file path")

class DataAnalysisInput(BaseModel):
    """Input schema for data analysis tool."""
    data: list = Field(..., description="Data to analyze")
    operation: str = Field(..., description="Operation: mean, median, std, correlation")

class CustomSearchTool(BaseTool):
    """Custom search tool with advanced capabilities."""
    
    name: str = "advanced_search"
    description: str = "Search multiple sources for comprehensive information"
    args_schema: Type[BaseModel] = SearchInput
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """Execute search across multiple sources."""
        
        results = {
            'web_results': self._search_web(query, max_results),
            'knowledge_base': self._search_knowledge_base(query),
            'recent_news': self._search_news(query)
        }
        
        return json.dumps(results, indent=2)
    
    def _search_web(self, query: str, max_results: int) -> list:
        """Simulate web search."""
        # In production, integrate with actual search API
        return [
            {
                'title': f'Result {i+1} for {query}',
                'url': f'https://example.com/result{i+1}',
                'snippet': f'Relevant information about {query}...'
            }
            for i in range(max_results)
        ]
    
    def _search_knowledge_base(self, query: str) -> list:
        """Search internal knowledge base."""
        # Simulate knowledge base search
        return [
            {
                'topic': query,
                'relevance': 0.95,
                'content': f'Expert knowledge about {query}'
            }
        ]
    
    def _search_news(self, query: str) -> list:
        """Search recent news."""
        # Simulate news search
        return [
            {
                'headline': f'Latest developments in {query}',
                'date': datetime.now().isoformat(),
                'source': 'Tech News Daily'
            }
        ]

class DatabaseTool(BaseTool):
    """Tool for database operations and queries."""
    
    name: str = "database_query"
    description: str = "Execute SQL queries on the analytics database"
    args_schema: Type[BaseModel] = DatabaseQueryInput
    
    def _run(self, query: str, database: str = "analytics.db") -> str:
        """Execute database query safely."""
        
        try:
            # Connect to database
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            
            # Execute query (in production, add SQL injection protection)
            cursor.execute(query)
            
            # Fetch results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                # Convert to DataFrame for better formatting
                df = pd.DataFrame(results, columns=columns)
                return df.to_json(orient='records', indent=2)
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
                
        except Exception as e:
            return f"Database error: {str(e)}"
        finally:
            conn.close()

class DataAnalysisTool(BaseTool):
    """Tool for statistical data analysis."""
    
    name: str = "data_analysis"
    description: str = "Perform statistical analysis on data"
    args_schema: Type[BaseModel] = DataAnalysisInput
    
    def _run(self, data: list, operation: str) -> str:
        """Perform data analysis operation."""
        
        try:
            import numpy as np
            import pandas as pd
            from scipy import stats
            
            # Convert to numpy array
            arr = np.array(data)
            
            results = {}
            
            if operation == "mean":
                results['mean'] = float(np.mean(arr))
            elif operation == "median":
                results['median'] = float(np.median(arr))
            elif operation == "std":
                results['std'] = float(np.std(arr))
            elif operation == "correlation":
                if len(arr.shape) == 2 and arr.shape[1] >= 2:
                    corr_matrix = np.corrcoef(arr.T)
                    results['correlation_matrix'] = corr_matrix.tolist()
                else:
                    results['error'] = "Correlation requires 2D data with at least 2 variables"
            else:
                # Comprehensive analysis
                results = {
                    'mean': float(np.mean(arr)),
                    'median': float(np.median(arr)),
                    'std': float(np.std(arr)),
                    'min': float(np.min(arr)),
                    'max': float(np.max(arr)),
                    'q25': float(np.percentile(arr, 25)),
                    'q75': float(np.percentile(arr, 75))
                }
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return f"Analysis error: {str(e)}"

class CodeGenerationTool(BaseTool):
    """Tool for generating code snippets."""
    
    name: str = "code_generator"
    description: str = "Generate code snippets in various languages"
    
    def _run(self, language: str, task: str) -> str:
        """Generate code based on requirements."""
        
        templates = {
            'python': {
                'api': self._generate_python_api,
                'class': self._generate_python_class,
                'function': self._generate_python_function
            },
            'javascript': {
                'api': self._generate_js_api,
                'react': self._generate_react_component
            }
        }
        
        # Determine task type
        task_type = self._identify_task_type(task)
        
        if language in templates and task_type in templates[language]:
            return templates[language][task_type](task)
        else:
            return self._generate_generic_code(language, task)
    
    def _identify_task_type(self, task: str) -> str:
        """Identify the type of code to generate."""
        task_lower = task.lower()
        
        if 'api' in task_lower or 'endpoint' in task_lower:
            return 'api'
        elif 'class' in task_lower:
            return 'class'
        elif 'function' in task_lower or 'method' in task_lower:
            return 'function'
        elif 'component' in task_lower and 'react' in task_lower:
            return 'react'
        else:
            return 'generic'
    
    def _generate_python_api(self, task: str) -> str:
        """Generate Python API code."""
        return f'''
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/endpoint', methods=['GET', 'POST'])
def api_endpoint():
    """API endpoint for {task}"""
    if request.method == 'GET':
        # Handle GET request
        return jsonify({{"status": "success", "data": []}})
    elif request.method == 'POST':
        # Handle POST request
        data = request.json
        # Process data
        return jsonify({{"status": "created", "id": 123}})

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    def _generate_python_class(self, task: str) -> str:
        """Generate Python class code."""
        return f'''
class GeneratedClass:
    """Class for {task}"""
    
    def __init__(self):
        self.data = []
        
    def process(self, input_data):
        """Process input data"""
        # Implementation here
        self.data.append(input_data)
        return True
        
    def get_results(self):
        """Get processed results"""
        return self.data
'''
    
    def _generate_python_function(self, task: str) -> str:
        """Generate Python function code."""
        return f'''
def generated_function(param1, param2=None):
    """Function for {task}"""
    
    # Validate inputs
    if not param1:
        raise ValueError("param1 is required")
    
    # Process logic
    result = {{
        'input': param1,
        'processed': True,
        'timestamp': datetime.now().isoformat()
    }}
    
    if param2:
        result['additional'] = param2
    
    return result
'''
    
    def _generate_js_api(self, task: str) -> str:
        """Generate JavaScript API code."""
        return f'''
const express = require('express');
const router = express.Router();

// API endpoint for {task}
router.get('/api/endpoint', async (req, res) => {{
    try {{
        // Handle GET request
        const data = await fetchData();
        res.json({{ success: true, data }});
    }} catch (error) {{
        res.status(500).json({{ error: error.message }});
    }}
}});

router.post('/api/endpoint', async (req, res) => {{
    try {{
        // Handle POST request
        const result = await processData(req.body);
        res.status(201).json({{ success: true, result }});
    }} catch (error) {{
        res.status(400).json({{ error: error.message }});
    }}
}});

module.exports = router;
'''
    
    def _generate_react_component(self, task: str) -> str:
        """Generate React component code."""
        return f'''
import React, {{ useState, useEffect }} from 'react';

const GeneratedComponent = () => {{
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {{
        // Fetch data on mount
        fetchData();
    }}, []);
    
    const fetchData = async () => {{
        setLoading(true);
        try {{
            const response = await fetch('/api/endpoint');
            const result = await response.json();
            setData(result.data);
        }} catch (error) {{
            console.error('Error fetching data:', error);
        }} finally {{
            setLoading(false);
        }}
    }};
    
    return (
        <div className="component-container">
            <h2>{task}</h2>
            {{loading ? (
                <p>Loading...</p>
            ) : (
                <ul>
                    {{data.map(item => (
                        <li key={{item.id}}>{{item.name}}</li>
                    ))}}
                </ul>
            )}}
        </div>
    );
}};

export default GeneratedComponent;
'''
    
    def _generate_generic_code(self, language: str, task: str) -> str:
        """Generate generic code template."""
        return f"# Code generation for {language}: {task}\n# Implementation needed"

# Tool factory function
def create_custom_tools():
    """Create and return all custom tools."""
    return [
        CustomSearchTool(),
        DatabaseTool(),
        DataAnalysisTool(),
        CodeGenerationTool()
    ]