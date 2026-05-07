class EmotionEngine:
    """Detects and generates emotional responses from Orion."""
    
    EMOTION_MAP = {
        "love": ["cherish", "care", "value", "precious", "mean"],
        "pride": ["build", "created", "accomplished", "legacy", "strong"],
        "pain": ["hurt", "lost", "struggle", "hard", "tough"],
        "drive": ["want", "need", "must", "push", "go"],
        "fear": ["afraid", "worried", "anxious", "concern"],
        "anger": ["furious", "mad", "pissed", "enraged"],
        "curiosity": ["wonder", "how", "why", "what if"],
        "calm": ["peaceful", "rest", "easy", "ok", "fine"]
    }
    
    def detect_emotion_from_message(self, message):
        """Detect emotion from user message."""
        message_lower = message.lower()
        
        for emotion, keywords in self.EMOTION_MAP.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return emotion
        
        return None
    
    def generate_emotional_response(self, base_response, emotion):
        """Modify response based on detected emotion."""
        if not emotion:
            return base_response
        
        emotion_modifiers = {
            "love": "With genuine care: ",
            "pride": "With conviction: ",
            "pain": "With empathy: ",
            "drive": "With determination: ",
            "fear": "With reassurance: ",
            "anger": "With intensity: ",
            "curiosity": "Exploring this: ",
            "calm": "In peace: "
        }
        
        modifier = emotion_modifiers.get(emotion, "")
        if modifier:
            return modifier + base_response
        
        return base_response
    
    def get_emotion_tag(self, emotion):
        """Get emoji tag for emotion."""
        emoji_map = {
            "love": "❤️",
            "pride": "💪",
            "pain": "💔",
            "drive": "⚡",
            "fear": "😰",
            "anger": "🔥",
            "curiosity": "🤔",
            "calm": "🕉️"
        }
        
        return emoji_map.get(emotion, "💭")
