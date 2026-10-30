#!/usr/bin/env python3
"""Acceptance verifier for live-panel views ("验证技能" CLI).

Renders one config in 6 combos (3 canvas presets x 2 themes), runs the DOM
layout checks via scripts/check_frames.py --repeat, then applies the hard
rules from references/views.md section 4 inside the page (contrast, fill,
edges through boxes, flicker, views present, page error) and writes 3
screenshots per combo plus out/report.json.

  CHROME=$(command -v chromium || command -v google-chrome || find / -name chrome-headless-shell -type f 2>/dev/null | head -1)
  python3 scripts/verify_view.py --config examples/<kind>/config.json --chrome "$CHROME" --out /tmp/vv-<kind>

Exit 0 = every combo passed. stdout carries the JSON report only with --json;
the human-readable summary always goes to stderr. Windows requires websocket-client.
"""
import argparse, json, os, subprocess, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import livepanel as lp

CANVAS_PRESETS = ["4:5", "3:4", "1:1"]
THEMES = ["terminal-dark", "light-pastel"]
VIEW_KINDS = sorted({"nebula", "timeline", "funnel", "tree", "ring", "kpi"} |
                    {f.stem for f in (Path(__file__).resolve().parent.parent / "assets" / "views").glob("*.js") if not f.name.startswith("_")})
QUICK_COMBO = ("4x5_light-pastel", "4:5", "light-pastel")


def combo_name(preset, theme):
    return f"{preset.replace(':', 'x')}_{theme}"


def select_combos(args):
    if args.quick:
        return [QUICK_COMBO]
    if args.combos == "cur":
        return [("cur", None, None)]
    # the config exactly as written, then the 6 forced canvas x theme combos
    return [("cur", None, None)] + [(combo_name(p, t), p, t) for p in CANVAS_PRESETS for t in THEMES]


def make_combo_config(cfg, preset, theme):
    """Copy the config and force canvas/theme to one combo. Everything except
    preset/titleFont is stripped from theme so the theme really switches."""
    c = json.loads(json.dumps(cfg))
    if preset is None:
        return c
    cv = c.setdefault("canvas", {})
    cv["preset"] = preset
    cv.pop("width", None)
    cv.pop("height", None)
    th = c.setdefault("theme", {})
    th["preset"] = theme
    for k in list(th):
        if k not in ("preset", "titleFont"):
            del th[k]
    return c


# ---------------------------------------------------------------- schema ----

def _nonempty_array(e, where, field, fix, msgs):
    v = e.get(field)
    if not isinstance(v, list) or not v:
        msgs.append(f"{where}: missing/empty '{field}' — {fix}")
        return False
    return True


