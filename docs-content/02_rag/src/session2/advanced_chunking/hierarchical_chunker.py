# src/advanced_chunking/hierarchical_chunker.py - Setup
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from .document_analyzer import DocumentStructureAnalyzer, DocumentElement, ContentType

class HierarchicalChunker:
    """Creates intelligent chunks based on document hierarchy."""
    
    def __init__(self, 
                 max_chunk_size: int = 1000,
                 min_chunk_size: int = 100,
                 overlap_ratio: float = 0.1):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_ratio = overlap_ratio
        self.analyzer = DocumentStructureAnalyzer()

    def create_hierarchical_chunks(self, document: Document) -> List[Document]:
        """Create chunks that preserve document hierarchy."""
        # Analyze document structure
        elements = self.analyzer.analyze_structure(document)
        
        # Group elements into logical sections
        sections = self._group_elements_by_hierarchy(elements)
        
        # Create chunks from sections
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section, document.metadata)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _group_elements_by_hierarchy(self, elements: List[DocumentElement]) -> List[List[DocumentElement]]:
        """Group elements into hierarchical sections."""
        sections = []
        current_section = []
        current_level = -1
        
        for element in elements:
            # Start new section on same or higher level heading
            if (element.element_type == ContentType.HEADING and 
                element.level <= current_level and current_section):
                sections.append(current_section)
                current_section = [element]
                current_level = element.level
            elif element.element_type == ContentType.HEADING and not current_section:
                current_section = [element]
                current_level = element.level
            else:
                current_section.append(element)
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections

    def _chunk_section(self, section: List[DocumentElement], 
                      base_metadata: Dict) -> List[Document]:
        """Create chunks from a document section."""
        chunks = []
        current_chunk_elements = []
        current_size = 0
        
        section_title = self._extract_section_title(section)

        for element in section:
            element_size = len(element.content)
            
            # If adding this element would exceed chunk size
            if current_size + element_size > self.max_chunk_size and current_chunk_elements:
                # Create chunk from current elements
                chunk = self._create_chunk_from_elements(
                    current_chunk_elements, 
                    base_metadata, 
                    section_title
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_elements = self._get_overlap_elements(current_chunk_elements)
                current_chunk_elements = overlap_elements + [element]
                current_size = sum(len(e.content) for e in current_chunk_elements)
            else:
                current_chunk_elements.append(element)
                current_size += element_size

        # Create final chunk
        if current_chunk_elements:
            chunk = self._create_chunk_from_elements(
                current_chunk_elements, 
                base_metadata, 
                section_title
            )
            chunks.append(chunk)
        
        return chunks

    def _create_chunk_from_elements(self, elements: List[DocumentElement], 
                                  base_metadata: Dict, section_title: str) -> Document:
        """Create a document chunk with rich metadata."""
        # Combine element content
        content_parts = []
        for element in elements:
            if element.element_type == ContentType.HEADING:
                content_parts.append(f"\n{element.content}\n")
            else:
                content_parts.append(element.content)
        
        content = "\n".join(content_parts).strip()
        
        # Extract rich metadata
        content_types = [e.element_type.value for e in elements]
        hierarchy_levels = [e.level for e in elements]
        
        enhanced_metadata = {
            **base_metadata,
            "section_title": section_title,
            "chunk_type": "hierarchical",
            "content_types": list(set(content_types)),
            "hierarchy_levels": hierarchy_levels,
            "element_count": len(elements),
            "has_heading": ContentType.HEADING.value in content_types,
            "has_table": ContentType.TABLE.value in content_types,
            "has_code": ContentType.CODE.value in content_types,
            "min_hierarchy_level": min(hierarchy_levels),
            "max_hierarchy_level": max(hierarchy_levels)
        }
        
        return Document(page_content=content, metadata=enhanced_metadata)
    
    def _extract_section_title(self, section: List[DocumentElement]) -> str:
        """Extract title from section elements."""
        for element in section:
            if element.element_type == ContentType.HEADING:
                return element.content.strip('#').strip()
        return "Untitled Section"
    
    def _get_overlap_elements(self, elements: List[DocumentElement]) -> List[DocumentElement]:
        """Get elements for overlap between chunks."""
        if not elements:
            return []
        
        total_chars = sum(len(e.content) for e in elements)
        overlap_chars = int(total_chars * self.overlap_ratio)
        
        overlap_elements = []
        current_chars = 0
        
        # Take elements from the end for overlap
        for element in reversed(elements):
            overlap_elements.insert(0, element)
            current_chars += len(element.content)
            if current_chars >= overlap_chars:
                break
        
        return overlap_elements