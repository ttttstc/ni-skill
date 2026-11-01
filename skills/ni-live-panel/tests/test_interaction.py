"""Browser tests for interactive playback, local edits and standalone downloads."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import livepanel as lp


class InteractionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="livepanel-interaction-")
        cls.root = Path(cls.temp.name)
        cls.browser = lp.Chrome(lp.find_chrome(os.environ.get("CHROME")), 900, 700)
        cls.page = cls.root / "panel.html"
        config = {
            "meta": {"title": "Interaction Panel"},
            "canvas": {"width": 500, "height": 360, "duration": 0.7},
            "theme": {"preset": "light-pastel", "font": "Arial"},
            "machines": {"seq": {"type": "cycle", "period": 0.35, "values": ["FIRST", "SECOND"]}},
            "elements": [
                {"type": "text", "x": 50, "y": 65, "w": 400, "runs": [{"t": "Panel title", "c": "fg"}]},
                {"type": "text", "x": 50, "y": 125, "w": 400, "runs": [{"v": "seq"}]},
                {"type": "text", "x": 50, "y": 185, "w": 400, "runs": [{"t": "Task: ", "c": "fg"}, {"v": "seq", "c": "gr"}]},
            ],
        }
        path = cls.root / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        lp.build_page(path, cls.page)
        ring = json.loads((SKILL / "examples" / "ring" / "config.json").read_text(encoding="utf-8"))
        ring["elements"][0]["period"] = 1.2
        ring["canvas"]["duration"] = 1.2
        path.write_text(json.dumps(ring, ensure_ascii=False), encoding="utf-8")
        cls.ring = cls.root / "ring.html"
        lp.build_page(path, cls.ring)
        cls.views = {}
        for name, source in (("funnel", "funnel/config.json"), ("loop", "loop-poteto/config.json"),
                             ("ambient-loop", "loop-poteto/config.json"),
                             ("excalidraw", "excalidraw-aqua/config-3x4.json")):
            view = json.loads((SKILL / "examples" / source).read_text(encoding="utf-8"))
            if name == "loop":
                view["elements"][0]["motion"] = "ambient+walk"
            path.write_text(json.dumps(view, ensure_ascii=False), encoding="utf-8")
            page = cls.root / (name + ".html")
            lp.build_page(path, page)
            cls.views[name] = page
        config["playback"] = {"steps": [{"label": "First scene", "start": 0.1, "end": 0.3},
                                        {"label": "Second scene", "start": 1.0, "end": 1.4}]}
        path.write_text(json.dumps(config), encoding="utf-8")
        cls.explicit = cls.root / "explicit.html"
        lp.build_page(path, cls.explicit)
        config["playback"]["steps"][0]["end"] = 0
        path.write_text(json.dumps(config), encoding="utf-8")
        cls.invalid = cls.root / "invalid.html"
        lp.build_page(path, cls.invalid)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.temp.cleanup()

    def setUp(self):
        self.open_page(self.page.as_uri())
        self.browser.eval("localStorage.clear()")
        self.open_page(self.page.as_uri())

    def open_page(self, url):
        # Avoid observing the old document's ready flag while a navigation is in flight.
        self.browser.eval("window.__ready=false")
        self.browser.open(url)

    def click(self, selector):
        point = self.browser.eval("""(function(){var r=document.querySelector(%s).getBoundingClientRect();
            return {x:r.left+r.width/2,y:r.top+r.height/2};})()""" % json.dumps(selector))
        for kind in ("mousePressed", "mouseReleased"):
            self.browser.cmd("Input.dispatchMouseEvent", {"type": kind, "button": "left", "clickCount": 1, **point})

    def edit_text(self, original, value, cancel=False):
        if self.browser.eval("document.getElementById('lp-edit').getAttribute('aria-pressed')") != "true":
            self.click("#lp-edit")
        point = self.browser.eval("""(function(){var found=null;
            document.querySelectorAll('#stage [data-t="text"],#stage svg text').forEach(function(el){
              var w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT), n;
              while((n=w.nextNode())) if(n.nodeValue===%s) found=n;
            }); var r=document.createRange(); r.selectNodeContents(found); var b=r.getBoundingClientRect();
            return {x:b.left+b.width/2,y:b.top+b.height/2};})()""" % json.dumps(original, ensure_ascii=False))
        for kind in ("mousePressed", "mouseReleased"):
            self.browser.cmd("Input.dispatchMouseEvent", {"type": kind, "button": "left", "clickCount": 1, **point})
        self.assertFalse(self.browser.eval("document.getElementById('lp-dialog').hidden"))
        self.browser.cmd("Input.insertText", {"text": value})
        self.click("#lp-cancel" if cancel else "#lp-save")

    def test_step_loops_until_next_and_automatic_mode_resumes(self):
        self.browser.eval("window.seek(0); document.getElementById('lp-mode').click()")
        time.sleep(0.12)
        first = self.browser.eval("({t:window.__t,text:document.querySelectorAll('#stage [data-t=text]')[1].textContent})")
        frames = self.browser.eval("""new Promise(function(resolve){var seen=new Set(), timer=setTimeout(function(){resolve(Array.from(seen));},3000);
            function sample(){seen.add(window.__t); if(seen.size>=2){clearTimeout(timer);resolve(Array.from(seen));}
              else requestAnimationFrame(sample);} requestAnimationFrame(sample);})""")
        self.assertGreaterEqual(len(frames), 2, "animation did not advance within the current step")
        self.assertTrue(all(0 <= t < 0.35 for t in frames))
        time.sleep(0.7)
        loop = self.browser.eval("({t:window.__t,text:document.querySelectorAll('#stage [data-t=text]')[1].textContent})")
        self.assertEqual((first["text"], loop["text"]), ("FIRST", "FIRST"))
        self.assertTrue(0 <= first["t"] < 0.35 and 0 <= loop["t"] < 0.35)
        self.click("#lp-next")
        time.sleep(0.7)
        second = self.browser.eval("({t:window.__t,text:document.querySelectorAll('#stage [data-t=text]')[1].textContent,pos:document.getElementById('lp-position').textContent})")
        self.assertEqual(second["text"], "SECOND")
        self.assertTrue(0.35 <= second["t"] < 0.7)
        self.assertIn("2 / 2", second["pos"])
        self.click("#lp-mode")
        time.sleep(0.45)
        self.assertEqual(self.browser.eval("document.getElementById('lp-mode').textContent"), "单步模式")
        self.assertTrue(self.browser.eval("document.getElementById('lp-next').disabled"))

    def test_ring_uses_its_real_steps(self):
        self.open_page(self.ring.as_uri())
        self.browser.eval("window.seek(0); document.getElementById('lp-mode').click()")
        self.assertIn("1 / 4", self.browser.eval("document.getElementById('lp-position').textContent"))
        self.click("#lp-next")
        time.sleep(0.7)
        state = self.browser.eval("({t:window.__t,pos:document.getElementById('lp-position').textContent})")
        self.assertIn("2 / 4", state["pos"])
        self.assertIn("Act", state["pos"])
        self.assertTrue(0.3 <= state["t"] < 0.6)

    def test_edit_survives_reload_and_downloaded_html_is_independent(self):
        value = "新标题 </script><b>safe</b>"
        self.edit_text("Panel title", value)
        self.assertIn(value, self.browser.eval("document.getElementById('stage').textContent"))
        self.open_page(self.page.as_uri())
        self.assertIn(value, self.browser.eval("document.getElementById('stage').textContent"))
        downloads = self.root / "downloads"
        downloads.mkdir(exist_ok=True)
        self.browser.cmd("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
        self.click("#lp-export")
        end = time.monotonic() + 10
        while time.monotonic() < end and not list(downloads.glob("*.html")):
            time.sleep(0.1)
        exported = next(downloads.glob("*.html"), None)
        self.assertIsNotNone(exported, "HTML download did not finish")
        self.assertNotIn(value, self.page.read_text(encoding="utf-8"))
        self.open_page(exported.as_uri())
        self.assertIn(value, self.browser.eval("document.getElementById('stage').textContent"))
        self.assertEqual(self.browser.eval("document.querySelectorAll('#stage [data-t=text]').length"), 3)
        self.assertFalse(self.browser.eval("document.getElementById('lp-edit').getAttribute('aria-pressed')==='true'"))
        self.browser.eval("window.seek(0);document.getElementById('lp-mode').click();document.getElementById('lp-next').click()")
        self.assertIn("2 / 2", self.browser.eval("document.getElementById('lp-position').textContent"))
        self.assertIn(value, self.browser.eval("document.getElementById('stage').textContent"))
        self.open_page(exported.as_uri() + "?manual")
        self.assertTrue(self.browser.eval("document.getElementById('lp-controls').hidden"))
        self.browser.seek(0.2)
        self.assertIn(value, self.browser.eval("document.getElementById('stage').textContent"))
        self.assertEqual(self.browser.eval("window.__error||''"), "")

    def test_editing_one_styled_run_preserves_the_dynamic_value(self):
        self.browser.eval("window.seek(0); document.getElementById('lp-mode').click()")
        self.edit_text("Task: ", "Work: ")
        self.click("#lp-next")
        time.sleep(0.15)
        line = self.browser.eval("document.querySelectorAll('#stage [data-t=text]')[2].textContent")
        self.assertEqual(line, "Work: SECOND")

    def test_svg_label_is_editable_and_updates_step_label(self):
        self.open_page(self.ring.as_uri())
        self.browser.eval("window.seek(0); document.getElementById('lp-mode').click()")
        self.edit_text("Plan 规划", "定义目标")
        self.assertIn("定义目标", self.browser.eval("document.getElementById('lp-position').textContent"))
        self.edit_text("1", "①")
        self.open_page(self.ring.as_uri())
        self.assertIn("定义目标", self.browser.eval("document.getElementById('stage').textContent"))
        self.assertIn("①", self.browser.eval("document.getElementById('stage').textContent"))

    def test_other_views_follow_their_own_steps(self):
        for name, expected in (("funnel", "2 / 7"), ("loop", "2 / 31"), ("excalidraw", "2 / 16")):
            with self.subTest(view=name):
                self.open_page(self.views[name].as_uri())
                self.browser.eval("window.seek(0); document.getElementById('lp-mode').click()")
                self.browser.eval("document.getElementById('lp-next').click()")
                self.assertIn(expected, self.browser.eval("document.getElementById('lp-position').textContent"))
                self.assertEqual(self.browser.eval("window.__error||''"), "")

    def test_explicit_steps_and_invalid_ranges(self):
        self.open_page(self.explicit.as_uri())
        self.browser.eval("window.seek(0.15); document.getElementById('lp-mode').click()")
        self.browser.eval("document.getElementById('lp-next').click()")
        time.sleep(0.1)
        state = self.browser.eval("({t:window.__t,pos:document.getElementById('lp-position').textContent})")
        self.assertIn("Second scene", state["pos"])
        self.assertTrue(1.0 <= state["t"] < 1.4)
        self.open_page(self.invalid.as_uri() + "?manual")
        self.assertTrue(any("playback.steps" in problem for problem in self.browser.eval("window.__check()")))

    def test_ambient_loop_can_step_through_its_walk(self):
        self.open_page(self.views["ambient-loop"].as_uri())
        self.browser.eval("window.seek(0); document.getElementById('lp-mode').click()")
        self.assertIn("1 / 31", self.browser.eval("document.getElementById('lp-position').textContent"))
        self.assertEqual(self.browser.eval("document.querySelector('[data-lp-focus-node=watch]').style.opacity"), "1")
        self.browser.eval("document.getElementById('lp-next').click()")
        self.assertEqual(self.browser.eval("document.querySelector('[data-lp-focus-node=watch]').style.opacity"), "0")
        self.assertEqual(self.browser.eval("document.querySelector('[data-lp-focus-node=ticket]').style.opacity"), "1")
        self.browser.eval("document.getElementById('lp-mode').click()")
        self.assertEqual(self.browser.eval("document.querySelector('[data-lp-focus-node=ticket]').style.opacity"), "0")

    def test_different_files_do_not_share_saved_edits(self):
        self.edit_text("Panel title", "独立标题")
        other = self.root / "other.html"
        other.write_bytes(self.page.read_bytes())
        self.open_page(other.as_uri())
        self.assertIn("Panel title", self.browser.eval("document.getElementById('stage').textContent"))
        self.assertNotIn("独立标题", self.browser.eval("document.getElementById('stage').textContent"))

    def test_cancel_restores_the_previous_saved_text(self):
        self.edit_text("Panel title", "已保存标题")
        self.edit_text("已保存标题", "取消的修改", cancel=True)
        self.open_page(self.page.as_uri())
        text = self.browser.eval("document.getElementById('stage').textContent")
        self.assertIn("已保存标题", text)
        self.assertNotIn("取消的修改", text)

    def test_storage_failure_is_visible_and_download_still_works(self):
        self.browser.eval("Storage.prototype.setItem=function(){throw new Error('blocked')}")
        self.edit_text("Panel title", "离线备份标题")
        self.assertIn("无法自动保存", self.browser.eval("document.getElementById('lp-status').textContent"))
        downloads = self.root / "storage-denied"
        downloads.mkdir(exist_ok=True)
        self.browser.cmd("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
        self.click("#lp-export")
        end = time.monotonic() + 10
        while time.monotonic() < end and not list(downloads.glob("*.html")):
            time.sleep(0.1)
        exported = next(downloads.glob("*.html"), None)
        self.assertIsNotNone(exported)
        self.open_page(exported.as_uri())
        self.assertIn("离线备份标题", self.browser.eval("document.getElementById('stage').textContent"))

    def test_mismatched_saved_text_is_reported_instead_of_replacing_another_label(self):
        broken = self.root / "mismatched.html"
        edits = json.dumps({"0:0": {"text": "unexpected", "anchor": "not this page", "count": 1}})
        tag = '<script id="live-edits" type="application/json">' + edits + '</script>'
        broken.write_text(self.page.read_text(encoding="utf-8").replace('</head>', tag + '</head>'), encoding="utf-8")
        self.open_page(broken.as_uri())
        self.assertIn("部分修改未匹配", self.browser.eval("document.getElementById('lp-status').textContent"))
        self.assertIn("Panel title", self.browser.eval("document.getElementById('stage').textContent"))
        self.assertTrue(any("saved text" in problem for problem in self.browser.eval("window.__check()")))


if __name__ == "__main__":
    unittest.main()
