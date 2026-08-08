---
name: ni-poster
description: |
  Generate ZINE-style paper-poster prompts and raster images through one public skill with four internal modes: Standard, Gathered Scenes, Scene Distillation, and Photo Abstract Editorial. Use for themes, sentences, objects, moods, photos, or content briefs that need a tactile editorial poster. Triggers include 「做一张海报」「ZINE 风格」「极简海报」「纸感海报」「拾景纸刊」「保留照片」「撕纸边」「场景提炼」「不保留照片」「视觉隐喻」「单色块模式」「照片抽象编辑」「抽象记忆面板」「poster」「zine poster」「photo abstract editorial」. Style controls are `/ni-poster s`, `/ni-poster g`, `/ni-poster d`, and `/ni-poster a`; full names remain aliases. If no selector, explicit mode, or decisive treatment is given, interview one question at a time until one mode is confirmed before generating. Not for commercial ads, product KV, UI mockups, or article inline illustrations (use ni-article-image-gen).
---

# ni-poster — Minimal Zine Poster

Turn the user's content into both:

1. a final image-generation prompt, and
2. a generated raster image made from that prompt.

## Style Router

Select exactly one mode before compiling a prompt. Read the matching reference only after routing:

| Mode | Choose when | Photo treatment | Visual grammar |
| --- | --- | --- | --- |
| **Standard** | Generic minimal paper/zine request, no supplied photo, small subject, huge quiet field | No photo requirement; use a photo only as a small crop/cutout when requested | Small cluster, 70–90% paper, one compact high-chroma anchor, subordinate short text |
| **Gathered Scenes** | User wants the supplied scene kept truthful, photo as anchor, photo-to-illustration continuity, visible torn-paper seam, or source-derived collage | Preserve a recognizable photographic section | Photo anchor plus expansive simplified illustration field; one source-derived structural hue |
| **Scene Distillation** | User wants the photo used only as semantic reference, an authored abstract rewrite, visual metaphor, free typography, or exact `单色块模式` | Do not retain photographic pixels or photorealistic regions | Independent illustration, emotional proposition, adaptive edge, authorial text/color |
| **Photo Abstract Editorial** | User wants the original photo kept intact and paired with a clean, source-derived abstract memory panel | Preserve the original photograph as the upper/principal section | Adaptive photo/panel diptych, flat ivory panel, muted source palette, one restrained English title |

**Standard** is the original `ni-poster` base style: a quiet vertical 3:5 paper poster with 70–90% negative space, one small image cluster, aged scanned-paper texture, sparse short typography, and one clear but restrained high-chroma anchor. It does not require a source photo.

Use this priority order:

1. A valid slash selector is authoritative: `/ni-poster s`, `/ni-poster g`, `/ni-poster d`, or `/ni-poster a`. Strip the command and selector before parsing the poster content.
2. An explicit style name wins when no slash selector is present: `Standard`, `Gathered Scenes`/`拾景纸刊`, `Scene Distillation`/`场景提炼`, or `Photo Abstract Editorial`/`照片抽象编辑`.
3. A decisive visual treatment may resolve the mode without an interview: “极简纸刊/大留白小主体” selects **Standard**; “保留照片＋撕纸插画融合” selects **Gathered Scenes**; “不保留照片/场景提炼” or exact `单色块模式` selects **Scene Distillation**; “保留原片＋下方抽象面板” selects **Photo Abstract Editorial**.
4. Partial or generic cues do not resolve the mode. `保留照片` alone leaves Gathered Scenes versus Photo Abstract Editorial unresolved. `照片`, `抽象`, `纸感`, `ZINE`, or `杂志风` alone also remain unresolved.
5. If the mode remains unresolved, run the Guided Style Interview. Do not silently default to Standard and do not generate before the user confirms a mode.
6. Do not mix the core photo rules of Gathered Scenes, Scene Distillation, and Photo Abstract Editorial.

