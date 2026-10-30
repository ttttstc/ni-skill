#!/usr/bin/env python3
"""Build a complete, valid live-panel config from a short spec, so you never type a 20-40 KB config by hand.

  python3 scripts/scaffold.py --spec spec.json --out out/config.json
  python3 scripts/scaffold.py --example > spec.json      # print a starter spec

The spec is a few lines of JSON: what the boxes say, not where they go. The script does the layout
(rows of boxes top to bottom, wires with packets between rows, an optional side rail of on-call triggers,
a scrolling log, a status line, a footnote and the credit), wraps text to fit the boxes, and writes a
config that already passes check_frames.py in the common cases. Then edit the output in small steps.

Spec keys (all optional except rows):
  theme      "terminal-dark" | "light-pastel"           (default terminal-dark)
  canvas     "4:5" (X) | "3:4" (Xiaohongshu) | "1:1"    (default 4:5)
  lang       "en" | "zh"
  title      headline text;  titlebar: terminal title-bar text (dark only)
  rows       list of rows, top to bottom; each row is a list of 1-5 boxes (a line may show a counter: "{tokens} tokens"):
             {"name": "...", "lines": ["...", ...], "color": "cy",
              "lane":  {"busy": "running", "done": ["done", "tests pass"], "log": ["edited src/a.ts", ...]},
              "gauge": {"label": "p95", "values": [0.31, 0.42, 0.78, ...], "threshold": 0.6,
                        "above": "slow", "below": "ok", "bad": "above", "log": ["routing", ...]}}
             gauge values are fractions 0-1: they are both the bar length and the number shown.
  steps      true = one shared cycle lights the boxes one at a time, row by row (default: true on light-pastel)
  rail       {"name": "ON CALL", "side": "left"|"right", "sub": "on demand",
              "items": [{"name": "tests fail twice", "adv": ["» line 1", "» line 2"], "row": 1}, ...]}
             "row" = index of the row the trigger points at (default: spread over the rows)
  counters   [{"id": "tokens", "label": "tokens", "start": 120000, "rate": 850, "suffix": ""}, ...]  -> status line
  log        {"title": "session log", "rows": 4}   (set "log": false for no log)
  note       footnote on screen, e.g. "numbers are illustrative" / "数字为示意"
  credit     credit/source line: original author handle + full link, or the data source
"""
import argparse, json, math, os, re, sys, unicodedata

CANVAS = {"4:5": (1200, 1500), "3:4": (1080, 1440), "1:1": (1080, 1080)}
DARK_COLORS = ["cy", "bl", "gr", "pu", "ye"]
LIGHT_COLORS = [("bl", "blf", "blt"), ("gn", "gnf", "ink"), ("or", "orf", "ort"), ("pu", "puf", "put"),
                ("tl", "tlf", "ink"), ("rd", "rdf", "rdt"), ("yl", "ylf", "ink")]

EXAMPLE = {
    "theme": "terminal-dark", "canvas": "4:5", "lang": "en",
    "title": "AGENT TREE · LIVE", "titlebar": "~/agents — zsh",
    "rows": [
        [{"name": "Planner · main", "lines": ["splits the task", "hands out work"]}],
        [{"name": "coder", "lines": ["writes code"], "lane": {"busy": "running", "done": ["done"], "log": ["edited src/auth.ts"]}},
         {"name": "tester", "lines": ["runs tests"], "lane": {"busy": "running", "done": ["green"], "log": ["42 tests pass"]}},
         {"name": "writer", "lines": ["writes docs"], "lane": {"busy": "running", "done": ["done"], "log": ["README updated"]}}],
        [{"name": "Reviewer", "lines": ["merges the results"]}]
    ],
    "rail": {"name": "ON CALL", "sub": "woken on demand", "side": "left",
             "items": [{"name": "tests fail twice", "adv": ["» wrong fixture,", "» not the code"]},
                       {"name": "context nearly full", "adv": ["» compact first", "» then continue"]},
                       {"name": "before delivery", "adv": ["» run full suite", "» then ship"]}]},
    "counters": [{"id": "tokens", "label": "tokens", "start": 128400, "rate": 730}],
    "log": {"title": "session log", "rows": 4},
    "note": "all numbers are illustrative",
    "credit": "made with live-panel · numbers simulated"
}


