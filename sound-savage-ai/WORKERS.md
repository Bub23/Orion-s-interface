# WORKER SYSTEM DOCUMENTATION

## Overview

Workers handle all async heavy-lifting:
- Long-running tasks (content generation, rendering)
- Background processing (analytics, learning loops)
- Queue management and retry logic

**No API blocks. Everything runs in background.**

---

## 🏗️ Architecture

```
API Request
   ↓
Task Queued to Redis
   ↓
Celery Worker Pool
   ↓
Service Execution
   ↓
Result Stored in Redis
   ↓
Client Polls for Completion
```

---

## 📁 Worker Files

```
app/workers/
├── celery_app.py                    # Celery config
├── content_pipeline_worker.py       # Idea → Hook → Script
├── render_worker.py                 # Video rendering
├── analytics_worker.py              # Metrics + learning
```

---

## 🧠 Core Workers

### 1. Content Pipeline Worker

**File:** `content_pipeline_worker.py`

**Task:** `tasks.generate_content_pipeline`

**What it does:**
- Validates idea input
- Generates 8 viral hooks
- Builds structured script
- Returns complete output

**Input:**
```python
generate_content_pipeline.apply_async(
    args=[user_id, raw_input, source]
)
```

**Output (on success):**
```python
{
    "status": "success",
    "user_id": "user_123",
    "idea": {...},
    "hooks": [...],
    "script": {...}
}
```

**Timeout:** 5 minutes

**Concurrency:** 2 (can process 2 ideas simultaneously)

---

### 2. Render Worker

**File:** `render_worker.py`

**Tasks:**
- `tasks.render_video` — Queue render job
- `tasks.check_render_status` — Poll render status
- `tasks.handle_render_complete` — Process completion

**What it does:**
- Routes script to appropriate renderer (Runway/HeyGen/Synthesia)
- Calls external render API
- Polls for completion
- Stores output URL

**Input:**
```python
render_video.apply_async(
    args=[script_id, platform, style_template]
)
```

**Output (on success):**
```python
{
    "status": "complete",
    "render_job_id": "render_xyz789",
    "output_url": "https://..."
}
```

**Timeout:** 30 minutes (rendering takes time)

**Concurrency:** 1 (avoid overloading render APIs)

---

### 3. Analytics Worker

**File:** `analytics_worker.py`

**Tasks:**
- `tasks.track_post_performance` — Track metrics
- `tasks.trigger_learning_loop` — Generate remixes
- `tasks.aggregate_daily_stats` — Daily aggregation

**What it does:**
- Calculates viral score from raw metrics
- Analyzes performance
- Identifies high performers
- **Automatically triggers learning loop** if viral

**Input:**
```python
track_post_performance.apply_async(
    args=[post_id, views, engagement, clicks, shares, comments, hook, idea]
)
```

**Output (on success):**
```python
{
    "post_id": "post_123",
    "metrics": {
        "viral_score": 50,
        "performance_tier": "high"
    },
    "is_high_performer": True,
    "learning_triggered": {
        "task_id": "learning_abc123",
        "remix_type": "escalation"
    }
}
```

**Timeout:** 5 minutes

**Concurrency:** 2

---

## 🔄 Task Flow Examples

### Example 1: Full Content Generation

```
User: POST /ideas/create
   ↓ (immediate response with task_id)
┌──────────────────────────┐
│ Redis Queue              │
│ content_pipeline queue   │
└──────────────────────────┘
   ↓
Worker-pipeline picks up task
   ↓
IdeaEngine.process()        (1 sec)
HookEngine.generate_all()   (2 sec)
ScriptEngine.build()        (1 sec)
   ↓
Result stored in Redis
   ↓
User: GET /ideas/status/{task_id}
   ↓ (immediate response with result)
```

