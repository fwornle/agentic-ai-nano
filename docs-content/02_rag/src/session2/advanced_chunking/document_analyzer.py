# src/advanced_chunking/document_analyzer.py - Core definitions
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from langchain.schema import Document
import re
from enum import Enum

class ContentType(Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    CODE = "code"
    QUOTE = "quote"
    UNKNOWN = "unknown"

@dataclass
class DocumentElement:
    """Represents a structured document element."""
    content: str
    element_type: ContentType
    level: int  # Hierarchy level (0=top, 1=section, 2=subsection, etc.)
    metadata: Dict[str, Any]
    position: int  # Position in document

class DocumentStructureAnalyzer:
    """Analyzes document structure and content types."""
    
    def __init__(self):
        self.heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headers
            r'^([A-Z][^a-z]*)\s*$',  # ALL CAPS headers
            r'^\d+\.\s+(.+)$',  # Numbered headers
            r'^[A-Z][^.!?]*:$',  # Title followed by colon
        ]

    def detect_content_type(self, text: str) -> ContentType:
        """Detect the type of content based on patterns."""
        text = text.strip()
        
        if not text:
            return ContentType.UNKNOWN
        
        # Check for headings
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.MULTILINE):
                return ContentType.HEADING
        
        # Check for lists
        if re.match(r'^\s*[-*+•]\s+', text) or re.match(r'^\s*\d+\.\s+', text):
            return ContentType.LIST
        
        # Check for code blocks
        if text.startswith('```') or text.startswith('    ') or text.startswith('\t'):
            return ContentType.CODE
        
        # Check for quotes
        if text.startswith('>') or text.startswith('"'):
            return ContentType.QUOTE
        
        # Check for tables (simple detection)
        if '|' in text and text.count('|') >= 2:
            return ContentType.TABLE
        
        return ContentType.PARAGRAPH

    def analyze_structure(self, document: Document) -> List[DocumentElement]:
        """Analyze document structure and create structured elements."""
        content = document.page_content
        lines = content.split('\n')
        
        elements = []
        current_level = 0
        position = 0

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            content_type = self.detect_content_type(line)
            
            # Determine hierarchy level
            level = self._determine_level(line, current_level, content_type)
            
            # Group related lines for complex content types
            element_content, lines_consumed = self._group_content_lines(
                lines, i, content_type
            )

            # Create document element
            element = DocumentElement(
                content=element_content,
                element_type=content_type,
                level=level,
                metadata={
                    "original_position": position,
                    "line_number": i + 1,
                    "parent_document": document.metadata.get("source", ""),
                    "char_count": len(element_content),
                    "word_count": len(element_content.split())
                },
                position=position
            )
            
            elements.append(element)
            
            i += lines_consumed
            position += 1
            current_level = level
        
        return elements

    def _determine_level(self, line: str, current_level: int, content_type: ContentType) -> int:
        """Determine hierarchy level of content."""
        if content_type == ContentType.HEADING:
            # Count markdown header level
            if line.startswith('#'):
                return line.count('#') - 1
            # Or determine based on formatting
            elif line.isupper():
                return 0  # Top level
            elif line.endswith(':'):
                return current_level + 1
        
        return current_level + 1

    def _group_content_lines(self, lines: List[str], start_idx: int, 
                           content_type: ContentType) -> Tuple[str, int]:
        """Group related lines for complex content types."""
        if content_type == ContentType.TABLE:
            return self._group_table_lines(lines, start_idx)
        elif content_type == ContentType.CODE:
            return self._group_code_lines(lines, start_idx)
        elif content_type == ContentType.LIST:
            return self._group_list_lines(lines, start_idx)
        else:
            return lines[start_idx], 1

    def _group_table_lines(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """Group table lines together."""
        table_lines = []
        i = start_idx
        
        while i < len(lines) and '|' in lines[i]:
            table_lines.append(lines[i])
            i += 1
        
        return '\n'.join(table_lines), i - start_idx

    def _group_code_lines(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """Group code block lines together."""
        code_lines = []
        i = start_idx
        
        # Handle markdown code blocks
        if lines[i].startswith('```'):
            code_lines.append(lines[i])
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                code_lines.append(lines[i])
                i += 1
        else:
            # Handle indented code blocks
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t') or lines[i].strip() == ''):
                code_lines.append(lines[i])
                i += 1
        
        return '\n'.join(code_lines), i - start_idx

    def _group_list_lines(self, lines: List[str], start_idx: int) -> Tuple[str, int]:
        """Group list item lines together."""
        list_lines = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i].strip()
            # Check if it's a list item or continuation
            if (re.match(r'^\s*[-*+•]\s+', lines[i]) or 
                re.match(r'^\s*\d+\.\s+', lines[i]) or
                (list_lines and line and not re.match(r'^\s*[-*+•]\s+', lines[i]) and not re.match(r'^\s*\d+\.\s+', lines[i]))):
                list_lines.append(lines[i])
                i += 1
            else:
                break
        
        return '\n'.join(list_lines), i - start_idx