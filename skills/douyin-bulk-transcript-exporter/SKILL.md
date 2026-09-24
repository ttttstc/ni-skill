---
name: douyin-bulk-transcript-exporter
description: 给定抖音博主主页链接，用内置浏览器滚动加载并提取全部视频链接，再通过 web.fetch 批量导出每条视频的完整逐字稿、校订同音错字，最后按"视频标题-博主名.md"归档到本地目录。需要批量导出抖音某博主全部或最新 N 条视频逐字稿时使用。
---
# 抖音博主主页全量逐字稿导出

## 适用与边界
- 输入：抖音博主主页 `https://www.douyin.com/user/xxx`；也支持直接给一批单条视频 URL。
- 输出：本地 Markdown 文件，每个视频一个，文件名 `{视频标题}-{博主名}.md`。
- 本 Skill 只做本地文件归档，**不写飞书表格**。
- 逐字稿以抖音页面 web.fetch 返回的字幕为准；禁止伪造逐字稿、禁止写占位符。

## 输入确认（Step 0，先问齐再开跑）
开工前必须确认，缺失就问，不要假设：
1. **博主主页 URL**（必填）：用户没给就问"请提供博主主页链接"。
2. **输出目录**（必填）：默认 `./douyin_transcripts/{博主名}/`，用户指定则用指定目录。
3. **视频数量**：默认全量；说"最新 N 条"只取前 N。
4. **短视频处理**：默认跳过口播极短的片段（页面时长 < 约 20 秒）。用户要求全部导出则不跳过。
5. 是否校订错字：默认校订（见 Step 3）。

## Step 1：从博主主页提取全部视频链接（内置浏览器）
> 这是"全量"的关键环节：主页默认只加载前几条，必须滚动懒加载到底，再从 DOM 提取所有视频链接。

> **⚠️ 已有视频清单时，整步可跳过（最快路径）**：如果用户已提供或手头已有视频链接清单（整理好的 md / csv / json，或一批单条 URL），直接跳到 Step 2 逐条取稿，不要再爬主页。实测几百上千条就是这么跑的，零滚动、零反爬。
>
> **⚠️ 别再折腾"更优雅"的程序化取法**（已实测不可用，别重复试）：
> - **yt-dlp** 只有单条 `Douyin` 提取器，没有"列博主全部作品"的 user 列表能力，单条还会报"需要新鲜 cookie"。
> - **抖音作品列表 JSON 接口** `/aweme/v1/web/aweme/post/` 虽存在，但依赖 `a_bogus` 反爬混淆签名参数；在浏览器里用 fetch / XHR / http_get 调它都返回空，不重写抖音那套签名就调不通。
> - 结论：绕不开登录态浏览器，没有"一行命令拉全量"的捷径。

Windows 用 `computer_use_tool`（`plane="bu"`），代码里 `import seed_browser_use as bu`；Mac 用 `mac_computer_use_tool`（同为 `plane="bu"`）。API 一致。

1. 打开主页：
   ```python
   bu.navigate("https://www.douyin.com/user/xxx")
   bu.wait_for_load(timeout=25)
   ```
2. **登录检测**：作品列表显示"服务异常，重新刷新拉取数据"、出现登录弹窗、或页面顶部有"登录"按钮且列表为空 → 调用 `interaction.request_action(type="browserControl", display_message="抖音需要登录才能查看完整作品列表，请接管浏览器登录后交回。")`，用户交回后重新 `bu.snapshot()` 确认列表已加载。
3. **滚动加载到底**：
   ```python
   import time
   for _ in range(30):  # 视频多就加大上限
       bu.scroll(500, 500, "down", amount=3)
       time.sleep(1.5)
       txt = bu.get_page_text()
       if "暂时没有更多了" in txt:
           break
   ```
