#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


BOUNDING_BOX = {
    "lamin": "45.8389",
    "lomin": "5.9962",
    "lamax": "47.8229",
    "lomax": "10.5226",
}

ENV_PATH = Path(__file__).with_name(".env")
SCHEMA_PATH = Path(__file__).with_name("opensky_poll.schema.json")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def normalize_state(state: list) -> dict:
    padded = list(state[:17]) + [None] * max(0, 17 - len(state))
    sensors = padded[12]
    if sensors is not None:
        sensors = [int(item) for item in sensors]

    return {
        "icao24": padded[0],
        "callsign": padded[1].strip() if isinstance(padded[1], str) else padded[1],
        "origin_country": padded[2],
        "time_position": padded[3],
        "last_contact": padded[4],
        "longitude": padded[5],
        "latitude": padded[6],
        "baro_altitude": padded[7],
        "on_ground": padded[8],
        "velocity": padded[9],
        "true_track": padded[10],
        "vertical_rate": padded[11],
        "sensors": sensors,
        "geo_altitude": padded[13],
        "squawk": padded[14],
        "spi": padded[15],
        "position_source": padded[16],
    }


def fetch_snapshot() -> dict:
    query = urllib.parse.urlencode(BOUNDING_BOX)
    url = f"https://opensky-network.org/api/states/all?{query}"
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.load(response)

    return {
        "time": payload.get("time"),
        "states": [normalize_state(state) for state in payload.get("states") or []],
    }


def produce_snapshot(snapshot: dict, topic: str) -> None:
    cmd = [
        "confluent",
        "kafka",
        "topic",
        "produce",
        topic,
        "--bootstrap",
        require_env("BOOTSTRAP_SERVERS"),
        "--api-key",
        require_env("KAFKA_API_KEY"),
        "--api-secret",
        require_env("KAFKA_API_SECRET"),
        "--value-format",
        "jsonschema",
        "--schema",
        str(SCHEMA_PATH),
        "--schema-registry-endpoint",
        require_env("SCHEMA_REGISTRY_URL"),
        "--schema-registry-api-key",
        require_env("SCHEMA_REGISTRY_API_KEY"),
        "--schema-registry-api-secret",
        require_env("SCHEMA_REGISTRY_API_SECRET"),
    ]
    result = subprocess.run(
        cmd,
        input=json.dumps(snapshot) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    if result.stdout.strip():
        print(result.stdout.strip(), flush=True)


def main() -> int:
    load_env_file(ENV_PATH)

    topic = require_env("TOPIC")
    interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

    print(f"Polling OpenSky every {interval_seconds}s and producing to {topic}", flush=True)

    while True:
        snapshot = fetch_snapshot()
        produce_snapshot(snapshot, topic)
        print(
            f"snapshot_time={snapshot.get('time')} states={len(snapshot.get('states') or [])}",
            flush=True,
        )
        time.sleep(interval_seconds)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("stopped", flush=True)
        raise SystemExit(0)
    except Exception as exc:
        print(str(exc), file=sys.stderr, flush=True)
        raise SystemExit(1)
