# 来源清单与机制细节

本 skill 的脚本覆盖 5 个下载渠道（自动降级链）＋ PDF 文字提取兜底。

## 来源对照（免配额优先排序）

| 顺序 | 来源 | 账号 | 配额 | 覆盖 | 机制 |
|------|------|------|------|------|------|
| 1 | GitHub 索引 / 城通网盘 | 无 | 无（低速） | 中文文字版合集（2.4 万条） | 本地缓存索引按书名检索 → CDP 点「普通下载」→ 解包抽格式 |
| 2 | LibGen (`libgen.li`) | 无 | 无 | 英文书强，中文书弱 | 搜索页 HTML → `ads.php?md5=` → `get.php` 直链，支持断点续传 |
| 3 | Z-Library (`1lib.sk`) | 用户自备（配套 Chrome 登录） | 免费 ~10 本/天 | 中文书强，英文书也全 | 网页 `z-bookcard` → `/dl/` 触发 → CDN 直链 |
| 4 | Anna's Archive (`annas-archive.gl`) | 无 | 无（慢速） | 聚合 LibGen + Z-Lib + duxiu 等 | `slow_download` 等待后出限时直链（beta） |
| 5 | 全网搜索 | 网盘链接需用户账号 | 无 | 兜底 | 多引擎（默认 必应/百度/搜狗，`NI_BOOK_SEARCH_ENGINES` 可配）搜「书名 epub 下载」「书名 网盘」→ 解码跳转 → 扫描结果页与落地页提取全类型网盘/直链 |

## 降级逻辑（auto / batch）

1. 按 1→2→3→4 顺序逐源尝试（GitHub 索引仅参与非 pdf 格式；Z-Library 有意排后，省配额）。
2. 全空 → 全网搜索：网盘链接（夸克/百度/阿里/天翼/115/123）原样报告给用户（`needs_manual`）；直接文件链接与城通链接自动尝试下载。
3. `--no-web` 可关闭第 2 步；`--source` 可自定义参与渠道与顺序（如只走 `github` 则完全不碰 zlib 配额）。

## 配额策略

- Z-Library 免费账号 10 本/天是硬上限；默认链路把它排在免配额渠道之后，尽量不消耗。
- 需要集中用 zlib 时（比如网盘索引没有的冷门书），`--source zlib` 直连使用，`quota` 命令查余量，配额用尽次日重跑（batch 幂等）。
- 本机实测来源构成（一次 55 本文字版下载）：LibGen ~31（英文书全部）、Z-Library ~17（中文）、城通网盘 2、PDF 文字提取 5。

## Z-Library 会话与 DiamWall

- Z-Library 全站有 **DiamWall** 浏览器验证：无头 Chrome 与 requests 都会被 513 拦截；**有头 Chrome（CDP 专用 profile）一次验证后持续可用**。
- 首次使用由 `setup --launch-chrome` 引导：在打开的窗口里注册（免费）或登录一次，`remix_userid / remix_userkey` cookie 持久化在该 Chrome profile；skill 不接触密码。
- 对应的 CDP 端口默认 9222；判断登录：`book.py quota` 显示 `{logged_in: true, used: N, limit: 10}`。

## 城通网盘（ctfile）细节

- 下载由页面 JS 管理：点**普通下载 → 立即下载**后，**期间不要导航离开该标签页**，否则下载中断。
- 文件会落到浏览器下载目录（或 CDP 指定的 staging 目录，脚本两处都监听）；速度几十 KB/s~几百 KB/s；压缩包内含 epub+mobi+azw3 多格式，脚本自动解包并逐一落盘为 `{书名}.{格式}`。
- 若系统装有迅雷等下载管理器会抢存副本（下载目录出现 `.xltd`/`.xltd.cfg`），可忽略或删除，不影响脚本主流程。

## GitHub 索引（ebook-treasure-chest）

- 索引地址：`https://raw.githubusercontent.com/jbiaojerry/ebook-treasure-chest/main/docs/all-books.json`（约 2.4 万条，含书名/作者/城通链接/格式）。
- 本地缓存 `%LOCALAPPDATA%\ni-book-downloader\cache\ebook-chest.json`，7 天自动刷新；首次搜索会下载一次。
- 索引里的书全部是文字格式（epub/mobi/azw3），适合"文字版"需求；没有 pdf。

## 全网搜索兜底的边界

- 多引擎不锁单一来源：默认按 `bing,baidu,sogou` 顺序最多合并 2 个引擎的结果，`NI_BOOK_SEARCH_ENGINES` 可自定义顺序/子集；单引擎被限流时自动落到下一个。
- 关键词为两组：`书名 epub 下载` 无有效命中时追加 `书名 网盘 电子书`，扩大网盘链接召回。
- 网盘识别不限制类型（正则清单见 `scripts/book.py` 的 `NETDISK_RES`）：
  - 国内：夸克、百度（pan/yun/eyun）、阿里云盘（aliyundrive/alipan）、天翼（cloud.189.cn）、115、123 系列（123pan/123684/123865/123912）、迅雷云盘、微云、移动云盘（caiyun.139）、UC 网盘、蓝奏云（lanzou*.com）
  - 国际：Google Drive、Mega、OneDrive、Dropbox、TeraBox
  - 城通网盘单独识别（`ctfile.com/f/...`）并可直接自动下载
- 搜到网盘分享链接时原样交给用户（`needs_manual`）——转存/下载需要用户自己的网盘账号，skill 不代填、不绕过。
- 搜到可直接访问的文件链接（`.epub/.mobi/.azw3/.fb2/.txt/.pdf`）或城通链接时自动尝试下载并做文件头校验；城通/直链只尝试与书名上下文匹配（`_ctx_match`）的链接，避免误下书库页里的其他书。
- 结果里的中文电子书聚合站（`read678`、`shuyuan.org`、`qifeibook.com`、`deshu.cn`、`zhihailib.com` 等）质量参差，链接有效但常需网盘账号或注册。

## Anna's Archive 手工流程（脚本 beta 失败时）

1. 在 CDP Chrome 里打开 `https://annas-archive.gl/search?q=<书名>`（首次遇 DDoS-Guard 等几秒自动放行）。
2. 结果行里挑带 `EPUB/MOBI/AZW3` 标记的记录，点进 `/md5/<md5>` 详情页。
3. 详情页找 **🐢 Slow downloads** 段（"might require browser verification — unlimited downloads!"），点其中一个 Slow Partner Server（多试 #5~#10）。
4. 等待几秒后页面出现"To download, copy this URL..."，复制里面的 `http://<ip>:<port>/...` 限时直链。
5. 用 Python/curl 直接下载该链接（通常数十秒到几分钟有效）。

## PDF 与文字版

- 中文书常见的"文字版"在 zlib/网盘里多为 `epub/mobi/azw3/fb2/txt`；同一本书常有多个格式上传，**按 ISBN 或"书名 + 出版社"再搜一轮**常能翻出隐藏的文字版（例如按 ISBN `9787508698366` 搜出了只有 mobi 的《崔玉涛育儿百科》）。
- 数字原生 PDF 用 `extract-pdf` 直接提取文字层；扫描件（IMAGE 分类）只能 OCR 或换源，本 skill 不内置 OCR。
- 扫描版《崔玉涛图解家庭育儿》系列这类"图解书"，即使 epub 也可能是整页图片打包——文字版收益有限，蒸馏前先抽样确认。