def schema_check(cfg):
    """Structural checks that do not need a browser. Returns problem strings,
    each with a hint on how to fix it."""
    msgs = []
    if "canvas" not in cfg:
        msgs.append('missing top-level "canvas" — add e.g. "canvas":{"preset":"4:5","duration":30}')
    els = cfg.get("elements")
    if "elements" not in cfg:
        msgs.append('missing top-level "elements" — add an array of element objects')
        return msgs
    if not isinstance(els, list):
        msgs.append('"elements" must be an array')
        return msgs
    if not any(isinstance(e, dict) and e.get("type") == "view" for e in els):
        msgs.append('no {"type":"view"} element — verify_view.py accepts views only; use check_frames.py for hand-placed panels')
    for i, e in enumerate(els):
        if not isinstance(e, dict) or e.get("type") != "view":
            continue
        where = f"elements[{i}] (type=view)"
        kind = e.get("kind")
        if kind not in VIEW_KINDS:
            msgs.append(f"{where}: kind {kind!r} is not a view — kind must be one of {', '.join(VIEW_KINDS)}")
            continue
        where += f" kind={kind}"
        if kind == "nebula":
            if _nonempty_array(e, where, "nodes", 'add "nodes":[{"id","label","group"}]', msgs):
                _nonempty_array(e, where, "edges", 'add "edges":[{"a","b","w"}] (w = 0..1 strength)', msgs)
        elif kind == "timeline":
            if _nonempty_array(e, where, "lanes", 'add "lanes":[{"id","label"}]', msgs):
                _nonempty_array(e, where, "events", 'add "events":[{"lane","start","end","label"}] in abstract time units', msgs)
        elif kind == "funnel":
            if _nonempty_array(e, where, "stages", 'add "stages":[{"label","value"}]', msgs):
                vals = [s.get("value") for s in e["stages"] if isinstance(s, dict)]
                if not all(isinstance(v, (int, float)) for v in vals):
                    msgs.append(f"{where}: every stage needs a numeric \"value\" — stages:[{{\"label\",\"value\"}}]")
                else:
                    for k in range(1, len(vals)):
                        if vals[k] > vals[k - 1]:
                            msgs.append(
                                f"{where}: stages[{k}].value={vals[k]} > stages[{k - 1}].value={vals[k - 1]} — "
                                "funnel values must be non-increasing; fix the data or merge/split stages")
                            break
        elif kind == "tree":
            root = e.get("root")
            if not isinstance(root, dict) or not root.get("label"):
                msgs.append(f"{where}: missing 'root' — add \"root\":{{\"label\",...,\"children\":[...]}}")
        elif kind == "ring":
            steps = e.get("steps")
            n = len(steps) if isinstance(steps, list) else 0
            if not 3 <= n <= 8:
                msgs.append(f"{where}: ring needs 3..8 steps, got {n} — add \"steps\":[{{\"label\"}}] (split or merge until 3..8)")
        elif kind == "kpi":
            _nonempty_array(e, where, "cards", 'add "cards":[{"label","value","series":[...]}]', msgs)
        elif kind == "loop":
            # the loop closes on the video length: canvas.duration is a whole multiple of the effective period
            # (ambientPeriod for motion "ambient", period when the walk is on)
            dur = (cfg.get("canvas") or {}).get("duration")
            motion = e.get("motion", "ambient")
            amb = e.get("ambientPeriod", 3.0)
            per = e.get("period", 26) if "walk" in str(motion) else amb
            name = "period" if "walk" in str(motion) else "ambientPeriod"
            if isinstance(dur, (int, float)) and isinstance(per, (int, float)) and per > 0:
                q = dur / per
                if q < 1 or abs(q - round(q)) > 1e-6:
                    msgs.append(f"{where}: canvas.duration={dur} is not a whole multiple of {name}={per} — "
                                f"the loop would not close; set duration = k * {name}")
    return msgs


# ------------------------------------------------------------- check_frames --

def run_check_frames(script_dir, config_path, out_dir, chrome, template, samples):
    """Run scripts/check_frames.py --repeat. Returns (rc, [problem lines])."""
    cmd = [sys.executable, str(script_dir / "check_frames.py"),
           "--config", str(config_path), "--out-dir", str(out_dir),
           "--samples", str(samples), "--repeat", "--chrome", chrome]
    if template:
        cmd += ["--template", template]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return 124, ["check_frames timed out after 600s"]
    problems = []
    for ln in (p.stdout or "").splitlines() + (p.stderr or "").splitlines():
        ln = ln.strip()
        if ln.startswith("PROBLEM: "):
            problems.append(ln[len("PROBLEM: "):])
        elif "DIFFERENT" in ln:
            problems.append("replay not identical: " + ln)
    if p.returncode != 0 and not problems:
        # check_frames itself crashed (e.g. page JS error -> traceback): show why
        tail = [l.strip() for l in (p.stderr or "").splitlines() if l.strip()]
        problems.append("check_frames crashed: " + (tail[-1] if tail else f"exit {p.returncode}"))
    return p.returncode, problems


# ----------------------------------------------------------------- JS ----

