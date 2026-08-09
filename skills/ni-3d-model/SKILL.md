---
name: ni-3d-model
description: |
  将用户给出的主题、对象或参考资产转成经过人工审核的多视图图片和可交付 GLB 3D 模型。用于“按主题做 3D 模型”“先出多视图再生成 GLB”“用混元 3D / Tripo 做模型”“把参考图变成带纹理的 GLB”“生成可放进项目的 3D 资产”等请求。流程强制包含两个人工门禁：出图前确认需求，出图后确认视觉与结构；未经当前门禁的明确确认，不得生成图片、上传 3D 服务、消耗额度或交付模型。支持参考模型风格对齐、多视图一致性、免费额度生成、GLB 下载、压缩、结构/材质/实际渲染验收。
---

# ni-3d-model

把一个主题变成可验证的 GLB。坚持“先确认，再出图；先审图，再建模”。

## 不可绕过的规则

1. 把用户确认当作流程输入，不把沉默、旧版本确认或模糊好评当作确认。
2. 在需求确认前，只允许读取和分析参考资料；禁止调用图像生成能力。
3. 在图片审核通过前，禁止上传 Hunyuan、Tripo 或其他 3D 服务，禁止提交任务和消耗额度。
4. 用户改变主题、关键结构、风格或视图后，使对应确认失效并退回最近门禁。
5. 只使用用户允许的免费额度；禁止购买、充值或自动启用付费方案。
6. 不把网页预览当作成功。必须下载 GLB，并完成文件级和实际渲染验收。
7. 保留源资产与被拒版本。不要用新文件覆盖原始 GLB 或已审核图片。

## 工作目录

用户未指定目录时，在当前工作区创建：

```text
3d-models/{model-slug}/
├── requirements.md
├── references/
├── review/
│   └── v001/
│       ├── turntable-review.png
│       ├── front.png
│       ├── left.png
│       ├── right.png
│       └── back.png
├── models/
│   ├── sources/
│   │   └── generation-v001-source.glb
│   └── {model-slug}.glb
└── qa/
    ├── inspection.md
    └── renders/
```

使用小写 kebab-case 命名。递增 `v001`、`v002`；不要覆盖被拒图。

## 阶段 1：澄清并锁定需求

先读取用户给出的图片、GLB、项目页面或说明。需要对齐现有模型时，实际渲染或检查参考资产，不凭文件名猜风格。

完整读取 `references/intake-and-image-review.md`，用其中的最小问题集补齐会改变结果的信息。一次只问 1–3 个最关键问题，已有答案不要重复问；持续澄清到对目标、范围、约束和验收标准至少有 95% 把握。

至少锁定：

- 主题与主体边界；单个物体还是组合结构
- 使用场景与观看距离
- 风格锚点、颜色、材质、灯光表现
- 必须出现、禁止出现、数量和朝向等结构约束
- 外观完整体、剖面、爆炸图或透明结构
- 目标面数、纹理、文件大小、坐标/原点等交付约束
- 输出目录和文件名
- 目标 3D 服务及其当前多视图槽位协议
- 指定或允许的图像生成器、图片尝试次数与费用上限
- 允许使用的 3D 服务及免费额度范围

把结论写入 `requirements.md`，向用户展示精简的“需求确认单”，明确说：

> 请回复“确认”，或指出需要修改的字段。确认前我不会生成图片。

只有用户针对当前确认单明确回复“确认”“通过”“按这版执行”或语义等价内容，才进入阶段 2。

## 阶段 2：生成可审核的多视图图片

用户明确指定图像生成器时，优先使用该工具。指定工具不可用时停止，说明原因并让用户批准替代方案；不要静默切换供应商、数据处理方式或额度。用户未指定时，依次选择原生图像生成工具、已安装的图像生成 skill/tool，并记录运行时实际报告的工具、模型和模式；不要假设不存在的模型模式。没有可用能力时停止，明确说明缺少什么；不要伪造产物。

生成一套“审核包”，而不是互不相关的漂亮单图：

- 同一个对象、同一几何身份、同一比例和材质
- 严格遵守确认单中的目标服务槽位协议，不使用跨服务的通用斜视图默认值
- 中性纯色背景，无台座、文字、水印、边框或遮挡主体的阴影
- 相同正交感、相同相机高度、相同照明与色彩管理
- 满足 `requirements.md` 的数量、左右、朝向、剖面和禁用结构
- 优先一次生成 2×2 转台审核图并裁成四张；若工具不能稳定做到，则用同一锚点图派生各视图

先做自检：身份是否漂移、左右是否镜像错置、数量是否重复、背面是否只是正面翻转、结构是否跨视图消失。发现明显失败时标记为 rejected；仅在确认单的图片尝试预算内生成新版本并递增 `image_attempts_used`。达到上限后停止，展示失败版本与原因，重新询问用户。

