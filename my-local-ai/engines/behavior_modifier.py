from memory.structured_memory import StructuredMemory

class BehaviorModifier:
    """Uses memory directives to modify behavior and decisions."""
    
    def __init__(self):
        self.structured_memory = StructuredMemory()
    
    def get_identity_filters(self):
        """Get identity-based behavior filters."""
        identity = self.structured_memory.get_identity_core()
        
        if not identity:
            return {"style": "neutral", "directives": []}
        
        return {
            "style": identity["title"],
            "core_memory": identity["memory"],
            "directive": identity["orion_directive"],
            "emotions": identity["emotion"]
        }
    
    def get_mission_filters(self):
        """Get mission-based behavior filters."""
        mission = self.structured_memory.get_mission()
        
        if not mission:
            return {"mission": None, "directive": None}
        
        return {
            "mission": mission["memory"],
            "directive": mission["orion_directive"],
            "priority_override": mission["priority"]
        }
    
    def get_applicable_rules(self, context):
        """Get rules that apply to current context."""
        rules = self.structured_memory.get_by_type("rule")
        applicable = []
        
        for rule in rules:
            # Match rules to context
            if any(tag.lower() in context.lower() for tag in rule["tags"]):
                applicable.append({
                    "rule": rule["title"],
                    "directive": rule["orion_directive"],
                    "priority": rule["priority"]
                })
        
        return sorted(applicable, key=lambda x: -x["priority"])
    
    def modify_decision(self, decision_context, decision_state):
        """
        Modify a decision based on all active memories.
        
        Returns: modified decision with memory influence applied
        """
        identity_filter = self.get_identity_filters()
        mission_filter = self.get_mission_filters()
        rules = self.get_applicable_rules(decision_context)
        
        modification = {
            "original_decision": decision_state,
            "identity_influence": identity_filter.get("directive", ""),
            "mission_influence": mission_filter.get("directive", ""),
            "applicable_rules": rules,
            "final_directive": self._synthesize_directives(
                identity_filter, mission_filter, rules, decision_state
            )
        }
        
        return modification
    
    def _synthesize_directives(self, identity, mission, rules, decision):
        """Combine all directives into final behavior instruction."""
        directives = []
        
        # Identity is core—always apply
        if identity.get("directive"):
            directives.append(f"[IDENTITY] {identity['directive']}")
        
        # Mission overrides decisions
        if mission.get("directive"):
            directives.append(f"[MISSION] {mission['directive']}")
        
        # Rules apply to specific contexts
        for rule in rules:
            directives.append(f"[RULE] {rule['directive']}")
        
        synthesized = "\n".join(directives)
        
        return {
            "directives": synthesized,
            "decision_modified": True,
            "reason": f"Modified {decision} using {len(directives)} active memory directives"
        }
    
    def get_memory_context_for_query(self, query):
        """Get all relevant memories for a query with their directives."""
        relevant = self.structured_memory.get_relevant_to_query(query)
        
        context = {
            "query": query,
            "relevant_memories": [],
            "combined_directives": []
        }
        
        for mem in relevant:
            context["relevant_memories"].append({
                "id": mem["memory_id"],
                "type": mem["type"],
                "title": mem["title"],
                "memory": mem["memory"],
                "priority": mem["priority"]
            })
            
            if mem["orion_directive"]:
                context["combined_directives"].append(mem["orion_directive"])
        
        return context
    
    def get_full_behavior_ruleset(self):
        """Get complete ruleset for AI/content generation."""
        identity = self.structured_memory.get_identity_core()
        mission = self.structured_memory.get_mission()
        all_rules = self.structured_memory.get_by_type("rule")
        all_directives = self.structured_memory.get_directives()
        
        ruleset = {
            "identity": identity["memory"] if identity else None,
            "mission": mission["memory"] if mission else None,
            "rules": [r["orion_directive"] for r in all_rules if r["orion_directive"]],
            "all_directives": all_directives,
            "global_behavior": {
                "priority_order": [
                    "identity memories",
                    "mission memories",
                    "rule memories",
                    "other memories"
                ],
                "behavior_override": "Higher priority memories always override lower priority decisions"
            }
        }
        
        return ruleset