# Shared prelude: map client rects to canvas coordinates (the stage may be
# CSS-scaled), parse/blend rgb colours, WCAG luminance and contrast.
JS_PRELUDE = r"""
var ST=document.getElementById('stage');
var sr=ST.getBoundingClientRect();
var scale=sr.width/(parseFloat(ST.style.width)||sr.width);
function cv(r){return {l:(r.left-sr.left)/scale,t:(r.top-sr.top)/scale,r:(r.right-sr.left)/scale,b:(r.bottom-sr.top)/scale}}
function parseC(s){var m=/rgba?\(([^)]+)\)/.exec(s||'');if(!m)return null;var p=m[1].split(/\s*,\s*/).map(Number);
  return [p[0],p[1],p[2],p.length>3?p[3]:1]}
function mix(f,b,a){return [f[0]*a+b[0]*(1-a),f[1]*a+b[1]*(1-a),f[2]*a+b[2]*(1-a)]}
function lum(c){function f(v){v/=255;return v<=0.04045?v/12.92:Math.pow((v+0.055)/1.055,2.4)}
  return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])}
function ratio(a,b){var x=lum(a),y=lum(b);return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)}
function css(c){return 'rgb('+Math.round(c[0])+','+Math.round(c[1])+','+Math.round(c[2])+')'}
"""

# Contrast: for every marked text node (HTML and SVG), compute text colour,
# effective background (first opaque background up the ancestor chain; SVG text
# uses the nearest marked box containing it, else the stage background), blend
# by accumulated opacity, and compute the WCAG ratio.
JS_CONTRAST = "(function(){" + JS_PRELUDE + r"""
var out=[];
function opacityTo(el){var op=1,e=el;while(e&&e!==ST){if(e.nodeType===1){var o=parseFloat(getComputedStyle(e).opacity);if(!isNaN(o))op*=o}e=e.parentNode}return op}
function bgHTML(el){var layers=[],e=el;
  while(e&&e.nodeType===1){var c=parseC(getComputedStyle(e).backgroundColor);
    if(c&&c[3]>0){layers.push(c);if(c[3]>=0.999)break}
    if(e===ST)break;e=e.parentElement}
  if(!layers.length)layers.push([0,0,0,1]);
  var bg=layers[layers.length-1];
  for(var i=layers.length-2;i>=0;i--)bg=mix(layers[i],bg,layers[i][3]);
  return bg}
function bgSVG(el){var r=cv(el.getBoundingClientRect()),best=null,ba=0;
  document.querySelectorAll('[data-t="box"]').forEach(function(b){
    var br=cv(b.getBoundingClientRect());
    var cx=(r.l+r.r)/2,cy=(r.t+r.b)/2;
    if(cx>br.l&&cx<br.r&&cy>br.t&&cy<br.b){
      var isS=b.namespaceURI==='http://www.w3.org/2000/svg'; var c=isS?parseC(getComputedStyle(b).fill):parseC(getComputedStyle(b).backgroundColor); if(c&&c[3]<=0.001)c=null;
      if(c&&c[3]>ba){ba=c[3];best=c}}});
  if(!best)best=parseC(getComputedStyle(ST).backgroundColor)||[0,0,0,1];
  return best}
var els=document.querySelectorAll('[data-t="text"]');
for(var i=0;i<els.length;i++){var el=els[i];
  if(el.getAttribute('data-nocheck'))continue;
  var cs=getComputedStyle(el),svg=(el.ownerSVGElement!=null);
  var rect=el.getBoundingClientRect();
  if(cs.display==='none'||cs.visibility==='hidden'||rect.width<0.5||rect.height<0.5)continue;
  var txt=(el.textContent||'').trim().slice(0,28);if(!txt)continue;
  var col=parseC(svg?cs.fill:cs.color);
  if(!col||col[3]===0||(svg&&cs.fill==='none'))continue;
  var bg=svg?bgSVG(el):bgHTML(el);
  var op=opacityTo(el);
  var shown=col;if(op<0.999)shown=mix(col,bg,op);
  var size=parseFloat(cs.fontSize);
  var need=size>=20?3.0:4.5;
  out.push({txt:txt,color:css(shown),bg:css(bg),size:Math.round(size*10)/10,
            ratio:Math.round(ratio(shown,bg)*100)/100,need:need,ok:ratio(shown,bg)>=need-1e-9})}
return out})()"""

