#!/usr/bin/env bash
set -euo pipefail

CHROME="${WANGHONG_CHROME:-}"
FILE="${1:-}"
COUNT="${2:-all}"
OUT="${3:-}"
FONT_FILE="${4:-${WANGHONG_FONT_PATH:-}}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${WANGHONG_PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys' >/dev/null 2>&1; then PYTHON="$candidate"; break; fi
  done
fi
if [[ -z "$PYTHON" ]]; then echo "error: Python not found; set WANGHONG_PYTHON" >&2; exit 1; fi

if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "usage: render.sh <html-file> [N|all] [out-dir] [font-file]" >&2
  exit 1
fi

if [[ -z "$CHROME" ]]; then
  for candidate in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "${PROGRAMFILES:-}/Google/Chrome/Application/chrome.exe" "${PROGRAMFILES:-}/Microsoft/Edge/Application/msedge.exe"; do
    if [[ -x "$candidate" ]]; then CHROME="$candidate"; break; fi
  done
fi
if [[ -z "$CHROME" ]]; then
  for candidate in google-chrome google-chrome-stable chromium chromium-browser chrome; do
    if command -v "$candidate" >/dev/null 2>&1; then CHROME="$(command -v "$candidate")"; break; fi
  done
fi
if [[ -z "$CHROME" || ! -x "$CHROME" ]]; then
  echo "error: Chrome/Chromium not found; set WANGHONG_CHROME to its executable path" >&2
  exit 1
fi

if [[ -z "$FONT_FILE" ]]; then
  for candidate in \
    "$HOME/Library/Fonts/Hanzipen.ttc" \
    "$HOME/Library/Fonts/HanziPen.ttc" \
    "/Library/Fonts/Hanzipen.ttc" \
    "/Library/Fonts/HanziPen.ttc" \
    "/System/Library/Fonts/Supplemental/Hanzipen.ttc" \
    "/System/Library/Fonts/Supplemental/HanziPen.ttc"; do
    if [[ -f "$candidate" ]]; then
      FONT_FILE="$candidate"
      break
    fi
  done
fi
if [[ -z "$FONT_FILE" && -d "/System/Library/AssetsV2/com_apple_MobileAsset_Font7" ]]; then
  FONT_FILE="$(find /System/Library/AssetsV2/com_apple_MobileAsset_Font7 -path '*/AssetData/Hanzipen.ttc' -type f -print -quit 2>/dev/null || true)"
fi
if [[ -z "$FONT_FILE" && -f "$SCRIPT_DIR/../assets/fonts/Xiaolai-Regular.ttf" ]]; then
  FONT_FILE="$SCRIPT_DIR/../assets/fonts/Xiaolai-Regular.ttf"
fi
if [[ -z "$FONT_FILE" || ! -f "$FONT_FILE" ]]; then
  echo "error: 未找到字体；请恢复随包的小赖字体，或指定 HanziPen SC 文件" >&2
  echo "usage: render.sh <html-file> [N|all] [out-dir] [font-file]" >&2
  exit 1
fi

STEM="$(basename "${FILE%.*}")"

if [[ "$COUNT" == "all" ]]; then
  COUNT="$(grep -c '<section class="slide' "$FILE" || true)"
fi

if [[ -z "$COUNT" || "$COUNT" -lt 1 ]]; then
  echo "error: no slides found" >&2
  exit 1
fi

if [[ -z "$OUT" ]]; then
  OUT="$(dirname "$FILE")/${STEM}-png"
fi
mkdir -p "$OUT"

RENDER_DIR="$(mktemp -d "/tmp/wanghong-ppt-render.XXXXXX")"
RENDER_HTML="$RENDER_DIR/deck.html"
trap 'rm -f "$RENDER_HTML"; rmdir "$RENDER_DIR"' EXIT
"$PYTHON" "$SCRIPT_DIR/prepare_render_html.py" "$FILE" "$FONT_FILE" "$RENDER_HTML"
RENDER_URL="$("$PYTHON" -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve().as_uri())' "$RENDER_HTML")"

if ! FONT_CHECK="$("$CHROME" \
  --headless=new \
  --allow-file-access-from-files \
  --disable-gpu \
  --hide-scrollbars \
  --no-sandbox \
  --virtual-time-budget=4000 \
  --dump-dom \
  "$RENDER_URL#/1")"; then
  echo "error: Chrome 字体预检失败" >&2
  exit 1
fi
if [[ "$FONT_CHECK" != *'data-wanghong-font-ready="yes"'* ]]; then
  echo "error: 预览封面字体加载失败" >&2
  exit 1
fi

for i in $(seq 1 "$COUNT"); do
  target="$OUT/${STEM}_$(printf '%02d' "$i").png"
  "$CHROME" \
    --headless=new \
    --allow-file-access-from-files \
    --disable-gpu \
    --hide-scrollbars \
    --no-sandbox \
    --virtual-time-budget=4000 \
    --window-size=1920,1080 \
    --screenshot="$target" \
    "$RENDER_URL#/$i" >/dev/null 2>&1
  [[ -s "$target" ]] || { echo "error: failed to render slide $i" >&2; exit 1; }
  echo "rendered: $target"
done

echo "done: $COUNT slide(s)"
