# Session 6: Graph-Based RAG (GraphRAG)

## 🎯📝⚙️ Learning Path Overview

This session offers three distinct learning paths designed to match your goals and time investment:

=== "🎯 Observer (30-45 min)"

    **Focus**: Understanding concepts and architecture
    
    **Activities**: Core GraphRAG principles, NodeRAG architecture, knowledge reasoning concepts
    
    **Ideal for**: Decision makers, architects, overview learners

=== "📝 Participant (2-3 hours)"

    **Focus**: Guided implementation and analysis
    
    **Activities**: Build working GraphRAG systems, traditional and code-based approaches
    
    **Ideal for**: Developers, technical leads, hands-on learners

=== "⚙️ Implementer (6-8 hours)"

    **Focus**: Complete implementation and customization
    
    **Activities**: Advanced graph algorithms, production systems, optimization techniques
    
    **Ideal for**: Senior engineers, architects, specialists

## 🎯 Observer Path: Core GraphRAG Concepts

In Sessions 1-5, you built sophisticated vector-based RAG systems with intelligent chunking, optimized search, query enhancement, and comprehensive evaluation. But when users ask complex questions like "What technologies do companies that partner with Apple use in automotive manufacturing?", you discover vector RAG's fundamental limitation: it finds similar content, but can't reason about relationships between entities.

This session transforms your RAG system from similarity matching to knowledge reasoning. You'll build graph-based architectures that capture entities, relationships, and hierarchical knowledge structures, enabling multi-hop reasoning that connects disparate information through logical pathways. The goal is moving from "find similar documents" to "understand and traverse knowledge relationships."

![RAG Architecture Overview](images/RAG-overview.png)

### The Core GraphRAG Insight

Knowledge isn't just about content similarity – it's about the relationships between concepts, entities, and facts. A question about Apple's automotive partnerships requires understanding:

1. Who Apple partners with  
2. Which of those partners work in automotive  
3. What technologies those automotive partners use  

Vector RAG can find documents about each piece, but can't connect them logically. GraphRAG solves this by representing knowledge as a graph where nodes are entities/concepts and edges are relationships, enabling traversal through logical reasoning pathways.

### NodeRAG: Structured Knowledge Architecture

The challenge with vector RAG is that it treats all content uniformly – a company name gets the same representation type as a concept or relationship. But knowledge has inherent structure: entities have attributes, relationships have directionality, and concepts have hierarchies.

NodeRAG addresses this by creating specialized node types that preserve the semantic structure of different knowledge components. This enables reasoning capabilities that are impossible with flat vector representations.

```
Traditional RAG: Document → Chunks → Uniform Embeddings → Similarity Search
NodeRAG: Document → Specialized Nodes → Heterogeneous Graph → Reasoning Pathways
```

#### NodeRAG's Core Innovation: Six Specialized Node Types

Instead of treating all content uniformly, NodeRAG creates different node types for different knowledge structures:

1. **Semantic Unit Nodes** - Abstract concepts and themes  
   - Example: "Supply Chain Management" connecting related methodologies  

2. **Entity Nodes** - Concrete entities with rich metadata  
   - Example: "Apple Inc." with subsidiaries and partnerships  

3. **Relationship Nodes** - Explicit connections with evidence  
   - Example: "Partnership" linking Apple and Foxconn with details  

4. **Attribute Nodes** - Properties and characteristics  
   - Example: "Revenue: $394.3B" with temporal information  

5. **Document Nodes** - Original source segments  
   - Example: SEC filing containing partnership disclosures  

6. **Summary Nodes** - Cross-document synthesis  
   - Example: "Apple Automotive Strategy" synthesizing multiple sources  

#### Three-Stage Processing Pipeline

NodeRAG transforms documents through three key stages:

1. **Decomposition**: Extract specialized node types from documents  
2. **Augmentation**: Build connections between different node types  
3. **Enrichment**: Add similarity edges and reasoning pathways  

For detailed technical implementation, see: ⚙️ [Session6_NodeRAG_Technical_Implementation.md](Session6_NodeRAG_Technical_Implementation.md)

### Bridge to Session 7: Agentic Reasoning

NodeRAG's heterogeneous graph architecture provides the structured foundation for advanced reasoning capabilities. Session 7 will show how to build agents that actively reason through these graph structures.

