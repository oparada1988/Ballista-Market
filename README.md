# Ballista Market

The official community plugin catalog for **[Ballista](https://github.com/oparada1988/Ballista)** — a fast, native Linux controller for Elgato Stream Deck hardware.

Ballista Market supports two plugin runtimes, clearly badged in the Store UI:
- **`ballista` (Ballista Native):** First-class native plugins built for Ballista's Rust & Cairo SDK (keys, dials, and touchscreen cards with zero bridge overhead).
- **`streamcontroller` (StreamController):** Existing StreamController plugins running seamlessly via Ballista's built-in standalone Compatibility Bridge (no StreamController installation required).

---

## Plugin Repository Directory Structure

Separating storefront media into a dedicated `store/` directory keeps runtime deck icons clean while maintaining full StreamController compatibility.

### StreamController-Compatible Plugin
```text
MyPlugin/
├── manifest.json            # Required: id, name, version, author, descriptions
├── main.py                  # Required: PluginBase entry point
├── __install__.py           # Optional: pip / venv hook (auto-run by Ballista)
├── LICENSE                  # Recommended: SPDX license file (MIT, GPL-3.0, etc.)
├── README.md
├── CHANGELOG.md             # Optional
├── actions/                 # Action modules
├── backend/                 # Optional: RPyC backend service
├── locales/                 # Optional: en_US.json, etc.
├── assets/                  # Runtime deck icons + SC-compatible icon/thumbnail
│   ├── icon.png             # Square PNG (>= 256×256)
│   ├── thumbnail.png        # Spotlight banner
│   └── action_*.png
└── store/                   # Optional: Ballista Market storefront media
    ├── banner.png           # Optional dedicated Spotlight banner (e.g. 1200×430)
    └── screenshots/         # Up to 6 ordered 16:9 PNG/WebP screenshots (1280×720 or 1920×1080)
        ├── 01-overview.png
        ├── 02-deck-layout.png
        └── 03-inspector.png
```

### Native Ballista Plugin
```text
com_author_MyNativePlugin/
├── manifest.json            # Includes "runtime": "ballista", "min_ballista_version", "license"
├── LICENSE
├── README.md
├── bin/                     # Platform binaries (linux-x86_64, linux-aarch64)
├── assets/                  # Runtime icons, SVGs, fonts
│   └── icon.png             # Square PNG (>= 256×256) or icon.svg
└── store/                   # Market storefront media
    ├── banner.png           # Spotlight banner
    └── screenshots/         # Up to 6 ordered 16:9 PNG/WebP screenshots
        ├── 01-dial-card.png
        ├── 02-key-grid.png
        └── 03-settings.png
```

---

## `Ballista-Market` Registry Structure

To avoid PR merge conflicts, each plugin lives in its own folder under `plugins/<plugin_id>/plugin.json`. On merge to `main`, GitHub Actions compiles all manifests into root [`catalog.json`](./catalog.json) automatically.

```text
Ballista-Market/
├── plugins/
│   ├── com_oparada_AppLauncher/
│   │   └── plugin.json
│   ├── com_oparada_DiscordSC/
│   │   └── plugin.json
│   └── com_oparada_GoveeStreamController/
│       └── plugin.json
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
| `download_url` | Yes | `string` | Direct `https://` URL to the downloadable `.zip` archive. |
| `icon` | Yes | `string` | Direct `https://` URL to square PNG icon (`>= 256×256`), or standard GTK symbolic icon name. |
| `thumbnail` | Yes | `string` | Direct `https://` URL to Store Spotlight banner PNG. |
| `screenshots` | No | `string[]` | Up to 6 `https://` URLs to `16:9` PNG/WebP screenshots for the Detail gallery & lightbox. |
| `surfaces` | No | `string[]` | Supported hardware surfaces: `"keys"`, `"dials"`, `"touchscreen"`. |
| `compatible_devices` | No | `string[]` | Supported Stream Deck models (`StreamDeckPlus`, `StreamDeckPlusXL`, `StreamDeckXL`, `StreamDeckMK2`, `StreamDeckMini`, `StreamDeckNeo`, `StreamDeckOriginal`, `StreamDeckPedal`, `StreamDeckStudio`). |
| `actions` | No | `object[]` | Preview list of included actions (`{ "name", "description", "surfaces" }`). |
| `rating` | No | `number \| null` | Optional community rating (`0.0`–`5.0`); omitted/hidden in UI when `null`. |
| `rating_count` | No | `integer` | Number of community ratings. |

---

## How to Submit or Update a Plugin

1. **Test Locally in Ballista First**
   - Open Ballista → **Plugin Store** → **Install Local** and verify actions, Property Inspector rows, global settings, and hardware presses.
2. **Fork & Create `plugins/<your_plugin_id>/plugin.json`**
   - Create a branch and add/update your plugin's manifest file.
3. **Validate Locally**
   ```bash
   python3 scripts/validate.py
   ```
   *(Optionally run `python3 scripts/build_catalog.py` to preview the compiled `catalog.json`.)*
4. **Open a Pull Request**
   - Automated checks verify schema, unique IDs, valid categories/surfaces/devices, and live HTTPS asset URLs.
   - Once merged to `main`, `build-catalog.yml` updates `catalog.json` automatically and Ballista users receive the new listing or one-click update immediately.
