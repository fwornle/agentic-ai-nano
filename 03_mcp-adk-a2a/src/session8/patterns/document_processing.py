"""
Document Processing Workflow - Session 8
Advanced document processing workflow using parallel and conditional patterns.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import base64
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Types of documents that can be processed."""
    PDF = "pdf"
    WORD = "word"
    TEXT = "text"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    file_name: str
    file_size: int
    file_type: DocumentType
    content_hash: str
    upload_timestamp: datetime
    source: str = ""
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of document processing."""
    document_id: str
    status: ProcessingStatus
    processed_content: Dict[str, Any] = field(default_factory=dict)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)


@dataclass
class DocumentBatch:
    """Batch of documents for processing."""
    batch_id: str
    documents: List[Dict[str, Any]]
    batch_type: str = "standard"
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    processing_options: Dict[str, Any] = field(default_factory=dict)


class DocumentClassifier:
    """Classifies documents by type and content."""
    
    def __init__(self):
        self.type_mappings = {
            '.pdf': DocumentType.PDF,
            '.doc': DocumentType.WORD,
            '.docx': DocumentType.WORD,
            '.txt': DocumentType.TEXT,
            '.md': DocumentType.TEXT,
            '.jpg': DocumentType.IMAGE,
            '.jpeg': DocumentType.IMAGE,
            '.png': DocumentType.IMAGE,
            '.gif': DocumentType.IMAGE,
            '.xls': DocumentType.SPREADSHEET,
            '.xlsx': DocumentType.SPREADSHEET,
            '.csv': DocumentType.SPREADSHEET
        }
    
    async def classify_document(self, document_data: Dict[str, Any]) -> DocumentType:
        """Classify document type based on file extension and content."""
        file_name = document_data.get('file_name', '').lower()
        
        # Check file extension
        for ext, doc_type in self.type_mappings.items():
            if file_name.endswith(ext):
                return doc_type
        
        # Content-based classification (simplified)
        content = document_data.get('content', '')
        if content:
            if content.startswith('%PDF'):
                return DocumentType.PDF
            elif '<html' in content.lower():
                return DocumentType.TEXT
            elif content.startswith('PK'):  # ZIP-based formats (docx, xlsx)
                if 'word' in file_name:
                    return DocumentType.WORD
                elif any(x in file_name for x in ['excel', 'sheet']):
                    return DocumentType.SPREADSHEET
        
        return DocumentType.UNKNOWN
    
    async def extract_metadata(self, document_data: Dict[str, Any]) -> DocumentMetadata:
        """Extract metadata from document."""
        file_name = document_data.get('file_name', 'unknown')
        content = document_data.get('content', '')
        
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode() if isinstance(content, str) else content).hexdigest()
        
        # Determine file size
        file_size = len(content) if content else document_data.get('file_size', 0)
        
        # Classify document
        doc_type = await self.classify_document(document_data)
        
        return DocumentMetadata(
            file_name=file_name,
            file_size=file_size,
            file_type=doc_type,
            content_hash=content_hash,
            upload_timestamp=datetime.now(),
            source=document_data.get('source', 'upload'),
            tags=document_data.get('tags', []),
            custom_fields=document_data.get('metadata', {})
        )


class ContentExtractor:
    """Extracts content and data from different document types."""
    
    def __init__(self):
        self.extractors = {
            DocumentType.PDF: self._extract_pdf_content,
            DocumentType.WORD: self._extract_word_content,
            DocumentType.TEXT: self._extract_text_content,
            DocumentType.IMAGE: self._extract_image_content,
            DocumentType.SPREADSHEET: self._extract_spreadsheet_content
        }
    
    async def extract_content(self, document_data: Dict[str, Any], 
                             metadata: DocumentMetadata) -> Dict[str, Any]:
        """Extract content based on document type."""
        extractor = self.extractors.get(metadata.file_type, self._extract_generic_content)
        
        try:
            result = await extractor(document_data, metadata)
            return result
        except Exception as e:
            logger.error(f"Content extraction failed for {metadata.file_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "structured_data": {}
            }
    
    async def _extract_pdf_content(self, document_data: Dict[str, Any], 
                                  metadata: DocumentMetadata) -> Dict[str, Any]:
        """Extract content from PDF documents."""
        await asyncio.sleep(0.2)  # Simulate PDF processing time
        
        # Mock PDF extraction
        return {
            "success": True,
            "extracted_text": f"Extracted text from PDF: {metadata.file_name}",
            "page_count": 5,
            "structured_data": {
                "title": f"Document: {metadata.file_name}",
                "author": "Unknown",
                "creation_date": metadata.upload_timestamp.isoformat(),
                "pages": [
                    {"page": 1, "text": "First page content..."},
                    {"page": 2, "text": "Second page content..."}
                ]
            },
            "metadata": {
                "pdf_version": "1.4",
                "encrypted": False,
                "form_fields": []
            }
        }
    
    async def _extract_word_content(self, document_data: Dict[str, Any],
                                   metadata: DocumentMetadata) -> Dict[str, Any]:
        """Extract content from Word documents."""
        await asyncio.sleep(0.15)  # Simulate processing
        
        return {
            "success": True,
            "extracted_text": f"Extracted text from Word document: {metadata.file_name}",
            "structured_data": {
                "title": f"Document: {metadata.file_name}",
                "paragraphs": [
                    "Introduction paragraph...",
                    "Body paragraph 1...",
                    "Body paragraph 2...",
                    "Conclusion paragraph..."
                ],
                "headings": ["Introduction", "Main Content", "Conclusion"],
                "styles_used": ["Normal", "Heading 1", "Heading 2"]
            },
            "metadata": {
                "word_count": 250,
                "character_count": 1500,
                "revision_number": 1
            }
        }
    
    async def _extract_text_content(self, document_data: Dict[str, Any],
                                   metadata: DocumentMetadata) -> Dict[str, Any]:
        """Extract content from plain text documents."""
        content = document_data.get('content', '')
        
        await asyncio.sleep(0.05)  # Simulate processing
        
        # Simple text analysis
        lines = content.split('\n') if content else []
        words = content.split() if content else []
        
        return {
            "success": True,
            "extracted_text": content,
            "structured_data": {
                "line_count": len(lines),
                "word_count": len(words),
                "character_count": len(content),
                "non_empty_lines": len([line for line in lines if line.strip()]),
                "first_line": lines[0] if lines else ""
            }
        }
    
    async def _extract_image_content(self, document_data: Dict[str, Any],
                                    metadata: DocumentMetadata) -> Dict[str, Any]:
        """Extract content from image documents using OCR simulation."""
        await asyncio.sleep(0.3)  # Simulate OCR processing time
        
        return {
            "success": True,
            "extracted_text": f"OCR extracted text from {metadata.file_name}",
            "structured_data": {
                "image_dimensions": "1920x1080",
                "format": "JPEG",
                "color_space": "RGB",
                "ocr_confidence": 0.85,
                "detected_objects": ["text", "table", "logo"],
                "text_regions": [
                    {"region": "header", "text": "Document Header"},
                    {"region": "body", "text": "Main content area"},
                    {"region": "footer", "text": "Page footer"}
                ]
            }
        }
    
    async def _extract_spreadsheet_content(self, document_data: Dict[str, Any],
                                          metadata: DocumentMetadata) -> Dict[str, Any]:
        """Extract content from spreadsheet documents."""
        await asyncio.sleep(0.1)  # Simulate processing
        
        return {
            "success": True,
            "extracted_text": f"Data from spreadsheet: {metadata.file_name}",
            "structured_data": {
                "sheets": ["Sheet1", "Sheet2"],
                "total_rows": 100,
                "total_columns": 10,
                "data_sample": [
                    {"A1": "Name", "B1": "Age", "C1": "City"},
                    {"A2": "John", "B2": "25", "C2": "New York"},
                    {"A3": "Jane", "B3": "30", "C3": "Los Angeles"}
                ],
                "charts_count": 2,
                "pivot_tables_count": 1
            }
        }
    
    async def _extract_generic_content(self, document_data: Dict[str, Any],
                                      metadata: DocumentMetadata) -> Dict[str, Any]:
        """Generic content extraction for unknown types."""
        return {
            "success": True,
            "extracted_text": f"Generic extraction for {metadata.file_name}",
            "structured_data": {
                "file_name": metadata.file_name,
                "file_size": metadata.file_size,
                "processing_note": "Generic extraction used - specific type handler not available"
            }
        }


class DocumentProcessor:
    """Main document processing engine with workflow integration."""
    
    def __init__(self, max_concurrent: int = 10):
        self.classifier = DocumentClassifier()
        self.extractor = ContentExtractor()
        self.max_concurrent = max_concurrent
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "average_processing_time": 0.0
        }
    
    async def process_document(self, document_data: Dict[str, Any]) -> ProcessingResult:
        """Process a single document."""
        start_time = time.time()
        document_id = document_data.get('id', f"doc_{int(time.time())}")
        
        try:
            # Step 1: Extract metadata
            metadata = await self.classifier.extract_metadata(document_data)
            
            # Step 2: Extract content
            content_result = await self.extractor.extract_content(document_data, metadata)
            
            # Step 3: Post-process extracted data
            processed_content = await self._post_process_content(content_result, metadata)
            
            processing_time = time.time() - start_time
            
            # Update stats
            self._update_processing_stats(processing_time, True)
            
            return ProcessingResult(
                document_id=document_id,
                status=ProcessingStatus.COMPLETED,
                processed_content=processed_content,
                extracted_data=content_result.get("structured_data", {}),
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, False)
            
            logger.error(f"Document processing failed for {document_id}: {str(e)}")
            
            return ProcessingResult(
                document_id=document_id,
                status=ProcessingStatus.FAILED,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def process_document_batch(self, batch: DocumentBatch) -> Dict[str, Any]:
        """Process a batch of documents with parallel execution."""
        start_time = time.time()
        
        logger.info(f"Processing batch {batch.batch_id} with {len(batch.documents)} documents")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(doc_data):
            async with semaphore:
                return await self.process_document(doc_data)
        
        # Process documents in parallel
        tasks = [process_with_semaphore(doc) for doc in batch.documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_results.append({
                    "error": str(result),
                    "document_id": "unknown"
                })
            elif isinstance(result, ProcessingResult):
                if result.status == ProcessingStatus.COMPLETED:
                    successful_results.append(result)
                else:
                    failed_results.append(result)
        
        total_time = time.time() - start_time
        
        batch_result = {
            "batch_id": batch.batch_id,
            "processing_summary": {
                "total_documents": len(batch.documents),
                "successful": len(successful_results),
                "failed": len(failed_results),
                "success_rate": len(successful_results) / len(batch.documents) * 100,
                "total_processing_time": total_time,
                "average_time_per_document": total_time / len(batch.documents) if batch.documents else 0,
                "documents_per_second": len(batch.documents) / total_time if total_time > 0 else 0
            },
            "successful_results": [
                {
                    "document_id": r.document_id,
                    "processing_time": r.processing_time,
                    "extracted_data_keys": list(r.extracted_data.keys())
                }
                for r in successful_results
            ],
            "failed_results": [
                {
                    "document_id": getattr(r, 'document_id', 'unknown'),
                    "error": getattr(r, 'error_message', str(r))
                }
                for r in failed_results
            ],
            "batch_metadata": {
                "batch_type": batch.batch_type,
                "priority": batch.priority,
                "created_at": batch.created_at.isoformat(),
                "processing_options": batch.processing_options
            }
        }
        
        return batch_result
    
    async def _post_process_content(self, content_result: Dict[str, Any], 
                                   metadata: DocumentMetadata) -> Dict[str, Any]:
        """Post-process extracted content."""
        if not content_result.get("success", False):
            return content_result
        
        # Add enrichments
        processed = content_result.copy()
        processed["enrichments"] = {
            "document_metadata": {
                "file_name": metadata.file_name,
                "file_type": metadata.file_type.value,
                "file_size": metadata.file_size,
                "content_hash": metadata.content_hash,
                "processing_timestamp": datetime.now().isoformat()
            },
            "content_analysis": {
                "has_text": bool(content_result.get("extracted_text")),
                "has_structured_data": bool(content_result.get("structured_data")),
                "content_length": len(content_result.get("extracted_text", "")),
                "data_fields_count": len(content_result.get("structured_data", {}))
            }
        }
        
        # Add quality score (simplified)
        quality_score = self._calculate_quality_score(content_result)
        processed["quality_score"] = quality_score
        
        return processed
    
    def _calculate_quality_score(self, content_result: Dict[str, Any]) -> float:
        """Calculate content quality score."""
        score = 0.0
        
        # Base score for successful extraction
        if content_result.get("success", False):
            score += 50.0
        
        # Points for having text content
        extracted_text = content_result.get("extracted_text", "")
        if extracted_text:
            score += 25.0
            # Bonus for longer content
            if len(extracted_text) > 100:
                score += 10.0
        
        # Points for structured data
        structured_data = content_result.get("structured_data", {})
        if structured_data:
            score += 15.0
            # Bonus for rich structured data
            if len(structured_data) > 5:
                score += 5.0
        
        return min(100.0, score)  # Cap at 100
    
    def _update_processing_stats(self, processing_time: float, success: bool):
        """Update processing statistics."""
        self.processing_stats["total_processed"] += 1
        
        if success:
            self.processing_stats["successful"] += 1
        else:
            self.processing_stats["failed"] += 1
        
        # Update average processing time
        total = self.processing_stats["total_processed"]
        current_avg = self.processing_stats["average_processing_time"]
        
        self.processing_stats["average_processing_time"] = \
            (current_avg * (total - 1) + processing_time) / total
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        stats = self.processing_stats.copy()
        
        if stats["total_processed"] > 0:
            stats["success_rate"] = stats["successful"] / stats["total_processed"] * 100
            stats["failure_rate"] = stats["failed"] / stats["total_processed"] * 100
        else:
            stats["success_rate"] = 0.0
            stats["failure_rate"] = 0.0
        
        return stats


# Example usage and testing functions
async def create_sample_documents(count: int = 10) -> List[Dict[str, Any]]:
    """Create sample documents for testing."""
    documents = []
    doc_types = ["report.pdf", "data.xlsx", "notes.txt", "image.jpg", "presentation.docx"]
    
    for i in range(count):
        doc_type = doc_types[i % len(doc_types)]
        documents.append({
            "id": f"doc_{i:03d}",
            "file_name": f"document_{i:03d}_{doc_type}",
            "content": f"Sample content for document {i}",
            "file_size": 1024 + (i * 100),  # Variable file sizes
            "source": "test_upload",
            "tags": [f"tag{i % 3}", "sample"],
            "metadata": {
                "priority": i % 5,
                "department": "test"
            }
        })
    
    return documents


async def run_document_processing_demo():
    """Demonstration of the document processing workflow."""
    logger.info("Starting document processing demo")
    
    # Create processor
    processor = DocumentProcessor(max_concurrent=5)
    
    # Create sample documents
    sample_docs = await create_sample_documents(15)
    
    # Create batch
    batch = DocumentBatch(
        batch_id="demo_batch_001",
        documents=sample_docs,
        batch_type="demo",
        priority=1,
        processing_options={"enable_ocr": True, "extract_tables": True}
    )
    
    # Process batch
    result = await processor.process_document_batch(batch)
    
    # Print results
    logger.info("Document processing demo completed")
    logger.info(f"Processed {result['processing_summary']['total_documents']} documents")
    logger.info(f"Success rate: {result['processing_summary']['success_rate']:.1f}%")
    logger.info(f"Average processing time: {result['processing_summary']['average_time_per_document']:.3f}s")
    
    return result