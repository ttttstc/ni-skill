# Unknown 路由表

`ni-unknown-ladder` 只负责诊断和路由，不替代具体技能。

## 路由原则

- 如果用户环境中有专门 skill，推荐使用该 skill。
- 如果没有专门 skill，输出等价中文提示词。
- 不自动调用下一阶段。
- 由用户决定是否进入下一阶段。
- 推荐时必须说明下一阶段 AI 角色。

## 路由表

> 诊断可以多标签，行动必须单线程。当前轮只路由主 Unknown，次级 Unknown 进入后续队列。

| Unknown 阶段 | 推荐下一模式 | 下一阶段 AI 角色 | 可类比 skill / 能力 | 下一阶段目标 |
|---|---|---|---|---|
| 想法空白 | Blind Spot Pass / Idea Interview | 想法访谈官 + 盲点扫描器 + 第一版假设设计师 | Fable unknown discovery | 定义 idea，识别盲点 |
| 伪需求风险 | Office Hours / Framing Challenge | 产品访谈官 + 需求反方 + Framing Challenger | gstack `/office-hours` 风格 | 挑战 framing，挖真实 pain |
| 行动未知 | Brainstorming / MVP 切片 | 方案脑暴伙伴 + MVP 裁剪者 + 交付节奏设计师 | obra `/brainstorming` 风格 | 生成 2-3 个路径，选 MVP |
| 质量未知 | 多方案原型 | 质量标尺设计师 + 多方案原型伙伴 + 偏好发现教练 | prototype / visual companion 风格 | 建立质量标尺 |
| 表达未知 | Preference Profile | 偏好翻译器 + 风格约束整理员 + 反馈结构化教练 | memory / learn 风格 | 把偏好翻译成约束 |
| 决策未知 | Engineering Plan Review | 架构访谈官 + 关键决策过滤器 + Decision Log 记录员 | gstack `/plan-eng-review` 风格 | 锁定关键决策 |
| 计划风险 | Grill / Pre-mortem | 严厉方案评审 + Pre-mortem 主持人 + 反方架构顾问 | mattpocock `/grill-me` 风格 | 暴露隐含假设和失败路径 |
| 代码库未知 | Codebase Scan | 代码库导游 + 架构地形扫描器 + 最小安全修改顾问 | architecture scan 风格 | 画出代码库地形 |
| 实现偏移 | Deviation Log | 保守执行者 + 偏差记录员 + Scope 守门员 | implementation-notes 工作流 | 记录偏差，防止静默漂移 |
| 验收未知 | Review / QA / Quiz | 验收官 + QA 评审 + 变更讲解员 + 理解考官 | gstack `/review` `/qa` 风格 | 生成验收报告，确认理解 |

## 推荐话术

```markdown
如果你的环境里有对应 skill，可以进入「{skill 名称}」模式。
如果没有，直接复制下面的中文提示词给当前 AI 使用。
```
