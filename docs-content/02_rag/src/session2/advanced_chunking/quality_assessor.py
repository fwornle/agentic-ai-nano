# src/advanced_chunking/quality_assessor.py
from typing import List, Dict, Any, Tuple
from langchain.schema import Document
import numpy as np
from collections import Counter

class ChunkQualityAssessor:
    """Assess the quality of generated chunks."""
    
    def __init__(self):
        self.quality_metrics = [
            "coherence_score",
            "information_density",
            "metadata_richness",
            "size_consistency",
            "overlap_efficiency"
        ]
    
    def assess_chunk_quality(self, chunks: List[Document]) -> Dict[str, float]:
        """Comprehensive quality assessment of chunks."""
        if not chunks:
            return {metric: 0.0 for metric in self.quality_metrics}
        
        # Calculate individual metrics
        coherence = self._calculate_coherence_score(chunks)
        density = self._calculate_information_density(chunks)
        metadata_richness = self._calculate_metadata_richness(chunks)
        size_consistency = self._calculate_size_consistency(chunks)
        overlap_efficiency = self._calculate_overlap_efficiency(chunks)
        
        return {
            "coherence_score": coherence,
            "information_density": density,
            "metadata_richness": metadata_richness,
            "size_consistency": size_consistency,
            "overlap_efficiency": overlap_efficiency,
            "overall_quality": np.mean([coherence, density, metadata_richness, size_consistency, overlap_efficiency])
        }

    def _calculate_coherence_score(self, chunks: List[Document]) -> float:
        """Calculate coherence score based on topic consistency."""
        if len(chunks) < 2:
            return 1.0
        
        # Extract topics from each chunk
        chunk_topics = []
        for chunk in chunks:
            topics = chunk.metadata.get("topics", [])
            chunk_topics.append(set(topics))
        
        # Calculate topic overlap between adjacent chunks
        overlaps = []
        for i in range(len(chunk_topics) - 1):
            current_topics = chunk_topics[i]
            next_topics = chunk_topics[i + 1]
            
            if current_topics and next_topics:
                overlap = len(current_topics & next_topics) / len(current_topics | next_topics)
                overlaps.append(overlap)
        
        return np.mean(overlaps) if overlaps else 0.0
    
    def _calculate_information_density(self, chunks: List[Document]) -> float:
        """Calculate information density score."""
        densities = []
        
        for chunk in chunks:
            content = chunk.page_content
            words = content.split()
            
            # Count unique words vs total words
            unique_words = len(set(words))
            total_words = len(words)
            
            if total_words > 0:
                density = unique_words / total_words
                densities.append(density)
        
        return np.mean(densities) if densities else 0.0
    
    def _calculate_metadata_richness(self, chunks: List[Document]) -> float:
        """Calculate metadata richness score."""
        metadata_features = [
            "topics", "entities", "keywords", "technical_terms",
            "difficulty_level", "content_summary"
        ]
        
        richness_scores = []
        
        for chunk in chunks:
            present_features = 0
            for feature in metadata_features:
                if feature in chunk.metadata and chunk.metadata[feature]:
                    present_features += 1
            
            richness = present_features / len(metadata_features)
            richness_scores.append(richness)
        
        return np.mean(richness_scores) if richness_scores else 0.0

    def _calculate_size_consistency(self, chunks: List[Document]) -> float:
        """Calculate size consistency score."""
        if not chunks:
            return 0.0
        
        sizes = [len(chunk.page_content) for chunk in chunks]
        
        if len(sizes) == 1:
            return 1.0
        
        # Calculate coefficient of variation (std dev / mean)
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        
        if mean_size == 0:
            return 0.0
        
        cv = std_size / mean_size
        
        # Convert to consistency score (lower CV = higher consistency)
        consistency = 1 / (1 + cv)
        
        return consistency

    def _calculate_overlap_efficiency(self, chunks: List[Document]) -> float:
        """Calculate overlap efficiency score."""
        if len(chunks) < 2:
            return 1.0
        
        # Calculate text overlap between consecutive chunks
        overlaps = []
        
        for i in range(len(chunks) - 1):
            current_content = set(chunks[i].page_content.split())
            next_content = set(chunks[i + 1].page_content.split())
            
            if current_content and next_content:
                overlap = len(current_content & next_content)
                union = len(current_content | next_content)
                
                if union > 0:
                    overlap_ratio = overlap / union
                    overlaps.append(overlap_ratio)
        
        if not overlaps:
            return 0.0
        
        avg_overlap = np.mean(overlaps)
        
        # Optimal overlap is around 10-20%
        optimal_overlap = 0.15
        efficiency = 1 - abs(avg_overlap - optimal_overlap) / optimal_overlap
        
        return max(0.0, efficiency)

    def generate_quality_report(self, chunks: List[Document]) -> str:
        """Generate a detailed quality report."""
        quality_scores = self.assess_chunk_quality(chunks)
        
        report = ["=== Chunk Quality Assessment Report ===\n"]
        
        report.append(f"Total chunks analyzed: {len(chunks)}")
        report.append(f"Overall quality score: {quality_scores['overall_quality']:.3f}\n")
        
        report.append("Individual Metrics:")
        for metric, score in quality_scores.items():
            if metric != 'overall_quality':
                status = self._get_score_status(score)
                report.append(f"  - {metric.replace('_', ' ').title()}: {score:.3f} ({status})")
        
        report.append("\nRecommendations:")
        recommendations = self._generate_recommendations(quality_scores)
        for rec in recommendations:
            report.append(f"  • {rec}")
        
        return "\n".join(report)

    def _get_score_status(self, score: float) -> str:
        """Get status description for a score."""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"

    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on scores."""
        recommendations = []
        
        if scores['coherence_score'] < 0.5:
            recommendations.append("Improve topic consistency between adjacent chunks")
        
        if scores['information_density'] < 0.4:
            recommendations.append("Reduce redundancy and increase unique information per chunk")
        
        if scores['metadata_richness'] < 0.5:
            recommendations.append("Enhance metadata extraction to capture more document features")
        
        if scores['size_consistency'] < 0.6:
            recommendations.append("Improve chunk size consistency through better boundary detection")
        
        if scores['overlap_efficiency'] < 0.5:
            recommendations.append("Optimize overlap ratio for better context continuity")
        
        if not recommendations:
            recommendations.append("Chunking quality is good - consider fine-tuning for specific use cases")
        
        return recommendations