**Total time:** <5 seconds (but user doesn't wait)

---

### Example 2: Render + Analytics Loop

```
User: POST /scripts/render
   ↓ (immediate response with render_task_id)
┌──────────────────────────┐
│ Redis Queue              │
│ render queue             │
└──────────────────────────┘
   ↓
Worker-render picks up task
   ↓
Call HeyGen API
Poll until complete         (~120 seconds)
   ↓
Store video URL
   ↓
External service: POST /render/complete
   ↓ (webhook callback)
┌──────────────────────────┐
│ Redis Queue              │
│ analytics queue          │
└──────────────────────────┘
   ↓
Worker-analytics processes
   ↓
Update DB, log metrics
   ↓
Done
```

**Total time:** 2-3 minutes (async, user continues working)

---

## 🚀 Running Workers

### Docker (Recommended)

```bash
# All-in-one
docker-compose up

# Separate terminals
docker-compose up api db redis
docker-compose up worker-pipeline
docker-compose up worker-render
docker-compose up worker-analytics
docker-compose up flower
```

### Local Development

```bash
# Terminal 1: API
uvicorn app.main:app --reload

# Terminal 2: Pipeline worker
celery -A app.workers.celery_app worker -Q content_pipeline --loglevel=info

# Terminal 3: Render worker
celery -A app.workers.celery_app worker -Q render --loglevel=info

# Terminal 4: Analytics worker
celery -A app.workers.celery_app worker -Q analytics --loglevel=info

# Terminal 5: Monitoring (optional)
celery -A app.workers.celery_app flower
# Open http://localhost:5555
```

---

## 📊 Monitoring

### Flower UI

Open `http://localhost:5555` to see:
- Active tasks
- Completed tasks
- Failed tasks
- Worker stats
- Task history
- Task details

---

## ⚙️ Configuration

**File:** `app/workers/celery_app.py`

Key settings:

```python
broker="redis://redis:6379/0"           # Message queue
backend="redis://redis:6379/1"          # Result storage
task_serializer="json"                  # Format
timezone="UTC"
task_time_limit=30 * 60                 # 30 min hard limit
task_soft_time_limit=25 * 60            # 25 min soft limit
worker_prefetch_multiplier=4            # Load balance
worker_max_tasks_per_child=1000         # Memory management
```

---

## 🔄 Queues

Three dedicated queues:

| Queue | Worker | Tasks | Concurrency |
|-------|--------|-------|-------------|
| `content_pipeline` | worker-pipeline | Content generation | 2 |
| `render` | worker-render | Video rendering | 1 |
| `analytics` | worker-analytics | Metrics, learning | 2 |

This separation prevents one heavy task type from blocking others.

---

## 🔥 Error Handling

### Automatic Retries

```python
@celery_app.task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5}
)
```

Failed tasks automatically retry (with 5-second delay between attempts).

### Task States

- **PENDING** — Waiting in queue
- **PROCESSING** — Currently running
- **SUCCESS** — Completed successfully
- **FAILURE** — Failed after retries
- **RETRY** — Retrying after failure

---

## 📈 Performance Tuning

### Adjust Concurrency

```bash
# More concurrent tasks (higher CPU usage)
celery -A app.workers.celery_app worker -Q content_pipeline --concurrency=4

# Single-threaded (safe for I/O)
celery -A app.workers.celery_app worker -Q content_pipeline --concurrency=1
```

### Prefetch Multiplier

```python
# Load balance better (default 4)
worker_prefetch_multiplier=2  # Workers grab fewer tasks at a time
```

### Memory Management

```python
# Restart worker after N tasks to prevent memory leaks
worker_max_tasks_per_child=1000
```

---

## 🧪 Testing Workers

```bash
# Test task directly
from app.workers.content_pipeline_worker import generate_content_pipeline

task = generate_content_pipeline.apply_async(
    args=["user_123", "I made $1M in 90 days", "manual"]
)

# Poll result
result = task.get(timeout=10)
print(result)
```

---

## 🚨 Common Issues

### "Task not found in registry"
**Solution:** Import workers in `celery_app.py`
```python
celery_app.autodiscover_tasks(["app.workers"])
```

### "Connection refused to Redis"
**Solution:** Ensure Redis is running
```bash
docker-compose up redis
# or
redis-cli ping  # should return PONG
```

### "Worker idle"
**Solution:** Ensure queue exists
```bash
celery -A app.workers.celery_app worker -Q content_pipeline -l info
```

### Memory growing unbounded
**Solution:** Set `worker_max_tasks_per_child`
```python
worker_max_tasks_per_child=1000
```

---

## 📝 Adding New Workers

1. Create new file: `app/workers/my_worker.py`
2. Define Celery task:
```python
@celery_app.task(name="tasks.my_task")
def my_task(arg1, arg2):
    return {"result": "..."}
```
3. Run new worker:
```bash
celery -A app.workers.celery_app worker -Q my_queue --loglevel=info
```
4. Queue task from API:
```python
my_task.apply_async(args=[arg1, arg2], queue="my_queue")
```

---

## 🎯 Production Checklist

- [ ] Redis configured with persistence
- [ ] Multiple workers running (redundancy)
- [ ] Flower monitoring enabled
- [ ] Error alerting set up
- [ ] Task timeouts configured
- [ ] Dead letter queue for failed tasks
- [ ] Concurrency tuned for your hardware
- [ ] Memory limits set per worker