def is_wide(ch):
    return unicodedata.east_asian_width(ch) in ("W", "F")


class Metrics:
    def __init__(self, dark, size):
        self.dark, self.size = dark, size
        self.lat, self.cjk = (0.6, 1.2) if dark else (0.6, 1.0)  # light: proportional sans, be generous

    def w(self, s, size=None):
        size = size or self.size
        return sum((self.cjk if is_wide(c) else self.lat) for c in str(s)) * size

    def wrap(self, s, width, size=None):
        s = str(s)
        if self.w(s, size) <= width:
            return [s]
        out, cur = [], ""
        tokens = re.findall(r"[A-Za-z0-9_./:@#%+\-]+|\s+|.", s)
        for tok in tokens:
            if self.w(cur + tok, size) <= width:
                cur += tok
            else:
                if cur.strip():
                    out.append(cur.rstrip())
                cur = tok.lstrip()
                while self.w(cur, size) > width:  # a single token longer than the line
                    k = len(cur)
                    while k > 1 and self.w(cur[:k], size) > width:
                        k -= 1
                    out.append(cur[:k]); cur = cur[k:]
        if cur.strip():
            out.append(cur.rstrip())
        return out or [""]

    def clip(self, s, width, size=None):
        s = str(s)
        if self.w(s, size) <= width:
            return s
        while s and self.w(s + "…", size) > width:
            s = s[:-1]
        return s + "…"