### Explicit slash selectors

Treat the first token after `/ni-poster` as a case-insensitive style selector. Prefer the short selectors; accept full names as compatibility aliases:

| Selector | Internal mode | Reference |
| --- | --- | --- |
| `s` (`standard`) | Standard | rules in this `SKILL.md` |
| `g` (`gathered`) | Gathered Scenes | `references/gathered-scenes-zine.md` |
| `d` (`distillation`) | Scene Distillation | `references/scene-distillation-zine.md` |
| `a` (`abstract`, `photo-abstract-editorial`) | Photo Abstract Editorial | `references/photo-abstract-editorial.md` |

Supported forms:

```text
/ni-poster s <theme, sentence, object, or photo request>
/ni-poster g <photo + source-faithful collage request>
/ni-poster d <photo/theme + abstract reinterpretation request>
/ni-poster a <photo + clean abstract editorial panel request>
```

If `/ni-poster` has no selector, use an explicit mode name or decisive visual treatment when present; otherwise run the Guided Style Interview. If the selector is unknown, state the valid short values (`s`, `g`, `d`, `a`) and interview the user unless the remaining request already identifies one mode decisively.

Keyword categories and examples are maintained in [references/style-routing.md](references/style-routing.md). For **Gathered Scenes**, read [references/gathered-scenes-zine.md](references/gathered-scenes-zine.md). For **Scene Distillation**, read [references/scene-distillation-zine.md](references/scene-distillation-zine.md). For **Photo Abstract Editorial**, read [references/photo-abstract-editorial.md](references/photo-abstract-editorial.md).

Photo input rule: Gathered Scenes and Photo Abstract Editorial need a supplied photo. Scene Distillation can use a supplied photo or, when explicitly requested without one, treat the user's theme/text as the semantic source. When Gathered Scenes or Photo Abstract Editorial is selected without a photo, keep the selected mode, ask the user to upload a reference photo, and wait. Never fall back to Standard merely because the photo is missing.

## Guided Style Interview

Run this interview only when no selector, explicit mode name, or decisive visual treatment has resolved the mode. Ask one concise question per turn and stop as soon as one mode is certain.

The interview selects a mode only. Never use it to rewrite, merge, weaken, or extend any mode's visual rules, source contract, generation workflow, correction policy, or output contract. After selection, execute the chosen mode unchanged.

1. Establish whether a photo exists or will be supplied and whether it should remain visible in the final artwork.
   - If a photo is supplied but its role is unclear, ask: `成品里需要保留原照片吗？`
   - If the answer is no, select **Scene Distillation**.
2. If the photo should remain visible, distinguish the two preservation modes.
   - Ask: `你想让照片与撕纸插画融合，还是保留原片并在下方接干净抽象面板？`
   - Torn-paper photo/illustration fusion selects **Gathered Scenes**.
   - Original-photo plus clean lower panel selects **Photo Abstract Editorial**.
3. If no photo is supplied or planned, distinguish the two theme-driven modes.
   - Ask: `你更想要极简大留白纸刊，还是把主题提炼成独立抽象插画？`
   - Minimal paper zine selects **Standard**.
   - Independent abstract reinterpretation selects **Scene Distillation**.
4. If an answer remains ambiguous, reflect the inferred preference in one sentence and ask one narrower confirmation. Do not repeat the full four-style menu.
5. After selection, state one concise confirmation: `将使用 [Mode]：[direct defining trait].` Then continue the normal workflow. If the chosen mode is Gathered Scenes or Photo Abstract Editorial and no photo is available, request the photo and wait.

Do not ask about color, typography, or decorative details before mode selection unless the answer is necessary to separate two remaining modes.

## Mode Policy

Use the compiler and output policy of the selected mode. Use **Standard Mode** rules below for the default route. For the other routes, load only the matching reference file and do not copy Standard's small-cluster, tiny-accent, or subordinate-text constraints into them. If the user asks for higher quality, strengthen the selected mode without changing its visual grammar.

