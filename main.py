#!/usr/bin/env python3
import sys
from pathlib import Path
from ai_interface import AIInterface

def main():
    ai = AIInterface()
    
    print("\n=== Local AI System ===")
    print("Commands:")
    print("  'import <filepath>' - Import ChatGPT export")
    print("  'stats' - Show memory stats")
    print("  'quit' - Exit")
    print("  Or just type to chat!\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                sys.exit(0)
            
            if user_input.lower() == "stats":
                stats = ai.get_stats()
                print(f"\nMemory Stats: {stats}\n")
                continue
            
            if user_input.lower().startswith("import "):
                filepath = user_input[7:].strip()
                result = ai.import_chatgpt_history(filepath)
                print(f"✓ {result}\n")
                continue
            
            # Regular chat
            print("\nAI: Processing...")
            response = ai.chat(user_input)
            print(f"AI: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
