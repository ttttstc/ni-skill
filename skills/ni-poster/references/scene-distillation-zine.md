# Scene Distillation Zine v1.3

Use only when the Style Router selects **Scene Distillation**. This is a compact port of `Zeejay0/gathered-scenes-zine-skill/skills/scene-distillation-zine-v1-3`. The photo is semantic reference only; the final artwork contains original illustration, paper, and typography, not photographic pixels.

## Core identity

Turn a supplied photo, or an explicitly supplied theme/text when no photo exists, into an independently compelling paper poster. Follow:

`source fact → emotional residue → expressive proposition → central tension → visual metaphor → formal embodiment → interpretive opening`

Prioritize one specific artistic proposition, one central emotional/conceptual tension, an independent aesthetic voice, semantic provenance, deliberate hierarchy/eye path, material/edge/color/text that serve the proposition, substantial quiet space, and one meaningful unresolved relationship. Do not treat the work as photo filtering, style transfer, rotoscoping, or a literal illustrated copy.

## Distillation Card

Inspect the source and resolve:

- **Semantic nucleus:** smallest subject, relationship, or event that gives it meaning.
- **Core subject:** one primary subject, or at most two inseparable subjects.
- **Supporting elements:** one to three place, season, action, or atmosphere cues.
- **Dominant gesture:** gaze, lean, curve, diagonal, path, repetition, convergence, or movement.
- **Spatial cue:** one relationship worth preserving: near/far, above/below, facing, overlap, enclosure, or direction.
- **Visual-weight map:** area, darkness, saturation, faces, isolation, edge tension, texture.
- **Native palette/material/weather:** hue family, temperature, water, snow, haze, glass, foliage, stone, fabric, wind, rain, or light.
- **Emotional residue:** feeling left after factual description is removed.
- **Discard list:** clutter, redundant objects, background detail, and realistic information that should disappear.
- **Transformation opportunities:** forms to enlarge, merge, fragment, repeat, displace, or turn into negative space.

Preserve only two to four source anchors. Do not preserve the original composition by default.

## Expression engine

Write one internal proposition that is relational and source-specific, not a generic label such as “quiet,” “healing,” “nostalgic,” or “beautiful.” Choose one central tension such as intimacy/distance, shelter/confinement, movement/stillness, smallness/vastness, warmth/coldness, memory/disappearance, order/growth, visibility/concealment, or permanence/fragility.

Use one source-derived object, spatial relationship, material behavior, or gesture as the central visual metaphor. Allow purposeful shifts of scale, function, proportion, crop, orientation, or interval, but every invented addition must extend emotion, clarify relationship, establish rhythm, balance weight, guide the eye, or strengthen the metaphor. Leave one meaningful interpretive opening through omission, obstruction, scale shift, incomplete action, or text–image gap.

## Abstraction and composition

Use editorial abstraction: preserve semantic nucleus, dominant gesture, and one source-specific cue; remove roughly 65–90% of descriptive detail; replace realism with simplified masses, broken contours, paper fragments, sparse marks, or print fields; generalize facial identity unless likeness is requested.

Choose one primary grammar and at most one supporting grammar:

- cut-paper mass;
- dry-print silhouette;
- broken contour;
- rhythm field;
- fragment stack;
- orbit or drift.

Choose one composition family from source geometry: asymmetric island, torn window, directional drift, rhythmic circulation, staggered fragments, vertical tension, or auxiliary constellation. Start with 68–85% quiet paper, one active cluster about 12–32% of the canvas, one dominant mass, one to three supporting forms, and one restrained texture field. Correct by actual visual weight, not by mechanical centering. Preserve source orientation by default: portrait 3:5, landscape 5:3, square/ambiguous 3:5.

## Transition edge

Choose one primary edge treatment and at most one subordinate treatment by material mood and expressive function:

- **Torn-fiber edge:** exposed fibers and broken contour for separation, rupture, or accumulation.
- **Layered grayscale edge:** two or three narrow neutral bands for shallow material separation without cast shadow.
- **Stippled dissolution:** sparse dots/halftone/grain derived from source movement.
- **Irregular mark edge:** one to three source-derived shapes continue rhythm or direction.
- **Natural isolated contour:** clean organic illustrated silhouette meets paper directly; no torn boundary, halo, rim, or border.

Align the edge with a source horizon, gesture, path, pressure, material change, or directional break. Keep it flat and tactile. Allow zero to two forms to cross when useful. Never apply all treatments together; avoid generic ripped rectangles, tape, floating paper, heavy shadows, curled corners, bevels, and realistic depth.

## Color modes

