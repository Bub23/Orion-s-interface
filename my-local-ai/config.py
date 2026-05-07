import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Decision Engine thresholds
PRIORITY_THRESHOLD = 5
EMOTION_INTENSITY_HIGH = 7
EMOTION_INTENSITY_LOW = 3

# Emotion map
EMOTIONS = {
    "focus": 8,
    "drive": 7,
    "curiosity": 6,
    "calm": 5,
    "uncertainty": 4,
    "stress": 3,
    "frustration": 2,
    "reset": 1
}

# Decision states
DECISION_STATES = {
    "FOCUS": "High priority, execute core task",
    "BUILD": "Creative mode, generate content",
    "EXECUTE": "Action mode, implement",
    "RESET": "Pause and recalibrate",
    "LEARN": "Absorb new information"
}

# Legacy content templates
LEGACY_TEMPLATES = {
    "hook": "What if {memory_theme} could {action}?",
    "story": "Started with {emotion_context}. Now {current_state}. Next: {vision}.",
    "mantra": "I am {identity}. I {core_action}. I {outcome}.",
    "brand_line": "{subject}: {verb}. {context}. {call_to_action}."
}
