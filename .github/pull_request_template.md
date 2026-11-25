## Plugin Submission / Update

- **Plugin Name:**
- **Plugin ID (must match `manifest.json`):**
- **Repository URL:**
- **Submission Type:** [ ] New StreamController Plugin / [ ] Version Update

### Checklist

- [ ] Entry added/updated in `catalog.json` and top-level `updated_at` timestamp refreshed
- [ ] `id` and `version` in `catalog.json` match the plugin's `manifest.json`
- [ ] `download_url` points directly to a `.zip` archive containing `manifest.json` and `main.py`
- [ ] `icon` and `thumbnail` point to valid, publicly accessible `https://` image URLs
- [ ] Tested locally in Ballista (actions, Inspector config rows, Plugin Settings dialog, and hardware input) without StreamController installed
- [ ] Validated JSON syntax (`python3 -m json.tool catalog.json > /dev/null`)
