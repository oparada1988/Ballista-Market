## Plugin Submission / Update

- **Plugin Name:**
- **Plugin ID (must match `plugins/<id>/plugin.json` and `manifest.json`):**
- **Runtime Type:** [ ] Native Ballista (`ballista`) / [ ] StreamController (`streamcontroller`)
- **Repository URL:**
- **Submission Type:** [ ] New Plugin / [ ] Version Update

### Checklist

- [ ] Added or updated `plugins/<plugin_id>/plugin.json` (do **not** hand-edit `catalog.json` — GitHub Actions compiles it automatically on merge, or run `python3 scripts/build_catalog.py`)
- [ ] `id`, `version`, and `license` match the plugin repository
- [ ] `download_url` points directly to a `.zip` archive containing `manifest.json`
- [ ] `icon`, `thumbnail`, and any `screenshots` (16:9 PNG/WebP, max 6) point to publicly accessible `https://` URLs
- [ ] Tested locally in Ballista (actions, Inspector config rows, Plugin Settings dialog, and hardware input) without StreamController installed
- [ ] Validated locally (`python3 scripts/validate.py`)
