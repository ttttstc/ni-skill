#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PPT_CHECK="$SKILL_DIR/scripts/check_deck.py"
PPT_TEMPLATE_CSS="$SKILL_DIR/assets/template.css"

HTML="${1:-}"
OUTPUT="${2:-}"

if [[ -z "$HTML" || -z "$OUTPUT" || ! -f "$HTML" ]]; then
  echo "usage: render_html_video.sh <deck.html> <output.mp4> [options]" >&2
  exit 2
fi
if [[ ! -f "$PPT_CHECK" || ! -f "$PPT_TEMPLATE_CSS" ]]; then
  echo "error: 必须与 ni-wanghong-handwritten-style 一起安装" >&2
  echo "required: ni-wanghong-handwritten-style/scripts/check_deck.py" >&2
  echo "required: ni-wanghong-handwritten-style/assets/template.css" >&2
  exit 2
fi
FFMPEG_PATH="$(command -v ffmpeg || true)"
if [[ -n "$FFMPEG_PATH" ]]; then
  FFMPEG_DIR="$(dirname "$FFMPEG_PATH")"
  if [[ -x "$FFMPEG_DIR/ffprobe" || -x "$FFMPEG_DIR/ffprobe.exe" ]]; then
    export PATH="$FFMPEG_DIR:$PATH"
  fi
fi
for command in node ffmpeg ffprobe; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "error: 缺少命令 $command" >&2
    exit 2
  fi
done
PYTHON="${WANGHONG_PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys' >/dev/null 2>&1; then PYTHON="$candidate"; break; fi
  done
fi
if [[ -z "$PYTHON" ]]; then echo "error: Python not found; set WANGHONG_PYTHON" >&2; exit 2; fi
export WANGHONG_PYTHON="$PYTHON"
if [[ ! -d "$SKILL_DIR/node_modules/puppeteer-core" ]]; then
  echo "error: 请先在 $SKILL_DIR 运行 npm install" >&2
  exit 2
fi

"$PYTHON" "$PPT_CHECK" "$HTML"
node "$SCRIPT_DIR/render_html_video.mjs" "$@"

if [[ "$OUTPUT" != /* ]]; then
  OUTPUT="$(pwd)/$OUTPUT"
fi

video_streams="$(ffprobe -v error -select_streams v -show_entries stream=index -of csv=p=0 "$OUTPUT" | wc -l | tr -d ' ')"
audio_streams="$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$OUTPUT" | wc -l | tr -d ' ')"
codec_name="$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$OUTPUT")"
pixel_format="$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of csv=p=0 "$OUTPUT")"
video_size="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$OUTPUT")"
frame_rate="$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$OUTPUT")"

if [[ "$video_streams" != "1" ]]; then
  echo "error: 视频流数量为 $video_streams" >&2
  exit 1
fi
if [[ "$audio_streams" != "0" ]]; then
  echo "error: 成片含有 $audio_streams 条音频流" >&2
  exit 1
fi
if [[ "$codec_name" != "h264" || "$pixel_format" != "yuv420p" ]]; then
  echo "error: 编码规格异常: $codec_name / $pixel_format" >&2
  exit 1
fi
if [[ "$video_size" != "1920x1080" || "$frame_rate" != "30/1" ]]; then
  echo "error: 画面规格异常: $video_size / $frame_rate" >&2
  exit 1
fi

ffmpeg -v error -i "$OUTPUT" -f null -
echo "verified: 1920x1080, 30fps, H.264, yuv420p, 0 audio"
