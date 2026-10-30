#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path


FONT_ALIAS = "Wanghong Preview Hand"
DEMO_FONT_POSTSCRIPT = "HanziPenSC-W3"
PORTABLE_FONT_POSTSCRIPT = "Xiaolai"


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def postscript_names(font: Path) -> set[str]:
    data = font.read_bytes()
    if data[:4] == b"ttcf":
        face_count = _u32(data, 8)
        face_offsets = [_u32(data, 12 + index * 4) for index in range(face_count)]
    else:
        face_offsets = [0]

    names: set[str] = set()
    for face_offset in face_offsets:
        table_count = _u16(data, face_offset + 4)
        name_offset = None
        for index in range(table_count):
            record = face_offset + 12 + index * 16
            if data[record : record + 4] == b"name":
                name_offset = _u32(data, record + 8)
                break
        if name_offset is None:
            continue

        record_count = _u16(data, name_offset + 2)
        string_offset = name_offset + _u16(data, name_offset + 4)
        for index in range(record_count):
            record = name_offset + 6 + index * 12
            platform_id = _u16(data, record)
            name_id = _u16(data, record + 6)
            if name_id != 6:
                continue
            length = _u16(data, record + 8)
            offset = _u16(data, record + 10)
            raw = data[string_offset + offset : string_offset + offset + length]
            encoding = "utf-16-be" if platform_id in {0, 3} else "mac_roman"
            try:
                names.add(raw.decode(encoding))
            except UnicodeDecodeError:
                continue
    return names


def validate_font_file(font: Path) -> str:
    try:
        names = postscript_names(font)
    except (OSError, struct.error, ValueError) as error:
        raise ValueError("无法读取指定字体文件") from error
    for name in (DEMO_FONT_POSTSCRIPT, PORTABLE_FONT_POSTSCRIPT):
        if name in names:
            return name
    raise ValueError("指定字体必须是 HanziPen SC 或随包的小赖字体")


def inject_font(source: Path, font: Path, output: Path) -> str:
    font_name = validate_font_file(font)
    html = source.read_text(encoding="utf-8")
    if "<head" not in html or "</head>" not in html:
        raise ValueError("HTML 缺少 head 元素")

    head_end = html.find(">", html.find("<head"))
    if head_end < 0:
        raise ValueError("HTML head 元素不完整")

    base_uri = source.resolve().parent.as_uri().rstrip("/") + "/"
    font_uri = font.resolve().as_uri()
    injection = f"""
  <base href="{base_uri}">
  <style id="wanghong-preview-font-lock">
    @font-face {{
      font-family: "{FONT_ALIAS}";
      src: url("{font_uri}");
      font-style: normal;
      font-weight: 100 900;
    }}
    :root {{
      --hand: "{FONT_ALIAS}";
      --hand-font: "{FONT_ALIAS}";
      --ann-font: "{FONT_ALIAS}";
      --font-sans: "{FONT_ALIAS}";
      --font-display: "{FONT_ALIAS}";
      --font-mono: "{FONT_ALIAS}";
      --font-serif: "{FONT_ALIAS}";
    }}
    html, body, .deck, .deck *, .deck svg text {{
      font-family: "{FONT_ALIAS}" !important;
    }}
  </style>
  <script>
    window.addEventListener('DOMContentLoaded', async () => {{
      try {{
        await document.fonts.load('32px "{FONT_ALIAS}"', '王虹学术手写');
        await document.fonts.ready;
        document.documentElement.dataset.wanghongFontReady =
          document.fonts.check('32px "{FONT_ALIAS}"', '王虹学术手写') ? 'yes' : 'no';
      }} catch (error) {{
        document.documentElement.dataset.wanghongFontReady = 'no';
      }}
    }});
  </script>
"""
    output.write_text(html[: head_end + 1] + injection + html[head_end + 1 :], encoding="utf-8")
    return font_name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="为王虹 PPT 静态渲染注入预览封面的指定字体"
    )
    parser.add_argument("--identify-font", type=Path)
    parser.add_argument("source", type=Path, nargs="?")
    parser.add_argument("font", type=Path, nargs="?")
    parser.add_argument("output", type=Path, nargs="?")
    args = parser.parse_args()

    if args.identify_font:
        try:
            print(validate_font_file(args.identify_font))
        except ValueError as error:
            parser.error(str(error))
        return 0
    if not all((args.source, args.font, args.output)):
        parser.error("请提供 source、font 和 output")
    if not args.source.is_file():
        parser.error(f"HTML 不存在: {args.source}")
    if not args.font.is_file():
        parser.error(f"字体文件不存在: {args.font}")
    print(f"font verified: {inject_font(args.source, args.font, args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
