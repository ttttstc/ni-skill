"""Build pages and drive Chrome: POSIX DevTools pipe or Windows DevTools WebSocket."""
import base64, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = ROOT / "assets" / "template.html"
CHROME_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge"]
# On macOS the browser lives inside an .app bundle, not on PATH. Homebrew's `chromium` shim on PATH launches
# and then dies on the DevTools pipe, so real bundles are preferred over anything shutil.which() would find.
CHROME_MAC_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]


def find_exe(explicit, names, what):
    if explicit:
        p = shutil.which(explicit) or (explicit if os.path.exists(explicit) else None)
        if p:
            return p
        sys.exit(f"{what} not found: {explicit}")
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    sys.exit(f"{what} not found on PATH (tried {', '.join(names)}); pass it explicitly")


def find_chrome(explicit):
    """Chrome lookup: an explicit path wins, then macOS .app bundles, then the PATH names in CHROME_NAMES."""
    if explicit:
        return find_exe(explicit, CHROME_NAMES, "Chrome")
    if sys.platform == "darwin":
        for p in CHROME_MAC_PATHS:
            if os.path.exists(p):
                return p
    if sys.platform == "win32":
        for root in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")):
            if root:
                for relative in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe"):
                    p = os.path.join(root, relative)
                    if os.path.isfile(p):
                        return p
    return find_exe(None, CHROME_NAMES, "Chrome")


CANVAS_PRESETS = {"4:5": (1200, 1500), "3:4": (1080, 1440), "1:1": (1080, 1080)}


def canvas(cfg):
    """(width, height, duration, fps) from a config, honouring canvas.preset."""
    cv = cfg.get("canvas", {})
    pw, ph = CANVAS_PRESETS.get(cv.get("preset"), (1200, 1500))
    return cv.get("width", pw), cv.get("height", ph), cv.get("duration", 30), cv.get("fps", 30)


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def views_html():
    """Every assets/views/*.js (sorted, '_' prefix skipped) as inline <script> tags, so the page stays self-contained."""
    d = ROOT / "assets" / "views"
    if not d.is_dir():
        return ""
    out = []
    for f in sorted(d.glob("*.js")):
        if f.name.startswith("_"):
            continue
        out.append("<script>/* view: %s */\n%s\n</script>" % (f.name, f.read_text(encoding="utf-8").replace("</script", "<\\/script")))
    return "\n".join(out)


def _font_face(family, path, weight, chars, subset_ok=True):
    """One @font-face rule with the font file inlined as a data URL. A TTF/OTF over 400 KB (a full CJK font) is
    subset to the characters the config actually uses when fontTools is installed, so the page stays small."""
    import base64
    data = Path(path).read_bytes()
    ext = Path(path).suffix.lower()
    fmt = {".woff2": "woff2", ".woff": "woff", ".otf": "opentype"}.get(ext, "truetype")
    if subset_ok and chars and fmt in ("truetype", "opentype") and len(data) > 400_000:
        try:
            import io
            from fontTools import subset
            opts = subset.Options(); opts.flavor = "woff"; opts.layout_features = ["*"]
            font = subset.load_font(path, opts)
            sub = subset.Subsetter(opts); sub.populate(text=chars); sub.subset(font)
            buf = io.BytesIO(); subset.save_font(font, buf, opts); data, fmt = buf.getvalue(), "woff"
            font.close()  # fontTools keeps the source open; leaked fds push render.py's Chrome pipes past fd 9, which sh cannot redirect
        except ImportError:
            print(f"note: fontTools not installed, embedding all of {path} ({len(data) // 1024} KB)", file=sys.stderr)
    mime = {"woff2": "font/woff2", "woff": "font/woff", "opentype": "font/otf", "truetype": "font/ttf"}[fmt]
    b64 = base64.b64encode(data).decode("ascii")
    return ('@font-face{font-family:"%s";src:url(data:%s;base64,%s) format("%s");font-weight:%s;font-display:block}'
            % (family, mime, b64, fmt, weight or "100 900"))


def fonts_html(cfg, base_dir=None):
    """Embed fonts as data URLs: Smiley Sans (得意黑, OFL) when theme.titleFont == "smiley", and every entry of
    theme.fonts ([{family, src, weight?}], src relative to the config file) so a custom look (e.g. the hand-drawn
    sketch theme) stays one self-contained page."""
    th = cfg.get("theme") or {}
    rules = []
    if th.get("titleFont") == "smiley":
        f = ROOT / "assets" / "fonts" / "SmileySans-Oblique.woff2"
        rules.append(_font_face("Smiley Sans", str(f), None, "", subset_ok=False))
    if th.get("fonts"):
        chars = "".join(sorted(set(json.dumps(cfg, ensure_ascii=False)) | set(map(chr, range(32, 127))) | set("…·—–×→←↑↓✓“”‘’（）：，。、；？！「」《》")))
        for f in th["fonts"]:
            src = Path(f["src"])
            if not src.is_absolute():
                cand = [Path(base_dir or ".") / src, ROOT / "assets" / "fonts" / src]
                src = next((c for c in cand if c.exists()), cand[0])
            if not src.exists():
                print(f"note: theme.fonts: {f['src']} not found, falling back to the next font in theme.font", file=sys.stderr)
                continue
            rules.append(_font_face(f["family"], str(src), f.get("weight"), chars))
    return "<style>%s</style>" % "".join(rules) if rules else ""


