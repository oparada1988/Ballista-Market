#!/usr/bin/env python3
"""Validate Ballista-Market plugin manifests and generated catalog.json."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
CATALOG_PATH = ROOT / "catalog.json"

VALID_CATEGORIES = {
    "Utility",
    "System",
    "Audio",
    "Streaming",
    "Productivity",
    "Developer",
}
VALID_RUNTIMES = {
    "ballista",
    "streamcontroller",
}
VALID_SURFACES = {
    "keys",
    "dials",
    "touchscreen",
}
VALID_DEVICES = {
    "StreamDeckOriginal",
    "StreamDeckMK2",
    "StreamDeckMini",
    "StreamDeckXL",
    "StreamDeckNeo",
    "StreamDeckPlus",
    "StreamDeckPlusXL",
    "StreamDeckPedal",
    "StreamDeckStudio",
}
REQUIRED_STR_FIELDS = [
    "id",
    "name",
    "author",
    "license",
    "version",
    "runtime",
    "category",
    "description",
    "github_url",
    "download_url",
    "icon",
    "thumbnail",
]


def check_url(url: str, pid: str, field: str, errors: list[str]) -> None:
    if not url.startswith("https://"):
        errors.append(f"[{pid}] '{field}' must start with https:// (got: {url!r})")
        return

    headers = {"User-Agent": "Ballista-Market-Validator/2.0"}
    req = urllib.request.Request(url, method="HEAD", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status >= 400:
                errors.append(f"[{pid}] '{field}' returned HTTP {resp.status}: {url}")
    except urllib.error.HTTPError as e:
        if e.code == 405:
            req_get = urllib.request.Request(url, headers={**headers, "Range": "bytes=0-0"})
            try:
                with urllib.request.urlopen(req_get, timeout=15) as r2:
                    if r2.status >= 400:
                        errors.append(f"[{pid}] '{field}' returned HTTP {r2.status}: {url}")
            except Exception as e2:
                errors.append(f"[{pid}] Failed to reach '{field}' ({url}): {e2}")
        else:
            errors.append(f"[{pid}] '{field}' returned HTTP {e.code}: {url}")
    except Exception as e:
        errors.append(f"[{pid}] Failed to reach '{field}' ({url}): {e}")


def validate_plugin_dict(
    p: dict,
    expected_dir_id: str | None,
    seen_ids: set[str],
    errors: list[str],
    check_network: bool,
) -> None:
    pid = p.get("id", expected_dir_id or "<unknown>")

    for field in REQUIRED_STR_FIELDS:
        val = p.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"[{pid}] Missing or empty required string field: '{field}'")

    if isinstance(p.get("id"), str):
        if expected_dir_id and p["id"] != expected_dir_id:
            errors.append(
                f"[{pid}] Plugin folder name '{expected_dir_id}' must exactly match 'id' ('{p['id']}')"
            )
        if p["id"] in seen_ids:
            errors.append(f"[{pid}] Duplicate plugin id")
        seen_ids.add(p["id"])

    runtime = p.get("runtime")
    if runtime and runtime not in VALID_RUNTIMES:
        errors.append(f"[{pid}] Invalid runtime '{runtime}'. Allowed: {sorted(VALID_RUNTIMES)}")

    cat = p.get("category")
    if cat and cat not in VALID_CATEGORIES:
        errors.append(f"[{pid}] Invalid category '{cat}'. Allowed: {sorted(VALID_CATEGORIES)}")

    if "short_description" in p and p["short_description"] is not None:
        if not isinstance(p["short_description"], str):
            errors.append(f"[{pid}] 'short_description' must be a string")

    for surf in p.get("surfaces", []):
        if surf not in VALID_SURFACES:
            errors.append(f"[{pid}] Invalid surface '{surf}'. Allowed: {sorted(VALID_SURFACES)}")

    for dev in p.get("compatible_devices", []):
        if dev not in VALID_DEVICES:
            errors.append(f"[{pid}] Invalid compatible_device '{dev}'. Allowed: {sorted(VALID_DEVICES)}")

    if "screenshots" in p:
        if not isinstance(p["screenshots"], list) or not all(isinstance(s, str) for s in p["screenshots"]):
            errors.append(f"[{pid}] 'screenshots' must be an array of HTTPS image URLs")
        elif len(p["screenshots"]) > 6:
            errors.append(f"[{pid}] 'screenshots' cannot exceed 6 items (got {len(p['screenshots'])})")

    if "actions" in p:
        if not isinstance(p["actions"], list):
            errors.append(f"[{pid}] 'actions' must be an array")
        else:
            for idx, act in enumerate(p["actions"]):
                if not isinstance(act, dict):
                    errors.append(f"[{pid}] actions[{idx}] must be an object")
                    continue
                if not isinstance(act.get("name"), str) or not act["name"].strip():
                    errors.append(f"[{pid}] actions[{idx}] missing required 'name'")
                for s in act.get("surfaces", []):
                    if s not in VALID_SURFACES:
                        errors.append(f"[{pid}] actions[{idx}] invalid surface '{s}'")

    if "rating" in p and p["rating"] is not None:
        if not isinstance(p["rating"], (int, float)) or not (0.0 <= float(p["rating"]) <= 5.0):
            errors.append(f"[{pid}] 'rating' must be null or a number between 0.0 and 5.0")

    if "rating_count" in p and p["rating_count"] is not None:
        if not isinstance(p["rating_count"], int) or p["rating_count"] < 0:
            errors.append(f"[{pid}] 'rating_count' must be a non-negative integer")

    if check_network:
        for url_field in ("github_url", "download_url", "icon", "thumbnail"):
            url = p.get(url_field, "")
            if url_field == "icon" and isinstance(url, str) and not url.startswith("http"):
                continue  # Allow standard GTK symbolic icon names
            if isinstance(url, str) and url.strip():
                check_url(url, pid, url_field, errors)
        for idx, shot_url in enumerate(p.get("screenshots", [])):
            if isinstance(shot_url, str) and shot_url.strip():
                check_url(shot_url, pid, f"screenshots[{idx}]", errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Ballista-Market manifests & catalog.json")
    parser.add_argument("--skip-network", action="store_true", help="Skip live HTTP reachability checks")
    parser.add_argument(
        "--check-catalog-sync",
        action="store_true",
        help="Verify catalog.json matches plugins/*/plugin.json",
    )
    args = parser.parse_args()

    errors: list[str] = []
    seen_ids: set[str] = set()
    discovered_plugins: list[dict] = []

    if not PLUGINS_DIR.is_dir():
        errors.append("Missing required 'plugins/' directory.")
    else:
        for entry in sorted(PLUGINS_DIR.iterdir(), key=lambda p: p.name.lower()):
            if not entry.is_dir():
                continue
            manifest_path = entry / "plugin.json"
            if not manifest_path.is_file():
                errors.append(f"Directory 'plugins/{entry.name}' is missing 'plugin.json'")
                continue
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"Invalid JSON in 'plugins/{entry.name}/plugin.json': {e}")
                continue
            validate_plugin_dict(
                data,
                expected_dir_id=entry.name,
                seen_ids=seen_ids,
                errors=errors,
                check_network=not args.skip_network,
            )
            discovered_plugins.append(data)

    if CATALOG_PATH.is_file():
        try:
            catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            if "plugins" not in catalog or not isinstance(catalog["plugins"], list):
                errors.append("catalog.json: top-level 'plugins' must be a JSON array")
            elif args.check_catalog_sync:
                expected_sorted = sorted(
                    discovered_plugins,
                    key=lambda p: (p.get("name", "").lower(), p.get("id", "").lower()),
                )
                if catalog["plugins"] != expected_sorted:
                    errors.append(
                        "catalog.json is out of sync with plugins/*/plugin.json. "
                        "Run `python3 scripts/build_catalog.py`."
                    )
        except Exception as e:
            errors.append(f"Invalid JSON in catalog.json: {e}")
    else:
        errors.append("Missing catalog.json at repository root.")

    if errors:
        print("Validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"Validation PASSED ({len(discovered_plugins)} plugins verified).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
