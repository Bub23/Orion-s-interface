# Orion Content Engine v1 - Setup & Deployment Guide

## ✓ Verification Complete

All components have been verified and are ready for deployment.

## File Structure

```
orion-interface/
├── content_engine.py              # Core engine (310 lines) - NEW
├── web_app.py                     # Flask backend (modified +180 lines)
├── templates/
│   └── chat.html                  # Dashboard (modified +500 lines)
├── data/                          # Storage directory (auto-created)
│   └── content_history.json       # Content storage (auto-created)
├── verify_setup.py                # Setup verification script - NEW
├── test_api_routes.py             # Route testing script - NEW
├── test_content_engine.py         # Unit tests - NEW
├── CONTENT_ENGINE.md              # Feature documentation - NEW
└── [all existing files preserved]
```

## Storage Path Verification

**Confirmed:** `data/content_history.json`

- Location: Repo root + `/data/` subdirectory
- Created automatically by `ContentStorage._ensure_storage_dir()`
- Initialized automatically by `ContentStorage._ensure_storage_file()`
- Format: JSON with structure:
  ```json
  {
    "version": "1.0",
    "drafts": [
      {
        "id": "uuid",
        "title": "Draft Title",
        "content": "Content text",
        "formatted": { ... },
        "platforms": ["tiktok", "facebook", ...],
        "created_at": "2024-01-01T12:00:00.000000",
        "updated_at": "2024-01-01T12:00:00.000000",
        "metadata": {}
      }
    ]
  }
  ```

## Code Verification Checklist

### content_engine.py
✓ Imports: json, os, datetime, uuid, typing
✓ Three classes: PlatformFormatter, ContentStorage, ContentEngine
✓ Storage path default: "data/content_history.json" (line 74, 219)
✓ Auto-creates data directory (line 81)
✓ Auto-creates storage file (line 87)
✓ Platform specs: TikTok, Facebook, Instagram, Threads, YouTube
✓ CRUD operations: save, get, update, delete, search
✓ 310 lines of production code

### web_app.py (Modified)
✓ Import: `from content_engine import ContentEngine` (line 11)
✓ Initialize: `content_engine = ContentEngine()` (line 28)
✓ 7 new routes added:
  - POST /api/content/create (line 381)
  - POST /api/content/save (line 410)
  - GET /api/content/history (line 451)
  - GET /api/content/platform-pack (line 476)
  - GET /api/content/search (line 498)
  - GET /api/content/draft/<id> (line 517)
  - DELETE /api/content/draft/<id> (line 533)
✓ Existing routes preserved: /api/status, /api/health, /api/chat, etc.
✓ GPU telemetry: Preserved and functional
✓ AI routing: Preserved and functional
✓ Docker support: Preserved

### templates/chat.html (Modified)
✓ Tab system: console + content tabs (lines 667-668)
✓ CSS: 350+ lines for tabbed UI and forms
✓ Form elements: title, textarea, platform checkboxes
✓ JavaScript: 300+ lines for tab switching and API calls
✓ Preview display: Platform-specific formatting with stats
✓ History view: Selectable list of drafts
✓ Dashboard styling: Consistent with existing theme

## API Endpoints

### 4 Required Endpoints ✓

1. **POST /api/content/create**
   - Creates new content draft
   - Input: content, title, platforms
   - Output: draft_id, title, platforms, created_at

2. **POST /api/content/save**
   - Updates or creates draft
   - Input: draft_id, content, title
   - Output: success, draft_id, updated_at

3. **GET /api/content/history**
   - Retrieves content history
   - Query params: limit, offset, platform
   - Output: total, offset, limit, drafts[]

4. **GET /api/content/platform-pack**
   - Gets platform-specific versions
   - Query params: draft_id (required)
   - Output: draft_id, title, original_content, platforms{}

### Bonus Endpoints ✓

5. **GET /api/content/search**
   - Search by title/content
   - Query params: q (required)

6. **GET /api/content/draft/<id>**
   - Get specific draft details

7. **DELETE /api/content/draft/<id>**
   - Delete a draft

## Existing Routes Preserved ✓

- GET /api/status - App status
- GET /api/health - Server health
- GET /api/system-metrics - System metrics
- GET /api/gpu - GPU telemetry
- GET /api/memories/sidebar - Memory status
- POST /api/chat - AI chat
- GET / - Dashboard

## Testing Scripts

### 1. Setup Verification
```bash
python verify_setup.py
```
Checks:
- Data folder creation
- Storage file initialization
- Import verification
- Basic functionality test

### 2. Unit Tests
```bash
python test_content_engine.py
```
Tests:
- PlatformFormatter
- ContentStorage
- ContentEngine
- All CRUD operations

### 3. API Route Testing
```bash
python test_api_routes.py
```
Tests:
- /api/status (existing)
- /api/content/history (GET)
- /api/content/create (POST)
- /api/content/platform-pack (GET)
- /api/content/search (GET)
- /api/content/draft/<id> (GET)
- /api/content/save (POST)
- All existing routes

