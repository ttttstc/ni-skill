# Agent 可读性评级标准(L0–L3)

评的是单个符号(函数 / 组件 / 类 / 类型 / 接口)。问题始终是同一个:

> **一个没有隐性经验、只能读字面的 Agent,拿到这个符号,能不能用对?**

## L0 失明

只有类型签名,零文档(或只有自动生成的、无信息量的注释)。

```ts
export declare function PieChart(props: PieChartProps): JSX.Element;
```

Agent 只知道「有这么个东西、签名长这样」。它会调,但不知道:什么时候该用、什么时候不该用、有没有更合适的替代。**高频 L0 是审计里最危险的一类。**

## L1 命名可读

有名字 + 类型,顶多一句话描述「是什么」。

```ts
/** A pie chart component. */
export declare function PieChart(props: PieChartProps): JSX.Element;
```

比 L0 强在 Agent 能从名字 + 一句话猜出大致用途。但「a pie chart component」几乎没有信息量——Agent 还是不知道边界。命名清晰本身是 L1 的底线:`PieChart` 比 `Chart2` 可读。

## L2 用途明确

写清「做什么」和「典型场景」。

```ts
/**
 * Pie or donut chart for part-of-whole breakdowns.
 * Use for small slice counts, such as request share by region.
 */
export declare function PieChart(props: PieChartProps): JSX.Element;
```

Agent 现在知道何时**该考虑**它(要表达占比时)。但还缺一半:它不知道何时**不该**用——遇到趋势数据,Agent 仍可能错用 PieChart。

## L3 边界完整

L2 + 反向边界(不适合什么)+ 替代指引(那种情况改用谁)+ 至少一个 `@example`。

```ts
/**
 * Pie or donut chart for part-of-whole breakdowns.
 *
 * Use for small slice counts, such as request share by region.
 * Do NOT use for time series or precise ranking — use LineChart
 * or BarChart instead.
 *
 * @example
 * <PieChart donut data={[{ label: "Free", value: 320 }]} />
 */
export declare function PieChart(props: PieChartProps): JSX.Element;
```

这是终点态。Agent 知道:何时用、何时不用、不用时改用谁、长什么样。判 L3 要四样都有:

- ✅ 用途
- ✅ 反向边界(「不适合 X」/「不要用于 X」)
- ✅ 替代指引(「改用 Y」)
- ✅ ≥1 个可直接抄的 `@example`

缺任意一样,降到 L2。

## 评级要点

- **审「字面」,不审「言下之意」。** 「这个函数处理用户数据」对人能脑补,对 Agent 等于没说。要具体到场景。
- **反例比正例值钱。** L2 → L3 的关键跳跃是「不该用什么」。Agent 最常见的错误不是不会用,而是用在错的地方。
- **`@example` 要能直接抄。** 一个真实、可运行的调用示例,比三段文字描述更能约束 Agent 的输出。
- **类型本身也是文档。** `tone: "warning" | "danger"` 比 `tone: string` 可读得多——枚举型签名能给可读性加分。
- **存疑就标存疑。** 一个符号是不是 agent-facing(会被 Agent 直接调)有时不清楚。不确定就在报告里标出,让用户定,不硬塞进评级。
