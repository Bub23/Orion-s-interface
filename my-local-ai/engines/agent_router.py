class AgentRouter:
    """
    Simple Orion decision layer:
    Turns user text → intent → action
    """

    def __init__(self):
        self.intents = {
            "youtube_title": ["title", "youtube", "viral", "video title"],
            "music_idea": ["song", "beat", "hook", "country rap", "lyrics"],
            "memory": ["remember", "save", "note"],
            "general": []
        }

    def detect_intent(self, text: str):
        text_lower = text.lower()

        for intent, keywords in self.intents.items():
            if any(k in text_lower for k in keywords):
                return intent

        return "general"

    def route(self, intent: str, llm_output: str):
        """
        Future expansion point:
        You can plug YouTube / Facebook / Spotify here.
        """

        if intent == "youtube_title":
            return {
                "type": "content",
                "platform": "youtube",
                "output": llm_output
            }

        if intent == "music_idea":
            return {
                "type": "music",
                "output": llm_output
            }

        if intent == "memory":
            return {
                "type": "memory",
                "output": llm_output
            }

        return {
            "type": "chat",
            "output": llm_output
        }