## Standard Mode Prompt Compiler

Default generation should compile only the parts that become pixels in the final image prompt.

### Visual Rules Used by the Prompt Compiler

Use these rule groups as prompt material:

- **风格总述:** use only the visual identity and anti-identity: poetic minimal paper poster, huge negative space, old paper, tiny anchor, sparse type, one clear high-chroma anchor, zine/editorial mood.
- **核心视觉规则:** use the concrete renderable rules for canvas, composition, background, image anchor, typography, color, texture, lighting, and mood.
- **稳定共性:** use as non-negotiable must-haves: vertical 3:5 paper canvas, small cluster, scanned-paper view, old print defects, serif/typewriter text, and a saturated color anchor visible at thumbnail size.
- **可替换变量:** use as slot choices: object, photo/cutout/silhouette/block type, accent color, text line, date/weather, position, paper tone.
- **反向约束:** use as negative prompt material.
- **Prompt 结构模板:** use its field order, not its sample wording.

Do not use these as default prompt material:

- source path, sample count, README/metadata notes, or analysis scope
- long explanatory prose about why the style works
- sample-specific signatures, dates, captions, objects, or text
- example prompts as text to imitate line by line
- checklist phrasing unless it becomes a concrete visual constraint

### First-Principles Prompt Fields

Every Standard Mode prompt must answer these rendering questions in this order:

1. **Canvas:** What is the output frame and base surface?
   - tall vertical 3:5 phone-poster; full-frame aged paper; no border, no mockup.

2. **Attention Geometry:** Where does the eye go and how much is empty?
   - 70%-90% plain paper; one visual cluster occupying about 8%-25%; placed center, upper-middle, lower-middle, lower-left, or upper-right; no edge-hugging.

3. **Image Anchor:** What is the one imageable subject?
   - convert the user's theme into one object, fragment, photo crop, specimen, cutout, silhouette, old printed illustration, texture window, or small conceptual relation.

4. **Anchor Treatment:** What material process makes the anchor belong to paper?
   - grayscale photos and paper fragments may use low contrast, photocopy softness, torn edge, softened edge, halftone, scanline, risograph grain, xerox wear, ink bleed, or slight misregistration. Do not apply low saturation or low contrast to the chosen color anchor.

5. **Typography System:** How does text behave visually?
   - small serif/typewriter/monospaced type; one short readable phrase; optional tiny date/location/weather and signature; semi-legible microtext or fragmented letters; text can drift, press against the image edge, blur, or misregister.

6. **Color Logic:** What is the restrained accent strategy?
   - paper tones plus gray/black support one unmistakably high-chroma anchor. Prefer cobalt or ultramarine; rotate through cyan, violet, magenta-pink, lemon yellow, pear green, orange, or tomato red. The color may be the subject, a flat silhouette, an irregular cutout, a substantial block, a partial-color photo region, or bold fragmented type. It must not be reduced automatically to a tiny dot or hairline.

7. **Reproduction Texture:** What print/scanning process defines the whole image?
   - flat orthographic scanned-paper appearance; matte absorbent paper; diffuse light; low-to-medium contrast; no hard shadow; no 3D depth.

8. **Emotional Temperature:** What should the viewer feel before identifying the object?
   - quiet, poetic, nostalgic, sparse, diary-like, archival, distant, memory-like, Japanese/Korean indie zine or minimal editorial.

9. **Hard Avoids:** What must not appear?
   - full-bleed scene, commercial headline, product ad, logo/CTA, glossy mockup, clean UI white, cinematic lighting, 3D, neon, cute cartoon, fashion editorial drama, dense scrapbook, too many colors, long clean text.

### Standard Color Engine

This section defines the color strategy for Standard Mode.

