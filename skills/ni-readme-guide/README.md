# ni-readme-guide

中文 | [English](./README.en.md)

为 GitHub 仓库创建或重构双语 README：`README.md` 使用简体中文并作为默认入口，`README.en.md` 提供英文版本，两份文件保持结构、事实、命令和链接同步。

## 适用场景

- 从仓库代码、配置、示例和真实输出整理 README
- 重构首屏叙事、快速开始、功能说明、架构和贡献指南
- 设计项目原生的 SVG、截图、流程图或其他 README 视觉素材
- 审计双语一致性、断链、图片引用和 GitHub 渲染安全性

## 输出约定

每次创建或修改 README 文案，都交付：

```text
README.md
README.en.md
```

两份文件顶部互相跳转：

```markdown
中文 | [English](./README.en.md)
[中文](./README.md) | English
```

不编造功能、数据、兼容性、用户量或项目证明。优先展示真实输出和最短可运行路径；命令、版本、链接和代码在两种语言中保持一致。

## 使用

```text
Use $ni-readme-guide to rewrite this repository README.
Deliver README.md in Chinese and README.en.md in English with reciprocal language links.
```

审计现有双语 README：

```bash
python scripts/audit_readme.py /path/to/repository
```

脚本检查文件配对、双向语言链接、标题层级、代码块、链接和图片目标、HTML alt 文本及基础 SVG 安全性。

## 资源

- [SKILL.md](./SKILL.md)：完整工作流与质量标准
- [references/bilingual-delivery.md](./references/bilingual-delivery.md)：双语交付规则
- [references/growth-readme-patterns.md](./references/growth-readme-patterns.md)：证据驱动的 README 结构
- [scripts/audit_readme.py](./scripts/audit_readme.py)：本地双语审计

本 skill 基于 [oil-oil/beautify-github-readme](https://github.com/oil-oil/beautify-github-readme)，上游许可证见 [LICENSE.upstream](./LICENSE.upstream)。
