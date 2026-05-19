# ni-skill 套件整体实现计划

**依据**：DESIGN.md v1.0 + SPEC.md v2.0 + 用户决策（2026-05-19）
**日期**：2026-05-19
**状态**：待评审

---

## 0. 现状与目标

**现状**
- `ni-writer/` 已存在且完整（套件基因标杆，不重写）
- `DESIGN.md` / `SPEC.md` 已定稿
- Python 3.12.13 可用

**目标**：先逐个交付可独立运行的原子 skill，全部单点能力就绪后再做编排层。

---

## 1. 三条用户决策（覆盖 DESIGN.md 原方案）

| # | 决策 | 对计划的影响 |
|---|------|------------|
| 1 | 先做各 skill 单点能力、支持独立运行，编排层最后做 | 里程碑重排：原子 skill 在前（S1-S6），`ni-article-workflow` 移到最后（S7） |
| 2 | 封面图先占位，用户自己在草稿箱编辑 | ni-draft 不再强制 `cover_media_id`；草稿创建后用户自行设封面 |
| 3 | 各 skill 不强依赖 ni-writer，只保持基因风格一致 | G1-G5 基因**内嵌**进每个 SKILL.md（不引用 ni-writer 文件）；ni-inspect **自带**禁用词黑名单副本 |
| 4 | 不走 CCG，全部由 Claude Code 直接完成 | 所有 SKILL.md / references / Python 脚本均 Claude 直接撰写，不委托 Coder/Codex |

---

## 2. 贯穿约束

- **基因内嵌**：G1 真实优先 / G2 独特角度门槛 / G3 活人在场 / G4 四层自检骨架 / G5 降级而不放弃——每个 SKILL.md 自带这 5 条，不 `@import` ni-writer。
- **独立可运行**：每个原子 skill 单独调用时，输入靠「用户粘贴 / 用户给文件路径」，输出落到用户指定或默认路径，**不硬编码 workflow 的 `drafts/` 约定**。workflow 后续通过传参注入路径即可复用。
- 每个 SKILL.md 写完用 G1-G5 逐条自查。

---

## 3. 里程碑分解（原子 skill 优先，编排最后）

### S1 — ni-insight（灵魂 ⭐ 最高价值，最早验证 prompt）✅ 已完成

- [x] `ni-insight/SKILL.md` — 角度发现→用户碰撞→灵魂锁定三轮流程；强制用户选定角度才输出；G3 对话腔；基因 G1-G5 内嵌
- [x] `references/angle-discovery.md` — 5 种角度类型（反转/升维/利己/类比/时间）详解 + 案例
- [x] `references/question-templates.md` — 三个反直觉提问模板话术 + 变体
- **独立运行**：用户粘贴调研素材或给 research.md 路径 → 产出 insight.md
- **验收**：核心论点 10-20 字、用户选择有记录、支撑逻辑≥3、预判反驳≥1、通过朋友圈测试。用 3 个真实选题做 A/B 调优（留待真实使用时迭代 prompt）

### S2 — ni-formatter（穿衣，5 模块最小集）✅ 已完成

- [x] `ni-formatter/SKILL.md` — 选模块决策算法、5 模块上限规则、G1 不堆模块；基因内嵌
- [x] `references/layout-modules.md` — part/callout/quote/steps/verdict 完整转译 prompt + 正反例
- [x] `references/module-decision.md` — 决策算法 + 文章类型映射表（6 原型 × 5 模块）
- **独立运行**：用户给 article.md（或粘贴文章）+ 可选核心论点 → 产出 formatted.md
- **验收**：模块语法合法、verdict 必存在且=1；去掉 `:::xxx` 注释文章仍可读

### S3 — ni-draft（发布，Python 内嵌，封面占位）✅ 已完成

- [x] `ni-draft/SKILL.md` — G3 错误转人话、G5 失败降级本地 HTML；基因内嵌
- [x] `references/wechat-api.md` — 错误码表、API 端点、配置示例
- [x] `references/html-style-guide.md` — 5 模块内联 CSS 规范
- [x] `scripts/token_cache.py` — access_token 文件缓存（sidecar 锁文件，跨平台；TTL 留 200s buffer）
- [x] `scripts/md_to_wechat_html.py` — markdown→内联 CSS HTML + 5 模块渲染
- [x] `scripts/wechat_draft.py` — CLI 入口 + 主流程（create 子命令）
- [x] `requirements.txt` — requests / markdown / pyyaml
- [x] `tests/fixtures/` — sample-article.md / expected-html.html / mock-wechat-response.json
- [x] `tests/smoke_test.py` — 离线冒烟测试（成功/40001/45004/缺封面四分支）
- **封面处理**：`--cover-media-id` 可选；缺省草稿建好后用户自行设封面。微信强制 `thumb_media_id` 时降级给占位 media_id 指引
- **验收结果**：md→HTML 转换 5 模块全对、与基准一致 ✓；3 脚本编译通过 ✓；CLI 解析正常 ✓；4 个错误码分支冒烟测试全过 ✓。真实推送待用户在自己公众号验证
- **备注**：参考了 `md2wechat-skill`（Go 项目）的微信 API 错误码与接口形态校准实现；Python 内嵌、零二进制依赖

### S4 — ni-research（调研）✅ 已完成

- [x] `ni-research/SKILL.md` — 热点分析、竞品二分扫描、素材具名；G5 WebSearch 降级；基因内嵌
- [x] `references/topic-analysis.md` — 热点判断标准 + 写作时机决策树 + 素材质量分级 + 竞品扫描策略
- **独立运行**：用户给选题关键词 → 产出 research.md
- **验收**：素材≥5、具名率≥60%、竞品≥3、角度≥3