## 📝 Participant Path: Practical GraphRAG Implementation

*Prerequisites: Complete Observer Path sections above*

Now that you understand core GraphRAG concepts, let's build working implementations. This path covers traditional GraphRAG, code-based GraphRAG, and hybrid approaches.

### Understanding the GraphRAG Spectrum

Before diving into implementation, it's important to understand the different approaches available:

- **Traditional GraphRAG**: Entity-relationship extraction with standard graph traversal  
- **Code GraphRAG**: Specialized for analyzing software codebases and dependencies  
- **Hybrid GraphRAG**: Combines graph reasoning with vector similarity for comprehensive search  

Each approach serves different use cases and complexity requirements.

### Traditional GraphRAG Implementation - Building the Foundation

Before implementing advanced NodeRAG architectures, it's essential to understand traditional GraphRAG approaches. Traditional GraphRAG establishes the core entity-relationship extraction and graph construction techniques that power all graph-based knowledge systems.

#### Traditional GraphRAG: Foundational Entity-Relationship Extraction

Traditional GraphRAG remains valuable for:

- **Simpler Use Cases**: When specialized node types aren't needed  
- **Resource Constraints**: Lower computational requirements  
- **Rapid Prototyping**: Faster implementation and iteration  
- **Legacy Integration**: Working with existing graph systems  

#### Core Traditional GraphRAG Components

1. **Entity Extraction**: Identify people, organizations, locations, concepts  
2. **Relationship Mapping**: Connect entities through typed relationships  
3. **Graph Construction**: Build searchable knowledge graph  
4. **Query Processing**: Traverse graph for multi-hop reasoning  

#### Basic Entity and Relationship Extraction

```python
import spacy
from typing import List, Dict, Any, Tuple
import networkx as nx

class TraditionalGraphRAG:
    """Traditional GraphRAG implementation"""

    def __init__(self):
        # Load spaCy model for entity extraction
        self.nlp = spacy.load("en_core_web_sm")
        self.graph = nx.Graph()
```

This initialization sets up the basic components needed for traditional GraphRAG implementation using standard NLP libraries.

```python
    def extract_entities_and_relationships(self, text: str):
        """Extract entities and relationships from text"""

        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT"]:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
```

Entity extraction uses named entity recognition to identify key entities that will become nodes in the knowledge graph.

```python
        # Simple relationship extraction using dependency parsing
        relationships = []
        for token in doc:
            if token.dep_ in ["nsubj", "dobj"] and token.head.pos_ == "VERB":
                relationships.append({
                    'subject': token.text,
                    'predicate': token.head.text,
                    'object': [child.text for child in token.head.children
                             if child.dep_ in ["dobj", "attr"]]
                })

        return entities, relationships
```

Relationship extraction uses dependency parsing to identify verb-based connections between entities.

#### Building the Knowledge Graph

```python
    def build_knowledge_graph(self, documents: List[str]):
        """Build knowledge graph from multiple documents"""

        all_entities = []
        all_relationships = []

        for doc in documents:
            entities, relationships = self.extract_entities_and_relationships(doc)
            all_entities.extend(entities)
            all_relationships.extend(relationships)
```

Document processing aggregates entities and relationships across multiple sources to build a comprehensive knowledge graph.

```python
        # Add entities as nodes
        for entity in all_entities:
            if not self.graph.has_node(entity['text']):
                self.graph.add_node(
                    entity['text'],
                    type=entity['label'],
                    entity_type='traditional'
                )

        # Add relationships as edges
        for rel in all_relationships:
            if rel['object']:
                self.graph.add_edge(
                    rel['subject'],
                    rel['object'][0],  # Take first object for simplicity
                    relationship=rel['predicate']
                )
```

Graph construction creates nodes for entities and edges for relationships, forming the queryable knowledge structure.

#### Query Processing and Graph Traversal

```python
    def query_graph(self, query: str, max_hops: int = 3):
        """Query the knowledge graph for relevant information"""

        # Extract entities from query
        query_doc = self.nlp(query)
        query_entities = [ent.text for ent in query_doc.ents]

        # Find paths between query entities
        relevant_paths = []
```

Query processing starts by extracting entities from the user's question using the same NLP pipeline used for document processing.

