# 提示词

以下是可调整的模板。替换主体、数量、动作、比例和用户保持项；不要直接把示例双人场景塞进其他请求。保存最终实际发送的完整提示词。

## 白石底图

```text
Use case: stylized-concept.
Asset type: a base illustration for an interactive shallow-relief material.
Subject: [exact subjects, count, pose, direction, necessary props].
Composition: [aspect ratio], full complete silhouettes, [layout]. Keep all limbs,
hands, feet and object tips inside the frame with useful empty margins.
Style: refined Athens-like ivory VERY SHALLOW bas-relief on a flat warm-gray
#DDDCD7 wall. Graceful readable silhouettes and broad smooth sculptural planes.
Only a few broad shallow cloth folds; smooth skin, simplified hair masses,
[smooth refined robot shells if relevant], clear facial forms and hands.
Lighting: soft diffuse low-contrast light, shallow clean carving.
Avoid: tiny repeated folds, gritty grain, pores, dirty scratches, intricate
mechanical seams, deep cut shadows, baked metallic highlights, extra objects,
text, logos, borders and watermarks unless explicitly requested.
Preserve: [user's actual invariants].
```

保留足够结构供法线恢复。不要用“完全无细节”代替“减少碎细节”。用户已有底图时，把它标为编辑目标，写明只改哪些部位。

## 配套法线

编辑输入顺序优先为：1 当前底图（唯一构图目标）；2 用户给出的法线风格参考，或 `assets/reference/normal.png`；需要时再加入参考底图解释配套关系。实际工具只能提供有限参考数量时，先保留目标与法线参考。

```text
Use case: precise-object-edit / technical texture conversion.
Asset type: registered RGB surface normal DATA TEXTURE for the Athens relief shader.
Image 1 is the EXACT edit target: preserve its geometry, framing and pixel layout.
Image 2 is a normal encoding and sculptural-detail reference ONLY, never a
composition or subject reference.
Convert image 1 into its matching full-frame normal map. Preserve the exact
[count, identities, faces, outlines, limbs, fingers, hair, cloth, objects], their
positions, proportions and pose. Match [width x height] and [aspect ratio].
Reconstruct sculpted surface direction: clear eyelids, nose bridge, lips, ears,
finger joints, curved necks, shallow hair forms and broad flowing cloth with
crisp rounded edges. Keep subtle metal-ready surface undulations without grit,
extra wrinkles, scratches or extra folds. No smeared bulbous normals, plastic
cast or broad shiny bands. Do not move features or add anatomy.
Encode actual RGB direction gradients matching image 2: flat forward-facing
surfaces and empty background RGB(128,128,255); left-facing lower red, right-facing
higher red; up-facing higher green, down-facing lower green; positive forward Z
in blue. Keep high blue and controlled green/cyan/pink gradients.
No baked white highlights, grayscale marble shading, final metallic render,
material/albedo colors, cast shadows, text, labels, borders or watermark.
Background is uniform #8080ff, without grain or gradients outside the sculpture.
Prioritize exact registration and small sculpted curves.
```

法线提示词不保证数学正确。把输出接进真实 shader、固定光源和局部细节对照后才能判断。

## 透明主体 / 遮罩辅助

只有确实需要切出主体时调用图像编辑，设置透明背景，保留真实 alpha。

```text
Use case: background-extraction.
Extract ONLY the existing relief sculpture from image 1 onto genuine transparency.
Preserve exact framing, dimensions, pose, fingers, thin objects and silhouettes.
All air gaps between limbs, objects and inside arches remain transparent.
Remove the wall and wall cast shadows. No outer glow, no added outlines, no filled
holes, no redesigned objects, no cropping or recentering.
```

检查后把 alpha 作为遮罩，不把生成器返回的棋盘格或白底当作透明度。提取造成轮廓位移时不得直接用于旧底图，需修配准或换用分割得到的候选遮罩。

## 静态金属导出

优先打开验收通过的 HTML，切换固定左/中/右光源，等待一帧稳定渲染后截图。全幅、局部脸手与不同光源一起审视。交付 PNG 时附对应光源与参数。

用户明确要求直接生成金属图片时，在底图模板中把材质替换为“silver-gray sculpted metal, controlled narrow moving-form-like highlights, readable faces and hands, no blown-out highlights”；删除“no baked metallic highlights”。不要再把这种图用于白石底图或法线恢复，也不要说它能响应鼠标。
