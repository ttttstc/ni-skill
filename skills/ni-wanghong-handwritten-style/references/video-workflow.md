
# 王虹学术手写 HTML 动画视频

直接渲染原 HTML DOM，在原页面元素上增加帧驱动的写入、分步出现、荧光揭示、SVG 路径绘制和纸张转场。文字节点和排版仍由原 HTML 提供，渲染器在截图前加载与静态导出相同的选定字体，并校验 Chrome 实际命中的字形。不重新排版文字。

## 硬性边界

- 输入必须是 `ni-wanghong-handwritten-style` 生成并通过检查的 HTML。
- 优先使用本机或指定的 HanziPen SC；没有时使用随包的小赖字体。用户明确要求 HanziPen 而无可用文件时停止。
- 渲染器必须读取指定字体文件，并通过 Chrome 的实际字体记录验证标题和正文；校验失败立即停止。
- 字号、字重、颜色、布局、图表和标注由原 HTML 决定。
- 输出固定为 1920×1080、30fps、H.264、`yuv420p`。
- 成片恰好一条视频流、零条音频流；不添加旁白、音乐、音效或静音占位音轨。
- 同时输出 MP4 和同目录下的 `cover.png`。

## 工作流程

### 1. 先得到原版手写 HTML

用户提供文章、讲稿或技术主题时，先严格使用同仓库的 `ni-wanghong-handwritten-style` 生成 HTML。不要在本 Skill 内重新设计页面。

用户已经提供该 Skill 的 HTML 时，直接进入检查。保留 HTML 所在目录和相对资源路径，避免复制单个文件造成 CSS、图片或脚本丢失。

### 2. 用原 Skill 检查 HTML

```bash
python3 scripts/check_deck.py \
  "/absolute/path/to/deck/index.html"
```

检查失败时先修复原 HTML。动画渲染不得绕过缺失的 `base.css`、`runtime.js` 或 `neat-annotations.css`。

### 3. 安装一次渲染依赖

在本 Skill 目录运行：

```bash
npm install
```

渲染器使用本机 Google Chrome 或 Chromium 打开原 HTML。默认使用已安装的 HanziPen 或随包小赖字体；也可用 `--font-file "/absolute/path/to/Hanzipen.ttc"` 指定 HanziPen。可通过 `--chrome "/absolute/path/to/chrome"` 指定浏览器。

### 4. 渲染无声 MP4

```bash
bash scripts/render_html_video.sh \
  "/absolute/path/to/deck/index.html" \
  "/absolute/path/to/output/wanghong-handwritten-video.mp4" \
  --seconds-per-slide 4
```

快速样片可以限制页数：

```bash
bash scripts/render_html_video.sh \
  "/absolute/path/to/deck/index.html" \
  "/absolute/path/to/output/preview.mp4" \
  --seconds-per-slide 4 \
  --max-slides 6
```

渲染器按以下顺序处理每页：

1. 原标题与标题线写入；
2. 原页面的顶层内容组依次出现；
3. 原荧光标记横向揭示；
4. 原 SVG 线条按路径绘制；
5. 结尾使用暖白纸张转场。

这些动作只修改透明度、位移、裁切和 SVG 描边进度。原 DOM 内容与计算后的排版保持原样，字形锁定为本次选定的字体。

### 5. 验收

包装脚本会自动检查编码、分辨率、帧率、像素格式、视频流和音频流，并执行完整解码测试。仍需人工查看：

- `cover.png` 与同次静态导出是否使用相同字形；
- 每页开始、内容完全显示、转场前各一帧；
- 标题、图表、标注、脚注有无遮挡或裁切；
- 结论是否至少完整停留 0.8 秒；
- MP4 是否没有可见或隐藏的音频流。

需要逐帧核对时，使用原 PPT Skill 的 `scripts/render.sh` 先导出同一页静态 PNG，再与 MP4 对应完成帧对照。字形或排版出现差异时停止交付，检查指定字体文件、原 CSS 和 HTML 路径。

## 动效纪律

- 一页只推进一个问题，动作服务于阅读顺序。
- 页面主体保持稳定，避免镜头缩放、卡片弹跳、粒子和发布会式炫技。
- 原 HTML 已有 CSS 动画时，渲染器把它们固定到最终视觉状态，再用统一帧进度控制进入顺序。
- 不改写原 HTML 的文字和事实，不添加页面外的新结论。

## 随附资源

- `scripts/render_html_video.mjs`：直接驱动原 HTML DOM 并逐帧编码。
- `scripts/render_html_video.sh`：原 Skill 检查、渲染和媒体验收入口。
- `references/motion-injection.md`：DOM 选择与动效规则。
- `examples/handwritten-html-motion-demo/`：由原创 HTML 示例直接生成的无声样片。
- `tests/test_renderer_contract.py`：防止重新排版与音频回归。
