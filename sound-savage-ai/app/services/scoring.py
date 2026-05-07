"""
Scoring utilities for viral potential
Pure calculation logic
"""

import re
from typing import Dict
from app.services.constants import CATEGORY_KEYWORDS


class ScoringEngine:
    """Calculate viral scores and metrics"""
    
    @staticmethod
    def score_text_length(text: str) -> float:
        """Score based on optimal length"""
        word_count = len(text.split())
        
        # Sweet spot: 15-80 words
        if 15 <= word_count <= 80:
            return 1.0
        elif 10 <= word_count < 15 or 80 < word_count <= 120:
            return 0.7
        else:
            return 0.3
    
    @staticmethod
    def score_trigger_words(text: str) -> float:
        """Score based on emotional/action trigger words"""
        trigger_words = [
            "lost", "made", "shocked", "revealed", "secret",
            "changed", "never", "impossible", "exposed", "truth",
            "hate", "love", "angry", "cry", "laugh",
            "proof", "mistake", "wrong", "failed", "won"
        ]
        
        text_lower = text.lower()
        word_tokens = re.findall(r'\b\w+\b', text_lower)
        
        trigger_count = sum(1 for word in word_tokens if word in trigger_words)
        density = trigger_count / max(len(word_tokens), 1)
        
        # Optimal density: 3-8% of text
        if 0.03 <= density <= 0.08:
            return 1.0
        elif 0.02 <= density < 0.03 or 0.08 < density <= 0.15:
            return 0.7
        else:
            return 0.4
    
    @staticmethod
    def score_structure(text: str) -> float:
        """Score based on text structure"""
        sentences = text.split('.')
        avg_sentence_length = len(text.split()) / max(len(sentences), 1)
        
        # Good structure: 10-20 words per sentence
        if 10 <= avg_sentence_length <= 20:
            return 1.0
        elif 8 <= avg_sentence_length < 10 or 20 < avg_sentence_length <= 30:
            return 0.7
        else:
            return 0.4
    
    @staticmethod
    def score_source_boost(source: str) -> float:
        """Apply source-based score boost"""
        boosts = {
            "manual": 1.0,
            "trend": 1.25,
            "remix": 1.15
        }
        return boosts.get(source, 1.0)
    
    @classmethod
    def calculate_viral_score(cls, text: str, source: str = "manual") -> float:
        """
        Calculate overall viral potential score (0-1)
        
        Combines:
        - Text length score
        - Trigger word density
        - Structure quality
        - Source boost
        """
        length_score = cls.score_text_length(text)
        trigger_score = cls.score_trigger_words(text)
        structure_score = cls.score_structure(text)
        source_boost = cls.score_source_boost(source)
        
        # Weighted average
        base_score = (length_score * 0.3 + trigger_score * 0.4 + structure_score * 0.3)
        final_score = base_score * source_boost
        
        # Clamp to 0-1
        return min(max(final_score, 0.0), 1.0)


class CategoryScorer:
    """Score confidence for each category"""
    
    @staticmethod
    def score_categories(text: str) -> Dict[str, float]:
        """
        Return confidence scores for each category
        """
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            score = min(matches / max(len(keywords), 1), 1.0)
            scores[category] = score
        
        return scores
    
    @staticmethod
    def get_primary_category(text: str) -> str:
        """Get category with highest confidence"""
        scores = CategoryScorer.score_categories(text)
        return max(scores, key=scores.get) if scores else "brand"
