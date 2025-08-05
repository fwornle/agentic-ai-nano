# Session 8: Advanced Agent Workflows - Solution Guide

## 🧪 Multiple Choice Quiz - Answer Key

### Quick Check Questions

1. **What is the main advantage of parallel workflow execution?**
   - A) Simpler error handling
   - B) Reduced execution time through concurrency ✅ **CORRECT**
   - C) Better resource management
   - D) Easier debugging

   **Explanation:** Parallel workflow execution allows independent steps to run simultaneously, significantly reducing overall execution time by utilizing available resources more efficiently.

2. **How does conditional branching work in advanced workflows?**
   - A) Random selection between branches
   - B) User input determines the branch
   - C) Expression evaluation determines execution path ✅ **CORRECT**
   - D) Time-based routing

   **Explanation:** Conditional branching evaluates expressions against workflow data to dynamically determine which execution path to follow, enabling intelligent workflow routing.

3. **What triggers workflow optimization recommendations?**
   - A) Manual requests only
   - B) Performance analysis and pattern detection ✅ **CORRECT**
   - C) Schedule-based analysis
   - D) Error thresholds

   **Explanation:** The workflow optimizer continuously analyzes performance metrics and execution patterns to automatically identify optimization opportunities and generate recommendations.

4. **How does the retry mechanism handle different error types?**
   - A) All errors are retried equally
   - B) Only timeout errors are retried
   - C) Retryable vs non-retryable errors are distinguished ✅ **CORRECT**
   - D) No retry logic is implemented

   **Explanation:** The retry mechanism categorizes errors into retryable (temporary failures) and non-retryable (permanent failures) to avoid wasting resources on errors that will consistently fail.

5. **What is the purpose of workflow rollback mechanisms?**
   - A) Performance optimization
   - B) Undo changes when workflows fail ✅ **CORRECT**
   - C) Agent load balancing
   - D) Error logging

   **Explanation:** Rollback mechanisms ensure data consistency by undoing changes made by completed steps when a workflow fails, preventing partial state corruption.

---

## 💡 Practical Exercise Solution

**Challenge:** Create an intelligent document processing workflow.

### Complete Solution:

```python
# document_processing/intelligent_workflow.py
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from workflows.advanced_engine import (
    AdvancedWorkflowEngine, AdvancedWorkflow, WorkflowStep, 
    StepType, StepStatus
)

logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    """Document metadata structure."""
    document_id: str
    file_name: str
    file_size: int
    mime_type: str
    page_count: int
    language: str
    confidence_score: float
    extracted_text: str = ""
    structured_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.structured_data is None:
            self.structured_data = {}

class DocumentProcessingWorkflow:
    """Advanced workflow for intelligent document processing."""
    
    def __init__(self, workflow_engine: AdvancedWorkflowEngine):
        self.engine = workflow_engine
        self.supported_formats = [
            "application/pdf", "image/jpeg", "image/png", 
            "image/tiff", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
    
    def create_document_workflow(self, document_info: Dict[str, Any]) -> AdvancedWorkflow:
        """Create a complex document processing workflow."""
        
        workflow_id = f"doc_processing_{int(datetime.now().timestamp())}"
        
        # Step 1: Document validation and preprocessing
        validation_step = WorkflowStep(
            step_id="validate_document",
            name="Document Validation",
            step_type=StepType.ACTION,
            action="validate_document_format",
            agent_capability="document_validation",
            input_mapping={
                "document_data": "input_document",
                "supported_formats": "supported_formats"
            },
            output_mapping={
                "is_valid": "document_valid",
                "metadata": "document_metadata",
                "preprocessing_required": "needs_preprocessing"
            },
            timeout=60,
            retry_policy={
                "max_retries": 2,
                "retry_delay": 1.0,
                "non_retryable_errors": ["ValueError", "UnsupportedFormatError"]
            }
        )
        
        # Step 2: Conditional preprocessing
        preprocessing_condition = WorkflowStep(
            step_id="check_preprocessing",
            name="Check Preprocessing Need",
            step_type=StepType.CONDITION,
            dependencies=["validate_document"],
            conditions=[
                {
                    "expression": "data.get('needs_preprocessing', False) == True",
                    "steps": ["preprocess_document"],
                    "description": "Document requires preprocessing"
                },
                {
                    "expression": "data.get('document_valid', False) == False",
                    "steps": ["handle_invalid_document"],
                    "description": "Document is invalid"
                }
            ],
            next_steps=["parallel_extraction"]
        )
        
        # Step 3: Document preprocessing (if needed)
        preprocessing_step = WorkflowStep(
            step_id="preprocess_document",
            name="Document Preprocessing",
            step_type=StepType.ACTION,
            action="preprocess_document",
            agent_capability="document_preprocessing",
            input_mapping={
                "document_data": "input_document",
                "metadata": "document_metadata"
            },
            output_mapping={
                "processed_document": "preprocessed_document",
                "processing_log": "preprocessing_log"
            },
            timeout=120,
            retry_policy={
                "max_retries": 3,
                "retry_delay": 2.0,
                "continue_on_failure": False
            }
        )
        
        # Step 4: Invalid document handler
        invalid_doc_step = WorkflowStep(
            step_id="handle_invalid_document",
            name="Handle Invalid Document",
            step_type=StepType.ACTION,
            action="handle_invalid_document",
            agent_capability="error_handling",
            input_mapping={
                "document_info": "input_document",
                "validation_errors": "validation_errors"
            },
            output_mapping={
                "error_report": "processing_errors",
                "recovery_suggestions": "recovery_options"
            }
        )
        
        # Step 5: Parallel extraction container
        parallel_extraction = WorkflowStep(
            step_id="parallel_extraction",
            name="Parallel Content Extraction",
            step_type=StepType.PARALLEL,
            dependencies=["check_preprocessing"],
            parallel_steps=[
                # OCR extraction sub-step
                WorkflowStep(
                    step_id="ocr_extraction",
                    name="OCR Text Extraction",
                    step_type=StepType.ACTION,
                    action="extract_text_ocr",
                    agent_capability="ocr_processing",
                    input_mapping={
                        "document": "preprocessed_document",
                        "language_hint": "document_language"
                    },
                    output_mapping={
                        "extracted_text": "ocr_text",
                        "confidence": "ocr_confidence",
                        "word_boxes": "text_coordinates"
                    },
                    timeout=180,
                    retry_policy={"max_retries": 2}
                ),
                
                # Metadata extraction sub-step
                WorkflowStep(
                    step_id="metadata_extraction",
                    name="Metadata Extraction",
                    step_type=StepType.ACTION,
                    action="extract_metadata",
                    agent_capability="metadata_extraction",
                    input_mapping={
                        "document": "preprocessed_document"
                    },
                    output_mapping={
                        "document_properties": "extracted_metadata",
                        "creation_date": "document_created",
                        "author": "document_author"
                    },
                    timeout=60,
                    retry_policy={"max_retries": 2}
                ),
                
                # Structure analysis sub-step
                WorkflowStep(
                    step_id="structure_analysis",
                    name="Document Structure Analysis",
                    step_type=StepType.ACTION,
                    action="analyze_document_structure",
                    agent_capability="structure_analysis",
                    input_mapping={
                        "document": "preprocessed_document"
                    },
                    output_mapping={
                        "document_type": "detected_type",
                        "sections": "document_sections",
                        "tables": "extracted_tables",
                        "images": "embedded_images"
                    },
                    timeout=120,
                    retry_policy={"max_retries": 2}
                )
            ],
            retry_policy={
                "parallel_failure_threshold": 0.7  # 70% must succeed
            }
        )
        
        # Step 6: Content type detection and routing
        content_routing = WorkflowStep(
            step_id="content_type_routing",
            name="Content Type Routing",
            step_type=StepType.CONDITION,
            dependencies=["parallel_extraction"],
            conditions=[
                {
                    "expression": "data.get('detected_type') == 'invoice'",
                    "steps": ["process_invoice"],
                    "description": "Process as invoice document"
                },
                {
                    "expression": "data.get('detected_type') == 'contract'",
                    "steps": ["process_contract"],
                    "description": "Process as legal contract"
                },
                {
                    "expression": "data.get('detected_type') == 'form'",
                    "steps": ["process_form"],
                    "description": "Process as structured form"
                },
                {
                    "expression": "data.get('detected_type') in ['report', 'article']",
                    "steps": ["process_text_document"],
                    "description": "Process as text document"
                }
            ],
            next_steps=["quality_validation"]
        )
        
        # Specialized processing steps
        invoice_processing = WorkflowStep(
            step_id="process_invoice",
            name="Invoice Processing",
            step_type=StepType.ACTION,
            action="process_invoice_document",
            agent_capability="invoice_processing",
            input_mapping={
                "text": "ocr_text",
                "tables": "extracted_tables",
                "metadata": "extracted_metadata"
            },
            output_mapping={
                "invoice_data": "structured_invoice",
                "line_items": "invoice_line_items",
                "totals": "invoice_totals"
            },
            timeout=90
        )
        
        contract_processing = WorkflowStep(
            step_id="process_contract",
            name="Contract Processing",
            step_type=StepType.ACTION,
            action="process_legal_contract",
            agent_capability="legal_document_processing",
            input_mapping={
                "text": "ocr_text",
                "sections": "document_sections",
                "metadata": "extracted_metadata"
            },
            output_mapping={
                "contract_data": "structured_contract",
                "key_terms": "contract_terms",
                "parties": "contract_parties",
                "dates": "important_dates"
            },
            timeout=120
        )
        
        form_processing = WorkflowStep(
            step_id="process_form",
            name="Form Processing",
            step_type=StepType.ACTION,
            action="process_form_document",
            agent_capability="form_processing",
            input_mapping={
                "text": "ocr_text",
                "text_coordinates": "text_coordinates",
                "form_structure": "document_sections"
            },
            output_mapping={
                "form_data": "structured_form",
                "field_values": "form_fields",
                "validation_status": "form_validation"
            },
            timeout=75
        )
        
        text_processing = WorkflowStep(
            step_id="process_text_document",
            name="Text Document Processing",
            step_type=StepType.ACTION,
            action="process_text_document",
            agent_capability="text_analysis",
            input_mapping={
                "text": "ocr_text",
                "sections": "document_sections"
            },
            output_mapping={
                "summary": "document_summary",
                "key_entities": "extracted_entities",
                "topics": "document_topics"
            },
            timeout=90
        )
        
        # Step 7: Multi-page processing loop
        multipage_processing = WorkflowStep(
            step_id="multipage_processing",
            name="Multi-page Processing Loop",
            step_type=StepType.LOOP,
            dependencies=["content_type_routing"],
            loop_condition="data.get('current_page', 1) <= data.get('total_pages', 1)",
            loop_max_iterations=100,
            parallel_steps=[
                WorkflowStep(
                    step_id="process_page",
                    name="Process Individual Page",
                    step_type=StepType.ACTION,
                    action="process_document_page",
                    agent_capability="page_processing",
                    input_mapping={
                        "page_number": "current_page",
                        "page_content": "page_data"
                    },
                    output_mapping={
                        "processed_page": "page_result"
                    }
                )
            ]
        )
        
        # Step 8: Quality validation with retry logic
        quality_validation = WorkflowStep(
            step_id="quality_validation",
            name="Quality Validation",
            step_type=StepType.ACTION,
            dependencies=["content_type_routing", "multipage_processing"],
            action="validate_extraction_quality",
            agent_capability="quality_validation",
            input_mapping={
                "extracted_data": "processed_content",
                "confidence_scores": "extraction_confidence",
                "original_document": "input_document"
            },
            output_mapping={
                "quality_score": "validation_score",
                "validation_passed": "quality_check_passed",
                "issues_found": "quality_issues"
            },
            timeout=60,
            retry_policy={
                "max_retries": 3,
                "retry_delay": 2.0,
                "continue_on_failure": True
            }
        )
        
        # Step 9: Human review fallback (conditional)
        human_review_check = WorkflowStep(
            step_id="check_human_review",
            name="Check Human Review Need",
            step_type=StepType.CONDITION,
            dependencies=["quality_validation"],
            conditions=[
                {
                    "expression": "data.get('quality_check_passed', False) == False or data.get('validation_score', 0) < 0.8",
                    "steps": ["human_review_task"],
                    "description": "Quality validation failed, require human review"
                }
            ],
            next_steps=["finalize_processing"]
        )
        
        # Step 10: Human review task
        human_review = WorkflowStep(
            step_id="human_review_task",
            name="Human Review Task",
            step_type=StepType.HUMAN_TASK,
            action="request_human_review",
            agent_capability="human_task_management",
            input_mapping={
                "document": "input_document",
                "extracted_data": "processed_content",
                "quality_issues": "quality_issues",
                "validation_score": "validation_score"
            },
            output_mapping={
                "reviewed_data": "human_reviewed_content",
                "review_comments": "human_review_notes",
                "approval_status": "human_approval"
            },
            timeout=86400,  # 24 hours for human review
            error_handlers=["handle_review_timeout"]
        )
        
        # Step 11: Review timeout handler
        review_timeout_handler = WorkflowStep(
            step_id="handle_review_timeout",
            name="Handle Review Timeout",
            step_type=StepType.ACTION,
            action="handle_human_review_timeout",
            agent_capability="escalation_management",
            input_mapping={
                "original_request": "human_review_request",
                "timeout_duration": "review_timeout"
            },
            output_mapping={
                "escalation_result": "timeout_escalation",
                "fallback_decision": "automated_fallback"
            }
        )
        
        # Step 12: Final processing and output
        finalize_processing = WorkflowStep(
            step_id="finalize_processing",
            name="Finalize Document Processing",
            step_type=StepType.ACTION,
            dependencies=["check_human_review"],
            action="finalize_document_processing",
            agent_capability="output_generation",
            input_mapping={
                "processed_content": "final_content",
                "metadata": "document_metadata",
                "quality_info": "quality_validation_results"
            },
            output_mapping={
                "final_document": "processed_document",
                "processing_report": "completion_report",
                "confidence_metrics": "final_confidence"
            },
            timeout=30,
            rollback_actions=["cleanup_temp_files", "restore_original_state"]
        )
        
        # Create the workflow
        workflow = AdvancedWorkflow(
            workflow_id=workflow_id,
            name="Intelligent Document Processing",
            description="Advanced document processing with OCR, NLP, and quality validation",
            version="2.0",
            steps=[
                validation_step,
                preprocessing_condition,
                preprocessing_step,
                invalid_doc_step,
                parallel_extraction,
                content_routing,
                invoice_processing,
                contract_processing,
                form_processing,
                text_processing,
                multipage_processing,
                quality_validation,
                human_review_check,
                human_review,
                review_timeout_handler,
                finalize_processing
            ],
            global_variables={
                "input_document": document_info,
                "supported_formats": self.supported_formats,
                "quality_threshold": 0.8,
                "max_processing_time": 3600
            },
            timeout=7200,  # 2 hours total timeout
            max_parallel_steps=5,
            retry_policy={
                "global_max_retries": 3,
                "continue_on_failure": False
            },
            sla_targets={
                "completion_time": 1800,  # 30 minutes target
                "quality_score": 0.9,
                "success_rate": 0.95
            },
            optimization_enabled=True,
            adaptive_routing=True,
            tags=["document-processing", "ocr", "nlp", "quality-validation"]
        )
        
        return workflow
    
    async def process_document(self, document_data: bytes, 
                             document_name: str,
                             document_type: str = None) -> Dict[str, Any]:
        """Process a document using the intelligent workflow."""
        
        document_info = {
            "document_id": f"doc_{int(datetime.now().timestamp())}",
            "file_name": document_name,
            "file_data": document_data,
            "file_size": len(document_data),
            "document_type": document_type,
            "processing_options": {
                "enable_ocr": True,
                "enable_nlp": True,
                "quality_validation": True,
                "human_review_threshold": 0.8
            }
        }
        
        # Create workflow
        workflow = self.create_document_workflow(document_info)
        
        # Execute workflow
        execution_result = await self.engine.execute_workflow(
            workflow=workflow,
            input_data=document_info,
            execution_options={
                "enable_monitoring": True,
                "enable_optimization": True,
                "quality_gates": True
            }
        )
        
        return execution_result
    
    def create_batch_processing_workflow(self, documents: List[Dict[str, Any]]) -> AdvancedWorkflow:
        """Create a workflow for batch document processing."""
        
        workflow_id = f"batch_processing_{int(datetime.now().timestamp())}"
        
        # Batch processing with parallel document workflows
        batch_processing = WorkflowStep(
            step_id="batch_document_processing",
            name="Batch Document Processing",
            step_type=StepType.PARALLEL,
            parallel_steps=[
                WorkflowStep(
                    step_id=f"process_doc_{i}",
                    name=f"Process Document {i+1}",
                    step_type=StepType.ACTION,
                    action="process_single_document",
                    agent_capability="document_processing",
                    input_mapping={
                        "document_data": f"document_{i}",
                        "processing_config": "batch_config"
                    },
                    output_mapping={
                        "processed_result": f"result_{i}"
                    },
                    timeout=1800  # 30 minutes per document
                ) for i in range(len(documents))
            ],
            retry_policy={
                "parallel_failure_threshold": 0.8,  # 80% must succeed
                "max_retries": 2
            }
        )
        
        # Aggregate results
        aggregation_step = WorkflowStep(
            step_id="aggregate_results",
            name="Aggregate Batch Results",
            step_type=StepType.ACTION,
            dependencies=["batch_document_processing"],
            action="aggregate_processing_results",
            agent_capability="result_aggregation",
            input_mapping={
                "individual_results": "batch_results",
                "processing_metadata": "batch_metadata"
            },
            output_mapping={
                "aggregated_data": "final_batch_results",
                "batch_statistics": "processing_stats",
                "failed_documents": "processing_failures"
            }
        )
        
        return AdvancedWorkflow(
            workflow_id=workflow_id,
            name="Batch Document Processing",
            description="Process multiple documents in parallel with aggregation",
            version="1.0",
            steps=[batch_processing, aggregation_step],
            global_variables={
                "documents": documents,
                "batch_size": len(documents),
                "batch_config": {
                    "enable_optimization": True,
                    "quality_threshold": 0.8,
                    "parallel_limit": 10
                }
            },
            timeout=3600 * len(documents) // 10,  # Scale timeout with batch size
            max_parallel_steps=min(10, len(documents)),
            optimization_enabled=True
        )

# Example usage and testing
async def demo_document_processing():
    """Demonstrate the intelligent document processing workflow."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    # Mock workflow engine setup
    from workflows.advanced_engine import AdvancedWorkflowEngine
    from workflows.step_executor import StepExecutor
    from workflows.monitors import WorkflowMonitor
    
    step_executor = StepExecutor()
    monitor = WorkflowMonitor()
    engine = AdvancedWorkflowEngine(step_executor, monitor)
    
    # Create document processing system
    doc_processor = DocumentProcessingWorkflow(engine)
    
    console.print(Panel.fit(
        "📄 Intelligent Document Processing Demo\nAdvanced workflow with parallel processing and quality validation",
        title="Document Processing System",
        border_style="blue"
    ))
    
    # Sample documents
    sample_documents = [
        {
            "name": "invoice_001.pdf",
            "type": "invoice",
            "size": 1024 * 500,  # 500KB
            "pages": 2
        },
        {
            "name": "contract_legal.pdf", 
            "type": "contract",
            "size": 1024 * 1200,  # 1.2MB
            "pages": 15
        },
        {
            "name": "application_form.pdf",
            "type": "form",
            "size": 1024 * 300,  # 300KB
            "pages": 3
        }
    ]
    
    # Process documents
    results_table = Table(title="Document Processing Results")
    results_table.add_column("Document", style="cyan")
    results_table.add_column("Type", style="yellow")
    results_table.add_column("Status", style="green")
    results_table.add_column("Processing Time", style="blue")
    results_table.add_column("Quality Score", style="magenta")
    
    for doc in sample_documents:
        console.print(f"🔄 Processing {doc['name']}...")
        
        # Mock document processing
        mock_result = {
            "execution_id": f"exec_{doc['name']}",
            "status": "completed",
            "execution_time": 45.2,
            "result": {
                "quality_score": 0.92,
                "confidence": 0.88,
                "pages_processed": doc['pages']
            }
        }
        
        results_table.add_row(
            doc['name'],
            doc['type'],
            mock_result['status'],
            f"{mock_result['execution_time']:.1f}s",
            f"{mock_result['result']['quality_score']:.2f}"
        )
    
    console.print(results_table)
    
    # Show workflow optimization recommendations
    console.print("\n🔍 Workflow Optimization Recommendations:")
    recommendations = [
        "• Implement caching for repeated document types (25% improvement)",
        "• Increase parallel OCR processing (15% improvement)", 
        "• Add pre-processing filters for better quality (10% improvement)",
        "• Optimize memory usage during large document processing (20% improvement)"
    ]
    
    for rec in recommendations:
        console.print(rec)

if __name__ == "__main__":
    asyncio.run(demo_document_processing())
```