Use **Standard Accent Mode** unless the request contains the exact trigger `单色块模式`. Resolve color by visual role, source relation, value contrast, chroma, material form, area, and adjacency. Choose one exact high-chroma hue and one role: focal pin, counterweight, bridge, directional cue, or rhythmic beat. Use a paper-native material such as risograph ink, opaque cut paper, flat silhouette, or dry-print block. Keep total high-chroma area roughly 0.8–3% of the poster or 10–30% of the active cluster, with subordinate echoes below 25% of accent area.

When the source has a meaningful repeatable motif, a **Distributed Supporting Accent** may redraw and disperse several unequal source-derived instances around the core subject. Do not invent confetti, arbitrary petals, equal spacing, or unsupported color points.

### Solid Color-Block Mode

When the exact trigger `单色块模式` appears, use exactly three color categories:

1. natural paper tone;
2. one unified achromatic/near-neutral ink system for all non-accent forms and text;
3. one contiguous, fully saturated color field.

Make the connected color field source-derived, opaque, and about 3–12% of the poster or 25–65% of the active cluster. It must be the visual entry point or central spatial idea, not a detached rectangle, dot, stripe, swatch, or set of echoes. Every other printed form stays charcoal, graphite, warm gray, brown-black, or off-black. Include this explicit constraint in the final prompt:

`Color mode: Solid Color-Block Mode. Use exactly one contiguous [exact hue] field. Render every other printed form in neutral charcoal, graphite, warm gray, or off-black ink. Typography may use the neutral ink system and/or [exact hue], but no other chromatic color may appear anywhere.`

## Typography

Typography is fully authorial. Do not impose a preset language, word count, font, alignment, hierarchy, baseline, direction, placement, color relationship, legibility threshold, or amount. Use English, Chinese, bilingual material, fragments, repeated words, long passages, marks, or no text according to the proposition. Text may be caption, countervoice, interruption, visual rhythm, architectural form, field, path, quotation, private notation, or primary subject; it may be tiny, oversized, cropped, rotated, curved, obscured, fragmented, overwritten, or mixed into the material. Do not default to a neat caption.

## Prompt and workflow

Compile five compact sections:

1. expressive proposition, central tension, visual metaphor, interpretive opening, and visible formal consequences;
2. source-responsive canvas/orientation, paper, quiet-space share, cluster, hierarchy, and eye path;
3. semantic nucleus, preserved anchors, transformations, omissions, inventions, and illustration grammar;
4. chosen edge treatment, exact hue/mode/role/area, and any authorial text behavior;
5. reproduction texture, emotional temperature, no-photo rule, and hard avoids.

Always include: `Do not reproduce, embed, crop, collage, trace, or retain photographic pixels or photorealistic regions from the reference. The final image must contain original illustration, paper, and typography only.`

Workflow: inspect source, select orientation, build Distillation Card, write proposition/tension/metaphor/opening, detect exact color trigger, select anchors and discard list, choose one transformation, choose composition and grammar, choose edge, resolve color, decide text freely, compile, generate using the source semantically, and return image plus idea/notes. Inspect or regenerate only when the user requests a check/revision, unless the runtime requires one targeted correction to recover a clearly failed generation.

## Output contract

By default return the generated image, a concise Chinese **创作想法**, and concise **艺术指导** notes:

- Distillation: semantic nucleus / preserved anchors / discarded reality;
- Expression: proposition / central tension / interpretive opening;
- Authorship: recomposition / metaphor / exaggeration / invention;
- Composition: family / hierarchy / eye path / quiet-space share;
- Edge: primary treatment / structural role;
- Color: mode / exact hue / form / role / position / area;
- Text: material / role / behavior / hierarchy / image interaction.

Reveal the full generation prompt only when the user explicitly asks.

## Hard avoids

No original photo fragments, photorealistic regions, photo windows, tracing, rotoscoping, literal full-scene illustration, exact composition copying, generic mood labels without embodiment, arbitrary dots/grids, unsupported decorative scattering, evenly repeated color motifs, sticker outlines, fuzzy halos, stamps, tape, multiple bright hues, dense scrapbooking, commercial hierarchy, logos, CTA, glossy mockups, curled paper, hard shadows, 3D, cinematic lighting, depth of field, neon, fashion drama, cute cartoon/anime, polished vector characters, long text, invented quotations, faux metadata, or watermark. In Solid Color-Block Mode also avoid supporting color tints, multiple colored regions, accent echoes, and detached swatches.

## Attribution

Ported and condensed from [Zeejay0/gathered-scenes-zine-skill](https://github.com/Zeejay0/gathered-scenes-zine-skill), `scene-distillation-zine-v1-3`, MIT License. Preserve the upstream copyright notice in `LICENSE.gathered-scenes`.
