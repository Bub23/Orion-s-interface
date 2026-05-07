from flask import Flask, render_template, request, jsonify
from memory.structured_memory import StructuredMemory
import json

class MemoryImporterAPI:
    """API for bulk importing memories."""
    
    def __init__(self, structured_memory):
        self.memory = structured_memory
    
    def import_batch(self, memories_text):
        """Import multiple memories from formatted text."""
        # Split by memory blocks (separated by blank lines with ---)
        blocks = memories_text.split('\n---\n')
        
        results = []
        for block in blocks:
            if not block.strip():
                continue
            
            try:
                parsed = self.memory.parse_memory_block(block)
                result = self.memory.add_memory(parsed)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        
        return {
            "total_imported": len([r for r in results if r.get("success")]),
            "total_failed": len([r for r in results if r.get("error")]),
            "results": results
        }
    
    def import_json(self, json_data):
        """Import memories from JSON format."""
        try:
            memories = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            if not isinstance(memories, list):
                memories = [memories]
            
            results = []
            for mem in memories:
                result = self.memory.add_memory(mem)
                results.append(result)
            
            return {
                "total_imported": len([r for r in results if r.get("success")]),
                "total_failed": len([r for r in results if r.get("error")]),
                "results": results
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_import_template(self):
        """Get template for memory format."""
        template = """[MEMORY_ID]: ID_001_EXAMPLE

[TYPE]: identity

[TITLE]: Your Title Here

[MEMORY]:
What you want to remember

[EMOTION]:
pride, drive, motivation

[WHY IT MATTERS]:
How this affects decisions

[ORION DIRECTIVE]:
What Orion should do because of this

[PRIORITY]: 5

[TAGS]: keyword, keyword, keyword

---

[MEMORY_ID]: ID_002_EXAMPLE

[TYPE]: mission

[TITLE]: Your Mission

[MEMORY]:
What you're building

[EMOTION]:
drive

[WHY IT MATTERS]:
Core motivation

[ORION DIRECTIVE]:
Always push toward this goal

[PRIORITY]: 5

[TAGS]: mission, goals
"""
        return template
