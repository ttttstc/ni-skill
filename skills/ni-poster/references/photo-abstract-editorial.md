# Photo Abstract Editorial

Use only when the Style Router selects **Photo Abstract Editorial**. This is an internal, non-verbatim adaptation of [`ZzzLc0405/photo-abstract-editorial`](https://github.com/ZzzLc0405/photo-abstract-editorial). Keep its clean photo-plus-panel grammar separate from Gathered Scenes' torn paper handoff and Scene Distillation's no-photo output.

## Core identity

Build a complete vertical editorial diptych:

`faithful original photograph → clean direct join → abstract memory panel → one poetic English title`

- treat the uploaded photo as the only content source;
- keep the photograph as the upper or principal section, with its content intact;
- derive the lower panel from the photograph's spatial, tonal, color, and rhythmic relationships;
- make the result feel like a restrained editorial artwork, not a filter, redraw, vector trace, or generic abstract poster.

This mode is defined by **photo truth plus clean ivory abstraction**. It does not use a torn seam, paper texture, collage shadow, mockup depth, or invented visual material.

## Photo Card

Inspect the supplied photo before compiling the prompt. Resolve three to six decisive facts:

- subject relationships, scale, position, and depth;
- horizontal/vertical axes, curves, direction, intervals, repetition, and overlap;
- light, tonal hierarchy, color roles, and negative space;
- the minimum identity cues needed for a distinctive subject.

The photo remains the factual source. Do not introduce another image, scene, object, symbol, or unsupported color.

## Photo area and adaptive join

- Keep the original photograph in the upper or principal region. Allow only proportional scaling or a slight crop needed for the composition; never redraw, extend, replace, retouch, stylize, or outpaint it.
- Use a vertical composition, but let the final canvas ratio follow the source photo and panel height rather than forcing equal halves or a fixed 3:5 ratio.
- For landscape or strongly horizontal photos, use roughly 38–52% photo / 48–62% panel.
- For vertical architecture, people, or tall subjects, use roughly 55–68% photo / 32–45% panel.
- For near-square or balanced photos, use roughly 48–58% photo / 42–52% panel. Shift by about 8% when the actual visual weight requires it.
- Join both sections directly and flat: no frame, shadow, tape, torn edge, curled corner, collage seam, or dimensional card.

## Abstract memory panel

Use a uniform, continuous neutral ivory panel, close to `#F3F0E8`. Reconstruct relationships rather than objects:

- preserve direction, density, hierarchy, rhythm, axes, gaps, and asymmetry;
- remove surface texture, perspective detail, background noise, and low-information decoration;
- make the first read a minimal abstract composition and the second read a residue of this particular photo;
- choose one primary mark family and no more than two supporting families: flat/organic masses, soft irregular forms, arcs, short bars or bands, simplified architectural masses, fine axes, small dots, or restrained human marks;
- every important mark must trace to a real spatial, tonal, or color fact in the photo;
- use relationships first and contours second: ordinary scenes, horizons, water, crowds, and light keep rhythm rather than full silhouettes; distinctive architecture keeps at most one to three identity cues; people become irregular continuous short vertical marks, never faces or limbs.

Keep the panel spacious: motif width about 30–42% of panel width, motif height normally no more than 28–34% of panel height, and about 65–80% clean whitespace. Let a supported horizontal subject extend farther while remaining low; keep compact organic groups gathered rather than scattering them.

## Color and title

- Extract all motif colors from the photo, lower saturation, and reduce the palette to one dominant role, one dark structural role, one light/neutral role, and at most one or two small accents.
- Do not add neon, unsupported complements, decorative color points, or a second visual source.
- Create one original English title of two to five words from a visible subject, spatial relation, light, time, movement, or mood. Avoid empty words such as `Memory`, `Dream`, and `Moment`, travel-copy language, and unrelated grand narratives.
- Put the title only on the ivory panel, below or beside the motif, in a restrained editorial serif. Use lower-left alignment or bottom-centering according to the panel's balance; never put it in the photo, lower-right corner, or on the edge.
- Add a three-to-seven-word subtitle only when it adds a new meaning layer. Return no title options, labels, dates, logos, signatures, or watermarks.

## Prompt and workflow

Compile four compact sections:

1. source photo fidelity, adaptive photo/panel proportions, and clean direct join;
2. spatial facts, semantic minimum, abstract motif, mark families, and whitespace;
3. ivory panel, source-derived muted palette, title text/placement, and editorial typography;
4. clean flat reproduction, emotional temperature, and hard avoids.

Workflow: inspect the photo, build the Photo Card, choose the adaptive split, select one source-derived motif grammar, reduce the palette, write one title, compile, generate with the supplied photo, and check that the photo remains faithful and the panel remains flat and clean. Regenerate at most once for one concrete observed failure.

## Output contract

By default return the generated image and one brief Chinese rationale covering the faithful photo, derived panel relationship, adaptive split, and title. Reveal the full prompt only when the user explicitly asks.

If generation fails, report the concrete failure and do not claim that the photograph was preserved. Return the compiled prompt only when requested.

## Hard avoids

No photo filter, redraw, scene reconstruction, outpainting, posterized photo, vector tracing, photo thumbnail in the panel, generic icon, invented material, unsupported color, gradient, lighting variation, paper grain, fibers, stains, scan marks, shadow, glow, vignette, torn-paper edge, tape, frame, collage artifact, mockup, equal mechanical split, dense decoration, full architectural detail, illustrated faces/limbs/clothing, commercial hierarchy, logo/CTA, glossy paper, 3D, cinematic lighting, neon, fashion drama, cute cartoon/anime, long text, title-option list, faux metadata, or watermark.

## Attribution

Adapted from [`ZzzLc0405/photo-abstract-editorial`](https://github.com/ZzzLc0405/photo-abstract-editorial). The upstream repository did not expose a LICENSE file at import time; this route is a non-verbatim internal adaptation and does not import upstream example assets.
