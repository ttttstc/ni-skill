# View rules (园丁规则 — every weed you pull becomes a rule)

Each rule came from a real failure (or a known failure of the original engine). Rules marked
**[lint]** are enforced by `scripts/verify_view.py`; the rest are enforced by review.
Append new rules at the bottom with the failure that produced them.

R1 [lint] Determinism: no Math.random / Date / performance.now / CSS animation or transition / requestAnimationFrame in a view. Seeded `ctx.hash` only.
R2 [lint] Never create or remove DOM nodes in `seek`; create everything in `build`, then toggle styles.
R3 [lint] Every text node is `mark`ed 'text' and stays inside its 'box'/'frame' and the canvas; use `ctx.fit` for every label (CJK labels are ~2x wider than Latin).
R4 [lint] Contrast ≥ 4.5 (≥ 3 for ≥20px). `dim` text on an accent fill usually fails — use `fg`.
R5 [lint] Connectors (`mark` 'edge') end on card borders and never cross another card.
R6 [lint] No toggle faster than 0.4 s; highlights last ≥ 0.8 s.
R7 [lint] Content fills ≥70% of rect width and ≥60% of height, balanced left/right margins.
R8 Derive every size from rect (`u = Math.min(w,h)/100`); a constant tuned on 4:5 breaks 1:1.
R9 Only theme colour names (acc1..6, accf1..6, fg, muted, dim, panel, grid, ok, warn, bad, bg, line, line2); no hex in view code.
R10 Numbers shown twice come from one variable (one truth); simulated numbers are labelled illustrative in `credit`.
R11 Seamless loop: every sub-period divides `period` (and canvas.duration is a multiple of `period`), so seek(0) and seek(duration) look the same. (from senior review, 20:58)
R12 Frame 0 is a cover: at t=0 there is already one highlighted focus and no "not started yet" empty state (platforms use the first frame as thumbnail).
R13 Number text changes at most every 0.4 s and keeps its width (pad / tabular figures) so it does not jitter.
R14 Data completeness: at most 20% of labels may be hidden/ellipsized, and every data item in the config has a drawn node — never pass the overlap check by dropping data.
R15 Calm frames: at any time at most ~30% of elements are highlighted and at most 4 accent colours are prominent; exactly one focus.
R16 Per-view key decisions — nebula: place cluster centres first (ellipse/grid by group), force layout only inside clusters, greedy label placement by weight. timeline: one `playhead(t)` derives done/active/pending, fills and counters; the wrap-around must not flash. funnel: honest linear widths with a minimum readable width; labels in a fixed column outside the shapes. tree: choose orientation once in build from leaf count and rect aspect; node size from the most crowded level; collapsed state must still pass contrast. ring: comet angle is the single truth (current step = floor(angle/step), lap = floor(t/lapPeriod)); labels outside the ring, aligned by quadrant. kpi: the big number is the series interpolated at the cursor and delta comes from the same series; cursors of different cards are phase-shifted, never all in sync. loop: the walks are the single truth (hop = period / total hops, round = index of the current walk, `canvas.duration` a multiple of `period`); the focus has no gaps (source until mid-edge, then target, crossfaded); loop-back semantics follow the final `dashed` flag, never the Yes/No kind.
R17 [lint] Secondary text uses `muted`, not `dim`: light-pastel `dim` (#7b828c) is only 3.78:1 on its background and cannot be changed without altering the legacy examples, so the core added `muted` (#5f6670 light, #949db0 dark, ≥4.5:1 on bg and panel). (from the ring draft: 5 descriptions failed contrast, 21:25)

R18 [loop] The loop view defaults to ambient: the whole graph moves at once and any two adjacent frames differ in at least 6 places (flow packets on every forward edge, marching loop-back dashes, a small motion per icon; cards and frames stay still, no colour flashes). The single-focus walk is an optional, weakened overlay (`motion:"ambient+walk"`, `period` a multiple of `ambientPeriod`); R15's "exactly one focus" applies to the walk only. Packets are moving objects, not toggles, so R6 does not count them.
R19 [loop] Ambient actions use easing and an action window (a fraction of `ambientPeriod`, phases staggered by node order); delivery feedback (ripple, lift) is a smooth bump of >= 0.8 s, once per node per period, and the same element is never highlighted twice within 0.4 s.
