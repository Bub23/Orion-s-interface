# API ENDPOINTS WITH WORKER INTEGRATION

## Complete API Flow (Request → Queue → Worker → Response)

---

## 🔐 Authentication

### POST `/auth/register`
Register new user
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
**Response:** `{ "access_token": "...", "token_type": "bearer" }`

### POST `/auth/login`
Login user
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
**Response:** `{ "access_token": "...", "token_type": "bearer" }`

---

## 💡 Ideas (Content Generation Pipeline)

### POST `/ideas/create` ⚡ ASYNC
Submit idea and queue full content pipeline

**Request:**
```json
{
  "raw_input": "I made a million dollars in 90 days using AI automation",
  "source": "manual"
}
```

**Response (Immediate):**
```json
{
  "task_id": "abc123def456",
  "status": "queued",
  "message": "Content pipeline queued. Check /ideas/status/abc123def456 for progress."
}
```

**Behind the scenes:**
- Request → Redis queue
- Celery worker picks up task
- Runs ContentPipeline.execute_full_pipeline()
- Processes Idea → Hooks → Script
- Stores in cache (returned on status check)

### GET `/ideas/status/{task_id}` 🔄 POLL
Check pipeline progress

**Response (PROCESSING):**
```json
{
  "task_id": "abc123def456",
  "status": "processing",
  "current": 2,
  "total": 3
}
```

**Response (SUCCESS):**
```json
{
  "task_id": "abc123def456",
  "status": "success",
  "result": {
    "idea": {
      "raw_input": "I made a million dollars...",
      "category": "hustle",
      "viral_score": 0.82,
      "word_count": 12
    },
    "hooks": [
      {
        "text": "I lost everything in 24 hours",
        "hook_type": "shock",
        "intensity": 0.85,
        "variants": ["You lost everything...", "WAIT: I lost..."]
      }
    ],
    "script": {
      "hook": "I lost everything in 24 hours",
      "sections": [
        {
          "title": "Hook & Setup",
          "duration_seconds": 4,
          "content": "I lost everything in 24 hours. Here's how I made it work."
        },
        {
          "title": "Body",
          "duration_seconds": 8,
          "content": "So here's what actually happened... Most people would've quit..."
        }
      ],
      "cta": "Follow for more real ones.",
      "total_duration": 35
    }
  }
}
```

---

## 🔥 Hooks

### GET `/hooks/status/{task_id}` 
Get hooks from completed pipeline

**Response:**
```json
{
  "task_id": "abc123def456",
  "status": "success",
  "hooks": [
    {
      "text": "I lost everything in 24 hours",
      "hook_type": "shock",
      "intensity": 0.85
    },
    {
      "text": "Nobody talks about this reality",
      "hook_type": "confession",
      "intensity": 0.72
    }
  ]
}
```

---

## ✍️ Scripts

### GET `/scripts/status/{task_id}`
Get script from completed pipeline

**Response:**
```json
{
  "task_id": "abc123def456",
  "status": "success",
  "script": {
    "hook": "I lost everything in 24 hours",
    "pacing": "medium",
    "total_duration": 35,
    "sections": [...]
  }
}
```

### POST `/scripts/render` ⚡ ASYNC
Queue video render job

**Request:**
```json
{
  "pipeline_task_id": "abc123def456",
  "platform": "heygen",
  "style_template": "talking_head"
}
```

**Response (Immediate):**
```json
{
  "render_task_id": "render_xyz789",
  "status": "queued",
  "message": "Render queued on heygen. Check /render/status/render_xyz789"
}
```

**Behind the scenes:**
- Request → Redis queue (render priority queue)
- Celery worker picks up render task
- Calls HeyGen API (via /integrations)
- Polls for completion
- Stores output URL
- Triggers analytics logging

---

## 🎥 Render

### GET `/render/status/{task_id}` 🔄 POLL
Check render job status

**Response (PROCESSING):**
```json
{
  "task_id": "render_xyz789",
  "status": "processing",
  "progress": 45
}
```

**Response (SUCCESS):**
```json
{
  "task_id": "render_xyz789",
  "status": "complete",
  "output_url": "https://cdn.example.com/videos/render_xyz789.mp4"
}
```

### POST `/render/complete` (Webhook)
External render service notifies when complete

**Request:**
```json
{
  "render_task_id": "render_xyz789",
  "output_url": "https://cdn.example.com/videos/render_xyz789.mp4",
  "render_duration": 127
}
```

**Response:**
```json
{
  "task_id": "handler_abc123",
  "status": "queued",
  "message": "Render completion being processed"
}
```

---

## 📊 Analytics

### POST `/analytics/track` ⚡ ASYNC
Track post performance metrics

