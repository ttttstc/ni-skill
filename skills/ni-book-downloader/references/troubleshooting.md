# 故障排查

## 环境类

| 症状 | 原因 | 处理 |
|------|------|------|
| `zlib: Chrome CDP 未运行` | CDP 专用 Chrome 没开 | `python book.py setup --launch-chrome`，在弹出的窗口登录 Z-Library |
| `CDP unreachable` | 调试端口被占用/Chrome 换了 profile | 检查 `NI_BOOK_CDP_PORT`；确认 Chrome 用 `--remote-debugging-port` + `NI_BOOK_CHROME_PROFILE` 启动 |
| 所有来源失败 | 代理没开或端口不对 | `setup` 看 `checks.proxy`；改 `NI_BOOK_PROXY` 或置空直连 |
| `websocket handshake 403` | CDP 拒绝带 Origin 的 WebSocket | 脚本已用 `suppress_origin=True`；如手动连接需同款处理 |
| 本地 127.0.0.1:9222 连不上但端口在听 | Chrome 调试端口只监听了 IPv6 `[::1]` | 先试 `http://[::1]:9222/json/version`；脚本已双栈探测 |

## Z-Library 类

| 症状 | 原因 | 处理 |
|------|------|------|
| 搜索页 513 / `DiamWall` | 无头浏览器或 requests 被防爬 | 必须用有头 Chrome 的 CDP 会话；不要用 requests 直连 1lib.sk |
| `no downloadWillBegin (配额用尽或条目失效)` | 当日 10 本配额用尽，或 /dl/ token 过期 | `quota` 确认；配额用尽→次日重跑（batch 幂等）；条目失效→重新 `search` 换新的 /dl/ token |
| 搜索出 0 卡片 | 未登录/会话掉了 | 在 CDP Chrome 里重新登录；`quota` 验证 |
| 下载到 1083 字节的 html | 拿成了 DiamWall 拦截页 | 不会落盘为最终文件（文件头校验拦截）；若无头模式请改有头 |
| 下载目录出现 `.xltd` | 迅雷等抢存 | 可忽略；主流程走 CDN 直链不受影响 |

## LibGen 类

| 症状 | 原因 | 处理 |
|------|------|------|
| `get status 500/503` | 服务端限流 | 脚本自动重试+退避；仍失败换 zlib 来源 |
| 连接中断 `IncompleteRead` | 大文件中途断流 | 脚本支持 `Range` 断点续传，重跑同一命令会从 `.part` 续传 |
| 检索结果全被过滤 | 标题/作者对不上（如英译名、ISBN 为题） | 用 `auto --loose --must-any "关键词"`；或 `search` 后用 `get` 手工指定候选 |
| 中文书找不到文字版 | LibGen 中文覆盖弱 | 切 `--source zlib`（或 `--source zlib,aa`） |

## Anna's Archive 类

| 症状 | 原因 | 处理 |
|------|------|------|
| 页面停在 `DDoS-Guard` | 反爬校验 | 等 5~15 秒通常自动放行；重试一次；仍不行换来源 |
| `slow_download` 无直链 | 排队/验证波动 | 多试几个 Slow Partner Server 编号；数十秒后重读页面 |
| SSL EOF / 连不上 | 域名或线路问题 | 换 `annas-archive.gl` / 保持代理开启 |

## GitHub 索引 / 城通网盘类

| 症状 | 原因 | 处理 |
|------|------|------|
| 首次搜索等待较久 | 首次会拉取 6.4MB 索引并缓存 | 正常；之后走本地缓存（7 天刷新） |
| ctfile 下载很慢 | 网盘免费通道限速（几十 KB/s~几百 KB/s） | 正常；大批量建议挂在后台慢慢跑 |
| ctfile 下载中断/超时 | 下载由页面 JS 管理，页签被导航走了 | 脚本已在专用页签等待，期间不要手动操作该窗口 |
| 下载目录出现 `.xltd` | 迅雷等管理器抢存 | 可忽略；主文件照常落盘 |
| 压缩包解出"免责声明.txt"等小文件 | 仅抽取 ≥50KB 的电子书格式文件 | 已在解包时过滤 |

## 全网搜索类

| 症状 | 原因 | 处理 |
|------|------|------|
| 两个引擎都返回空 | 连续高频查询触发限流 | 脚本自带一次退避重试；仍空则稍等几分钟再跑 |
| 只找到网盘链接 | 夸克/百度等需要用户账号 | 正常行为（`needs_manual`）；把链接清单交给用户处理 |
| Bing 结果 URL 是跳转链接 | Bing 用 `bing.com/ck/a` 包装 | 脚本自动解码 `u=` 参数还原真实地址 |

## PDF / 提取类

| 症状 | 原因 | 处理 |
|------|------|------|
| `extract-pdf` 返回 `scanned_no_text` | 纯扫描件 | 找 epub/文字版换源；或接受 OCR 方案（本 skill 不内置） |
| `SPARSE` 分类 | 图文混排（图解书） | 提取文字仅含图注，蒸馏价值有限，抽样确认后再用 |
| pymupdf 未安装 | 缺依赖 | `pip install pymupdf` |

## 快速自检顺序

1. `setup` → 依赖/代理/Chrome/CDP/登录/配额 一屏看全。
2. `search "任一本英文书" --source libgen` → LibGen 链路。
3. `search "任一本中文书" --source zlib` → Z-Library 链路（搜索不耗配额）。
4. 下载只挑一本小体积书验证 → 再批量。