# Fill: union bounding box of all marked nodes inside each view root vs its
# data-rect — width/height coverage and margin balance.
JS_FILL = "(function(){" + JS_PRELUDE + r"""
var out=[];
document.querySelectorAll('[data-view]').forEach(function(root){
  var parts=(root.getAttribute('data-rect')||'').split(',').map(Number);
  var rect={x:parts[0],y:parts[1],w:parts[2],h:parts[3]};
  var u=null;
  root.querySelectorAll('[data-t]').forEach(function(n){
    var r=cv(n.getBoundingClientRect());
    if(r.r-r.l<0.5&&r.b-r.t<0.5)return;
    if(!u)u={l:r.l,t:r.t,r:r.r,b:r.b};
    else{u.l=Math.min(u.l,r.l);u.t=Math.min(u.t,r.t);u.r=Math.max(u.r,r.r);u.b=Math.max(u.b,r.b)}});
  if(!u||rect.w<=0||rect.h<=0){out.push({kind:root.dataset.view,rect:rect,empty:true});return}
  var cw=(u.r-u.l)/rect.w,ch=(u.b-u.t)/rect.h,ml=u.l-rect.x,mr=rect.x+rect.w-u.r;
  out.push({kind:root.dataset.view,rect:rect,union:{l:Math.round(u.l),t:Math.round(u.t),r:Math.round(u.r),b:Math.round(u.b)},
    cw:Math.round(cw*1000)/1000,ch:Math.round(ch*1000)/1000,
    ml:Math.round(ml),mr:Math.round(mr),
    okW:cw>=0.70,okH:ch>=0.60,okM:Math.abs(ml-mr)<0.12*rect.w})}
);return out})()"""

# Edges: sample every ~4px, map to canvas coords, flag samples that fall inside
# an inset (3px) marked box unless that box is the edge's endpoint box (within
# 6px of the first/last sample).
JS_EDGES = "(function(){" + JS_PRELUDE + r"""
function pt(p){return {x:(p.x-sr.left)/scale,y:(p.y-sr.top)/scale}}
var boxes=[];
document.querySelectorAll('[data-t="box"]').forEach(function(b,i){
  var r=cv(b.getBoundingClientRect());
  boxes.push({i:i,l:r.l,t:r.t,r:r.r,b:r.b,txt:(b.textContent||'').trim().slice(0,24)})});
function dist(p,b){var dx=Math.max(b.l-p.x,0,p.x-b.r),dy=Math.max(b.t-p.y,0,p.y-b.b);return Math.hypot(dx,dy)}
function inside(p,b){return p.x>b.l+3&&p.x<b.r-3&&p.y>b.t+3&&p.y<b.b-3}
var res=[];
document.querySelectorAll('[data-t="edge"]').forEach(function(e,ei){
  var raw=[],L=0;
  if(e.tagName==='path'&&e.getTotalLength){L=e.getTotalLength();if(L<1)return;
    var n=Math.max(2,Math.ceil(L/4));for(var i=0;i<=n;i++)raw.push(e.getPointAtLength(L*i/n))}
  else if(e.tagName==='line'){var x1=+e.getAttribute('x1'),y1=+e.getAttribute('y1'),x2=+e.getAttribute('x2'),y2=+e.getAttribute('y2');
    L=Math.hypot(x2-x1,y2-y1);if(L<1)return;var n2=Math.max(2,Math.ceil(L/4));
    for(var j=0;j<=n2;j++)raw.push({x:x1+(x2-x1)*j/n2,y:y1+(y2-y1)*j/n2})}
  else if(e.tagName==='polyline'){var ps=(e.getAttribute('points')||'').trim().split(/[\s,]+/).map(Number);
    if(ps.length<4)return;var pts=[];for(var k=0;k+1<ps.length;k+=2)pts.push({x:ps[k],y:ps[k+1]});
    for(var s=0;s+1<pts.length;s++){var a=pts[s],b2=pts[s+1],d=Math.hypot(b2.x-a.x,b2.y-a.y),m=Math.max(1,Math.ceil(d/4));
      for(var q=(s===0?0:1);q<=m;q++)raw.push({x:a.x+(b2.x-a.x)*q/m,y:a.y+(b2.y-a.y)*q/m})}}
  else return;
  var ctm=e.getScreenCTM();if(!ctm)return;
  var svg=e.ownerSVGElement||document.querySelector('svg'),ip=svg.createSVGPoint();
  var cpts=raw.map(function(p){ip.x=p.x;ip.y=p.y;return pt(ip.matrixTransform(ctm))});
  var A=null,B=null;
  boxes.forEach(function(b){if(dist(cpts[0],b)<=6)A=b;if(dist(cpts[cpts.length-1],b)<=6)B=b});
  var hits={};
  cpts.forEach(function(p,pi){boxes.forEach(function(b){
    if(b!==A&&b!==B&&inside(p,b)){var key=b.i;
      if(!hits[key])hits[key]={box:b.txt||('#'+b.i),x:Math.round(p.x),y:Math.round(p.y)}}})});
  var h=Object.keys(hits).map(function(k){return hits[k]});
  if(h.length)res.push({edge:ei,d:(e.getAttribute('d')||e.getAttribute('points')||'').slice(0,48),hits:h})});
return res})()"""

