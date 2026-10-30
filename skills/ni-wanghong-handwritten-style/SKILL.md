---
name: ni-wanghong-handwritten-style
description: 按用户指令创作王虹学术手写风 HTML 幻灯片，或从同一 HTML 渲染无声动画 MP4。用户明确选择 PPT、视频或两者时照此执行；未说明且无法从上下文判断时先询问。
---

# 王虹学术手写风创作

根据用户指令输出 PPT 或视频。PPT 与视频共用同一套 HTML 页面和视觉规范。

## 选择输出模式

- 用户明确要 PPT、演示文稿、幻灯片、HTML 或逐页 PNG 时，读取 references/ppt-workflow.md，完成 PPT 模式。
- 用户明确要动画、视频、MP4 或纯画面手写视频时，读取 references/video-workflow.md。若用户提供的是文章或讲稿，先按 PPT 工作流生成并检查 HTML，再将同一 HTML 渲染成视频。
- 用户同时要求 PPT 和视频时，只生成一次 HTML，然后完成两种交付。
- 用户没有说明输出类型且上下文无法判断时，先询问要 PPT 还是视频。不要默认同时生成两种成品。

## 共用要求

- 保持王虹学术手写风的 16:9 版面、淡暖白背景、清楚中文与原 HTML 布局。
- 优先使用本机或用户指定的 HanziPen SC；不可用时使用随包的小赖字体。小赖字体字形不同，交付时说明。若用户明确要求 HanziPen 而未提供，或实际字体校验失败，则停止交付。
- 视频模式直接渲染 HTML DOM，不重新排版文字；输出固定为 1920×1080、30fps、H.264、yuv420p，且没有音频流。
- 用户只要求某一种格式时，只交付该格式需要的文件。视频模式生成用于验收的封面和帧图不代表额外交付 PPT 成品。

## 详细工作流

- PPT 模式：references/ppt-workflow.md。
- 视频模式：references/video-workflow.md。
