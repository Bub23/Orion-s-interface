#!/usr/bin/env python3
"""
Memory Importer - Paste your structured memories in the format and this tool will parse them.
"""

import sys
from memory.structured_memory import StructuredMemory

def print_header():
    print("\n" + "="*60)
    print("🧠 ORION MEMORY IMPORTER")
    print("="*60)
    print("\nPaste your memory blocks in this format:\n")
    print("[MEMORY_ID]: ID_123_NAME")
    print("[TYPE]: identity | skill | preference | relationship | mission | rule | experience")
    print("[TITLE]: Your Title")
    print("[MEMORY]: What happened / what is true")
    print("[EMOTION]: anger | pride | pain | love | fear | motivation")
    print("[WHY IT MATTERS]: What this affects")
    print("[ORION DIRECTIVE]: What I should DO differently")
    print("[PRIORITY]: 1-5")
    print("[TAGS]: keyword, keyword, keyword")
    print("\nType '---' on a new line to finish a memory block.")
    print("Type 'quit' to exit.\n")
    print("="*60 + "\n")

def get_memory_block():
    """Get a memory block from user input."""
    lines = []
    print("Paste memory block (end with '---' on its own line):")
    
    while True:
        try:
            line = input()
        except EOFError:
            break
        
        if line.strip() == "---":
            break
        lines.append(line)
    
    return "\n".join(lines)

def main():
    print_header()
    structured_mem = StructuredMemory()
    
    while True:
        command = input("\n1. Add Memory\n2. View Memories\n3. Get Directives\n4. Quit\n\nChoose > ").strip()
        
        if command == "1":
            block = get_memory_block()
            
            if not block.strip():
                print("Empty block. Skipping.")
                continue
            
            # Parse
            parsed = structured_mem.parse_memory_block(block)
            
            # Add
            result = structured_mem.add_memory(parsed)
            
            if result.get("success"):
                print(f"✓ Memory added: {result['memory_id']}")
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
        
        elif command == "2":
            memories = structured_mem.get_by_priority(5)
            
            if not memories:
                print("No memories stored yet.")
                continue
            
            print("\n--- TOP MEMORIES ---")
            for mem in memories:
                print(f"\n[{mem['memory_id']}] {mem['title']} ({mem['type'].upper()})")
                print(f"  Priority: {mem['priority']}/5")
                print(f"  Directive: {mem['orion_directive'][:80]}...")
        
        elif command == "3":
            directives = structured_mem.get_directives()
            
            if not directives:
                print("No directives yet.")
                continue
            
            print("\n--- ALL ORION DIRECTIVES ---")
            for i, directive in enumerate(directives, 1):
                print(f"\n{i}. {directive}")
        
        elif command == "4":
            print("👋 Exiting importer.\n")
            break
        
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
