"""
Hook Engine - Pure business logic
Viral hook generation from ideas
NO database access, NO async, pure functions
"""

from dataclasses import dataclass
from typing import List, Dict
import random
from app.services.constants import HOOK_PATTERNS, HOOK_TYPES


@dataclass
class GeneratedHook:
    """A single generated hook"""
    text: str
    hook_type: str
    variants: List[str]
    intensity: float  # 0-1, how aggressive/shocking


class HookEngine:
    """
    Generates viral hooks from ideas
    Creates multiple variations per idea
    Pure logic - no DB, no async
    """
    
    @staticmethod
    def truncate_for_hook(text: str, max_words: int = 20) -> str:
        """Truncate text to fit in hook pattern"""
        words = text.split()
        return " ".join(words[:max_words])
    
    @staticmethod
    def apply_hook_pattern(pattern: str, idea_text: str) -> str:
        """Apply pattern template to idea"""
        truncated = HookEngine.truncate_for_hook(idea_text)
        return pattern.format(truncated)
    
    @classmethod
    def generate_for_type(
        cls,
        idea_text: str,
        hook_type: str,
        count: int = 2
    ) -> List[GeneratedHook]:
        """Generate hooks for specific type"""
        if hook_type not in HOOK_PATTERNS:
            return []
        
        patterns = HOOK_PATTERNS[hook_type]
        hooks = []
        
        # Select random patterns for this type
        selected_patterns = random.sample(patterns, min(count, len(patterns)))
        
        for pattern in selected_patterns:
            hook_text = cls.apply_hook_pattern(pattern, idea_text)
            
            # Generate variants with different intensities
            variants = cls._generate_variants(hook_text, hook_type)
            
            hook = GeneratedHook(
                text=hook_text,
                hook_type=hook_type,
                variants=variants,
                intensity=0.7 + (random.random() * 0.3)
            )
            
            hooks.append(hook)
        
        return hooks
    
    @staticmethod
    def _generate_variants(hook_text: str, hook_type: str) -> List[str]:
        """Generate 2-3 variants of a hook"""
        variants = [hook_text]
        
        # Variant 1: Flip perspective
        if hook_text.startswith("I "):
            variants.append("You " + hook_text[2:])
        else:
            variants.append("I " + hook_text)
        
        # Variant 2: Add intensity marker
        if hook_type in ["shock", "confession"]:
            variants.append("WAIT: " + hook_text)
        
        return variants[:3]
    
    @classmethod
    def generate_all_types(
        cls,
        idea_text: str,
        total_hooks: int = 8
    ) -> List[GeneratedHook]:
        """
        Generate hooks across all types
        Distribute count evenly across types
        """
        hooks = []
        hooks_per_type = max(1, total_hooks // len(HOOK_TYPES))
        
        for hook_type in HOOK_TYPES:
            type_hooks = cls.generate_for_type(
                idea_text,
                hook_type,
                count=hooks_per_type
            )
            hooks.extend(type_hooks)
        
        # Shuffle and trim to exact count
        random.shuffle(hooks)
        return hooks[:total_hooks]
    
    @staticmethod
    def rank_hooks_by_characteristics(hooks: List[GeneratedHook]) -> List[GeneratedHook]:
        """
        Simple heuristic ranking
        Shock hooks often perform better, but variety matters
        """
        shock_hooks = [h for h in hooks if h.hook_type == "shock"]
        other_hooks = [h for h in hooks if h.hook_type != "shock"]
        
        # Shock first, then others
        return shock_hooks + other_hooks
