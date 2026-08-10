# GLB 生成与质量验收

只在当前图片版本已获用户明确批准后读取和执行。

## 目录

- [服务选择](#服务选择)
- [浏览器与账号边界](#浏览器与账号边界)
- [上传前检查](#上传前检查)
- [可恢复提交日志](#可恢复提交日志)
- [生成结果的视觉检查](#生成结果的视觉检查)
- [下载与溯源](#下载与溯源)
- [文件级检查](#文件级检查)
- [真实渲染检查](#真实渲染检查)
- [压缩策略](#压缩策略)
- [通过标准](#通过标准)

## 服务选择

按以下顺序决定：

1. 使用用户明确指定的服务。
2. 未指定时，优先使用当前可用、支持多图输入、彩色纹理和 GLB 下载的免费服务。
3. Hunyuan 支持当前任务时优先使用多图模式；Tripo 或其他服务只能作为显式降级方案。
4. 页面版本、模型名、额度和参数会变化。读取当前 UI，不依赖历史按钮名称或旧默认值。
5. 免费额度不足、需要付费或条款不明确时停止并询问用户。

## 浏览器与账号边界

- 优先使用当前运行时已安装的浏览器控制能力。
- 复用用户已登录的浏览器会话，不读取或回显凭证。
- 遇到登录、验证码、扫码或扩展本地文件权限时，请用户在浏览器中完成。
- 上传失败时先判断：文件权限、文件选择事件、弹窗遮挡、站点自定义控件、会话断开。
- 自动上传不可用时，给出每个槽位的绝对文件路径和精确映射，让用户只接手上传；用户完成后继续其余步骤。
- 提交失败或连接断开后，先查看任务历史与额度变化，确认没有已提交任务，再重试。

## 上传前检查

逐项核对：

- 图片版本等于 `requirements.md.image_version`
- `image_approved: true`
- 槽位映射等于 `requirements.md.view_protocol`
- 四个文件可打开，尺寸和色彩模式正常
- 槽位映射与页面当前定义一致
- 四张图是同一对象，未混入镜像、另一侧对象或旧版本
- 模型模式会生成纹理，不是纯白模或仅几何
- 面数、质量和额度与确认单一致

在点击“生成”前，把槽位缩略图和关键参数再核对一次。图片确认已经授权当前确认单内的免费额度；如果实际额度、服务或参数超出确认单，重新询问。

## 可恢复提交日志

每次提交使用新的 `generation_version`。点击生成前，把以下字段一次写入 `requirements.md`：

```yaml
generation_version: v001
provider: hunyuan
submission_status: submitting
job_id: null
credits_before: 20
credits_after: null
submitted_at: null
input_image_version: v001
source_file: null
```

提交被站点接受后，立即写入 `submission_status: submitted`、任务 ID 或任务 URL、`submitted_at` 和可见的 `credits_after`。完成、下载、失败分别更新为 `completed`、`downloaded`、`failed`。无法判断是否提交成功时设为 `unknown`。

恢复时只要状态为 `submitting`、`submitted` 或 `unknown`，必须先按任务 ID/URL、任务历史、提交时间和额度变化查重。确认不存在任务后才能创建新的 `generation_version`；不得复用旧版本或直接重试。

## 生成结果的视觉检查

不要只看首屏。旋转检查至少：

- 正面与背面
- 左右两侧
- 顶部与底部边缘
- 剖面、孔洞、细长结构和连接处

检查重复主体、镜像残片、多余附肢、悬浮碎片、孔洞、塌陷、拉丝、粘连、错误数量、错误左右关系和材质断裂。任一硬性结构错误都判为失败，不能靠灯光掩盖。

## 下载与溯源

把站点原始下载保存为 `models/sources/generation-{generation_version}-source.glb`，并在 `qa/inspection.md` 记录：

```yaml
provider:
generation_version:
submission_status:
job_id:
model_version:
input_image_version:
quality_or_polygon_setting:
texture_setting:
free_credits_before:
free_credits_after:
generated_at:
source_file:
```

不要把浏览器下载目录里的临时文件直接当最终文件。

## 文件级检查

使用环境已有的 glTF/GLB 检查工具；优先官方 Khronos Validator 或 glTF-Transform。记录工具与版本。至少验证：

- GLB 可解析，validator 无 error
- scene、node、mesh、primitive、material、texture、image 数量
- 顶点与三角面数量
- 图片尺寸、编码和色彩用途
- 所需扩展是否被目标查看器支持
- 文件大小和 MIME/扩展名正确

validator warning 逐条判断。不要把 warning 宣称为 error，也不要省略会影响目标运行时的 warning。

## 真实渲染检查

用目标项目查看器优先；没有目标项目时，用本地 glTF 查看器。使用与交付环境相同的解码器和色彩空间。

保存至少四个方向的截图到 `qa/renders/`，并与批准图片对照：

- 主轮廓和比例
- 数量、左右和结构位置
- Base Color
- 粗糙度与金属度
- 法线细节
- 透明、双面或背面剔除问题
- 原点、地面接触和初始朝向

网页“看起来有颜色”不等于 GLB 包含完整纹理；必须检查文件材质和贴图。网页环境灯通常不会自动成为 GLB 内容；按确认单区分外部查看器灯光、烘焙光照和 `KHR_lights_punctual` 等模型内灯光，不要混为一谈。

## 压缩策略

只有文件超过确认单限制或用户要求时压缩。始终保留当前 `generation_version` 对应的源 GLB，输出新候选文件。

优先级：

1. 对几何使用目标查看器支持的 Meshopt 或 Draco 编码。
2. 把无压缩 PNG/JPEG 纹理转为目标查看器支持的 WebP 或 KTX2。
3. 保留 Base Color 的分辨率；仍超限时，优先降低 Normal 和 Metallic/Roughness 的分辨率。
4. 只有用户批准时才简化网格。

使用 glTF-Transform 时，先运行当前安装版本的 `help optimize` 或对应帮助，再根据当前 CLI 选项执行；不要盲抄历史参数。压缩后重新运行 validator、统计三角面/纹理，并做同镜头 A/B 截图。若能计算 SSIM，可作为纹理差异证据，但不能替代人工结构检查。

## 通过标准

以下全部满足才可交付：

- 当前图片版本已批准
- GLB 可解析且 validator 无 error
- 所有硬性结构约束通过
- 材质和纹理完整
- 文件大小符合限制
- 目标查看器实际加载成功
- QA 截图与批准图没有不可接受偏差
- 原始 GLB、最终 GLB 和检查记录均已保存

失败时记录失败层级：`image-source`、`provider-generation`、`download`、`glb-structure`、`material`、`runtime-render`。只回退到能修正根因的最近阶段。