4. **提取视频链接（DOM 去重）**：
   ```python
   rows = bu.read_all("a[href*='/video/']", fields=["href"], limit=1000)
   seen, videos = set(), []
   for r in rows:
       href = r.get("href","")
       vid = href.rstrip("/").split("/")[-1].split("?")[0]
       if vid.isdigit() and vid not in seen:
           seen.add(vid)
           videos.append({"video_id": vid, "url": f"https://www.douyin.com/video/{vid}"})
   ```
   - 同一视频可能在"作品/推荐/置顶"多处出现，按 video_id 去重。
   - 保持页面顺序（新→旧）。用户只要最新 N 条就截断。
5. （可选）从 `bu.get_page_text()` 里顺带记录每条的标题、点赞数，写入结果清单便于核对。

> 注意：禁止用 curl/requests 直接请求抖音接口；必须走真实浏览器。视频较多时滚动上限要相应加大，别漏。

## Step 2：逐条 web.fetch 导出逐字稿
对 Step 1 得到的每个 `url`：
1. 首次：`web.fetch(url=url, pagination={"offset":0,"limit":4000})`。
2. **分页读完整**：看返回 `pagination_content` 的 `end_offset` 与 `total_length`。若 `end_offset < total_length`，下一次用 `pagination.offset = 上一次 end_offset` 继续读，直到 `end_offset >= total_length`，把各段拼接成完整文本。
3. **分离正文**：完整文本第一个空行之前是标题+文案，空行之后是逐字稿正文。
4. **完整性判定**（任一不满足即视为该条失败）：
   - 正文 < 50 字；
   - 结尾不是句末标点（。？！…），像被拦腰截断；
   - 正文里出现"完整内容""web.fetch""已通过"等占位词；
   - web.fetch 只回了页面标题（`total_length` 很小，正文几乎为空）。
   - 这种情况**不要重试到死、不要伪造**：先按 Step 2.5 走 ni-video2md 本地转写回退；回退也失败才记入失败清单，继续下一条。
5. 用户说"不要逐字稿/只要清单"时跳过本步。

## Step 2.5：web.fetch 失败时的回退——ni-video2md 本地转写
> 实测：5~7 分钟的长口播视频，web.fetch 经常只回标题；这类恰恰是最值钱的长内容。用本机 `ni-video2md`（whisper.cpp 本地推理）抓媒体流转写，已验证可用。**短视频（<约20秒金句卡片）不要走这一步**，它们多半是配乐文字卡，转出来也没价值，直接判"无口播"。

1. 入口脚本（`SKILL.md` 同级 `ni-video2md` skill 目录下）：
   ```bash
   python "<ni-video2md 安装目录>/scripts/video_to_md.py "<视频URL>" -o <临时输出目录>"
   ```
   - Windows 实测安装目录：`C:\Users\泥巴猪\.agents\skills\ni-video2md`。
   - 首次运行缺依赖（ffmpeg / whisper.cpp / yt-dlp / playwright）会自动下载到 `%LOCALAPPDATA%\ni-video2md`；若报 `--user install disabled`，先手动 `python -m pip install playwright`，再重跑。
   - 抖音走无头浏览器抓公开媒体流；**不要绕过登录/验证码**，抓不到流就报失败。
2. **并行**：多条回退可同时后台跑（whisper 吃 CPU，5 条并行约每条几分钟）。单条命令 `exit code 1` 但 stdout 出现"已保存 Markdown：…"即为成功（PowerShell 把进度写到 stderr 会误报）。
3. **重包装成本归档格式**（关键，别直接用脚本产物文件名）：脚本自动生成的文件名是"一句话概括-我的.md"、author 被识别成"我的"、title 是抽取式概括——**全部要替换**：
   - 读脚本产出的 `.md`，取 `## 文字稿` 之后的正文；
   - 按 Step 4 模板重写，`title`/文件名用**真实视频标题**（来自 Step 1 清单），`author` 改成博主名；
   - frontmatter 的 `transcription` 写 `local whisper.cpp (ni-video2md)`，并加 `model: "small"`。
