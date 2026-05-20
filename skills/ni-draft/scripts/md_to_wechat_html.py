"""markdown -> 微信兼容 HTML（全内联 CSS）。

负责两件事：
1. 把 ni-formatter 注入的 5 个 :::xxx 排版模块渲染成对应 HTML 结构。
2. 把普通 markdown 渲染成 HTML，并把所有样式内联到 style 属性
   （公众号不支持 <style> / <link>）。

样式规范见 ni-draft/references/html-style-guide.md。
"""

import re
import sys

import markdown

CONTAINER_OPEN = (
    '<section style="font-size:16px;color:#333;'
    'line-height:1.75;letter-spacing:0.3px;">'
)
CONTAINER_CLOSE = "</section>"

# 普通标签 -> 内联样式
_STYLES = {
    "h1": "font-size:22px;font-weight:bold;color:#222;margin:1.4em 0 0.8em;",
    "h2": "font-size:19px;font-weight:bold;color:#222;margin:1.4em 0 0.7em;",
    "h3": "font-size:17px;font-weight:bold;color:#333;margin:1.2em 0 0.6em;",
    "p": "margin:0 0 1.2em;",
    "ul": "margin:0 0 1.2em;padding-left:1.4em;",
    "ol": "margin:0 0 1.2em;padding-left:1.4em;",
    "li": "margin:0 0 0.5em;",
    "strong": "font-weight:bold;color:#222;",
    "blockquote": "border-left:3px solid #ccc;padding-left:1em;"
    "color:#888;margin:1em 0;",
}
_PRE_STYLE = (
    "background:#f7f7f7;padding:1em;border-radius:5px;"
    "overflow-x:auto;font-size:13px;line-height:1.5;"
)
_CODE_INLINE = (
    "background:#f4f4f4;padding:2px 5px;border-radius:3px;font-size:14px;"
)
_A_STYLE = "color:#576b95;text-decoration:none;"

# callout 三色：(背景, 左边框)
CALLOUT_COLORS = {
    "warning": ("#fff3cd", "#ffc107"),
    "info": ("#e7f3fe", "#2196f3"),
    "tip": ("#e8f5e9", "#4caf50"),
}

_PART_RE = re.compile(r"^<!--\s*:::part\s+(.+?)\s*-->\s*$")
_OPEN_RE = re.compile(r"^<!--\s*:::(callout|quote|steps|verdict)(?:\s+(\w+))?\s*-->\s*$")
_CLOSE_RE = re.compile(r"^<!--\s*:::\s*-->\s*$")
_HEADING_RE = re.compile(r"^#{1,6}\s")
_STRAY_COMMENT_RE = re.compile(r"<!--\s*:::.*?-->", re.DOTALL)


def _md(text):
    """markdown -> HTML（未内联）。"""
    return markdown.markdown(text, extensions=["fenced_code"])


def _inline(html):
    """把标准 HTML 的样式全部内联。"""
    html = html.replace(
        "<pre><code>",
        f'<pre style="{_PRE_STYLE}"><code style="display:block;">',
    )
    html = re.sub(r"<code>", f'<code style="{_CODE_INLINE}">', html)
    for tag, style in _STYLES.items():
        html = re.sub(rf"<{tag}>", f'<{tag} style="{style}">', html)
    html = re.sub(r"<a ", f'<a style="{_A_STYLE}" ', html)
    return html


def _render_part(title):
    return (
        '<hr style="border:none;border-top:1px solid #ddd;'
        'margin:2.2em 0 1.2em;">'
        f'<h2 style="{_STYLES["h2"]}">{title}</h2>'
    )


def _render_callout(inner_html, ctype):
    bg, bar = CALLOUT_COLORS.get(ctype or "info", CALLOUT_COLORS["info"])
    return (
        f'<section style="background:{bg};border-left:4px solid {bar};'
        f'padding:0.9em 1em;margin:1.3em 0;border-radius:3px;">'
        f"{inner_html}</section>"
    )


def _render_quote(inner_html):
    return (
        '<blockquote style="border-left:3px solid #999;'
        'padding:0.4em 0 0.4em 1em;color:#666;margin:1.3em 0;">'
        f"{inner_html}</blockquote>"
    )


def _render_verdict(inner_html):
    text = re.sub(r"^<p[^>]*>", "", inner_html.strip())
    text = re.sub(r"</p>$", "", text)
    return (
        '<section style="text-align:center;font-weight:bold;'
        "font-size:17px;color:#222;margin:2em 0;padding:1.1em 1em;"
        f'background:#f5f5f5;border-radius:5px;">{text}</section>'
    )


def convert(md_text):
    """把带 :::xxx 注释的 markdown 转成完整微信兼容 HTML。"""
    lines = md_text.splitlines()
    n = len(lines)
    segments = []  # ("plain", md) 或 ("html", html)
    buf = []
    i = 0

    def flush():
        if buf:
            text = "\n".join(buf).strip()
            if text:
                segments.append(("plain", text))
            buf.clear()

    while i < n:
        stripped = lines[i].strip()
        m_part = _PART_RE.match(stripped)
        m_open = _OPEN_RE.match(stripped)
        if m_part:
            flush()
            segments.append(("html", _render_part(m_part.group(1))))
            # 跳过紧随的原 H2 标题（由 part 接管）
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            i = j + 1 if (j < n and _HEADING_RE.match(lines[j])) else i + 1
            continue
        if m_open:
            flush()
            mod, ctype = m_open.group(1), m_open.group(2)
            inner = []
            i += 1
            while i < n and not _CLOSE_RE.match(lines[i].strip()):
                inner.append(lines[i])
                i += 1
            i += 1  # 越过 close 行（或文件尾）
            inner_html = _inline(_md("\n".join(inner).strip()))
            if mod == "callout":
                segments.append(("html", _render_callout(inner_html, ctype)))
            elif mod == "quote":
                segments.append(("html", _render_quote(inner_html)))
            elif mod == "steps":
                segments.append(("html", inner_html))
            else:  # verdict
                segments.append(("html", _render_verdict(inner_html)))
            continue
        buf.append(lines[i])
        i += 1
    flush()

    rendered = []
    for kind, content in segments:
        rendered.append(_inline(_md(content)) if kind == "plain" else content)
    body = "\n".join(rendered)
    # 兜底：吞掉任何没被解析掉的 :::xxx 残留注释
    body = _STRAY_COMMENT_RE.sub("", body)
    return f"{CONTAINER_OPEN}{body}{CONTAINER_CLOSE}"


if __name__ == "__main__":
    # 离线快速测试：python md_to_wechat_html.py article.md
    if len(sys.argv) != 2:
        print("用法：python md_to_wechat_html.py <markdown 文件>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        print(convert(fh.read()))
