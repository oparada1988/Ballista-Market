## Plugin Submission / Update

> New to Ballista Market? Follow the step-by-step **[Publishing Guide](../docs/PUBLISHING.md)** (or **[Migrating from StreamController](../docs/MIGRATING_FROM_STREAMCONTROLLER.md)**).

- **Plugin Name:**
- **Plugin ID (must match `plugins/<id>/plugin.json` and `manifest.json`):**
- **Runtime Type:** [ ] Native Ballista (`ballista`) / [ ] StreamController (`streamcontroller`)
- **Repository URL:**
- **Submission Type:** [ ] New Plugin / [ ] Version Update

### Checklist

- [ ] Added or updated `plugins/<plugin_id>/plugin.json` (do **not** hand-edit `catalog.json` or set `added_at` — GitHub Actions computes both automatically on merge)
- [ ] `id`, `version`, and `license` match the plugin repository
- [ ] `download_url` points directly to a `.zip` archive containing `manifest.json`
- [ ] `icon`, `thumbnail`, and any `screenshots` (16:9 PNG/WebP, max 6) point to direct `https://` image URLs (e.g. `raw.githubusercontent.com/...`)
- [ ] Tested locally in Ballista (actions, Inspector config rows, Plugin Settings dialog, and hardware input) without StreamController installed
- [ ] Validated locally (`python3 scripts/validate.py`)