- Default to one visibly saturated, opaque chromatic ink anchor. Use wording such as `fully saturated cobalt-blue risograph ink`, `opaque ultramarine cutout`, `vivid pear-green flat silhouette`, or `clean tomato-red printed block`.
- Keep the paper, grayscale photo, microtext, and secondary marks subdued. Preserve saturation in the color anchor even when adding grain, halftone, ink bleed, or misregistration.
- The high-chroma area should occupy roughly 0.8%-2.5% of the whole canvas or 15%-35% of the small visual cluster. It must remain visible when the image is viewed as a thumbnail.
- Color can carry the subject itself. Prefer a colored tree, fruit, shell, flower, geometric cutout, window, poster fragment, or image panel over a gray object with one colored registration tick.
- For a single image, use a substantial color anchor by default. For batches, at least 60% of images must use a colored subject, cutout, or block; the remaining images may use dots, hairlines, or colored type for rhythm.
- Do not use `near-monochrome`, `no strong accent`, `pale accent`, `muted accent`, `faded accent`, or `pastel accent` unless the user explicitly requests monochrome, muted, or pastel output.
- Do not describe the entire image as low saturation. Apply `low contrast` and `muted grayscale` only to paper, photos, and secondary ink.
- Use only one main high-chroma hue per image. A tiny secondary hue is allowed only when it supports the subject and does not make the poster commercially colorful.

### Standard Prompt Shape

Write the final Standard Mode prompt as four compact paragraphs:

1. canvas + paper + negative space + cluster size/location
2. subject metaphor + anchor type + anchor treatment
3. typography + accent strategy + print defects
4. flat scan mood + avoid-list

In paragraph 3, state the exact high-chroma hue, its material form, and its approximate visual share. This structure is more important than reciting every rule. Prefer a concrete, imageable prompt over a long style essay.

## Variation Engine

Before writing the prompt, choose one option from each axis. Randomness must change visual grammar, not only position. If recent outputs used the same layout or anchor, choose a different one.

### Layout Family

- **center-fragment:** tiny central image or object with surrounding air
- **lower-left-float:** small anchor in the lower-left quadrant, lots of empty top space
- **upper-right-block:** small color/photo block in the upper-right with loose text drift
- **dual-panel:** two small overlapping or adjacent panels with a narrow gap
- **irregular-cutout:** torn or organic paper shape carrying image or type
- **type-led:** typography is the main visual anchor, image secondary or absent
- **dot-orbit:** dots, letters, or hairline create an orbit around a small subject
- **single-specimen:** one isolated object or mark with almost no support graphics

### Image Anchor

- tiny faded photo
- torn-paper clipping
- flat silhouette
- solid color block
- old printed illustration
- object specimen
- translucent geometric overlay
- abstract texture window

### Typography Mode

- fragmented floating letters
- short phrase pressed against image edge
- archive microtext with date/weather
- diagonal scattered words
- low-contrast gray ghost text
- headline-as-object with rough letterpress
- text inside a color block or cutout
- almost textless, only a tiny caption

### Texture Mode

- xerox softness
- risograph grain
- letterpress ink bleed
- halftone degradation
- film grain photo
- scan noise and paper fibers
- aged paper mottling
- soft motion blur on selected text

### Mood Mode

- quiet
- summer
- solitude
- childhood
- seaside
- afternoon
- night
- memory
- slight surrealism

## Workflow

1. Determine mode.
   - Parse `/ni-poster <selector>` first. If present and valid (`s`, `g`, `d`, `a`, or a full-name alias), use that selector as the resolved mode even when content keywords point elsewhere. Record both the selector and resolved mode in the final response.
   - If no selector is present, use an explicit mode name or decisive treatment when available. Otherwise run the Guided Style Interview, stop the current generation workflow, and wait for the user's answer. Resume only after one mode is confirmed.
   - Record the selection method as `selector`, `explicit request`, or `interview`.
   - If the selected mode is Gathered Scenes, Scene Distillation, or Photo Abstract Editorial, read its reference file before analyzing the source image.

