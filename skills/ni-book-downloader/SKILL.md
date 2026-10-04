---
name: ni-book-downloader
description: |
  按书名下载电子书，区分文字版（epub/mobi/azw3/fb2/txt）与版式版（pdf）：指定 PDF 则只下 PDF，指定文字版则只下文字格式，**未指定格式时全量格式允许**（自动选最优，优先 epub）。搜索前可先确认书名、格式偏好和目标目录。渠道按免配额优先：GitHub 电子书索引/城通网盘 → LibGen（免账号）→ Z-Library（配套 Chrome 登录，免费账号每日约 10 本）→ Anna's Archive（慢速免费），全部没有时自动全网搜索（网盘链接交用户、直接文件链接自动下载）；只有 PDF 而用户要文字版时用 PDF 文字层提取兜底。用户说"下载电子书""找书下载""帮我下这本书""book download"时触发。
---

# ni-book-downloader — 按书名下载电子书

把一个书名（或一批书名）变成落在指定目录里的电子书文件，并且**在开始搜索前先和用户确认格式偏好**。核心是格式区分：

| 类别 | 格式 | 适用 |
|------|------|------|
| **文字版** | epub / mobi / azw3 / fb2 / txt | 蒸馏、检索、RAG、精读 |
| **版式版** | pdf | 保版式、图示多的书；可能是数字原生或纯扫描件 |

## 不可变要求

- **先确认后搜索**：动任何网络请求之前，与用户确认三件事：① 书名（尽量含作者/版次等消歧信息）；② 格式偏好（**文字版 / PDF / 未指定**）；③ 保存目录。可先问一句格式偏好，用户回答"都行/随便/没要求"或未指定时按 `any` 处理，不阻塞不追问。
- **格式语义固定**：`--format text` = 仅 `epub/mobi/azw3/fb2/txt`；`--format pdf` = 仅 pdf；**未指定（默认 any）= 全量格式允许**——所有格式都可参与选优（偏好顺序 epub > txt > pdf > mobi/azw3；网盘压缩包内自带的多种格式会全部保留落盘）。用户明确要文字版时，候选里不得混入 pdf 冒充交付；只有 pdf 存在时要如实报告并给出兜底选项。
- **来源优先级与降级链（免配额优先）**：GitHub 电子书索引/城通网盘（免账号免配额，中文文字版第一优先）→ LibGen（免账号免配额，英文书主力）→ Z-Library（**每日 ~10 本配额是瓶颈，前面都拿不到才动它**）→ Anna's Archive（慢速免费，beta）→ **全部没有时自动全网搜索兜底**：找到网盘链接（夸克/百度/阿里等）必须原样交给用户处理（需要用户自己的网盘账号），找到可直接下载的文件或城通链接才自动尝试。`--source` 可自定义参与渠道与顺序。
- **账号与配额是用户的边界**：Z-Library 会话由用户自己在配套 Chrome（CDP 专用 profile）里登录维护；不得向用户索取密码、不得把密码写入文件或对话。免费账号每日下载约 10 本为硬约束，配额用尽必须明确报告（`quota` 命令可查），不得伪造成功、不得同一天反复重试刷量。
- **候选要可核验**：`search` 输出候选表（标题/作者/格式/大小/年份/来源）供用户或调用方确认；下载用 `get` 指定候选。`auto` 仅用于用户已确认格式、且接受自动选优的场景。
- **防伪书**：过滤 `summary of / study guide / workbook / companion / 解读 / 笔记` 类读书笔记伪书；标题或作者对不上的候选直接丢弃，宁缺毋滥。
- **下载必校验**：每个文件落盘前校验扩展名对应的文件头（pdf=`%PDF`、epub=zip、mobi/azw3=`BOOKMOBI`、fb2=XML）与大小阈值；校验失败的文件不得留在最终目录（改名 `.part` 或删除），失败要报告原因。
- **PDF 兜底有边界**：用户要文字版而只有 PDF 时，先做文字层检测：数字原生 PDF 用 `extract-pdf` 提取成 `.txt` 交付；纯扫描件（IMAGE 分类）明确报告"需要 OCR 或换源"，不得用 OCR 乱码文本冒充文字版。
- **命名与落盘**：文件名固定为 `{书名}.{扩展名}`（非法字符替换为 `_`）。每本书的报告包含：来源、标题、格式、大小、路径。批量模式输出 `ni_book_batch_report.json`。

## 标准入口

优先运行配套脚本，不要临场手写抓取逻辑：