### Key Features Implemented:

1. **Parallel Processing**: OCR, metadata extraction, and structure analysis run concurrently
2. **Conditional Logic**: Dynamic routing based on document type detection
3. **Loop Processing**: Multi-page document handling with iteration control
4. **Error Handling**: Comprehensive retry policies and rollback mechanisms
5. **Human Review Integration**: Fallback to human review for low-quality extractions
6. **Quality Validation**: Multi-stage quality checks with configurable thresholds
7. **Batch Processing**: Parallel processing of multiple documents
8. **Optimization**: Built-in performance optimization and monitoring

### Advanced Workflow Patterns:

```python
# Additional advanced patterns for enterprise use

class EnterpriseWorkflowPatterns:
    """Advanced enterprise workflow patterns."""
    
    @staticmethod
    def create_disaster_recovery_workflow() -> AdvancedWorkflow:
        """Create workflow with comprehensive disaster recovery."""
        
        # Checkpointing step
        checkpoint_step = WorkflowStep(
            step_id="create_checkpoint",
            name="Create Processing Checkpoint",
            step_type=StepType.ACTION,
            action="create_workflow_checkpoint",
            agent_capability="checkpoint_management",
            input_mapping={"current_state": "workflow_state"},
            output_mapping={"checkpoint_id": "recovery_checkpoint"}
        )
        
        # Recovery validation
        recovery_validation = WorkflowStep(
            step_id="validate_recovery",
            name="Validate Recovery Point",
            step_type=StepType.CONDITION,
            conditions=[
                {
                    "expression": "data.get('checkpoint_valid', False) == True",
                    "steps": ["resume_from_checkpoint"],
                    "description": "Resume from valid checkpoint"
                },
                {
                    "expression": "data.get('checkpoint_valid', False) == False",
                    "steps": ["restart_workflow"],
                    "description": "Restart workflow from beginning"
                }
            ]
        )
        
        return AdvancedWorkflow(
            workflow_id="disaster_recovery_example",
            name="Disaster Recovery Workflow",
            description="Workflow with comprehensive recovery mechanisms",
            steps=[checkpoint_step, recovery_validation],
            retry_policy={
                "enable_checkpointing": True,
                "checkpoint_interval": 300,  # Every 5 minutes
                "auto_recovery": True
            }
        )
    
    @staticmethod  
    def create_adaptive_optimization_workflow() -> AdvancedWorkflow:
        """Create self-optimizing workflow."""
        
        # Performance monitoring step
        monitor_step = WorkflowStep(
            step_id="monitor_performance",
            name="Monitor Workflow Performance",
            step_type=StepType.ACTION,
            action="collect_performance_metrics",
            agent_capability="performance_monitoring",
            metrics_enabled=True,
            custom_metrics=[
                "execution_time_per_step",
                "resource_utilization",
                "error_rates",
                "bottleneck_detection"
            ]
        )
        
        # Adaptive optimization step
        optimization_step = WorkflowStep(
            step_id="adaptive_optimization",
            name="Apply Adaptive Optimizations",
            step_type=StepType.ACTION,
            dependencies=["monitor_performance"],
            action="apply_runtime_optimizations",
            agent_capability="workflow_optimization",
            input_mapping={
                "performance_data": "collected_metrics",
                "historical_data": "optimization_history"
            },
            output_mapping={
                "optimizations_applied": "runtime_optimizations",
                "performance_improvement": "optimization_impact"
            }
        )
        
        return AdvancedWorkflow(
            workflow_id="adaptive_optimization_example",
            name="Self-Optimizing Workflow",
            description="Workflow that adapts and optimizes during execution",
            steps=[monitor_step, optimization_step],
            optimization_enabled=True,
            adaptive_routing=True,
            sla_targets={
                "optimization_improvement": 0.15,  # 15% improvement target
                "adaptation_frequency": 600  # Optimize every 10 minutes
            }
        )
```

### Testing Scenarios:

1. **Multi-format Document Processing**: Tests handling of PDFs, images, and Office documents
2. **Quality Validation Failure**: Tests human review fallback when quality is low
3. **Parallel Processing Optimization**: Tests concurrent extraction performance
4. **Loop Processing**: Tests multi-page document iteration
5. **Error Recovery**: Tests rollback and retry mechanisms
6. **Batch Processing**: Tests parallel processing of multiple documents

This comprehensive document processing workflow demonstrates all advanced workflow patterns: parallel execution, conditional branching, loops, error handling, human tasks, and quality validation with intelligent optimization.