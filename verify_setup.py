#!/usr/bin/env python
"""
Setup verification script for Orion Content Engine v1
Checks:
1. Data folder creation
2. Storage file initialization
3. Import verification
4. Basic functionality
"""

import sys
import os
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add repo root to path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_root)

print("=" * 60)
print("ORION CONTENT ENGINE V1 - SETUP VERIFICATION")
print("=" * 60)

# Step 1: Check and create data folder
print("\n[1] Checking data folder...")
data_dir = os.path.join(repo_root, "data")
if os.path.exists(data_dir):
    print(f"    ✓ Data folder exists: {data_dir}")
else:
    print(f"    + Creating data folder: {data_dir}")
    os.makedirs(data_dir, exist_ok=True)
    print(f"    ✓ Data folder created")

# Step 2: Check storage file
print("\n[2] Checking storage file...")
storage_file = os.path.join(data_dir, "content_history.json")
if os.path.exists(storage_file):
    print(f"    ✓ Storage file exists: {storage_file}")
    with open(storage_file, "r") as f:
        data = json.load(f)
    print(f"    ✓ Storage file valid JSON with {len(data.get('drafts', []))} drafts")
else:
    print(f"    + Creating storage file: {storage_file}")
    with open(storage_file, "w") as f:
        json.dump({"version": "1.0", "drafts": []}, f, indent=2)
    print(f"    ✓ Storage file created")

# Step 3: Import verification
print("\n[3] Verifying imports...")
try:
    from content_engine import ContentEngine, ContentStorage, PlatformFormatter
    print("    ✓ content_engine imports successful")
except ImportError as e:
    print(f"    ✗ Import failed: {e}")
    sys.exit(1)

# Step 4: Instantiate ContentEngine
print("\n[4] Instantiating ContentEngine...")
try:
    engine = ContentEngine()
    print(f"    ✓ ContentEngine initialized")
    print(f"    ✓ Storage path: {engine.storage.storage_path}")
except Exception as e:
    print(f"    ✗ Instantiation failed: {e}")
    sys.exit(1)

# Step 5: Test platform formatter
print("\n[5] Testing PlatformFormatter...")
try:
    test_content = "Test content for all platforms"
    result = PlatformFormatter.format_all_platforms(test_content)
    print(f"    ✓ Formatted for {len(result)} platforms")
    for platform in result:
        chars = result[platform].get('char_count', 0)
        max_chars = result[platform].get('max_chars', 0)
        print(f"      - {platform}: {chars}/{max_chars} chars")
except Exception as e:
    print(f"    ✗ Platform formatter failed: {e}")
    sys.exit(1)

# Step 6: Test content creation
print("\n[6] Testing content creation...")
try:
    draft = engine.create_content(
        content="Test content for setup verification",
        title="Setup Test"
    )
    print(f"    ✓ Draft created: {draft['draft_id']}")
    print(f"    ✓ Platforms: {draft['platforms']}")
except Exception as e:
    print(f"    ✗ Content creation failed: {e}")
    sys.exit(1)

# Step 7: Test history retrieval
print("\n[7] Testing history retrieval...")
try:
    history = engine.get_content_history(limit=10)
    print(f"    ✓ History retrieved: {history['total']} total drafts")
except Exception as e:
    print(f"    ✗ History retrieval failed: {e}")
    sys.exit(1)

# Step 8: Test platform pack
print("\n[8] Testing platform pack...")
try:
    pack = engine.get_platform_pack(draft['draft_id'])
    print(f"    ✓ Platform pack generated for {len(pack['platforms'])} platforms")
except Exception as e:
    print(f"    ✗ Platform pack failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL SETUP VERIFICATION TESTS PASSED")
print("=" * 60)
print("\nReady to start Flask server:")
print("  python web_app.py")
print("\nOr with environment variables:")
print("  export APP_PORT=8000")
print("  python web_app.py")
print()
