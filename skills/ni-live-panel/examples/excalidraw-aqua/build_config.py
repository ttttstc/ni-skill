#!/usr/bin/env python3
"""Build the AQuA (inner + outer loop) configs for the excalidraw view: 4:5 (X) and 3:4 (Xiaohongshu).
Recreation of the diagram in Google adk-recipes' Ambient Quality Agent README, made to move.
  python3 examples/excalidraw-aqua/build_config.py   -> config-4x5.json, config-3x4.json next to this file"""
import json
from pathlib import Path

HERE = Path(__file__).parent
# box fills sampled from the reference image: Excalidraw's pastels, a touch greyer
PASTEL = {"xblue": "#b8d3ec", "xgreen": "#bedcb9", "xyellow": "#f5e49e", "xred": "#ecbcb6", "xviolet": "#d3c6ef"}


def build(preset):
    tall = preset == "3:4"
    SH = 1330 if tall else 1250
    Y = (lambda y: round(28 + y * 1.04)) if tall else (lambda y: y)   # 3:4 has a little more height: stretch y

    def P(pts):
        return [[x, Y(y)] for x, y in pts]

    nodes = [
        dict(id="offline", t="offline\nevals", x=500, y=222, w=222, h=112, hue="green"),
        dict(id="evalset", t="eval set", x=800, y=405, w=222, h=96, hue="blue"),
        dict(id="coding", t="coding\nagent /\noptimizer", x=200, y=405, w=222, h=140, hue="yellow", size=34),
        dict(id="compare", t="compare\n+ deploy", x=500, y=592, w=226, h=112, hue="red"),
        dict(id="live", t="live\ntraffic", x=500, y=810, w=210, h=108, hue="blue"),
        dict(id="online", t="online\nevals", x=800, y=966, w=216, h=112, hue="violet"),
        dict(id="sweep", t="AQuA\nsweep", x=500, y=1122, w=216, h=108, hue="green"),
        dict(id="root", t="AQuA root\ncause", x=200, y=966, w=226, h=116, hue="yellow"),
    ]
    for n in nodes:
        n["y"] = Y(n["y"])
        n.setdefault("size", 38)

    def E(id, f, t, fs, ts, bend=0.25, fo=0, to=0, **kw):
        return dict(id=id, **{"from": f}, to=t, fromSide=fs, toSide=ts, bend=bend, fromOff=fo, toOff=to, **kw)

    edges = [
        E("e1", "evalset", "offline", "top", "right", 0.25, fo=-0.45),
        E("e2", "offline", "coding", "left", "top", 0.25),
        E("e3", "coding", "compare", "bottom", "left", 0.25),
        E("e4", "compare", "evalset", "right", "bottom", 0.25, to=-0.1),
        E("deploy", "compare", "live", "bottom", "top", 0, width=3.6, label="deploy", labelAt=[566, Y(707)]),
        E("e5", "live", "online", "right", "top", -0.25),
        E("e6", "online", "sweep", "bottom", "right", -0.25),
        E("e7", "sweep", "root", "left", "bottom", -0.25),
        E("d1", "online", "evalset", "top", "bottom", 0.17, fo=0.72, to=0.72, dashed=True,
          label="failing transcripts\nseed evals", labelAt=[908, Y(712)], labelAlign="right"),
        E("d2", "root", "coding", "top", "bottom", -0.17, fo=-0.72, to=-0.72, dashed=True,
          label="root causes, evidence\n& raw traces", labelAt=[72, Y(712)], labelAlign="left"),
    ]
    AT = {  # where each box's handwritten note goes: next to it, in free space
        "compare": ([500, Y(488)], "center"), "evalset": ([846, Y(312)], "center"), "offline": ([640, Y(156)], "left"),
        "coding": ([338, Y(454)], "left"), "live": ([500, Y(910)], "center"), "online": ([692, Y(897)], "right"),
        "sweep": ([500, Y(1024)], "center"), "root": ([140, Y(870)], "left"),
    }
    steps = [  # starts on the failed compare, so the first frame (the X cover) reads "not better yet"
        ("compare", "e4", "not better yet", 1.5),
        ("evalset", "e1", "run it again", 1),
        ("offline", "e2", "scoring offline…", 1),
        ("coding", "e3", "trying another fix", 1),
        ("compare", "deploy", "better → ship it", 1.5),
        ("live", "e5", "real users, 24/7", 1),
        ("online", "e6", "reviewing sessions", 1),
        ("sweep", "e7", "grouping failures", 1),
        ("root", "d2", "root cause found", 1),
        ("coding", "e3", "applying the fix", 1),
        ("compare", "deploy", "better → ship it", 1.5),
        ("live", "e5", "real users, 24/7", 1),
        ("online", "d1", "a failing transcript!", 1),
        ("evalset", "e1", "new eval case", 1),
        ("offline", "e2", "scoring offline…", 1),
        ("coding", "e3", "patching the agent", 1),
    ]
    view = {
        "type": "view", "kind": "excalidraw", "space": [1000, SH], "period": 32, "t0": 1.55, "seed": 11,
        "boil": {"step": 0.125, "variants": 4, "amp": 0.5}, "noteSize": 30, "roughness": 1.05, "strokeWidth": 2.6,
        "edgeRough": 0.8, "edgeMulti": False,
        "zones": [  # pale washes: inner loop (top) vs outer loop (bottom)
            {"x": 34, "y": Y(132), "w": 932, "h": Y(680) - Y(132), "fill": "#f1f6fc", "r": 40},
            {"x": 34, "y": Y(744), "w": 932, "h": Y(1204) - Y(744), "fill": "#f1f7ef", "r": 40},
        ],
        "texts": [
            {"t": "Ambient Quality Agent (AQuA)", "x": 500, "y": Y(64), "size": 56, "c": "ink", "weight": 0.8,
             "underline": {"hue": "yellow", "width": 16, "dy": 20, "tilt": -4}},
            {"t": "INNER LOOP:\nBuild & Test\n(local / CI)", "x": 140, "y": Y(200), "size": 28, "c": "slate"},
            {"t": "OUTER LOOP:\nShip, Monitor & Learn\n(24/7 in production)", "x": 940, "y": Y(1153), "size": 22, "c": "sage", "align": "right"},
        ],
        "icons": [{"kind": "laptop", "x": 500, "y": Y(372), "w": 112}, {"kind": "cloud", "x": 500, "y": Y(966), "w": 150}],
        "nodes": nodes, "edges": edges,
        "steps": [dict({"node": n, "edge": e, "note": t, "at": AT[n][0], "align": AT[n][1], "dur": d}, **({"dwell": 0.62} if i == 0 else {}))
                  for i, (n, e, t, d) in enumerate(steps)],
    }
    cw, ch = (1080, 1440) if tall else (1200, 1500)
    return {
        "meta": {"title": "AQuA inner + outer loop (excalidraw view)", "lang": "en"},
        "canvas": {"preset": preset, "duration": 32, "fps": 30},
        "theme": {"preset": "light-pastel", "font": 'Excalifont, Xiaolai, "Noto Sans CJK SC", sans-serif',
                  "fonts": [{"family": "Excalifont", "src": "Excalifont-Regular-Latin.woff2", "weight": "400"}],
                  "colors": {"bg": "#ffffff", "muted": "#5c636b", **PASTEL}},
        "credit": {"text": "after Google adk-recipes AQuA diagram, via @Saboo_Shubham_ · https://github.com/google/adk-recipes/tree/main/core/python/ambient-quality-agent\n"
                           "https://x.com/Saboo_Shubham_/status/2112428713979900248 · recreation, motion illustrative · made with live-panel (excalidraw view)",
                   "y": ch - 28, "size": 12.5, "lh": 16, "c": "#868e96", "font": '"Noto Sans CJK SC", sans-serif'},
        "elements": [view],
    }


if __name__ == "__main__":
    for preset, name in (("4:5", "config-4x5.json"), ("3:4", "config-3x4.json")):
        (HERE / name).write_text(json.dumps(build(preset), ensure_ascii=False, indent=1), encoding="utf-8")
        print("wrote", HERE / name)
