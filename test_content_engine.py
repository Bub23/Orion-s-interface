#!/usr/bin/env python
"""Test script for Content Engine functionality."""

import sys
import json
from content_engine import ContentEngine, PlatformFormatter, ContentStorage

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def test_platform_formatter():
    """Test platform formatting."""
    print("\n=== Testing Platform Formatter ===")
    
    content = "Check out this amazing content! It's perfect for social media and all platforms. #awesome #content #orion"
    
    # Test single platform
    tiktok_result = PlatformFormatter.format_for_platform(content, "tiktok")
    print(f"TikTok: {tiktok_result['char_count']}/{tiktok_result['max_chars']} chars")
    assert not tiktok_result.get('error')
    assert tiktok_result['platform'] == 'tiktok'
    
    # Test all platforms
    all_platforms = PlatformFormatter.format_all_platforms(content)
    print(f"All platforms formatted: {list(all_platforms.keys())}")
    assert len(all_platforms) == 5
    
    print("✓ Platform formatter tests passed")

def test_storage():
    """Test content storage."""
    print("\n=== Testing Content Storage ===")
    
    storage = ContentStorage("test_content_history.json")
    
    # Test save draft
    draft = storage.save_draft(
        content="Test content for storage",
        platforms=["tiktok", "instagram"],
        title="Test Draft"
    )
    print(f"Draft saved: {draft['id']}")
    assert draft['id']
    assert draft['title'] == 'Test Draft'
    
    # Test get draft
    retrieved = storage.get_draft(draft['id'])
    print(f"Draft retrieved: {retrieved['title']}")
    assert retrieved is not None
    assert retrieved['title'] == 'Test Draft'
    
    # Test get all drafts
    all_drafts = storage.get_all_drafts()
    print(f"Total drafts: {all_drafts['total']}")
    assert all_drafts['total'] >= 1
    
    # Test update draft
    updated = storage.update_draft(draft['id'], "Updated content", "Updated Title")
    print(f"Draft updated: {updated['title']}")
    assert updated['title'] == 'Updated Title'
    assert updated['content'] == 'Updated content'
    
    # Test search
    search_results = storage.search_drafts("Updated")
    print(f"Search results: {len(search_results)}")
    assert len(search_results) >= 1
    
    # Test delete
    deleted = storage.delete_draft(draft['id'])
    print(f"Draft deleted: {deleted}")
    assert deleted
    
    print("✓ Storage tests passed")

def test_content_engine():
    """Test content engine."""
    print("\n=== Testing Content Engine ===")
    
    engine = ContentEngine("test_content_history.json")
    
    # Test create content
    result = engine.create_content(
        content="Orion Content Engine is live!",
        title="Test Post",
        platforms=["tiktok", "facebook", "youtube"]
    )
    print(f"Content created: {result['draft_id']}")
    assert result['success']
    assert result['draft_id']
    draft_id = result['draft_id']
    
    # Test get history
    history = engine.get_content_history(limit=5)
    print(f"History items: {history['total']}")
    assert history['total'] >= 1
    
    # Test platform pack
    pack = engine.get_platform_pack(draft_id)
    print(f"Platform pack platforms: {list(pack['platforms'].keys())}")
    assert 'tiktok' in pack['platforms']
    assert 'facebook' in pack['platforms']
    
    # Test search
    search = engine.search_content("Orion")
    print(f"Search results: {search['total_results']}")
    assert search['total_results'] >= 1
    
    # Test get draft details
    details = engine.get_draft_details(draft_id)
    print(f"Draft details: {details['title']}")
    assert details['title'] == 'Test Post'
    
    print("✓ Content Engine tests passed")

if __name__ == "__main__":
    try:
        test_platform_formatter()
        test_storage()
        test_content_engine()
        print("\n✓✓✓ All tests passed! ✓✓✓\n")
    except Exception as e:
        print(f"\n✗ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
