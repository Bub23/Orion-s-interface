import json
import os
from datetime import datetime
from pathlib import Path
from config import MEMORY_FILE, DATA_DIR, EMOTIONS

class MemoryStore:
    """Persistent local memory with emotion and priority scoring."""
    
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.memories = self._load()
    
    def _load(self):
        """Load memory from disk."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {"entries": [], "metadata": {"created": datetime.now().isoformat(), "version": "1.0"}}
    
    def _save(self):
        """Save memory to disk."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def add_entry(self, content, emotion="calm", priority=5, context=""):
        """
        Add a memory entry with emotion and priority scoring.
        
        emotion: one of the EMOTIONS keys
        priority: 1-10 scale
        context: additional metadata
        """
        emotion_score = EMOTIONS.get(emotion, 5)
        
        entry = {
            "id": len(self.memories["entries"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "emotion": emotion,
            "emotion_score": emotion_score,
            "priority": priority,
            "context": context,
            "tags": [],
            "accessed_count": 0
        }
        
        self.memories["entries"].append(entry)
        self._save()
        return entry
    
    def search(self, query, limit=5):
        """Search memories by keyword."""
        results = []
        query_lower = query.lower()
        
        for entry in self.memories["entries"]:
            if query_lower in entry["content"].lower() or query_lower in entry["context"].lower():
                results.append(entry)
        
        return results[:limit]
    
    def get_high_priority(self, limit=5):
        """Get high-priority memories."""
        sorted_entries = sorted(
            self.memories["entries"],
            key=lambda x: (x["priority"], x["emotion_score"]),
            reverse=True
        )
        return sorted_entries[:limit]
    
    def get_recent(self, limit=5):
        """Get most recent memories."""
        sorted_entries = sorted(
            self.memories["entries"],
            key=lambda x: x["timestamp"],
            reverse=True
        )
        return sorted_entries[:limit]
    
    def get_all(self):
        """Get all memories."""
        return self.memories["entries"]
    
    def tag_entry(self, entry_id, tag):
        """Add a tag to a memory entry."""
        for entry in self.memories["entries"]:
            if entry["id"] == entry_id:
                if tag not in entry["tags"]:
                    entry["tags"].append(tag)
                self._save()
                return entry
        return None
    
    def delete_entry(self, entry_id):
        """Delete a memory entry."""
        self.memories["entries"] = [e for e in self.memories["entries"] if e["id"] != entry_id]
        self._save()
        return True
    
    def get_summary(self):
        """Get memory statistics."""
        entries = self.memories["entries"]
        if not entries:
            return {"total_entries": 0, "avg_priority": 0, "avg_emotion_score": 0}
        
        avg_priority = sum(e["priority"] for e in entries) / len(entries)
        avg_emotion = sum(e["emotion_score"] for e in entries) / len(entries)
        
        return {
            "total_entries": len(entries),
            "avg_priority": round(avg_priority, 2),
            "avg_emotion_score": round(avg_emotion, 2),
            "most_recent": entries[-1]["timestamp"] if entries else None
        }
