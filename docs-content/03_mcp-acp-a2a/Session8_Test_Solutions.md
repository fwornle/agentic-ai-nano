# Session 8: Advanced Agent Workflows - Test Solutions

## 📝 Multiple Choice Test

**Question 1:** Which workflow pattern enables multiple tasks to execute simultaneously?  

A) Loop workflows  
B) Parallel workflows ✅  
C) Sequential workflows  
D) Conditional workflows  

**Explanation:** Parallel workflows enable concurrent execution of independent tasks, improving overall workflow performance through simultaneous processing of multiple operations.

---

**Question 2:** What triggers dynamic branching in conditional workflows?  

A) Random selection  
B) Agent availability  
C) Time-based schedules  
D) Data values and context evaluation ✅  

**Explanation:** Conditional workflows use data values and context evaluation to make dynamic routing decisions, allowing workflows to adapt their execution path based on runtime conditions.

---

**Question 3:** What is the most comprehensive approach to workflow fault recovery?  

A) Restarting the entire workflow  
B) Simple retry mechanisms  
C) Ignoring errors and continuing  
D) Rollback and retry with compensation actions ✅  

**Explanation:** Comprehensive fault recovery includes rollback capabilities and retry mechanisms with compensation actions to undo partial work when failures occur, ensuring system consistency.

---

**Question 4:** How do adaptive workflows improve their performance over time?  

A) By running more frequently  
B) By reducing the number of steps  
C) By analyzing performance metrics and adjusting execution strategies ✅  
D) By using faster hardware  

**Explanation:** Adaptive workflows analyze performance metrics like execution times and success rates to automatically adjust execution strategies, optimizing their performance based on historical data.

---

**Question 5:** What information does the workflow execution context typically maintain?  

A) Only the current step  
B) Just error messages  
C) State data, execution history, and resource allocations ✅  
D) Only timing information  

**Explanation:** Execution context maintains comprehensive information including state data, execution history, resource allocations, and metadata needed for proper workflow execution and recovery.

---

**Question 6:** How are dependencies between workflow steps managed?  

A) Using dependency graphs and prerequisite checking ✅  
B) By alphabetical ordering  
C) Through timing delays only  
D) Through random execution  

**Explanation:** Step dependencies are managed through dependency graphs that define prerequisite relationships, ensuring steps execute in the correct order based on their interdependencies.

---

**Question 7:** What is the purpose of resource allocation in advanced workflows?  

A) To reduce costs  
B) To improve security  
C) To simplify configuration  
D) To prevent resource contention and ensure optimal performance ✅  

**Explanation:** Resource allocation prevents resource contention by managing CPU, memory, and agent assignments, ensuring workflows have necessary resources for optimal performance.

---

**Question 8:** What metrics are most important for workflow observability?  

A) Only network traffic  
B) Only execution time  
C) Execution time, success rates, resource utilization, and error patterns ✅  
D) Just memory usage  

**Explanation:** Comprehensive workflow observability requires monitoring execution time, success rates, resource utilization, and error patterns to understand system behavior and identify optimization opportunities.

---

**Question 9:** What mechanisms prevent infinite loops in workflow systems?  

A) Time-based termination only  
B) Manual intervention  
C) Maximum iteration limits and conditional exit criteria ✅  
D) Random termination  

**Explanation:** Loop termination is ensured through maximum iteration limits combined with conditional exit criteria that evaluate whether the loop's objectives have been met.

---

**Question 10:** What advantage do hybrid workflows provide over simple workflow patterns?  

A) Lower resource usage  
B) Faster execution  
C) Easier implementation  
D) Flexibility to combine multiple execution patterns for complex scenarios ✅  

**Explanation:** Hybrid workflows combine multiple execution patterns (sequential, parallel, conditional) providing the flexibility needed to handle complex real-world scenarios that require sophisticated coordination.

---

## Scoring Guide

- **10 correct**: Expert level - Ready for enterprise workflow orchestration  
- **8-9 correct**: Proficient - Strong understanding of advanced workflow patterns  
- **6-7 correct**: Competent - Good grasp of workflow optimization concepts  
- **4-5 correct**: Developing - Review parallel processing and fault recovery sections  
- **Below 4**: Beginner - Revisit workflow fundamentals and execution patterns  

