from config import DECISION_STATES, PRIORITY_THRESHOLD, EMOTION_INTENSITY_HIGH, EMOTION_INTENSITY_LOW
from engines.behavior_modifier import BehaviorModifier

class DecisionEngine:
    """Reads memory state and outputs actionable decisions, modified by behavior rules."""
    
    def __init__(self, memory_store):
        self.memory = memory_store
        self.behavior = BehaviorModifier()
    
    def analyze(self):
        """Analyze memory state and return decision signal modified by directives."""
        entries = self.memory.get_all()
        
        if not entries:
            return {
                "decision": "RESET",
                "reason": "No memories found. Initialize system.",
                "action": "Log your first memory to begin.",
                "confidence": 0.5
            }
        
        # Calculate aggregate metrics
        avg_priority = sum(e["priority"] for e in entries) / len(entries)
        avg_emotion = sum(e["emotion_score"] for e in entries) / len(entries)
        recent_entries = self.memory.get_recent(3)
        
        # Decision logic
        if avg_priority >= PRIORITY_THRESHOLD and avg_emotion >= EMOTION_INTENSITY_HIGH:
            decision = "FOCUS"
            reason = f"High priority ({avg_priority:.1f}) + high emotional intensity ({avg_emotion:.1f})"
            action = "Execute your core focus. Eliminate distractions."
        
        elif avg_emotion >= EMOTION_INTENSITY_HIGH:
            decision = "BUILD"
            reason = f"High emotional intensity ({avg_emotion:.1f}). Creative mode engaged."
            action = "Channel this energy into creation. Generate content."
        
        elif avg_priority >= PRIORITY_THRESHOLD:
            decision = "EXECUTE"
            reason = f"High priority items detected ({avg_priority:.1f}). Action needed."
            action = "Work systematically through priorities."
        
        elif avg_emotion <= EMOTION_INTENSITY_LOW:
            decision = "RESET"
            reason = f"Low emotional energy ({avg_emotion:.1f}). Recalibration needed."
            action = "Rest, reflect, or seek input."
        
        else:
            decision = "LEARN"
            reason = f"Balanced state. Optimal for learning."
            action = "Absorb new information and build skills."
        
        # Apply behavior modification based on structured memories
        behavior_modification = self.behavior.modify_decision(decision, decision)
        
        return {
            "decision": decision,
            "reason": reason,
            "action": action,
            "metrics": {
                "avg_priority": round(avg_priority, 2),
                "avg_emotion_score": round(avg_emotion, 2),
                "total_memories": len(entries)
            },
            "recent_context": [e["content"][:50] + "..." for e in recent_entries],
            "description": DECISION_STATES.get(decision, ""),
            "confidence": min(0.95, 0.5 + (avg_priority / 10)),
            "memory_directives": behavior_modification.get("final_directive", {}).get("directives", "")
        }
    
    def get_focus_target(self):
        """Identify what you should focus on right now."""
        high_priority = self.memory.get_high_priority(1)
        
        if high_priority:
            target = high_priority[0]
            return {
                "target": target["content"],
                "priority": target["priority"],
                "emotion": target["emotion"],
                "reason": f"Highest priority item: {target['context']}"
            }
        
        return {"target": "No priority target set", "priority": 0, "reason": "Log a high-priority memory."}
    
    def get_behavioral_rules(self):
        """Get full behavior ruleset from structured memories."""
        return self.behavior.get_full_behavior_ruleset()