```bash
# 1. 环境诊断（依赖 / 代理 / Chrome / Z-Library 登录与配额）
python ${SKILL_DIR}/scripts/book.py setup
# 首次使用 Z-Library：拉起专用 Chrome 并打开登录页；引导用户在窗口里
# 注册（免费账号，每日约 10 本配额）或登录，登录一次后会话保存在该 Chrome profile
python ${SKILL_DIR}/scripts/book.py setup --launch-chrome

# 2. 列候选（不消耗配额），交给用户确认；--web 附带全网搜索结果
python ${SKILL_DIR}/scripts/book.py search "崔玉涛育儿百科" --format text --lang zh
python ${SKILL_DIR}/scripts/book.py search "某本冷门书" --format text --web

# 3. 下载指定候选（用 search 输出里的 id）
python ${SKILL_DIR}/scripts/book.py get --source zlib --dl /dl/xxxx --name "崔玉涛育儿百科" --ext epub -o D:\books
python ${SKILL_DIR}/scripts/book.py get --source libgen --md5 5f5e... --name "The Montessori Baby" --ext epub -o D:\books
python ${SKILL_DIR}/scripts/book.py get --source github --link "https://url89.ctfile.com/f/..." --name "书名" --ext epub -o D:\books

# 4. 自动选优下载（用户已确认格式后可用；前四渠道全空时自动全网兜底，--no-web 可关闭）
python ${SKILL_DIR}/scripts/book.py auto "The Montessori Baby" --format text --lang en -o D:\books

# 5. 批量（manifest.json：{"books": [{"name": "...", "author": "...", "lang": "zh", "queries": ["..."]}]}）
python ${SKILL_DIR}/scripts/book.py batch manifest.json --format text -o D:\books

# 6. 其他
python ${SKILL_DIR}/scripts/book.py quota            # Z-Library 配额
python ${SKILL_DIR}/scripts/book.py extract-pdf book.pdf -o book.txt

# 7. 离线自检（不联网，验证脚本与匹配逻辑完好）
python ${SKILL_DIR}/tests/smoke_test.py
```

`${SKILL_DIR}` 是本 `SKILL.md` 所在目录。所有命令输出 JSON，便于调用方解析。

支持的环境变量：

| 变量 | 用途 |
|------|------|
| `NI_BOOK_PROXY` | HTTP 代理，默认 `http://127.0.0.1:7890`；直连环境设为空字符串 |
| `NI_BOOK_CDP_PORT` | 浏览器调试端口，默认 `9222` |
| `NI_BOOK_CHROME` | 浏览器可执行文件路径；默认读 Windows 注册表取**系统默认浏览器**（Chrome/Edge/Brave/Vivaldi/Opera），取不到再回退 Chrome→Edge |
| `NI_BOOK_CHROME_PROFILE` | CDP 专用用户目录，默认 `%LOCALAPPDATA%\ni-book-downloader\chrome-profile` |
| `NI_BOOK_SEARCH_ENGINES` | 全网搜索的引擎顺序，默认 `bing,baidu,sogou`；不锁单一引擎，可自由增删排序 |
| `NI_BOOK_CACHE` | 索引缓存目录，默认 `%LOCALAPPDATA%\ni-book-downloader\cache` |

依赖：`requests`、`websocket-client`、`pymupdf`（见 `requirements.txt`）。

## 运行边界

