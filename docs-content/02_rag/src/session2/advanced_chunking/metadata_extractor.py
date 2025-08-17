# src/advanced_chunking/metadata_extractor.py
from typing import List, Dict, Any, Optional, Set
from langchain.schema import Document
import re
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ExtractedMetadata:
    """Container for extracted metadata."""
    entities: List[str]
    keywords: List[str]
    topics: List[str]
    dates: List[str]
    numbers: List[float]
    technical_terms: List[str]
    difficulty_level: str
    content_summary: str

class MetadataExtractor:
    """Extracts rich metadata from document content."""
    
    def __init__(self):
        self.technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+\(\)\b',    # Function calls
            r'\b[a-zA-Z_]\w*\.[a-zA-Z_]\w*\b',  # Object notation
            r'\b\d+\.\d+\.\d+\b',  # Version numbers
        ]
        
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
        ]

    def extract_enhanced_metadata(self, document: Document) -> ExtractedMetadata:
        """Extract comprehensive metadata from document."""
        content = document.page_content
        
        # Extract different types of information
        entities = self._extract_entities(content)
        keywords = self._extract_keywords(content)
        topics = self._infer_topics(content)
        dates = self._extract_dates(content)
        numbers = self._extract_numbers(content)
        technical_terms = self._extract_technical_terms(content)
        difficulty_level = self._assess_difficulty(content)
        content_summary = self._generate_summary(content)
        
        return ExtractedMetadata(
            entities=entities,
            keywords=keywords,
            topics=topics,
            dates=dates,
            numbers=numbers,
            technical_terms=technical_terms,
            difficulty_level=difficulty_level,
            content_summary=content_summary
        )
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities using pattern matching."""
        entities = []
        
        # Extract capitalized words (potential proper nouns)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        entities.extend(capitalized_words)
        
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]*)"', content)
        entities.extend(quoted_terms)
        
        # Remove duplicates and filter by length
        entities = list(set([e for e in entities if len(e) > 2 and len(e) < 50]))
        
        return entities[:10]  # Limit to top 10

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content."""
        # Simple keyword extraction based on word frequency and length
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in ['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were', 'said', 'each', 'which', 'their']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)
        return keywords[:15]  # Top 15 keywords

    def _infer_topics(self, content: str) -> List[str]:
        """Infer topics from content using keyword analysis."""
        # Define topic keywords
        topic_keywords = {
            "technology": ["software", "computer", "digital", "algorithm", "data", "system"],
            "science": ["research", "study", "analysis", "experiment", "hypothesis", "theory"],
            "business": ["market", "customer", "revenue", "strategy", "company", "industry"],
            "education": ["learning", "student", "teach", "course", "curriculum", "knowledge"],
            "health": ["medical", "health", "patient", "treatment", "diagnosis", "therapy"]
        }
        
        content_lower = content.lower()
        topic_scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                topic_scores[topic] = score
        
        # Return topics sorted by relevance
        return sorted(topic_scores.keys(), key=lambda x: topic_scores[x], reverse=True)[:3]

    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content."""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))[:5]  # Limit to 5 unique dates

    def _extract_numbers(self, content: str) -> List[float]:
        """Extract numeric values from content."""
        # Find numbers (integers and floats)
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        matches = re.findall(number_pattern, content)
        
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers[:10]  # Limit to 10 numbers

    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms using patterns."""
        technical_terms = []
        
        for pattern in self.technical_patterns:
            matches = re.findall(pattern, content)
            technical_terms.extend(matches)
        
        # Remove duplicates and filter
        technical_terms = list(set([term for term in technical_terms if len(term) > 1]))
        
        return technical_terms[:10]  # Limit to 10 terms
    
    def _assess_difficulty(self, content: str) -> str:
        """Assess content difficulty level."""
        words = content.split()
        sentences = content.split('.')
        
        if not words or not sentences:
            return "unknown"
        
        # Calculate readability metrics
        avg_words_per_sentence = len(words) / len(sentences)
        long_words = len([w for w in words if len(w) > 6])
        long_word_ratio = long_words / len(words)
        
        # Technical term density
        technical_terms = len(self._extract_technical_terms(content))
        technical_density = technical_terms / len(words) if words else 0
        
        # Determine difficulty
        if avg_words_per_sentence > 20 or long_word_ratio > 0.3 or technical_density > 0.1:
            return "advanced"
        elif avg_words_per_sentence > 15 or long_word_ratio > 0.2:
            return "intermediate"
        else:
            return "beginner"
    
    def _generate_summary(self, content: str) -> str:
        """Generate a brief summary of the content."""
        sentences = content.split('.')
        if len(sentences) <= 2:
            return content[:200] + "..." if len(content) > 200 else content
        
        # Take first and potentially last sentence for summary
        first_sentence = sentences[0].strip()
        
        if len(sentences) > 3:
            # Find sentence with important keywords
            important_sentence = self._find_important_sentence(sentences[1:-1])
            summary = f"{first_sentence}. {important_sentence}"
        else:
            summary = first_sentence
        
        return summary[:300] + "..." if len(summary) > 300 else summary

    def _find_important_sentence(self, sentences: List[str]) -> str:
        """Find the most important sentence based on keyword density."""
        if not sentences:
            return ""
        
        # Simple scoring based on sentence length and presence of key terms
        scores = []
        for sentence in sentences:
            score = len(sentence.split())  # Basic length score
            # Boost score for sentences with technical terms or numbers
            if re.search(r'\d+', sentence):
                score += 5
            if any(pattern in sentence for pattern in ['important', 'key', 'main', 'primary']):
                score += 3
            scores.append(score)
        
        # Return sentence with highest score
        max_idx = scores.index(max(scores))
        return sentences[max_idx].strip()