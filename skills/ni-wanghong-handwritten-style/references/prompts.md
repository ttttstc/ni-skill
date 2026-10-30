# 王虹学术手写 PPT：GPT Image 与 HTML 完整提示词

这套提示词用于复刻一种 16:9 的 Notability 学术报告手写页：暖白纸面、细而工整的深蓝手写字、克制的荧光标记、手绘箭头与图表，以及非常清楚的逻辑链。

## 统一风格提示词

```text
Use case: productivity-visual
Asset type: exact 16:9 technical presentation slide

Create one handwritten Chinese technical presentation slide on a flat warm off-white Notability-style digital note page. The slide should feel like a mathematician's carefully prepared conference lecture notes: calm, precise, information-dense, logically ordered, and genuinely handwritten.

Use authentic fine dark-navy digital handwriting, slightly irregular baselines, natural pen-pressure variation, thin hand-drawn boxes, arrows, axes, tables and diagrams. Keep generous outer margins. Use vivid cobalt blue only for derivation lines and axes, magenta-red for conclusions or recommendation boxes, fluorescent yellow for one short priority phrase, fluorescent green for a confirmed structure or recommended option, and coral pink for an exception or loss.

The page must be a clean flat slide, with no stage, projector, camera perspective, paper edge or photo texture. Avoid commercial presentation design: no rounded cards, no gradient, no shadow, no glossy icon, no decorative background, no brand logo, no footer, no page number, no watermark.

Render every Chinese character, Latin word and number exactly as supplied. Use small neat handwriting and thin strokes. Keep bright highlights narrow and imperfect, like a real highlighter. One slide answers one question. Preserve large empty areas where the logic does not need content.
```

## 原创示例：从问题到成果

使用 examples/ni-demo/index.html 作为排版示例。以下文字可用于创建同一主题的图像：

- 封面：“从问题到成果”“一套可核对的工作流程”“ni-skill 原创示例”。
- 流程页：“先把问题说清楚”，以“目标 → 现有材料 → 验收方式”串联要点。
- 图解页：“拆成小步，边做边验证”，展示“制作 → 检查 → 调整”的循环。
- 对照页：“每一步留下可核对的结果”，列出理解、行动、验证三个阶段。

保留暖白背景、深蓝手写文字、细线、有限的高亮和充足留白。图中只出现给定的文字。
## 从文章继续生成后续页面

```text
Continue the same exact 16:9 handwritten Notability academic slide system for every remaining page.

For each page:
1. Answer one clear question.
2. Use 3 to 6 short handwritten lines, or one diagram/table plus a short explanation.
3. Put the causal chain in visible reading order from left to right or top to bottom.
4. Use only one main diagram type: flow, coordinate chart, comparison table, memory scale, architecture sketch, command block or summary formula.
5. Use yellow and green highlights only on short phrases. Use one magenta conclusion box at most.
6. Preserve the same handwriting scale, line weight, warm off-white background, outer margins and color meanings.
7. Render all supplied text verbatim and add no new claims.

Constraints: no commercial template, no large decorative title, no gradients, no shadows, no icons, no photos, no page number, no watermark, no extra text.
```

## HTML 完整实现提示词

```text
请把提供的中文文章制作成一套完整的 16:9 HTML 幻灯片，视觉参考 Notability 制作的数学学术报告手写页。

内容组织：
- 先提炼一个总问题、3 到 6 个核心判断，以及支撑判断的数据、流程、例子和陷阱。
- 拆成 12 到 24 页，每页只回答一个问题。
- 推荐结构：封面 → 变化发生了什么 → 为什么重要 → 证据与推导 → 怎么做 → 选择与陷阱 → 总结 → 结束。
- 每页只保留投影需要的关键词，其余解释写入隐藏的演讲备注。

视觉系统：
1. 画布固定 1920×1080 和 16:9，背景使用淡暖白。没有页眉、页脚、页码、品牌装饰和卡片阴影。
2. 中文、英文与数字使用选定字体：优先 HanziPen SC，否则使用随包小赖字体。小赖字形示例见 `assets/preview-cover.png`。
3. 主文字用深蓝色。蓝色用于推导线和坐标轴，玫红用于结论框和推荐项，绿色用于已确认结构，荧光黄用于极少量关键词，珊瑚粉用于例外或剩余部分。
4. 框、线、箭头和坐标轴保留轻微手画抖动。关键词高亮只覆盖文字本身。
5. 禁止圆角卡片、渐变、阴影、照片背景、装饰图标、粗大数字墙和统一商业网格。

封面：
- 单行标题位于画面上方约三分之一。
- 标题下方画一条细玫红横线。
- 作者、场合和日期分三行居中。
- 下半页保持大面积留白。

正文：
- 优先使用左文右图、流程、坐标轴、对比表、公式总结。
- 标题比正文大一档，正文保持小而清楚。
- 结论使用 2px 到 3px 的玫红细框。
- SVG 图表线条使用圆头，并加入极轻微位移滤镜。

使用 neat-annotations：
- 本地引入 neat-annotations.css。
- 中文可以直接写入 data-note，例如 data-note="甜点档"。
- 将 --ann-font 设为与正文一致的字体，--ann-label-max-width 设置为 180px 到 240px。
- 标注采用绝对定位，因此在目标内容四周预留空间。
- 重要信息同时写在正文中，标注只做视觉提示。

交互与导出：
- 支持左右键、空格翻页和全屏。
- 每页写一段隐藏讲稿备注。
- 逐页导出为 1920×1080 PNG。
- 用浏览器检查全部页面的中文、溢出、遮挡、翻页和 16:9 比例。
- 生成一张全部页面的总览图，人工检查整套风格是否统一。
```
