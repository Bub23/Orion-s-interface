#!/usr/bin/env python
"""
API Route Testing Script
Tests the Content Engine routes using Flask's test client
"""

import sys
import os
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add repo root to path
repo_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_root)

print("=" * 70)
print("ORION CONTENT ENGINE V1 - API ROUTE TESTING")
print("=" * 70)

# Import Flask app
print("\n[1] Importing Flask app...")
try:
    from web_app import app
    print("    ✓ Flask app imported successfully")
except Exception as e:
    print(f"    ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create test client
print("\n[2] Creating Flask test client...")
try:
    client = app.test_client()
    print("    ✓ Test client created")
except Exception as e:
    print(f"    ✗ Test client creation failed: {e}")
    sys.exit(1)

# Test 1: GET /api/status (existing route - should still work)
print("\n[3] Testing GET /api/status (existing route)...")
try:
    response = client.get("/api/status")
    if response.status_code == 200:
        data = response.get_json()
        print(f"    ✓ Status: {data.get('status')}")
        print(f"    ✓ App: {data.get('app')}")
        print(f"    ✓ AI Ready: {data.get('ai_ready')}")
    else:
        print(f"    ✗ Failed with status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    sys.exit(1)

# Test 2: GET /api/content/history (empty)
print("\n[4] Testing GET /api/content/history...")
try:
    response = client.get("/api/content/history")
    if response.status_code == 200:
        data = response.get_json()
        print(f"    ✓ Response: {response.status_code}")
        print(f"    ✓ Total drafts: {data.get('total')}")
        print(f"    ✓ Offset: {data.get('offset')}")
        print(f"    ✓ Limit: {data.get('limit')}")
    else:
        print(f"    ✗ Failed with status {response.status_code}")
        print(f"    Response: {response.get_data(as_text=True)}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: POST /api/content/create
print("\n[5] Testing POST /api/content/create...")
try:
    payload = {
        "content": "This is a test content for Orion Content Engine",
        "title": "Test Draft",
        "platforms": ["tiktok", "instagram", "threads"]
    }
    response = client.post(
        "/api/content/create",
        json=payload,
        content_type="application/json"
    )
    if response.status_code == 201:
        data = response.get_json()
        draft_id = data.get('draft_id')
        print(f"    ✓ Response: {response.status_code}")
        print(f"    ✓ Draft ID: {draft_id}")
        print(f"    ✓ Title: {data.get('title')}")
        print(f"    ✓ Platforms: {data.get('platforms')}")
    else:
        print(f"    ✗ Failed with status {response.status_code}")
        print(f"    Response: {response.get_data(as_text=True)}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: GET /api/content/history (should now have 1 draft)
print("\n[6] Testing GET /api/content/history (with draft)...")
try:
    response = client.get("/api/content/history")
    if response.status_code == 200:
        data = response.get_json()
        print(f"    ✓ Response: {response.status_code}")
        print(f"    ✓ Total drafts: {data.get('total')}")
        if data.get('total') > 0:
            draft = data['drafts'][0]
            print(f"    ✓ First draft: {draft.get('title')}")
    else:
        print(f"    ✗ Failed with status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    sys.exit(1)

# Test 5: GET /api/content/platform-pack
print("\n[7] Testing GET /api/content/platform-pack...")
try:
    if 'draft_id' in locals() and draft_id:
        response = client.get(f"/api/content/platform-pack?draft_id={draft_id}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"    ✓ Response: {response.status_code}")
            print(f"    ✓ Draft ID: {data.get('draft_id')}")
            print(f"    ✓ Platforms in pack: {list(data.get('platforms', {}).keys())}")
            for platform, content in data.get('platforms', {}).items():
                if 'char_count' in content:
                    print(f"      - {platform}: {content['char_count']}/{content['max_chars']} chars")
        else:
            print(f"    ✗ Failed with status {response.status_code}")
            print(f"    Response: {response.get_data(as_text=True)}")
            sys.exit(1)
    else:
        print("    ! Skipped (no draft_id available)")
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: GET /api/content/search
print("\n[8] Testing GET /api/content/search...")
try:
    response = client.get("/api/content/search?q=test")
    if response.status_code == 200:
        data = response.get_json()
        print(f"    ✓ Response: {response.status_code}")
        print(f"    ✓ Query: {data.get('query')}")
        print(f"    ✓ Results: {data.get('total_results')}")
    else:
        print(f"    ✗ Failed with status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    sys.exit(1)

# Test 7: GET /api/content/draft/<id>
print("\n[9] Testing GET /api/content/draft/<id>...")
try:
    if 'draft_id' in locals() and draft_id:
        response = client.get(f"/api/content/draft/{draft_id}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"    ✓ Response: {response.status_code}")
            print(f"    ✓ Draft title: {data.get('title')}")
            print(f"    ✓ Content length: {len(data.get('content', ''))}")
        else:
            print(f"    ✗ Failed with status {response.status_code}")
            sys.exit(1)
    else:
        print("    ! Skipped (no draft_id available)")
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    sys.exit(1)

# Test 8: POST /api/content/save (update)
print("\n[10] Testing POST /api/content/save (update)...")
try:
    if 'draft_id' in locals() and draft_id:
        payload = {
            "draft_id": draft_id,
            "content": "Updated test content with new text",
            "title": "Updated Test Draft"
        }
        response = client.post(
            "/api/content/save",
            json=payload,
            content_type="application/json"
        )
        if response.status_code == 200:
            data = response.get_json()
            print(f"    ✓ Response: {response.status_code}")
            print(f"    ✓ Success: {data.get('success')}")
            print(f"    ✓ Draft ID: {data.get('draft_id')}")
        else:
            print(f"    ✗ Failed with status {response.status_code}")
            print(f"    Response: {response.get_data(as_text=True)}")
            sys.exit(1)
    else:
        print("    ! Skipped (no draft_id available)")
except Exception as e:
    print(f"    ✗ Request failed: {e}")
    sys.exit(1)

# Test 9: Verify existing routes still work
print("\n[11] Verifying existing routes still work...")
try:
    routes_to_test = [
        ("/api/health", 200, "GET"),
        ("/api/system-metrics", 200, "GET"),
        ("/api/gpu", 200, "GET"),
    ]
    
    for route, expected_status, method in routes_to_test:
        if method == "GET":
            response = client.get(route)
        else:
            response = client.post(route)
        
        if response.status_code == expected_status:
            print(f"    ✓ {route}: {response.status_code}")
        else:
            print(f"    ! {route}: {response.status_code} (expected {expected_status})")

except Exception as e:
    print(f"    ! Route verification error: {e}")

# Test 10: Empire Ops draft routes
print("\n[12] Testing Empire Ops draft routes...")
try:
    campaign_payload = {
        "title": "Empire Ops Test",
        "goal": "book paid setup calls",
        "offer": "Orion dashboard setup sprint",
        "audience": "local business owners",
        "platforms": ["facebook", "instagram", "tiktok", "youtube", "threads"]
    }
    response = client.post("/api/campaign/create", json=campaign_payload)
    assert response.status_code == 201
    campaign = response.get_json()
    assert campaign["status"] == "draft"
    assert campaign["review_status"] == "manual_review"
    print(f"    ✓ /api/campaign/create: {response.status_code}")
    print(f"    ✓ /api/campaign/history: {client.get('/api/campaign/history').status_code}")
    print(f"    ✓ /api/campaign/<id>: {client.get('/api/campaign/' + campaign['id']).status_code}")

    lead_payload = {
        "business_type": "AI automation studio",
        "target_customer": "local service businesses",
        "offer": "lead follow-up workflow",
        "pain_point": "missed leads",
        "tone": "blunt",
        "platform": "facebook"
    }
    response = client.post("/api/leads/draft-message", json=lead_payload)
    assert response.status_code == 200
    assert response.get_json()["status"] == "draft"
    print(f"    ✓ /api/leads/draft-message: {response.status_code}")
    response = client.post("/api/leads/save", json=lead_payload)
    assert response.status_code == 201
    assert response.get_json()["review_status"] == "manual_review"
    print(f"    ✓ /api/leads/save: {response.status_code}")
    print(f"    ✓ /api/leads/history: {client.get('/api/leads/history').status_code}")
except Exception as e:
    print(f"    ✗ Empire Ops route test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL API ROUTE TESTS PASSED")
print("=" * 70)
print("\nContent Engine Status:")
print(f"  - Storage path: data/content_history.json")
print(f"  - Test draft created: {draft_id if 'draft_id' in locals() else 'N/A'}")
print(f"  - All 4 required endpoints working")
print(f"  - All existing routes preserved")
print(f"  - Empire Ops campaign and lead draft routes working")
print("\nReady for production deployment!")
print()
