"""
Configuration settings for advanced chunking and preprocessing.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ChunkingConfig:
    """Configuration for chunking parameters."""
    max_chunk_size: int = 1000
    min_chunk_size: int = 100
    overlap_ratio: float = 0.1
    
    # Hierarchical chunking settings
    respect_document_structure: bool = True
    preserve_table_integrity: bool = True
    maintain_code_blocks: bool = True
    
    # Content type specific sizes
    table_max_size: int = 1500
    code_block_max_size: int = 2000
    list_max_size: int = 800

@dataclass
class MetadataConfig:
    """Configuration for metadata extraction."""
    extract_entities: bool = True
    extract_keywords: bool = True
    extract_topics: bool = True
    extract_dates: bool = True
    extract_technical_terms: bool = True
    
    # Extraction limits
    max_entities: int = 10
    max_keywords: int = 15
    max_topics: int = 5
    max_technical_terms: int = 10
    
    # Topic classification keywords
    topic_keywords: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.topic_keywords is None:
            self.topic_keywords = {
                "technology": ["software", "computer", "digital", "algorithm", "data", "system", "AI", "ML"],
                "science": ["research", "study", "analysis", "experiment", "hypothesis", "theory", "method"],
                "business": ["market", "customer", "revenue", "strategy", "company", "industry", "sales"],
                "education": ["learning", "student", "teach", "course", "curriculum", "knowledge", "training"],
                "health": ["medical", "health", "patient", "treatment", "diagnosis", "therapy", "clinical"],
                "finance": ["financial", "investment", "banking", "economics", "money", "capital", "trading"],
                "legal": ["legal", "law", "court", "regulation", "compliance", "contract", "litigation"]
            }

@dataclass
class ProcessingConfig:
    """Configuration for document processing pipeline."""
    enable_hierarchical_chunking: bool = True
    enable_metadata_extraction: bool = True
    enable_multimodal_processing: bool = True
    enable_table_aware_chunking: bool = True
    enable_quality_assessment: bool = True
    
    # Processing strategy selection
    auto_detect_strategy: bool = True
    default_strategy: str = "hierarchical"  # Options: hierarchical, table_aware, standard
    
    # Content type detection thresholds
    table_detection_threshold: int = 5  # Minimum number of '|' characters
    code_block_detection_threshold: int = 3  # Minimum indented lines
    list_detection_threshold: int = 3  # Minimum list items
    heading_detection_threshold: int = 2  # Minimum heading markers

@dataclass
class QualityConfig:
    """Configuration for quality assessment."""
    enable_coherence_scoring: bool = True
    enable_density_scoring: bool = True
    enable_metadata_richness_scoring: bool = True
    enable_size_consistency_scoring: bool = True
    enable_overlap_efficiency_scoring: bool = True
    
    # Quality thresholds
    min_acceptable_quality: float = 0.5
    target_quality: float = 0.7
    excellent_quality: float = 0.85
    
    # Scoring weights
    coherence_weight: float = 0.25
    density_weight: float = 0.20
    metadata_weight: float = 0.20
    consistency_weight: float = 0.15
    overlap_weight: float = 0.20

@dataclass
class AdvancedProcessingConfig:
    """Master configuration for advanced processing."""
    chunking: ChunkingConfig = ChunkingConfig()
    metadata: MetadataConfig = MetadataConfig()
    processing: ProcessingConfig = ProcessingConfig()
    quality: QualityConfig = QualityConfig()
    
    # Global settings
    verbose_logging: bool = True
    performance_monitoring: bool = True
    cache_analysis_results: bool = True
    
    # File processing settings
    supported_file_types: List[str] = None
    max_file_size_mb: int = 50
    batch_processing_enabled: bool = True
    max_batch_size: int = 100
    
    def __post_init__(self):
        if self.supported_file_types is None:
            self.supported_file_types = [
                '.txt', '.md', '.pdf', '.docx', '.html', '.csv', '.json', '.xml'
            ]

# Default configuration instance
DEFAULT_CONFIG = AdvancedProcessingConfig()

# Preset configurations for different use cases
RESEARCH_PAPER_CONFIG = AdvancedProcessingConfig(
    chunking=ChunkingConfig(
        max_chunk_size=1200,
        overlap_ratio=0.15,
        preserve_table_integrity=True
    ),
    metadata=MetadataConfig(
        max_entities=15,
        max_keywords=20,
        extract_dates=True
    ),
    processing=ProcessingConfig(
        enable_multimodal_processing=True,
        enable_table_aware_chunking=True
    )
)

TECHNICAL_MANUAL_CONFIG = AdvancedProcessingConfig(
    chunking=ChunkingConfig(
        max_chunk_size=800,
        overlap_ratio=0.05,
        maintain_code_blocks=True,
        code_block_max_size=2500
    ),
    metadata=MetadataConfig(
        extract_technical_terms=True,
        max_technical_terms=15
    ),
    processing=ProcessingConfig(
        enable_hierarchical_chunking=True,
        default_strategy="hierarchical"
    )
)

BUSINESS_DOCUMENT_CONFIG = AdvancedProcessingConfig(
    chunking=ChunkingConfig(
        max_chunk_size=1000,
        overlap_ratio=0.1,
        preserve_table_integrity=True
    ),
    metadata=MetadataConfig(
        topic_keywords={
            **DEFAULT_CONFIG.metadata.topic_keywords,
            "business": ["revenue", "profit", "market", "strategy", "customer", "growth", "ROI", "KPI"]
        }
    ),
    processing=ProcessingConfig(
        enable_table_aware_chunking=True,
        auto_detect_strategy=True
    )
)

def get_config(config_name: str = "default") -> AdvancedProcessingConfig:
    """Get a configuration by name."""
    configs = {
        "default": DEFAULT_CONFIG,
        "research": RESEARCH_PAPER_CONFIG,
        "technical": TECHNICAL_MANUAL_CONFIG,
        "business": BUSINESS_DOCUMENT_CONFIG
    }
    
    return configs.get(config_name.lower(), DEFAULT_CONFIG)