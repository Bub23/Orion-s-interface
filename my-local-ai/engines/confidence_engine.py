class ConfidenceEngine:
    """Tracks Orion's confidence in responses."""
    
    def __init__(self):
        self.response_accuracy_log = []
    
    def calculate_confidence(self, message_type, has_relevant_memories, behavioral_rules_applied):
        """Calculate confidence score for a response."""
        confidence = 0.5  # Base confidence
        
        # Has relevant memory = more confident
        if has_relevant_memories > 0:
            confidence += min(0.3, has_relevant_memories * 0.1)
        
        # Has behavioral rules = more confident
        if behavioral_rules_applied > 0:
            confidence += min(0.2, behavioral_rules_applied * 0.05)
        
        return min(1.0, confidence)
    
    def format_confidence(self, score):
        """Format confidence as emoji/text."""
        if score >= 0.9:
            return "💯 Certain"
        elif score >= 0.7:
            return "✓ Confident"
        elif score >= 0.5:
            return "~ Somewhat sure"
        else:
            return "❓ Uncertain"
    
    def add_confidence_to_response(self, response, confidence_score):
        """Add confidence indicator to response."""
        if confidence_score < 0.6:
            response = f"[{self.format_confidence(confidence_score)}] {response}"
        return response