```python
        for i, entity1 in enumerate(query_entities):
            for entity2 in query_entities[i+1:]:
                if (self.graph.has_node(entity1) and
                    self.graph.has_node(entity2)):
                    try:
                        path = nx.shortest_path(
                            self.graph, entity1, entity2
                        )
                        if len(path) <= max_hops + 1:
                            relevant_paths.append(path)
                    except nx.NetworkXNoPath:
                        continue

        return relevant_paths
```

Path finding uses NetworkX's shortest path algorithm to connect query entities through the knowledge graph, enabling multi-hop reasoning.

Query processing finds paths between entities mentioned in the query, enabling multi-hop reasoning.

### Code GraphRAG Implementation - Understanding Software Knowledge

Code GraphRAG specializes in analyzing software repositories and codebases to enable natural language queries about code structure, dependencies, and functionality.

#### Core Code GraphRAG Components

1. **AST Analysis**: Parse code structure into graph nodes  
2. **Dependency Mapping**: Track imports, calls, and data flow  
3. **Semantic Extraction**: Understand code functionality and purpose  
4. **Query Processing**: Enable natural language queries about code  

For complete technical implementation, see: ⚙️ [Session6_Code_GraphRAG_Advanced.md](Session6_Code_GraphRAG_Advanced.md)

#### Basic AST-based Graph Construction

```python
import ast
from typing import Dict, List, Any

class CodeGraphRAG:
    """Code-specialized GraphRAG implementation"""

    def __init__(self):
        self.code_graph = nx.DiGraph()  # Directed graph for code dependencies
        self.file_asts = {}
```

Code GraphRAG uses directed graphs to properly represent the directional nature of code dependencies and call relationships.

```python
    def analyze_python_file(self, file_path: str, content: str):
        """Analyze Python file and extract code entities"""

        try:
            tree = ast.parse(content)
            self.file_asts[file_path] = tree

            # Extract functions, classes, and imports
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.add_function_node(node, file_path)
                elif isinstance(node, ast.ClassDef):
                    self.add_class_node(node, file_path)
                elif isinstance(node, ast.Import):
                    self.add_import_relationships(node, file_path)

        except SyntaxError:
            print(f"Syntax error in {file_path}")
```

AST analysis extracts structured information about code components and their relationships.

### Hybrid Graph-Vector Search

Hybrid GraphRAG combines the strengths of both graph reasoning and vector similarity search for comprehensive knowledge retrieval.

#### Core Hybrid Architecture

```python
class HybridGraphRAG:
    """Hybrid system combining graph and vector approaches"""

    def __init__(self, graph_store, vector_store):
        self.graph_rag = TraditionalGraphRAG()
        self.vector_rag = VectorRAG(vector_store)
        self.fusion_engine = ResultFusionEngine()
```

The hybrid approach maintains both systems and intelligently combines their results.

For complete technical implementation, see: ⚙️ [Session6_Hybrid_GraphRAG_Advanced.md](Session6_Hybrid_GraphRAG_Advanced.md)

### Advanced Graph Traversal and Multi-Hop Reasoning

Multi-hop reasoning enables complex queries that require connecting information across multiple logical steps.

For complete technical implementation, see: ⚙️ [Session6_Graph_Traversal_Advanced.md](Session6_Graph_Traversal_Advanced.md)

## Hands-On Exercise: Build Production GraphRAG System

Let's build a complete GraphRAG system that combines traditional entity-relationship extraction with modern vector similarity search.

### Exercise Overview

You'll create a hybrid system that:

1. Extracts entities and relationships from documents  
2. Builds a queryable knowledge graph  
3. Integrates vector similarity for semantic search  
4. Provides natural language query interface  

### Implementation Steps

```python
# Complete implementation available in advanced modules
from traditional_graph_rag import TraditionalGraphRAG
from hybrid_graph_vector import HybridGraphRAG

# Initialize hybrid system
hybrid_rag = HybridGraphRAG(
    graph_store="neo4j://localhost:7687",
    vector_store="chroma_db"
)

# Process documents
documents = ["document1.txt", "document2.txt"]
hybrid_rag.process_documents(documents)

# Query the system
result = hybrid_rag.query("What are the partnerships between tech companies?")
print(result)
```

