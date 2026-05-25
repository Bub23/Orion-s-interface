import json
import os
from datetime import datetime
from uuid import uuid4


DATA_DIR = "data"
TASKS_PATH = os.path.join(DATA_DIR, "daily_tasks.json")
GOALS_PATH = os.path.join(DATA_DIR, "content_goals.json")
REVENUE_PATH = os.path.join(DATA_DIR, "daily_revenue.json")


def _ensure(path, root_key, default=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default or {"version": "1.0", root_key: []}, f, indent=2)


def _read(path, root_key, default=None):
    _ensure(path, root_key, default)
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        data = default or {"version": "1.0", root_key: []}
    data.setdefault(root_key, default.get(root_key, []) if default else [])
    return data


def _write(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def create_task(payload):
    data = _read(TASKS_PATH, "tasks")
    task = {
        "id": str(uuid4()),
        "title": str(payload.get("title", "")).strip(),
        "category": str(payload.get("category", "ops")).strip(),
        "priority": str(payload.get("priority", "normal")).strip(),
        "due_time": str(payload.get("due_time", "")).strip(),
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }
    if not task["title"]:
        return {"error": "title is required"}
    data["tasks"].append(task)
    _write(TASKS_PATH, data)
    return task


def get_tasks():
    tasks = sorted(_read(TASKS_PATH, "tasks")["tasks"], key=lambda item: item.get("created_at", ""), reverse=True)
    total = len(tasks)
    done = len([task for task in tasks if task.get("completed")])
    return {"total": total, "completed": done, "completion_percent": round((done / total) * 100, 1) if total else 0, "tasks": tasks}


def complete_task(payload):
    task_id = str(payload.get("id", "")).strip()
    data = _read(TASKS_PATH, "tasks")
    for task in data["tasks"]:
        if task.get("id") == task_id:
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            _write(TASKS_PATH, data)
            return task
    return {"error": "Task not found"}


def reset_day():
    _write(TASKS_PATH, {"version": "1.0", "tasks": []})
    return {"status": "reset", "timestamp": datetime.now().isoformat()}


def set_content_goals(payload):
    goals = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "shorts_goal": int(payload.get("shorts_goal") or 0),
        "posts_goal": int(payload.get("posts_goal") or 0),
        "leads_goal": int(payload.get("leads_goal") or 0),
        "outreach_goal": int(payload.get("outreach_goal") or 0),
        "completed_counts": payload.get("completed_counts") if isinstance(payload.get("completed_counts"), dict) else {
            "shorts": 0,
            "posts": 0,
            "leads": 0,
            "outreach": 0,
        },
    }
    _write(GOALS_PATH, goals)
    return goals


def get_content_goals():
    return _read(GOALS_PATH, "completed_counts", {
        "version": "1.0",
        "shorts_goal": 0,
        "posts_goal": 0,
        "leads_goal": 0,
        "outreach_goal": 0,
        "completed_counts": {"shorts": 0, "posts": 0, "leads": 0, "outreach": 0},
    })


def log_revenue(payload):
    data = _read(REVENUE_PATH, "entries")
    entry = {
        "id": str(uuid4()),
        "amount": float(payload.get("amount") or 0),
        "source": str(payload.get("source", "")).strip(),
        "notes": str(payload.get("notes", "")).strip(),
        "timestamp": datetime.now().isoformat(),
    }
    data["entries"].append(entry)
    _write(REVENUE_PATH, data)
    return entry


def revenue_today():
    today = datetime.now().date().isoformat()
    entries = [entry for entry in _read(REVENUE_PATH, "entries")["entries"] if str(entry.get("timestamp", "")).startswith(today)]
    return {"date": today, "total": sum(float(entry.get("amount") or 0) for entry in entries), "entries": entries}
