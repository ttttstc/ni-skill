# 微信兼容 HTML 内联 CSS 规范

> 本文定义 ni-draft 把 markdown 转成微信草稿 HTML 时的样式约定。`md_to_wechat_html.py` 按本文实现。

---

## 1. 硬约束

公众号编辑器对 HTML 有严格限制：

| 约束 | 处理 |
|------|------|
| 不支持 `<style>` 和 `<link>` | 所有 CSS 内联到元素 `style` 属性 |
| 不支持 JavaScript | 不引入任何 JS |
| `<img>` 的 src 需是微信素材 URL | P0 不处理正文图片，遇本地图片跳过并提示 |
| 段落需 `<p>` 包裹 | markdown 库默认行为，保留 |

---

## 2. 基础元素样式

整篇文章外层包一个容器：

```
<section style="font-size:16px;color:#333;line-height:1.75;letter-spacing:0.3px;">
```

| 元素 | 内联样式 |
|------|---------|
| h1 | `font-size:22px;font-weight:bold;color:#222;margin:1.4em 0 0.8em;` |
| h2 | `font-size:19px;font-weight:bold;color:#222;margin:1.4em 0 0.7em;` |
| h3 | `font-size:17px;font-weight:bold;color:#333;margin:1.2em 0 0.6em;` |
| p | `margin:0 0 1.2em;` |
| ul / ol | `margin:0 0 1.2em;padding-left:1.4em;` |
| li | `margin:0 0 0.5em;` |
| strong | `font-weight:bold;color:#222;` |
| code（行内） | `background:#f4f4f4;padding:2px 5px;border-radius:3px;font-size:14px;` |
| pre（代码块） | `background:#f7f7f7;padding:1em;border-radius:5px;overflow-x:auto;font-size:13px;line-height:1.5;` |
| blockquote（原生） | `border-left:3px solid #ccc;padding-left:1em;color:#888;margin:1em 0;` |
| a | `color:#576b95;text-decoration:none;` |

字号、颜色可微调，原则是：正文 16px、行距 1.75、深灰不纯黑，符合公众号长文阅读习惯。

---

## 3. 5 个排版模块的渲染

ni-formatter 注入的 `:::xxx` 注释，在此转成对应 HTML。

### part — `<!-- :::part 标题 -->`

渲染为分隔线 + 强调标题：

```html
<hr style="border:none;border-top:1px solid #ddd;margin:2.2em 0 1.2em;">
<h2 style="font-size:19px;font-weight:bold;color:#222;margin:0 0 0.8em;">标题</h2>
```

注：part 注释后面紧跟的原 H2 标题，渲染时由 part 接管，不再重复输出原 H2。

### callout — `<!-- :::callout 类型 -->...<!-- ::: -->`

三色背景块：

| 类型 | 背景 | 左边框 |
|------|------|--------|
| warning | `#fff3cd` | `4px solid #ffc107` |
| info | `#e7f3fe` | `4px solid #2196f3` |
| tip | `#e8f5e9` | `4px solid #4caf50` |

```html
<section style="background:#fff3cd;border-left:4px solid #ffc107;padding:0.9em 1em;margin:1.3em 0;border-radius:3px;">
  <p style="margin:0;">内容</p>
</section>
```

### quote — `<!-- :::quote -->...<!-- ::: -->`

缩进引用 + 左侧色条：

```html
<blockquote style="border-left:3px solid #999;padding:0.4em 0 0.4em 1em;color:#666;margin:1.3em 0;font-style:normal;">
  <p style="margin:0;">内容</p>
</blockquote>
```

### steps — `<!-- :::steps -->...<!-- ::: -->`

编号列表，每步开头加粗（加粗由 markdown 的 `**` 处理）：

```html
<ol style="margin:1.3em 0;padding-left:1.5em;">
  <li style="margin:0 0 0.7em;"><strong>第一步</strong>，说明……</li>
</ol>
```

### verdict — `<!-- :::verdict -->...<!-- ::: -->`

加粗居中视觉锚点块：

```html
<section style="text-align:center;font-weight:bold;font-size:17px;color:#222;margin:2em 0;padding:1.1em 1em;background:#f5f5f5;border-radius:5px;">
  核心判断句
</section>
```

---

## 4. 模块注释解析规则

- `:::part` 是单行注释，无配对收尾，作用于紧随其后的 H2。
- `:::callout` / `:::quote` / `:::steps` / `:::verdict` 是配对注释，以 `<!-- ::: -->` 收尾，包裹中间的 markdown 块。
- 解析时先抽出模块块、单独渲染，再渲染剩余正文。
- 注释残留（如配对不全）应被吞掉，绝不出现在最终 HTML 里。
- 模块内部的 markdown（加粗、列表）正常按基础样式渲染。