# Flicker: per-node signature (visibility + colour/fill/stroke). Text content
# is deliberately excluded so counters don't count as flicker.
JS_SIG = "(function(){" + JS_PRELUDE + r"""
var o=[];
document.querySelectorAll('[data-t]').forEach(function(e){
  var cs=getComputedStyle(e),r=e.getBoundingClientRect();
  var vis=cs.display!=='none'&&cs.visibility!=='hidden'&&parseFloat(cs.opacity)>0.05&&r.width>0.5&&r.height>0.5;
  o.push((vis?1:0)+'|'+cs.color+'|'+cs.fill+'|'+cs.stroke)});
return o})()"""

JS_NODE_META = "(function(){" + JS_PRELUDE + r"""
var o=[];
document.querySelectorAll('[data-t]').forEach(function(e,i){
  o.push({i:i,tag:e.tagName.toLowerCase(),dt:e.getAttribute('data-t'),txt:(e.textContent||'').trim().slice(0,24)})});
return o})()"""


# ------------------------------------------------------------ rule runner --

def run_rules(br, config_path, cfg, out_dir, template):
    """Open the page, take 3 screenshots, run all in-page rule checks.
    Returns the rules dict of the report."""
    w, h, dur, _ = lp.canvas(cfg)
    page = Path(tempfile.mkdtemp(prefix="livepanel-page-")) / "page.html"
    lp.build_page(str(config_path), str(page), template)
    br.cmd("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": False})
    rules = {"contrast": [], "fill": {"checked": False, "views": [], "problems": []},
             "edges": {"checked": False, "violations": []}, "flicker": [], "page_error": ""}
    try:
        br.open(page.resolve().as_uri() + "?manual")
    except RuntimeError as e:
        # A page that cannot boot (JS error / never ready) fails here; the other
        # rules have nothing meaningful to measure on a half-built DOM.
        rules["page_error"] = str(e)
        return rules
    times = [round(dur * f, 2) for f in (0.1, 0.45, 0.8)]

    contrast_raw, fill_raw, edges_raw = [], [], []
    for i, t in enumerate(times):
        br.seek(t)
        out_dir.joinpath(f"shot_{i + 1}.png").write_bytes(br.shot())
        contrast_raw.append({"t": t, "rows": br.eval(JS_CONTRAST) or []})
        fill_raw.append({"t": t, "rows": br.eval(JS_FILL) or []})
        edges_raw.append({"t": t, "rows": br.eval(JS_EDGES) or []})

    # ---- contrast: worst 5 across all time points (dedup by text+colours)
    worst = {}
    for tr in contrast_raw:
        for r in tr["rows"]:
            key = (r["txt"], r["color"], r["bg"], r["need"])
            if key not in worst or r["ratio"] < worst[key]["ratio"]:
                worst[key] = dict(r, t=tr["t"])
    failing = [r for r in worst.values() if not r["ok"]]
    rules["contrast"] = sorted(failing, key=lambda r: r["ratio"])[:5]
    if len(rules["contrast"]) < 5:  # pad with the worst passing rows for context
        passing = sorted([r for r in worst.values() if r["ok"]], key=lambda r: r["ratio"])
        rules["contrast"] += passing[:5 - len(rules["contrast"])]

    # ---- fill (aggregate the 3 time points leniently: keep each view's best
    # coverage / smallest margin diff; failing even then = definitely failing)
    n_view_elements = sum(1 for e in (cfg.get("elements") or [])
                          if isinstance(e, dict) and e.get("type") == "view")
    has_views = bool(fill_raw[0]["rows"])
    if n_view_elements and not has_views:
        rules["fill"]["problems"].append(
            f"config has {n_view_elements} view element(s) but the page rendered no [data-view] root — "
            "check that the view registers LP.registerView('<kind>',...) and that assets/views/<kind>.js exists "
            "(build_page inlines every assets/views/*.js at <!--LIVE_VIEWS-->)")
    elif has_views:
        rules["fill"]["checked"] = True
        by_key, empty_count = {}, {}
        for fr in fill_raw:
            for v in fr["rows"]:
                r = v.get("rect") or {}
                key = (v.get("kind"), r.get("x"), r.get("y"))
                if v.get("empty") or r.get("w", 0) <= 0 or r.get("h", 0) <= 0:
                    empty_count[key] = empty_count.get(key, 0) + 1
                    continue
                k = by_key.setdefault(key, {"cw": 0.0, "ch": 0.0, "md": 1e18, "rw": r["w"]})
                k["cw"] = max(k["cw"], v["cw"])
                k["ch"] = max(k["ch"], v["ch"])
                k["md"] = min(k["md"], abs(v["ml"] - v["mr"]))
        n_times = len(fill_raw)
        for key, cnt in sorted(empty_count.items()):
            if key not in by_key and cnt >= n_times:
                rules["fill"]["problems"].append(
                    f"view '{key[0]}' at ({key[1]},{key[2]}) rendered no measurable [data-t] content at any "
                    "sampled time — draw the diagram in build() (seek() may only update styles/attributes)")
        for key, k in sorted(by_key.items()):
            kind = key[0]
            probs = []
            if k["cw"] < 0.70:
                probs.append(f"width coverage {k['cw']:.0%} < 70%")
            if k["ch"] < 0.60:
                probs.append(f"height coverage {k['ch']:.0%} < 60%")
            if k["md"] >= 0.12 * k["rw"]:
                probs.append(f"left/right margins unbalanced (min diff {k['md']:.0f}px, "
                             f"must be < 12% of rect width {k['rw']:.0f}px) — re-centre the content bbox")
            rules["fill"]["views"].append(kind)
            if probs:
                rules["fill"]["problems"].append(
                    f"view '{kind}': " + "; ".join(probs) +
                    " — spread the layout across the rect, deriving all sizes from rect.w/rect.h")

    # ---- edges
    rules["edges"]["checked"] = bool(br.eval("!!document.querySelector('[data-t=\"edge\"]')"))
    seen = {}
    for er in edges_raw:
        for row in er["rows"]:
            for hit in row["hits"]:
                key = (row["edge"], hit["box"])
                if key not in seen:
                    seen[key] = {"edge": row["edge"], "d": row["d"], "box": hit["box"], "at": []}
                seen[key]["at"].append({"t": er["t"], "x": hit["x"], "y": hit["y"]})
    rules["edges"]["violations"] = list(seen.values())

    # ---- flicker: 0.1s steps over [0.2dur, min(0.2dur+8s, dur)]
    t0 = 0.2 * dur
    t1 = min(t0 + 8.0, dur)
    n_steps = max(2, int(round((t1 - t0) / 0.1)) + 1)
    steps = [round(t0 + 0.1 * k, 2) for k in range(n_steps)]
    sigs = [br.eval(f"window.seek({t!r});" + JS_SIG) for t in steps]
    metas = br.eval(JS_NODE_META) or []
    if sigs and all(isinstance(s, list) for s in sigs):
        width = min(len(s) for s in sigs)
        for idx in range(width):
            changes = []
            prev = sigs[0][idx]
            for k in range(1, len(sigs)):
                if sigs[k][idx] != prev:
                    changes.append(steps[k])
                    prev = sigs[k][idx]
            fast = [changes[j] for j in range(1, len(changes)) if changes[j] - changes[j - 1] < 0.4 - 1e-6]
            if fast:
                m = metas[idx] if idx < len(metas) else {"tag": "?", "dt": "?", "txt": ""}
                rules["flicker"].append({
                    "index": idx, "tag": m.get("tag"), "dt": m.get("dt"), "txt": m.get("txt"),
                    "changes": len(changes), "first_fast_pair": [round(fast[0] - 0.1, 2), fast[0]]})

    rules["page_error"] = br.eval("window.__error||''") or ""
    return rules


