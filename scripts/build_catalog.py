#!/usr/bin/env python3
"""Compile plugins/*/plugin.json into root catalog.json."""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
CATALOG_PATH = ROOT / "catalog.json"

CATEGORIES = [
    "Utility",
    "System",
    "Audio",
    "Streaming",
    "Productivity",
    "Developer",
]


def load_plugins() -> list[dict]:
    plugins: list[dict] = []
    if not PLUGINS_DIR.is_dir():
        return plugins

    for entry in sorted(PLUGINS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir():
            continue
        manifest_path = entry / "plugin.json"
        if not manifest_path.is_file():
            continue
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        plugins.append(data)

    plugins.sort(key=lambda p: (p.get("name", "").lower(), p.get("id", "").lower()))
    return plugins


def build_catalog(timestamp: str | None = None) -> dict:
    updated_at = timestamp or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "version": "2.0.0",
        "updated_at": updated_at,
        "categories": CATEGORIES,
        "plugins": load_plugins(),
    }


def main() -> int:
    existing_ts: str | None = None
    existing_plugins: list[dict] | None = None
    if CATALOG_PATH.is_file():
        try:
            old = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            existing_ts = old.get("updated_at")
            existing_plugins = old.get("plugins")
        except Exception:
            pass

    new_plugins = load_plugins()
    # Keep existing timestamp if plugin contents did not change (idempotent builds)
    ts = existing_ts if (existing_plugins == new_plugins and existing_ts) else None
    catalog = build_catalog(timestamp=ts)

    rendered = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    CATALOG_PATH.write_text(rendered, encoding="utf-8")
    print(f"Built {CATALOG_PATH.name} with {len(new_plugins)} plugin(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
