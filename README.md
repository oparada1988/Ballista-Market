# Ballista Market

The official community plugin catalog for **[Ballista](https://github.com/oparada1988/Ballista)** — a fast, native Linux controller for Elgato Stream Deck hardware.

> **Currently Supported:** **StreamController Plugins** (zero code modifications required).
> **Coming Soon:** **Native Ballista Plugins** will be documented here once the native SDK is finalized.

---

## StreamController Plugin Compatibility

Ballista includes a standalone, built-in **StreamController Compatibility Bridge** — users do **not** need StreamController installed on their system. Existing StreamController plugins run natively out of the box with no code changes:

- `PluginBase`, `ActionCore`, and legacy `ActionBase`
- `ActionHolder`, `ActionHolderGroup`, `EventAssigner`, `EventHolder`, `EventManager`
- `GtkHelper` and `GtkHelper.GenerativeUI` (`ComboRow`, `SearchComboRow`, `ItemListComboRow`, `EntryRow`, `PasswordEntryRow`, `SwitchRow`, `SpinRow`, `ScaleRow`, `ColorButtonRow`, `ExpanderRow`, `ToggleRow`, `FileDialogRow`)
- Live action config rows (`get_config_rows()`, `get_custom_config_area()`) and live plugin settings dialogs (`get_settings_area()`, `get_config_rows()`)
- Multi-position labels (`top`, `center`, `bottom`), dynamic icons (`media_path` & `PIL.Image`), and background colors
- `LocaleManager` (JSON & CSV locales), `PluginAssetManager`, `SignalManager`, `on_tick()` heartbeats
- RPyC backend processes (`streamcontroller_plugin_tools.BackendBase`) and automatic `__install__.py` install hooks

---

## Plugin Repository Requirements

Before submitting your plugin to `catalog.json`, make sure your repository meets these requirements:

1. **Direct `.zip` Download Archive**
   - `download_url` must be a direct `https://` link to a `.zip` archive (for example, a GitHub release tag archive `https://github.com/<user>/<repo>/archive/refs/tags/v1.0.0.zip` or branch archive `https://github.com/<user>/<repo>/archive/refs/heads/main.zip`).
   - Ballista extracts the zip and automatically locates `manifest.json` either at the archive root or inside GitHub's single top-level folder (e.g., `MyPlugin-main/manifest.json`).
2. **Valid `manifest.json` & `main.py`**
   - Your plugin must include `manifest.json` and a `main.py` defining a `PluginBase` subclass.
   - The `"id"` field in `catalog.json` **must exactly match** the `"id"` in your plugin's `manifest.json` (recommended format: `com_<author>_<PluginName>`).
3. **Python Runtime Dependencies**
   - Ballista's installer provisions a dedicated `--system-site-packages` Python environment containing:
     - `PyGObject` (`gi`, GTK 4, Libadwaita)
     - `loguru`, `Pillow`, `requests`, `rpyc`, `websocket-client`, `pulsectl`, `psutil`, `packaging`, `pynput`, `cairosvg`
   - If your plugin requires additional PyPI packages or a dedicated backend virtualenv, include a standard StreamController `__install__.py` script in your plugin root — Ballista runs it automatically on install and update.
4. **Store Artwork**
   - **`icon`**: Direct `https://` URL to a square PNG icon (recommended `128x128` or larger) used in catalog cards and the plugin detail header.
   - **`thumbnail`**: Direct `https://` URL to a landscape banner PNG (recommended `16:9` / `600x220`+) displayed in the Store Spotlight carousel and Detail page.

---

## `catalog.json` Schema Reference

All listed plugins live inside the `"plugins"` array in [`catalog.json`](./catalog.json).

### Entry Fields

| Field | Required | Type | Description |
| :--- | :---: | :--- | :--- |
| `id` | Yes | `string` | Unique plugin ID matching `manifest.json` (e.g. `com_author_MyPlugin`). |
| `name` | Yes | `string` | Human-readable display name shown in the Store. |
| `author` | Yes | `string` | Author handle or display name. |
| `version` | Yes | `string` | Semantic version string without `v` prefix (e.g. `"1.0.0"`), matching `manifest.json`. |
| `category` | Yes | `string` | Primary Store category (see allowed values below). |
| `tags` | No | `string[]` | Extra keywords/tags for discoverability. |
| `description` | Yes | `string` | Short summary of what the plugin does (1–2 sentences). |
| `github_url` | Yes | `string` | Public repository or homepage URL (`https://...`). |
| `download_url` | Yes | `string` | Direct `https://` URL to the downloadable `.zip` archive. |
| `icon` | Yes | `string` | Direct `https://` URL to the plugin icon PNG, or a standard GTK symbolic icon name. |
| `thumbnail` | Yes | `string` | Direct `https://` URL to the Store banner/thumbnail PNG. |
| `compatible_devices` | No | `string[]` | Supported Stream Deck models (see allowed values below). |

### Valid `category` Values

- `Utility`
- `System`
- `Audio`
- `Streaming`
- `Productivity`
- `Developer`

### Valid `compatible_devices` Values

- `StreamDeckOriginal`
- `StreamDeckMK2`
- `StreamDeckMini`
- `StreamDeckXL`
- `StreamDeckNeo`
- `StreamDeckPlus`
- `StreamDeckPlusXL`
- `StreamDeckPedal`
- `StreamDeckStudio`

### Example Plugin Entry

```json
{
  "id": "com_yourname_MyAwesomePlugin",
  "name": "My Awesome Plugin",
  "author": "yourname",
  "version": "1.0.0",
  "category": "Utility",
  "tags": [
    "Utility",
    "Automation"
  ],
  "description": "Control your favorite Linux app or smart device directly from your Stream Deck.",
  "github_url": "https://github.com/yourname/MyAwesomePlugin",
  "download_url": "https://github.com/yourname/MyAwesomePlugin/archive/refs/tags/v1.0.0.zip",
  "icon": "https://raw.githubusercontent.com/yourname/MyAwesomePlugin/main/assets/icon.png",
  "thumbnail": "https://raw.githubusercontent.com/yourname/MyAwesomePlugin/main/assets/thumbnail.png",
  "compatible_devices": [
    "StreamDeckPlus",
    "StreamDeckPlusXL",
    "StreamDeckXL",
    "StreamDeckMK2",
    "StreamDeckMini",
    "StreamDeckNeo"
  ]
}
```

---

## How to Submit Your Plugin

1. **Test Locally in Ballista First**
   - Open Ballista → **Plugin Store** → **Install Local Plugin...** and select your plugin folder.
   - Verify that:
     - All actions appear in the sidebar with expected names and icons.
     - Action settings rows (`ComboRow`, `SwitchRow`, `EntryRow`, `ScaleRow`, `ColorRow`, etc.) render and update cleanly in the Property Inspector.
     - Global plugin settings (if applicable) work via the Settings gear button.
     - Physical key presses, dial turns/presses, icons, and labels work as expected without StreamController installed.
2. **Fork This Repository**
   - Fork `oparada1988/Ballista-Market` and create a feature branch (e.g. `add-my-awesome-plugin`).
3. **Add Your Entry to `catalog.json`**
   - Append your plugin JSON object to the `"plugins"` array in `catalog.json`.
   - Update the top-level `"updated_at"` UTC ISO-8601 timestamp.
4. **Validate JSON Syntax Locally**
   ```bash
   python3 -m json.tool catalog.json > /dev/null
   ```
5. **Open a Pull Request**
   - Submit a PR against `main`. Automated checks will verify your JSON schema, unique ID, valid categories/devices, and live download/asset URLs.

---

## Publishing Plugin Updates

Ballista automatically checks installed plugins' `manifest.json` `"version"` against the `"version"` listed in `catalog.json`:

1. Bump `"version"` in your plugin repository's `manifest.json` (and create a release/tag if using tag-pinned URLs).
2. Open a PR in `Ballista-Market` updating `"version"`, `"updated_at"`, and (if tag-pinned) `"download_url"` in `catalog.json`.
3. Once merged, Ballista users will see **Updates Available** in the Plugin Store and can download and apply the updated archive directly with one click.

---

## Roadmap: Native Ballista Plugins

Future versions of Ballista will introduce a first-class **Native Ballista Plugin** format alongside full StreamController backwards compatibility. Contribution guidelines and templates for native plugins will be added to this repository when available.
