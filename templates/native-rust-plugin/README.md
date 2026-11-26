# Native Ballista Rust Plugin Template

A minimal, zero-bloat starter template for building **Native Ballista Plugins** in Rust.

> **Full Real-World Example:** See **[Music Assistant for Ballista (`MASS`)](https://github.com/oparada1988/MASS)** for a complete production Native Ballista Rust plugin featuring async WebSocket state sync, live artwork caching, custom `200×100` Stream Deck + dial card rendering, and 11 actions.

---

## Quick Start

1. Copy this folder into your new plugin repository.
2. Replace `com_yourhandle_MyPlugin`, `My Plugin`, `yourhandle`, and `ballista-my-plugin` in:
   - `Cargo.toml`
   - `manifest.json`
   - `src/main.rs`
3. Add your artwork:
   - `assets/icon.png` — **`512 × 512 px`** (`1:1` PNG)
   - `assets/thumbnail.png` — **`1168 × 420 px`** (`~2.78:1` Store Spotlight banner PNG)
   - `assets/<action>.png` — **`512 × 512 px`** (`1:1` PNG)
   - `store/screenshots/01-*.png` — **`1920 × 1080 px`** (or `1280 × 720 px`, `16:9` PNG/WebP, up to 6)
4. Build and package locally:
   ```bash
   chmod +x build-package.sh
   ./build-package.sh
   ```
5. Test in Ballista via **Plugin Store → Install Local → Install from ZIP (.zip)...** and pick the generated archive in `dist/`.
6. Tag a release (`git tag v1.0.0 && git push origin v1.0.0`) so `.github/workflows/release.yml` builds and publishes your `.zip` to GitHub Releases, then submit your plugin to [Ballista-Market](https://github.com/oparada1988/Ballista-Market) using `templates/plugin-entry.json`.

---

## Environment Variables Provided by Ballista

When Ballista spawns your plugin binary, it sets:
- `BALLISTA_PLUGIN_ID` — your `manifest.json` `"id"`
- `BALLISTA_PLUGIN_DIR` — installed plugin directory (contains `manifest.json` and `assets/`)
- `BALLISTA_DATA_DIR` — persistent writable settings directory (`~/.local/share/ballista/plugin_data/<id>`)
- `BALLISTA_CACHE_DIR` — cache directory for downloaded artwork & rendered dial cards (`~/.cache/ballista/plugins/<id>`)
