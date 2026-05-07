# SERVICE ENGINE DOCUMENTATION

## 🧠 Core Services (Pure Logic Layer)

All services are:
- **Pure functions** — no side effects
- **No database access** — only work with data passed in
- **No async** — synchronous execution for simplicity
- **100% testable** — no external dependencies

---

## 🔧 SERVICE ARCHITECTURE

```
IdeaEngine → HookEngine → ScriptEngine
                              ↓
                        AnalyticsEngine ← PostMetrics
                              ↓
                        RemixEngine → (feedback loop)
```

---

## 📍 SERVICE BREAKDOWN

### 1. **IdeaEngine** (`idea_engine.py`)

**Responsibility:** Validate, categorize, and score raw ideas

**Input:** Raw text string + source

**Output:** `ProcessedIdea` with:
- Validated text
- Category (music, story, ai, hustle, brand)
- Viral score (0-1)
- Confidence scores per category

**Key Methods:**
```python
IdeaEngine.validate_input(text: str) → bool
IdeaEngine.categorize(text: str) → str
IdeaEngine.process(raw_input: str, source: str) → ProcessedIdea
```

**Example:**
```python
from app.services.idea_engine import IdeaEngine

idea = IdeaEngine.process(
    "I lost everything in 24 hours but here's what I learned",
    source="manual"
)

print(idea.category)  # "story"
print(idea.viral_score)  # 0.75
```

---

### 2. **HookEngine** (`hook_engine.py`)

**Responsibility:** Generate multiple viral hooks from ideas

**Input:** Idea text + category + desired count

**Output:** List of `GeneratedHook` objects with:
- Hook text
- Hook type (shock, story, authority, confession)
- Variants (2-3 variations)
- Intensity score

**Key Methods:**
```python
HookEngine.generate_for_type(idea_text: str, hook_type: str) → List[GeneratedHook]
HookEngine.generate_all_types(idea_text: str, total_hooks: int) → List[GeneratedHook]
HookEngine.rank_hooks_by_characteristics(hooks: List) → List[GeneratedHook]
```

**Example:**
```python
from app.services.hook_engine import HookEngine

hooks = HookEngine.generate_all_types(
    "I lost everything in 24 hours",
    total_hooks=8
)

for hook in hooks:
    print(f"[{hook.hook_type}] {hook.text}")
    print(f"  Variants: {hook.variants}")
```

---

### 3. **ScriptEngine** (`script_engine.py`)

**Responsibility:** Build structured video scripts from hooks

**Input:** Hook text + idea + category + pacing

**Output:** `StructuredScript` with:
- Hook section
- Setup, Body, Payoff sections
- CTA (call-to-action)
- Total duration estimate
- Pacing information

**Key Methods:**
```python
ScriptEngine.build(hook: str, idea_text: str, category: str, pacing: str) → StructuredScript
ScriptEngine.estimate_duration_for_words(word_count: int) → int
```

**Example:**
```python
from app.services.script_engine import ScriptEngine

script = ScriptEngine.build(
    hook="I lost everything in 24 hours",
    idea_text="The story of my startup failure",
    category="story",
    pacing="medium"
)

for section in script.sections:
    print(f"{section.title} ({section.duration_seconds}s): {section.content}")
```

---

### 4. **RemixEngine** (`remix_engine.py`)

**Responsibility:** Generate content variations from high performers

**Input:** Hook text, original idea, remix type

**Output:** List of remixed variations

**Key Methods:**
```python
RemixEngine.remix_hook(original_hook: str, remix_type: str) → List[str]
RemixEngine.remix_idea(original_idea: str, remix_type: str) → str
RemixEngine.blend_high_performers(high_performing_hooks: List, new_idea: str) → List[str]
```

**Remix Types:**
- `"variation"` — Safe mutations (perspective flip, intensifiers)
- `"escalation"` — Increase intensity (for winners)
- `"reframe"` — Different angle (for underperformers)
- `"sequel"` — Part 2 angle
- `"controversy"` — Unpopular take

**Example:**
```python
from app.services.remix_engine import RemixEngine

remixes = RemixEngine.remix_hook(
    "I lost everything in 24 hours",
    remix_type="escalation"
)

for remix in remixes:
    print(remix)
```

---

### 5. **AnalyticsEngine** (`analytics_engine.py`)

**Responsibility:** Calculate metrics and performance insights

**Input:** Raw metrics (views, engagement, clicks, shares, comments)

**Output:** `PerformanceAnalysis` with:
- Viral score
- Performance tier (low/medium/high/viral)
- Key insights
- Suggested remix type
- Hook effectiveness score

