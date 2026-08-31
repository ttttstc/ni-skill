---
name: ni-video2md
description: |
  将抖音等公开视频 URL 或分享文案转成本地 Whisper 生成的 Markdown 文字稿。用户说“视频转文字”“视频转 md”“提取字幕/文字稿”时触发；优先本地转录，缺少 ffmpeg、whisper.cpp、模型或浏览器工具时先下载或安装。只输出 .md，不生成 SRT；标题和文件名统一为“全文一句话概括-作者”；交付后可按用户指定路径归档。
---

# ni-video2md — 视频转 Markdown 文字稿

把一个公开视频链接或分享文案变成可保存、可检索的 Markdown 文字稿。默认针对中文视频，使用本地 `whisper.cpp` 推理，不调用云端 Whisper 或其他转录 API。

## 不可变要求

- 输入可以是单独的 URL，也可以是包含 URL 的完整抖音分享文案；从文案中提取第一个 `http(s)` URL。
- 先检查本地依赖。缺少 `ffmpeg`、`whisper-cli`、Whisper 模型、Playwright 或 Chromium 时，先通过脚本下载/安装；找到或安装可执行文件后，把其目录加入当前进程 `PATH`，Windows 同步写入当前用户 `PATH`；不能因为依赖缺失直接切换到云端转录。
- 只交付一个 `.md` 文件。不得调用 SRT 输出参数，不生成 `.srt` 文件，也不把字幕时间轴当成最终输出。
- 媒体、WAV 和 Whisper 中间 TXT 必须放在一次性私有临时目录；成功、失败或中断退出时都自动删除，不提供保留临时文件或指定工作目录的参数。依赖安装缓存是持久缓存，不属于转录临时文件。
- Markdown 必须保留原始来源 URL、捕获时间、语言、模型和 `local whisper.cpp` 标识；不要把带签名的临时媒体 URL 写入 Markdown 或打印出来。
- 转录完成后，必须基于清理后的完整文字稿生成一句话概括；默认由脚本使用本地抽取式算法生成，不调用额外云端模型。使用页面公开作者信息，页面取不到时再从分享文案提取，仍取不到就使用 `未知作者`，不得臆造作者。
- Markdown 的 `title`、一级标题和文件名必须完全一致，格式为 `{对全文的一句话总结}-{作者}`；文件名再加 `.md`。标题组件只做文件系统非法字符清理，不得改成网页标题或时间戳命名。
- 返回 Markdown 路径或文件后，必须询问用户是否归档；用户确认归档后，再询问或确认归档目录/完整目标路径。归档使用安全复制，保留原文件；目标已存在时停止并报告，不覆盖。
- 只处理公开可访问的媒体。不绕过登录、验证码、付费墙或访问控制；捕获不到媒体流时明确报告失败原因。

## 标准入口

优先运行配套脚本，不要重新手写下载、浏览器抓流或 Whisper 命令：

```bash
python ${SKILL_DIR}/scripts/video_to_md.py "<视频 URL 或完整分享文案>" -o <输出目录或 .md 路径>
```

`-o` 只用于指定输出目录；如果传入 `.md` 路径，只取其父目录，文件名仍强制使用生成的“概括-作者.md”。不指定 `-o` 时，脚本在当前目录生成该文件。常用参数：

```bash
python ${SKILL_DIR}/scripts/video_to_md.py "<URL>" --model-size small -o ./transcripts
```

`${SKILL_DIR}` 是本 `SKILL.md` 所在目录。Windows 首次运行会在 `NI_VIDEO2MD_HOME`（未设置时为 `%LOCALAPPDATA%\\ni-video2md`）缓存便携版 ffmpeg、Whisper.cpp 和模型；安装或发现 ffmpeg、Whisper.cpp 后会自动把可执行文件目录加入当前进程 `PATH`，并持久化到当前用户 `PATH`，同时复用已安装的 Chrome/Edge，没有可用浏览器时才下载 Playwright Chromium。已经打开的终端或 agent 需要重启后才能读取新的用户 `PATH`。脚本只下载公开依赖和视频，不需要 OpenAI API key。

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
2. 在一次性临时目录下载媒体，使用 `ffmpeg` 转成 16 kHz、单声道 WAV；流程结束后删除整个目录。
3. 使用本地 `whisper-cli` 和本地模型转录；默认 `small`，语言默认 `zh`。
4. 基于完整清理稿生成一句话概括，提取作者，组合出唯一标题，并把同名 `.md` 写到输出目录；成功或失败都不留下媒体、WAV、TXT 等中间文件。
5. 先把 Markdown 交付给用户，再询问是否归档。用户确认且给出路径后，运行安全复制：

```bash
python ${SKILL_DIR}/scripts/archive_markdown.py "<生成的 Markdown 路径>" "<用户指定的归档目录或 .md 路径>"
```

归档目录不存在时可以创建；如果用户给的是目录，保留原文件名；如果给的是 `.md` 路径，使用该完整目标路径。目标已存在时不得覆盖，先报告冲突。

脚本针对当前抖音页面的动态媒体流实现，未把旧版页面数据解析器或 `dyt` 作为必需依赖。页面结构、地区限制或登录状态变化时，必须把它报告为访问/兼容性失败，不能伪造文字稿。

## 输出合同

```markdown
---
source: "https://www.douyin.com/..."
title: "企业采购 AI Agent 不能只按单价判断。-VA7"
summary: "企业采购 AI Agent 不能只按单价判断。"
author: "VA7"
captured_at: "2026-08-31T00:00:00+00:00"
transcription: "local whisper.cpp"
model: "small"
language: "zh"
---

# 企业采购 AI Agent 不能只按单价判断。-VA7

## 文字稿

转录内容……
```

脚本成功时只报告 Markdown 路径；skill 随后交付该 Markdown，并询问是否归档。依赖下载失败、浏览器无法打开、没有媒体流、ffmpeg 转换失败或 Whisper 没有产出文字时，停止并给出下一步；不要降级到线上转录，也不要把部分结果冒充完整结果。

## 验收

- 输入为 URL 或分享文案时，能提取并打开公开视频链接。
- 依赖缺失时先下载/安装，缓存后可复用；设置环境变量时优先使用用户指定路径。
- 找到或下载 ffmpeg、whisper-cli 后，当前进程可以直接通过 `PATH` 找到它们；Windows 新开的终端或 agent 可以读取持久化的用户 `PATH`。
- 转录过程没有云端 Whisper/API 调用，且不会输出 API key、Cookie 或签名媒体 URL。
- 结果是一个非空 `.md` 文件，包含来源、捕获时间、模型、语言、作者、一句话概括和文字稿；`title`、一级标题和文件名完全一致，格式为“概括-作者”。
- 输出目录中没有由本 skill 生成的 `.srt` 文件。
- 转换结束后，运行期间创建的一次性临时目录和其中的媒体、WAV、TXT 均不存在；输出路径之外不留下转录中间文件。
- Markdown 交付后才询问归档；确认归档时按用户指定路径复制，原文件保留，已有目标不被覆盖。
- 失败场景明确可区分为依赖、网络/媒体、浏览器、音频转换或转录失败。
