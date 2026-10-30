# hybrid-agent (sketchboard view, sketch theme)

Source: Jiaru Zou et al. (Stanford × Together AI), *Hybrid Reasoning Agents*, arXiv:2610.18861 — https://arxiv.org/abs/2610.18861 ;
post by @rohanpaul_ai https://x.com/rohanpaul_ai/status/2110417627608969646 . Figures: Table 1 (GAIA avg, 14B: 52.4 vs ARPO 43.7),
Table 9 (decoding compute 51.2–66.9 → 13.9–25.1 TFLOP, −62.5%~72.9%), §5 analysis (2.1× faster). Token chain and decoded text are illustrative.
Layout style after Avi Chawla / DailyDoseofDS explainer boards.

Fonts are not bundled: put `mali.ttf`, `mali-bold.ttf` (Mali, OFL) and `wenkai.ttf` (LXGW WenKai, OFL) in `examples/hybrid-agent/fonts/`;
without them the page falls back to the system CJK font.
