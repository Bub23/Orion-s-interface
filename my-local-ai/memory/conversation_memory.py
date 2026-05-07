import json
import os
from datetime import datetime
from config import DATA_DIR

class ConversationMemory:
    """Tracks conversation history within a session."""
    
    def __init__(self):
        self.history_file = os.path.join(DATA_DIR, "conversation_history.json")
        self.history = self._load()
    
    def _load(self):
        """Load conversation history."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {"conversations": []}
        return {"conversations": []}
    
    def _save(self):
        """Save conversation history."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def start_conversation(self):
        """Start a new conversation session."""
        session = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "summary": ""
        }
        self.history["conversations"].append(session)
        self._save()
        return session["id"]
    
    def add_message(self, conversation_id, role, content):
        """Add a message to conversation."""
        for conv in self.history["conversations"]:
            if conv["id"] == conversation_id:
                conv["messages"].append({
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                self._save()
                return
    
    def get_conversation_context(self, conversation_id, limit=10):
        """Get recent messages from conversation for context."""
        for conv in self.history["conversations"]:
            if conv["id"] == conversation_id:
                messages = conv["messages"][-limit:]
                return [f"{m['role']}: {m['content']}" for m in messages]
        return []
    
    def summarize_conversation(self, conversation_id):
        """Auto-summarize a conversation for memory filing."""
        for conv in self.history["conversations"]:
            if conv["id"] == conversation_id:
                messages = conv["messages"]
                if len(messages) > 5:
                    # Extract key points from conversation
                    summary = f"Conversation with {len(messages)} messages. Topics discussed: "
                    topics = set()
                    
                    for msg in messages:
                        if "goal" in msg["content"].lower():
                            topics.add("goals")
                        if "build" in msg["content"].lower():
                            topics.add("building")
                        if "learn" in msg["content"].lower():
                            topics.add("learning")
                        if "feeling" in msg["content"].lower():
                            topics.add("emotions")
                    
                    summary += ", ".join(topics) if topics else "general"
                    conv["summary"] = summary
                    self._save()
                    return summary
        return None
    
    def get_all_conversations(self):
        """Get list of all conversations."""
        return self.history["conversations"]
