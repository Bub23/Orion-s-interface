import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4


RUN_STATUSES = {
    "queued",
    "running",
    "needs_approval",
    "approved",
    "finished",
    "failed",
}

RUN_TYPES = {
    "content",
    "song",
    "hook",
    "caption",
    "short_script",
    "youtube_title",
    "remix",
    "voice",
    "mastering",
    "upload_plan",
}

REMIX_PLATFORMS = {
    "youtube",
    "youtube_shorts",
    "tiktok",
    "instagram",
    "facebook",
    "threads",
    "song_hook",
    "song_verse",
    "promo_post",
    "dm_offer",
}

REMIX_STYLES = {
    "harder",
    "cleaner",
    "more_outlaw",
    "more_emotional",
    "more_sales_focused",
    "shorter",
    "longer",
    "more_viral",
    "more_country_rap",
    "more_storytelling",
}

VOICE_PROFILES = ["BUB_OUTLAW", "ORION", "VALE", "CUSTOM"]
VOICE_MODES = [
    "clone",
    "convert",
    "narrate",
    "song_hook",
    "ad_libs",
    "demo_vocal",
    "master_voice_output",
]
VOICE_PATHS = [
    r"C:\REAPER_LAB",
    r"C:\REAPER_LAB\MODELS",
    r"C:\REAPER_LAB\RVC",
    r"C:\REAPER_LAB\OUTPUTS",
]


def _now():
    return datetime.now().isoformat()


def ensure_directory_for_file(path):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


