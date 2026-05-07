import sqlite3
import os
from ai_interface import AIInterface

DB_PATH = "database/orion.db"

class HookGenerator:
    """Viral hook generator with AI pattern learning"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.ai = AIInterface()
        
        # Hook patterns that trigger virality
        self.hook_patterns = {
            "curiosity_gap": [
                "They told me this would never work...",
                "Nobody talks about this...",
                "Wait until you see what happens next...",
            ],
            "shock_statement": [
                "I lost everything in 24 hours...",
                "This AI just replaced 3 jobs in 10 seconds...",
                "You've been lied to about this...",
            ],
            "outlaw_tension": [
                "This is what they don't want you to know...",
                "Raw truth incoming...",
                "This will make you uncomfortable...",
            ],
            "authority_flip": [
                "A $0 startup just beat billion-dollar companies...",
                "The CEO admits they were wrong...",
                "This changes everything...",
            ]
        }
    
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_hooks_from_content(self, content_id, content_text, num_hooks=5):
        """
        Generate 5 viral hooks from content using AI + pattern learning
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        hooks = []
        
        for pattern_type, patterns in self.hook_patterns.items():
            for base_hook in patterns[:2]:  # Use 2 patterns per type
                # Generate AI variation
                prompt = f"""
You are a viral content expert. Create a hook that:
- Starts with: "{base_hook}"
- Relates to: "{content_text}"
- Is 1 sentence max
- Creates curiosity gap or shock
- Makes someone stop scrolling

Output ONLY the hook, nothing else:
"""
                
                try:
                    ai_hook = self.ai.chat(prompt)
                except:
                    ai_hook = base_hook
                
                hook_obj = {
                    "text": ai_hook[:100],  # Cap at 100 chars
                    "type": pattern_type,
                    "pattern_base": base_hook
                }
                
                # Store hook
                cursor.execute("""
                    INSERT INTO hooks (content_id, hook_text, hook_type)
                    VALUES (?, ?, ?)
                """, (content_id, hook_obj["text"], pattern_type))
                
                conn.commit()
                hook_id = cursor.lastrowid
                
                hook_obj["hook_id"] = hook_id
                hooks.append(hook_obj)
        
        conn.close()
        
        return {
            "content_id": content_id,
            "hooks": hooks[:num_hooks],
            "total_generated": len(hooks)
        }
    
    def rank_hooks_by_performance(self, content_id):
        """
        Rank all hooks for this content by performance score
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM hooks WHERE content_id = ?
            ORDER BY performance_score DESC
        """, (content_id,))
        
        hooks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return hooks
    
    def mark_hook_high_performer(self, hook_id):
        """
        When a hook "kills it", tag it and trigger learning
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get hook details
        cursor.execute("SELECT * FROM hooks WHERE id = ?", (hook_id,))
        hook = cursor.fetchone()
        
        if not hook:
            return {"error": "Hook not found"}
        
        # Mark as high performer
        cursor.execute("""
            UPDATE hooks SET is_high_performer = 1, times_used = times_used + 1
            WHERE id = ?
        """, (hook_id,))
        
        # Update pattern success rate
        cursor.execute("""
            UPDATE hook_patterns SET
            times_succeeded = times_succeeded + 1,
            success_rate = CAST(times_succeeded AS FLOAT) / times_tested
            WHERE pattern_type = ?
        """, (hook["hook_type"],))
        
        conn.commit()
        conn.close()
        
        return {
            "hook_id": hook_id,
            "status": "marked_high_performer",
            "times_used": hook["times_used"] + 1
        }
    
    def auto_generate_hook_variations(self, hook_id, num_variations=5):
        """
        ACTION 1 — AUTO REPLICATE
        When a hook kills it, generate 5 variations with same structure
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        # Get original hook
        cursor.execute("SELECT * FROM hooks WHERE id = ?", (hook_id,))
        original = cursor.fetchone()
        
        if not original:
            return {"error": "Hook not found"}
        
        variations = []
        
        # Generate emotional angle variations
        prompt = f"""
You are a viral hook master. The following hook is a high performer:
"{original['hook_text']}"

Create {num_variations} variations with the SAME structure but DIFFERENT emotional angles:
- 1 version for curiosity
- 1 version for urgency
- 1 version for fear
- 1 version for aspiration
- 1 version for rebellion

Format: Output each on a new line, numbered 1-5. No explanations.
"""
        
        try:
            response = self.ai.chat(prompt)
            variation_lines = response.strip().split('\n')
            
            for i, variation in enumerate(variation_lines[:num_variations]):
                # Clean up numbering
                variation_text = variation.replace(f"{i+1}.", "").strip()[:100]
                
                cursor.execute("""
                    INSERT INTO hooks (content_id, hook_text, hook_type)
                    VALUES (?, ?, ?)
                """, (original['content_id'], variation_text, f"{original['hook_type']}_variation"))
                
                conn.commit()
                var_id = cursor.lastrowid
                
                variations.append({
                    "variation_id": var_id,
                    "text": variation_text,
                    "emotional_angle": ["curiosity", "urgency", "fear", "aspiration", "rebellion"][i]
                })
        except:
            pass
        
        conn.close()
        
        return {
            "original_hook_id": hook_id,
            "variations_created": len(variations),
            "variations": variations
        }
    
    def get_top_performing_hooks(self, limit=10):
        """
        Get the highest performing hooks across all content
        Used by remix engine to inject into new content
        """
        conn = self.get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM hooks
            WHERE is_high_performer = 1
            ORDER BY performance_score DESC
            LIMIT ?
        """, (limit,))
        
        top_hooks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return top_hooks

