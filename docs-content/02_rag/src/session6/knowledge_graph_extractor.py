# Traditional GraphRAG Knowledge Graph Extraction
import spacy
from typing import List, Dict, Any, Tuple, Set
import networkx as nx
import json
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time

class KnowledgeGraphExtractor:
    """Traditional GraphRAG implementation with entity-relationship extraction."""
    
    def __init__(self, llm_model, spacy_model: str = "en_core_web_lg"):
        self.llm_model = llm_model
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            print(f"SpaCy model {spacy_model} not found, using en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Entity and relationship storage
        self.entities = {}
        self.relationships = []
        self.knowledge_graph = nx.DiGraph()
        
        # Entity extraction patterns
        self.entity_patterns = {
            'PERSON': ['CEO', 'founder', 'president', 'director', 'manager'],
            'ORG': ['company', 'corporation', 'organization', 'startup'],
            'PRODUCT': ['iPhone', 'software', 'platform', 'application'],
            'TECH': ['AI', 'machine learning', 'blockchain', 'cloud computing']
        }
        
        # Relationship extraction patterns
        self.relation_patterns = {
            'works_for': [r'\b(\w+)\s+works?\s+(?:for|at)\s+(\w+)', r'(\w+)\s+(?:is|was)\s+(?:CEO|founder|president)\s+of\s+(\w+)'],
            'founded': [r'\b(\w+)\s+founded\s+(\w+)', r'(\w+)\s+(?:established|created|started)\s+(\w+)'],
            'partners_with': [r'\b(\w+)\s+partners?\s+with\s+(\w+)', r'(\w+)\s+(?:collaborates?|cooperates?)\s+with\s+(\w+)'],
            'acquires': [r'\b(\w+)\s+(?:acquired|bought|purchased)\s+(\w+)'],
            'invests_in': [r'\b(\w+)\s+(?:invested|invests)\s+in\s+(\w+)'],
            'uses': [r'\b(\w+)\s+uses?\s+(\w+)', r'(\w+)\s+(?:employs?|utilizes?)\s+(\w+)'],
            'located_in': [r'\b(\w+)\s+(?:is\s+)?(?:located|based|situated)\s+in\s+(\w+)']
        }
    
    def extract_knowledge_graph(self, documents: List[str], 
                               extraction_config: Dict = None) -> Dict[str, Any]:
        """Extract knowledge graph from documents using traditional GraphRAG methods."""
        
        config = extraction_config or {
            'merge_similar_entities': True,
            'similarity_threshold': 0.85,
            'min_entity_confidence': 0.6,
            'max_entities_per_doc': 50,
            'extract_relationships': True,
            'use_llm_enhancement': True
        }
        
        print(f"Extracting knowledge graph from {len(documents)} documents...")
        
        # Step 1: Extract entities from all documents
        print("Extracting entities...")
        all_entities = {}
        
        for doc_idx, document in enumerate(documents):
            print(f"Processing document {doc_idx + 1}/{len(documents)}")
            doc_entities = self._extract_entities_from_document(document, doc_idx, config)
            
            # Merge entities into global collection
            for canonical, entity_data in doc_entities.items():
                if canonical in all_entities:
                    # Merge entity information
                    all_entities[canonical] = self._merge_entity_data(
                        all_entities[canonical], entity_data
                    )
                else:
                    all_entities[canonical] = entity_data
        
        print(f"Extracted {len(all_entities)} unique entities")
        
        # Step 2: Merge similar entities if enabled
        if config.get('merge_similar_entities', True):
            print("Merging similar entities...")
            all_entities = self._merge_similar_entities(
                all_entities, config.get('similarity_threshold', 0.85)
            )
            print(f"After merging: {len(all_entities)} entities")
        
        # Step 3: Extract relationships
        relationships = []
        if config.get('extract_relationships', True):
            print("Extracting relationships...")
            for doc_idx, document in enumerate(documents):
                doc_relationships = self._extract_relationships_from_document(
                    document, all_entities, doc_idx, config
                )
                relationships.extend(doc_relationships)
            
            print(f"Extracted {len(relationships)} relationships")
        
        # Step 4: Build NetworkX graph
        print("Building NetworkX graph...")
        graph = self._build_networkx_graph(all_entities, relationships)
        
        # Step 5: Calculate graph metrics
        graph_metrics = self._calculate_graph_metrics(graph)
        
        return {
            'entities': all_entities,
            'relationships': relationships,
            'graph': graph,
            'extraction_metadata': {
                'document_count': len(documents),
                'entity_count': len(all_entities),
                'relationship_count': len(relationships),
                'graph_metrics': graph_metrics,
                'extraction_config': config
            }
        }
    
    def _extract_entities_from_document(self, document: str, doc_idx: int, 
                                      config: Dict) -> Dict[str, Any]:
        """Extract entities from a single document."""
        
        doc_entities = {}
        
        # Use spaCy for basic NER
        doc = self.nlp(document)
        spacy_entities = []
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                entity_data = {
                    'canonical': self._canonicalize_entity(ent.text),
                    'text_variants': [ent.text],
                    'type': ent.label_,
                    'confidence': 0.8,  # Base confidence for spaCy
                    'extraction_method': 'spacy',
                    'context': document[max(0, ent.start_char-100):ent.end_char+100],
                    'document_id': doc_idx,
                    'char_start': ent.start_char,
                    'char_end': ent.end_char
                }
                spacy_entities.append(entity_data)
        
        # Use pattern matching for domain-specific entities
        pattern_entities = self._extract_pattern_entities(document, doc_idx)
        
        # Combine and deduplicate entities
        all_doc_entities = spacy_entities + pattern_entities
        
        for entity_data in all_doc_entities:
            canonical = entity_data['canonical']
            if canonical in doc_entities:
                # Merge with existing entity
                doc_entities[canonical] = self._merge_entity_data(
                    doc_entities[canonical], entity_data
                )
            else:
                doc_entities[canonical] = entity_data
        
        # Apply LLM enhancement if enabled
        if config.get('use_llm_enhancement', True) and len(doc_entities) > 0:
            doc_entities = self._enhance_entities_with_llm(document, doc_entities)
        
        # Filter by confidence threshold
        min_confidence = config.get('min_entity_confidence', 0.6)
        doc_entities = {
            k: v for k, v in doc_entities.items() 
            if v.get('confidence', 0.5) >= min_confidence
        }
        
        # Limit entities per document
        max_entities = config.get('max_entities_per_doc', 50)
        if len(doc_entities) > max_entities:
            # Keep highest confidence entities
            sorted_entities = sorted(
                doc_entities.items(), 
                key=lambda x: x[1].get('confidence', 0.5), 
                reverse=True
            )
            doc_entities = dict(sorted_entities[:max_entities])
        
        return doc_entities
    
    def _canonicalize_entity(self, entity_text: str) -> str:
        """Create canonical form of entity."""
        
        # Basic canonicalization
        canonical = entity_text.strip()
        
        # Remove common prefixes/suffixes
        canonical = re.sub(r'\b(Inc\.?|Corp\.?|Ltd\.?|LLC|Co\.?)\b', '', canonical, flags=re.IGNORECASE)
        canonical = re.sub(r'\b(Mr\.?|Mrs\.?|Dr\.?|Prof\.?)\b', '', canonical, flags=re.IGNORECASE)
        
        # Normalize whitespace
        canonical = re.sub(r'\s+', ' ', canonical).strip()
        
        # Handle special cases
        if canonical.lower() in ['apple inc', 'apple computer']:
            canonical = 'Apple'
        elif canonical.lower() in ['microsoft corp', 'microsoft corporation']:
            canonical = 'Microsoft'
        
        return canonical
    
    def _extract_pattern_entities(self, document: str, doc_idx: int) -> List[Dict]:
        """Extract entities using pattern matching."""
        
        pattern_entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                # Simple pattern matching for demonstration
                if pattern.lower() in document.lower():
                    start_idx = document.lower().find(pattern.lower())
                    entity_data = {
                        'canonical': pattern,
                        'text_variants': [pattern],
                        'type': entity_type,
                        'confidence': 0.7,
                        'extraction_method': 'pattern',
                        'context': document[max(0, start_idx-100):start_idx+len(pattern)+100],
                        'document_id': doc_idx,
                        'char_start': start_idx,
                        'char_end': start_idx + len(pattern)
                    }
                    pattern_entities.append(entity_data)
        
        return pattern_entities
    
    def _enhance_entities_with_llm(self, document: str, entities: Dict) -> Dict:
        """Enhance entity extraction using LLM."""
        
        try:
            # Create prompt for LLM entity enhancement
            entity_list = list(entities.keys())[:10]  # Limit for token constraints
            
            enhancement_prompt = f"""
            Given this document excerpt and the entities found, enhance the entity information.
            
            Document: {document[:1000]}...
            
            Entities found: {entity_list}
            
            For each entity, provide:
            1. Improved type classification
            2. Confidence score (0.0-1.0)
            3. Alternative names/variants
            
            Return JSON format:
            {{
                "entity_name": {{
                    "type": "PERSON|ORG|LOCATION|PRODUCT|CONCEPT",
                    "confidence": 0.95,
                    "variants": ["variant1", "variant2"]
                }}
            }}
            """
            
            response = self.llm_model.predict(enhancement_prompt, temperature=0.1)
            enhanced_data = json.loads(self._extract_json_from_response(response))
            
            # Apply enhancements
            for entity_name, enhancement in enhanced_data.items():
                canonical = self._canonicalize_entity(entity_name)
                if canonical in entities:
                    entities[canonical].update({
                        'type': enhancement.get('type', entities[canonical].get('type')),
                        'confidence': enhancement.get('confidence', entities[canonical].get('confidence')),
                        'text_variants': list(set(
                            entities[canonical].get('text_variants', []) + 
                            enhancement.get('variants', [])
                        ))
                    })
            
        except Exception as e:
            print(f"LLM enhancement error: {e}")
        
        return entities
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response."""
        
        # Look for JSON block
        json_match = re.search(r'```json\n(.*?)```', response, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Look for JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # Return response as-is if no clear JSON found
        return response
    
    def _merge_entity_data(self, entity1: Dict, entity2: Dict) -> Dict:
        """Merge two entity data dictionaries."""
        
        merged = entity1.copy()
        
        # Combine text variants
        variants1 = set(entity1.get('text_variants', []))
        variants2 = set(entity2.get('text_variants', []))
        merged['text_variants'] = list(variants1.union(variants2))
        
        # Use higher confidence
        merged['confidence'] = max(
            entity1.get('confidence', 0.5),
            entity2.get('confidence', 0.5)
        )
        
        # Combine contexts
        context1 = entity1.get('context', '')
        context2 = entity2.get('context', '')
        if context1 and context2 and context1 != context2:
            merged['context'] = f"{context1} ... {context2}"
        
        # Use more specific type if available
        type1 = entity1.get('type', 'UNKNOWN')
        type2 = entity2.get('type', 'UNKNOWN')
        if type2 != 'UNKNOWN' and (type1 == 'UNKNOWN' or len(type2) > len(type1)):
            merged['type'] = type2
        
        return merged
    
    def _merge_similar_entities(self, entities: Dict[str, Any], 
                               similarity_threshold: float = 0.85) -> Dict[str, Any]:
        """Merge semantically similar entities."""
        
        try:
            # Load embedding model for similarity computation
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            entity_names = list(entities.keys())
            if len(entity_names) < 2:
                return entities
            
            # Generate embeddings for entity canonical forms
            entity_embeddings = embedding_model.encode(entity_names)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(entity_embeddings)
            
            # Find similar entity pairs
            merged_entities = {}
            entity_clusters = []
            processed_entities = set()
            
            for i, entity1 in enumerate(entity_names):
                if entity1 in processed_entities:
                    continue
                    
                # Find similar entities
                cluster = [entity1]
                for j, entity2 in enumerate(entity_names):
                    if i != j and entity2 not in processed_entities:
                        if similarity_matrix[i][j] > similarity_threshold:
                            cluster.append(entity2)
                
                # Create merged entity
                if len(cluster) > 1:
                    # Choose canonical form (highest confidence entity)
                    canonical_entity = max(
                        cluster, 
                        key=lambda x: entities[x].get('confidence', 0.5)
                    )
                    
                    # Merge information
                    merged_entity = entities[canonical_entity].copy()
                    merged_entity['text_variants'] = []
                    merged_entity['merged_from'] = cluster
                    
                    for entity_name in cluster:
                        entity_data = entities[entity_name]
                        merged_entity['text_variants'].extend(
                            entity_data.get('text_variants', [entity_name])
                        )
                        processed_entities.add(entity_name)
                    
                    # Remove duplicates in text variants
                    merged_entity['text_variants'] = list(set(merged_entity['text_variants']))
                    merged_entities[canonical_entity] = merged_entity
                    
                else:
                    # Single entity, no merging needed
                    merged_entities[entity1] = entities[entity1]
                    processed_entities.add(entity1)
            
            print(f"Entity merging: {len(entities)} -> {len(merged_entities)} entities")
            return merged_entities
            
        except ImportError:
            print("sentence_transformers not available, skipping entity merging")
            return entities
        except Exception as e:
            print(f"Entity merging error: {e}")
            return entities
    
    def _extract_relationships_from_document(self, document: str, entities: Dict,
                                           doc_idx: int, config: Dict) -> List[Dict]:
        """Extract relationships from document."""
        
        relationships = []
        
        # Pattern-based relationship extraction
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, document, re.IGNORECASE)
                for match in matches:
                    subject = self._canonicalize_entity(match.group(1))
                    object_entity = self._canonicalize_entity(match.group(2))
                    
                    # Check if both entities exist in our entity collection
                    if subject in entities and object_entity in entities:
                        relationship = {
                            'subject': subject,
                            'predicate': relation_type,
                            'object': object_entity,
                            'confidence': 0.8,
                            'extraction_method': 'pattern',
                            'evidence': match.group(0),
                            'document_id': doc_idx,
                            'char_start': match.start(),
                            'char_end': match.end()
                        }
                        relationships.append(relationship)
        
        # LLM-enhanced relationship extraction
        if config.get('use_llm_enhancement', True) and entities:
            llm_relationships = self._extract_relationships_with_llm(
                document, list(entities.keys())[:20], doc_idx  # Limit for performance
            )
            relationships.extend(llm_relationships)
        
        return relationships
    
    def _extract_relationships_with_llm(self, document: str, entity_list: List[str], 
                                      doc_idx: int) -> List[Dict]:
        """Extract relationships using LLM."""
        
        try:
            relationship_prompt = f"""
            Extract relationships between entities in this document.
            
            Document: {document[:1500]}...
            
            Entities: {entity_list}
            
            Find relationships and return JSON format:
            [
                {{
                    "subject": "entity1",
                    "predicate": "works_for|founded|partners_with|uses|located_in|acquires",
                    "object": "entity2",
                    "confidence": 0.95,
                    "evidence": "text span supporting this relationship"
                }}
            ]
            
            Only include relationships with high confidence that are clearly supported by the text.
            """
            
            response = self.llm_model.predict(relationship_prompt, temperature=0.1)
            
            try:
                relationships_data = json.loads(self._extract_json_from_response(response))
                
                llm_relationships = []
                for rel_data in relationships_data:
                    if all(key in rel_data for key in ['subject', 'predicate', 'object']):
                        relationship = {
                            'subject': self._canonicalize_entity(rel_data['subject']),
                            'predicate': rel_data['predicate'],
                            'object': self._canonicalize_entity(rel_data['object']),
                            'confidence': rel_data.get('confidence', 0.7),
                            'extraction_method': 'llm',
                            'evidence': rel_data.get('evidence', ''),
                            'document_id': doc_idx
                        }
                        llm_relationships.append(relationship)
                
                return llm_relationships
                
            except json.JSONDecodeError:
                print("Failed to parse LLM relationship response")
                return []
                
        except Exception as e:
            print(f"LLM relationship extraction error: {e}")
            return []
    
    def _build_networkx_graph(self, entities: Dict, relationships: List[Dict]) -> nx.DiGraph:
        """Build NetworkX graph from entities and relationships."""
        
        graph = nx.DiGraph()
        
        # Add entity nodes
        for canonical, entity_data in entities.items():
            graph.add_node(canonical, **{
                'type': entity_data.get('type', 'UNKNOWN'),
                'confidence': entity_data.get('confidence', 0.5),
                'text_variants': entity_data.get('text_variants', []),
                'extraction_method': entity_data.get('extraction_method', 'unknown')
            })
        
        # Add relationship edges
        for rel in relationships:
            subject = rel['subject']
            object_entity = rel['object']
            
            if subject in graph.nodes and object_entity in graph.nodes:
                graph.add_edge(subject, object_entity, **{
                    'relation': rel['predicate'],
                    'confidence': rel.get('confidence', 0.5),
                    'evidence': rel.get('evidence', ''),
                    'extraction_method': rel.get('extraction_method', 'unknown')
                })
        
        return graph
    
    def _calculate_graph_metrics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Calculate comprehensive graph metrics."""
        
        if graph.number_of_nodes() == 0:
            return {'empty_graph': True}
        
        metrics = {
            'node_count': graph.number_of_nodes(),
            'edge_count': graph.number_of_edges(),
            'density': nx.density(graph),
            'is_connected': nx.is_weakly_connected(graph)
        }
        
        # Calculate centrality measures
        try:
            metrics['degree_centrality'] = nx.degree_centrality(graph)
            metrics['betweenness_centrality'] = nx.betweenness_centrality(graph)
            metrics['pagerank'] = nx.pagerank(graph)
            
            # Find most central entities
            metrics['top_degree_entities'] = sorted(
                metrics['degree_centrality'].items(),
                key=lambda x: x[1], reverse=True
            )[:5]
            
            metrics['top_pagerank_entities'] = sorted(
                metrics['pagerank'].items(),
                key=lambda x: x[1], reverse=True
            )[:5]
            
        except Exception as e:
            print(f"Error calculating centrality metrics: {e}")
        
        return metrics