**Request:**
```json
{
  "post_id": "post_123",
  "views": 5000,
  "engagement": 500,
  "clicks": 250,
  "shares": 100,
  "comments": 150,
  "hook_used": "I lost everything in 24 hours",
  "idea_used": "The story of my startup failure"
}
```

**Response (Immediate):**
```json
{
  "task_id": "track_abc123",
  "status": "queued",
  "message": "Performance metrics being processed"
}
```

**Behind the scenes:**
- Request → Redis queue (analytics priority queue)
- Celery worker calculates metrics
- AnalyticsEngine.analyze() returns insights
- Viral score calculated: ((shares + comments) / views) * 1000 = 50
- Performance tier: "high"
- If high performer: triggers learning loop automatically

### GET `/analytics/learning/{post_id}`
Get learning insights for post

**Response:**
```json
{
  "post_id": "post_123",
  "task_id": "learning_xyz789",
  "status": "complete",
  "learning_status": "complete",
  "analysis": {
    "viral_score": 50,
    "is_high_performer": true,
    "performance_tier": "high",
    "insights": [
      "High virality - strong performer",
      "Strong retention - people are staying engaged",
      "Share-focused content - good for reach"
    ]
  },
  "next_steps": {
    "remix_type": "escalation",
    "remixed_hooks": [
      "I JUST lost everything in 24 hours",
      "WAIT. I lost everything and it's worse than you think"
    ],
    "remixed_idea": "Part 2: The deeper truth about startup failure",
    "suggestion": "Use escalation strategy for next content batch"
  }
}
```

### GET `/analytics/daily-stats`
Get daily performance aggregation

**Response:**
```json
{
  "user_id": "user_123",
  "date": "2024-05-07",
  "total_posts": 5,
  "avg_viral_score": 18.5,
  "high_performers": 2,
  "total_views": 25000,
  "engagement_rate": 12.5
}
```

---

## 🔄 COMPLETE USER FLOW (REAL EXAMPLE)

```bash
# 1. Register
POST /auth/register
← { "access_token": "token123" }

# 2. Submit idea (queued)
POST /ideas/create
   Headers: Authorization: Bearer token123
   Body: { "raw_input": "I made $1M in 90 days with AI", "source": "manual" }
← { "task_id": "task_abc123", "status": "queued" }

# 3. Poll for completion
GET /ideas/status/task_abc123
← { "status": "processing", "current": 2, "total": 3 }
(wait 5-10 seconds)
GET /ideas/status/task_abc123
← { "status": "success", "result": { idea, hooks, script } }

# 4. Queue render
POST /scripts/render
   Body: { "pipeline_task_id": "task_abc123", "platform": "heygen" }
← { "render_task_id": "render_xyz789", "status": "queued" }

# 5. Poll render
GET /render/status/render_xyz789
← { "status": "complete", "output_url": "https://..." }

# 6. Publish and track
POST /analytics/track
   Body: { "post_id": "post_123", "views": 5000, ... }
← { "task_id": "track_abc123", "status": "queued" }

# 7. Check learning insights
GET /analytics/learning/post_123
← { "analysis": {...}, "next_steps": {...} }
```

---

## ⚙️ WORKER QUEUES

Three separate Celery worker queues:

| Queue | Tasks | Priority | Timeout |
|-------|-------|----------|---------|
| `content_pipeline` | Idea → Hook → Script | High | 5 min |
| `render` | Video rendering | Medium | 30 min |
| `analytics` | Metrics, learning loop | Low | 5 min |

Run multiple workers:
```bash
# Terminal 1: Pipeline worker
celery -A app.workers.celery_app worker -Q content_pipeline --loglevel=info

# Terminal 2: Render worker
celery -A app.workers.celery_app worker -Q render --loglevel=info

# Terminal 3: Analytics worker
celery -A app.workers.celery_app worker -Q analytics --loglevel=info
```

---

## 🔥 ERROR HANDLING

All endpoints handle failures gracefully:

**Failed task:**
```json
{
  "task_id": "task_abc123",
  "status": "failed",
  "result": { "error": "Idea validation failed - text too short" }
}
```

**Invalid request:**
```json
{
  "detail": "Referenced pipeline task is not complete or failed"
}
```

---

## 🚀 PERFORMANCE CHARACTERISTICS

- **Ideas API:** ~200ms (queued, returns immediately)
- **Ideas status check:** ~50ms (cache lookup)
- **Ideas generation:** 2-5 seconds (worker processing)
- **Render API:** ~300ms (queued)
- **Render execution:** 30-180 seconds (external API)
- **Analytics API:** ~100ms (queued)
- **Analytics processing:** 1-2 seconds (worker)

All requests return in <500ms. Heavy work happens in background workers.
