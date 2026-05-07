import re
from datetime import datetime


class AGICore:
    """Agentic cognition layer for Orion.

    This does not claim artificial general intelligence. It gives Orion a
    practical cognitive loop: understand, plan, choose tools, respond, reflect,
    and file useful memory.
    """

    INTENT_KEYWORDS = {
        "build": ["build", "create", "make", "code", "app", "system", "automate", "fix", "improve"],
        "research": ["search", "find", "look up", "latest", "current", "who is", "what is", "tell me about"],
        "browse": ["browse", "visit", "go to", "open", "extract", "check site", "website"],
        "image": ["image", "picture", "draw", "logo", "thumbnail", "cover art", "generate art"],
        "strategy": ["strategy", "plan", "scale", "business", "revenue", "investor", "growth"],
        "memory": ["remember", "my name", "i am", "i'm", "i like", "i need", "i want", "always", "never"],
        "emotional_support": ["stuck", "overwhelmed", "angry", "sad", "worried", "scared", "tired", "frustrated"],
        "creative": ["song", "lyrics", "rap", "script", "story", "hook", "brand", "content"],
    }

    TOOL_BY_INTENT = {
        "research": "web_search",
        "browse": "browser",
        "image": "image_generation",
        "strategy": "decision_engine",
        "build": "execution_planner",
        "memory": "memory_writer",
        "creative": "personality_modes",
    }

    MEMORY_PATTERNS = [
        (r"\bmy goal is\b|\bi want to\b|\bi need to\b", "mission", 4),
        (r"\bi am\b|\bi'm\b|\bmy name is\b", "identity", 4),
        (r"\bi like\b|\bi prefer\b|\bi hate\b|\bi believe\b", "preference", 3),
        (r"\balways\b|\bnever\b|\bdon't let me\b", "rule", 5),
        (r"\bi learned\b|\bthat taught me\b|\bi remember\b", "experience", 3),
        (r"\bi can\b|\bi know how to\b|\bi'm good at\b", "skill", 3),
    ]

    def think(self, user_message, memories=None, recent_messages=None, learning_stats=None, decision_state=None):
        """Return Orion's working model for this turn."""
        memories = memories or []
        recent_messages = recent_messages or []
        learning_stats = learning_stats or {}
        decision_state = decision_state or {}

        intents = self.detect_intents(user_message)
        tools = self.select_tools(intents, user_message)
        plan = self.make_plan(user_message, intents, tools, memories, recent_messages)
        risks = self.detect_risks(user_message, tools)
        memory_candidates = self.extract_memory_candidates(user_message)

        return {
            "timestamp": datetime.now().isoformat(),
            "primary_intent": intents[0]["intent"] if intents else "general",
            "intents": intents,
            "tools": tools,
            "plan": plan,
            "risks": risks,
            "memory_candidates": memory_candidates,
            "context_pressure": {
                "relevant_memories": len(memories),
                "recent_messages": len(recent_messages),
                "learning_interactions": learning_stats.get("total_interactions", 0),
                "decision": decision_state.get("decision", "UNKNOWN"),
            },
            "briefing": self.build_briefing(intents, tools, plan, risks, memory_candidates, decision_state),
        }

    def detect_intents(self, message):
        """Classify the message into weighted intents."""
        text = message.lower()
        matches = []

        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            hits = []
            for keyword in keywords:
                if keyword in text:
                    score += 2 if " " in keyword else 1
                    hits.append(keyword)
            if score:
                matches.append({"intent": intent, "score": score, "signals": hits[:5]})

        if not matches:
            matches.append({"intent": "general", "score": 1, "signals": []})

        return sorted(matches, key=lambda item: item["score"], reverse=True)

    def select_tools(self, intents, message):
        """Choose internal tools/capabilities for this turn."""
        text = message.lower()
        tools = []

        for item in intents:
            tool = self.TOOL_BY_INTENT.get(item["intent"])
            if tool and tool not in tools:
                tools.append(tool)

        if any(word in text for word in ["remember", "always", "never", "my goal", "i am", "i'm"]):
            if "memory_writer" not in tools:
                tools.append("memory_writer")

        if "self_check" not in tools:
            tools.append("self_check")

        return tools

    def make_plan(self, message, intents, tools, memories, recent_messages):
        """Create a small execution plan the model can follow."""
        primary = intents[0]["intent"] if intents else "general"
        plan = [
            "Parse the user's real objective and constraints.",
            "Use relevant long-term memories and recent conversation context.",
        ]

        if "web_search" in tools:
            plan.append("Gather current facts before answering anything time-sensitive.")
        if "browser" in tools:
            plan.append("Browse or extract page data, then summarize only verified observations.")
        if "image_generation" in tools:
            plan.append("Convert visual intent into a concrete image prompt or generated asset.")
        if "execution_planner" in tools:
            plan.append("Break the work into direct implementation steps and complete the highest-value step.")
        if primary == "strategy":
            plan.append("Return a measurable plan with priorities, next actions, and tradeoffs.")
        if "memory_writer" in tools:
            plan.append("File durable personal facts only when they are explicit and useful.")

        plan.append("Run a self-check for accuracy, completeness, and unsafe assumptions before finalizing.")
        return plan

    def detect_risks(self, message, tools):
        """Flag places where Orion should slow down or verify."""
        text = message.lower()
        risks = []

        if any(word in text for word in ["latest", "current", "today", "now", "price", "law", "news"]):
            risks.append("time_sensitive")
        if any(word in text for word in ["delete", "password", "token", "private key", "secret"]):
            risks.append("sensitive_or_destructive")
        if "browser" in tools:
            risks.append("external_site_variability")
        if len(message) < 8:
            risks.append("underspecified_request")

        return risks

    def extract_memory_candidates(self, message):
        """Find explicit facts worth storing."""
        text = message.strip()
        candidates = []

        for pattern, mem_type, priority in self.MEMORY_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                candidates.append({
                    "type": mem_type,
                    "title": text[:60],
                    "memory": text,
                    "priority": priority,
                    "tags": ["agi-core", "conversation"],
                    "why_it_matters": "Explicitly stated by the user during conversation.",
                })

        return candidates

    def build_briefing(self, intents, tools, plan, risks, memory_candidates, decision_state):
        """Render cognition state for the LLM prompt."""
        intent_text = ", ".join(f"{i['intent']}({i['score']})" for i in intents)
        tool_text = ", ".join(tools) if tools else "none"
        risk_text = ", ".join(risks) if risks else "none"
        decision_text = decision_state.get("decision", "UNKNOWN")

        plan_text = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(plan))

        return (
            "[ORION COGNITIVE LOOP]\n"
            f"Intent map: {intent_text}\n"
            f"Selected tools: {tool_text}\n"
            f"Decision state: {decision_text}\n"
            f"Risks to watch: {risk_text}\n"
            f"Memory candidates: {len(memory_candidates)}\n"
            "Working plan:\n"
            f"{plan_text}"
        )

    def reflect(self, user_message, response_text, cognition):
        """Score the response and produce a small reflection record."""
        text = response_text or ""
        issues = []

        if len(text.strip()) < 20:
            issues.append("response_too_short")
        if cognition.get("risks") and "time_sensitive" in cognition["risks"]:
            lower = text.lower()
            if not any(word in lower for word in ["checked", "current", "as of", "verify", "source"]):
                issues.append("time_sensitive_answer_needs_verification_language")
        if cognition.get("primary_intent") == "build" and not any(word in text.lower() for word in ["done", "built", "step", "file", "implement"]):
            issues.append("build_request_may_need_concrete_execution")

        score = max(0.1, 1.0 - (0.2 * len(issues)))
        return {
            "timestamp": datetime.now().isoformat(),
            "primary_intent": cognition.get("primary_intent", "general"),
            "score": round(score, 2),
            "issues": issues,
            "response_chars": len(text),
        }