### S5 — ni-inspect（预检，自带禁用词表）✅ 已完成

- [x] `ni-inspect/SKILL.md` — Metadata/内容质量/结构三组检查、BLOCKED/WARNING/INFO 分级；基因内嵌
- [x] `references/check-rules.md` — 各项阈值 + 分级规则 + **自带的禁用词黑名单副本**（文件头标注「源自 ni-writer，手动同步」）
- **独立运行**：用户给 formatted.md → 产出 inspect-report.md（含 readiness 字段）
- **验收**：检查项不漏检、问题定位到段落/句子、修复建议可操作

### S6 — ni-article-image-gen（配图 prompt，P1）✅ 已完成

- [x] `ni-article-image-gen/SKILL.md` — 风格默认黏土定格动画（可按用户输入切换），每篇 1 封面 + 9 内文，实体锚定；基因内嵌
- [x] `references/visual-prompts.md` — 默认黏土风格块 + 其他风格的风格块结构 + 6 种构图类型模板 + 封面 3 构思方向 + 9 图分布 + 实体锚定正反例
- **优化记录（2026-05-19）**：①输出从「封面 3 组 + 内文 3-6 张」改为「封面 1 张 + 内文固定 9 张」；②风格默认黏土定格动画，用户可指定其他风格，整篇 10 图风格统一
- **独立运行**：用户给 article.md（+ 可选 insight）→ 产出 cover-prompts.md / inline-prompts.md
- **验收**：封面 3 组差异化、每条 prompt ≥2 个文章实体

### S7 — ni-article-workflow（编排层，最后做）✅ 已完成

- [x] `ni-article-workflow/SKILL.md` — 纯编排：状态机、article-name 校验、阶段映射、降级、断点续跑
- [x] `references/state-schema.md` — state.yaml schema + `drafts/{article-name}/` 目录布局 + 接口契约
- [x] `drafts/` 加入 `.gitignore`（同时忽略 Python 运行产物）
- [x] ni-writer 接口适配：写进 SKILL.md + state-schema.md 的适配契约——workflow 把 insight 核心论点作「独特视角」注入、跳过 ni-writer 第二步；**不改 ni-writer/SKILL.md**
- [x] 端到端编排：S1-S6 六 skill + ni-writer 接入状态机，阶段映射表完整
- **验收**：编排层结构完整、阶段映射对齐 7 个 skill ✓；真实选题 init→done 跑通需用户提供微信凭证后实测

---

## 4. 依赖与风险

| 项 | 说明 / 对策 |
|----|-----------|
| 微信 API 凭证 | S3 真实推送需用户提供 WECHAT_APPID/SECRET；离线测试不依赖，可先做 |
| 微信 thumb_media_id 是否强制 | S3 实现时先验空封面能否建草稿；不行则退化为一次性占位 media_id |
| ni-insight prompt 效果 | S1 用 3 个真实选题 A/B 调优至通过朋友圈测试 |
| 基因副本与 ni-writer 漂移 | 禁用词表等副本在文件头标注「源自 ni-writer，手动同步」 |

---

## 5. 交付顺序

S1 → S2 → S3 → S4 → S5 → S6 → S7。每个 skill 独立验收通过后再进下一个；任一不过就地返工。

---

## 评审区（实现完成）

**完成日期**：2026-05-19
**状态**：S1-S7 全部交付，套件结构完整。

### 交付清单（28 个新文件）

| Skill | 文件 |
|-------|------|
| ni-insight (S1) | SKILL.md + references/angle-discovery.md + question-templates.md |
| ni-formatter (S2) | SKILL.md + references/layout-modules.md + module-decision.md |
| ni-draft (S3) | SKILL.md + requirements.txt + references×2 + scripts×3 + tests/(fixtures×3 + smoke_test.py) |
| ni-research (S4) | SKILL.md + references/topic-analysis.md |
| ni-inspect (S5) | SKILL.md + references/check-rules.md（自带禁用词黑名单副本） |
| ni-article-image-gen (S6) | SKILL.md + references/visual-prompts.md |
| ni-article-workflow (S7) | SKILL.md + references/state-schema.md |
| 套件 | .gitignore 更新（drafts/ + Python 产物） |

### 验收结果

- **ni-draft 可执行验证全过**：md→HTML 5 模块渲染正确、与基准快照一致；3 脚本编译通过；CLI 解析正常；4 个错误码分支（成功/40001/45004/缺封面）冒烟测试通过。
- **6 个 markdown skill 结构完整**：G1-G5 基因内嵌、独立运行接口清晰、L1-L4 验收 + G5 降级齐全。
- **编排层阶段映射对齐 7 个 skill**，ni-writer 适配走传参契约、未改其 SKILL.md。

### 三条用户决策落实

1. 原子 skill 优先、独立可运行，编排层最后做 ✓
2. ni-draft 封面占位（`--cover-media-id` 可选）✓
3. 各 skill 不依赖 ni-writer，基因内嵌、ni-inspect 自带禁用词副本 ✓

### 待用户实测项

- ni-draft 真实推送：需用户提供 `WECHAT_APPID`/`SECRET`，在自己公众号验证。
- ni-insight prompt：用 3 个真实选题 A/B 调优至通过朋友圈测试。
- workflow 端到端 init→done：需微信凭证后真实选题跑通。
