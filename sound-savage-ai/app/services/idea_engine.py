"""
Idea Engine - Pure business logic
Input validation, categorization, scoring
NO database access, NO async, pure functions
"""

from dataclasses import dataclass
from typing import Optional
from app.services.constants import CATEGORIES
from app.services.scoring import ScoringEngine, CategoryScorer


@dataclass
class ProcessedIdea:
    """Normalized idea ready for hook generation"""
    raw_input: str
    source: str  # manual, trend, remix
    category: str
    viral_score: float
    word_count: int
    confidence: dict


class IdeaEngine:
    """
    Validates and processes raw ideas
    Assigns category and viral score
    Pure logic - no DB, no async
    """
    
    @staticmethod
    def validate_input(text: str) -> bool:
        """Validate idea text meets minimum requirements"""
        if not text or not isinstance(text, str):
            return False
        
        word_count = len(text.split())
        if word_count < 5:
            return False
        
        if word_count > 500:
            return False
        
        return True
    
    @staticmethod
    def categorize(text: str) -> str:
        """Determine primary category"""
        return CategoryScorer.get_primary_category(text)
    
    @staticmethod
    def get_category_confidence(text: str) -> dict:
        """Get confidence scores for all categories"""
        return CategoryScorer.score_categories(text)
    
    @classmethod
    def process(
        cls,
        raw_input: str,
        source: str = "manual"
    ) -> Optional[ProcessedIdea]:
        """
        Full idea processing pipeline
        
        Returns ProcessedIdea if valid, None if validation fails
        """
        # Validate
        if not cls.validate_input(raw_input):
            return None
        
        # Categorize
        category = cls.categorize(raw_input)
        confidence = cls.get_category_confidence(raw_input)
        
        # Score
        viral_score = ScoringEngine.calculate_viral_score(raw_input, source)
        
        # Package
        idea = ProcessedIdea(
            raw_input=raw_input.strip(),
            source=source,
            category=category,
            viral_score=viral_score,
            word_count=len(raw_input.split()),
            confidence=confidence
        )
        
        return idea
    
    @classmethod
    def process_batch(cls, ideas: list, source: str = "manual") -> list:
        """Process multiple ideas in batch"""
        return [cls.process(idea, source) for idea in ideas if cls.process(idea, source)]
