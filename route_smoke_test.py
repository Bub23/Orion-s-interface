import os
import sys
from urllib.error import URLError
from urllib.request import urlopen


ROUTES = [
    "/api/status",
    "/api/health",
    "/api/system-metrics",
    "/api/content/history",
    "/api/platform/full-status",
    "/api/meta/status",
    "/api/youtube/status",
    "/api/youtube/oauth-url",
    "/api/youtube/token-status",
    "/oauth/callback?code=smoke-test&state=smoke-test",
    "/api/approval-queue",
    "/api/scheduler/items",
    "/api/export-pack/history",
]


def env_port():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8", errors="ignore") as env_file:
            for raw in env_file:
                line = raw.strip()
                if line.startswith("APP_PORT="):
                    return line.split("=", 1)[1].strip() or "8000"
    return os.getenv("APP_PORT", "8000")


def main():
    port = env_port()
    base_url = f"http://127.0.0.1:{port}"
    failures = []

    print("=" * 64)
    print(f"ORION ROUTE SMOKE TEST - {base_url}")
    print("=" * 64)

    for route in ROUTES:
        url = f"{base_url}{route}"
        try:
            with urlopen(url, timeout=8) as response:
                ok = 200 <= response.status < 300
                print(f"{'PASS' if ok else 'FAIL'}: {route} - {response.status}")
                if not ok:
                    failures.append(route)
        except URLError as error:
            print(f"FAIL: {route} - {error.reason}")
            failures.append(route)
        except Exception as error:
            print(f"FAIL: {route} - {error}")
            failures.append(route)

    print("=" * 64)
    if failures:
        print("ROUTE SMOKE RESULT: FAIL")
        return 1
    print("ROUTE SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