class RunStore:
    def __init__(self, storage_path="data/runs.json"):
        self.storage_path = storage_path
        self._ensure_file()

    def _ensure_file(self):
        ensure_directory_for_file(self.storage_path)
        if not os.path.exists(self.storage_path):
            self._write({"version": "1.0", "runs": []})

    def _read(self):
        try:
            with open(self.storage_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            data = {"version": "1.0", "runs": []}
        data.setdefault("runs", [])
        return data

    def _write(self, data):
        ensure_directory_for_file(self.storage_path)
        with open(self.storage_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def list_runs(self):
        runs = self._read()["runs"]
        return sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True)

    def get_run(self, run_id):
        for run in self._read()["runs"]:
            if run.get("run_id") == run_id:
                return run
        return None

    def create_run(self, payload):
        run_type = str(payload.get("type") or "content").strip()
        if run_type not in RUN_TYPES:
            raise ValueError(f"Unsupported run type: {run_type}")

        status = str(payload.get("status") or "queued").strip()
        if status not in RUN_STATUSES:
            raise ValueError(f"Unsupported run status: {status}")

        timestamp = _now()
        run = {
            "run_id": str(uuid4()),
            "type": run_type,
            "title": str(payload.get("title") or f"{run_type} run").strip(),
            "input_text": str(payload.get("input_text") or payload.get("text") or "").strip(),
            "source_file": str(payload.get("source_file") or "").strip(),
            "platform": str(payload.get("platform") or "").strip(),
            "status": status,
            "created_at": timestamp,
            "updated_at": timestamp,
            "output_text": str(payload.get("output_text") or "").strip(),
            "output_file": str(payload.get("output_file") or "").strip(),
            "error_message": str(payload.get("error_message") or "").strip(),
        }
        data = self._read()
        data["runs"].append(run)
        self._write(data)
        return run

    def update_run(self, run_id, updates):
        data = self._read()
        for run in data["runs"]:
            if run.get("run_id") == run_id:
                for key, value in updates.items():
                    if key in run:
                        run[key] = value
                run["updated_at"] = _now()
                self._write(data)
                return run
        return None


class RemixService:
    def __init__(self, run_store):
        self.run_store = run_store

    def remix(self, text, platform, style, intensity=5, brand_voice=""):
        platform = platform if platform in REMIX_PLATFORMS else "youtube_shorts"
        style = style if style in REMIX_STYLES else "more_viral"
        intensity = max(1, min(10, int(float(intensity or 5))))
        original = self._clean(text)
        if not original:
            raise ValueError("text is required")

        output = self._build_output(original, platform, style, intensity, brand_voice)
        run = self.run_store.create_run({
            "type": "remix",
            "title": f"{platform} remix - {style}",
            "input_text": original,
            "platform": platform,
            "status": "finished",
            "output_text": output,
        })
        return {"run_id": run["run_id"], "status": run["status"], "output": output}

    def remix_run(self, source_run, platform="", style="more_viral", intensity=6, brand_voice=""):
        text = source_run.get("output_text") or source_run.get("input_text") or ""
        return self.remix(text, platform or source_run.get("platform") or "youtube_shorts", style, intensity, brand_voice)

    def _clean(self, text):
        text = re.sub(r"\s+", " ", str(text or "")).strip()
        filler = [
            "basically",
            "really",
            "very",
            "just",
            "kind of",
            "sort of",
            "you know",
        ]
        for word in filler:
            text = re.sub(rf"\b{re.escape(word)}\b", "", text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", text).strip()

    def _build_output(self, text, platform, style, intensity, brand_voice):
        hook = self._hook(text, style, intensity)
        body = self._style_body(text, style, intensity, brand_voice)

        if platform in ("youtube_shorts", "tiktok", "instagram"):
            return f"{hook}\n\n{body}\n\nCTA: Save this and move on it today."
        if platform == "youtube":
            return f"{hook}\n\n{body}\n\nDescription angle: show the system, the result, and the next step."
        if platform == "facebook":
            return f"{hook}\n\n{body}\n\nQuestion: where are you losing the most time right now?"
        if platform == "threads":
            return f"{hook}\n\n{body[:430]}"
        if platform == "song_hook":
            return f"{hook}\n{self._song_lines(text, style, 4)}"
        if platform == "song_verse":
            return f"{self._song_lines(text, style, 8)}\n\nHook: {hook}"
        if platform == "promo_post":
            return f"{hook}\n\n{body}\n\nOffer: DM to get the build plan."
        if platform == "dm_offer":
            return f"{hook}\n\nI saw the gap: {body}\n\nWant me to map the next move?"
        return f"{hook}\n\n{body}"

    def _hook(self, text, style, intensity):
        lead = " ".join(text.split()[:14])
        hooks = {
            "harder": "Stop playing with this.",
            "cleaner": "Here is the clean version.",
            "more_outlaw": "Outlaw rule: build it real or do not claim it.",
            "more_emotional": "This hits harder when it is your name on the line.",
            "more_sales_focused": "This is where attention turns into money.",
            "shorter": "Here is the move.",
            "longer": "The real story starts before the result.",
            "more_viral": "Most people miss this part.",
            "more_country_rap": "Mud on the boots, pressure in the booth.",
            "more_storytelling": "First, the problem looked smaller than it was.",
        }
        suffix = "!" if intensity >= 8 else "."
        return f"{hooks.get(style, 'Most people miss this part')}{suffix} {lead}"

    def _style_body(self, text, style, intensity, brand_voice):
        voice = f" Voice: {brand_voice}." if brand_voice else ""
        if style == "shorter":
            return " ".join(text.split()[:28]) + voice
        if style == "longer":
            return f"{text} The point is simple: the idea only matters when it becomes a shipped asset, a clean offer, or a run Bub can approve.{voice}"
        if style == "more_sales_focused":
            return f"{text} Turn the pain into a clear offer, make the next step obvious, and remove every weak line before it reaches the audience.{voice}"
        if style == "more_storytelling":
            return f"{text} Start with the pressure, show the decision, then land on the outcome so the audience can feel the shift.{voice}"
        if style == "more_country_rap":
            return f"{text} Keep it raw, direct, and rhythmic: pain, pride, work, proof, then the hook.{voice}"
        if style == "more_outlaw":
            return f"{text} Strip the soft language. Keep the truth, the leverage, and the action.{voice}"
        if style == "cleaner":
            return f"{text} Clear headline, clean proof, direct next step.{voice}"
        return f"{text} Make the hook stronger, remove filler, and push the strongest promise to the front.{voice}"

    def _song_lines(self, text, style, count):
        words = text.split()
        base = " ".join(words[:10]) if words else "Orion on the line"
        lines = []
        for index in range(count):
            lines.append(f"{base} / line {index + 1} / {style.replace('_', ' ')}")
        return "\n".join(lines)


class VoiceBridge:
    def __init__(self, run_store):
        self.run_store = run_store

    def status(self):
        paths = [{"path": path, "exists": os.path.exists(path)} for path in VOICE_PATHS]
        detected = any(item["exists"] for item in paths)
        script_path = os.getenv("ORION_VOICE_SCRIPT", "").strip()
        executable = script_path and os.path.exists(script_path)
        return {
            "status": "detected" if detected else "not_connected",
            "message": "Voice engine detected" if detected else "Voice engine not connected",
            "paths": paths,
            "script_path_set": bool(script_path),
            "script_path": script_path,
            "script_exists": bool(executable),
            "output_root": r"C:\REAPER_LAB\OUTPUTS" if os.path.exists(r"C:\REAPER_LAB\OUTPUTS") else "",
        }

    def profiles(self):
        return {"profiles": VOICE_PROFILES, "modes": VOICE_MODES}

    def run(self, payload):
        profile = str(payload.get("voice_profile") or payload.get("profile") or "BUB_OUTLAW").strip()
        mode = str(payload.get("mode") or "narrate").strip()
        if profile not in VOICE_PROFILES:
            profile = "CUSTOM"
        if mode not in VOICE_MODES:
            mode = "narrate"

        run = self.run_store.create_run({
            "type": "voice",
            "title": f"{profile} {mode}",
            "input_text": str(payload.get("text") or payload.get("text_to_speak") or "").strip(),
            "source_file": str(payload.get("reference_audio") or payload.get("reference_audio_path") or "").strip(),
            "status": "queued",
        })

        script_path = os.getenv("ORION_VOICE_SCRIPT", "").strip()
        if not script_path or not os.path.exists(script_path):
            message = "bridge_waiting: ORION_VOICE_SCRIPT is missing or does not point to a local executable or script."
            return self.run_store.update_run(run["run_id"], {
                "status": "needs_approval",
                "output_text": message,
                "error_message": "bridge_waiting",
            })

        try:
            bridge_payload = {
                "run_id": run["run_id"],
                "text": run["input_text"],
                "voice_profile": profile,
                "profile": profile,
                "mode": mode,
                "reference_audio": run["source_file"],
                "master_output": bool(payload.get("master_output")),
            }
            command = self._command_for_script(script_path)
            result = subprocess.run(
                command,
                input=json.dumps(bridge_payload),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            parsed = self._parse_stdout_json(result.stdout)
            output_file = str(parsed.get("audio_file") or "") if isinstance(parsed, dict) else ""
            if output_file and not Path(output_file).exists():
                output_file = ""
            summary = {
                "bridge_status": parsed.get("status", "unknown") if isinstance(parsed, dict) else "unknown",
                "message": parsed.get("message", "") if isinstance(parsed, dict) else "",
                "request_file": parsed.get("request_file", "") if isinstance(parsed, dict) else "",
                "output_dir": parsed.get("output_dir", "") if isinstance(parsed, dict) else "",
                "audio_file": output_file or None,
                "return_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "parsed_json": parsed,
            }
            if result.returncode != 0:
                return self.run_store.update_run(run["run_id"], {
                    "status": "failed",
                    "output_text": json.dumps(summary, indent=2),
                    "error_message": result.stderr.strip() or result.stdout.strip() or "Voice script failed",
                })

            status = "finished" if output_file else "needs_approval"
            return self.run_store.update_run(run["run_id"], {
                "status": status,
                "output_text": json.dumps(summary, indent=2),
                "output_file": output_file,
                "error_message": "",
            })
        except Exception as error:
            return self.run_store.update_run(run["run_id"], {
                "status": "failed",
                "error_message": str(error),
            })

    def _command_for_script(self, script_path):
        suffix = Path(script_path).suffix.lower()
        if suffix == ".py":
            return [sys.executable, script_path]
        return [script_path]

    def _parse_stdout_json(self, stdout):
        text = (stdout or "").strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            for line in reversed(text.splitlines()):
                line = line.strip()
                if not line:
                    continue
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return {"raw_stdout": text}

    def _extract_output_path(self, output):
        for token in output.split():
            if token.lower().endswith((".wav", ".mp3", ".flac", ".aiff")) and Path(token).exists():
                return token
        return ""
