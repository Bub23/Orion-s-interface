# Orion Content Engine v1

## Overview

The Orion Content Engine is a multi-platform content generation and management system integrated into the Orion Command Center. It enables users to create, format, and manage social media content for TikTok, Facebook, Instagram, Threads, and YouTube with platform-specific optimizations.

## Features

### ✓ Complete
- **Local JSON Storage**: All content drafts are stored locally in `data/content_history.json`
- **Draft Management**: Create, update, retrieve, and delete content drafts
- **Platform-Specific Formatting**: Automatic content optimization for each platform with:
  - Character limit enforcement (TikTok: 2200, Facebook: 63206, Instagram: 2200, Threads: 500, YouTube: 5000)
  - Platform-appropriate presentation
  - Content truncation warnings
- **Dashboard Integration**: Content generator tab in the Orion dashboard with intuitive UI
- **Draft-Only Mode**: No auto-posting (planned for future phases)

## API Endpoints

### POST `/api/content/create`
Create a new content draft.

**Request:**
```json
{
  "content": "Your content here",
  "title": "Optional draft title",
  "platforms": ["tiktok", "facebook", "instagram", "threads", "youtube"]
}
```

**Response:**
```json
{
  "success": true,
  "draft_id": "uuid-string",
  "title": "Draft title",
  "platforms": ["tiktok", "facebook", ...],
  "created_at": "2024-01-01T12:00:00.000000"
}
```

### POST `/api/content/save`
Save or update a content draft.

**Request:**
```json
{
  "draft_id": "optional-uuid-for-update",
  "content": "Updated content",
  "title": "Updated title"
}
```

### GET `/api/content/history`
Retrieve content history with pagination and filtering.

**Query Parameters:**
- `limit` (int): Maximum results (default: all, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `platform` (string): Filter by platform

**Response:**
```json
{
  "total": 42,
  "offset": 0,
  "limit": 20,
  "drafts": [
    {
      "id": "uuid",
      "title": "Draft title",
      "content": "Draft content",
      "platforms": ["tiktok", "facebook"],
      "created_at": "2024-01-01T12:00:00.000000",
      "updated_at": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

### GET `/api/content/platform-pack`
Get platform-specific versions of a draft.

**Query Parameters:**
- `draft_id` (string, required): The draft ID

**Response:**
```json
{
  "draft_id": "uuid",
  "title": "Draft title",
  "original_content": "Full content",
  "platforms": {
    "tiktok": {
      "platform": "tiktok",
      "title": "TikTok",
      "formatted_content": "Truncated content...",
      "char_count": 450,
      "max_chars": 2200,
      "is_truncated": false
    },
    ...
  }
}
```

### GET `/api/content/draft/<draft_id>`
Get details of a specific draft.

### DELETE `/api/content/draft/<draft_id>`
Delete a draft.

### GET `/api/content/search`
Search content by title or content text.

**Query Parameters:**
- `q` (string, required): Search query

## Dashboard Features

### Content Engine Tab
- **Title Input**: Optional title for the draft
- **Content Textarea**: Main content creation area with 6rem default height
- **Platform Selection**: Checkboxes for TikTok, Facebook, Instagram, Threads, YouTube (all selected by default)
- **Create Draft Button**: Generate and save a new draft
- **View History Button**: Browse existing drafts
- **Platform Preview**: Shows formatted content for each platform with character counts
- **History View**: Lists all drafts with creation date and platform info

## Storage Format

Content drafts are stored in `data/content_history.json`:

```json
{
  "version": "1.0",
  "drafts": [
    {
      "id": "uuid-string",
      "title": "Draft Title",
      "content": "Original content text",
      "formatted": {
        "tiktok": {
          "platform": "tiktok",
          "title": "TikTok",
          "formatted_content": "...",
          "char_count": 450,
          "max_chars": 2200,
          "is_truncated": false
        }
      },
      "platforms": ["tiktok", "facebook", "instagram", "threads", "youtube"],
      "created_at": "2024-01-01T12:00:00.000000",
      "updated_at": "2024-01-01T12:00:00.000000",
      "metadata": {}
    }
  ]
}
```

## Platform Specifications

| Platform | Max Chars | Max Hashtags | Description |
|----------|-----------|--------------|-------------|
| TikTok | 2,200 | 30 | Short video platform - focus on hooks and trend awareness |
| Facebook | 63,206 | 30 | Long-form content - community and engagement focused |
| Instagram | 2,200 | 30 | Visual platform - short captions with hashtags |
| Threads | 500 | 5 | Twitter alternative - concise, threaded conversations |
| YouTube | 5,000 | 15 | Video platform - detailed descriptions with timestamps |

## Existing Features Preserved

✓ Flask backend on web_app.py
✓ Dashboard in templates/chat.html
✓ Docker support
✓ GPU telemetry via /api/gpu
✓ Live system metrics at /api/system-metrics
✓ AI routing and chat functionality
✓ All existing API routes

## Code Structure

### content_engine.py
Contains three main classes:

1. **PlatformFormatter**: Static methods for formatting content per platform
   - `format_for_platform(content, platform)`: Format for single platform
   - `format_all_platforms(content)`: Format for all platforms

2. **ContentStorage**: Handles JSON file I/O and draft management
   - `save_draft()`: Create new draft
   - `get_draft(draft_id)`: Retrieve specific draft
   - `get_all_drafts()`: List with pagination and filtering
   - `update_draft()`: Modify existing draft
   - `delete_draft()`: Remove draft
   - `search_drafts(query)`: Full-text search

3. **ContentEngine**: Main orchestrator
   - `create_content()`: High-level draft creation
   - `get_content_history()`: History retrieval
   - `get_platform_pack()`: Platform-specific versions
   - `search_content()`: Content search
   - `get_draft_details()`: Draft information

### web_app.py Additions
6 new route handlers:
- `content_create()`: POST /api/content/create
- `content_save()`: POST /api/content/save
- `content_history()`: GET /api/content/history
- `content_platform_pack()`: GET /api/content/platform-pack
- `content_search()`: GET /api/content/search
- `content_get_draft()`: GET /api/content/draft/<draft_id>
- `content_delete_draft()`: DELETE /api/content/draft/<draft_id>

### templates/chat.html Updates
- Tab system for Console and Content Engine
- Content form with title, textarea, and platform selection
- Platform preview display with character counts
- History view with draft list
- Consistent styling with existing dashboard
- Full JavaScript event handling for all interactions

## Testing

Run the test suite:
```bash
python test_content_engine.py
```

Tests cover:
- Platform formatting for all platforms
- Local JSON storage operations
- Draft CRUD operations
- Search functionality
- Content engine orchestration

## Future Enhancements (Phase 2+)

- ✓ Auto-posting to platforms with API integration
- ✓ Media attachment support
- ✓ Scheduling drafts
- ✓ Analytics and engagement tracking
- ✓ AI-powered content suggestions
- ✓ Draft collaboration
- ✓ Version history
- ✓ Hashtag recommendations

## Running the Application

```bash
# Start the Flask server
python web_app.py

# With environment variables
export APP_PORT=8000
export NVIDIA_API_KEY="your-key"
python web_app.py

# Using Docker
docker-compose up
```

Access the dashboard at `http://localhost:8000` and open the "Content Engine" tab.
