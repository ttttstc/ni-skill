# Poetry Book

把诗词、古籍资料、技术文章和课程讲义，做成**有出处、可重建、经过逐页检查的 LaTeX PDF**。

这不是一张封面模板，而是一条完整流水线：资料结构化 → 编年或文章块解析 → 六套主题排版 → 字体与内容检查 → PDF、来源清单和预览图。

![六套主题](docs/images/theme-gallery.png)

## 能做什么

- **编年诗传与文集**：作品排序、未系年附录、题解、笺注、批语、出处和篇名索引。
- **技术图文专题**：解析 Markdown 标题、粗体、列表、链接、图片、代码块、简单表格和引用。
- **六套真实主题**：每套都能生成完整 PDF，不只是颜色名称。
- **来源可追踪**：原稿、图片地址、SHA-256、作品页映射和构建清单一并保留。
- **结果可验证**：检查缺字、字体嵌入、溢出、越界、异常空白页、横排、链接、图片比例和 Markdown 残留。
- **离线重建**：随附诗词书稿和技术排版夹具，可脱离原始工作目录重建。

## 六套主题

| ID | 中文名 | 风格 |
|---|---|---|
| `song-mist` | 烟雨留白 | 默认；米白、淡墨、远山、江面与朱印 |
| `celadon` | 青瓷天青 | 青灰纸色、天青层山，适合清透的技术专题 |
| `ink-zen` | 墨禅寂照 | 灰白、墨山、圆相与墨评 |
| `cinnabar-seal` | 朱砂印谱 | 米纸、朱砂、鉴藏印章 |
| `moon-river` | 月夜赤壁 | 蓝灰、明月、江水与夜航 |
| `bamboo` | 竹影清风 | 淡青绿、疏竹与叶影 |

所有主题均为**简体中文、横排**。宋式审美留在封面、章首、纸色和装帧线上，不以竖排牺牲阅读效率。

## 真实案例

### 苏轼编年诗传

在原始项目中完成《用诗词读懂苏轼——一蓑烟雨任平生》：1448 页、3202 条作品、82 篇名篇精注。默认全书通过 16 项项目测试、73 项来源检查和 19 项 PDF 检查。

![苏轼封面](docs/images/sushi-cover.png)

### 技术文章排版

随附技术排版夹具，展示代码、表格、引用和链接的处理方式。

![技术排版示例](docs/images/technical-layout.png)

## 安装

此副本位于 ni-skill 的 skills/ni-poetry-book，源自 [tjxj/z-skills](https://github.com/tjxj/z-skills) 的 z-poetry-book。保留上游代码、资源与许可文件。

### 环境要求

- Python 3.9+
- `latexmk`、LuaLaTeX、Ghostscript
- 中文默认使用随包的 Noto Serif SC（思源宋体简体版）；可通过 `POETRY_BOOK_MAIN_FONT` 指定其他主中文字体文件
- 英文使用本机提供的 Anthropic Serif 正体 TTF/OTF；可通过 `POETRY_BOOK_LATIN_FONT` 指定文件路径
- LaTeX 包：luatexja、TikZ、mdframed、fancyvrb、booktabs、tabularx

Python 依赖：

```bash
python3 -m pip install -r requirements.txt
```

Noto Serif SC 及其 SIL Open Font License 1.1 随包附带，无需注册到系统。它与思源宋体同源；单一中文字库对部分生僻字的覆盖少于原来的多字体组合，缺字时会停止并指出字符，不会使用 Last Resort 或 Unifont 凑字。

随包文件为本机 Noto Serif SC 2.02 版，字体内标注为 non-release；SHA-256 为 `a4aed9985a5916fbf6690456f8732a9fccd517938e353165d4142b4f11a39280`。字体来源与许可见 [Noto 项目](https://github.com/notofonts/noto-cjk)和 `assets/fonts/NotoSerifSC-OFL.txt`。

Anthropic Serif 不随仓库分发。请自行准备可使用的字体文件，将正体放在技能目录 `assets/fonts/AnthropicSerif-Regular.ttf` 或 `~/.local/share/ni-skill/fonts/AnthropicSerif-Regular.ttf`，也可设置 `POETRY_BOOK_LATIN_FONT` 指向正体文件；同目录存在 `AnthropicSerif-Italic.ttf` 时会用于斜体。放在技能目录的字体可以随技能文件一起离线复制。

### 安装为 Skill

从仓库根目录运行：

    cd skills/ni-poetry-book
    make install

默认安装到 ~/.agents/skills/ni-poetry-book/。也可以指定目录：

    python3 scripts/install.py --dest "/your/skill/directory/ni-poetry-book"

安装器会拒绝覆盖同名非 Poetry Book 目录或符号链接。升级时会清理与旧版随包文件完全一致的字体；改过的同名字体及其许可会保留并提示。

## 使用

### 结构化诗词或文集

```bash
python3 scripts/render_book.py \
  --input "/absolute/path/book.json" \
  --theme song-mist \
  --output "/absolute/path/new-output"
```

输入格式和字段说明见 [SKILL.md](SKILL.md) 与 `examples/book.json`。

### Markdown 技术文章

```bash
python3 scripts/render_article.py \
  --input "/absolute/path/article.md" \
  --theme celadon \
  --title "文章主标题" \
  --subtitle "文章副标题" \
  --author "作者或栏目名" \
  --seal "印章文字" \
  --output "/absolute/path/new-output"
```

常用参数：

- `--offline`：禁止联网，只复用来源清单中已有且校验一致的图片。
- `--assets-dir`：指定原稿副本、图片和规范化 JSON 的保存目录。
- `--require "必须出现的语句"`：增加关键内容检查，可重复使用。
- `--series`、`--edition`、`--date`、`--subject`：覆盖封面和 PDF 元数据。

输出目录必须为空或不存在，避免覆盖用户资料。输出包括正式 PDF、`build/`、`book.works`、`manifest.json`、`validation-report.json` 和 `preview/`。

## 运行测试

```bash
make test              # Python 单元测试
make examples          # 六套主题各生成一本李清照示例，逐套检查
make article-examples  # 离线生成技术夹具
make check             # 上述全部测试
```

上游案例记录：

- 22 项单元测试通过。
- 六个诗词示例均为 13 页、4 条作品，各通过 17 项检查。
- 代码、表格、引用和链接夹具为 5 页，通过 20 项检查。
- 缺字、溢出、文字越界和异常空白页均为 0。

## 范围与限制

- 不宣称任意格式都能不经读取和结构化直接成书。
- 不虚构系年、出处、注释或“绝对无遗漏”的收录结论。
- 当前不支持复杂 HTML、嵌套列表、数学公式、转义竖线表格等完整 Markdown 扩展。
- 简单表格要求列数一致；图片仅支持 PNG/JPEG，网络图片仅允许 HTTPS，单张上限 25MB。
- 新输出目录是默认安全策略；重建时请选择新目录，或由用户明确处理旧产物。

## 文档

- [Skill 完整说明](SKILL.md)
- [从苏轼书到 Poetry Book 的工作记录](docs/poetry-book-worklog.md)

## 目录

```text
assets/                 六套主题、共享 LaTeX、字体及许可
scripts/                构建、Markdown 解析、安装和 PDF 校验
examples/               李清照书稿、技术夹具
tests/                  单元测试
docs/                   工作记录、过程文章和真实样张图片
```

## 授权

- 项目代码采用 [MIT License](LICENSE)。
- 字体按 `assets/fonts/` 中各自的许可使用。
- 范文文字及原文配图仅用于功能演示，版权归原作者或来源方，不随代码 MIT 许可重新授权。
