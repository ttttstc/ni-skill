# ni-poster Style Routing

Use this file only after `ni-poster/SKILL.md` has triggered. Resolve exactly one of five internal modes before compiling a prompt or generating an image.

## Mode map

| Mode | Direct defining trait | Photo contract | Visual grammar |
| --- | --- | --- | --- |
| Standard | 极简纸刊 / 大留白小主体 | Photo optional | 3:5 aged paper, 70–90% quiet space, small cluster, one saturated anchor |
| Gathered Scenes | 保留照片 + 撕纸插画融合 | Supplied photo remains recognizable | Truthful photo anchor, torn-fiber handoff, expansive source-derived illustration field |
| Scene Distillation | 不保留照片 / 场景提炼 | Photo is semantic reference only; theme/text may substitute | Independent abstract illustration, visual metaphor, authorial typography; exact `单色块模式` |
| Photo Abstract Editorial | 保留原片 + 下方抽象面板 | Supplied photo remains intact as upper/principal section | Clean direct join, flat ivory memory panel, muted source palette, one English title |
| Reality Restaged | 超现实电影画面 / 纪实重构 | Supplied documentary/travel/street/cultural photo is memory, not pixels; real people, gestures, and cultural details survive | Cinematic tableau, radically simplified stage, large saturated color fields, strong negative space, one impossible relationship, analog film realism |

## Decisive signals

Use only direct, mode-defining signals for no-interview routing:

- **Standard:** `极简纸刊`, `大留白小主体`, `minimal zine`.
- **Gathered Scenes:** `撕纸边`, `照片与插画融合`, `拾景纸刊`, `torn-paper photo illustration`.
- **Scene Distillation:** `不保留照片`, `场景提炼`, `照片只作参考`, `no photo pixels`, or exact `单色块模式`.
- **Photo Abstract Editorial:** `照片＋抽象面板`, `原片下方接抽象面板`, `照片抽象编辑`, `photo plus abstract panel`.
- **Reality Restaged:** `超现实电影画面`, `纪实重构`, `重构这张照片`, `不可能世界`, `克制的超现实`, `reality-restaged`, `restage this photo`, `restrained surreal cinematic tableau`.

Do not route from generic words alone: `照片`, `保留照片`, `抽象`, `纸感`, `ZINE`, `杂志风`, `安静`, `诗性`, `memory`, `editorial`, or bare `超现实`/`电影感`/`surreal`. These describe more than one mode.

## Guided interview

Interview when no selector, explicit mode name, or decisive signal identifies one mode. Ask one question per turn.

Interview controls selection only. It must not change or hybridize any child style's capabilities. Once selected, load and follow that mode's existing rules unchanged.

### Photo supplied or planned

1. Ask whether the original photo should remain visible.
2. If no, ask whether the user wants:
   - the photo rebuilt as a photographically believable surreal cinematic world, real people and cultural details preserved: **Reality Restaged**;
   - an independent abstract illustration: **Scene Distillation**.
3. If yes, ask whether the user wants:
   - photo fused into torn-paper illustration: **Gathered Scenes**;
   - original photo joined to a clean lower abstract panel: **Photo Abstract Editorial**.

### No photo supplied or planned

Ask whether the user wants:

- minimal aged-paper zine with large whitespace: **Standard**;
- independent abstract reinterpretation from the theme/text: **Scene Distillation**.

If the answer stays vague, ask one narrower contrast based on the remaining two modes. Do not show all five choices again. Confirm the selected mode in one sentence before continuing.

## Conflict resolution

1. A valid `/ni-poster s|g|d|a|r` selector overrides all other signals, including `单色块模式`.
2. An explicit mode name overrides inferred treatment cues.
3. A decisive treatment resolves the mode without an interview.
4. `保留照片` alone is incomplete because both Gathered Scenes and Photo Abstract Editorial retain photography; interview between torn illustration and clean abstract panel.
5. If the user combines contradictory treatments, ask a narrow clarification instead of honoring word order or inventing a hybrid.
6. Gathered Scenes, Photo Abstract Editorial, and Reality Restaged require a supplied photo. If one is selected without a photo, ask for the photo and wait; do not fall back to Standard.
7. Do not compile a prompt or generate an image while mode remains unresolved.

## Slash command contract

`ni-poster` remains the only public skill:

```text
/ni-poster s ...
/ni-poster g ...
/ni-poster d ...
/ni-poster a ...
/ni-poster r ...
```

Full names remain compatibility aliases. `/ni-poster ...` without a selector uses decisive signals when present; otherwise it starts the Guided Style Interview.

## Examples

```text
用 $ni-poster 做一张关于雨天的海报
```

No mode specified. Start interview; do not generate yet.

```text
保留这张照片做海报
```

Photo retention specified, handoff unresolved. Ask Gathered Scenes versus Photo Abstract Editorial.

```text
用这张照片做场景提炼，不保留照片像素
```

Route: Scene Distillation.

```text
把这张旅行照重构成克制的超现实电影画面，人物和文化细节要真实
```

Route: Reality Restaged. If no photo is attached, request it and wait.

```text
/ni-poster a 保留原照片，在下方生成干净象牙色抽象面板
```

Route: Photo Abstract Editorial. If no photo is attached, request it and wait.
