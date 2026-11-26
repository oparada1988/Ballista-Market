#!/usr/bin/env python3
"""Compile plugins/*/plugin.json into root catalog.json with Spotlight selection."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
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

# Spotlight rules:
# - New submissions stay in Spotlight for 7 days from their Git merge date.
# - When fewer than SPOTLIGHT_MIN_SLOTS plugins qualify (or during quiet weeks),
#   remaining slots backfill via deterministic weekly rotation so slides stay full.
SPOTLIGHT_WINDOW_DAYS = 7
SPOTLIGHT_MIN_SLOTS = 6
SPOTLIGHT_MAX_SLOTS = 9
SPOTLIGHT_SLIDE_SIZE = 3


def parse_iso_utc(ts: str | None) -> dt.datetime | None:
    if not ts or not isinstance(ts, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return None


def get_git_added_at(manifest_path: Path, fallback_now: dt.datetime) -> str:
    """Return the UTC ISO-8601 timestamp when a plugin manifest was first added to Git."""
    rel_path = manifest_path.relative_to(ROOT).as_posix()
    try:
        res = subprocess.run(
            [
                "git",
                "-C",
                str(ROOT),
                "log",
                "--diff-filter=A",
                "--follow",
                "--format=%cI",
                "--",
                rel_path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            lines = [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]
            if lines:
                parsed = parse_iso_utc(lines[-1])
                if parsed is not None:
                    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        pass
    return fallback_now.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_plugins(now_utc: dt.datetime | None = None) -> list[dict]:
    now = (now_utc or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
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
        # Always stamp authoritative added_at from Git merge history
        data["added_at"] = get_git_added_at(manifest_path, now)
        plugins.append(data)

    plugins.sort(key=lambda p: (p.get("name", "").lower(), p.get("id", "").lower()))
    return plugins


def is_spotlight_eligible(plugin: dict) -> bool:
    thumb = plugin.get("thumbnail")
    return isinstance(thumb, str) and thumb.strip().startswith("https://")


def weekly_sort_key(plugin_id: str, now_utc: dt.datetime) -> str:
    iso_year, iso_week, _ = now_utc.isocalendar()
    return hashlib.sha256(f"{iso_year}-W{iso_week:02d}:{plugin_id}".encode("utf-8")).hexdigest()


def compute_spotlight(plugins: list[dict], now_utc: dt.datetime | None = None) -> list[str]:
    """Select Spotlight plugin IDs: 7-day new arrivals first, backfilled via weekly rotation."""
    now = (now_utc or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    eligible = [p for p in plugins if is_spotlight_eligible(p) and isinstance(p.get("id"), str)]
    if not eligible:
        return []

    cutoff = now - dt.timedelta(days=SPOTLIGHT_WINDOW_DAYS)

    # Tier 1: New submissions within the last 7 days (newest first, native tie-break, weekly fair tie-break)
    new_arrivals: list[tuple[dt.datetime, dict]] = []
    for p in eligible:
        added = parse_iso_utc(p.get("added_at"))
        if added is not None and added >= cutoff:
            new_arrivals.append((added, p))

    new_arrivals.sort(
        key=lambda item: (
            -item[0].timestamp(),
            0 if item[1].get("runtime") == "ballista" else 1,
            weekly_sort_key(item[1]["id"], now),
        )
    )

    selected: list[str] = [p["id"] for _, p in new_arrivals[:SPOTLIGHT_MAX_SLOTS]]

    # Target slot count: at least SPOTLIGHT_MIN_SLOTS (6), or rounded up to full 3-card slides up to 9
    if len(selected) >= SPOTLIGHT_MIN_SLOTS:
        slides = (len(selected) + SPOTLIGHT_SLIDE_SIZE - 1) // SPOTLIGHT_SLIDE_SIZE
        desired = min(len(eligible), min(SPOTLIGHT_MAX_SLOTS, slides * SPOTLIGHT_SLIDE_SIZE))
    else:
        desired = min(len(eligible), SPOTLIGHT_MIN_SLOTS)

    # Fallback: rotate remaining eligible plugins deterministically by ISO week
    if len(selected) < desired:
        selected_set = set(selected)
        pool = [p for p in eligible if p["id"] not in selected_set]
        pool.sort(key=lambda p: weekly_sort_key(p["id"], now))
        for p in pool[: desired - len(selected)]:
            selected.append(p["id"])

    return selected


def build_catalog(
    timestamp: str | None = None,
    now_utc: dt.datetime | None = None,
) -> dict:
    now = (now_utc or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    updated_at = timestamp or now.strftime("%Y-%m-%dT%H:%M:%SZ")
    plugins = load_plugins(now_utc=now)
    spotlight = compute_spotlight(plugins, now_utc=now)
    return {
        "version": "2.0.0",
        "updated_at": updated_at,
        "categories": CATEGORIES,
        "spotlight": spotlight,
        "plugins": plugins,
    }


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc)
    existing_ts: str | None = None
    existing_plugins: list[dict] | None = None
    existing_spotlight: list[str] | None = None
    if CATALOG_PATH.is_file():
        try:
            old = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            existing_ts = old.get("updated_at")
            existing_plugins = old.get("plugins")
            existing_spotlight = old.get("spotlight")
        except Exception:
            pass

    new_plugins = load_plugins(now_utc=now)
    new_spotlight = compute_spotlight(new_plugins, now_utc=now)
    # Keep existing timestamp if neither plugins nor spotlight changed (idempotent daily builds)
    unchanged = (
        existing_plugins == new_plugins
        and existing_spotlight == new_spotlight
        and bool(existing_ts)
    )
    ts = existing_ts if unchanged else None
    catalog = build_catalog(timestamp=ts, now_utc=now)

    rendered = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    CATALOG_PATH.write_text(rendered, encoding="utf-8")
    print(
        f"Built {CATALOG_PATH.name} with {len(new_plugins)} plugin(s) "
        f"and {len(new_spotlight)} spotlight slot(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
