# Contributing to Ballista Market

Thank you for sharing your plugin with the **[Ballista](https://github.com/oparada1988/Ballista)** community!

## Guides & Starter Templates

- **[Publishing Guide (`docs/PUBLISHING.md`)](./docs/PUBLISHING.md)** — complete step-by-step walkthrough for packaging, validating, submitting, and updating plugins.
- **[Migrating from StreamController (`docs/MIGRATING_FROM_STREAMCONTROLLER.md`)](./docs/MIGRATING_FROM_STREAMCONTROLLER.md)** — port an existing Python StreamController plugin to a Native Ballista Rust binary.
- **[Native Rust Plugin Starter (`templates/native-rust-plugin/`)](./templates/native-rust-plugin)** — ready-to-build template with JSONL IPC, packaging script, and GitHub Release workflow.
- **[Market Entry Template (`templates/plugin-entry.json`)](./templates/plugin-entry.json)** — copy into `plugins/<your_plugin_id>/plugin.json`.
- **Production Native Reference:** **[Music Assistant (`MASS`)](https://github.com/oparada1988/MASS)**.

## Submission Rules

1. **One folder per plugin:** Add or edit only `plugins/<your_plugin_id>/plugin.json`. The folder name must match `"id"` in both `plugin.json` and your plugin's `manifest.json`.
2. **Do not hand-edit `catalog.json`:** GitHub Actions compiles root `catalog.json` automatically on merge to `main`.
3. **Do not set `added_at`:** Timestamps are stamped automatically from Git merge history (and power the 7-day Spotlight window).
4. **Direct HTTPS asset URLs:** Use `raw.githubusercontent.com/...` URLs for `icon`, `thumbnail`, and `screenshots`, and a direct `.zip` link for `download_url`.
5. **Validate before opening a PR:** Run `python3 scripts/validate.py` locally and confirm all checks pass.
6. **Licensing:** `Ballista-Market` and official Ballista templates are licensed under **`GPL-3.0-or-later`**. Community plugins submitted to the catalog may use any valid open-source SPDX license (`GPL-3.0-or-later`, `MIT`, `Apache-2.0`, `BSD-3-Clause`, etc.), accurately declared in `"license"`.
