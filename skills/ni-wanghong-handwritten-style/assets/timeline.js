/* z-wanghong-handwritten-timeline :: timeline.js
 * 把王虹手写 HTML 变成带时间轴的演示，逐条出现，接近 Office PPT 的动画手感。
 *
 * 每一页被拆成若干“步骤”：标题、每个框、每个箭头、每一行文字、每张图都各自一步。
 * 默认手动模式：进入页面先出现标题，之后按一下空格 / 回车 / 点击画面，只出现下一步。
 * 开启自动连播后，每一步自动间隔出现，全部出完自动翻页。
 *
 * 操作：
 *   → / 空格 / 回车 / 点击画面   下一步（当前页还有内容就出下一条；出完了就翻下一页）
 *   ← / Backspace               上一步（当前页回退一条；回退到标题后再按，翻上一页）
 *   Home / End                  首页 / 末页
 *   F                           全屏
 *
 * 底部控制条：首页 / 上一步 / 重播本页 / 下一步 / 自动连播 / 全屏。
 */
(function () {
  'use strict';

  var CFG = {
    stepDur: 450,        // 每条目入场过渡时长 ms
    titleDur: 520,       // 标题组过渡时长 ms
    svgDur: 1300,        // SVG 描画时长 ms
    svgStagger: 70,      // 同一张图内线条之间的间隔 ms
    markerDelay: 420,    // 条目出现后荧光再隔多久揭示 ms
    markerDur: 700,      // 荧光揭示时长 ms
    autoStepDelay: 1300, // 自动连播：每步间隔 ms
    autoNextDelay: 2200, // 自动连播：全部出完后停留多久翻页 ms
    wipeDur: 330,        // 纸张转场时长 ms
    barHideDelay: 2800,  // 控制条自动隐藏 ms
  };

  var slides = [];
  var cur = 0;
  var shown = 0;          // 当前页已显示的步骤数（至少 1 = 标题）
  var autoPlay = false;
  var busy = false;
  var animTimers = [];    // 元素动画（线条描画、荧光揭示）的计时器
  var autoTimers = [];    // 自动步进、自动翻页的计时器
  var barHideTimer = 0;

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function schedule(fn, delay, list) {
    var id = setTimeout(fn, delay);
    list.push(id);
    return id;
  }

  function scheduleAnim(fn, delay) {
    return schedule(fn, delay, animTimers);
  }

  function scheduleAuto(fn, delay) {
    return schedule(fn, delay, autoTimers);
  }

  function clearList(list) {
    list.forEach(function (id) {
      clearTimeout(id);
    });
    list.length = 0;
  }

  function clearAnimTimers() {
    clearList(animTimers);
  }

  function clearAutoTimers() {
    clearList(autoTimers);
  }

  function clearAllTimers() {
    clearAnimTimers();
    clearAutoTimers();
  }

  function isBlockish(el) {
    var tag = el.tagName || '';
    if (el.matches && el.matches('svg')) return true;
    return [
      'DIV', 'P', 'UL', 'OL', 'LI', 'TABLE', 'TR', 'TD', 'SECTION',
      'CODE', 'H1', 'H2', 'H3', 'H4', 'H5', 'FIGURE', 'BLOCKQUOTE', 'HR', 'PRE',
    ].indexOf(tag) >= 0;
  }

  /* 把一个内容容器拆成“一条一条”的步骤元素。
   * 规则：容器里如果有多个平级内容元素就拆开；拆到叶子（文字行、框、箭头）为止；
   * 行内装饰（span/b/i）和图表 svg 不再往下拆。 */
  function flatten(el, depth) {
    if (depth >= 2 || (el.matches && el.matches('svg'))) return [el];
    var children = Array.prototype.slice.call(el.children).filter(function (c) {
      return !c.matches('.notes, aside.notes, .speaker-notes, script');
    });
    if (children.length < 2) return [el];

    var svgs = children.filter(function (c) {
      return c.matches && c.matches('svg');
    });
    var rest = children.filter(function (c) {
      return !(c.matches && c.matches('svg'));
    });
    if (svgs.length) {
      var out = svgs.slice();
      rest.forEach(function (c) {
        out = out.concat(flatten(c, depth + 1));
      });
      return out;
    }

    var blocky = rest.filter(isBlockish);
    if (blocky.length >= 2) {
      var result = [];
      rest.forEach(function (c) {
        result = result.concat(flatten(c, depth + 1));
      });
      return result;
    }
    return [el];
  }

  /* ---------- 页面准备：识别标题、条目、描边与荧光元素 ---------- */
  function prepareSlide(slide) {
    var children = $$(':scope > *', slide).filter(function (el) {
      return !el.matches('.notes, aside.notes, .speaker-notes');
    });

    var titleGroup = null;
    children.forEach(function (el) {
      if (!titleGroup && el.matches && el.matches('.page-heading')) titleGroup = el;
    });
    if (!titleGroup) {
      children.forEach(function (el) {
        if (!titleGroup && el.querySelector && el.querySelector('.hand-title, .slide-title, h1, h2')) {
          titleGroup = el;
        }
      });
    }

    var blocks = children.filter(function (el) {
      return el !== titleGroup;
    });
    var blockSteps = [];
    blocks.forEach(function (b) {
      blockSteps = blockSteps.concat(flatten(b, 0));
    });
    var steps = [];
    if (titleGroup) steps.push(titleGroup);
    steps = steps.concat(blockSteps);

    var svgEls = [];
    var svgFill = [];
    $$('svg path, svg line, svg polyline, svg rect, svg circle, svg ellipse', slide).forEach(function (el) {
      var attrStroke = (el.getAttribute('stroke') || '').trim();
      var cs = getComputedStyle(el);
      var stroke = (attrStroke || cs.stroke || '').toString().trim();
      var hasStroke = stroke && stroke !== 'none' && !/^rgba\(0,\s*0,\s*0,\s*0\)$/.test(stroke);
      if (hasStroke) {
        el.setAttribute('pathLength', '1');
        el.classList.add('tl-svg');
        svgEls.push(el);
      } else {
        el.classList.add('tl-svg-fill');
        svgFill.push(el);
      }
    });

    var markers = [];
    $$('.marker, .marker-yellow, .marker-green, .marker-coral, [class*="mark-"]', slide).forEach(function (el) {
      el.classList.add('tl-marker');
      markers.push(el);
    });

    var lines = [];
    $$('.title-line', slide).forEach(function (el) {
      el.classList.add('tl-line');
      lines.push(el);
    });

    steps.forEach(function (el) {
      el.classList.add('tl-group');
    });

    slide.__tl = {
      titleGroup: titleGroup,
      steps: steps,
      svg: svgEls,
      svgFill: svgFill,
      markers: markers,
      lines: lines,
    };
  }

  /* ---------- 步骤控制 ---------- */
  function tlOf(idx) {
    return slides[idx].__tl;
  }

  function setProgress(p) {
    var el = $('#tl-progress');
    if (el) el.style.width = (p * 100) + '%';
  }

  function totalSteps(idx) {
    return tlOf(idx).steps.length;
  }

  /* 让一个元素“进入”：自身淡入，内部的图开始描画，荧光随后揭示 */
  function revealEl(el, isTitle) {
    var dur = isTitle ? CFG.titleDur : CFG.stepDur;
    el.style.transitionDuration = dur + 'ms';
    el.classList.add('tl-in');
    var svgs = el.querySelectorAll ? $$('.tl-svg', el) : [];
    var fills = el.querySelectorAll ? $$('.tl-svg-fill', el) : [];
    var marks = el.querySelectorAll ? $$('.tl-marker', el) : [];
    if (svgs.length || fills.length) {
      scheduleAnim(function () {
        svgs.forEach(function (s, j) {
          scheduleAnim(function () {
            s.classList.add('tl-svg-in');
          }, j * CFG.svgStagger);
        });
        fills.forEach(function (f, j) {
          scheduleAnim(function () {
            f.classList.add('tl-svg-in');
          }, j * Math.min(CFG.svgStagger, 50));
        });
      }, 120);
    }
    if (marks.length) {
      scheduleAnim(function () {
        marks.forEach(function (m, j) {
          scheduleAnim(function () {
            m.classList.add('tl-marker-in');
          }, j * 80);
        });
      }, CFG.markerDelay);
    }
  }

  function revealStep(idx, stepIndex) {
    var tl = tlOf(idx);
    var el = tl.steps[stepIndex];
    if (!el) return;
    if (el === tl.titleGroup) {
      revealEl(el, true);
      tl.lines.forEach(function (l) {
        scheduleAnim(function () {
          l.classList.add('tl-in');
        }, 60);
      });
    } else {
      revealEl(el, false);
    }
  }

  function hideStep(idx, stepIndex) {
    var tl = tlOf(idx);
    var els = [tl.steps[stepIndex]];
    if (tl.steps[stepIndex] === tl.titleGroup) {
      els = els.concat(tl.lines);
    }
    els.forEach(function (el) {
      el.classList.remove('tl-in');
      var inner = el.querySelectorAll ? el.querySelectorAll('.tl-svg, .tl-svg-fill, .tl-marker') : [];
      Array.prototype.slice.call(inner).forEach(function (c) {
        c.classList.remove('tl-svg-in', 'tl-marker-in');
      });
    });
  }

  /* 当前页所有元素一步到位全部显示（用于回到上一页时快速查看） */
  function showAll(idx) {
    clearAllTimers();
    var deck = $('.deck');
    var tl = tlOf(idx);
    deck.classList.add('tl-instant');
    void document.body.offsetWidth;
    tl.steps.forEach(function (el) {
      el.classList.add('tl-in');
    });
    tl.lines.forEach(function (l) {
      l.classList.add('tl-in');
    });
    tl.svg.forEach(function (el) {
      el.classList.add('tl-svg-in');
    });
    tl.svgFill.forEach(function (el) {
      el.classList.add('tl-svg-in');
    });
    tl.markers.forEach(function (el) {
      el.classList.add('tl-marker-in');
    });
    shown = totalSteps(idx);
    setProgress(1);
  }

  /* 从标题开始播放当前页（手动模式：出完标题后等待操作） */
  function playSlide(idx) {
    clearAllTimers();
    var deck = $('.deck');
    var tl = tlOf(idx);
    deck.classList.add('tl-instant');
    void document.body.offsetWidth;
    var all = tl.steps.concat(tl.lines, tl.svg, tl.svgFill, tl.markers);
    all.forEach(function (el) {
      el.classList.remove('tl-in', 'tl-svg-in', 'tl-marker-in');
    });
    deck.classList.remove('tl-instant');
    void document.body.offsetWidth;

    shown = 0;
    setProgress(0);
    revealStep(idx, 0);
    shown = 1;
    setProgress(shown / totalSteps(idx));
    if (autoPlay) scheduleAutoStep();
  }

  function scheduleAutoStep() {
    clearAutoTimers();
    if (!autoPlay) return;
    var total = totalSteps(cur);
    if (shown >= total) {
      scheduleAuto(function () {
        if (autoPlay) nextPage();
      }, CFG.autoNextDelay);
      return;
    }
    scheduleAuto(function () {
      if (autoPlay && shown < total) stepForward();
    }, CFG.autoStepDelay);
  }

  /* ---------- 上一步 / 下一步 ---------- */
  function stepForward() {
    if (busy) return;
    var total = totalSteps(cur);
    if (shown < total) {
      clearAutoTimers();
      revealStep(cur, shown);
      shown += 1;
      setProgress(shown / total);
      if (autoPlay) scheduleAutoStep();
    } else {
      nextPage();
    }
  }

  function stepBack() {
    if (busy) return;
    if (shown > 1) {
      clearAutoTimers();
      hideStep(cur, shown - 1);
      shown -= 1;
      setProgress(shown / totalSteps(cur));
      if (autoPlay) scheduleAutoStep();
    } else if (cur > 0) {
      // 已经回退到只剩标题，再按就回上一页，上一页直接完整显示
      showSlide(cur - 1, false, true);
    }
  }

  function nextPage() {
    if (cur >= slides.length - 1) return;
    showSlide(cur + 1, true, true);
  }

  /* ---------- 页面切换 ---------- */
  function switchNow(idx, animate) {
    // 瞬间切换页面：先关过渡再切 class，避免新旧两页淡入淡出叠加出残影
    var deck = $('.deck');
    deck.classList.add('tl-instant');
    void document.body.offsetWidth;
    slides.forEach(function (s, i) {
      var active = i === idx;
      s.classList.toggle('is-active', active);
      // 非激活页直接移出渲染，任何残留都不可能出现
      s.style.display = active ? '' : 'none';
    });
    deck.classList.remove('tl-instant');
    void document.body.offsetWidth;
    cur = idx;
    if (location.hash !== '#/' + (idx + 1)) {
      history.replaceState(null, '', '#/' + (idx + 1));
    }
    updateBar();
    busy = false;
    if (animate) playSlide(idx);
    else showAll(idx);
  }

  function showSlide(idx, animate, wipe) {
    if (busy) return;
    idx = Math.max(0, Math.min(slides.length - 1, idx));
    if (idx === cur) {
      if (animate) playSlide(idx);
      return;
    }
    busy = true;
    clearAllTimers();
    var wipeEl = $('#tl-wipe');
    if (!wipe) {
      switchNow(idx, animate);
      return;
    }
    wipeEl.classList.add('on');
    scheduleAuto(function () {
      switchNow(idx, animate);
      wipeEl.classList.remove('on');
    }, CFG.wipeDur);
  }

  /* ---------- 键盘与点击 ---------- */
  function onKey(e) {
    var tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    var k = e.key;
    if (k === 'ArrowRight' || k === ' ' || k === 'Enter' || k === 'PageDown') {
      e.preventDefault();
      e.stopPropagation();
      stepForward();
      showBar();
    } else if (k === 'ArrowLeft' || k === 'Backspace' || k === 'PageUp') {
      e.preventDefault();
      e.stopPropagation();
      stepBack();
      showBar();
    } else if (k === 'Home') {
      e.preventDefault();
      e.stopPropagation();
      showSlide(0, true, true);
      showBar();
    } else if (k === 'End') {
      e.preventDefault();
      e.stopPropagation();
      showSlide(slides.length - 1, true, true);
      showBar();
    } else if (k === 'f' || k === 'F') {
      e.preventDefault();
      e.stopPropagation();
      toggleFullscreen();
      showBar();
    }
  }

  function onClick(e) {
    if (e.target.closest && e.target.closest('#tl-bar, #tl-progress')) return;
    stepForward();
    showBar();
  }

  function toggleFullscreen() {
    if (document.fullscreenElement) {
      if (document.exitFullscreen) document.exitFullscreen();
    } else if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
    }
  }

  /* ---------- 控制条 ---------- */
  function buildUI() {
    var deck = $('.deck');
    var wipe = document.createElement('div');
    wipe.id = 'tl-wipe';
    deck.appendChild(wipe);

    var bar = document.createElement('div');
    bar.id = 'tl-bar';
    bar.innerHTML =
      '<span id="tl-title"></span>' +
      '<button type="button" data-act="home" title="首页">⏮</button>' +
      '<button type="button" data-act="prev" title="上一步">◀</button>' +
      '<button type="button" data-act="replay" title="重播本页">↻</button>' +
      '<button type="button" data-act="next" title="下一步">▶</button>' +
      '<button type="button" data-act="auto" title="自动连播">▶▶</button>' +
      '<button type="button" data-act="fs" title="全屏 (F)">⛶</button>' +
      '<span id="tl-count"></span>';
    document.body.appendChild(bar);

    var progress = document.createElement('div');
    progress.id = 'tl-progress';
    document.body.appendChild(progress);

    bar.addEventListener('click', function (e) {
      var btn = e.target.closest && e.target.closest('button[data-act]');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      var act = btn.getAttribute('data-act');
      if (act === 'home') showSlide(0, true, true);
      else if (act === 'prev') stepBack();
      else if (act === 'next') stepForward();
      else if (act === 'replay') playSlide(cur);
      else if (act === 'auto') {
        autoPlay = !autoPlay;
        btn.classList.toggle('active', autoPlay);
        if (autoPlay) scheduleAutoStep();
        else clearAutoTimers();
      } else if (act === 'fs') {
        toggleFullscreen();
      }
      showBar();
    });

    document.addEventListener('mousemove', function () {
      showBar();
    });
    document.addEventListener('touchstart', function () {
      showBar();
    }, { passive: true });
  }

  function updateBar() {
    var t = $('#tl-title');
    var c = $('#tl-count');
    if (t && slides[cur]) t.textContent = slides[cur].getAttribute('data-title') || '';
    if (c) c.textContent = (cur + 1) + ' / ' + slides.length;
    var autoBtn = $('button[data-act="auto"]');
    if (autoBtn) autoBtn.classList.toggle('active', autoPlay);
  }

  function showBar() {
    var bar = $('#tl-bar');
    if (!bar) return;
    bar.classList.add('show');
    clearTimeout(barHideTimer);
    barHideTimer = setTimeout(function () {
      bar.classList.remove('show');
    }, CFG.barHideDelay);
  }

  /* ---------- 窗口适配与初始化 ---------- */
  function fitToWindow() {
    var deck = $('.deck');
    if (!deck) return;
    var scale = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    deck.style.setProperty('--tl-scale', String(Math.max(scale, 0.1)));
  }

  function onHashChange() {
    var m = /#\/(\d+)/.exec(location.hash);
    if (!m) return;
    var idx = Math.min(Math.max(parseInt(m[1], 10) - 1, 0), slides.length - 1);
    if (idx === cur) return;
    showSlide(idx, true, true);
  }

  function init() {
    var deck = $('.deck');
    if (!deck) return;
    slides = $$('.deck > .slide');
    if (!slides.length) return;

    var m = /#\/(\d+)/.exec(location.hash);
    if (m) cur = Math.min(Math.max(parseInt(m[1], 10) - 1, 0), slides.length - 1);

    slides.forEach(prepareSlide);
    deck.classList.add('tl-ready');
    buildUI();
    fitToWindow();
    window.addEventListener('resize', fitToWindow);
    document.addEventListener('keydown', onKey, true);
    document.addEventListener('click', onClick);
    window.addEventListener('hashchange', onHashChange);

    slides.forEach(function (s, i) {
      var active = i === cur;
      s.classList.toggle('is-active', active);
      s.style.display = active ? '' : 'none';
    });
    updateBar();
    playSlide(cur);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
