# src/advanced_chunking/multimodal_processor.py
from typing import List, Dict, Any, Optional, Union
from langchain.schema import Document
import base64
from PIL import Image
from io import BytesIO
import pandas as pd
import re
import json

class MultiModalProcessor:
    """Process documents with mixed content types."""
    
    def __init__(self):
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        self.supported_table_formats = ['.csv', '.xlsx', '.xls']
    
    def process_document_with_images(self, document: Document, 
                                   image_descriptions: Dict[str, str] = None) -> Document:
        """Process document that may contain image references."""
        content = document.page_content
        
        # Find image references
        image_refs = self._find_image_references(content)
        
        # Replace image references with descriptions
        enhanced_content = content
        for img_ref in image_refs:
            description = self._get_image_description(img_ref, image_descriptions)
            enhanced_content = enhanced_content.replace(
                img_ref, 
                f"[IMAGE: {description}]"
            )
        
        enhanced_metadata = {
            **document.metadata,
            "has_images": len(image_refs) > 0,
            "image_count": len(image_refs),
            "image_references": image_refs
        }
        
        return Document(page_content=enhanced_content, metadata=enhanced_metadata)

    def _find_image_references(self, content: str) -> List[str]:
        """Find image references in the content."""
        image_refs = []
        
        # Markdown image syntax
        markdown_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
        image_refs.extend(markdown_images)
        
        # HTML img tags
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', content)
        image_refs.extend(html_images)
        
        # Direct file references
        for ext in self.supported_image_formats:
            pattern = rf'\b\S+{re.escape(ext)}\b'
            matches = re.findall(pattern, content, re.IGNORECASE)
            image_refs.extend(matches)
        
        return list(set(image_refs))

    def _get_image_description(self, image_ref: str, image_descriptions: Dict[str, str] = None) -> str:
        """Get description for an image reference."""
        if image_descriptions and image_ref in image_descriptions:
            return image_descriptions[image_ref]
        
        # Generate basic description from filename
        filename = image_ref.split('/')[-1].split('.')[0]
        return f"Image: {filename}"

    def process_structured_data(self, data_content: str, data_type: str) -> Document:
        """Process structured data (CSV, JSON, etc.)."""
        if data_type.lower() in ['csv']:
            return self._process_csv_data(data_content)
        elif data_type.lower() in ['json']:
            return self._process_json_data(data_content)
        else:
            # Fallback to text processing
            return Document(page_content=data_content)
    
    def _process_csv_data(self, csv_content: str) -> Document:
        """Process CSV data into readable format."""
        try:
            # Parse CSV
            from io import StringIO
            df = pd.read_csv(StringIO(csv_content))
            
            # Create descriptive text
            description_parts = []
            description_parts.append(f"Dataset with {len(df)} rows and {len(df.columns)} columns")
            description_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Add sample data
            if len(df) > 0:
                description_parts.append("Sample data:")
                description_parts.append(df.head(3).to_string(index=False))
            
            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                description_parts.append("Numeric column summaries:")
                for col in numeric_cols[:3]:  # Limit to first 3
                    stats = df[col].describe()
                    description_parts.append(f"{col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
            
            processed_content = "\n\n".join(description_parts)
            
            metadata = {
                "content_type": "structured_data",
                "data_format": "csv",
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "numeric_columns": numeric_cols.tolist()
            }
            
            return Document(page_content=processed_content, metadata=metadata)
            
        except Exception as e:
            print(f"Error processing CSV data: {e}")
            return Document(
                page_content=csv_content,
                metadata={"content_type": "raw_csv", "processing_error": str(e)}
            )

    def _process_json_data(self, json_content: str) -> Document:
        """Process JSON data into readable format."""
        try:
            data = json.loads(json_content)
            
            # Create descriptive text
            description_parts = []
            description_parts.append(f"JSON data structure")
            
            if isinstance(data, dict):
                description_parts.append(f"Object with {len(data)} keys: {', '.join(list(data.keys())[:10])}")
                
                # Add sample values for each key
                for key, value in list(data.items())[:5]:
                    if isinstance(value, (str, int, float, bool)):
                        description_parts.append(f"{key}: {value}")
                    elif isinstance(value, list):
                        description_parts.append(f"{key}: List with {len(value)} items")
                    elif isinstance(value, dict):
                        description_parts.append(f"{key}: Object with {len(value)} properties")
                        
            elif isinstance(data, list):
                description_parts.append(f"Array with {len(data)} items")
                if len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        description_parts.append(f"Each item has keys: {', '.join(list(first_item.keys())[:5])}")
            
            processed_content = "\n\n".join(description_parts)
            
            metadata = {
                "content_type": "structured_data",
                "data_format": "json",
                "data_type": type(data).__name__,
                "size": len(str(data))
            }
            
            if isinstance(data, dict):
                metadata["keys"] = list(data.keys())[:10]
            elif isinstance(data, list):
                metadata["array_length"] = len(data)
            
            return Document(page_content=processed_content, metadata=metadata)
            
        except Exception as e:
            print(f"Error processing JSON data: {e}")
            return Document(
                page_content=json_content,
                metadata={"content_type": "raw_json", "processing_error": str(e)}
            )