# 需求确认与图片审核

## 目录

- [最小问题集](#最小问题集)
- [需求确认单模板](#需求确认单模板)
- [多视图生成提示结构](#多视图生成提示结构)
- [审图自检](#审图自检)
- [图片审核回复模板](#图片审核回复模板)

## 最小问题集

只问会改变结果的问题。优先顺序如下：

1. **主体边界**：具体要做什么？单体、成组、剖面还是完整外观？
2. **用途**：网页近看、游戏实时、AR、打印、演示还是收藏？
3. **风格锚点**：有参考图、现有 GLB、项目页面或色板吗？哪些特征必须继承？灯光只是查看器预览，还是需要烘焙效果或模型内灯光？
4. **结构约束**：数量、左右、朝向、必须出现和绝不能出现的结构是什么？
5. **交付规格**：面数、纹理、文件大小、尺寸/原点、输出目录有什么限制？
6. **外部服务**：目标是 Hunyuan、Tripo 还是其他服务？当前上传槽位是什么？只用免费额度吗？允许消耗几次？
7. **图片预算**：指定哪个图像生成器？最多允许几次图片尝试、多少费用或额度？默认建议“初稿 + 1 次自动纠正”，但必须写入确认单。

用户没有技术偏好时，给出带理由的默认值，不把术语题全部丢回用户。例如网页展示可建议：带纹理 GLB、PBR 材质、中心原点、Y-up、保持完整轮廓，文件上限由项目已有资产推断。

## 需求确认单模板

```markdown
## 需求确认单 v001

- 主题/名称：
- 主体边界：
- 使用场景：
- 风格参考：
- 配色/材质/灯光：
- 必须出现：
- 禁止出现：
- 结构与视角：
- 目标服务与槽位协议：
- 图像生成器：
- 图片尝试预算：
- GLB 规格：
- 输出位置：
- 生成服务与额度：
- 本轮非目标：

请回复“确认”，或指出需要修改的字段。确认前我不会生成图片。
```

如果用户说“跟参考模型一样”，必须先实际查看至少一个参考模型的轮廓、材质、色彩和光照。把“像”拆成可审核事实，不写空泛的“风格统一”。

## 多视图生成提示结构

把已确认需求编译为具体、可见的像素约束：

```text
Create one coherent 3D asset multiview review sheet for [subject].
The panels depict the exact same physical instance and geometry using
the confirmed [provider] slot protocol: [ordered view names and angles].

Identity locks:
- [count / left-right / orientation / silhouette constraints]
- [required structures and their stable relative positions]
- no mirrored duplicate, no second instance, no geometry drift between panels

Appearance locks:
- [reference-derived palette]
- [material, roughness, texture, stylization]
- [neutral studio lighting used only for review]

Reconstruction constraints:
- centered object, full silhouette visible, consistent scale and camera height
- neutral solid background, minimal perspective, no pedestal
- no text inside panels, no watermark, no labels over the object
- no cropped extremities, no floating debris, no unexplained occlusion
```

按主题补充结构事实。医学、工程和产品结构不得仅凭印象生成；优先读取用户资料或可靠参考。无法确认的事实必须在需求门禁中暴露。

当确认协议为 Hunyuan `front/left/right/back` 时，生成正面、真实左侧、真实右侧、真实背面；不要用左前 45° 或右后 45° 替代左右侧图。其他服务按其当前槽位协议生成，不跨服务复用视图模板。

## 审图自检

展示给用户前检查：

- 四格是否是同一对象，而不是四个相似对象
- 正面与背面是否真有视角变化，不是水平翻转
- 左右结构在旋转中是否保持同一侧
- 数量是否固定，有无第二耳垂、额外手指、重复附件等
- 剖面是否在正确一侧，是否产生悬垂碎片
- 颜色、材质、比例和光照是否跨视图一致
- 每格是否完整露出轮廓，足以供图生 3D
- 是否包含文字、水印、台座、边框或背景杂物

明显失败时保存到 `review/rejected/` 或标明 rejected，不要让用户误以为它是候选终稿。每次调用前先检查 `image_attempts_used < image_attempt_budget`；调用后立即递增次数并记录实际工具、模型、模式和已知费用。达到上限后停止并让用户决定是否增加预算。

## 图片审核回复模板

```markdown
多视图审核包 v001 已生成：

![多视图审核图](绝对路径)

请重点检查：
- [关键结构 1]
- [关键结构 2]
- [数量/左右/朝向]
- [风格与材质]

请回复“图片通过”，或按下面格式反馈：
- 保留项：
- 修改项：

图片通过前我不会上传 3D 服务或消耗额度。
```

用户只修改局部时，锁住保留项，不重做无关风格。任何实质修改生成新版本，并重新走图片审核门。
