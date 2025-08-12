# Code GraphRAG using AST parsing
import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import networkx as nx
import time

class CodeGraphRAG:
    """GraphRAG system specialized for software repositories."""
    
    def __init__(self, supported_languages: List[str] = ['python', 'javascript']):
        self.supported_languages = supported_languages
        
        # Code entity types
        self.code_entity_types = {
            'function', 'class', 'method', 'variable', 'module', 
            'interface', 'enum', 'constant', 'type', 'namespace'
        }
        
        # Code relationship types
        self.code_relation_types = {
            'calls', 'inherits', 'implements', 'imports', 'uses',
            'defines', 'contains', 'overrides', 'instantiates'
        }
        
        # Code knowledge graph
        self.code_entities = {}
        self.code_relationships = []
        self.call_graph = nx.DiGraph()
        self.dependency_graph = nx.DiGraph()
    
    def analyze_repository(self, repo_path: str, 
                          analysis_config: Dict = None) -> Dict[str, Any]:
        """Analyze entire repository and build code knowledge graph."""
        
        config = analysis_config or {
            'max_files': 1000,
            'include_patterns': ['*.py', '*.js', '*.ts'],
            'exclude_patterns': ['*test*', '*__pycache__*', '*.min.js'],
            'extract_docstrings': True,
            'analyze_dependencies': True,
            'build_call_graph': True
        }
        
        print(f"Analyzing repository: {repo_path}")
        
        # Discover source files
        source_files = self._discover_source_files(repo_path, config)
        print(f"Found {len(source_files)} source files")
        
        # Analyze each file
        all_entities = {}
        all_relationships = []
        
        for file_path in source_files[:config.get('max_files', 1000)]:
            try:
                file_analysis = self._analyze_source_file(file_path, config)
                
                if file_analysis:
                    all_entities.update(file_analysis['entities'])
                    all_relationships.extend(file_analysis['relationships'])
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue
        
        # Build specialized graphs
        if config.get('build_call_graph', True):
            self.call_graph = self._build_call_graph(all_entities, all_relationships)
        
        if config.get('analyze_dependencies', True):
            self.dependency_graph = self._build_dependency_graph(all_entities, all_relationships)
        
        return {
            'entities': all_entities,
            'relationships': all_relationships,
            'call_graph': self.call_graph,
            'dependency_graph': self.dependency_graph,
            'analysis_stats': {
                'files_analyzed': len(source_files),
                'entities_extracted': len(all_entities),
                'relationships_extracted': len(all_relationships),
                'supported_languages': self.supported_languages
            }
        }
    
    def _discover_source_files(self, repo_path: str, config: Dict) -> List[str]:
        """Discover source files in repository."""
        
        include_patterns = config.get('include_patterns', ['*.py'])
        exclude_patterns = config.get('exclude_patterns', ['*test*', '*__pycache__*'])
        
        source_files = []
        
        for pattern in include_patterns:
            # Simple glob pattern matching
            if pattern == '*.py':
                for root, dirs, files in os.walk(repo_path):
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if not any(
                        exc_pattern.replace('*', '') in d for exc_pattern in exclude_patterns
                    )]
                    
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            # Check if file should be excluded
                            if not any(exc_pattern.replace('*', '') in file_path for exc_pattern in exclude_patterns):
                                source_files.append(file_path)
        
        return source_files
    
    def _analyze_source_file(self, file_path: str, config: Dict) -> Dict[str, Any]:
        """Analyze a single source file."""
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.py':
            return self._analyze_python_file(file_path, config)
        else:
            print(f"Unsupported file type: {file_ext}")
            return None
    
    def _analyze_python_file(self, file_path: str, config: Dict) -> Dict[str, Any]:
        """Analyze Python file using AST parsing."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST
            tree = ast.parse(source_code, filename=file_path)
            
            entities = {}
            relationships = []
            
            # Extract entities and relationships
            for node in ast.walk(tree):
                # Function definitions
                if isinstance(node, ast.FunctionDef):
                    func_entity = self._extract_function_entity(node, file_path, source_code)
                    entities[func_entity['canonical']] = func_entity
                    
                    # Extract function relationships (calls, uses)
                    func_relationships = self._extract_function_relationships(
                        node, func_entity['canonical'], source_code
                    )
                    relationships.extend(func_relationships)
                
                # Class definitions
                elif isinstance(node, ast.ClassDef):
                    class_entity = self._extract_class_entity(node, file_path, source_code)
                    entities[class_entity['canonical']] = class_entity
                    
                    # Extract class relationships (inheritance, methods)
                    class_relationships = self._extract_class_relationships(
                        node, class_entity['canonical'], source_code
                    )
                    relationships.extend(class_relationships)
                
                # Import statements
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_relationships = self._extract_import_relationships(
                        node, file_path
                    )
                    relationships.extend(import_relationships)
            
            return {
                'entities': entities,
                'relationships': relationships,
                'file_metadata': {
                    'path': file_path,
                    'language': 'python',
                    'lines_of_code': len(source_code.splitlines()),
                    'ast_nodes': len(list(ast.walk(tree)))
                }
            }
            
        except Exception as e:
            print(f"Python AST analysis error for {file_path}: {e}")
            return None
    
    def _extract_function_entity(self, node: ast.FunctionDef, 
                               file_path: str, source_code: str) -> Dict[str, Any]:
        """Extract function entity with comprehensive metadata."""
        
        # Get function signature
        signature = self._get_function_signature(node)
        
        # Extract docstring
        docstring = ast.get_docstring(node) or ""
        
        # Get source code for function
        function_source = self._get_node_source(node, source_code)
        
        # Analyze parameters and return type
        params = [arg.arg for arg in node.args.args]
        returns = self._extract_return_type(node)
        
        canonical_name = f"{file_path}::{node.name}"
        
        return {
            'canonical': canonical_name,
            'type': 'FUNCTION',
            'name': node.name,
            'signature': signature,
            'parameters': params,
            'returns': returns,
            'docstring': docstring,
            'source_code': function_source,
            'file_path': file_path,
            'line_start': node.lineno,
            'line_end': getattr(node, 'end_lineno', node.lineno),
            'complexity': self._calculate_complexity(node),
            'calls': self._extract_function_calls(node),
            'confidence': 0.95  # High confidence for AST extraction
        }
    
    def _extract_class_entity(self, node: ast.ClassDef, 
                             file_path: str, source_code: str) -> Dict[str, Any]:
        """Extract class entity with comprehensive metadata."""
        
        # Extract docstring
        docstring = ast.get_docstring(node) or ""
        
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        canonical_name = f"{file_path}::{node.name}"
        
        return {
            'canonical': canonical_name,
            'type': 'CLASS',
            'name': node.name,
            'base_classes': base_classes,
            'methods': methods,
            'docstring': docstring,
            'file_path': file_path,
            'line_start': node.lineno,
            'line_end': getattr(node, 'end_lineno', node.lineno),
            'confidence': 0.95
        }
    
    def _extract_function_relationships(self, node: ast.FunctionDef, 
                                      function_canonical: str, source_code: str) -> List[Dict]:
        """Extract relationships from function definition."""
        
        relationships = []
        
        # Extract function calls
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Name):
                    called_function = item.func.id
                    relationships.append({
                        'subject': function_canonical,
                        'predicate': 'calls',
                        'object': called_function,
                        'confidence': 0.9,
                        'evidence': f"Function call: {called_function}()",
                        'line_number': item.lineno
                    })
                elif isinstance(item.func, ast.Attribute):
                    if isinstance(item.func.value, ast.Name):
                        called_method = f"{item.func.value.id}.{item.func.attr}"
                        relationships.append({
                            'subject': function_canonical,
                            'predicate': 'calls',
                            'object': called_method,
                            'confidence': 0.9,
                            'evidence': f"Method call: {called_method}()",
                            'line_number': item.lineno
                        })
        
        return relationships
    
    def _extract_class_relationships(self, node: ast.ClassDef, 
                                   class_canonical: str, source_code: str) -> List[Dict]:
        """Extract relationships from class definition."""
        
        relationships = []
        
        # Extract inheritance relationships
        for base in node.bases:
            base_name = ""
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = f"{base.value.id}.{base.attr}"
            
            if base_name:
                relationships.append({
                    'subject': class_canonical,
                    'predicate': 'inherits',
                    'object': base_name,
                    'confidence': 0.95,
                    'evidence': f"Class inheritance: class {node.name}({base_name})",
                    'line_number': node.lineno
                })
        
        # Extract method containment relationships
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_canonical = f"{class_canonical}::{item.name}"
                relationships.append({
                    'subject': class_canonical,
                    'predicate': 'contains',
                    'object': method_canonical,
                    'confidence': 0.95,
                    'evidence': f"Method definition: def {item.name}()",
                    'line_number': item.lineno
                })
        
        return relationships
    
    def _extract_import_relationships(self, node, file_path: str) -> List[Dict]:
        """Extract import relationships."""
        
        relationships = []
        file_canonical = f"module::{file_path}"
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                relationships.append({
                    'subject': file_canonical,
                    'predicate': 'imports',
                    'object': f"module::{module_name}",
                    'confidence': 0.95,
                    'evidence': f"import {module_name}",
                    'line_number': node.lineno
                })
        
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            for alias in node.names:
                import_name = alias.name
                relationships.append({
                    'subject': file_canonical,
                    'predicate': 'imports',
                    'object': f"module::{module_name}.{import_name}",
                    'confidence': 0.95,
                    'evidence': f"from {module_name} import {import_name}",
                    'line_number': node.lineno
                })
        
        return relationships
    
    def _build_call_graph(self, entities: Dict[str, Any], 
                         relationships: List[Dict]) -> nx.DiGraph:
        """Build call graph from extracted entities and relationships."""
        
        call_graph = nx.DiGraph()
        
        # Add function nodes
        for entity_id, entity in entities.items():
            if entity['type'] == 'FUNCTION':
                call_graph.add_node(entity_id, **{
                    'name': entity['name'],
                    'file_path': entity['file_path'],
                    'complexity': entity.get('complexity', 1),
                    'parameters': entity.get('parameters', []),
                    'docstring': entity.get('docstring', '')[:200]  # Truncate for storage
                })
        
        # Add call edges
        for relationship in relationships:
            if relationship['predicate'] == 'calls':
                caller = relationship['subject']
                callee = relationship['object']
                
                if caller in call_graph.nodes and callee in call_graph.nodes:
                    call_graph.add_edge(caller, callee, **{
                        'confidence': relationship.get('confidence', 0.8),
                        'call_count': relationship.get('call_count', 1),
                        'evidence': relationship.get('evidence', '')
                    })
        
        # Calculate graph metrics
        self._calculate_call_graph_metrics(call_graph)
        
        return call_graph
    
    def _build_dependency_graph(self, entities: Dict[str, Any], 
                               relationships: List[Dict]) -> nx.DiGraph:
        """Build dependency graph from extracted entities and relationships."""
        
        dependency_graph = nx.DiGraph()
        
        # Add module nodes
        modules = set()
        for relationship in relationships:
            if relationship['predicate'] == 'imports':
                modules.add(relationship['subject'])
                modules.add(relationship['object'])
        
        for module in modules:
            dependency_graph.add_node(module)
        
        # Add import edges
        for relationship in relationships:
            if relationship['predicate'] == 'imports':
                dependency_graph.add_edge(
                    relationship['subject'],
                    relationship['object'],
                    confidence=relationship.get('confidence', 0.9)
                )
        
        return dependency_graph
    
    def _calculate_call_graph_metrics(self, call_graph: nx.DiGraph):
        """Calculate and store call graph metrics."""
        
        # Basic graph metrics
        num_nodes = call_graph.number_of_nodes()
        num_edges = call_graph.number_of_edges()
        
        if num_nodes > 0:
            # Centrality measures
            in_degree_centrality = nx.in_degree_centrality(call_graph)
            out_degree_centrality = nx.out_degree_centrality(call_graph)
            betweenness_centrality = nx.betweenness_centrality(call_graph)
            
            # Add centrality as node attributes
            for node in call_graph.nodes():
                call_graph.nodes[node].update({
                    'in_degree_centrality': in_degree_centrality.get(node, 0),
                    'out_degree_centrality': out_degree_centrality.get(node, 0),
                    'betweenness_centrality': betweenness_centrality.get(node, 0)
                })
            
            # Identify key functions (high centrality)
            key_functions = sorted(
                call_graph.nodes(),
                key=lambda x: (call_graph.nodes[x]['in_degree_centrality'] + 
                              call_graph.nodes[x]['betweenness_centrality']),
                reverse=True
            )[:10]
            
            # Store graph-level metadata
            call_graph.graph.update({
                'num_functions': num_nodes,
                'num_calls': num_edges,
                'key_functions': key_functions,
                'analysis_timestamp': time.time()
            })
    
    # Helper methods with basic implementations
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get function signature as string."""
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({', '.join(args)})"
    
    def _get_node_source(self, node, source_code: str) -> str:
        """Extract source code for AST node."""
        lines = source_code.splitlines()
        start_line = node.lineno - 1
        end_line = getattr(node, 'end_lineno', node.lineno) - 1
        
        if 0 <= start_line < len(lines) and 0 <= end_line < len(lines):
            return '\n'.join(lines[start_line:end_line + 1])
        return ""
    
    def _extract_return_type(self, node: ast.FunctionDef) -> str:
        """Extract return type annotation if available."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return ""
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity approximation."""
        complexity = 1  # Base complexity
        
        for item in ast.walk(node):
            if isinstance(item, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(item, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract list of functions called within this function."""
        calls = []
        
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                if isinstance(item.func, ast.Name):
                    calls.append(item.func.id)
                elif isinstance(item.func, ast.Attribute):
                    if isinstance(item.func.value, ast.Name):
                        calls.append(f"{item.func.value.id}.{item.func.attr}")
        
        return calls