**Key Methods:**
```python
AnalyticsEngine.calculate_metrics(...) → PostMetrics
AnalyticsEngine.analyze(metrics: PostMetrics) → PerformanceAnalysis
AnalyticsEngine.extract_insights(metrics: PostMetrics) → List[str]
```

**Example:**
```python
from app.services.analytics_engine import AnalyticsEngine, PostMetrics

metrics = PostMetrics(
    views=5000,
    engagement=500,
    clicks=250,
    shares=100,
    comments=150
)

analysis = AnalyticsEngine.analyze(metrics)

print(f"Viral Score: {analysis.viral_score}")
print(f"Tier: {analysis.performance_tier}")
print(f"Insights: {analysis.key_insights}")
print(f"Suggested Remix: {analysis.suggested_remix_type}")
```

---

### 6. **Scoring utilities** (`scoring.py`)

**Responsibility:** Viral score and category confidence calculations

**Key Methods:**
```python
ScoringEngine.calculate_viral_score(text: str, source: str) → float
CategoryScorer.get_primary_category(text: str) → str
CategoryScorer.score_categories(text: str) → Dict[str, float]
```

---

## 🔄 PIPELINE ORCHESTRATION

### ContentPipeline (`pipeline.py`)

Orchestrates all services in sequence:

```python
from app.services.pipeline import ContentPipeline

# Single-stage execution
idea = ContentPipeline.execute_idea_stage("raw idea text")
hooks = ContentPipeline.execute_hook_stage(idea)
script = ContentPipeline.execute_script_stage(hooks[0], idea)

# Full pipeline
output = ContentPipeline.execute_full_pipeline("raw idea text")
# output.idea
# output.hooks
# output.script
```

### LearningFeedbackLoop (`pipeline.py`)

Connects performance back to content generation:

```python
from app.services.pipeline import LearningFeedbackLoop
from app.services.analytics_engine import PostMetrics

metrics = PostMetrics(
    views=1000, engagement=100, clicks=50, shares=20, comments=30
)

feedback = LearningFeedbackLoop.full_feedback_cycle(
    metrics=metrics,
    hook_used="Original hook text",
    idea_used="Original idea text",
    viral_threshold=10
)

# Returns:
# {
#   "analysis": {...},
#   "next_steps": {
#     "remix_type": "escalation",
#     "remixed_hooks": [...],
#     "remixed_idea": "..."
#   }
# }
```

---

## 🧪 TESTING SERVICES

Run tests:
```bash
pytest tests/test_services.py -v
```

Each service is independently testable:
```python
pytest tests/test_services.py::TestIdeaEngine -v
pytest tests/test_services.py::TestHookEngine -v
pytest tests/test_services.py::TestScriptEngine -v
```

---

## 📊 DATA FLOW EXAMPLE

```
User Input: "I made a million dollars in 90 days with AI"
    ↓
IdeaEngine.process()
    → Validates ✓
    → Categorizes: "hustle"
    → Scores: 0.82 viral potential
    ↓
ProcessedIdea {
    raw_input: "I made a million dollars...",
    category: "hustle",
    viral_score: 0.82
}
    ↓
HookEngine.generate_all_types(idea, 8)
    → Generates 8 hooks across 4 types
    ↓
GeneratedHook[] {
    [0] "I lost everything when I tried AI automation",
    [1] "This is why AI business fails for 99%",
    [2] "Everyone gets AI money wrong",
    ...
}
    ↓
ScriptEngine.build(hooks[0], idea, "hustle", "medium")
    → Builds structured script
    ↓
StructuredScript {
    hook: "...",
    sections: [Setup, Body, Payoff, CTA],
    total_duration: 45s
}
    ↓
(Ready for rendering)
```

---

## 🎯 SERVICE DESIGN PRINCIPLES

1. **Single Responsibility** — Each service has ONE job
2. **Pure Functions** — No side effects, no state
3. **Data In/Out** — Simple input objects, structured output
4. **Testable** — No external dependencies to mock
5. **Composable** — Services chain together cleanly
6. **Deterministic** — Same input = same output (mostly — hooks have randomness by design)

---

## 🚀 INTEGRATION WITH WORKERS

These services are meant to be called by **Celery workers** in production:

```python
# In app/workers/content_pipeline_worker.py
from celery import shared_task
from app.services.pipeline import ContentPipeline

@shared_task
def generate_content(user_id: str, idea_text: str):
    output = ContentPipeline.execute_full_pipeline(idea_text)
    # Save to DB
    # Queue render job
    return {"status": "complete"}
```

---

## 📈 NEXT LAYER: WORKER INTEGRATION

Services are pure logic. **Workers** handle:
- Scheduling
- Queue management
- DB persistence
- External API calls
- Error handling + retries

(Built next)
