# verify_view.py — feature map (验收器功能地图)

`scripts/verify_view.py` is the acceptance gate for views (`{"type":"view"}` elements, see `references/views.md`).
A view is accepted only when this command exits 0. Taste is not checked here: that is the job of an adversarial
reviewer who looks at the screenshots it writes.

```bash
CHROME=$(command -v chromium || find / -name chrome-headless-shell -type f 2>/dev/null | head -1)
python3 scripts/verify_view.py --config examples/<kind>/config.json --chrome "$CHROME" --out /tmp/vv-<kind>   # all 6 combos
python3 scripts/verify_view.py --config ... --quick        # only 4:5 x light-pastel, for fast iteration
python3 scripts/verify_view.py --config ... --combos cur   # the config exactly as written
python3 scripts/verify_view.py --config ... --json         # JSON report on stdout (summary still on stderr)
```

Output: `<out>/<canvas>_<theme>/{config.json,shot_1.png,shot_2.png,shot_3.png}` and `<out>/report.json`.

| check | what it guarantees | typical failure message | fix |
| --- | --- | --- | --- |
| combos | the same config works at 4:5, 3:4, 1:1 and in terminal-dark and light-pastel (theme colour overrides are removed so the theme really switches) | any failure below, per combo | derive sizes from the rect (rule R8), use theme colour names only (R9) |
| schema | the view kind exists and has its required data (`nodes/edges`, `lanes/events`, non-increasing funnel `stages`, `root`, 3–8 ring `steps`, `cards`) | `stages[3].value=500 > stages[2].value=480` | fix the data, not the checker |
| check_frames | no text overflow / overlap / text over a foreign box / box overlap over ~60 sampled times, replay is byte-identical after seeking away, no page error | `text overlap: "生成补丁" x "Patched"` | `ctx.fit`, more spacing, hide minor labels by rule (R3, R14) |
| contrast | WCAG contrast of every marked text against its effective background: ≥ 4.5, or ≥ 3 for ≥ 20 px | `contrast 2.17 < 3 for text '390' (#5fbdb2 on #fcfcfb)` | text in `fg`/`dim`, colour carried by a swatch or bar instead (R4) |
| fill | the content of each view covers ≥ 70 % of its rect width and ≥ 60 % of its height, with balanced left/right margins | `fill: width 54% < 70%` | scale the layout to the rect (R7) |
| edges | sampled points of every `mark(...,'edge')` path stay out of every `mark(...,'box')` other than the two it connects | `edge #4 passes through box '工具'` | route around cards, end on borders (R5) |
| flicker | in an 8 s window sampled every 0.1 s, no marked node toggles visibility/colour twice within 0.4 s | `flicker: node 17 changes 0.2 s apart` | slower highlight, ≥ 0.8 s holds (R6) |
| views present | a config with view elements actually renders a `[data-view]` root | `unknown view kind "funnel"` | the `assets/views/<kind>.js` file must exist and parse (`node --check`) |

Known blind spots: beauty, hierarchy and motion quality (reviewer only); contrast over gradients or images is
approximate (the nearest opaque background is used); flicker looks at one 8 s window; packets and particles are
not marked and therefore not checked.

Proven on real output: the first draft of a funnel view was rejected for 7 label overlaps, 6 percentage pills
over a box and 5 value labels below 3:1 contrast — all real defects visible in its screenshot.
