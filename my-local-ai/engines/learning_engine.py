class LearningEngine:
    """Tracks what Orion learns and improves responses over time."""
    
    def __init__(self, structured_memory):
        self.memory = structured_memory
        self.learning_data = {
            "interaction_count": 0,
            "most_discussed_topics": {},
            "user_preferences": [],
            "communication_style": "neutral"
        }
    
    def analyze_user_style(self, messages):
        """Analyze user's communication style."""
        text = " ".join([m.get("content", "") for m in messages])
        text_lower = text.lower()
        
        # Detect style
        if any(word in text_lower for word in ["yo", "ya", "damn", "hell", "raw"]):
            return "casual_intense"
        elif any(word in text_lower for word in ["please", "thank", "kindly"]):
            return "formal_polite"
        elif any(word in text_lower for word in ["lol", "haha", "lmao"]):
            return "humorous"
        else:
            return "direct"
    
    def extract_topics(self, message):
        """Extract main topics from a message."""
        topics = []
        topic_keywords = {
            "music": ["song", "track", "beat", "rap", "artist", "album"],
            "business": ["business", "money", "revenue", "profit", "empire", "scale"],
            "tech": ["code", "build", "system", "app", "software", "api"],
            "personal": ["feel", "think", "believe", "want", "need", "love"],
            "goals": ["goal", "aim", "target", "mission", "future", "vision"]
        }
        
        msg_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def record_interaction(self, user_message, orion_response, user_satisfaction=None):
        """Record interaction for learning."""
        self.learning_data["interaction_count"] += 1
        
        # Extract and track topics
        topics = self.extract_topics(user_message)
        for topic in topics:
            self.learning_data["most_discussed_topics"][topic] = \
                self.learning_data["most_discussed_topics"].get(topic, 0) + 1
    
    def get_improvement_suggestions(self):
        """Suggest improvements based on learning data."""
        suggestions = []
        
        # If user talks about music a lot, suggest music-focused memories
        if self.learning_data["most_discussed_topics"].get("music", 0) > 5:
            suggestions.append("Add core music identity memory")
        
        # If interaction count is high, suggest personality refinement
        if self.learning_data["interaction_count"] > 20:
            suggestions.append("Refine personality based on communication patterns")
        
        return suggestions
    
    def get_learning_stats(self):
        """Get learning statistics."""
        return {
            "total_interactions": self.learning_data["interaction_count"],
            "main_topics": self.learning_data["most_discussed_topics"],
            "communication_style": self.learning_data["communication_style"],
            "improvement_areas": self.get_improvement_suggestions()
        }
