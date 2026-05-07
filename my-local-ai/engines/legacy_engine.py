from config import LEGACY_TEMPLATES

class LegacyEngine:
    """Generates actionable content from memories."""
    
    def __init__(self, memory_store):
        self.memory = memory_store
    
    def generate_hook(self, memory_entry):
        """Generate a compelling hook from a memory."""
        content = memory_entry.get("content", "")
        emotion = memory_entry.get("emotion", "")
        
        theme = content.split()[0] if content else "idea"
        action = "evolve" if emotion in ["drive", "focus"] else "transform"
        
        hook = LEGACY_TEMPLATES["hook"].format(memory_theme=theme, action=action)
        return hook
    
    def generate_story(self, start_entry, current_state, vision):
        """Generate a narrative arc from memory."""
        emotion_context = start_entry.get("emotion", "uncertain")
        
        story = LEGACY_TEMPLATES["story"].format(
            emotion_context=emotion_context,
            current_state=current_state,
            vision=vision
        )
        return story
    
    def generate_mantra(self, identity, core_action, outcome):
        """Generate a personal mantra."""
        mantra = LEGACY_TEMPLATES["mantra"].format(
            identity=identity,
            core_action=core_action,
            outcome=outcome
        )
        return mantra
    
    def generate_brand_line(self, subject, verb, context, call_to_action):
        """Generate a brand/positioning line."""
        line = LEGACY_TEMPLATES["brand_line"].format(
            subject=subject,
            verb=verb,
            context=context,
            call_to_action=call_to_action
        )
        return line
    
    def generate_from_memories(self, memory_entries):
        """Generate comprehensive content suite from multiple memories."""
        if not memory_entries:
            return {"error": "No memories to generate from"}
        
        primary = memory_entries[0]
        
        output = {
            "hook": self.generate_hook(primary),
            "story": self.generate_story(
                primary,
                f"Building {len(memory_entries)} things",
                "Become unstoppable"
            ),
            "mantra": self.generate_mantra(
                "Builder",
                "create systems",
                "that compound"
            ),
            "brand_line": self.generate_brand_line(
                primary.get("content", "Orion")[:10],
                "evolves",
                "one memory at a time",
                "Build your system"
            ),
            "memory_count": len(memory_entries),
            "generated_at": str(memory_entries[0].get("timestamp", ""))
        }
        
        return output
