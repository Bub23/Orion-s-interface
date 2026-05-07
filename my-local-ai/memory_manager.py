import json
import os
from datetime import datetime
from pathlib import Path

class MemoryManager:
    """Handles ChatGPT conversation export and memory storage."""
    
    def __init__(self, memory_dir="./memories"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.memories_file = self.memory_dir / "memories.json"
        self.memories = self._load_memories()
    
    def _load_memories(self):
        """Load existing memories from disk."""
        if self.memories_file.exists():
            with open(self.memories_file, 'r') as f:
                return json.load(f)
        return {"conversations": [], "facts": []}
    
    def import_chatgpt_export(self, export_file):
        """Import ChatGPT conversation export."""
        with open(export_file, 'r') as f:
            chatgpt_data = json.load(f)
        
        # Parse ChatGPT format
        for conversation in chatgpt_data:
            conv_record = {
                "id": conversation.get("id"),
                "title": conversation.get("title"),
                "messages": [],
                "imported_at": datetime.now().isoformat()
            }
            
            # Extract messages
            if "mapping" in conversation:
                for msg_id, msg_data in conversation["mapping"].items():
                    if msg_data.get("message"):
                        msg = msg_data["message"]
                        conv_record["messages"].append({
                            "role": msg.get("author", {}).get("role"),
                            "content": msg.get("content", {}).get("parts", [""])[0]
                        })
            
            self.memories["conversations"].append(conv_record)
        
        self._save_memories()
        return len(self.memories["conversations"])
    
    def add_memory(self, fact_type, content):
        """Add a new memory or fact."""
        self.memories["facts"].append({
            "type": fact_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_memories()
    
    def get_relevant_memories(self, query, limit=5):
        """Retrieve relevant past conversations (basic keyword matching)."""
        results = []
        query_lower = query.lower()
        
        for conv in self.memories["conversations"]:
            for msg in conv["messages"]:
                if query_lower in msg.get("content", "").lower():
                    results.append(msg["content"])
                    if len(results) >= limit:
                        return results
        
        return results
    
    def _save_memories(self):
        """Save memories to disk."""
        with open(self.memories_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def get_summary(self):
        """Get memory stats."""
        return {
            "total_conversations": len(self.memories["conversations"]),
            "total_facts": len(self.memories["facts"]),
            "memory_file_size": os.path.getsize(self.memories_file) if self.memories_file.exists() else 0
        }

if __name__ == "__main__":
    mm = MemoryManager()
    print(mm.get_summary())
