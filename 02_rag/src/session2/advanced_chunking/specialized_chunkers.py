# src/advanced_chunking/specialized_chunkers.py
from typing import List, Dict, Any
from langchain.schema import Document
import pandas as pd
from io import StringIO

class TableAwareChunker:
    """Specialized chunker that preserves table structure."""
    
    def __init__(self, max_chunk_size: int = 1500):
        self.max_chunk_size = max_chunk_size
    
    def chunk_with_tables(self, document: Document) -> List[Document]:
        """Chunk document while preserving table integrity."""
        content = document.page_content
        
        # Identify table sections
        table_sections = self._identify_tables(content)
        
        chunks = []
        current_pos = 0
        
        for table_start, table_end in table_sections:
            # Add content before table
            if current_pos < table_start:
                pre_table_content = content[current_pos:table_start].strip()
                if pre_table_content:
                    pre_chunks = self._chunk_text(pre_table_content, document.metadata)
                    chunks.extend(pre_chunks)
            
            # Add table as separate chunk
            table_content = content[table_start:table_end]
            table_chunk = self._create_table_chunk(table_content, document.metadata)
            chunks.append(table_chunk)
            
            current_pos = table_end
        
        # Add remaining content
        if current_pos < len(content):
            remaining_content = content[current_pos:].strip()
            if remaining_content:
                remaining_chunks = self._chunk_text(remaining_content, document.metadata)
                chunks.extend(remaining_chunks)
        
        return chunks

    def _identify_tables(self, content: str) -> List[tuple]:
        """Identify table boundaries in the content."""
        table_sections = []
        lines = content.split('\n')
        table_start = None
        
        for i, line in enumerate(lines):
            if '|' in line and line.count('|') >= 2:
                if table_start is None:
                    table_start = content.find(line)
            elif table_start is not None and '|' not in line:
                table_end = content.find(line, table_start)
                table_sections.append((table_start, table_end))
                table_start = None
        
        # Handle case where table goes to end of content
        if table_start is not None:
            table_sections.append((table_start, len(content)))
        
        return table_sections

    def _chunk_text(self, text: str, metadata: Dict) -> List[Document]:
        """Chunk regular text content."""
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            
            if current_size + word_size > self.max_chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(Document(page_content=chunk_text, metadata=metadata))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(Document(page_content=chunk_text, metadata=metadata))
        
        return chunks

    def _create_table_chunk(self, table_content: str, base_metadata: Dict) -> Document:
        """Create a specialized chunk for table content."""
        # Parse table structure
        table_info = self._analyze_table_structure(table_content)
        
        enhanced_metadata = {
            **base_metadata,
            "content_type": "table",
            "table_rows": table_info["rows"],
            "table_columns": table_info["columns"],
            "table_headers": table_info["headers"],
            "is_structured_data": True
        }
        
        # Enhance table content with description
        enhanced_content = self._enhance_table_content(table_content, table_info)
        
        return Document(page_content=enhanced_content, metadata=enhanced_metadata)
    
    def _analyze_table_structure(self, table_content: str) -> Dict[str, Any]:
        """Analyze table structure and extract metadata."""
        lines = table_content.strip().split('\n')
        table_lines = [line for line in lines if '|' in line]
        
        if not table_lines:
            return {"rows": 0, "columns": 0, "headers": []}
        
        # Extract headers from first row
        headers = []
        if table_lines:
            header_row = table_lines[0]
            headers = [cell.strip() for cell in header_row.split('|') if cell.strip()]
        
        return {
            "rows": len(table_lines),
            "columns": len(headers),
            "headers": headers
        }
    
    def _enhance_table_content(self, table_content: str, table_info: Dict) -> str:
        """Add descriptive text to table content."""
        description = f"Table with {table_info['rows']} rows and {table_info['columns']} columns"
        
        if table_info['headers']:
            headers_text = ", ".join(table_info['headers'])
            description += f" containing data about: {headers_text}"
        
        return f"{description}\n\n{table_content}"