def build_page(config_path, out_path, template=None):
    """Write a self-contained HTML file: template with the JSON config embedded. Returns the config dict."""
    cfg = load_config(config_path)
    tpl = Path(template or DEFAULT_TEMPLATE).read_text(encoding="utf-8")
    blob = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    tag = f'<script id="live-config" type="application/json">{blob}</script>'
    if "<!--LIVE_CONFIG-->" not in tpl:
        sys.exit("template has no <!--LIVE_CONFIG--> placeholder")
    page = tpl.replace("<!--LIVE_CONFIG-->", tag)
    page = page.replace("<!--LIVE_VIEWS-->", views_html()).replace("<!--LIVE_FONTS-->", fonts_html(cfg, Path(config_path).resolve().parent))
    Path(out_path).write_text(page, encoding="utf-8")
    return cfg


class Chrome:
    """Headless Chrome driven through DevTools, using websocket-client on Windows."""

    def __init__(self, chrome, width, height, no_sandbox=None):
        self.tmp = tempfile.mkdtemp(prefix="livepanel-")
        r1, w1 = os.pipe()   # we write -> chrome fd 3
        r2, w2 = os.pipe()   # chrome fd 4 -> we read
        args = [chrome, "--headless=new", "--remote-debugging-pipe", f"--user-data-dir={self.tmp}", "--no-first-run",
                "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--font-render-hinting=none",
                "--allow-file-access-from-files", "--disable-background-timer-throttling", "--mute-audio", "about:blank"]
        if no_sandbox or (no_sandbox is None and hasattr(os, "geteuid") and os.geteuid() == 0):
            args.insert(1, "--no-sandbox")
        self.ws = None
        if sys.platform == "win32":
            os.close(r1); os.close(w1); os.close(r2); os.close(w2)
            try:
                import websocket
            except ImportError:
                shutil.rmtree(self.tmp, ignore_errors=True)
                raise RuntimeError("Windows 需要 websocket-client：python -m pip install websocket-client") from None
            args = [a for a in args if a != "--remote-debugging-pipe"]
            args.insert(1, "--remote-debugging-port=0")
            self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                port_file = Path(self.tmp) / "DevToolsActivePort"
                deadline = time.monotonic() + 20
                lines = []
                while self.proc.poll() is None and time.monotonic() < deadline:
                    if port_file.exists():
                        lines = port_file.read_text().splitlines()
                        if len(lines) >= 2:
                            break
                    time.sleep(0.1)
                if len(lines) < 2:
                    raise RuntimeError("Chrome DevTools did not start")
                port, path = lines[:2]
                self.ws = websocket.create_connection(f"ws://127.0.0.1:{port}{path}", timeout=20, suppress_origin=True)
            except Exception:
                self.proc.terminate(); self.proc.wait(timeout=5)
                shutil.rmtree(self.tmp, ignore_errors=True)
                raise
        else:
            env = dict(os.environ, LP_R=str(r1), LP_W=str(w2))
            self.proc = subprocess.Popen(["sh", "-c", 'exec "$@" 3<&"$LP_R" 4>&"$LP_W"', "sh"] + args, pass_fds=(r1, w2), env=env,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.close(r1); os.close(w2)
            self.wf = os.fdopen(w1, "wb", buffering=0); self.rf = os.fdopen(r2, "rb", buffering=0)
        self.buf = b""; self.n = 0
        try:
            tid = self.call("Target.createTarget", {"url": "about:blank"})["targetId"]
            self.sid = self.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
            self.cmd("Page.enable")
            self.cmd("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False})
        except Exception:
            self.close()
            raise

    def call(self, method, params=None, session=None):
        self.n += 1
        msg = {"id": self.n, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        if self.ws:
            self.ws.send(json.dumps(msg))
            while True:
                m = json.loads(self.ws.recv())
                if m.get("id") == self.n:
                    if "error" in m:
                        raise RuntimeError(f"{method}: {m['error']}")
                    return m.get("result", {})
        self.wf.write(json.dumps(msg).encode() + b"\0")
        while True:
            while b"\0" not in self.buf:
                chunk = os.read(self.rf.fileno(), 1 << 20)
                if not chunk:
                    raise RuntimeError("Chrome closed the pipe")
                self.buf += chunk
            raw, self.buf = self.buf.split(b"\0", 1)
            m = json.loads(raw)
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def cmd(self, method, params=None):
        return self.call(method, params, self.sid)

    def eval(self, expr):
        r = self.cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in r:
            raise RuntimeError(f"js error: {r['exceptionDetails']}")
        return r["result"].get("value")

    def open(self, url, timeout=20):
        self.cmd("Page.navigate", {"url": url})
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                if self.eval("window.__ready===true"):
                    err = self.eval("window.__error||''")
                    if err:
                        raise RuntimeError("page error: " + err)
                    return
                err = self.eval("window.__error||''")
                if err:
                    raise RuntimeError("page error: " + err)
            except RuntimeError as e:
                if "page error" in str(e):
                    raise
            time.sleep(0.1)
        raise RuntimeError("page did not become ready (check the config JSON)")

    def seek(self, t):
        self.eval(f"window.seek({t!r})")

    def shot(self):
        return base64.b64decode(self.cmd("Page.captureScreenshot", {"format": "png"})["data"])

    def close(self):
        if self.ws:
            self.ws.close()
        try:
            self.proc.terminate(); self.proc.wait(5)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
