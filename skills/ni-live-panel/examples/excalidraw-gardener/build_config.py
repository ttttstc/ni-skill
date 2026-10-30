#!/usr/bin/env python3
"""园丁 loop in the excalidraw view (Chinese): 4:5 (X) and 3:4 (小红书).
Content and figures from the gardener README (https://github.com/ythx-101/gardener-loop, the author's own loop):
B 段最佳候选规则 30 题 10% -> 57%（没过 75% 线，一条没提）；C 段「审美」攒到 5 次后作者提前批准固化。
  python3 examples/excalidraw-gardener/build_config.py   -> config-4x5.json, config-3x4.json"""
import json
from pathlib import Path

HERE = Path(__file__).parent
# box fills sampled from the AQuA reference image: Excalidraw's pastels, a touch greyer
PASTEL = {"xblue": "#b8d3ec", "xgreen": "#bedcb9", "xyellow": "#f5e49e", "xred": "#ecbcb6", "xviolet": "#d3c6ef"}


def build(preset):
    tall = preset == "3:4"
    SH = 1330 if tall else 1250
    Y = (lambda y: round(28 + y * 1.04)) if tall else (lambda y: y)

    def P(pts):
        return [[x, Y(y)] for x, y in pts]

    nodes = [
        dict(id="daily", t="每日复盘", sub="读完昨天全部对话", x=500, y=250, w=300, h=116, hue="blue", size=42, subSize=24),
        dict(id="A", t="A 成果", sub="每天最多 3 条", x=200, y=470, w=236, h=118, hue="green"),
        dict(id="B", t="B 失败模式", sub="被纠正、返工", x=500, y=470, w=250, h=118, hue="red"),
        dict(id="C", t="C 成功模式", sub="被夸、被拿去发", x=800, y=470, w=236, h=118, hue="yellow"),
        dict(id="test", focusOff=15, t="loop 机实测", sub="合格率至少 75%\n且比无规则高 25 点", x=500, y=720, w=330, h=150, hue="blue"),
        dict(id="count", t="攒次数", sub="满 2 次：待固化\n满 6 次：已固化", x=830, y=720, w=250, h=150, hue="yellow"),
        dict(id="nod", t="青月点头", sub="人是闸门", x=680, y=952, w=250, h=112, hue="violet", size=40),
        dict(id="rule", t="写进常驻规矩", x=330, y=1132, w=300, h=100, hue="green", size=40),
    ]
    for n in nodes:
        n["y"] = Y(n["y"])
        n.setdefault("size", 36)
        n.setdefault("subSize", 26); n.setdefault("subC", "#3b4248")

    def E(id, f, t, fs, ts, bend=0.0, fo=0, to=0, **kw):
        return dict(id=id, **{"from": f}, to=t, fromSide=fs, toSide=ts, bend=bend, fromOff=fo, toOff=to, **kw)

    edges = [
        E("dA", "daily", "A", "bottom", "top", 0.08, fo=-0.62),
        E("dB", "daily", "B", "bottom", "top"),
        E("dC", "daily", "C", "bottom", "top", -0.08, fo=0.62),
        E("Bt", "B", "test", "bottom", "top", gap=30),
        E("Cc", "C", "count", "bottom", "top", 0, fo=0.25),
        E("tn", "test", "nod", "bottom", "top", 0.12, fo=0.45, to=-0.5),
        E("cn", "count", "nod", "bottom", "top", -0.12, fo=-0.4, to=0.5),
        E("nr", "nod", "rule", "left", "top", 0.22),
        dict(id="back", **{"from": "rule"}, to="daily", dashed=True,
             pts=P([[158, 1136], [66, 1088], [40, 760], [44, 430], [120, 276], [328, 250]]), width=4,
             label="第二天\n继续积累", labelAt=[84, Y(964)], labelAlign="left", labelSize=28),
    ]
    steps = [
        ("daily", "dA", "读完昨天的对话", [500, Y(152)], "center"),
        ("daily", "dB", "记下被纠正的地方", [500, Y(152)], "center"),
        ("B", "Bt", "满 2 次才写候选规则", [482, Y(588)], "right"),
        ("test", None, "还差 18 个点", [408, Y(842)], "center"),
        ("daily", "dC", "记下被夸的地方", [500, Y(152)], "center"),
        ("C", "Cc", "按底层原则归类", [800, Y(592)], "right"),
        ("count", "cn", "审美攒到 5 次", [990, Y(842)], "right"),
        ("nod", "nr", "提前批准固化", [830, Y(952)], "left"),
        ("rule", "back", "明天开工就读", [504, Y(1134)], "left"),
    ]
    view = {
        "type": "view", "kind": "excalidraw", "space": [1000, SH], "period": 22.5, "t0": 8.7, "seed": 5,
        "boil": {"step": 0.125, "variants": 4, "amp": 0.5}, "noteSize": 29, "roughness": 1.05, "strokeWidth": 2.6,
        "edgeRough": 0.8, "edgeMulti": False,
        "zones": [  # pale washes: the daily review (top) vs the cross-day verify -> nod -> rule loop (bottom)
            {"x": 72, "y": Y(132), "w": 918, "h": Y(566) - Y(132), "fill": "#f1f6fc", "r": 40},
            {"x": 72, "y": Y(598), "w": 918, "h": Y(1204) - Y(598), "fill": "#f1f7ef", "r": 40},
        ],
        "texts": [
            {"t": "园丁 loop · 让 AI 每天复盘一次自己", "x": 500, "y": Y(62), "size": 50, "c": "ink", "weight": 0.6,
             "underline": {"hue": "yellow", "width": 16, "dy": 22, "tilt": -4}},
            {"t": "每天早上\n复盘昨天", "x": 134, "y": Y(186), "size": 28, "c": "slate"},
            {"t": "实测 · B 段 30 题", "x": 184, "y": Y(664), "size": 22, "c": "red"},
            {"t": "10% → 57%", "x": 184, "y": Y(712), "size": 36, "c": "red", "weight": 0.7},
            {"t": "未达 75% · 0 条入规", "x": 184, "y": Y(762), "size": 22, "c": "red"},
        ],
        "icons": [{"kind": "sprout", "x": 900, "y": Y(1092), "w": 92}, {"kind": "server", "x": 404, "y": Y(560), "w": 0}],
        "nodes": nodes, "edges": edges,
        "steps": [{"node": n, "edge": e, "note": t, "at": at, "align": al} for n, e, t, at, al in steps],
    }
    view["icons"] = [i for i in view["icons"] if i.get("w")]
    ch = 1440 if tall else 1500
    return {
        "meta": {"title": "园丁 loop（excalidraw 主题）", "lang": "zh-CN"},
        "canvas": {"preset": preset, "duration": 22.5, "fps": 30},
        "theme": {"preset": "light-pastel", "font": 'Excalifont, Xiaolai, "Noto Sans CJK SC", sans-serif',
                  "fonts": [{"family": "Excalifont", "src": "Excalifont-Regular-Latin.woff2", "weight": "400"},
                            {"family": "Xiaolai", "src": "Xiaolai-Regular.ttf", "weight": "400"}],
                  "colors": {"bg": "#ffffff", "muted": "#5c636b", **PASTEL}},
        "credit": {"text": "数据：园丁 README（B 段最佳候选 30 题 10%→57%，作者 loop 机实测；C 段「审美」攒到 5 次后作者提前批准）\n"
                           "门槛 2 / 6 次借自胡海岚团队 Science 2017 · 动效为示意 · https://github.com/ythx-101/gardener-loop · live-panel excalidraw 主题",
                   "y": ch - 28, "size": 12.5, "lh": 16, "c": "#868e96", "font": '"Noto Sans CJK SC", sans-serif'},
        "elements": [view],
    }


if __name__ == "__main__":
    for preset, name in (("4:5", "config-4x5.json"), ("3:4", "config-3x4.json")):
        (HERE / name).write_text(json.dumps(build(preset), ensure_ascii=False, indent=1), encoding="utf-8")
        print("wrote", HERE / name)
