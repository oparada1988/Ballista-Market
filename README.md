# Ballista Market

The official community plugin catalog for **[Ballista](https://github.com/oparada1988/Ballista)** — a fast, native Linux controller for Elgato Stream Deck hardware.

Ballista Market supports two plugin runtimes, clearly badged in the Store UI:
- **`ballista` (Ballista Native):** First-class native Rust plugins running directly as isolated out-of-process binaries with zero Python runtime overhead (full keys, dials, and touchscreen support).
- **`streamcontroller` (StreamController):** Existing StreamController plugins running seamlessly via Ballista's built-in standalone Compatibility Bridge (no StreamController installation required).

---

## Starter Templates & Reference Implementation

- **Native Rust Starter Template:** [`templates/native-rust-plugin/`](./templates/native-rust-plugin) — ready-to-build Rust template with JSONL IPC protocol, key/dial/touchscreen handling, persistent settings, local packaging script, and GitHub Actions release workflow.
- **Market Catalog Entry Template:** [`templates/plugin-entry.json`](./templates/plugin-entry.json) — copy into `plugins/<your_plugin_id>/plugin.json` when submitting a PR.
- **Production Native Reference Plugin:** **[Music Assistant for Ballista (`MASS`)](https://github.com/oparada1988/MASS)** — real-world Native Rust plugin showcasing async WebSockets (`/ws`), live artwork caching, custom `200×100` Stream Deck + dial cards, touchscreen skip zones, and 11 actions.

---

## Storefront Artwork Dimensions

| Asset | Path in Plugin Repo | Recommended Size | Aspect Ratio |
| :--- | :--- | :--- | :---: |
| **Plugin Icon** | `assets/icon.png` | `512 × 512 px` *(min `256 × 256`)* | `1:1` |
| **Spotlight Banner** | `assets/thumbnail.png` | `1168 × 420 px` *(or `584 × 210`)* | `~2.78:1` |
| **Screenshots (1–6)** | `store/screenshots/01-*.png` | `1920 × 1080 px` *(or `1280 × 720`)* | `16:9` |
| **Action Icons** | `assets/<action>.png` | `512 × 512 px` *(min `144 × 144`)* | `1:1` |

---

## Plugin Repository Directory Structure

Separating storefront screenshots into `store/screenshots/` keeps runtime deck icons clean while maintaining full StreamController compatibility.

### Native Ballista Plugin (Rust)
```text
MyNativePlugin/
├── Cargo.toml
├── manifest.json            # Includes "runtime": "ballista", "entrypoint", "license", "actions"
├── LICENSE
├── README.md
├── build-package.sh
├── .github/workflows/release.yml
├── src/
│   ├── main.rs
│   └── protocol.rs
├── assets/                  # Runtime deck icons + Store icon/banner
│   ├── icon.png             # 512×512 PNG
│   ├── thumbnail.png        # 1168×420 Spotlight banner PNG
│   └── *.png                # Action icons (512×512 PNG)
└── store/
    └── screenshots/         # Up to 6 full-bleed 16:9 PNG/WebP screenshots
        ├── 01-overview.png
        ├── 02-actions.png
        └── 03-settings.png
```
*(In GitHub Releases, the packaged `.zip` ships `manifest.json`, `bin/linux-x86_64/<binary>`, `assets/*.png`, `LICENSE`, and `README.md`.)*

### StreamController-Compatible Plugin (Python)
```text
MyPlugin/
├── manifest.json            # Required: id, name, version, author, descriptions
├── main.py                  # Required: PluginBase entry point
├── __install__.py           # Optional: pip / venv hook (auto-run by Ballista)
├── LICENSE                  # Recommended: SPDX license file
├── README.md
├── actions/                 # Action modules
├── backend/                 # Optional: RPyC backend service
├── locales/                 # Optional: en_US.json, etc.
├── assets/                  # Runtime deck icons + SC-compatible icon/thumbnail
│   ├── icon.png             # 512×512 PNG
│   ├── thumbnail.png        # 1168×420 Spotlight banner PNG
│   └── action_*.png
└── store/
    └── screenshots/         # Optional: up to 6 full-bleed 16:9 PNG/WebP screenshots
```

---

## `Ballista-Market` Registry Structure

To avoid PR merge conflicts, each plugin lives in its own folder under `plugins/<plugin_id>/plugin.json`. On merge to `main`, GitHub Actions compiles all manifests into root [`catalog.json`](./catalog.json) automatically.

```text
Ballista-Market/
├── plugins/
│   ├── com_oparada_AppLauncher/plugin.json
│   ├── com_oparada_DiscordSC/plugin.json
│   ├── com_oparada_GoveeStreamController/plugin.json
│   └── com_oparada_MusicAssistant/plugin.json
├── templates/
│   ├── native-rust-plugin/
│   └── plugin-entry.json
├── scripts/
│   ├── build_catalog.py
│   └── validate.py
└── catalog.json             # Auto-generated catalog fetched by Ballista
```

---

## `plugin.json` Schema Reference

| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| `id` | Yes | `string` | Unique plugin ID matching folder name and `manifest.json` (e.g. `com_author_MyPlugin`). |
| `name` | Yes | `string` | Human-readable display name shown in the Store. |
| `author` | Yes | `string` | Author handle or display name. |
| `license` | Yes | `string` | SPDX license identifier (e.g. `"MIT"`, `"GPL-3.0-or-later"`, `"Apache-2.0"`). |
| `version` | Yes | `string` | Semantic version without `v` prefix (e.g. `"1.0.0"`), matching `manifest.json`. |
| `runtime` | Yes | `string` | `"ballista"` (Native Ballista) or `"streamcontroller"` (Compatibility Bridge). |
| `min_ballista_version` | No | `string` | Minimum compatible Ballista version (e.g. `"0.1.0"`). |
| `category` | Yes | `string` | One of: `Utility`, `System`, `Audio`, `Streaming`, `Productivity`, `Developer`. |
| `tags` | No | `string[]` | Extra keywords/tags displayed as highlights and used for discovery. |
| `short_description` | No | `string` | Concise 1-line tagline shown under the detail title and on catalog cards. |
| `description` | Yes | `string` | Full description shown on the plugin detail page (supports paragraphs via `\n\n`). |
| `github_url` | Yes | `string` | Public repository or homepage URL (`https://...`), linked as **Source & Issues**. |
| `download_url` | Yes | `string` | Direct `https://` URL to the downloadable `.zip` archive (GitHub Release `.zip` for Native Rust plugins). |
| `icon` | Yes | `string` | Direct `https://` URL to square PNG icon (`512×512`), or standard GTK symbolic icon name. |
| `thumbnail` | Yes | `string` | Direct `https://` URL to Store Spotlight banner PNG (`1168×420`). |
| `screenshots` | No | `string[]` | Up to 6 `https://` URLs to full-bleed `16:9` PNG/WebP screenshots (`1920×1080` or `1280×720`). |
| `surfaces` | No | `string[]` | Supported hardware surfaces: `"keys"`, `"dials"`, `"touchscreen"`. |
| `compatible_devices` | No | `string[]` | Supported Stream Deck models (`StreamDeckPlus`, `StreamDeckPlusXL`, `StreamDeckXL`, `StreamDeckMK2`, `StreamDeckMini`, `StreamDeckNeo`, `StreamDeckOriginal`, `StreamDeckPedal`, `StreamDeckStudio`). |
| `actions` | No | `object[]` | Preview list of included actions (`{ "name", "description", "surfaces" }`). |
| `rating` | No | `number \| null` | Optional community rating (`0.0`–`5.0`); cleanly hidden in UI when `null`. |
| `rating_count` | No | `integer` | Number of community ratings. |

---

## How to Submit or Update a Plugin

1. **Test Locally in Ballista First**
   - Open Ballista → **Plugin Store** → **Install Local** and verify actions, Property Inspector rows, global settings, and hardware presses.
2. **Fork & Create `plugins/<your_plugin_id>/plugin.json`**
   - Copy `templates/plugin-entry.json` into `plugins/<your_plugin_id>/plugin.json` and fill in your plugin details.
3. **Validate Locally**
   ```bash
   python3 scripts/validate.py
   ```
   *(Optionally run `python3 scripts/build_catalog.py` to preview the compiled `catalog.json`.)*
4. **Open a Pull Request**
   - Automated checks verify schema, unique IDs, valid categories/surfaces/devices, and live HTTPS asset URLs.
   - Once merged to `main`, `build-catalog.yml` updates `catalog.json` automatically and Ballista users receive the new listing or one-click update.
