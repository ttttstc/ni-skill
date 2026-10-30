# 王虹手写 PPT 风格拆解

这套风格的核心是“现场推导笔记”：让观众沿着颜色、框线和图示跟随一条清楚的逻辑链。

## 一、真实风格特征

1. **封面极简**
   - 单行标题放在画面上方约三分之一处。
   - 标题用深蓝色细笔，下面一条玫红色手绘横线。
   - 作者、场合、日期分三行居中。
   - 下半页保持大面积空白。

2. **正文像数字白板笔记**
   - 背景接近纯白或淡暖白，纸张纹理很弱。
   - 主体笔迹以深蓝或黑色为主，字小而工整，行距宽松。
   - 没有页眉、页脚、页码、品牌标识和装饰性背景。

3. **颜色承担逻辑功能**
   - 蓝色：标题下划线、公式、坐标轴、推导主线。
   - 玫红：结论、警告、重点框、推荐项。
   - 绿色：正向定义、成立条件、关键结构。
   - 荧光黄：一个词或一段短语的瞬时强调。
   - 每页可以出现多种颜色，颜色都要对应具体含义。

4. **图文排布自由，逻辑很规整**
   - 常见结构是左边文字、右边小图，也会在顶部放公式、下方放推论。
   - 直线、坐标轴、框、箭头都保留手画的不均匀感。
   - 内容密度较高，每页围绕一个问题逐层展开。

5. **强调方式克制**
   - 定理、目标、结论用细线框。
   - 关键词用窄条高亮，避免整段铺色。
   - 重要词用短下划线，避免粗体和大字号。

## 二、GPT Image 通用提示词

```text
Use case: productivity-visual
Asset type: exact 16:9 technical presentation slide
Primary request: Create one handwritten Chinese technical slide in the visual language of a real Notability academic lecture page. The page should feel like a mathematician's carefully prepared live derivation notes: dense, calm, clear, and handmade.

Scene/backdrop: flat warm off-white digital note page; no stage; no projector frame; no photo perspective; nearly textureless background

Style/medium: authentic fine digital handwriting; small dark navy body text; slightly irregular baselines; thin hand-drawn boxes, arrows, axes and diagrams; natural pen pressure variation; no typed font

Composition/framing: exact 16:9 landscape; one logical question per slide; compact handwritten notes on the left; one small explanatory diagram on the right; one thin result box near the bottom; generous outer margins; free-form alignment

Color system:
- deep navy for body text and formulas
- vivid cobalt blue for derivation lines and axes
- magenta-red for conclusions, warnings and recommendation boxes
- fluorescent yellow for one short high-priority phrase
- fluorescent green for a positive definition or confirmed structure
- coral pink for exceptions or the small remaining part

Text (verbatim):
"{标题或首句}"
"{要点 1}"
"{要点 2}"
"{要点 3}"
"{结论}"

Diagram: {说明图的对象、方向、标签、颜色和关系}

Constraints: render all Chinese and Latin text exactly; use small neat handwriting; thin strokes; bright highlights only on short phrases; no commercial cards; no grid template; no icons; no gradients; no shadows; no glossy design; no footer; no page number; no watermark; no extra text
```

### 封面专用提示词

```text
Create an exact 16:9 handwritten Chinese presentation cover on a flat warm off-white Notability page.

Place one single-line title near the upper third in fine dark navy handwriting. Draw one thin vivid magenta-red hand-drawn underline directly beneath it. Put the author, occasion and date as three small centered handwritten lines with generous vertical spacing. Keep the entire lower half almost empty.

Text (verbatim):
"从问题到成果"
"一套可核对的工作流程"
"ni-skill 原创示例"
"2026"

Constraints: exact text; one-line title; huge whitespace; no subtitle; no icon; no logo; no border; no shadow; no gradient; no typed font; no watermark; no extra text
```

## 三、HTML 实现提示词

```text
请把文章制作成一套 16:9 HTML 幻灯片，视觉参考 Notability 制作的数学学术报告手写页。

整体要求：
1. 画布固定为 16:9，背景使用淡暖白。页面没有页眉、页脚、页码、品牌装饰和卡片阴影。
2. 中文、英文与数字优先使用 HanziPen SC，否则使用随包小赖字体；示例字形以 `assets/preview-cover.png` 为验收基准。
3. 正文字号控制在投影可读范围内，标题比正文大一档，避免商业演示常见的超大标题。
4. 主文字用深蓝色。蓝色用于推导线和坐标轴，玫红用于结论框和推荐项，绿色用于已确认结构，荧光黄用于极少量关键词，珊瑚粉用于例外或剩余部分。
5. 每页只回答一个问题。允许左文右图、上式下图、定义加图解等自由布局。框、线、箭头和坐标轴都保留轻微手画抖动。
6. 禁止圆角卡片、渐变、阴影、照片背景、装饰图标、粗大数字墙和统一网格。

使用 neat-annotations：
- 本地引入 neat-annotations.css。
- 在要标注的词外包一层 span，使用 ann、方向类和颜色类。
- data-note 可以直接放中文，例如 data-note="甜点档"。
- 将 --ann-font 设为与正文一致的字体，--ann-label-max-width 设为 180px 到 240px。
- 标注采用绝对定位，因此被标注内容四周必须预留空间。
- 重要信息要同时出现在正文里，标注只承担视觉提示。

封面布局：
- 单行标题位于画面上方约三分之一。
- 标题下方画一条细玫红横线。
- 作者、场合和日期分三行居中。
- 下半页保持大面积留白。

正文布局建议：
- 左侧 3 到 5 行手写要点，右侧一个手绘示意图。
- 结论用 2px 到 3px 玫红细框。
- 关键词高亮只覆盖文字本身。
- SVG 线条使用轻微位移滤镜，保留手绘感。

交互与导出：
- 支持左右键翻页和全屏。
- 逐页导出为 1920×1080 PNG。
- 逐页检查中文标注、溢出、遮挡和 16:9 比例。
```

## 四、neat-annotations 中文支持结论

可以使用中文，已经用中文 `data-note` 做了实际页面测试。

- 标注文字来自 `data-note`，中文字符可以正常显示。
- 八个箭头方向、颜色、高亮和嵌套标注与文字语言无关。
- 项目所有文字统一使用本次选定字体。优先 HanziPen SC，否则使用随包小赖字体；渲染后核对静态图和视频字形是否一致。
- 标注处于目标元素外侧，不会自动占据页面空间。中文短语较长时要加大最大宽度，并预留上下左右的空白。
- 标注属于视觉提示。关键结论仍要写在正文中。

参考：[neat-annotations 项目](https://github.com/syabro/neat-annotations) · [项目演示页](https://neat-annotations.syabro.com/) · [王虹报告现场报道](https://m.21jingji.com/article/20260728/herald/620fe6808829148b183085b0c8979608.html)