1. **LibGen（libgen.li）**：免账号，直接 HTTP；适合英文书，中文书覆盖有限。搜索页解析 → 评分 → `ads.php` 换下载 key → `get.php` 拉取，内置断点续传与重试，偶发 500/断流靠重试解决。
2. **Z-Library（1lib.sk，经 CDP）**：必须复用用户在当前设备上的已登录会话——首次使用运行 `setup --launch-chrome`，引导用户在专用窗口中注册（免费）或登录，之后会话持久保存在该 Chrome profile，skill 全程不接触密码。机制：CDP 打开搜索页解析 `z-bookcard` 卡片 → 导航 `/dl/` 触发下载 → 截获 `Browser.downloadWillBegin` 里的 CDN 直链 → Python 请求拉取。期间 Chrome 会取消浏览器侧下载、迅雷等下载器可能抢存副本，都不影响本流程。**该站有 DiamWall 防爬，无头浏览器过不去，必须用有头 Chrome 的 CDP 会话**。配额 10 本/天，配额用尽时 `/dl/` 不再产生下载事件，报"配额用尽或条目失效"，次日重跑即可（`batch` 幂等，已完成的会跳过）。
3. **Anna's Archive（annas-archive.gl，beta）**：站内有 DDoS-Guard，需经 CDP 真浏览器访问；下载走 `slow_download` 慢速伙伴服务器拿到限时直链。反爬会波动，失败属正常，按来源顺序自动降级。
4. **GitHub 电子书索引（城通网盘）**：本地缓存 `jbiaojerry/ebook-treasure-chest` 的 2.4 万条书目索引（`%LOCALAPPDATA%\ni-book-downloader\cache`，7 天自动刷新），按书名筛选后经 CDP 打开城通页面点击「普通下载」；下载由页面 JS 管理，期间不得导航离开该标签页；得到的压缩包自动解包并抽出 epub/mobi/azw3 等文字格式。速度慢（几十 KB/s 到几百 KB/s），适合作为前三个来源全空后的兜底。
5. **全网搜索兜底**：前四渠道都没有时，经 CDP 用系统浏览器按引擎顺序（默认 必应→百度→搜狗，`NI_BOOK_SEARCH_ENGINES` 可配，最多合并 2 个引擎结果）搜索「书名 epub 下载」「书名 网盘 电子书」两组关键词；自动解码跳转链接（Bing `u=` 参数、百度 link 跳转），扫描搜索结果页与落地页，提取**全类型网盘链接**（夸克/百度/阿里/天翼/迅雷/微云/移动云盘/UC/蓝奏云/123 系列/城通，及 Google Drive/Mega/OneDrive/Dropbox 等）与直接文件链接：网盘链接原样报告给用户；直接文件链接与城通链接自动尝试下载并校验。返回状态 `needs_manual` 时把链接清单完整交给用户。
6. **PDF 文字层提取**：`extract-pdf` 用 PyMuPDF 直提数字原生 PDF 文字，输出分类 `TEXT/SPARSE/IMAGE`；扫描件报告 `scanned_no_text`。
7. **Agent 策略边界**：如果运行本 skill 的 Agent 引擎/模型因自身安全策略拒绝执行下载类操作，应尊重该策略——以候选清单、环境诊断或说明性交付收尾，不得改写话术、拆分步骤或换措辞来绕过策略；在评测（如 skill-up）中遇到此类拒答用例，按"引擎策略阻断"记录，而不是当作 skill 缺陷去修。

来源细节与手工兜底手法（网盘、城市通等）见 `references/sources.md`；常见故障排查见 `references/troubleshooting.md`。

## 输出合同

每本书下载成功时报告：

```json
{
  "status": "downloaded",
  "source": "zlib",
  "title": "崔玉涛育儿百科",
  "ext": "mobi",
  "bytes": 2560000,
  "path": "D:\\books\\崔玉涛育儿百科.mobi"
}
```

`status` 取值：`downloaded`（成功）/ `exists`（已存在跳过）/ `not_found`（含 `tried` 各渠道尝试记录）/ `download_failed`（有候选但下载失败）/ `verify_failed`（文件头校验失败）/ `picked`（dry 模式）/ `needs_manual`（全网兜底只找到需用户账号的网盘链接，附 `links` 清单与 `results` 网页结果）。批量另写 `ni_book_batch_report.json`。

失败时必须给出下一步建议（换格式、换来源、次日记配额重试、或对扫描件做 OCR），不得把不可用文件当成功交付。`needs_manual` 时必须把网盘链接原样交给用户，不得代填账号或尝试绕过网盘登录。

## 验收

- 用户指定 `text` 时结果里没有 pdf；指定 `pdf` 时结果里没有 epub/mobi/txt；**未指定（默认 any）时全量格式均参与**（含 pdf），GitHub 索引来源仅在非 pdf 格式下参与。
- 未指定格式时 `auto` 能对同一本书接受 pdf 或文字格式并按偏好顺序（epub > txt > pdf > mobi/azw3）选优；网盘压缩包内的多种格式全部保留落盘。
- 用 `search` + `get` 能精确下载用户选中的候选（含 github/网盘链接）；`auto` 在用户已确认格式时按「LibGen→Z-Library→Anna's→GitHub」降级链自动完成搜索、选优、下载、校验，全空时自动全网兜底。
- GitHub 索引搜索命中正确书目并返回城通链接；城通下载完成后能自动解包并抽出文字格式文件。
- 全网兜底提取到夸克/百度等网盘链接时，返回 `needs_manual` 并附完整链接清单，不尝试绕过网盘登录；直接文件/城通链接自动尝试下载。
- 下载产物通过文件头校验（pdf/epub/mobi/azw3/fb2 各自 magic），失败文件不污染输出目录。
- Z-Library 配额可通过 `quota` 查询；配额用尽时如实报告并给出次日重试建议，批量模式幂等可重跑。
- 只有扫描版 PDF 时，`extract-pdf` 返回 `scanned_no_text` 并明确提示需要 OCR 或换源，不产出乱码文本。
- 过程中不向用户索取密码；不把带签名 CDN 直链或会话 cookie 写入报告。
