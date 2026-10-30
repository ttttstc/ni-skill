# 原 HTML 动效注入规则

## 保真原则

渲染器在本机 Chrome/Chromium 中直接打开输入 HTML。视频层不创建或复制文字节点，字号和排版来自原页面 CSS。截图前将所有文字锁定到原 PPT Skill 预览封面的指定字体文件，并通过 Chrome DevTools Protocol 检查实际命中的字形。

## DOM 识别

- 页面：`.slide`
- 页面标题线：`.title-line`
- 演讲备注：`.notes`、`aside.notes`、`.speaker-notes`，渲染时隐藏
- 荧光标记：`.marker`、`.marker-yellow`、`.marker-green`、`.marker-coral`、`.mark-*`
- 手绘路径：当前页中的 `svg path`、`line`、`polyline`、`rect`、`circle` 与 `.scribble`

每页的直接子元素按 DOM 顺序分步出现。SVG 描边使用元素自身长度计算进度，填充图形使用透明度进入。

## 时间

默认每页 4 秒：

- 0.00–0.62 秒：标题组出现，标题线写入
- 0.34 秒后：直接子元素每隔约 0.24 秒出现
- 0.72 秒后：SVG 路径开始绘制
- 0.90 秒后：荧光标记开始揭示
- 最后 0.34 秒：暖白纸张覆盖并进入下一页

内容较密时增加 `--seconds-per-slide`，保持默认动效速度，让完整画面获得更长停留时间。
