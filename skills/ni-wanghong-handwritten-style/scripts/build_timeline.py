#!/usr/bin/env python3
"""给王虹手写 HTML 生成“时间轴版”：内联全部样式，注入逐条动画运行时。

时间轴版把每一页拆成若干步骤（标题、每个框、每个箭头、每行文字、每张图），
手动逐步播放（空格 / 点击出下一条），可开启自动连播，效果接近 Office PPT。

默认输出到源 HTML 同目录的 index-timeline.html；单文件，不依赖任何相对资源。

用法（在本 skill 目录运行）：
    python3 scripts/build_timeline.py
    python3 scripts/build_timeline.py --source /path/to/deck/index.html --out /path/to/index-timeline.html
"""

import argparse
import base64
import pathlib
import re
import sys


def load_css(tag, base_dir):
    href_match = re.search(r'href="([^"]+)"', tag)
    if not href_match or "stylesheet" not in tag:
        return tag
    url = href_match.group(1)
    if url.startswith(("data:", "http://", "https://")):
        return tag
    path = (base_dir / url).resolve()
    if not path.is_file():
        print(f"[warn] 找不到样式文件: {path}", file=sys.stderr)
        return ""
    css = path.read_text(encoding="utf-8")
    font_reference = 'url("fonts/Xiaolai-Regular.ttf")'
    if font_reference in css:
        font_path = path.parent / "fonts" / "Xiaolai-Regular.ttf"
        if not font_path.is_file():
            raise FileNotFoundError(f"缺少随包字体: {font_path}")
        data = base64.b64encode(font_path.read_bytes()).decode("ascii")
        css = css.replace(font_reference, f'url("data:font/ttf;base64,{data}")')
    return f'<style data-inline="{url}">\n{css}\n</style>'


def build(source_html, timeline_css, timeline_js, out_path):
    text = source_html.read_text(encoding="utf-8")
    base_dir = source_html.parent

    # 1. 内联所有本地样式表
    text = re.sub(r"<link\b[^>]*>", lambda m: load_css(m.group(0), base_dir), text)

    # 2. 移除原 runtime.js（时间轴版本用自己的运行时，避免键盘与翻页冲突）
    text = re.sub(
        r'<script\b[^>]*src="[^"]*runtime\.js"[^>]*>\s*</script>',
        "",
        text,
    )

    # 3. 注入时间轴样式与运行时
    injected = (
        f'<style data-inline="timeline.css">\n{timeline_css}\n</style>\n'
        f'<script data-inline="timeline.js">\n{timeline_js}\n</script>'
    )
    if "</body>" not in text:
        print("[error] 源 HTML 缺少 </body>", file=sys.stderr)
        sys.exit(1)
    text = text.replace("</body>", injected + "\n</body>")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"written: {out_path}")
    print(f"  source: {source_html}")


def main():
    parser = argparse.ArgumentParser(description="构建王虹手写 HTML 的时间轴版")
    parser.add_argument(
        "--source",
        default=None,
        type=pathlib.Path,
        help="源 HTML（王虹手写 PPT 的 index.html）",
    )
    parser.add_argument(
        "--out",
        default=None,
        type=pathlib.Path,
        help="输出 HTML 路径（默认与源同目录的 index-timeline.html）",
    )
    args = parser.parse_args()

    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    if args.source is None:
        source = skill_dir / "examples/ni-demo/index.html"
    elif args.source.is_absolute() or args.source.exists():
        source = args.source.resolve()
    else:
        source = (skill_dir / args.source).resolve()
    out = args.out.resolve() if args.out else source.parent / "index-timeline.html"
    timeline_css = (skill_dir / "assets/timeline.css").read_text(encoding="utf-8")
    timeline_js = (skill_dir / "assets/timeline.js").read_text(encoding="utf-8")

    if not source.is_file():
        print(f"[error] 源 HTML 不存在: {source}", file=sys.stderr)
        sys.exit(1)
    build(source, timeline_css, timeline_js, out)


if __name__ == "__main__":
    main()
