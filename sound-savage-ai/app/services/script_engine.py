"""
Script Engine - Pure business logic
Structured video script building
NO database access, NO async, pure functions
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Literal
from app.services.constants import PACING_TEMPLATES


PacingType = Literal["fast", "medium", "slow"]


@dataclass
class ScriptSection:
    """Single section of a script"""
    title: str
    duration_seconds: int
    content: str


@dataclass
class StructuredScript:
    """Complete video script"""
    hook: str
    sections: List[ScriptSection]
    cta: str
    pacing: PacingType
    total_duration: int
    category: str


class ScriptEngine:
    """
    Builds structured video scripts from hooks
    Pacing control, duration management
    Pure logic - no DB, no async
    """
    
    @staticmethod
    def estimate_duration_for_words(word_count: int, pacing: PacingType = "medium") -> int:
        """Estimate seconds needed to deliver word count"""
        # Average speaking rate: 130-150 words per minute
        words_per_second = 2.2
        return max(2, int(word_count / words_per_second))
    
    @staticmethod
    def build_setup(hook: str, category: str, pacing: PacingType) -> str:
        """Build opening/setup section"""
        pacing_guide = PACING_TEMPLATES.get(pacing, PACING_TEMPLATES["medium"])
        
        setups = {
            "music": f"{hook} Here's how I made it work.",
            "story": f"{hook} Let me tell you exactly what happened.",
            "ai": f"{hook} This is what AI is actually doing.",
            "hustle": f"{hook} This is what changes the game.",
            "brand": f"{hook} Here's the real story."
        }
        
        return setups.get(category, setups["brand"])
    
    @staticmethod
    def build_body(idea_text: str, category: str, pacing: PacingType) -> List[str]:
        """Build main body sections"""
        pacing_config = PACING_TEMPLATES[pacing]
        body_length = pacing_config["body_length"]
        
        templates = {
            "music": [
                "The beat came first. Then everything changed.",
                "This is the part where most people give up.",
                "But here's what nobody tells you:"
            ],
            "story": [
                "So here's what actually happened...",
                "Most people would've quit here.",
                "That's when I realized something:"
            ],
            "ai": [
                "The algorithm works like this...",
                "This is the part that blew my mind.",
                "Here's why this matters:"
            ],
            "hustle": [
                "The money starts flowing when...",
                "This is what separates winners.",
                "And that's when I understood:"
            ],
            "brand": [
                "The product solves this specific problem.",
                "Here's what makes it different.",
                "This is why people care:"
            ]
        }
        
        return templates.get(category, templates["brand"])[:body_length]
    
    @staticmethod
    def build_payoff(hook: str, category: str) -> str:
        """Build the payoff/lesson section"""
        payoffs = {
            "music": "That's why it works. That's why people feel it.",
            "story": "And that changed everything about how I see it.",
            "ai": "That's the automation nobody's talking about.",
            "hustle": "That's how the money actually scales.",
            "brand": "That's what makes it stick."
        }
        
        return payoffs.get(category, payoffs["brand"])
    
    @staticmethod
    def build_cta(category: str) -> str:
        """Build call-to-action"""
        ctas = {
            "music": "Follow for more beats that hit different.",
            "story": "If this resonated, follow for more real ones.",
            "ai": "Follow for more AI truth bombs.",
            "hustle": "Follow if you want to build something real.",
            "brand": "Follow for more product insights."
        }
        
        return ctas.get(category, ctas["brand"])
    
    @classmethod
    def build(
        cls,
        hook: str,
        idea_text: str,
        category: str,
        pacing: PacingType = "medium"
    ) -> StructuredScript:
        """
        Build complete structured script
        """
        # Setup
        setup_content = cls.build_setup(hook, category, pacing)
        setup = ScriptSection(
            title="Hook & Setup",
            duration_seconds=cls.estimate_duration_for_words(len(setup_content.split())),
            content=setup_content
        )
        
        # Body
        body_contents = cls.build_body(idea_text, category, pacing)
        body = ScriptSection(
            title="Body",
            duration_seconds=cls.estimate_duration_for_words(len(" ".join(body_contents).split())),
            content=" ".join(body_contents)
        )
        
        # Payoff
        payoff_content = cls.build_payoff(hook, category)
        payoff = ScriptSection(
            title="Payoff",
            duration_seconds=cls.estimate_duration_for_words(len(payoff_content.split())),
            content=payoff_content
        )
        
        # CTA
        cta = cls.build_cta(category)
        cta_section = ScriptSection(
            title="CTA",
            duration_seconds=3,
            content=cta
        )
        
        # Calculate total
        sections = [setup, body, payoff, cta_section]
        total_duration = sum(s.duration_seconds for s in sections)
        
        script = StructuredScript(
            hook=hook,
            sections=sections,
            cta=cta,
            pacing=pacing,
            total_duration=total_duration,
            category=category
        )
        
        return script
    
    @staticmethod
    def script_to_dict(script: StructuredScript) -> dict:
        """Convert script to serializable dict"""
        return {
            "hook": script.hook,
            "sections": [
                {
                    "title": s.title,
                    "duration_seconds": s.duration_seconds,
                    "content": s.content
                }
                for s in script.sections
            ],
            "cta": script.cta,
            "pacing": script.pacing,
            "total_duration": script.total_duration,
            "category": script.category
        }
