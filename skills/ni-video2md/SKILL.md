---
name: ni-video2md
description: |
  将抖音等公开视频 URL 或分享文案转成本地 Whisper 生成的 Markdown 文字稿。用户说“视频转文字”“视频转 md”“提取字幕/文字稿”时触发；优先本地转录，缺少 ffmpeg、whisper.cpp、模型或浏览器工具时先下载或安装。只输出 .md，不生成 SRT；不适用于要求云端转录、翻译或视频摘要的请求。
---

# ni-video2md — 视频转 Markdown 文字稿

把一个公开视频链接或分享文案变成可保存、可检索的 Markdown 文字稿。默认针对中文视频，使用本地 `whisper.cpp` 推理，不调用云端 Whisper 或其他转录 API。

## 不可变要求

- 输入可以是单独的 URL，也可以是包含 URL 的完整抖音分享文案；从文案中提取第一个 `http(s)` URL。
- 先检查本地依赖。缺少 `ffmpeg`、`whisper-cli`、Whisper 模型、Playwright 或 Chromium 时，先通过脚本下载/安装；不能因为依赖缺失直接切换到云端转录。
- 只交付一个 `.md` 文件。不得调用 SRT 输出参数，不生成 `.srt` 文件，也不把字幕时间轴当成最终输出。
- Markdown 必须保留原始来源 URL、捕获时间、语言、模型和 `local whisper.cpp` 标识；不要把带签名的临时媒体 URL 写入 Markdown 或打印出来。
- 默认只做转录和明显的术语噪声清理，不摘要、不翻译、不改写观点。若用户另外要求摘要或翻译，先把它视为后续独立任务。
- 只处理公开可访问的媒体。不绕过登录、验证码、付费墙或访问控制；捕获不到媒体流时明确报告失败原因。

## 标准入口

优先运行配套脚本，不要重新手写下载、浏览器抓流或 Whisper 命令：

```bash
python ${SKILL_DIR}/scripts/video_to_md.py "<视频 URL 或完整分享文案>" -o transcript.md
```

不指定 `-o` 时，脚本根据页面标题在当前目录生成 `.md` 文件。常用参数：

```bash
python ${SKILL_DIR}/scripts/video_to_md.py "<URL>" --model-size small -o transcript.md
python ${SKILL_DIR}/scripts/video_to_md.py "<URL>" --keep-work
```

`${SKILL_DIR}` 是本 `SKILL.md` 所在目录。Windows 首次运行会在 `NI_VIDEO2MD_HOME`（未设置时为 `%LOCALAPPDATA%\\ni-video2md`）缓存便携版 ffmpeg、Whisper.cpp 和模型；同时复用已安装的 Chrome/Edge，没有可用浏览器时才下载 Playwright Chromium。脚本只下载公开依赖和视频，不需要 OpenAI API key。

支持的环境变量：

| 变量 | 用途 |
|------|------|
| `NI_VIDEO2MD_HOME` | 工具、模型和下载缓存目录 |
| `NI_VIDEO2MD_FFMPEG` / `FFMPEG_PATH` | 指定 ffmpeg 可执行文件 |
| `NI_VIDEO2MD_WHISPER_CLI` / `WHISPER_CLI` | 指定 whisper-cli 可执行文件 |
| `NI_VIDEO2MD_MODEL` / `WHISPER_MODEL` | 指定本地 `ggml-*.bin` 模型 |
| `NI_VIDEO2MD_BROWSER` / `BROWSER_PATH` | 指定 Chrome、Edge 或 Chromium 可执行文件 |

## 运行边界

1. 提取 URL，使用无头浏览器打开公开页面并捕获媒体流。
2. 下载媒体到临时目录，使用 `ffmpeg` 转成 16 kHz、单声道 WAV。
3. 使用本地 `whisper-cli` 和本地模型转录；默认 `small`，语言默认 `zh`。
4. 清理临时媒体和中间文件，只把 Markdown 写到用户指定路径。

脚本针对当前抖音页面的动态媒体流实现，未把旧版页面数据解析器或 `dyt` 作为必需依赖。页面结构、地区限制或登录状态变化时，必须把它报告为访问/兼容性失败，不能伪造文字稿。

## 输出合同

```markdown
---
source: "https://www.douyin.com/..."
title: "视频标题"
captured_at: "2026-08-31T00:00:00+00:00"
transcription: "local whisper.cpp"
model: "small"
language: "zh"
---

# 视频标题

## 文字稿

转录内容……
```

脚本成功时只报告 Markdown 路径。依赖下载失败、浏览器无法打开、没有媒体流、ffmpeg 转换失败或 Whisper 没有产出文字时，停止并给出下一步；不要降级到线上转录，也不要把部分结果冒充完整结果。

## 验收

- 输入为 URL 或分享文案时，能提取并打开公开视频链接。
- 依赖缺失时先下载/安装，缓存后可复用；设置环境变量时优先使用用户指定路径。
- 转录过程没有云端 Whisper/API 调用，且不会输出 API key、Cookie 或签名媒体 URL。
- 结果是一个非空 `.md` 文件，包含来源、捕获时间、模型、语言和文字稿。
- 输出目录中没有由本 skill 生成的 `.srt` 文件。
- 失败场景明确可区分为依赖、网络/媒体、浏览器、音频转换或转录失败。