For complete exercise implementation, see the advanced modules linked above.

## Chapter Summary

In this session, you've learned how GraphRAG transforms information retrieval from similarity matching to knowledge reasoning:

### 🎯 Observer Path Key Concepts

- **Core Problem**: Vector RAG can't reason about entity relationships  
- **GraphRAG Solution**: Represent knowledge as graphs with nodes and edges  
- **NodeRAG Innovation**: Six specialized node types for different knowledge structures  
- **Processing Pipeline**: Decomposition → Augmentation → Enrichment  

### 📝 Participant Path Key Skills

- **Traditional GraphRAG**: Entity-relationship extraction and graph construction  
- **Code GraphRAG**: AST analysis and software dependency modeling  
- **Hybrid Approaches**: Combining graph reasoning with vector similarity  
- **Query Processing**: Multi-hop reasoning through graph traversal  

### ⚙️ Implementer Path Advanced Topics

For deep technical mastery, explore these advanced modules:

- ⚙️ [NodeRAG Technical Implementation](Session6_NodeRAG_Technical_Implementation.md) - Advanced algorithms and optimization  
- ⚙️ [Code GraphRAG Advanced](Session6_Code_GraphRAG_Advanced.md) - Software analysis and pattern recognition  
- ⚙️ [Graph Traversal Advanced](Session6_Graph_Traversal_Advanced.md) - Multi-hop reasoning algorithms  
- ⚙️ [Hybrid GraphRAG Advanced](Session6_Hybrid_GraphRAG_Advanced.md) - Fusion algorithms and performance optimization  
- ⚙️ [Module A: Advanced Graph Algorithms](Session6_ModuleA_Advanced_Algorithms.md) - Complex graph algorithms  
- ⚙️ [Module B: Production GraphRAG](Session6_ModuleB_Production_Systems.md) - Enterprise deployment patterns  

### Next Steps

Session 7 will show you how to build agentic RAG systems that actively reason through graph structures, making autonomous decisions about information retrieval and synthesis strategies.

## 📝 Multiple Choice Test - Session 6

Test your understanding of graph-based RAG systems and GraphRAG implementations.

**Question 1:** What is the primary advantage of GraphRAG over traditional vector-based RAG?  
A) Faster query processing  
B) Lower computational requirements  
C) Multi-hop reasoning through explicit relationship modeling  
D) Simpler system architecture  

**Question 2:** In knowledge graph construction, what is the purpose of entity standardization?  
A) To reduce memory usage  
B) To merge different mentions of the same entity (e.g., "Apple Inc." and "Apple")  
C) To improve query speed  
D) To compress graph storage  

**Question 3:** Which graph traversal algorithm is most suitable for finding related entities within a limited number of hops?  
A) Depth-First Search (DFS)  
B) Breadth-First Search (BFS)  
C) Dijkstra's algorithm  
D) A* search  

**Question 4:** In Code GraphRAG, what information is typically extracted from Abstract Syntax Trees (ASTs)?  
A) Only function definitions  
B) Function calls, imports, class hierarchies, and variable dependencies  
C) Only variable names  
D) Just file names and sizes  

**Question 5:** What is the key benefit of hybrid graph-vector search?  
A) Reduced computational cost  
B) Combining structural relationships with semantic similarity  
C) Simpler implementation  
D) Faster indexing  

**Question 6:** When should you choose Neo4j over a simple graph data structure for GraphRAG?  
A) Always, regardless of scale  
B) When you need persistent storage and complex queries at scale  
C) Only for small datasets  
D) Never, simple structures are always better  

**Question 7:** What is the primary challenge in multi-hop graph traversal for RAG?  
A) Memory limitations  
B) Balancing comprehensiveness with relevance and avoiding information explosion  
C) Slow database queries  
D) Complex code implementation  

**Question 8:** In production GraphRAG systems, what is the most important consideration for incremental updates?  
A) Minimizing downtime while maintaining graph consistency  
B) Reducing storage costs  
C) Maximizing query speed  
D) Simplifying the codebase  

[View Solutions →](Session6_Test_Solutions.md)

---

## 🧭 Navigation

**Previous:** [Session 5 - Type-Safe Development →](Session5_*.md)  
**Next:** [Session 7 - Agent Systems →](Session7_*.md)

---
