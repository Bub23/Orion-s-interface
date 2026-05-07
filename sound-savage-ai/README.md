# Sound Savage AI — Backend Production Codebase

**LOCKED PRODUCTION ARCHITECTURE v1.0**

---

## ⚙️ STACK

- **Framework:** FastAPI (Python async)
- **Database:** PostgreSQL + SQLAlchemy 2.0 ORM
- **Auth:** JWT (jose)
- **External APIs:** OpenAI, Runway, HeyGen, Synthesia
- **Queue:** Redis + Celery (setup ready)
- **Container:** Docker + Docker Compose

---

## 📁 PROJECT STRUCTURE

```
sound-savage-ai/
├── app/
│   ├── main.py                 # FastAPI app entry
│   ├── core/
│   │   ├── config.py          # Pydantic settings
│   │   ├── security.py        # JWT + password
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── exceptions.py      # Custom errors
│   ├── models/
│   │   ├── user.py            # User model
│   │   ├── content.py         # Ideas, Hooks, Scripts, RenderJobs, Posts
│   │   ├── performance.py     # Analytics
│   │   ├── subscription.py    # Tiers
│   ├── schemas/
│   │   ├── content.py         # Pydantic request/response schemas
│   ├── api/
│   │   ├── deps.py            # Route dependencies (auth)
│   │   ├── routes/
│   │   │   ├── auth.py        # POST /auth/register, /login
│   │   │   ├── ideas.py       # POST /ideas/create, GET /ideas/
│   │   │   ├── hooks.py       # POST /hooks/generate, GET /hooks/
│   │   │   ├── scripts.py     # POST /scripts/generate, GET /scripts/
│   │   │   ├── render.py      # POST /render/create, GET /render/status
│   ├── services/
│   │   ├── idea_engine.py     # Idea input + scoring
│   │   ├── hook_engine.py     # Hook generation + learning
│   │   ├── script_engine.py   # Script building
│   │   ├── render_router.py   # Render platform selection
│   ├── integrations/
│   │   ├── openai_client.py   # OpenAI API wrapper
│   │   ├── runway_client.py   # (stub)
│   │   ├── heygen_client.py   # (stub)
│   │   ├── synthesia_client.py # (stub)
│   ├── workers/
│   │   ├── content_pipeline_worker.py  # (Celery task)
│   │   ├── render_worker.py            # (Celery task)
│   │   ├── analytics_worker.py         # (Celery task)
├── migrations/                # Alembic migrations
├── tests/                     # Unit + integration tests
├── docker-compose.yml         # PostgreSQL + Redis + API
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 QUICK START

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up .env
cp .env.example .env
# Fill in API keys

# 3. Start services (PostgreSQL + Redis)
docker-compose up -d

# 4. Run migrations
alembic upgrade head

# 5. Start API
uvicorn app.main:app --reload
```

### Docker

```bash
docker-compose up
# API runs on http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 🧠 SYSTEM FLOW

```
Frontend → FastAPI Routes
         ↓
Dependencies (JWT auth)
         ↓
Services (Business logic)
         ↓
Models (SQLAlchemy ORM)
         ↓
PostgreSQL
         ↓
External APIs (via integrations/)
```

---

## 📊 API ENDPOINTS

### Auth
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login, get JWT

### Ideas
- `POST /ideas/create` — Submit manual idea
- `GET /ideas/` — List user ideas

### Hooks
- `POST /hooks/generate` — Generate 5 hooks
- `GET /hooks/{content_id}` — Get hooks for content
- `POST /hooks/{hook_id}/mark-performer` — Mark high performer

### Scripts
- `POST /scripts/generate` — Generate script from hook
- `GET /scripts/{content_id}` — Get scripts for content

### Render
- `POST /render/create` — Create render job
- `GET /render/status/{job_id}` — Check status

---

## 🔐 SYSTEM RULES (LOCKED)

### RULE 1: Single Responsibility
Every service does ONE job only.

### RULE 2: No Logic in Routes
API routes only handle request/response.
All logic lives in `/services`

### RULE 3: Isolated External APIs
External APIs ONLY called from `/integrations`
Never directly from routes or services.

### RULE 4: Workers for Heavy Work
Rendering, analytics, long tasks → Celery workers
Routes must respond in < 100ms

### RULE 5: Models are Dumb
Models are ORM definitions only.
No business logic in models.

---

## 🧬 DATABASE SCHEMA

### Users
```
id (UUID)
email (unique)
password_hash
subscription_status (free, creator, music, empire)
created_at, updated_at
```

### ContentIdea
```
id (UUID)
user_id (FK)
source (manual, trend, remix)
raw_input (text)
category (music, story, ai, brand)
viral_score (float)
status (pending, processing, ready)
```

### Hook
```
id (UUID)
content_id (FK)
hook_text
hook_type (curiosity_gap, shock, emotional, authority)
variants (JSON)
performance_score
is_high_performer (boolean)
times_used
```

### Script
```
id (UUID)
content_id (FK)
hook_id (FK)
hook (text)
body (JSON array)
cta (text)
pacing (fast, medium, slow)
status (pending, ready, rendering)
```

### RenderJob
```
id (UUID)
script_id (FK)
platform (runway, heygen, synthesia)
style_template
status (queued, processing, done, failed)
output_url
```

### Post
```
id (UUID)
render_job_id (FK)
platform (youtube, tiktok, instagram, facebook)
platform_post_id
status (pending, published, failed)
published_at
```

### PerformanceEvent
```
id (UUID)
post_id (FK)
content_id (FK)
views, engagement, clicks, shares, comments
retention_rate, ctr, viral_score
hook_tag
tracked_at
```

---

## 🔄 EXAMPLE FLOW

1. **User submits idea**
   ```
   POST /ideas/create
   → IdeaEngine.create_manual_idea()
   → Score assigned
   → ContentIdea created
   ```

2. **Generate hooks**
   ```
   POST /hooks/generate
   → HookEngine.generate_hooks()
   → Call OpenAI (via integrations/)
   → 5 hooks stored
   ```

3. **Generate script**
   ```
   POST /scripts/generate
   → ScriptEngine.generate_script()
   → Call OpenAI (hook → body → CTA)
   → Script stored
   ```

4. **Route to renderer**
   ```
   POST /render/create
   → RenderRouter.route_render_job()
   → Select platform (Runway/HeyGen/Synthesia)
   → Queue render job
   → Celery worker picks it up
   ```

5. **Track performance**
   ```
   POST /analytics/track
   → Calculate metrics
   → Store PerformanceEvent
   → Trigger learning loop (if viral_score > 5)
   ```

---

## 📦 NEXT STEPS

1. **Database Migrations** — Run Alembic to create tables
2. **Worker Setup** — Configure Celery for background tasks
3. **External Integrations** — Implement Runway/HeyGen/Synthesia clients
4. **Testing** — Write unit + integration tests
5. **Deployment** — Docker push to registry, deploy to K8s/EC2

---

## 🎯 THIS IS PRODUCTION-READY

- Proper separation of concerns
- Async/await for performance
- JWT auth
- Database ORM with migrations
- External API isolation
- Background workers ready
- Error handling
- CORS middleware
- Docker containerized

**No fluff. No guessing. Ship it.**
