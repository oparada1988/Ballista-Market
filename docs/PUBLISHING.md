# Publishing a Plugin to Ballista Market

This guide walks through packaging, testing, submitting, and updating a plugin in **[Ballista-Market](https://github.com/oparada1988/Ballista-Market)**.

Ballista supports two plugin runtimes:
- **Native Ballista (`ballista`)** — compiled Rust binaries with zero Python overhead and full key, dial, and touchscreen support. Start from [`templates/native-rust-plugin/`](../templates/native-rust-plugin) or inspect the full production example **[Music Assistant (`MASS`)](https://github.com/oparada1988/MASS)**.
- **StreamController (`streamcontroller`)** — Python plugins executed via Ballista's built-in standalone Compatibility Bridge (no StreamController installation required).

> Migrating an existing Python plugin to Native Rust? See [Migrating from StreamController](./MIGRATING_FROM_STREAMCONTROLLER.md).

---

## Step 1: Prepare & Package Your Plugin

### Choose a Consistent Plugin ID
Pick a globally unique reverse-domain style ID, such as `com_<your_github_handle>_<PluginName>` (for example, `com_oparada_MusicAssistant`).

This exact string **must match** in all three places:
1. Your plugin repository's `manifest.json` (`"id"`)
2. Your Market entry folder name: `plugins/<id>/`
3. Your Market entry file: `plugins/<id>/plugin.json` (`"id"`)

### Option A — Native Ballista Plugin (Rust)
1. Copy [`templates/native-rust-plugin/`](../templates/native-rust-plugin) into your plugin repository and fill in your metadata, actions, and artwork.
2. Package locally to verify your `.zip` layout:
   ```bash
   chmod +x build-package.sh
   ./build-package.sh
   ```
   The resulting `.zip` must contain `manifest.json`, `bin/linux-x86_64/<binary>`, `assets/*.png`, `LICENSE`, and `README.md`.
3. Tag a release so `.github/workflows/release.yml` automatically builds and publishes your `.zip` to GitHub Releases:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Copy the direct release asset URL for `download_url`:
   ```text
   https://github.com/<user>/<repo>/releases/download/v1.0.0/<Plugin>-v1.0.0.zip
   ```

### Option B — StreamController Plugin (Python)
1. Ensure your repository contains `manifest.json`, `main.py`, `assets/`, and a `LICENSE` file. (If your plugin has Python dependencies, provide `__install__.py` or `requirements.txt` — Ballista runs them automatically in its isolated bridge venv.)
2. Tag a release (recommended for deterministic versioned updates) and use the tag archive URL as `download_url`:
   ```text
   https://github.com/<user>/<repo>/archive/refs/tags/v1.0.0.zip
   ```
   *(Branch archives such as `.../archive/refs/heads/main.zip` are also accepted, though tagged releases make version updates cleaner.)*

---

## Step 2: Prepare Storefront Artwork & Direct URLs

Add crisp storefront assets to your plugin repository:

| Asset | Repo Path | Recommended Size | Aspect Ratio |
| :--- | :--- | :--- | :---: |
| **Plugin Icon** | `assets/icon.png` | `512 × 512 px` *(min `256 × 256`)* | `1:1` |
| **Spotlight Banner** | `assets/thumbnail.png` | `1168 × 420 px` *(or `584 × 210`)* | `~2.78:1` |
| **Screenshots (up to 6)** | `store/screenshots/01-*.png` | `1920 × 1080 px` *(or `1280 × 720`)* | `16:9` |
| **Action Icons** | `assets/<action>.png` | `512 × 512 px` *(min `144 × 144`)* | `1:1` |

> **Important — Use Direct Raw Image URLs:**
> Always link images with `https://raw.githubusercontent.com/<user>/<repo>/main/...` — **not** `https://github.com/<user>/<repo>/blob/main/...` (which returns an HTML web page instead of a PNG/WebP image).

---

## Step 3: Test Locally in Ballista First

Before opening a PR, test your packaged `.zip` (or local folder) inside Ballista:
1. Open **Ballista → Plugin Store → Install Local → Install from ZIP (.zip)...**
2. Confirm your plugin appears in the right-hand **Actions** sidebar and loads cleanly.
3. Drag actions onto keys and/or Stream Deck + dials and verify:
   - Live icons, labels, and dial cards render properly.
   - **Action Settings** (Property Inspector rows) load and persist values.
   - **Plugin Settings** (`⚙`) work if your plugin exposes global settings.
   - Physical key presses, dial rotations, and touchscreen taps behave as expected without StreamController installed.

---

## Step 4: Fork `Ballista-Market` & Add `plugins/<id>/plugin.json`

1. Fork **[Ballista-Market](https://github.com/oparada1988/Ballista-Market)** and create a branch:
   ```bash
   git clone https://github.com/<your_handle>/Ballista-Market.git
   cd Ballista-Market
   git checkout -b add-<your-plugin>
   ```
2. Copy the entry starter into your plugin's dedicated folder:
   ```bash
   mkdir -p plugins/com_yourhandle_MyPlugin
   cp templates/plugin-entry.json plugins/com_yourhandle_MyPlugin/plugin.json
   ```
3. Fill in all fields in `plugins/com_yourhandle_MyPlugin/plugin.json`:
   - `version`: semantic version without a leading `v` (e.g. `"1.0.0"`), matching `manifest.json`.
   - `license`: valid SPDX identifier (official Ballista repos use `"GPL-3.0-or-later"`; community plugins may use any valid open-source SPDX license such as `"GPL-3.0-or-later"`, `"MIT"`, or `"Apache-2.0"`).
   - `category`: one of `Utility`, `System`, `Audio`, `Streaming`, `Productivity`, `Developer`.
   - `surfaces`: subset of `["keys", "dials", "touchscreen"]`.
   - `compatible_devices`: subset of `StreamDeckOriginal`, `StreamDeckMK2`, `StreamDeckMini`, `StreamDeckXL`, `StreamDeckNeo`, `StreamDeckPlus`, `StreamDeckPlusXL`, `StreamDeckPedal`, `StreamDeckStudio`.
   - **Do not** set `added_at` in `plugin.json` — it is stamped automatically from Git merge history.
   - **Do not** hand-edit `catalog.json` — GitHub Actions compiles it automatically on merge to `main`.

---

## Step 5: Validate Locally & Open a Pull Request

Run the validator from the root of your `Ballista-Market` fork:

```bash
python3 scripts/validate.py
```

This checks JSON syntax, required fields, unique IDs, folder-name parity, allowed enums, and verifies that every `https://` URL (`github_url`, `download_url`, `icon`, `thumbnail`, `screenshots`) responds cleanly over HTTP.

Once validation passes:
```bash
git add plugins/com_yourhandle_MyPlugin/plugin.json
git commit -m "feat(plugins): add My Plugin (v1.0.0)"
git push origin add-my-plugin
```
Then open a Pull Request against `oparada1988/Ballista-Market` (`main`) and complete the PR checklist.

### Common Validation Errors

| Error | Cause & Fix |
| :--- | :--- |
| `Plugin folder name '...' must exactly match 'id'` | Rename `plugins/<folder>` or update `"id"` so both match character-for-character. |
| `Failed to reach 'download_url'` / HTTP 404 | Verify your GitHub Release is published (not a Draft) and the `.zip` filename matches the URL exactly. |
| `'icon'` or `'thumbnail'` doesn't load in Ballista | Replace `github.com/.../blob/main/...` with `raw.githubusercontent.com/.../main/...`. |
| `'added_at' is generated automatically...` | Remove `"added_at"` from `plugins/<id>/plugin.json`. |
| `'screenshots' cannot exceed 6 items` | Keep at most 6 full-bleed `16:9` screenshots. |

---

## Step 6: What Happens After Merge

1. **Automatic Catalog Build:** On merge to `main`, `.github/workflows/build-catalog.yml` runs `scripts/build_catalog.py` and updates `catalog.json` automatically.
2. **Automatic 7-Day Spotlight:** Because your plugin has a valid HTTPS `thumbnail`, it automatically enters the **Spotlight** carousel at the top of Ballista's Plugin Store for **7 days** from its merge date.
3. **Propagation:** GitHub Raw CDN caches `catalog.json` for ~5 minutes, after which every Ballista user immediately sees your plugin live in the Store.

---

## Publishing Updates (`v1.1.0`, etc.)

To ship an update to existing users:
1. Bump `version` in your plugin repository (`manifest.json` and `Cargo.toml` for Rust), tag a new release (e.g. `v1.1.0`), and verify the new `.zip` is attached to the GitHub Release.
2. Open a PR in `Ballista-Market` updating `version` and `download_url` (plus any new actions or screenshots) in `plugins/<id>/plugin.json`.
3. Run `python3 scripts/validate.py` and submit the PR.

Once merged, Ballista detects the newer semantic version automatically and presents an **Update** button in the Store and **My Plugins** view.