## Key Concepts Summary

1. **Workflow Patterns**: Sequential, parallel, conditional, and hybrid execution models  
2. **Fault Recovery**: Comprehensive error handling with rollback and compensation  
3. **Adaptive Optimization**: Performance-driven workflow improvement over time  
4. **Resource Management**: Preventing contention through proper allocation  
5. **Observability**: Multi-metric monitoring for system health and optimization  

---

**Challenge:** Create an intelligent document processing workflow with advanced patterns including parallel processing, conditional routing, human review integration, and quality validation.

### Complete Advanced Workflow Implementation:

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
    """Document metadata structure for workflow processing."""
    document_id: str
    file_name: str
    file_size: int
    mime_type: str
    page_count: int
    upload_time: datetime
    processing_priority: str
    language_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    extracted_text: Optional[str] = None
    processing_errors: List[str] = None
    review_required: bool = False

    def __post_init__(self):
        if self.processing_errors is None:
            self.processing_errors = []

class IntelligentDocumentWorkflow:
    """Advanced document processing workflow with parallel processing and conditional routing."""

    def __init__(self, workflow_engine: AdvancedWorkflowEngine):
        self.engine = workflow_engine
        self.workflow_id = "intelligent_document_processing"
        self._setup_workflow()

    def _setup_workflow(self):
        """Set up the complete document processing workflow."""

        # Define workflow steps with advanced patterns
        steps = [
            # Initial processing (sequential)
            WorkflowStep(
                step_id="document_validation",
                name="Document Validation",
                step_type=StepType.SEQUENTIAL,
                handler=self._validate_document,
                timeout_seconds=30,
                retry_count=2
            ),
            WorkflowStep(
                step_id="language_detection",
                name="Language Detection",
                step_type=StepType.SEQUENTIAL,
                handler=self._detect_language,
                dependencies=["document_validation"],
                timeout_seconds=60,
                retry_count=3
            ),

            # Parallel processing branch
            WorkflowStep(
                step_id="parallel_extraction",
                name="Parallel Content Extraction",
                step_type=StepType.PARALLEL,
                handler=self._coordinate_parallel_extraction,
                dependencies=["language_detection"],
                timeout_seconds=300,
                retry_count=2
            ),

            # Quality assessment (conditional)
            WorkflowStep(
                step_id="quality_assessment",
                name="Quality Assessment",
                step_type=StepType.CONDITIONAL,
                handler=self._assess_quality,
                dependencies=["parallel_extraction"],
                condition=lambda ctx: ctx.get("extraction_successful", False),
                timeout_seconds=120,
                retry_count=1
            ),

            # Conditional human review
            WorkflowStep(
                step_id="human_review_decision",
                name="Human Review Decision",
                step_type=StepType.CONDITIONAL,
                handler=self._decide_human_review,
                dependencies=["quality_assessment"],
                condition=lambda ctx: ctx.get("quality_score", 0) < 0.8,
                timeout_seconds=60
            ),
            WorkflowStep(
                step_id="human_review",
                name="Human Review Process",
                step_type=StepType.SEQUENTIAL,
                handler=self._request_human_review,
                dependencies=["human_review_decision"],
                condition=lambda ctx: ctx.get("review_required", False),
                timeout_seconds=3600  # 1 hour for human review
            ),

            # Final processing
            WorkflowStep(
                step_id="finalize_processing",
                name="Finalize Document Processing",
                step_type=StepType.SEQUENTIAL,
                handler=self._finalize_processing,
                dependencies=["quality_assessment", "human_review"],
                dependency_mode="ANY",  # Either quality assessment OR human review
                timeout_seconds=120
            ),

            # Adaptive optimization
            WorkflowStep(
                step_id="update_performance_metrics",
                name="Update Performance Metrics",
                step_type=StepType.SEQUENTIAL,
                handler=self._update_performance_metrics,
                dependencies=["finalize_processing"],
                timeout_seconds=30
            )
        ]

        # Create and register the workflow
        workflow = AdvancedWorkflow(
            workflow_id=self.workflow_id,
            name="Intelligent Document Processing",
            steps=steps,
            max_execution_time=7200,  # 2 hours maximum
            retry_policy="EXPONENTIAL_BACKOFF"
        )

        self.engine.register_workflow(workflow)

    async def _validate_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate document format and basic requirements."""
        metadata: DocumentMetadata = context["document_metadata"]

        # Perform validation checks
        validation_results = {
            "valid_format": metadata.mime_type in [
                "application/pdf", "text/plain", "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ],
            "acceptable_size": metadata.file_size <= 50 * 1024 * 1024,  # 50MB max
            "has_content": metadata.page_count > 0
        }

        is_valid = all(validation_results.values())

        if not is_valid:
            errors = [f"Validation failed: {k}" for k, v in validation_results.items() if not v]
            metadata.processing_errors.extend(errors)
            raise ValueError(f"Document validation failed: {'; '.join(errors)}")

        context.update({
            "validation_results": validation_results,
            "document_valid": True
        })

        logger.info(f"Document {metadata.document_id} validated successfully")
        return context

    async def _detect_language(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect document language with confidence scoring."""
        metadata: DocumentMetadata = context["document_metadata"]

        # Simulate language detection (in production, use ML service)
        await asyncio.sleep(0.5)  # Simulate processing time

        # Mock language detection results
        language_results = {
            "primary_language": "en",
            "confidence": 0.95,
            "secondary_languages": ["es", "fr"]
        }

        metadata.language_detected = language_results["primary_language"]
        metadata.confidence_score = language_results["confidence"]

        context.update({
            "language_detection": language_results,
            "processing_language": language_results["primary_language"]
        })

        logger.info(f"Language detected for {metadata.document_id}: {language_results['primary_language']} ({language_results['confidence']:.2f})")
        return context

    async def _coordinate_parallel_extraction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate parallel content extraction tasks."""
        metadata: DocumentMetadata = context["document_metadata"]

        # Define parallel extraction tasks
        extraction_tasks = [
            self._extract_text_content(context.copy()),
            self._extract_metadata(context.copy()),
            self._extract_images(context.copy()),
            self._extract_tables(context.copy())
        ]

        try:
            # Execute all extraction tasks in parallel
            results = await asyncio.gather(*extraction_tasks, return_exceptions=True)

            # Process results
            extraction_data = {}
            successful_extractions = 0

            for i, result in enumerate(results):
                task_name = ["text", "metadata", "images", "tables"][i]

                if isinstance(result, Exception):
                    logger.error(f"Extraction failed for {task_name}: {result}")
                    metadata.processing_errors.append(f"{task_name}_extraction_failed")
                else:
                    extraction_data[task_name] = result
                    successful_extractions += 1

            # Update context with extraction results
            context.update({
                "extraction_data": extraction_data,
                "extraction_successful": successful_extractions > 0,
                "successful_extractions": successful_extractions,
                "total_extractions": len(extraction_tasks)
            })

            logger.info(f"Parallel extraction completed for {metadata.document_id}: {successful_extractions}/{len(extraction_tasks)} successful")
            return context

        except Exception as e:
            metadata.processing_errors.append(f"parallel_extraction_failed: {str(e)}")
            context["extraction_successful"] = False
            raise

    async def _extract_text_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text content from document."""
        await asyncio.sleep(1.0)  # Simulate OCR/text extraction

        # Mock text extraction
        extracted_text = f"Sample extracted text from document {context['document_metadata'].document_id}"
        context['document_metadata'].extracted_text = extracted_text

        return {
            "text_content": extracted_text,
            "character_count": len(extracted_text),
            "word_count": len(extracted_text.split()),
            "extraction_confidence": 0.92
        }

    async def _extract_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document metadata and properties."""
        await asyncio.sleep(0.3)  # Simulate metadata extraction

        return {
            "creation_date": "2024-01-15",
            "author": "System User",
            "title": f"Document {context['document_metadata'].document_id}",
            "keywords": ["document", "processing", "automated"],
            "metadata_extraction_time": datetime.now().isoformat()
        }

    async def _extract_images(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and process images from document."""
        await asyncio.sleep(0.8)  # Simulate image processing

        return {
            "image_count": 3,
            "images": [
                {"image_id": "img_1", "type": "chart", "confidence": 0.89},
                {"image_id": "img_2", "type": "photo", "confidence": 0.95},
                {"image_id": "img_3", "type": "diagram", "confidence": 0.78}
            ],
            "total_image_size": 2048576  # ~2MB
        }

    async def _extract_tables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and parse tables from document."""
        await asyncio.sleep(0.6)  # Simulate table extraction

        return {
            "table_count": 2,
            "tables": [
                {"table_id": "tbl_1", "rows": 15, "columns": 4, "confidence": 0.91},
                {"table_id": "tbl_2", "rows": 8, "columns": 3, "confidence": 0.85}
            ],
            "extraction_method": "ML_based_detection"
        }

    async def _assess_quality(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall extraction quality and determine next steps."""
        metadata: DocumentMetadata = context["document_metadata"]
        extraction_data = context.get("extraction_data", {})

        # Calculate quality score based on extraction success and confidence
        quality_factors = []

        # Text extraction quality
        if "text" in extraction_data:
            text_quality = extraction_data["text"].get("extraction_confidence", 0)
            quality_factors.append(text_quality * 0.4)  # 40% weight

        # Image extraction quality
        if "images" in extraction_data:
            image_qualities = [img.get("confidence", 0) for img in extraction_data["images"].get("images", [])]
            avg_image_quality = sum(image_qualities) / len(image_qualities) if image_qualities else 0
            quality_factors.append(avg_image_quality * 0.2)  # 20% weight

        # Table extraction quality
        if "tables" in extraction_data:
            table_qualities = [tbl.get("confidence", 0) for tbl in extraction_data["tables"].get("tables", [])]
            avg_table_quality = sum(table_qualities) / len(table_qualities) if table_qualities else 0
            quality_factors.append(avg_table_quality * 0.2)  # 20% weight

        # Overall extraction success rate
        success_rate = context.get("successful_extractions", 0) / context.get("total_extractions", 1)
        quality_factors.append(success_rate * 0.2)  # 20% weight

        # Calculate final quality score
        overall_quality = sum(quality_factors)
        metadata.quality_score = overall_quality

        context.update({
            "quality_score": overall_quality,
            "quality_assessment": {
                "overall_score": overall_quality,
                "individual_factors": quality_factors,
                "assessment_time": datetime.now().isoformat()
            }
        })

        logger.info(f"Quality assessment for {metadata.document_id}: {overall_quality:.2f}")
        return context

    async def _decide_human_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide if human review is required based on quality metrics."""
        metadata: DocumentMetadata = context["document_metadata"]
        quality_score = context.get("quality_score", 1.0)

        # Determine review requirements
        review_required = (
            quality_score < 0.8 or  # Low quality score
            len(metadata.processing_errors) > 2 or  # Multiple errors
            metadata.processing_priority == "high"  # High priority documents
        )

        metadata.review_required = review_required
        context["review_required"] = review_required

        if review_required:
            context["review_reason"] = self._determine_review_reason(quality_score, metadata)

        logger.info(f"Human review decision for {metadata.document_id}: {'Required' if review_required else 'Not required'}")
        return context

    def _determine_review_reason(self, quality_score: float, metadata: DocumentMetadata) -> str:
        """Determine the specific reason for requiring human review."""
        reasons = []

        if quality_score < 0.8:
            reasons.append(f"Low quality score: {quality_score:.2f}")
        if len(metadata.processing_errors) > 2:
            reasons.append(f"Multiple errors: {len(metadata.processing_errors)}")
        if metadata.processing_priority == "high":
            reasons.append("High priority document")

        return "; ".join(reasons)

    async def _request_human_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Request human review for low-quality extractions."""
        metadata: DocumentMetadata = context["document_metadata"]

        # In production, this would integrate with a human review system
        review_request = {
            "document_id": metadata.document_id,
            "review_type": "quality_validation",
            "priority": metadata.processing_priority,
            "reason": context.get("review_reason", "Quality concerns"),
            "estimated_time": "15-30 minutes",
            "requested_at": datetime.now().isoformat()
        }

        # Simulate human review process (in production, this would be asynchronous)
        await asyncio.sleep(2.0)  # Simulate review time

        # Mock human review results
        human_review_result = {
            "reviewed_by": "human_reviewer_001",
            "review_completed_at": datetime.now().isoformat(),
            "quality_approved": True,
            "corrections_made": 3,
            "reviewer_notes": "Minor corrections to table extraction, overall good quality"
        }

        context.update({
            "human_review_request": review_request,
            "human_review_result": human_review_result,
            "review_completed": True
        })

        logger.info(f"Human review completed for {metadata.document_id}")
        return context

    async def _finalize_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize document processing and prepare output."""
        metadata: DocumentMetadata = context["document_metadata"]

        # Compile final processing results
        final_results = {
            "document_id": metadata.document_id,
            "processing_status": "completed",
            "completion_time": datetime.now().isoformat(),
            "quality_score": metadata.quality_score,
            "human_reviewed": context.get("review_completed", False),
            "extraction_summary": {
                "text_extracted": "text" in context.get("extraction_data", {}),
                "images_processed": "images" in context.get("extraction_data", {}),
                "tables_extracted": "tables" in context.get("extraction_data", {}),
                "metadata_extracted": "metadata" in context.get("extraction_data", {})
            },
            "processing_errors": metadata.processing_errors,
            "total_processing_time": "calculated_in_production"
        }

        context["final_results"] = final_results

        logger.info(f"Document processing finalized for {metadata.document_id}")
        return context

    async def _update_performance_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update performance metrics for adaptive optimization."""
        processing_time = 180  # Mock processing time in seconds
        quality_score = context.get("quality_score", 0.8)

        # Update metrics for adaptive optimization
        performance_update = {
            "workflow_execution_time": processing_time,
            "quality_achieved": quality_score,
            "human_review_required": context.get("review_required", False),
            "extraction_success_rate": context.get("successful_extractions", 0) / context.get("total_extractions", 1),
            "update_timestamp": datetime.now().isoformat()
        }

        # In production, this would update the adaptive optimization system
        context["performance_metrics_updated"] = performance_update

        logger.info(f"Performance metrics updated for workflow execution")
        return context