2. Parse the user's content.
   - Identify the core subject, mood, exact text if supplied, possible visual metaphor, and any reference image role.
   - For an article or complex idea, extract one central imageable idea rather than summarizing the whole argument.
   - In Standard Mode, if no image text is supplied, invent one short poetic English or Chinese phrase. In the routed modes, follow the selected reference's text policy instead.

3. Select a variation recipe.
   - In Standard Mode, pick layout, image anchor, typography, texture, and mood from the Variation Engine, then choose color through the Standard Color Engine. Do not select `near-monochrome` unless the user explicitly asks for it.
   - In Gathered Scenes, Scene Distillation, or Photo Abstract Editorial, follow the selected reference's source analysis, composition, edge, color, typography, and correction rules instead of this Variation Engine.
   - Do not default to "tiny photo + blue dots + microtext" unless it truly fits.
   - If the recipe becomes too dense, simplify typography or color treatment first.

4. Write the final image prompt.
   - In Standard Mode, use the Standard Mode Prompt Compiler to compile the user's content into the four-paragraph prompt shape: canvas, anchor, typography/accent/print, flat-scan mood and avoid-list.
   - Specify exact in-image text only when useful. Keep it short because image models distort long text.
   - Make the prompt decisive: say where the anchor sits, how large it is, how text behaves, what accent appears, and how the print/scan texture looks.

5. Generate the image.
   - Use whatever image-generation capability the current runtime exposes. Resolve it in this order, and stop at the first one that works:
     1. a native/built-in image-generation capability of the running agent (e.g. Codex built-in generation);
     2. an installed image-generation skill or tool in this environment (e.g. `chatgpt-imagegen`, an MCP image tool, or any project-local generation CLI);
     3. an image-generation command the user has already told you to use in this session.
   - Do not hardcode a single vendor. Do not ask the user which tool to use if one of the above is already available — just use it and name the tool in the output.
   - Do not stop after prompt-only unless the user explicitly asks for prompt-only, **or** no generation capability is available at all. In the no-capability case, state plainly that no image was generated and why, and name the concrete missing capability. Return the final prompt automatically only in Standard Mode; for Gathered Scenes, Scene Distillation, or Photo Abstract Editorial, return it only if the user asked for it.
   - If Standard, Gathered Scenes, or Photo Abstract Editorial visibly violates the selected mode or recipe, tighten only the failed constraint and regenerate once. In Gathered Scenes, preserve the truthful photo and torn handoff; in Photo Abstract Editorial, preserve the faithful photo and clean ivory join during this correction.
   - In Scene Distillation, follow its reference: do not perform an automatic visual-inspection review or regeneration after a successful generation unless the user asks for a check/revision. Retry only a concrete runtime generation failure.
   - In Standard Mode, inspect the result at thumbnail scale. If the high-chroma anchor is absent, washed out, or reduced to an imperceptible mark, regenerate once with stronger color wording and a larger colored area.

6. Return the mode-specific output contract. State the selected mode; Standard includes the final prompt by default, while the three routed reference modes return their rationale/notes and reveal the prompt only when requested.

## Negative Constraints

Always avoid:

- full-bleed subject or scene
- commercial poster headline hierarchy
- product ad layout, logo lockup, CTA, or brand campaign feeling
- clean digital UI background
- glossy paper mockup or heavy paper shadow
- 3D rendering, cinematic lighting, hard shadows, depth of field, neon, cyberpunk
- cute cartoon, kawaii illustration, anime poster, fashion editorial drama
- too many objects, stickers, colors, captions, or decorative textures
- high-resolution stock-photo realism
- long, clean, perfectly readable text blocks

## Output Format

Use this output format for **Standard Mode**. Gathered Scenes, Scene Distillation, and Photo Abstract Editorial have their own output contracts in their reference files: each returns the generated image and concise rationale/notes by default, and reveals the final prompt only when the user asks for it.