def build(spec):
    theme = spec.get("theme", "terminal-dark")
    dark = theme != "light-pastel"
    preset = spec.get("canvas", "4:5")
    W, H = CANVAS[preset]
    FS, LH = (21, 30) if dark else (17, 24)
    if W < 1200 and dark:
        FS, LH = 19, 28
    M = Metrics(dark, FS)
    steps = spec.get("steps", not dark)
    rows = spec.get("rows") or []
    if not rows:
        sys.exit("spec needs at least one row of boxes")
    rows = [r if isinstance(r, list) else [r] for r in rows]

    cfg = {"meta": {"title": spec.get("title", "live panel"), "lang": spec.get("lang", "en")},
           "canvas": {"preset": preset, "duration": 30, "fps": 30, "preroll": 12 if dark else 0},
           "theme": {"preset": theme, "fontSize": FS, "lineHeight": LH},
           "machines": {}, "elements": []}
    if dark:
        cfg["theme"]["colors"] = {"mute": "#aab1c0", "rd": "#f07178"}
        cfg["clock"] = {"start": "23:48:04", "rate": 3}
    E, MC = cfg["elements"], cfg["machines"]
    # ids the caller chose (counters) are reserved up front; derived ids never take them
    reserved = {str(c.get("id")) for c in (spec.get("counters") or []) if c.get("id")}

    def fresh(base):
        while base in MC or base in reserved:
            base += "x"
        reserved.add(base)
        return base
    margin = 40

    # ---- header ----
    top = 0
    if dark and spec.get("titlebar", True) is not False:
        cfg["titlebar"] = {"text": spec.get("titlebar") or "~/live-panel — zsh"}
        top = 44
    title = spec.get("title")
    if title:
        tsize = FS + 3 if dark else 34
        tsize = min(tsize, int((W - 2 * margin) / max(1, M.w(title, 1))))
        ty = top + (40 if dark else 70)
        E.append({"type": "text", "x": 0, "w": W, "y": ty, "align": "center", "size": tsize,
                  "c": "wh" if dark else "ink", "b": 1, "t": title})
        if dark:
            E.append({"type": "rule", "x": 34, "y": ty + 28, "w": W - 68})
        top = ty + (52 if dark else 60)
    else:
        top += 30

    # ---- footer (bottom up): credit, note, status, log ----
    bottom = H
    credit = spec.get("credit")
    csize = 12 if dark else 12
    if credit:
        cw = (W - 2 * 24) * 0.96
        while csize > 9 and M.w(credit, csize) > cw:
            csize -= 0.5
        if M.w(credit, csize) > cw:
            sys.stderr.write("warning: credit line is too long for one line even at 9 px; shorten it\n")
        cfg["credit"] = {"text": credit, "y": H - 16, "size": csize}
        bottom = H - 34
    note = spec.get("note")
    if note:
        nsize = 13 if dark else 13
        note = M.clip(note, W - 80, nsize)
        E.append({"type": "text", "x": 0, "w": W, "y": bottom - 10, "align": "center", "size": nsize, "c": "dim", "t": note})
        bottom -= 28
    counters = spec.get("counters") or []
    if counters:
        runs = []
        for k, c in enumerate(counters):
            cid = c.get("id") or f"n{k}"
            MC[cid] = {"type": "counter", "start": c.get("start", 1000), "rate": c.get("rate", 10), "format": "comma"}
            if c.get("prefix"): MC[cid]["prefix"] = c["prefix"]
            if c.get("suffix"): MC[cid]["suffix"] = c["suffix"]
            runs += [{"t": ("   " if k else "") + c.get("label", cid) + " ", "c": "dim"},
                     {"t": "[", "c": "gr" if dark else "bl", "b": 1}, {"v": cid, "c": "gr" if dark else "bl", "b": 1},
                     {"t": "]", "c": "gr" if dark else "bl", "b": 1}]
        E.append({"type": "text", "x": 34, "w": W - 68, "y": bottom - 14, "runs": runs, "_counters": True})
        bottom -= 40
    logspec = spec.get("log", {"title": "log", "rows": 4})
    log_el = None
    if logspec:
        lrows = logspec.get("rows", 4 if H > 1100 else 3)
        lh = lrows * LH + 29
        ly = bottom - lh - 6
        log_el = {"type": "log", "x": margin, "y": ly, "w": W - 2 * margin, "rows": lrows, "padTop": 16, "padBottom": 29,
                  "padLeft": 20, "title": logspec.get("title", "log"), "titleX": 38,
                  "titleW": int(M.w(logspec.get("title", "log")) + 40),
                  "cols": [{"key": "time", "x": 0}, {"key": "who", "x": int(M.w("00:00:00 ") + 10)},
                           {"key": "m", "x": 0}, {"key": "g", "x": 0}]}
        bottom = ly - 34

    # ---- rail ----
    rail = spec.get("rail")
    x0, x1 = margin, W - margin
    rail_x = None
    if rail and rail.get("items"):
        rw = int(W * (0.27 if W >= 1200 else 0.29))
        if rail.get("side", "left") == "right":
            rail_x = W - margin - rw; x1 = rail_x - 44
        else:
            rail_x = margin; x0 = margin + rw + 44

    # ---- rows of boxes: measure ----
    TW = x1 - x0
    gapx = 22 if dark else 26
    pad_t, pad_x = (13, 14)
    built = []  # per row: list of dicts
    color_i = 0
    for r, row in enumerate(rows):
        k = len(row)
        bw = (TW - (k - 1) * gapx) / k if k > 1 else min(TW, max(TW * 0.62, 0))
        if k == 1:
            need = max([M.w(row[0].get("name", ""), FS)] + [M.w(l, FS) for l in row[0].get("lines", [])]) + 2 * pad_x + 10
            bw = max(min(TW, need), min(TW, TW * 0.5))
        brow = []
        for j, b in enumerate(row):
            inner = bw - 2 * pad_x - 6
            if dark:
                col = b.get("color") or (DARK_COLORS[0] if (len(rows) > 1 and (r == 0 or r == len(rows) - 1) and k == 1) else DARK_COLORS[1 + (color_i % 4)])
                fill = None; tcol = col
            else:
                pal = LIGHT_COLORS[color_i % len(LIGHT_COLORS)]
                col, fill, tcol = b.get("color") or pal[0], pal[1], pal[2]
            color_i += 1
            lines = []
            nsz = FS
            for nl in M.wrap(b.get("name", ""), inner, nsz):
                nlo = {"t": nl, "c": tcol if not dark else (col if k == 1 else "fg"), "b": 1}
                lines.append(nlo)
            for ln in b.get("lines", []):
                for wl in M.wrap(ln, inner):
                    lines.append({"t": wl, "c": "mute" if dark else "fg"})
            bid = re.sub(r"\W+", "", (b.get("id") or b.get("name") or f"b{r}{j}").lower())[:12] or f"b{r}{j}"
            bid = f"r{r}{j}_{bid}" if not re.match(r"^[a-z_]", bid) else bid
            bid = fresh(bid)
            g = b.get("gauge")
            if g:
                gid = fresh(bid + "_g")
                bad_above = g.get("bad", "above") == "above"
                vals = [max(0.02, min(0.99, float(v))) for v in (g.get("values") or [0.32, 0.41, 0.55, 0.38, 0.81, 0.47])]
                th = float(g.get("threshold", 0.6))
                MC[gid] = {"type": "gauge", "values": vals, "threshold": th, "period": round(3.4 + 0.7 * len(built) + 0.4 * j, 1),
                           "t0": round(0.5 + 0.9 * j, 1), "seed": 11 + 13 * (r * 5 + j), "decimals": g.get("decimals", 2),
                           "high": {"label": g.get("above", "high"), "dest": ""}, "low": {"label": g.get("below", "ok"), "dest": ""},
                           "highColor": ("rd" if dark else "rdt") if bad_above else ("gr" if dark else "gn"),
                           "lowColor": ("gr" if dark else "gn") if bad_above else ("rd" if dark else "rdt")}
                gl = g.get("log") or [b.get("name", gid)]
                MC[gid]["log"] = {"who": M.clip(b.get("name", gid), 140, FS).lower(), "c": col if dark else tcol,
                                  "msgs": gl, "tail": "{value} {label}"}
                hi_c = MC[gid]["highColor"]; lo_c = MC[gid]["lowColor"]
                labw = M.w(g.get("label", ""), FS) + 10 if g.get("label") else 0
                valw = M.w("0." + "0" * int(g.get("decimals", 2)), FS) + 14
                val_run = {"runs": [{"v": gid, "c": "fg" if dark else "ink"}]}
                # size the row to the box: label | bar | value on one line only when all three fit,
                # else the label goes on its own line, else the value too (narrow 1:1 boxes)
                if inner - labw - valw >= 40 + 10:
                    lab_inline, val_inline, barw = True, True, min(220, inner - labw - valw - 10)
                elif inner - valw >= 24 + 10:
                    lab_inline, val_inline, barw = False, True, min(220, inner - valw - 10)
                else:
                    lab_inline, val_inline, barw = False, False, max(16, min(220, inner - 10))
                if labw and not lab_inline:
                    lines.append({"runs": [{"t": M.clip(g.get("label"), inner, FS), "c": "dim"}]})
                items = []
                if labw and lab_inline:
                    items.append({"w": int(labw), "runs": [{"t": g.get("label"), "c": "dim"}]})
                items.append({"w": int(barw + 10), "bar": {"gauge": gid, "w": int(barw), "h": 16, "high": hi_c, "low": lo_c}})
                if val_inline:
                    items.append(val_run)
                lines.append({"items": items, "align": "left"})
                if not val_inline:
                    lines.append(val_run)
                lines.append({"runs": [{"t": "→ ", "c": "dim"}, {"v": gid + ".label"}]})
            ln_ = b.get("lane")
            if ln_:
                lid = fresh(bid + "_l")
                per = 7 + 1.0 * (j % 3) + 0.5 * r
                MC[lid] = {"type": "lane", "period": per, "run": round(per * 0.68, 1), "off": round(0.7 * j + 0.3 * r, 1),
                           "busy": ln_.get("busy", "running"), "done": ln_.get("done", ["done"]), "phase": j}
                if not dark:
                    MC[lid].update({"busyColor": "blt", "doneColor": "gn"})
                MC[lid]["log"] = {"who": M.clip(b.get("name", lid), 140, FS).lower(), "c": col if dark else tcol,
                                  "msgs": [[m, ""] for m in (ln_.get("log") or [ln_.get("done", ["done"])[0]])]}
                lines.append({"runs": [{"v": lid}]})
            h = pad_t + len(lines) * LH + 12
            brow.append({"id": bid, "w": bw, "h": h, "color": col, "fill": fill, "lines": lines, "tcol": tcol})
        built.append(brow)

    # ---- vertical layout ----
    avail_top, avail_bot = top + 10, bottom
    heights = [max(b["h"] for b in row) for row in built]
    n = len(built)
    total = sum(heights)
    gap = (avail_bot - avail_top - total) / max(1, n - 1) if n > 1 else 0
    gap = max(56, min(gap, 230))
    used = total + gap * (n - 1)
    if used > avail_bot - avail_top:
        sys.stderr.write(f"warning: boxes need {int(used)} px but only {int(avail_bot-avail_top)} px are free; "
                         "shorten lines, drop the note/counters, or use fewer log rows\n")
    y = avail_top + max(0, (avail_bot - avail_top - used) / 2)
    order = []
    for r, row in enumerate(built):
        k = len(row)
        rowh = heights[r]
        roww = sum(b["w"] for b in row) + gapx * (k - 1)
        x = x0 + (TW - roww) / 2
        for b in row:
            b["x"], b["y"] = round(x), round(y)
            b["h"] = rowh
            b["cx"] = round(x + b["w"] / 2)
            x += b["w"] + gapx
            order.append(b)
        y += rowh + gap

    if steps:
        vals = [{"t": b["lines"][0]["t"], "m": "step " + str(i + 1) + " · " + b["lines"][0]["t"]} for i, b in enumerate(order)]
        MC["step"] = {"type": "cycle", "period": 2.2 if dark else 2.6, "t0": 0, "values": vals,
                      "log": {"who": "step", "c": "cy" if dark else "blt"}}

    # ---- wires between rows ----
    lc = "line"
    for r in range(n - 1):
        A, Bn = built[r], built[r + 1]
        ya = max(b["y"] + b["h"] for b in A)
        yb = min(b["y"] for b in Bn)
        ym = round((ya + yb) / 2)
        pcol = "bl" if dark else "pk"
        for a in A:
            for bb in Bn:
                if len(A) > 1 and len(Bn) > 1 and A.index(a) != Bn.index(bb) and len(A) == len(Bn):
                    continue  # equal rows: straight lanes, no crossing mesh
                ay = a["y"] + a["h"]
                pts = [[a["cx"], ay], [a["cx"], ym], [bb["cx"], ym], [bb["cx"], bb["y"] - 2]]
                if a["cx"] == bb["cx"]:
                    pts = [[a["cx"], ay], [bb["cx"], bb["y"] - 2]]
                el = {"type": "path", "points": pts, "color": lc, "r": 8 if not dark else 0,
                      "width": 2 if dark else 2.2,
                      "flow": {"period": round(1.8 + 0.3 * len(E) % 1.2, 2), "offsets": [0, 0.9], "color": pcol}}
                if steps:
                    el["when"] = {"var": "step.i", "eq": str(order.index(bb))}
                    el["then"] = {"color": "cy" if dark else "pk", "width": 3}
                E.append(el)

    # ---- boxes ----
    for i, b in enumerate(order):
        el = {"type": "box", "x": b["x"], "y": b["y"], "w": round(b["w"]), "h": round(b["h"]), "color": b["color"],
              "pad": [pad_t, pad_x], "lines": b["lines"]}
        if b["fill"]:
            el["fill"] = b["fill"]
        if steps:
            el["when"] = {"var": "step.i", "eq": str(i)}
            el["then"] = {"glow": b["color"], "border": 3} if not dark else {"glow": b["color"], "fill": "hl"}
        E.append(el)

    # ---- rail ----
    if rail_x is not None:
        rid = "rail"
        items = rail["items"]
        rcol = "pu" if dark else "put"
        MC[rid] = {"type": "triggers", "color": rcol, "period": 4.5, "on": 3.0, "t0": -1.6, "callsStart": 1,
                   "tokens": {"start": 129, "step": 93, "unit": "k"},
                   "items": [{"name": it["name"], "adv": (it.get("adv") or ["» checking", "» done"])[:2]} for it in items],
                   "onText": rail.get("onText", "advising" if spec.get("lang") != "zh" else "介入中"),
                   "offText": rail.get("offText", "on call" if spec.get("lang") != "zh" else "待命"),
                   "log": {"who": M.clip(rail.get("name", "on call"), 140, FS).lower(), "c": rcol,
                           "start": {"m": "{name} · " + ("woken" if spec.get("lang") != "zh" else "唤起")},
                           "end": {"m": "{name} · " + ("done, back on call" if spec.get("lang") != "zh" else "完成，回到待命")}}}
        rw = W - margin - rail_x if rail.get("side") == "right" else (x0 - 44 - margin)
        inner = rw - 14 - 6
        rtop = order[0]["y"]
        rbot = max(b["y"] + b["h"] for b in order)
        for it in MC[rid]["items"]:
            it["name"] = M.clip(it["name"], inner - M.w("◆ ", FS) - 4)
            it["adv"] = [M.clip(a, inner - 10) for a in it["adv"]]
        lines = [{"t": M.clip(rail.get("name", "ON CALL"), inner), "c": rcol, "b": 1}]
        if rail.get("sub"):
            lines.append({"t": M.clip(rail["sub"], inner), "c": rcol})
        nI = len(items)
        tail = [{"t": "last advice:" if spec.get("lang") != "zh" else "最近建议：", "c": "dim", "align": "left", "indent": 8},
                {"runs": [{"v": rid + ".adv0", "c": rcol, "b": 1}], "align": "left", "indent": 8},
                {"runs": [{"v": rid + ".adv1", "c": rcol, "b": 1}], "align": "left", "indent": 8},
                {"items": [{"w": int(inner * 0.6), "runs": [{"t": "calls" if spec.get("lang") != "zh" else "调用", "c": "dim"}]},
                           {"w": int(inner * 0.3), "align": "right", "runs": [{"v": rid + ".calls", "c": rcol, "b": 1}]}],
                 "indent": 8}]
        wants = []
        for i, it in enumerate(items):
            tr = it.get("row")
            if tr is None:
                tr = round(i * (n - 1) / max(1, nI - 1)) if nI > 1 else 0
            tr = max(0, min(n - 1, int(tr)))
            target = built[tr][0] if rail.get("side", "left") != "right" else built[tr][-1]
            wants.append((int(round((target["y"] + target["h"] / 2 - rtop - pad_t) / LH - 0.5)), target))
        trig_rows, tail_done = [], False
        for i, (want, target) in enumerate(wants):
            L = max(len(lines), want)
            if not tail_done and L - len(lines) >= len(tail) + 2:
                lines.append("")
                lines += tail
                tail_done = True
            while len(lines) < L:
                lines.append("")
            lines.append({"trigger": [rid, i]})
            trig_rows.append((i, len(lines) - 1, target))
        if not tail_done:
            lines += [""] + tail
        rh = max(rbot - rtop, pad_t + len(lines) * LH + 12)
        el = {"type": "box", "x": rail_x, "y": rtop, "w": rw, "h": round(rh), "color": rcol if dark else "pu",
              "pad": [pad_t, 7, 7], "lines": lines}
        if not dark:
            el["fill"] = "puf"
        E.insert(0, el)
        for i, li, target in trig_rows:
            yy = round(rtop + pad_t + li * LH + LH / 2)
            if rail.get("side", "left") != "right":
                fx, tx = rail_x + rw + 4, target["x"] - 4
            else:
                fx, tx = target["x"] + round(target["w"]) + 4, rail_x - 4
            if not (target["y"] <= yy <= target["y"] + target["h"]):
                tx = (x0 - 6) if rail.get("side", "left") != "right" else tx
                if rail.get("side") == "right":
                    fx = x1 + 6
            if tx - fx > 30:
                E.append({"type": "tarrow", "machine": rid, "i": i, "from": [fx, yy], "to": [tx, yy]})
        if rh > rbot - rtop + 1:
            sys.stderr.write("warning: the rail is taller than the rows; fewer triggers or shorter rail text\n")

    # ---- log ----
    if log_el is not None:
        if not any(isinstance(m, dict) and m.get("log") for m in MC.values()):
            vals = [{"t": b["lines"][0]["t"], "m": b["lines"][0]["t"] + " · ok"} for b in order]
            MC["tick"] = {"type": "cycle", "period": 2.4, "t0": 0, "values": vals, "log": {"who": "event", "c": "cy" if dark else "blt"}}
        whos = [m["log"]["who"] for m in MC.values() if isinstance(m, dict) and m.get("log")]
        wx = log_el["cols"][1]["x"]
        mx = int(wx + max(M.w(w, FS) for w in whos) + 24)
        gx = int(mx + (log_el["w"] - 30 - mx) * 0.62)
        log_el["cols"][2]["x"], log_el["cols"][3]["x"] = mx, gx
        mw, gw = gx - mx - 16, log_el["w"] - 30 - gx - 6
        for m in MC.values():
            lg = m.get("log") if isinstance(m, dict) else None
            if not lg:
                continue
            if m["type"] == "lane":
                lg["msgs"] = [[M.clip(a, mw), M.clip(b, gw)] for a, b in lg["msgs"]]
            elif m["type"] == "gauge":
                lg["msgs"] = [M.clip(a, mw) for a in lg["msgs"]]
            elif m["type"] == "cycle":
                for v in m["values"]:
                    if isinstance(v, dict) and "m" in v:
                        v["m"] = M.clip(v["m"], mw)
            elif m["type"] == "triggers":
                longest = max(M.w(it["name"], FS) for it in m["items"])
                for k in ("start", "end"):
                    suffix = lg[k]["m"].replace("{name}", "")
                    if longest + M.w(suffix, FS) > mw:
                        lg[k]["m"] = "{name}"
        E.append(log_el)
    for e in E:
        e.pop("_counters", None)
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", help="spec JSON file")
    ap.add_argument("--out", help="where to write the config (default stdout)")
    ap.add_argument("--example", action="store_true", help="print a starter spec and exit")
    a = ap.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, ensure_ascii=False, indent=1)); return
    if not a.spec:
        ap.error("--spec is required (or --example)")
    spec = json.load(open(a.spec, encoding="utf-8"))
    cfg = build(spec)
    txt = json.dumps(cfg, ensure_ascii=False, indent=1)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(txt)
        print(f"wrote {a.out} ({len(txt)//1024} KB, {len(cfg['elements'])} elements, {len(cfg['machines'])} machines)."
              f" Next: python3 scripts/check_frames.py --config {a.out} --out-dir frames --repeat")
    else:
        print(txt)


if __name__ == "__main__":
    main()