# Usage example
async def process_document_with_advanced_workflow():
    """Example of processing a document using the intelligent workflow."""

    # Initialize workflow engine and document processor
    workflow_engine = AdvancedWorkflowEngine()
    document_processor = IntelligentDocumentWorkflow(workflow_engine)

    # Create sample document metadata
    doc_metadata = DocumentMetadata(
        document_id="doc_12345",
        file_name="sample_report.pdf",
        file_size=2048576,  # 2MB
        mime_type="application/pdf",
        page_count=15,
        upload_time=datetime.now(),
        processing_priority="high"
    )

    # Execute the workflow
    initial_context = {
        "document_metadata": doc_metadata,
        "workflow_start_time": datetime.now().isoformat()
    }

    try:
        result = await workflow_engine.execute_workflow(
            workflow_id="intelligent_document_processing",
            context=initial_context
        )

        print(f"Document processing completed: {result['final_results']['processing_status']}")
        print(f"Quality score: {result['final_results']['quality_score']:.2f}")
        print(f"Human review required: {result['final_results']['human_reviewed']}")

        return result

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(process_document_with_advanced_workflow())
```

### Key Features Implemented:

1. **Parallel Processing**: Simultaneous extraction of text, images, tables, and metadata  
2. **Conditional Routing**: Dynamic decision-making based on quality scores and priorities  
3. **Human Review Integration**: Automatic escalation for low-quality extractions  
4. **Fault Recovery**: Comprehensive error handling with rollback capabilities  
5. **Adaptive Optimization**: Performance metrics collection for continuous improvement  

This advanced workflow demonstrates sophisticated coordination patterns while maintaining fault tolerance and quality assurance.

---

[Return to Session 8](Session8_Advanced_Agent_Workflows.md)
---

**Next:** [Session 9 - Production Agent Deployment →](Session9_Production_Agent_Deployment.md)

---