# -------------------------------------------------------------- messages --

def contrast_msg(r):
    return (f"contrast {r['ratio']} < {r['need']} for text '{r['txt']}' ({r['color']} on {r['bg']}) "
            f"at {r['size']}px — use a darker text colour ('fg' or 'dim' on 'bg'/'panel', 'wh' on strong "
            f"accents) or a lighter background ('accf*' tints); ≥20px titles may use ≥3.0")


def edge_msg(v):
    at = v["at"][0]
    return (f"edge #{v['edge']} ({v['d']}) passes through box '{v['box']}' near ({at['x']},{at['y']}) "
            "— route the connector around the card or end it at the card border "
            "(mark connectors mark(node,'edge') and cards mark(node,'box'))")


def flicker_msg(f):
    a, b = f["first_fast_pair"]
    return (f"node #{f['index']} <{f['tag']} data-t={f['dt']}> '{f['txt']}' changes style {f['changes']}x with "
            f"a gap <0.4s (e.g. t={a}s→{b}s) — slow the animation: state changes ≥0.4s apart, "
            "highlights ≥0.8s; counters may change text but must not change colour faster")


# ----------------------------------------------------------------- main ----

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="config.json to verify")
    ap.add_argument("--chrome", help="path to Chrome (default: search PATH)")
    ap.add_argument("--out", default="/tmp/vv", help="output directory (default /tmp/vv)")
    ap.add_argument("--combos", choices=["all", "cur"], default="all",
                    help="all = 3 canvases x 2 themes; cur = the config as-is")
    ap.add_argument("--json", action="store_true", help="print only the JSON report on stdout")
    ap.add_argument("--template", help="override the HTML template (assets/template.html)")
    ap.add_argument("--quick", action="store_true",
                    help="only run 4:5 x light-pastel (fast iteration for view authors)")
    ap.add_argument("--samples", type=int, default=60,
                    help="time samples passed to check_frames (default 60)")
    args = ap.parse_args()

    try:
        cfg = lp.load_config(args.config)
    except Exception as e:
        sys.exit(f"cannot load config {args.config}: {e}")
    chrome = lp.find_chrome(args.chrome)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    script_dir = Path(__file__).resolve().parent

    report = {"config": str(Path(args.config).resolve()), "pass": True, "combos": {}, "summary": {}}
    t_start = time.time()
    br = None  # one Chrome reused for the rule checks of every combo
    try:
        for name, preset, theme in select_combos(args):
            log(f"== {name}")
            cdir = out / name
            cdir.mkdir(parents=True, exist_ok=True)
            ccfg = make_combo_config(cfg, preset, theme)
            cpath = cdir / "config.json"
            cpath.write_text(json.dumps(ccfg, ensure_ascii=False, indent=1), encoding="utf-8")

            res = {"pass": True, "schema": [], "check_frames_rc": None, "problems": [],
                   "rules": {}, "shots": [], "error": ""}
            try:
                res["schema"] = schema_check(ccfg)
                if res["schema"]:
                    res["pass"] = False
                rc, problems = run_check_frames(script_dir, cpath, cdir / "frames",
                                                chrome, args.template, args.samples)
                res["check_frames_rc"] = rc
                res["problems"] = problems
                if rc != 0 or problems:
                    res["pass"] = False
                if br is None:
                    br = lp.Chrome(chrome, 1200, 1500)
                res["rules"] = run_rules(br, cpath, ccfg, cdir, args.template)
                res["shots"] = [str(cdir / f"shot_{i}.png") for i in (1, 2, 3)
                                if (cdir / f"shot_{i}.png").exists()]
                r = res["rules"]
                if r["contrast"] and any(not x["ok"] for x in r["contrast"]):
                    res["pass"] = False
                if r["fill"]["problems"] or r["edges"]["violations"] or r["flicker"] or r["page_error"]:
                    res["pass"] = False
            except Exception as e:  # keep going: one broken combo must not kill the run
                res["error"] = f"{type(e).__name__}: {e}"
                res["pass"] = False
            report["combos"][name] = res
            log(f"   {'PASS' if res['pass'] else 'FAIL'}")
    finally:
        if br is not None:
            br.close()

    report["pass"] = all(c["pass"] for c in report["combos"].values()) if report["combos"] else False
    report["summary"] = {"combos_total": len(report["combos"]),
                         "combos_passed": sum(1 for c in report["combos"].values() if c["pass"]),
                         "elapsed_s": round(time.time() - t_start, 1),
                         "report": str(out / "report.json")}
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print_summary(report, out)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(f"report: {out / 'report.json'}")
    sys.exit(0 if report["pass"] else 1)