````markdown
**生成图**

![ni-poster ZINE style poster](absolute-image-path-or-rendered-image)

**最终 Prompt**

```text
[final prompt used for image generation]
```

**说明**

- Selector: [s / g / d / a / none]
- Selection: [selector / explicit request / interview]
- Mode: Standard
- Tool: [the image-generation capability actually used]
- Recipe: [layout / anchor / typography / accent / texture / mood]
- [one short note about the content interpretation]
````

If generated images render directly without a file path, show the image normally and still include the final prompt.

If no generation capability was available, replace the **生成图** block with a one-line note naming the missing capability, and still deliver the final prompt and recipe.

## Quality Gate

Before finalizing, check:

- Was exactly one mode confirmed before prompt compilation or image generation?
- If the request did not specify a mode decisively, did the run interview the user instead of silently defaulting?
- Did the run use the Standard Mode Prompt Compiler?
- Did the run choose a variation recipe across layout, anchor, typography, accent, texture, and mood?
- Is the structure materially different from recent visible outputs?
- Does the image remain a sparse vertical paper poster?
- Does 70%-90% of the poster read as paper?
- Is the subject cluster roughly 8%-25% of the canvas?
- Is there one clear visual metaphor rather than a whole illustrated scene?
- Does the anchor have old-photo, clipping, print, scan, or paper-specimen treatment?
- Are typography and microtext part of the composition?
- Is there only one restrained accent strategy?
- In Standard Mode, is the high-chroma anchor clearly visible at thumbnail size?
- In Standard Mode, does saturated color occupy about 0.8%-2.5% of the canvas or 15%-35% of the visual cluster?
- In Standard Mode, did the prompt avoid weakening the color anchor with `pale`, `muted`, `faded`, `pastel`, `low saturation`, or `near-monochrome` wording?
- In Photo Abstract Editorial, is the uploaded photo faithful, is the lower panel flat neutral ivory, are all motif marks source-derived, and is there no torn edge, texture, shadow, or invented color?
- In Photo Abstract Editorial, is there only one restrained English title on the abstract panel and no extra labels, dates, logos, or watermarks?
- Did the prompt avoid full-bleed, commercial, 3D, neon, cinematic, cartoon, cute, brand, and generic template aesthetics?
- Did you actually generate the image, or explicitly report that no generation capability was available?

## Example Requests

- "用 ni-poster 做一张关于雨天的图"
- "用 ni-poster 做一张关于旧书的海报"
- "用这张照片做一张同风格 poster"
- "把这句话做成 ZINE 风海报：夏天结束得很轻"
- "保留这张照片的真实感，用拾景纸刊做成照片和插画相接的海报"
- "用这张照片做场景提炼，不要保留照片像素，要有视觉隐喻"
- "用 ni-poster 的单色块模式处理这张图"
- "用 photo abstract editorial 把这张照片和抽象记忆面板做成干净的编辑双联作品"
- "/ni-poster s 把这句话做成极简纸刊：夏天结束得很轻"
- "/ni-poster g 保留这张照片的真实场景，加入手撕纤维边"
- "/ni-poster d 用这张照片做视觉隐喻，不保留照片像素"
- "/ni-poster a 保留原照片，在下方生成来源于照片关系的象牙色抽象面板"

## Reference Examples

See `examples/` for six generated posters in this style: `night-door`, `yellow-step`, `shore-pause`, `pause-map`, `typhoon-memory`, `moon-tide`. Use them to calibrate negative-space ratio, cluster size, and accent share — not to copy their objects, dates, or captions.

## Attribution

Ported from [gc-minimal-zine-poster](https://github.com/LiamGvchi/gc-minimal-zine-poster) (Minimal Zine Poster v0.1) by LiamGvchi, MIT License. Visual rules and prompt compiler preserved verbatim; the generation step was made runtime-agnostic for the ni-skill suite.
