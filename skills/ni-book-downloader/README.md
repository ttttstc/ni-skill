# ni-book-downloader

中文 | [English](./README.en.md)

> 按书名下载电子书：严格区分文字版（epub/mobi/azw3/fb2/txt）与版式版（PDF），搜索前先确认格式偏好。

`ni-book-downloader` 聚合五个渠道（GitHub 书库索引/城通网盘、LibGen、Z-Library、Anna's Archive、全网搜索兜底），按「免配额优先」自动降级；只有 PDF 而需要文字版时，提供 PDF 文字层提取兜底。完整规则、命令与验收标准见 [SKILL.md](./SKILL.md)。

## 快速开始

```bash
python scripts/book.py setup --launch-chrome   # first run: diagnose and open the login window (Z-Library only)
python scripts/book.py search "TITLE" --format text   # list candidates without downloading
python scripts/book.py auto "TITLE" --format text -o /path/to/books
python scripts/book.py extract-pdf book.pdf   # extract text layer from a digital-born PDF
```

## 下载渠道与降级顺序

| 顺序 | 渠道 | 账号与配额 | 说明 |
|------|------|------------|------|
| 1 | GitHub 书库索引 / 城通网盘 | 免账号免配额 | 中文文字版主力，约 2.4 万条书目索引 |
| 2 | LibGen | 免账号免配额 | 英文书主力，支持断点续传 |
| 3 | Z-Library | 需登录，免费账号约 10 本/天 | 中文书补充；配额用尽次日恢复 |
| 4 | Anna's Archive | 免账号（慢速） | 聚合来源补充 |
| 5 | 全网搜索 | 网盘链接需用户自有账号 | 多引擎搜索并提取全类型网盘与直链 |

## 格式语义

| 参数 | 行为 |
|------|------|
| `--format text` | 仅文字版（epub/mobi/azw3/fb2/txt） |
| `--format pdf` | 仅 PDF |
| 未指定（默认） | 全量格式允许，自动选优：epub > txt > pdf > mobi/azw3 |

## 评测与自检

```bash
python tests/smoke_test.py
```

`evals/` 是与 skill-up 配套的评测配置（8 个用例），最终 8/8 通过；离线自检不联网，用于验证脚本与匹配逻辑完好。

## 依赖与运行边界

- Python 3.10+，依赖见 `requirements.txt`（requests / websocket-client / pymupdf）。
- Z-Library 与全网搜索经配套 Chrome（CDP 调试端口）执行；首次用 `setup --launch-chrome` 拉起窗口并自行登录，技能全程不接触密码。
- 代理默认 `http://127.0.0.1:7890`，可用环境变量覆盖；引擎顺序、浏览器与缓存位置等均可在 SKILL.md 中查到。
- Agent 引擎的安全策略若拒绝下载类请求，技能以候选清单交付并停止，不绕过策略。
