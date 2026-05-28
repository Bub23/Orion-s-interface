import os
import json
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

from run_engine import RunStore, RemixService, VoiceBridge
from web_app import app


def load_rvc_adapter():
    adapter_path = Path(r"C:\REAPER_LAB\orion_rvc_adapter.py")
    assert_true(adapter_path.exists(), "local Orion RVC adapter file missing")
    spec = importlib.util.spec_from_file_location("orion_rvc_adapter", adapter_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def test_empty_directory_path_storage():
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            store = RunStore("runs_test.json")
            run = store.create_run({"type": "content", "title": "No directory path"})
            assert_true(os.path.exists("runs_test.json"), "storage file was not created")
            assert_true(run["status"] == "queued", "run status mismatch")
        finally:
            os.chdir(cwd)


def test_run_crud_and_approval():
    with tempfile.TemporaryDirectory() as tmp:
        store = RunStore(os.path.join(tmp, "runs.json"))
        run = store.create_run({
            "type": "hook",
            "title": "Approval Test",
            "input_text": "Build the hook.",
        })
        assert_true(store.get_run(run["run_id"])["title"] == "Approval Test", "created run missing")
        assert_true(len(store.list_runs()) == 1, "run list mismatch")
        approved = store.update_run(run["run_id"], {"status": "approved"})
        assert_true(approved["status"] == "approved", "approval status mismatch")


def test_remix_service_returns_output():
    with tempfile.TemporaryDirectory() as tmp:
        store = RunStore(os.path.join(tmp, "runs.json"))
        service = RemixService(store)
        result = service.remix(
            "This is a basic content idea about building faster.",
            "youtube_shorts",
            "more_outlaw",
            8,
            "Bub Outlaw / 304 Reaper",
        )
        assert_true(result["status"] == "finished", "remix did not finish")
        assert_true(result["run_id"], "remix run id missing")
        assert_true("Outlaw" in result["output"] or "outlaw" in result["output"], "remix output not rewritten")


def test_voice_status_is_honest():
    bridge = VoiceBridge(RunStore(os.path.join(tempfile.gettempdir(), "orion_voice_status_test.json")))
    status = bridge.status()
    any_path_exists = any(item["exists"] for item in status["paths"])
    expected = "Voice engine detected" if any_path_exists else "Voice engine not connected"
    assert_true(status["message"] == expected, "voice status faked path state")


def test_missing_voice_script_reports_bridge_waiting():
    old_value = os.environ.pop("ORION_VOICE_SCRIPT", None)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            store = RunStore(os.path.join(tmp, "runs.json"))
            bridge = VoiceBridge(store)
            run = bridge.run({"text": "missing bridge test", "voice_profile": "ORION"})
            assert_true(run["status"] == "needs_approval", "missing script should need approval")
            assert_true(run["error_message"] == "bridge_waiting", "missing script did not report bridge_waiting")
            assert_true(store.get_run(run["run_id"])["error_message"] == "bridge_waiting", "voice run was not stored")
    finally:
        if old_value is not None:
            os.environ["ORION_VOICE_SCRIPT"] = old_value


def test_configured_voice_script_executes_and_parses_stdout_json():
    bridge_path = Path(r"C:\REAPER_LAB\orion_voice_bridge.py")
    assert_true(bridge_path.exists(), "local Orion voice bridge file missing")
    old_value = os.environ.get("ORION_VOICE_SCRIPT")
    old_backend = os.environ.get("ORION_RVC_BACKEND_CMD")
    os.environ["ORION_VOICE_SCRIPT"] = str(bridge_path)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            fake_backend = Path(tmp) / "fake_success_backend.py"
            fake_backend.write_text(
                "from pathlib import Path\n"
                "import sys\n"
                "out=Path(sys.argv[1]) / 'dummy.wav'\n"
                "out.write_bytes(b'RIFFdummyWAVE')\n"
                "print('created', out)\n",
                encoding="utf-8",
            )
            os.environ["ORION_RVC_BACKEND_CMD"] = f'"{sys.executable}" "{fake_backend}" "{{output_dir}}"'
            store = RunStore(os.path.join(tmp, "runs.json"))
            bridge = VoiceBridge(store)
            run = bridge.run({"text": "configured bridge test", "voice_profile": "BUB_OUTLAW"})
            output = json.loads(run["output_text"])
            assert_true(run["status"] == "finished", "configured fake backend should finish with real dummy audio")
            assert_true(output["return_code"] == 0, "bridge return code was not captured")
            assert_true(output["bridge_status"] == "finished", "stdout JSON status was not parsed")
            assert_true(output["request_file"], "request_file missing from parsed bridge output")
            assert_true(Path(output["request_file"]).exists(), "request_file was not written")
            assert_true(output["audio_file"] and Path(output["audio_file"]).exists(), "existing audio_file was not returned")
            assert_true(store.get_run(run["run_id"])["output_text"], "voice run result was not stored")
    finally:
        if old_backend is None:
            os.environ.pop("ORION_RVC_BACKEND_CMD", None)
        else:
            os.environ["ORION_RVC_BACKEND_CMD"] = old_backend
        if old_value is None:
            os.environ.pop("ORION_VOICE_SCRIPT", None)
        else:
            os.environ["ORION_VOICE_SCRIPT"] = old_value


def test_bridge_generator_missing_stays_honest():
    bridge_path = Path(r"C:\REAPER_LAB\orion_voice_bridge.py")
    old_disable = os.environ.get("ORION_RVC_DISABLE_BACKEND")
    old_backend = os.environ.get("ORION_RVC_BACKEND_CMD")
    os.environ["ORION_RVC_DISABLE_BACKEND"] = "1"
    os.environ.pop("ORION_RVC_BACKEND_CMD", None)
    try:
        payload = {"run_id": "test-generator-missing", "text": "missing generator", "voice_profile": "BUB_OUTLAW"}
        completed = subprocess.run(
            [sys.executable, str(bridge_path)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        result = json.loads(completed.stdout)
        assert_true(completed.returncode == 0, "generator_missing should be a clean bridge response")
        assert_true(result["status"] == "generator_missing", "generator missing status not returned")
        assert_true(result["audio_file"] is None, "audio_file should not be returned for missing generator")
        assert_true(Path(result["request_file"]).exists(), "bridge did not write request_file")
    finally:
        if old_disable is None:
            os.environ.pop("ORION_RVC_DISABLE_BACKEND", None)
        else:
            os.environ["ORION_RVC_DISABLE_BACKEND"] = old_disable
        if old_backend is None:
            os.environ.pop("ORION_RVC_BACKEND_CMD", None)
        else:
            os.environ["ORION_RVC_BACKEND_CMD"] = old_backend


def test_adapter_certifi_path_injection():
    adapter = load_rvc_adapter()
    env, certifi_path, error = adapter.build_applio_env()
    assert_true(not error, f"certifi detection failed: {error}")
    assert_true(certifi_path and Path(certifi_path).exists(), "certifi path was not detected")
    assert_true(env["SSL_CERT_FILE"] == certifi_path, "SSL_CERT_FILE was not injected")
    assert_true(env["REQUESTS_CA_BUNDLE"] == certifi_path, "REQUESTS_CA_BUNDLE was not injected")
    assert_true(env["PYTHONHTTPSVERIFY"] == "1", "PYTHONHTTPSVERIFY was not set")


def test_bridge_ssl_error_returns_tts_ssl_error():
    bridge_path = Path(r"C:\REAPER_LAB\orion_voice_bridge.py")
    with tempfile.TemporaryDirectory() as tmp:
        ssl_backend = Path(tmp) / "ssl_backend.py"
        ssl_backend.write_text(
            "import sys\n"
            "print('SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate')\n"
            "sys.exit(1)\n",
            encoding="utf-8",
        )
        old_backend = os.environ.get("ORION_RVC_BACKEND_CMD")
        os.environ["ORION_RVC_BACKEND_CMD"] = f'"{sys.executable}" "{ssl_backend}" "{{output_dir}}"'
        try:
            completed = subprocess.run(
                [sys.executable, str(bridge_path)],
                input=json.dumps({"run_id": "test-ssl-error", "text": "ssl fail", "voice_profile": "ORION"}),
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            result = json.loads(completed.stdout)
            assert_true(result["status"] == "tts_ssl_error", "SSL failure should return tts_ssl_error")
            assert_true(result["audio_file"] is None, "SSL failure must not return audio_file")
            assert_true("Edge TTS SSL" in result["message"], "SSL failure message was not specific")
        finally:
            if old_backend is None:
                os.environ.pop("ORION_RVC_BACKEND_CMD", None)
            else:
                os.environ["ORION_RVC_BACKEND_CMD"] = old_backend


class FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_text_only_uses_windows_sapi_path():
    adapter = load_rvc_adapter()
    original_run = adapter.subprocess.run
    original_sapi = adapter.create_windows_sapi_wav
    with tempfile.TemporaryDirectory() as tmp:
        cert_path = Path(tmp) / "cacert.pem"
        cert_path.write_text("dummy cert", encoding="utf-8")

        def fake_sapi(text, output_path, payload=None):
            Path(output_path).write_bytes(b"RIFFofflineWAVE")
            return {
                "ok": True,
                "message": "Windows SAPI created offline_tts_source.wav.",
                "return_code": 0,
                "stdout": "",
                "stderr": "",
                "command": ["powershell", "fake"],
            }

        def fake_run(command, **kwargs):
            if "-c" in command:
                return FakeCompleted(0, str(cert_path), "")
            if "infer" in command:
                output_path = Path(command[command.index("--output_path") + 1])
                output_path.write_bytes(b"RIFFrvcWAVE")
                return FakeCompleted(0, "infer ok", "")
            return FakeCompleted(1, "", "unexpected command")

        adapter.create_windows_sapi_wav = fake_sapi
        adapter.subprocess.run = fake_run
        try:
            result = adapter.run_generation({
                "run_id": "unit-windows-sapi",
                "output_dir": tmp,
                "text": "offline text test",
                "voice_profile": "BUB_OUTLAW",
            })
            assert_true(result["status"] == "finished", "text-only run should finish when infer output exists")
            assert_true(result["tts_mode"] == "windows_sapi", "text-only run did not use windows_sapi")
            assert_true(Path(result["source_audio_path"]).name == "offline_tts_source.wav", "offline source wav mismatch")
            assert_true(Path(result["audio_file"]).exists(), "final audio file was not created")
        finally:
            adapter.subprocess.run = original_run
            adapter.create_windows_sapi_wav = original_sapi


def test_audio_input_path_skips_tts_and_runs_direct_rvc():
    adapter = load_rvc_adapter()
    original_run = adapter.subprocess.run
    original_sapi = adapter.create_windows_sapi_wav
    with tempfile.TemporaryDirectory() as tmp:
        cert_path = Path(tmp) / "cacert.pem"
        cert_path.write_text("dummy cert", encoding="utf-8")
        source_audio = Path(tmp) / "source.wav"
        source_audio.write_bytes(b"RIFFsourceWAVE")

        def fail_sapi(text, output_path, payload=None):
            raise AssertionError("SAPI should not run when audio_input_path exists")

        def fake_run(command, **kwargs):
            if "-c" in command:
                return FakeCompleted(0, str(cert_path), "")
            if "infer" in command:
                output_path = Path(command[command.index("--output_path") + 1])
                output_path.write_bytes(b"RIFFdirectWAVE")
                return FakeCompleted(0, "direct infer ok", "")
            return FakeCompleted(1, "", "unexpected command")

        adapter.create_windows_sapi_wav = fail_sapi
        adapter.subprocess.run = fake_run
        try:
            result = adapter.run_generation({
                "run_id": "unit-direct-rvc",
                "output_dir": tmp,
                "audio_input_path": str(source_audio),
                "voice_profile": "BUB_OUTLAW",
            })
            assert_true(result["status"] == "finished", "direct RVC should finish when output exists")
            assert_true(result["tts_mode"] == "audio_input_path", "direct RVC did not report audio_input_path mode")
            assert_true(result["source_audio_path"] == str(source_audio), "direct RVC source path mismatch")
            assert_true(Path(result["audio_file"]).exists(), "direct RVC audio file was not created")
        finally:
            adapter.subprocess.run = original_run
            adapter.create_windows_sapi_wav = original_sapi


def test_missing_offline_tts_returns_tts_unavailable():
    adapter = load_rvc_adapter()
    original_run = adapter.subprocess.run
    original_sapi = adapter.create_windows_sapi_wav
    old_fallback = os.environ.pop("ORION_RVC_ALLOW_EDGE_TTS_FALLBACK", None)
    with tempfile.TemporaryDirectory() as tmp:
        cert_path = Path(tmp) / "cacert.pem"
        cert_path.write_text("dummy cert", encoding="utf-8")

        def fake_sapi(text, output_path, payload=None):
            return {
                "ok": False,
                "message": "Windows SAPI unavailable",
                "return_code": 5,
                "stdout": "",
                "stderr": "sapi failed",
                "command": ["powershell", "fake"],
            }

        def fake_run(command, **kwargs):
            if "-c" in command:
                return FakeCompleted(0, str(cert_path), "")
            return FakeCompleted(1, "", "unexpected command")

        adapter.create_windows_sapi_wav = fake_sapi
        adapter.subprocess.run = fake_run
        try:
            result = adapter.run_generation({
                "run_id": "unit-sapi-missing",
                "output_dir": tmp,
                "text": "offline text test",
                "voice_profile": "BUB_OUTLAW",
            })
            assert_true(result["status"] == "tts_unavailable", "missing SAPI should return tts_unavailable")
            assert_true(result["audio_file"] is None, "missing SAPI must not return audio_file")
            assert_true(result["tts_mode"] == "none", "missing SAPI should report no TTS mode")
        finally:
            adapter.subprocess.run = original_run
            adapter.create_windows_sapi_wav = original_sapi
            if old_fallback is not None:
                os.environ["ORION_RVC_ALLOW_EDGE_TTS_FALLBACK"] = old_fallback


def test_failed_voice_script_returns_clean_error():
    with tempfile.TemporaryDirectory() as tmp:
        bad_script = Path(tmp) / "bad_voice_bridge.py"
        bad_script.write_text(
            "import sys\nprint('{\"ok\": false, \"status\": \"error\", \"error\": \"boom\"}')\nsys.exit(3)\n",
            encoding="utf-8",
        )
        old_value = os.environ.get("ORION_VOICE_SCRIPT")
        os.environ["ORION_VOICE_SCRIPT"] = str(bad_script)
        try:
            store = RunStore(os.path.join(tmp, "runs.json"))
            bridge = VoiceBridge(store)
            run = bridge.run({"text": "failure bridge test", "voice_profile": "ORION"})
            output = json.loads(run["output_text"])
            assert_true(run["status"] == "failed", "failed script should mark run failed")
            assert_true(output["return_code"] == 3, "failed return code was not captured")
            assert_true("boom" in run["error_message"], "clean script error was not surfaced")
        finally:
            if old_value is None:
                os.environ.pop("ORION_VOICE_SCRIPT", None)
            else:
                os.environ["ORION_VOICE_SCRIPT"] = old_value


def test_bridge_command_failure_is_clean():
    bridge_path = Path(r"C:\REAPER_LAB\orion_voice_bridge.py")
    with tempfile.TemporaryDirectory() as tmp:
        fail_backend = Path(tmp) / "fail_backend.py"
        fail_backend.write_text("import sys\nprint('backend failed')\nsys.exit(7)\n", encoding="utf-8")
        old_backend = os.environ.get("ORION_RVC_BACKEND_CMD")
        os.environ["ORION_RVC_BACKEND_CMD"] = f'"{sys.executable}" "{fail_backend}" "{{output_dir}}"'
        try:
            completed = subprocess.run(
                [sys.executable, str(bridge_path)],
                input=json.dumps({"run_id": "test-failure", "text": "fail", "voice_profile": "ORION"}),
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            result = json.loads(completed.stdout)
            assert_true(completed.returncode == 1, "bridge should return failure code for generator error")
            assert_true(result["status"] == "error", "generator failure should return error status")
            assert_true(result["audio_file"] is None, "failed generator must not return audio_file")
            assert_true(result["generator"]["return_code"] == 7, "backend failure return code missing")
        finally:
            if old_backend is None:
                os.environ.pop("ORION_RVC_BACKEND_CMD", None)
            else:
                os.environ["ORION_RVC_BACKEND_CMD"] = old_backend


def test_bridge_ignores_missing_audio_file_from_backend():
    bridge_path = Path(r"C:\REAPER_LAB\orion_voice_bridge.py")
    with tempfile.TemporaryDirectory() as tmp:
        liar_backend = Path(tmp) / "liar_backend.py"
        liar_backend.write_text("import sys\nprint('no audio created')\nsys.exit(0)\n", encoding="utf-8")
        old_backend = os.environ.get("ORION_RVC_BACKEND_CMD")
        os.environ["ORION_RVC_BACKEND_CMD"] = f'"{sys.executable}" "{liar_backend}" "{{output_dir}}"'
        try:
            completed = subprocess.run(
                [sys.executable, str(bridge_path)],
                input=json.dumps({"run_id": "test-no-audio", "text": "no audio", "voice_profile": "ORION"}),
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            result = json.loads(completed.stdout)
            assert_true(result["audio_file"] is None, "bridge returned non-existent audio file")
            assert_true(result["status"] == "error", "missing audio should not be finished")
        finally:
            if old_backend is None:
                os.environ.pop("ORION_RVC_BACKEND_CMD", None)
            else:
                os.environ["ORION_RVC_BACKEND_CMD"] = old_backend


def test_flask_run_remix_voice_routes():
    client = app.test_client()

    create_response = client.post("/api/runs", json={
        "type": "content",
        "title": "Route Run",
        "input_text": "Route test input",
    })
    assert_true(create_response.status_code == 201, "POST /api/runs failed")
    run = create_response.get_json()

    list_response = client.get("/api/runs")
    assert_true(list_response.status_code == 200, "GET /api/runs failed")
    assert_true("runs" in list_response.get_json(), "runs array missing")

    approve_response = client.post(f"/api/runs/{run['run_id']}/approve", json={})
    assert_true(approve_response.status_code == 200, "approve route failed")
    assert_true(approve_response.get_json()["status"] == "approved", "approve route did not update status")

    remix_response = client.post("/api/remix", json={
        "text": "Make this content stronger for the audience.",
        "platform": "youtube_shorts",
        "style": "more_viral",
        "intensity": 7,
    })
    assert_true(remix_response.status_code == 201, "POST /api/remix failed")
    assert_true(remix_response.get_json()["output"], "remix output missing")

    voice_status_response = client.get("/api/voice/status")
    assert_true(voice_status_response.status_code == 200, "GET /api/voice/status failed")
    assert_true(voice_status_response.get_json()["message"] in ("Voice engine detected", "Voice engine not connected"), "voice message invalid")

    output_root = Path(r"C:\REAPER_LAB\OUTPUTS")
    output_root.mkdir(parents=True, exist_ok=True)
    test_audio = output_root / "route-test-voice-output.wav"
    test_audio.write_bytes(b"RIFFrouteWAVE")
    output_response = client.get("/api/voice/output/route-test-voice-output.wav")
    assert_true(output_response.status_code == 200, "voice output file route failed")
    blocked_response = client.get("/api/voice/output/../orion_voice_bridge.py")
    assert_true(blocked_response.status_code in (403, 404), "voice output route allowed unsafe path")


if __name__ == "__main__":
    test_empty_directory_path_storage()
    test_run_crud_and_approval()
    test_remix_service_returns_output()
    test_voice_status_is_honest()
    test_missing_voice_script_reports_bridge_waiting()
    test_bridge_generator_missing_stays_honest()
    test_adapter_certifi_path_injection()
    test_bridge_ssl_error_returns_tts_ssl_error()
    test_text_only_uses_windows_sapi_path()
    test_audio_input_path_skips_tts_and_runs_direct_rvc()
    test_missing_offline_tts_returns_tts_unavailable()
    test_configured_voice_script_executes_and_parses_stdout_json()
    test_failed_voice_script_returns_clean_error()
    test_bridge_command_failure_is_clean()
    test_bridge_ignores_missing_audio_file_from_backend()
    test_flask_run_remix_voice_routes()
    print("All run/remix/voice tests passed")
