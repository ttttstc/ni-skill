# 首层架构方法论

## 1. 第一性原则

按以下顺序推导，不从架构风格或技术产品开始：

1. 谁遇到什么问题；
2. 解决它产生什么价值；
3. 哪些事实不可改变；
4. 哪些约束相互冲突；
5. 什么结果算成功；
6. 哪些决定错误后代价最大；
7. 能否通过隔离、演进或延迟决定降低代价；
8. 满足以上条件的最小结构是什么。

技术栈、模式和组件只能是推导结果，不能是起点。

## 2. 从文章观点到执行动作

用户提供的《架构师和高级软件开发工程师的主要区别》强调六个转变。将其转成动作：

| 观点 | 执行动作 |
|---|---|
| 如何实现变为如何权衡 | 先定义驱动力、约束和评价标准，再讨论实现 |
| 局部最优变为全局有序 | 同时检查系统、业务、数据、信任和团队边界 |
| 被动实现变为主动定义 | 把模糊要求转为性能、可靠性、安全等可测基线 |
| 实现当下变为定义未来 | 写出演进路径、可逆性和复审触发条件 |
| 决策代价扩大 | 优先处理高爆炸半径、跨边界和难逆决定 |
| 技术沟通变为横向领导 | 用统一决策格式公开收益、代价、所有权和承诺 |

文章是职业视角来源，不把其中举例直接当成具体项目规则。

## 3. 架构驱动力

从业务目标、硬约束和隐含运营要求中提取候选驱动力，再裁剪为 3–5 个。

质量属性不得只写“高性能”“高可用”。使用轻量场景：

```text
当 {来源} 在 {运行环境} 触发 {事件/压力}，
系统中的 {对象} 应产生 {响应}，
并达到 {可测标准}。
```

示例：

```text
促销峰值期间，当每秒 2,000 个订单提交到达时，
订单入口应在不重复创建订单的前提下接收请求，
95% 响应低于 300ms，积压在 10 分钟内清空。
```

无法确定指标时写 `待确认`，并判断它是否阻塞结构选择。不要编造数字。

## 4. 核心能力与边界

依次识别：

- 核心业务能力：直接产生差异化价值，优先投入架构注意力；
- 支撑能力：服务核心业务，但不是差异化来源；
- 通用能力：优先复用、购买或采用成熟平台；
- 业务语义边界：术语、规则和模型在何处保持一致；
- 数据所有权：谁是唯一权威写入方，其他边界如何获取数据；
- 信任边界：身份、权限、敏感数据和外部输入在哪里跨界；
- 运行边界：独立部署、故障隔离和扩缩容是否真的必要；
- 团队边界：是否存在一个团队能端到端拥有该能力。

Bounded Context 不等于微服务。业务语义边界可以先落在模块化单体中。

## 5. 决策时机

将候选事项分成三类：

### 现在决定

阻塞近期交付，或涉及合规、安全、关键数据、外部长期契约、不可逆迁移。

### 现在只定边界

方向和责任必须清楚，但具体协议、产品或内部实现可以等待更多信息。

### 明确延迟

决策可逆、当前信息不足、等待会显著增加信息，且延迟不阻塞交付。

延迟不是遗漏。记录负责人、需要的信息和触发决定的条件。

## 6. 取舍分析

每个高价值决策回答：

- 它服务哪几个驱动力；
- 它牺牲什么；
- 最差的一面是什么；
- 错误选择的爆炸半径；
- 未来替换成本；
- 什么变化会触发复审。

重点寻找：

- 风险点：关键结果依赖未验证假设；
- 敏感点：小变化会显著改变结果；
- 取舍点：改善一个属性会损害另一个属性。

## 7. 现实承载能力

检查方案是否超过：

- 团队数量和经验；
- 可承担的认知负载；
- 发布、监控、故障响应和安全能力；
- 可接受的交接次数；
- 时间和预算。

平台能力只有在能降低多个交付团队的非差异化负担时才提出，并保持最薄可用范围。

## 8. 方法适用边界

- C4 表达结构，不生成决策，也不替代动态流和领域模型。
- DDD 帮助发现语义边界，不要求独立进程。
- ADR 记录已做决定，不把 Unknown 伪装成决定。
- 完整 ATAM 适合高风险、多利益相关方评估；首层方案只使用驱动力、场景、风险和取舍骨架。
- Wardley Mapping 适合价值链、成熟度和 build/buy，不负责组件与可靠性设计。
- 可选性有成本，只为高影响、高不确定且未来改变昂贵的事项购买。

## 一手来源

- Martin Fowler, [Software Architecture Guide](https://martinfowler.com/architecture/)
- Martin Fowler, [Who Needs an Architect?](https://martinfowler.com/ieeeSoftware/whoNeedsArchitect.pdf)
- Gregor Hohpe, [Architecture: Selling Options](https://architectelevator.com/architecture/architecture-options/)
- SEI, [Quality Attribute Workshops, Third Edition](https://www.sei.cmu.edu/library/quality-attribute-workshops-qaws-third-edition/)
- SEI, [ATAM: Method for Architecture Evaluation](https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf)
- Eric Evans, [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/reference/)
- Simon Brown, [C4 Model](https://c4model.com/introduction)
- Michael Nygard, [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- Team Topologies, [Key Concepts](https://teamtopologies.com/key-concepts)
