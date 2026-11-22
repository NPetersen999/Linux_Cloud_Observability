"""Query a public JSON REST API plus local host metrics and emit JSON lines."""

import datetime
import json
import os
import shutil
import sys
import urllib.error
import urllib.request

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=32.7767&longitude=-96.7970&current_weather=true"
)
LOG_PATH = "/var/log/observability_api_check.jsonl"


def get_disk_used_pct(path: str = "/") -> float:
    usage = shutil.disk_usage(path)
    if usage.total == 0:
        return 0.0
    return round((usage.used / usage.total) * 100, 2)


def fetch_json_api(url: str, timeout: int = 5) -> dict:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "observability-lab-linux/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = resp.status
            raw_body = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw_body)
            current = parsed.get("current_weather", {}) if isinstance(parsed, dict) else {}
            return {
                "ok": True,
                "status_code": status_code,
                "current_weather": {
                    "temperature_c": current.get("temperature"),
                    "windspeed_kmh": current.get("windspeed"),
                    "weathercode": current.get("weathercode"),
                },
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status_code": exc.code,
            "current_weather": None,
            "error": f"HTTP {exc.code}: {exc.reason}",
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {
            "ok": False,
            "status_code": None,
            "current_weather": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    load_1m, load_5m, load_15m = [round(val, 2) for val in os.getloadavg()]
    api_result = fetch_json_api(API_URL)

    record = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "host": os.uname().nodename,
        "load_average": {
            "1m": load_1m,
            "5m": load_5m,
            "15m": load_15m,
        },
        "root_disk_used_pct": get_disk_used_pct("/"),
        "api_check": {
            "url": API_URL,
            **api_result,
        },
    }

    json_line = json.dumps(record)

    try:
        with open(LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json_line + "\n")
    except OSError as exc:
        print(f"Failed to append to {LOG_PATH}: {exc}", file=sys.stderr)
        print(json_line)
        return 1

    print(json_line)
    return 0 if api_result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
