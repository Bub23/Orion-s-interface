"""
Remix Engine - Pure business logic
Learning-based content mutation and regeneration
NO database access, NO async, pure functions
"""

from dataclasses import dataclass
from typing import List, Dict
import random
import re


@dataclass
class RemixPattern:
    """Pattern extracted from high-performing content"""
    pattern_type: str  # "hook_structure", "emotional_trigger", "pacing"
    pattern_text: str
    success_count: int
    viral_score: float


class RemixEngine:
    """
    Generates content variations from high performers
    Learns patterns and applies them to new ideas
    Pure logic - no DB, no async
    """
    
    @staticmethod
    def extract_hook_patterns(high_performing_hooks: List[str]) -> List[RemixPattern]:
        """
        Extract structural patterns from high-performing hooks
        Examples: "I [verb] [emotion]", "The [adjective] about [noun]"
        """
        patterns = []
        
        for hook in high_performing_hooks:
            # Extract pronoun + verb pattern
            pronoun_match = re.match(r'^(I|You|They|This|That)\s+(\w+)', hook)
            if pronoun_match:
                pattern = f"{pronoun_match.group(1)} [verb]"
                patterns.append(RemixPattern(
                    pattern_type="hook_structure",
                    pattern_text=pattern,
                    success_count=1,
                    viral_score=0.8
                ))
        
        return patterns
    
    @staticmethod
    def apply_pattern_mutation(text: str, mutations: int = 3) -> List[str]:
        """
        Apply multiple mutations to text
        - Perspective flip (I → You)
        - Intensifier injection ("WAIT:", "Real talk:")
        - Emotional angle variation
        """
        variants = [text]
        
        # Mutation 1: Perspective flip
        if text.startswith("I "):
            variants.append("You " + text[2:])
        elif text.startswith("You "):
            variants.append("I " + text[4:])
        
        # Mutation 2: Intensifier prefix
        intensifiers = ["WAIT:", "Real talk:", "The truth:", "Here's the thing:", "Honest take:"]
        for intensifier in intensifiers[:min(2, mutations)]:
            variants.append(f"{intensifier} {text}")
        
        # Mutation 3: Emotional angle
        emotional_suffixes = [
            "and it changes everything.",
            "or you're missing out.",
            "and nobody talks about it.",
            "that most people ignore."
        ]
        for suffix in emotional_suffixes[:min(1, mutations)]:
            variants.append(f"{text} {suffix}")
        
        return variants[:mutations + 1]
    
    @classmethod
    def remix_hook(
        cls,
        original_hook: str,
        remix_type: str = "variation"
    ) -> List[str]:
        """
        Create remix variations of a hook
        Types: "variation", "escalation", "reframe"
        """
        if remix_type == "variation":
            # Simple mutations
            return cls.apply_pattern_mutation(original_hook, 3)
        
        elif remix_type == "escalation":
            # Increase intensity
            escalations = [
                original_hook.replace("I ", "I JUST "),
                original_hook.replace("this", "THIS"),
                f"WAIT. {original_hook}",
                f"{original_hook} And it's worse than you think."
            ]
            return escalations
        
        elif remix_type == "reframe":
            # Change perspective/angle
            reframes = []
            if "lost" in original_hook.lower():
                reframes.append(original_hook.replace("lost", "gained something instead"))
            if "never" in original_hook.lower():
                reframes.append(original_hook.replace("never", "always"))
            
            # Fallback to mutations
            if not reframes:
                reframes = cls.apply_pattern_mutation(original_hook, 2)
            
            return reframes
        
        else:
            return cls.apply_pattern_mutation(original_hook, 3)
    
    @classmethod
    def remix_idea(
        cls,
        original_idea: str,
        remix_type: str = "sequel"
    ) -> str:
        """
        Create remix version of an idea
        Types: "sequel", "angle_flip", "deep_dive"
        """
        if remix_type == "sequel":
            return f"Part 2: The deeper truth about {original_idea}"
        
        elif remix_type == "angle_flip":
            return f"Why everyone's wrong about {original_idea}"
        
        elif remix_type == "deep_dive":
            return f"The real mechanism behind {original_idea}"
        
        elif remix_type == "controversy":
            return f"The unpopular take on {original_idea}"
        
        else:
            return f"More on {original_idea}"
    
    @staticmethod
    def blend_high_performers(
        high_performing_hooks: List[str],
        new_idea: str,
        blend_count: int = 3
    ) -> List[str]:
        """
        Blend successful hook patterns with new idea
        Extract what worked, apply to fresh content
        """
        if not high_performing_hooks:
            return []
        
        blends = []
        selected_hooks = random.sample(high_performing_hooks, min(blend_count, len(high_performing_hooks)))
        
        for performer in selected_hooks:
            # Extract first few words (the winning pattern)
            words = performer.split()[:3]
            pattern_prefix = " ".join(words)
            
            # Apply to new idea
            truncated_idea = " ".join(new_idea.split()[:5])
            blend = f"{pattern_prefix} {truncated_idea}"
            blends.append(blend)
        
        return blends
    
    @staticmethod
    def adaptive_remix_score(
        viral_history: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate confidence scores for each remix type
        based on historical performance
        """
        remix_types = ["variation", "escalation", "reframe"]
        scores = {}
        
        for remix_type in remix_types:
            avg_score = viral_history.get(remix_type, 0.5)
            scores[remix_type] = avg_score
        
        return scores