## Quick Start

### 1. Verify Setup
```bash
cd c:\Users\outla\OneDrive\OIRONSINTERFACE.worktrees\agents-orion-content-engine-v1
python verify_setup.py
```

Expected output:
```
✓ Data folder exists
✓ Storage file valid JSON
✓ content_engine imports successful
✓ ContentEngine initialized
✓ Platform formatter working
✓ Content creation working
✓ History retrieval working
✓ Platform pack generation working
```

### 2. Run Unit Tests
```bash
python test_content_engine.py
```

Expected output:
```
✓ Platform formatter tests passed
✓ Storage tests passed
✓ Content Engine tests passed
✓✓✓ All tests passed!
```

### 3. Test API Routes (with Flask running)
```bash
# Terminal 1: Start Flask
python web_app.py

# Terminal 2: Run tests
python test_api_routes.py
```

Expected output:
```
✓ All API route tests passed
✓ All 4 required endpoints working
✓ All existing routes preserved
```

### 4. Start Production Server
```bash
# With default settings (port 8000)
python web_app.py

# Or with environment variables
set APP_PORT=8000
set NVIDIA_API_KEY=your-key
python web_app.py

# Or with Docker
docker-compose up
```

Access dashboard: http://localhost:8000

## Configuration

### Environment Variables (optional)
```bash
APP_PORT=8000                          # Default: 8000
NVIDIA_API_KEY=your-nvidia-key        # For NVIDIA API
NVIDIA_BASE_URL=https://...           # NVIDIA endpoint
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
OPENAI_API_KEY=your-openai-key        # For OpenAI
OPENAI_MODEL=gpt-4o-mini
```

### Storage Configuration
Edit in `content_engine.py` if needed:
```python
# Line 74 (ContentStorage.__init__)
def __init__(self, storage_path: str = "data/content_history.json"):

# Line 219 (ContentEngine.__init__)
def __init__(self, storage_path: str = "data/content_history.json"):
```

## Dashboard Usage

1. **Open Dashboard**
   - URL: http://localhost:8000
   - Two tabs: "Console" and "Content Engine"

2. **Create Content**
   - Click "Content Engine" tab
   - Enter title (optional)
   - Enter content in textarea
   - Select platforms (checkboxes)
   - Click "Create Draft"

3. **View Platform Preview**
   - Shows formatted content for each platform
   - Displays character counts vs limits
   - Warns if content truncated

4. **View History**
   - Click "View History"
   - Browse all saved drafts
   - Click draft to see preview
   - Click "New Draft" to create another

5. **Use Existing Console**
   - Click "Console" tab
   - All existing AI chat features work
   - System status and metrics unchanged

## Troubleshooting

### Issue: "No module named 'content_engine'"
**Solution:** Ensure content_engine.py is in repo root, same level as web_app.py

### Issue: "Permission denied" for data folder
**Solution:** Run Flask with appropriate permissions, or pre-create data folder

### Issue: "data/content_history.json not found"
**Solution:** Run verify_setup.py first - it will create all necessary files

### Issue: Dashboard tab doesn't appear
**Solution:** Clear browser cache, hard refresh (Ctrl+Shift+R)

### Issue: Content not saving
**Solution:** Check file permissions on data/ folder, verify disk space available

## Production Deployment

### Docker Deployment
```bash
docker-compose up -d
# Access: http://localhost:8000
```

### Manual Deployment
1. Verify setup: `python verify_setup.py`
2. Run tests: `python test_api_routes.py`
3. Start server: `python web_app.py`

### Gunicorn Deployment
```bash
gunicorn -w 4 -b 0.0.0.0:8000 web_app:app
```

### Nginx Proxy
```nginx
upstream orion {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://orion;
    }
}
```

## Monitoring

### Key Logs to Watch
- Flask startup messages
- API request logs (not noisy routes)
- Content creation confirmations
- Error messages

### Metrics
- Total drafts in storage
- Average content length
- Most used platforms
- API response times

## Next Steps (Phase 2)

- [ ] Auto-posting integration with platform APIs
- [ ] Scheduling content publication
- [ ] Media attachment support
- [ ] Analytics and engagement tracking
- [ ] AI content suggestions
- [ ] Draft collaboration features
- [ ] Version history for drafts
- [ ] Hashtag recommendations
- [ ] Content templates
- [ ] A/B testing capabilities

## Summary

**Status:** ✓ PRODUCTION READY

All required functionality implemented:
- ✓ 4 API endpoints functional
- ✓ Local JSON storage working
- ✓ Platform-specific formatting active
- ✓ Dashboard integrated
- ✓ No breaking changes
- ✓ Existing features preserved
- ✓ Full test coverage

**Ready to deploy and use!**
