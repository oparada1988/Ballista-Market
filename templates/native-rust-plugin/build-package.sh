#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ARCH="$(uname -m)"
PLATFORM="linux-${ARCH}"
PLUGIN_ID="$(python3 -c "import json; print(json.load(open('manifest.json'))['id'])")"
VERSION="$(python3 -c "import json; print(json.load(open('manifest.json'))['version'])")"
BIN_NAME="$(python3 -c "import json, os; print(os.path.basename(json.load(open('manifest.json'))['entrypoint']['${PLATFORM}']))")"

echo "[Ballista Plugin] Building release binary (${BIN_NAME}) for ${PLATFORM}..."
cargo build --release

mkdir -p "bin/${PLATFORM}" dist
cp "target/release/${BIN_NAME}" "bin/${PLATFORM}/${BIN_NAME}"
chmod +x "bin/${PLATFORM}/${BIN_NAME}"

STAGE_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGE_DIR"' EXIT
PKG_ROOT="${STAGE_DIR}/${PLUGIN_ID}"
mkdir -p "${PKG_ROOT}/bin/${PLATFORM}" "${PKG_ROOT}/assets"

cp manifest.json LICENSE README.md "${PKG_ROOT}/"
cp "bin/${PLATFORM}/${BIN_NAME}" "${PKG_ROOT}/bin/${PLATFORM}/${BIN_NAME}"
if compgen -G "assets/*.png" > /dev/null || compgen -G "assets/*.svg" > /dev/null; then
  cp assets/*.png assets/*.svg "${PKG_ROOT}/assets/" 2>/dev/null || true
fi

OUT_ZIP="${SCRIPT_DIR}/dist/${PLUGIN_ID}-v${VERSION}-${PLATFORM}.zip"
rm -f "$OUT_ZIP"
(cd "$STAGE_DIR" && zip -qr "$OUT_ZIP" "${PLUGIN_ID}")

echo "[Ballista Plugin] Built package: ${OUT_ZIP}"