def log(msg):
    print(msg, file=sys.stderr)


def print_summary(report, out):
    """Human-readable, fix-oriented summary. Always stderr."""
    log("")
    for name, c in report["combos"].items():
        log(f"== {name}: {'PASS' if c['pass'] else 'FAIL'}")
        for m in c["schema"]:
            log(f"   schema: {m}")
        if c["check_frames_rc"] not in (0, None):
            log(f"   check_frames rc={c['check_frames_rc']} (0 = ok; non-zero means overflow/overlap/replay problems)")
        for p in c["problems"][:10]:
            log(f"   check_frames: {p}")
        if len(c["problems"]) > 10:
            log(f"   ... and {len(c['problems']) - 10} more check_frames problems")
        r = c.get("rules") or {}
        for x in (r.get("contrast") or []):
            if not x["ok"]:
                log(f"   {contrast_msg(x)}")
        for p in (r.get("fill", {}).get("problems") or []):
            log(f"   fill: {p}")
        for v in (r.get("edges", {}).get("violations") or []):
            log(f"   edge: {edge_msg(v)}")
        for f in (r.get("flicker") or []):
            log(f"   flicker: {flicker_msg(f)}")
        if r.get("page_error"):
            log(f"   page error: {r['page_error']}")
        if c.get("error"):
            log(f"   error: {c['error']}")
    s = report["summary"]
    log(f"== overall: {'PASS' if report['pass'] else 'FAIL'} "
        f"({s['combos_passed']}/{s['combos_total']} combos, {s['elapsed_s']}s) report: {out / 'report.json'}")


if __name__ == "__main__":
    main()
