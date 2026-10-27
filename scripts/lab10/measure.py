#!/usr/bin/env python3
"""Measure explicit curl requests; no automatic polling that prevents spin-down."""
import argparse
import datetime
import json
import math
import pathlib
import statistics
import subprocess
import urllib.parse


def percentile(values, fraction):
    if not values:
        raise ValueError("No samples")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def measure_one(base_url, timeout):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(
        [
            "curl", "--silent", "--show-error",
            "--connect-timeout", "10", "--max-time", str(timeout),
            "--write-out", "\n%{json}",
            base_url.rstrip("/") + "/health",
        ],
        text=True, capture_output=True, check=False,
    )
    body, separator, metadata = result.stdout.rpartition("\n")
    if result.returncode or not separator:
        raise RuntimeError(f"curl failed (exit {result.returncode}); no valid health sample")
    info = json.loads(metadata)
    try:
        valid = json.loads(body).get("status") == "ok"
    except (ValueError, AttributeError):
        valid = False
    if info["http_code"] != 200 or not valid:
        raise RuntimeError("Health response was not HTTP 200 QuickNotes JSON; not counted as latency")
    return {
        "started_at_utc": started,
        "http_code": info["http_code"],
        "time_total_seconds": info["time_total"],
        "time_namelookup_seconds": info["time_namelookup"],
        "time_connect_seconds": info["time_connect"],
        "time_appconnect_seconds": info["time_appconnect"],
        "time_starttransfer_seconds": info["time_starttransfer"],
        "remote_ip": info["remote_ip"],
    }


def validate_base_url(value):
    parsed = urllib.parse.urlsplit(value)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise ValueError("Use an HTTP(S) origin without credentials, path, query or fragment")
    return value.rstrip("/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--label", default="warm")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.count <= 50 or not 1 <= args.timeout <= 300:
        parser.error("count must be 1..50 and timeout 1..300 seconds")
    try:
        base = validate_base_url(args.base_url)
    except ValueError as error:
        parser.error(str(error))
    if args.output.exists():
        parser.error("Output already exists; choose a new file to preserve earlier evidence")
    samples = [measure_one(base, args.timeout) for _ in range(args.count)]
    values = [sample["time_total_seconds"] for sample in samples]
    report = {
        "base_url": base, "label": args.label,
        "sample_count": len(samples), "samples": samples,
        "p50_seconds": statistics.median(values),
        "p95_seconds": percentile(values, 0.95),
        "percentile_method": "linear interpolation of ordered successful samples",
        "scope": "fresh curl process per request, including client DNS/connect/TLS",
    }
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
