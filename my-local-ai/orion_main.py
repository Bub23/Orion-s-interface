import sys
from datetime import datetime
from memory.memory_store import MemoryStore
from engines.decision_engine import DecisionEngine
from engines.legacy_engine import LegacyEngine
from config import EMOTIONS

class OrionOS:
    """Main CLI interface for Orion OS."""
    
    def __init__(self):
        self.memory = MemoryStore()
        self.decision = DecisionEngine(self.memory)
        self.legacy = LegacyEngine(self.memory)
    
    def print_header(self):
        print("\n" + "="*60)
        print("🧠 ORION OS - Decision Engine + Memory System")
        print("="*60 + "\n")
    
    def print_menu(self):
        print("1. 📝 Log Memory")
        print("2. 📖 View Memories")
        print("3. 🎯 Ask Decision Engine")
        print("4. 🔥 Generate Legacy Content")
        print("5. 🔍 Search Memories")
        print("6. 📊 Memory Stats")
        print("7. ❌ Delete Memory")
        print("8. 🚪 Exit")
        print()
    
    def log_memory(self):
        """Log a new memory entry."""
        print("\n--- Log a Memory ---")
        content = input("What's on your mind? > ").strip()
        
        if not content:
            print("Memory cannot be empty.")
            return
        
        print(f"\nEmotions: {', '.join(EMOTIONS.keys())}")
        emotion = input("Current emotion? (default: calm) > ").strip().lower()
        
        if emotion not in EMOTIONS:
            emotion = "calm"
        
        priority = input("Priority (1-10, default: 5) > ").strip()
        try:
            priority = int(priority) if priority else 5
            priority = max(1, min(10, priority))
        except ValueError:
            priority = 5
        
        context = input("Context/Tags (optional) > ").strip()
        
        entry = self.memory.add_entry(content, emotion, priority, context)
        print(f"✓ Memory saved (ID: {entry['id']})")
    
    def view_memories(self):
        """Display all memories."""
        print("\n--- Your Memories ---")
        entries = self.memory.get_all()
        
        if not entries:
            print("No memories yet. Start logging!")
            return
        
        for entry in entries:
            print(f"\n[{entry['id']}] {entry['content'][:60]}")
            print(f"    Emotion: {entry['emotion']} | Priority: {entry['priority']}/10")
            print(f"    Context: {entry['context']}")
            print(f"    Time: {entry['timestamp'][:10]}")
    
    def ask_decision_engine(self):
        """Run decision analysis."""
        print("\n--- Decision Engine Analysis ---")
        result = self.decision.analyze()
        
        print(f"\n🎯 DECISION: {result['decision']}")
        print(f"📊 Reason: {result['reason']}")
        print(f"⚡ Action: {result['action']}")
        print(f"\nMetrics:")
        for key, value in result['metrics'].items():
            print(f"  • {key}: {value}")
        
        print(f"\nFocus Target:")
        focus = self.decision.get_focus_target()
        print(f"  • {focus['target']}")
        print(f"  • Priority: {focus['priority']}/10")
    
    def generate_legacy_content(self):
        """Generate content from memories."""
        print("\n--- Generate Legacy Content ---")
        entries = self.memory.get_all()
        
        if not entries:
            print("No memories to generate from.")
            return
        
        high_priority = self.memory.get_high_priority(3)
        content = self.legacy.generate_from_memories(high_priority)
        
        print(f"\n🎯 Hook: {content['hook']}")
        print(f"\n📖 Story: {content['story']}")
        print(f"\n💪 Mantra: {content['mantra']}")
        print(f"\n🏷️  Brand Line: {content['brand_line']}")
    
    def search_memories(self):
        """Search for specific memories."""
        print("\n--- Search Memories ---")
        query = input("Search term > ").strip()
        
        if not query:
            return
        
        results = self.memory.search(query)
        
        if not results:
            print("No memories found.")
            return
        
        print(f"\nFound {len(results)} result(s):")
        for entry in results:
            print(f"\n[{entry['id']}] {entry['content']}")
            print(f"    Emotion: {entry['emotion']} | Priority: {entry['priority']}")
    
    def memory_stats(self):
        """Display memory statistics."""
        print("\n--- Memory Statistics ---")
        stats = self.memory.get_summary()
        
        for key, value in stats.items():
            print(f"  • {key}: {value}")
    
    def delete_memory(self):
        """Delete a memory entry."""
        print("\n--- Delete Memory ---")
        try:
            entry_id = int(input("Memory ID to delete > "))
            if self.memory.delete_entry(entry_id):
                print(f"✓ Memory {entry_id} deleted.")
            else:
                print("Memory not found.")
        except ValueError:
            print("Invalid ID.")
    
    def run(self):
        """Main loop."""
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("Choose > ").strip()
            
            if choice == "1":
                self.log_memory()
            elif choice == "2":
                self.view_memories()
            elif choice == "3":
                self.ask_decision_engine()
            elif choice == "4":
                self.generate_legacy_content()
            elif choice == "5":
                self.search_memories()
            elif choice == "6":
                self.memory_stats()
            elif choice == "7":
                self.delete_memory()
            elif choice == "8":
                print("\n👋 Orion OS shutting down...\n")
                break
            else:
                print("Invalid choice. Try again.")

if __name__ == "__main__":
    os = OrionOS()
    os.run()
