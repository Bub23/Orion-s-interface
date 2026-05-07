import json
import os
import re
from datetime import datetime
from pathlib import Path
from config import DATA_DIR
from memory.persistence import PersistenceManager

class StructuredMemory:
    """Parse and store structured memory in the directive format."""
    
    MEMORY_TYPES = ["identity", "skill", "preference", "relationship", "mission", "rule", "experience"]
    EMOTIONS = ["anger", "pride", "pain", "love", "fear", "motivation", "calm", "drive"]
    
    def __init__(self):
        self.memory_file = os.path.join(DATA_DIR, "structured_memories.json")
        self.persistence = PersistenceManager()
        self.memories = self._load()
    
    def _load(self):
        """Load structured memories."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {"memories": [], "global_behavior_rules": []}
    
    def _save(self):
        """Save to disk and create backup."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memories, f, indent=2)
        
        # Auto-backup every save
        self.persistence.backup_memories(self.memories)
    
    def parse_memory_block(self, block_text):
        """Parse a memory block and return structured dict."""
        lines = block_text.strip().split('\n')
        memory = {}
        current_key = None
        current_value = []
        
        for line in lines:
            if line.startswith('[') and line.endswith(']:'):
                # Save previous key
                if current_key:
                    memory[current_key] = '\n'.join(current_value).strip()
                
                # Parse new key
                current_key = line[1:-2].lower().replace(' ', '_')
                current_value = []
            else:
                current_value.append(line)
        
        # Save last key
        if current_key:
            memory[current_key] = '\n'.join(current_value).strip()
        
        return memory
    
    def add_memory(self, parsed_memory):
        """Add a parsed memory to storage."""
        # Validate required fields
        required = ['memory_id', 'type', 'title', 'memory']
        if not all(k in parsed_memory for k in required):
            return {"error": f"Missing required fields. Need: {required}"}
        
        # Normalize type
        mem_type = parsed_memory.get('type', '').lower()
        if mem_type not in self.MEMORY_TYPES:
            return {"error": f"Invalid type. Must be one of: {self.MEMORY_TYPES}"}
        
        # Build entry
        entry = {
            "memory_id": parsed_memory.get('memory_id') or self.next_memory_id("MEM"),
            "type": mem_type,
            "title": parsed_memory.get('title'),
            "memory": parsed_memory.get('memory'),
            "emotion": parsed_memory.get('emotion', '').split(', ') if parsed_memory.get('emotion') else [],
            "why_it_matters": parsed_memory.get('why_it_matters', ''),
            "orion_directive": parsed_memory.get('orion_directive', ''),
            "priority": int(parsed_memory.get('priority', 3)),
            "tags": [t.strip() for t in parsed_memory.get('tags', '').split(', ') if t.strip()],
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        self.memories["memories"].append(entry)
        self._save()
        return {"success": True, "memory_id": entry["memory_id"]}

    def next_memory_id(self, prefix="AUTO"):
        """Generate a durable memory id."""
        existing = {m.get("memory_id") for m in self.memories.get("memories", [])}
        counter = len(existing)
        while True:
            candidate = f"{prefix}_{datetime.now().strftime('%Y%m%d')}_{counter}"
            if candidate not in existing:
                return candidate
            counter += 1

    def add_auto_memory(self, mem_type, title, memory, priority=2, tags=None, why_it_matters=None, directive=""):
        """Add an automatically detected memory with duplicate protection."""
        normalized = self._normalize_text(memory)
        for existing in self.memories.get("memories", []):
            if self._normalize_text(existing.get("memory", "")) == normalized:
                return {"filed": False, "duplicate": True, "memory_id": existing.get("memory_id")}

        entry = {
            "memory_id": self.next_memory_id("AUTO"),
            "type": mem_type if mem_type in self.MEMORY_TYPES else "experience",
            "title": title[:80],
            "memory": memory,
            "emotion": [],
            "why_it_matters": why_it_matters or "Auto-filed from conversation",
            "orion_directive": directive,
            "priority": int(priority),
            "tags": tags or ["auto-filed", "conversation"],
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }

        self.memories["memories"].append(entry)
        self._save()
        return {"filed": True, "type": entry["type"], "preview": entry["title"], "memory_id": entry["memory_id"]}
    
    def get_by_priority(self, limit=10):
        """Get memories sorted by priority (highest first)."""
        sorted_mem = sorted(
            self.memories["memories"],
            key=lambda x: (-x["priority"], x["type"]),
        )
        return sorted_mem[:limit]
    
    def get_by_type(self, mem_type):
        """Get all memories of a specific type."""
        return [m for m in self.memories["memories"] if m["type"] == mem_type]
    
    def get_directives(self):
        """Get all ORION_DIRECTIVE entries (behavior-changing instructions)."""
        return [m["orion_directive"] for m in self.memories["memories"] if m["orion_directive"]]
    
    def get_identity_core(self):
        """Get core identity memory for behavior alignment."""
        identities = self.get_by_type("identity")
        return identities[0] if identities else None
    
    def get_mission(self):
        """Get mission memory to align decisions."""
        missions = self.get_by_type("mission")
        return missions[0] if missions else None
    
    def search_by_tag(self, tag):
        """Search memories by tag."""
        return [m for m in self.memories["memories"] if tag.lower() in [t.lower() for t in m["tags"]]]
    
    def get_relevant_to_query(self, query):
        """Get memories relevant to a query using weighted token scoring."""
        query_terms = self._tokenize(query)
        if not query_terms:
            return self.get_by_priority(5)

        scored = []
        
        for mem in self.memories["memories"]:
            haystack = " ".join([
                mem.get("title", ""),
                mem.get("memory", ""),
                " ".join(mem.get("tags", [])),
                mem.get("type", ""),
                mem.get("why_it_matters", ""),
            ])
            hay_terms = self._tokenize(haystack)
            overlap = query_terms.intersection(hay_terms)
            exact_bonus = 2 if query.lower() in haystack.lower() else 0
            score = (len(overlap) * 3) + exact_bonus + int(mem.get("priority", 1))

            if score > int(mem.get("priority", 1)):
                scored.append((score, mem))
        
        scored.sort(key=lambda item: (-item[0], -item[1].get("priority", 0)))

        results = []
        for _, mem in scored[:8]:
            mem["access_count"] = mem.get("access_count", 0) + 1
            results.append(mem)

        if results:
            self._save()

        return results

    def _tokenize(self, text):
        """Tokenize text into useful search terms."""
        stopwords = {
            "the", "and", "for", "with", "that", "this", "from", "you", "your",
            "what", "when", "where", "how", "why", "are", "was", "were", "have",
            "has", "had", "but", "not", "all", "can", "into", "about"
        }
        terms = re.findall(r"[a-z0-9']{3,}", text.lower())
        return {term for term in terms if term not in stopwords}

    def _normalize_text(self, text):
        """Normalize memory text for duplicate checks."""
        return " ".join(re.findall(r"[a-z0-9']+", text.lower()))
    
    def get_summary(self):
        """Get memory statistics."""
        memories = self.memories["memories"]
        type_counts = {}
        for mem in memories:
            type_counts[mem["type"]] = type_counts.get(mem["type"], 0) + 1
        
        return {
            "total_memories": len(memories),
            "by_type": type_counts,
            "avg_priority": round(sum(m["priority"] for m in memories) / len(memories), 2) if memories else 0
        }