把审核图保存到版本目录，在回复中直接展示绝对路径图片，并列出 3–5 个需要用户重点看的结构。明确说：

> 请回复“图片通过”，或按“保留项 / 修改项”反馈。图片通过前我不会生成 GLB。

只有用户针对当前图片版本明确批准，才进入阶段 3。任何新生成或实质修改后的多视图都必须重新审核；单纯无损裁切、改名或格式转换不需要重审。

## 阶段 3：准备 3D 输入

确认四张上传图来自已批准版本，并核对目标服务协议。Hunyuan 的 `front/left/right/back` 协议示例：

```text
front.png     -> 正图
left.png      -> 真实左侧图
right.png     -> 真实右侧图
back.png      -> 背图
```

若服务槽位定义与确认单不同，先更新需求版本并重新生成、审核图片。禁止把斜视图、左右对象、镜像图、顶视图或底视图冒充左右槽位。

完整读取 `references/glb-production-and-qa.md`，再操作外部 3D 服务。

## 阶段 4：生成并下载 GLB

优先使用用户指定服务；未指定时，选择当前可用、支持多图和纹理 GLB 的服务。Hunyuan 可用时优先走多图模式，Tripo 或其他服务作为明确降级项。

执行时：

1. 读取页面当前登录、额度、模型版本、面数和纹理选项。
2. 登录、验证码或本地文件权限需要用户操作时，请用户接手；不要索取账号、密码或验证码。
3. 核对四个槽位和缩略图后再提交。
4. 选择带纹理的最高质量免费模式；面数服从确认单，不盲目固定某个旧版本或旧档位。
5. 点击提交前，先递增 `generation_version`，原子记录 `provider`、`submission_status: submitting`、`job_id: null`、`credits_before` 和当前输入图片版本。
6. 提交成功后立即记录 `submission_status: submitted`、可见的 `job_id` 或任务 URL、`submitted_at` 和提交后额度；断线时先用这些字段查任务，禁止盲目重提。
7. 等待完成，更新状态并旋转查看正面、背面、左右侧和上下边缘。
8. 下载到 `models/sources/generation-{generation_version}-source.glb`，记录服务版本、参数和额度变化。每次生成使用独立源文件。

## 阶段 5：验收与交付

按 `references/glb-production-and-qa.md` 完成：

- 文件可解析，扩展和缓冲区有效
- 网格、节点、材质、纹理数量符合预期
- 无重复主体、镜像残片、破面、悬浮碎片或错误数量
- 朝向、比例、中心和原点适合目标项目
- Base Color、Normal、Metallic/Roughness 等所需材质存在
- 在真实查看器中加载并从至少四个角度截图
- 与已批准图片逐项对照结构、色彩和轮廓

目标文件超限时，保留对应的版本化源 GLB，另产出压缩候选。优先压缩几何编码和纹理；除非用户批准，不减面、不降 Base Color 分辨率。压缩后重新做结构验证和 A/B 渲染。

只有全部硬性检查通过，才把候选复制或命名为 `models/{model-slug}.glb`。不合格时保留产物、标记失败原因并回到图片或生成阶段，不要把它描述成完成。

## 最终交付

用简短清单报告：

- 已批准图片版本与路径
- 源 GLB、最终 GLB 的绝对路径和大小
- 服务、模型版本、参数和实际额度消耗
- 三角面/顶点、纹理与材质摘要
- 结构检查、glTF 验证和真实渲染结果
- 已知限制或降级

直接展示最终多视图图或 QA 渲染图。只有用户明确要求接入现有应用时，才修改应用注册表、页面或业务代码。

## 阶段状态

在 `requirements.md` 顶部维护一个状态：

```yaml
phase: intake | requirements-approved | image-review | image-approved | glb-generation | glb-qa | done | blocked
requirements_version: v001
requirements_approved: false
view_protocol: null
image_generator: null
image_attempt_budget: null
image_attempts_used: 0
image_version: null
image_approved: false
generation_version: null
provider: null
submission_status: not-submitted | submitting | submitted | completed | downloaded | failed | unknown
job_id: null
credits_before: null
credits_after: null
submitted_at: null
source_file: null
```

按以下规则原子更新状态：

- 需求改变：递增 `requirements_version`，清空两级批准、图片版本和全部外部提交字段，回到 `intake`。
- 生成新图：递增 `image_version` 与 `image_attempts_used`，设置 `image_approved: false`，清空全部外部提交字段，回到 `image-review`。
- 外部提交：先创建新的 `generation_version` 与提交身份，再点击生成；旧任务身份不得复用于新版本。

中断后从文件恢复，不重做已完成阶段。确认只对文件中记录的当前版本有效；`submitting`、`submitted` 或 `unknown` 状态必须先查任务历史与额度，禁止直接再次提交。
