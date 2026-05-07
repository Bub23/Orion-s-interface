"""
Constants and configuration for services
"""

from typing import Literal

CATEGORIES = Literal["music", "story", "ai", "hustle", "brand"]

# Category keyword mapping
CATEGORY_KEYWORDS = {
    "music": ["song", "beat", "rap", "music", "track", "produce", "sound", "melody"],
    "story": ["story", "happened", "life", "experience", "told", "moment", "day"],
    "ai": ["ai", "automation", "tool", "algorithm", "model", "machine", "code"],
    "hustle": ["money", "hustle", "rich", "make", "business", "startup", "scale"],
    "brand": ["brand", "product", "launch", "company", "service"]
}

# Hook types and patterns
HOOK_TYPES = ["shock", "story", "authority", "confession"]

HOOK_PATTERNS = {
    "shock": [
        "I lost everything in {}",
        "This is why {} never works",
        "They told me {} was impossible",
        "You're not ready for this: {}",
        "The truth about {} nobody talks about",
    ],
    "story": [
        "I almost gave up because {}",
        "This changed everything about {}",
        "Here's what really happened with {}",
        "Nobody believes me when I say {}",
        "The moment I understood {}",
    ],
    "authority": [
        "Everyone gets {} wrong",
        "Here's what experts miss about {}",
        "The real reason {} fails",
        "Most people don't understand {}",
        "This is what separates winners from losers in {}",
    ],
    "confession": [
        "I shouldn't say this, but {}",
        "People don't know this about {}",
        "Raw truth: {}",
        "This might get me in trouble: {}",
        "Honest opinion on {}: it's dangerous",
    ]
}

# Script pacing templates
PACING_TEMPLATES = {
    "fast": {
        "setup": "Short. Direct. Grab attention immediately.",
        "body_length": 2,
        "avg_sentence_length": 10
    },
    "medium": {
        "setup": "Balanced pacing. Mix of short and medium.",
        "body_length": 3,
        "avg_sentence_length": 15
    },
    "slow": {
        "setup": "Build tension. Longer sentences. More dramatic.",
        "body_length": 4,
        "avg_sentence_length": 20
    }
}

# Viral score thresholds
VIRAL_SCORE_THRESHOLDS = {
    "low": 0.5,
    "medium": 0.7,
    "high": 0.85
}
