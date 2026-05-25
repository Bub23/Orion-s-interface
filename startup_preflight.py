import json
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_ROOT = Path(r"C:\Users\outla\OneDrive\OIRONSINTERFACE.worktrees\agents-orion-content-engine-v1")
MAIN_ENV = Path(r"C:\Users\outla\OneDrive\OIRONSINTERFACE\.env")
DATA_FILES = {
    "content_history.json": {"version": "1.0", "drafts": []},
    "meta_queue.json": {"version": "1.0", "queue": []},
    "youtube_queue.json": {"version": "1.0", "queue": []},
    "oauth_callback.json": {"version": "1.0", "updated_at": "", "result": {}},
    "youtube_token_status.json": {"version": "1.0", "status": "missing"},
    "export_pack_history.json": {"version": "1.0", "packs": []},
}
REQUIRED_IMPORTS = ["flask", "flask_cors", "dotenv", "psutil", "requests"]
OPTIONAL_IMPORTS = ["GPUtil", "openai"]
REQUIRED_FILES = [
    "templates/chat.html",
    "web_app.py",
    "content_engine.py",
    "meta_integration.py",
    "youtube_integration.py",
]
MERGE_KEYS = [
    "NVIDIA_API_KEY",
    "OPENAI_API_KEY",
    "APP_PORT",
    "META_APP_ID",
    "META_APP_SECRET",
    "META_ACCESS_TOKEN",
    "FACEBOOK_PAGE_ID",
    "INSTAGRAM_BUSINESS_ID",
    "YOUTUBE_CLIENT_SECRET_FILE",
    "YOUTUBE_CLIENT_ID",
    "YOUTUBE_CLIENT_SECRET",
    "YOUTUBE_REFRESH_TOKEN",
    "YOUTUBE_CHANNEL_ID",
]


failures = []


def report(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {name}{' - ' + detail if detail else ''}")
    if not ok:
        failures.append(name)


def load_env(path):
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def merge_env_values(worktree_env, main_env, keys):
    text = worktree_env.read_text(encoding="utf-8", errors="ignore") if worktree_env.exists() else ""
    lines = text.splitlines()
    present = {}
    for index, raw in enumerate(lines):
        if "=" not in raw or raw.strip().startswith("#"):
            continue
        key, value = raw.split("=", 1)
        present[key.strip()] = (index, value.strip().strip('"').strip("'"))

    main_values = load_env(main_env)
    merged = []

    for key in keys:
        current = present.get(key, (None, ""))[1]
        replacement = main_values.get(key, "")
        if current or not replacement:
            continue
        if key in present:
            lines[present[key][0]] = f"{key}={replacement}"
        else:
            lines.append(f"{key}={replacement}")
        merged.append(key)

    if "APP_PORT" not in present and "APP_PORT" not in merged:
        lines.append("APP_PORT=8000")
        merged.append("APP_PORT")

    worktree_env.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return merged


def ensure_json_file(path, default):
    if not path.exists():
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return True
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except json.JSONDecodeError:
        return False


def main():
    print("=" * 64)
    print("ORION STARTUP PREFLIGHT")
    print("=" * 64)

    report("Correct repo root", ROOT == EXPECTED_ROOT, str(ROOT))
    report("Python works", True, sys.version.split()[0])

    for module in REQUIRED_IMPORTS:
        try:
            __import__(module)
            report(f"Required package {module}", True)
        except Exception as error:
            report(f"Required package {module}", False, error.__class__.__name__)

    for module in OPTIONAL_IMPORTS:
        try:
            __import__(module)
            report(f"Optional package {module}", True)
        except Exception:
            print(f"WARN: Optional package {module} - MISSING")

    for rel_path in REQUIRED_FILES:
        report(f"File exists {rel_path}", (ROOT / rel_path).exists())

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    report("Data folder exists", data_dir.exists())

    for filename, default in DATA_FILES.items():
        report(f"Data file {filename}", ensure_json_file(data_dir / filename, default))

    env_path = ROOT / ".env"
    if not env_path.exists() and MAIN_ENV.exists():
        shutil.copy2(MAIN_ENV, env_path)
        report(".env copied from main repo", True)
    else:
        report(".env exists", env_path.exists())

    merged_keys = []
    if env_path.exists() and MAIN_ENV.exists():
        merged_keys = merge_env_values(env_path, MAIN_ENV, MERGE_KEYS)
        if merged_keys:
            print(f"INFO: merged missing worktree .env keys from main repo: {', '.join(merged_keys)}")
        else:
            print("INFO: no .env key merge needed")
    elif env_path.exists():
        print("WARN: main repo .env not found; no merge performed")

    env_values = load_env(env_path)
    if env_path.exists():
        report("APP_PORT", True, "SET" if env_values.get("APP_PORT") else "MISSING")

        nvidia_set = bool(env_values.get("NVIDIA_API_KEY"))
        openai_set = bool(env_values.get("OPENAI_API_KEY"))
        report("NVIDIA_API_KEY", nvidia_set, "SET" if nvidia_set else "MISSING")
        report("OPENAI_API_KEY", openai_set, "SET" if openai_set else "MISSING")
        report("At least one AI key", nvidia_set or openai_set)

        for key in [
            "META_APP_ID",
            "META_APP_SECRET",
            "META_ACCESS_TOKEN",
            "FACEBOOK_PAGE_ID",
            "INSTAGRAM_BUSINESS_ID",
            "YOUTUBE_CLIENT_SECRET_FILE",
            "YOUTUBE_CLIENT_ID",
            "YOUTUBE_CLIENT_SECRET",
            "YOUTUBE_REFRESH_TOKEN",
            "YOUTUBE_CHANNEL_ID",
        ]:
            print(f"INFO: {key} - {'SET' if env_values.get(key) else 'MISSING'}")

    print("=" * 64)
    if failures:
        print("PREFLIGHT RESULT: FAIL")
        print("Fix these checks:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PREFLIGHT RESULT: PASS")
    print("Run Orion with: python web_app.py")
    print("Dashboard: http://localhost:8000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
