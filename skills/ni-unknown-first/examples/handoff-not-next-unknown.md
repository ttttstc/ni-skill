# 示例：继续不推进到下一个 Unknown

## 错误理解

```text
用户回复“继续”后，系统开始处理后续 Unknown 队列中的“行动未知”。
```

这是错误的。

## 正确理解

```text
用户回复“继续”后，系统进入上一轮推荐处理模式，继续处理当前主 Unknown。
```

## 何时推进 Unknown 队列

只有用户再次运行：

```text
/ni-unknown-first
```

并且当前主 Unknown 满足关闭条件，才可以把后续 Unknown 提升为新的主 Unknown。