4. **whisper small 错字更密，校订要更仔细**（见 Step 3）。常见误听对照：盈利模式→盈利博士、阅历→月历/月历、岗位→岛位、画大饼→花大饼、拿捏→拆钱、降维打击→降为打击、独轮车→独卵、讲群众路线→讲原汉（延安）、精英→金融、流程/术语词等同音替换。仍只改上下文唯一可判定的。
5. **失败判据**：报 `ffmpeg 无法从视频流提取音频` 且重试 1~2 次仍失败 = 该视频登录态/媒体流受限，记入 `_failed.json`，不要硬刚。

## Step 3：校订同音错字（默认开启）
抖音自带字幕会有同音/近音错字。规则：
- **只改**"根据上下文语义可以唯一确定"的同音错字，例如：下星期→下行期（经济下行语境）、办的出惨→办得出彩、提达到→提拔到、匪柴→肥差、懒活→烂活、卯足的劲→卯足了劲。
- **不改写风格、不润色、不增删观点**，保留口语化表达和博主语气。
- **拿不准的一律不动**（如个别无法唯一判定的词，原样保留）。
- 校订后句子必须通顺、原意不变。

## Step 4：写入 Markdown 文件
对每条成功视频写一个文件：
- **文件名**：`{视频标题}-{博主名}.md`。
- **文件名清洗**：把 `\ / : * ? " < > |` 及换行替换为全角或删除；中文逗号"，"保留。标题里若自带全角冒号"："可保留。
- **同标题冲突**：若目录下已存在同名文件，文件名追加 `-{video_id}` 后缀，避免覆盖。
- **文件内容模板**：
  ```markdown
  ---
  source: "{视频URL}"
  title: "{视频标题}-{博主名}"
  summary: "{视频标题}"
  author: "{博主名}"
  captured_at: "{ISO8601 当前时间，如 2026-09-23T11:00:00+08:00}"
  transcription: "douyin web.fetch"
  # 走 Step 2.5 回退时改为：transcription: "local whisper.cpp (ni-video2md)"，并加一行 model: "small"
  language: "zh"
  ---

  # {视频标题}-{博主名}

  ## 文字稿

  {校订后的逐字稿，按自然段分段}
  ```
- 短视频（Step 0 判定 <20 秒）跳过不写文件；用户要求全量时才写，并在文字稿处写"无逐字稿（视频过短/无口播）"。

## Step 5：自检与交付
1. 核对输出目录 `.md` 文件数 == 成功条数；统计失败数。
2. 抽查 2~3 个文件：frontmatter 完整、`## 文字稿` 存在、正文无占位符、长度合理。
3. 失败清单写入输出目录 `_failed.json`（含 video_id、title、url、原因），**不要**把失败条写成占位 md。
4. 向用户汇报：成功数、失败数、输出目录、失败清单摘要。

## 已知限制与经验
- **部分长视频 web.fetch 只回标题**：5~7 分钟的长口播视频常见。**不要直接判死**——先走 Step 2.5 ni-video2md 本地 whisper 回退，实测多数能补出完整逐字稿；回退也失败才记 `_failed.json`。
- **短视频（<约20秒金句卡）**：web.fetch 只回标题是常态，浏览器多为配乐文字卡、无口播，**不要再走 whisper 回退**，判"无逐字稿"即可。
- **妙记/在线转写链路对抖音支持有限**，本 Skill 不依赖它；统一用本机 ni-video2md 做回退。
- **ni-video2md 产物要重包装**：脚本自动标题是概括句、author 是"我的"，必须换成真实视频标题和博主名（见 Step 2.5 第3点）。
- **登录态**：看主页作品列表、ni-video2md 抓抖音媒体流都可能需要登录；用小号即可，仅用于读取公开内容。
- **不要因为个别视频失败就停整批**；失败单独记录，其余照常导出。
- 视频量大时（几百上千条），可按连续下标切成若干分片并行处理，但每个分片内部仍逐条顺序 web.fetch，避免触发限流；回退转写可少量并行。
