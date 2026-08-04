# ni-poster Style Routing

Use this file only after `ni-poster/SKILL.md` has been triggered. It separates the three modes so a generic “zine” request does not accidentally receive the wrong photo behavior.

## Mode map

| Mode | Source contract | Composition scale | Color role | Text role | Default return |
| --- | --- | --- | --- | --- | --- |
| Standard | Theme, text, object, or optional reference image | Small cluster; 8–25% cluster and 70–90% paper | One compact saturated anchor; roughly 0.8–2.5% canvas | Short, quiet, subordinate line | Image + final prompt + recipe |
| Gathered Scenes | Supplied photo is factual visual anchor | Photo about 25–60%; illustration field about 45–70%; much of field remains quiet | One source-derived added hue bridges or restructures photo and illustration | One small editorial micro-text line, English by default | Image + brief Chinese rationale; prompt only if requested |
| Scene Distillation | Supplied photo is semantic reference only; text/theme may substitute when explicitly requested | 68–85% paper; active cluster about 12–32%; source orientation normally preserved | Standard Accent or exact Solid Color-Block Mode | Fully authorial: caption, interruption, field, fragments, or none | Image + Chinese idea + concise art direction; prompt only if requested |

## Keyword buckets

### Explicit mode names — strongest

- Standard: `Standard Mode`, `minimal zine`, `极简纸刊`, `小主体海报`, `大留白海报`.
- Gathered Scenes: `Gathered Scenes`, `拾景纸刊`, `拾景`, `真景为锚`, `照片锚点`.
- Scene Distillation: `Scene Distillation`, `场景提炼`, `场景蒸馏`, `抽象重构`, `作者化再创作`.

### Source-handling cues — resolve photo ambiguity

Gathered Scenes cues:

- `保留照片`, `照片真实`, `照片是主体`, `保留场景识别度`, `照片与插画相接`
- `photo anchor`, `truthful photography`, `keep the photo`, `source-derived illustration field`

Scene Distillation cues:

- `照片只作参考`, `不保留照片`, `不要照片像素`, `不出现摄影区域`, `只提炼情绪/语义`
- `semantic reference only`, `no photo pixels`, `abstract reinterpretation`, `visual metaphor`

### Material and composition cues — secondary

Gathered Scenes cues:

- `撕纸纤维边`, `手撕照片边`, `照片到纸面的撕裂过渡`, `来源形状延展`, `场景拼贴但不拥挤`
- `torn-paper seam`, `hand-torn fibrous edge`, `photo-to-paper handoff`, `source continuation`

Scene Distillation cues:

- `情绪命题`, `中心张力`, `视觉隐喻`, `自由排版`, `不按模板排字`, `独立插画`
- `expressive proposition`, `central tension`, `authorial typography`, `independent illustration`

Standard cues:

- `安静`, `诗性`, `极简`, `超大留白`, `小图钉式主体`, `短句`, `静谧纸感`
- `quiet minimal`, `huge negative space`, `tiny anchor`, `short phrase`, `paper zine`

### Color trigger

The exact string `单色块模式` is a hard route to Scene Distillation. It means one contiguous fully saturated color field and neutral ink everywhere else. Do not interpret it as “use a small color accent,” and do not route it to Standard or Gathered Scenes.

## Conflict resolution

1. A valid `/ni-poster s|g|d` selector overrides all inferred cues and `单色块模式`; full names remain compatibility aliases.
2. Without a selector, follow an explicit mode name over inferred cues.
3. Without a selector, follow `单色块模式` over other color words, but keep the user's explicit source-handling instruction if compatible.
4. When “保留照片” and “不保留照片” both appear without a selector, honor the later explicit instruction and mention the chosen interpretation briefly.
5. Without an explicit selector, if a mode's source contract is impossible (for example, Gathered Scenes without a photo), fall back to Standard rather than inventing source material. With `/ni-poster g`, keep the requested mode and state that a reference photo is required.
6. Do not combine these pairs unless the user explicitly asks for a hybrid: “photo truthful” + “no photo pixels”; “tiny compact accent” + “large structural color field”; “subordinate micro-text” + “free authorial typography”. If a hybrid is requested, preserve the explicitly named source treatment and borrow only compatible secondary rules.

## Slash command contract

`ni-poster` is the only public skill. The first token after the slash command is optional and accepts three short canonical selectors:

```text
/ni-poster s ...
/ni-poster g ...
/ni-poster d ...
```

The selector controls the internal mode; the remaining text is the content request. Full names are accepted as aliases. `/ni-poster ...` without a selector uses automatic keyword routing.

## ni-poster invocation examples

```text
用 $ni-poster 做一张关于雨天的极简纸刊海报
```
Route: Standard.

```text
/ni-poster g 保留这张照片的场景，加入照片锚点和撕纸纤维边
```
Route: Gathered Scenes.

```text
/ni-poster d 处理这张照片，照片只作语义参考，改成视觉隐喻
```
Route: Scene Distillation.

```text
/ni-poster s 处理这张图，使用单色块模式
```
Route: Standard, because explicit selector overrides the inferred `单色块模式` route.
