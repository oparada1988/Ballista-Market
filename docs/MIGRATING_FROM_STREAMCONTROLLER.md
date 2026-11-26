# Migrating a StreamController Plugin to a Native Ballista Rust Plugin

Ballista runs existing Python StreamController plugins out of the box via its built-in standalone Compatibility Bridge — you **do not** have to rewrite a working plugin to list it in Ballista Market.

However, migrating to a **Native Ballista Rust Plugin** (`"runtime": "ballista"`) gives you:
- **Zero Python / venv / RPyC overhead** — launches in milliseconds with a tiny memory footprint.
- **Crash isolation** — runs as its own lightweight out-of-process binary speaking newline-delimited JSONL over `stdin`/`stdout`.
- **Native async networking** — ideal for WebSockets, REST APIs, and live state sync without RPyC backend boilerplate.
- **First-class Stream Deck + support** — render crisp `200×100` LCD dial cards and react to normalized `(norm_x, norm_y)` touchscreen tap zones.

> **Production Before/After Reference:** **[Music Assistant for Ballista (`MASS`)](https://github.com/oparada1988/MASS)** was migrated directly from a Python StreamController plugin to a pure-Rust Native Ballista plugin using this exact pattern.
>
> **Starter Template:** Copy [`templates/native-rust-plugin/`](../templates/native-rust-plugin) to scaffold your new Rust repo in seconds.

---

## 1. Architecture & API Concept Mapping

| StreamController (Python) | Native Ballista Plugin (Rust) |
| :--- | :--- |
| `PluginBase` (`main.py`) | Out-of-process Rust binary reading JSONL `BridgeCommand`s from `stdin` and emitting `BridgeEvent`s to `stdout` |
| `ActionBase` subclass | Per-slot state entry (`HashMap<String, SlotState>`) + metadata in `manifest.json` & `plugin_initialized` |
| `on_key_down()` / `on_key_up()` | `BridgeCommand::KeyDown { slot }` / `BridgeCommand::KeyUp { slot }` |
| `on_dial_turn(delta)` / `on_dial_down()` | `BridgeCommand::DialTurn { slot, delta }` / `BridgeCommand::DialDown { slot }` |
| Touchscreen tap | `BridgeCommand::DialTap { slot, norm_x, norm_y }` (`0.0..=1.0` normalized coordinates inside the dial's LCD segment) |
| `set_media(media_path=...)` | `BridgeEvent::SetMedia { slot, media_path, size, valign, halign }` |
| `set_top_label()` / `set_center_label()` / `set_bottom_label()` | `BridgeEvent::SetLabel { slot, text, position, color, font_size, font_family }` |
| `get_config_rows()` (GTK widgets) | `BridgeEvent::ActionConfigRows { slot, rows: Vec<BridgeConfigRow> }` (declarative JSON — no GTK bindings required!) |
| `get_settings_area()` (GTK widgets) | `BridgeEvent::PluginSettingsRows { plugin_id, rows: Vec<BridgeConfigRow> }` |
| `get_settings()` / `set_settings()` | Persist per-slot state via `BridgeEvent::SetSettings` and global plugin config JSON in `$BALLISTA_DATA_DIR` |
| `backend/` (RPyC server process) | Single async Tokio task inside the same binary (no RPyC or separate daemon needed) |
| `__install__.py` / `requirements.txt` | Eliminated — compiled directly into `bin/linux-x86_64/<binary>` |

---

## 2. Environment Variables Provided by Ballista

When Ballista spawns your native plugin binary, it injects four environment variables:

| Variable | Purpose |
| :--- | :--- |
| `BALLISTA_PLUGIN_ID` | Your plugin's `"id"` from `manifest.json` |
| `BALLISTA_PLUGIN_DIR` | Installed plugin directory containing `manifest.json` and `assets/` |
| `BALLISTA_DATA_DIR` | Persistent writable config directory (`~/.local/share/ballista/plugin_data/<id>`) |
| `BALLISTA_CACHE_DIR` | Writable cache directory for downloaded artwork and dynamically rendered key/dial PNGs (`~/.cache/ballista/plugins/<id>`) |

---

## 3. Preserving Existing User Deck Profiles

If users already have your StreamController plugin installed in Ballista, you can make the upgrade completely seamless:
1. Keep the **exact same plugin `"id"`** in `manifest.json` and `Ballista-Market` (e.g., `com_oparada_MusicAssistant`).
2. Keep the **exact same action IDs** (`<plugin_id>::<ActionClassName>`, e.g., `com_oparada_MusicAssistant::PlayPauseAction`).
3. Keep the **same setting keys** in each slot's `settings` map (or read legacy keys as fallback on `create_action`).

Because Ballista stores profiles by plugin ID and action ID, every existing key and dial on the user's Stream Deck continues working immediately after upgrading.

---

## 4. Upgrading `manifest.json`

Add `"runtime": "ballista"`, `"entrypoint"`, `"surfaces"`, and an `"actions"` list so Ballista discovers your binary and its capabilities instantly without executing Python:

```json
{
  "id": "com_yourhandle_MyPlugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "yourhandle",
  "license": "GPL-3.0-or-later",
  "runtime": "ballista",
  "min_ballista_version": "0.1.0",
  "repository": "https://github.com/yourhandle/MyPlugin",
  "entrypoint": {
    "linux-x86_64": "bin/linux-x86_64/ballista-my-plugin",
    "linux-aarch64": "bin/linux-aarch64/ballista-my-plugin"
  },
  "icon": "assets/icon.png",
  "thumbnail": "assets/thumbnail.png",
  "surfaces": ["keys", "dials", "touchscreen"],
  "actions": [
    {
      "id": "com_yourhandle_MyPlugin::MyAction",
      "name": "My Action",
      "description": "What this action does",
      "icon": "assets/my_action.png",
      "surfaces": ["keys", "dials"]
    }
  ]
}
```

---

## 5. Declarative Settings Without GTK

In StreamController plugins, you had to build Adwaita/GTK rows directly in Python (`Adw.ComboRow`, `Adw.EntryRow`, etc.). In Native Ballista plugins, you simply emit JSON `BridgeConfigRow` structs — Ballista renders native Libadwaita widgets automatically and sends back:
- `set_action_config_row` (for per-key/per-dial **Action Settings**)
- `set_plugin_setting` (for global **Plugin Settings** `⚙`)

Supported `row_type` values include `"ComboRow"`, `"SwitchRow"`, `"EntryRow"`, `"PasswordRow"`, `"SpinRow"`, `"ScaleRow"`, `"ColorRow"`, `"ButtonRow"`, and `"ActionRow"`.

> **Tip:** Proactively emit `ActionConfigRows` at the end of `create_action` (and whenever dropdown options refresh, such as after a successful "Test Connection") so the Property Inspector populates instantaneously.

---

## 6. Stream Deck + Dial Cards & Touchscreen Zones

To render rich `200×100` LCD cards on Stream Deck + (or + XL):
1. Render your PNG card into `$BALLISTA_CACHE_DIR` (e.g., using Rust's `image` + `ab_glyph` crates — see [`MASS/src/render.rs`](https://github.com/oparada1988/MASS/blob/main/src/render.rs)).
2. Write atomically (write to `.tmp`, then rename) and use a unique or content-hashed filename when the image changes so GTK/hardware reloads immediately.
3. Emit `BridgeEvent::SetMedia { slot, media_path, size: Some(1.0), ... }`.
4. Handle `BridgeCommand::DialTap { slot, norm_x, norm_y }` to map tap regions (e.g., `norm_x < 0.33` = Previous, middle = Play/Pause, `norm_x > 0.66` = Next).

---

## 7. Packaging & Updating `Ballista-Market`

1. Reuse [`build-package.sh`](../templates/native-rust-plugin/build-package.sh) and [`.github/workflows/release.yml`](../templates/native-rust-plugin/.github/workflows/release.yml) from the starter template.
2. Keep your `assets/` icons (`512×512` icon, `1168×420` `thumbnail.png`) and up to 6 `16:9` screenshots in `store/screenshots/`.
3. Tag a release (`git tag v1.0.0 && git push origin v1.0.0`) so GitHub Actions publishes `<Plugin>-v1.0.0.zip`.
4. Open a PR in `Ballista-Market` updating `plugins/<id>/plugin.json`:
   - Change `"runtime": "streamcontroller"` → `"runtime": "ballista"`
   - Update `"version"` and point `"download_url"` to your GitHub Release `.zip`
   - Run `python3 scripts/validate.py`

See [Publishing a Plugin to Ballista Market](./PUBLISHING.md) for the full PR checklist and Spotlight details.
