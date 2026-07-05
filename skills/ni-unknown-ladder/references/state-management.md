# 状态管理规则

`ni-unknown-ladder` 默认不污染用户工程目录。

## 三层状态策略

### 1. 默认模式：无状态

默认不创建任何文件。只基于：

- 当前用户输入；
- 当前对话上下文；
- 用户显式提供的文档 / spec / notes；
- 当前可访问的代码库信息。

适合短任务、一次性诊断、文章写作、临时 vibe coding。

### 2. 全局用户态持久化：显式启用

当用户明确要求“保存状态”“跨会话保留状态”“下次继续”时，建议写到用户全局目录，而不是工程目录：

```text
~/.claude/ni-unknown-ladder/projects/{project-id}/state.md
```

`{project-id}` 建议基于以下信息生成：

- 有 git 仓库：`hash(git remote url + repo root path)`
- 无 git 仓库：`hash(current working directory path)`

推荐只保留：

```text
state.md          # 当前 unknown 状态
latest-output.md  # 最近一次诊断输出，可选
```

### 3. 项目内状态：必须显式 opt-in

只有当用户明确要求“团队共享”“写入项目”“沉淀到当前工程”时，才允许写项目目录。

推荐路径：

```text
.ai/ni-unknown-ladder/state.md
```

写入项目目录前必须征得用户确认，并提示可加入 `.gitignore`：

```gitignore
.ai/ni-unknown-ladder/
```

## 状态文件内容

状态文件只保存诊断必要信息，不保存完整聊天记录、不保存敏感内容、不保存大段代码。

建议格式：

```markdown
# ni-unknown-ladder 状态

## 当前任务
{一句话描述当前任务}

## 已确认事实
- ...

## 已解决 Unknown
- 伪需求风险：已解决。真实 pain 是 ...

## 待处理 Unknown 队列
1. 行动未知：...
2. 决策未知：...

## 当前主 Unknown
{当前最阻塞 unknown}

## 上一次推荐模式
{例如：关键决策访谈}

## 上一次停止条件
{满足什么条件后进入下一阶段}

## 最近更新时间
{时间}
```

## 硬规则

- 默认不写文件。
- 写全局状态前，需要用户明确表达保存意图。
- 写项目内状态前，必须明确征得用户确认。
- 不把状态文件作为完整知识库。
- 不保存完整对话、隐私信息、密钥、业务敏感内容、大段代码。
- 状态只作为重新诊断的辅助输入，不替代当前上下文判断。
