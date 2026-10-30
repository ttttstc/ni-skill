/* ring view — loop / cycle diagram */
(function(){
  LP.registerView('ring', {
    build: function(ctx){
      var e = ctx.e, root = ctx.root, rect = ctx.rect;
      var w = rect.w, h = rect.h;
      var dark = ctx.dark;
      var period = e.period || 28;
      var steps = e.steps || [];
      var n = steps.length;
      if(n < 3) n = 3;
      var u = Math.min(w, h) / 100;
      var cx = w / 2, cy = h / 2;

      // ---- title area ----
      var titleH = 0, subH = 0;
      if(e.title){
        var titleSize = Math.round(u * 3.2);
        titleSize = Math.min(titleSize, 42);
        titleSize = Math.max(titleSize, 22);
        var tf = ctx.fit(e.title, titleSize, w * 0.8, 'var(--font-title)', 18, true);
        var titleEl = ctx.el('div');
        titleEl.style.cssText = 'position:absolute;left:0;top:' + Math.round(u*2) + 'px;width:' + w + 'px;text-align:center;font-family:var(--font-title);font-size:' + tf.size + 'px;line-height:' + Math.round(tf.size*1.3) + 'px;color:' + ctx.cc('fg') + ';font-weight:700;white-space:pre';
        titleEl.textContent = tf.text;
        ctx.mark(titleEl, 'text');
        root.appendChild(titleEl);
        titleH = Math.round(tf.size * 1.3) + u*2;
      }
      if(e.subtitle){
        var subSize = Math.round(u * 1.8);
        subSize = Math.min(subSize, 22);
        subSize = Math.max(subSize, 13);
        var sf = ctx.fit(e.subtitle, subSize, w * 0.7, null, 11);
        var subEl = ctx.el('div');
        subEl.style.cssText = 'position:absolute;left:0;top:' + Math.round(titleH + u*0.5) + 'px;width:' + w + 'px;text-align:center;font-size:' + sf.size + 'px;line-height:' + Math.round(sf.size*1.4) + 'px;color:' + ctx.cc('muted') + ';white-space:pre';
        subEl.textContent = sf.text;
        ctx.mark(subEl, 'text');
        root.appendChild(subEl);
        subH = Math.round(sf.size * 1.4);
      }
      var topPad = titleH + subH + u*2;

      // ---- layout ----
      var availH = h - topPad - u*2;
      var availW = w - u*4;
      var maxLab = 0;
      for(var q=0;q<steps.length;q++){
        var lw = ctx.measure(steps[q].label||'', Math.round(u*2.3), ctx.TH.titleFont, true);
        if(steps[q].desc) lw = Math.max(lw, ctx.measure(steps[q].desc, Math.round(u*1.6), null));
        maxLab = Math.max(maxLab, Math.min(lw, u*17));
      }
      var sideRoom = maxLab + u*2.8*1.25 + u*4.5;   // node radius + gap + label + margin
      var vRoom = u*2.8*1.25 + u*3 + Math.round(u*2.3)*1.25 + Math.round(u*1.6)*1.3 + u*1.5;
      var ringR = Math.min(availW/2 - sideRoom, availH/2 - vRoom);
      ringR = Math.max(ringR, u*18);
      cy = topPad + availH/2;

      // SVG
      var svg = ctx.svg('svg', {width: w, height: h});
      svg.style.cssText = 'position:absolute;left:0;top:0;overflow:visible;pointer-events:none';
      root.appendChild(svg);

      // outer ring track (static, faint)
      var track = ctx.svg('circle', {
        cx: cx, cy: cy, r: ringR,
        fill: 'none',
        stroke: ctx.cc('grid'),
        'stroke-width': dark ? 1.2 : 1.5
      });
      svg.appendChild(track);

      // step segments (arcs between steps)
      var stepAngle = 2 * Math.PI / n;
      // angles: step i is at angle = -PI/2 + i*stepAngle (start at top, go clockwise)
      function angleAt(i){ return -Math.PI/2 + i * stepAngle; }
      function ptOnRing(ang, r){
        return [cx + Math.cos(ang)*r, cy + Math.sin(ang)*r];
      }

      // arc path between step i and step i+1
      function arcPath(i){
        var a0 = angleAt(i) + stepAngle * 0.12;
        var a1 = angleAt((i+1)%n) - stepAngle * 0.12;
        var p0 = ptOnRing(a0, ringR);
        var p1 = ptOnRing(a1, ringR);
        var largeArc = (a1 - a0) > Math.PI ? 1 : 0;
        return 'M' + p0[0] + ',' + p0[1] + ' A' + ringR + ',' + ringR + ' 0 ' + largeArc + ' 1 ' + p1[0] + ',' + p1[1];
      }

      // arrow heads on arcs
      function arrowHead(i){
        var a = angleAt((i+1)%n) - stepAngle * 0.12;
        var tp = ptOnRing(a, ringR);
        var ap = ptOnRing(a - 0.15, ringR);
        var dx = tp[0]-ap[0], dy = tp[1]-ap[1];
        var L = Math.hypot(dx,dy)||1; dx/=L; dy/=L;
        var sz = u*1.2;
        var bx = tp[0]-dx*sz, by = tp[1]-dy*sz;
        return tp[0]+','+tp[1]+' '+(bx-dy*sz*0.5)+','+(by+dx*sz*0.5)+' '+(bx+dy*sz*0.5)+','+(by-dx*sz*0.5);
      }

      var arcPaths = [];
      var arrowHeads = [];
      for(var i=0;i<n;i++){
        var ap_ = ctx.svg('path', {
          d: arcPath(i),
          fill: 'none',
          stroke: ctx.cc('line2'),
          'stroke-width': dark ? 1.5 : 2,
          'stroke-linecap': 'round'
        });
        svg.appendChild(ap_);
        arcPaths.push(ap_);
        var ah = ctx.svg('polygon', {
          points: arrowHead(i),
          fill: ctx.cc('line2')
        });
        svg.appendChild(ah);
        arrowHeads.push(ah);
      }

      // step nodes + labels
      var nodeR = u * 2.8;
      var stepNodes = [];
      var stepLabels = [];
      var stepDescs = [];
      for(var i=0;i<n;i++){
        var a = angleAt(i);
        var p = ptOnRing(a, ringR);
        // node circle
        var nd = ctx.svg('circle', {
          cx: p[0], cy: p[1], r: nodeR,
          fill: ctx.cc('panel'),
          stroke: ctx.cc('line'),
          'stroke-width': 1.5
        });
        svg.appendChild(nd);
        // step number inside node
        var nt = ctx.svg('text', {
          x: p[0], y: p[1],
          'text-anchor': 'middle',
          'dominant-baseline': 'central',
          fill: ctx.cc('muted'),
          'font-size': Math.round(u*1.9),
          'font-family': 'var(--font)'
        });
        nt.textContent = String(i+1);
        svg.appendChild(nt);

        // label outside
        var labelR = ringR + nodeR + u*3;
        var lp = ptOnRing(a, labelR);
        var anchor = 'middle';
        var dx = 0;
        if(Math.cos(a) > 0.2){ anchor = 'start'; dx = u*1; }
        else if(Math.cos(a) < -0.2){ anchor = 'end'; dx = -u*1; }
        var lab = steps[i] ? steps[i].label : ('step '+(i+1));
        var labMaxW = u * 17;
        var labSize = Math.round(u*2.3);
        var lf = ctx.fit(lab, labSize, labMaxW, 'var(--font-title)', 11, true);
        var hasDesc = !!(steps[i] && steps[i].desc);
        var dSz = Math.round(u*1.6);
        var gapY = lf.size*0.62 + dSz*0.62 + u*0.45;
        var isTop = Math.sin(a) < -0.5;
        var labY = (hasDesc && isTop) ? lp[1] - gapY : lp[1];
        var descY = (hasDesc && isTop) ? lp[1] : lp[1] + gapY;
        var lt = ctx.svg('text', {
          x: lp[0]+dx, y: labY,
          'text-anchor': anchor,
          'dominant-baseline': 'central',
          fill: ctx.cc('fg'),
          'font-size': lf.size,
          'font-family': 'var(--font-title)',
          'font-weight': '700'
        });
        lt.textContent = lf.text;
        svg.appendChild(lt);
        ctx.mark(lt, 'text');

        // description below label
        if(steps[i] && steps[i].desc){
          var descMaxW = u * 17;
          var descSize = Math.round(u*1.6);
          var df = ctx.fit(steps[i].desc, descSize, descMaxW, null, 11);
          var dt = ctx.svg('text', {
            x: lp[0]+dx, y: descY,
            'text-anchor': anchor,
            'dominant-baseline': 'central',
            fill: ctx.cc('muted'),
            'font-size': df.size,
            'font-family': 'var(--font)'
          });
          dt.textContent = df.text;
          svg.appendChild(dt);
          ctx.mark(dt, 'text');
          stepDescs.push({el: dt, y: descY});
        }

        stepNodes.push({circle: nd, num: nt, x: p[0], y: p[1], a: a});
        stepLabels.push({el: lt, x: lp[0]+dx, y: lp[1]});
      }

      // comet (glowing dot + tail)
      var cometR = u * 1.9;
      var comet = ctx.svg('circle', {
        cx: 0, cy: 0, r: cometR,
        fill: ctx.cc('acc1'),
        stroke: 'none'
      });
      svg.appendChild(comet);

      // comet glow
      var glow = ctx.svg('circle', {
        cx: 0, cy: 0, r: cometR * 3,
        fill: ctx.cc('acc1'),
        opacity: dark ? 0.25 : 0.18
      });
      svg.appendChild(glow);

      // inner sub-loop (optional spokes / inner cycle)
      var innerR = ringR * 0.45;
      var innerCircle = null;
      var innerLabel = null;
      var innerIter = null;
      if(e.innerLoop){
        innerCircle = ctx.svg('circle', {
          cx: cx, cy: cy, r: innerR,
          fill: dark ? ctx.cc('panel') : ctx.cc('accf1'),
          stroke: ctx.cc('line2'),
          'stroke-width': dark ? 1 : 1.2,
          opacity: 0.7
        });
        svg.appendChild(innerCircle);
        ctx.mark(innerCircle, 'frame');
      }
      var innerItems = [];
      var innerList = Array.isArray(e.innerLoop) ? e.innerLoop : [];
      for(var k=0;k<innerList.length;k++){
        var ia = -Math.PI/2 + k * 2*Math.PI/innerList.length;
        var ip = ptOnRing(ia, innerR*1.22);
        var itf = ctx.fit(innerList[k], Math.round(u*1.5), u*10, null, 11);
        var it = ctx.svg('text', {x: ip[0], y: ip[1], 'text-anchor':'middle', 'dominant-baseline':'central',
          fill: ctx.cc('muted'), 'font-size': itf.size, 'font-family':'var(--font)'});
        it.textContent = itf.text; svg.appendChild(it); ctx.mark(it, 'text'); innerItems.push(it);
      }

      // center text: loop name + iteration
      var loopName = e.name || e.title || 'Loop';
      var nf = ctx.fit(loopName, Math.round(u*2.2), innerR*1.6, 'var(--font-title)', 11, true);
      var centerName = ctx.svg('text', {
        x: cx, y: cy - u*1.5,
        'text-anchor': 'middle',
        'dominant-baseline': 'central',
        fill: ctx.cc('fg'),
        'font-size': nf.size,
        'font-family': 'var(--font-title)',
        'font-weight': '700'
      });
      centerName.textContent = nf.text;
      svg.appendChild(centerName);
      ctx.mark(centerName, 'text');

      var iterLabel = ctx.svg('text', {
        x: cx, y: cy + u*1.5,
        'text-anchor': 'middle',
        'dominant-baseline': 'central',
        fill: ctx.cc('fg'),
        'font-size': Math.round(u*2.8),
        'font-family': 'var(--font-title)',
        'font-weight': '700',
        'font-variant-numeric': 'tabular-nums'
      });
      iterLabel.textContent = '#1';
      svg.appendChild(iterLabel);
      ctx.mark(iterLabel, 'text');

      var iterSub = ctx.svg('text', {
        x: cx, y: cy + u*4.2,
        'text-anchor': 'middle',
        'dominant-baseline': 'central',
        fill: ctx.cc('muted'),
        'font-size': Math.round(u*1.5),
        'font-family': 'var(--font)'
      });
      iterSub.textContent = 'iteration';
      svg.appendChild(iterSub);
      ctx.mark(iterSub, 'text');

      // ---- state for seek ----
      var _st = {
        cx:cx, cy:cy, ringR:ringR, n:n, stepAngle:stepAngle, period:period,
        comet:comet, glow:glow, iterLabel:iterLabel,
        stepNodes:stepNodes, arcPaths:arcPaths, arrowHeads:arrowHeads,
        innerCircle:innerCircle, nodeR:nodeR, u:u, dark:dark, innerItems:innerItems, innerStep:(e.innerLoopStep==null?1:e.innerLoopStep),
        accentIdx: 0
      };
      return _st;
    },

    seek: function(t, ctx, st){
      var s = st || (ctx && ctx.state);
      if(!s) return;
      var cx = s.cx, cy = s.cy, ringR = s.ringR, n = s.n;
      var stepAngle = s.stepAngle, period = s.period;

      // single truth: comet angle (full circle per period)
      var uT = (t / period); // normalized 0..1 per lap
      var lap = Math.floor(uT);
      var phase = uT - lap; // 0..1 within current lap
      var angle = -Math.PI/2 + phase * 2 * Math.PI;

      // comet position
      var cxp = cx + Math.cos(angle)*ringR;
      var cyp = cy + Math.sin(angle)*ringR;
      s.comet.setAttribute('cx', cxp);
      s.comet.setAttribute('cy', cyp);
      s.glow.setAttribute('cx', cxp);
      s.glow.setAttribute('cy', cyp);

      // iteration counter (pad to keep width stable)
      var iterNum = lap + 1;
      var iterStr = '#' + iterNum;
      if(s.iterLabel.textContent !== iterStr){
        s.iterLabel.textContent = iterStr;
      }

      // current step = floor(phase * n)
      var curStep = Math.floor(phase * n);
      if(curStep >= n) curStep = n-1;

      // highlight current step (slow tempo: the step changes every period/n seconds)
      var stepPhase = (phase * n) - curStep; // 0..1 within current step

      for(var i=0;i<n;i++){
        var node = s.stepNodes[i];
        var ap = s.arcPaths[i];
        var ah = s.arrowHeads[i];
        var isCur = (i === curStep);
        var isNext = (i === (curStep+1)%n);
        // arc leading to curStep: accented
        if(isCur){
          // arc i runs from step i to step i+1: the one the comet is travelling along
          ap.setAttribute('stroke', ctx.cc(ctx.acc(s.accentIdx)));
          ap.setAttribute('stroke-width', s.dark ? 2.5 : 3);
          ap.setAttribute('opacity', '1');
          ah.setAttribute('fill', ctx.cc(ctx.acc(s.accentIdx)));
        } else if(isNext && stepPhase > 0.7){
          // approaching next step
          var k = (stepPhase - 0.7)/0.3;
          ap.setAttribute('stroke', ctx.cc(ctx.acc(s.accentIdx)));
          ap.setAttribute('stroke-width', s.dark ? 1.5 + k : 2 + k);
          ap.setAttribute('opacity', String(0.4 + 0.6*k));
          ah.setAttribute('fill', ctx.cc(ctx.acc(s.accentIdx)));
        } else {
          ap.setAttribute('stroke', ctx.cc('line2'));
          ap.setAttribute('stroke-width', s.dark ? 1.5 : 2);
          ap.setAttribute('opacity', s.dark ? '0.5' : '0.7');
          ah.setAttribute('fill', ctx.cc('line2'));
        }

        // node highlight
        if(isCur){
          node.circle.setAttribute('fill', ctx.cc(ctx.accf(s.accentIdx)));
          node.circle.setAttribute('stroke', ctx.cc(ctx.acc(s.accentIdx)));
          node.circle.setAttribute('stroke-width', '2.5');
          node.circle.setAttribute('r', String(s.nodeR * 1.25));
          node.num.setAttribute('fill', ctx.cc(ctx.acc(s.accentIdx)));
          node.num.setAttribute('font-weight', '700');
        } else {
          node.circle.setAttribute('fill', ctx.cc('panel'));
          node.circle.setAttribute('stroke', ctx.cc('line'));
          node.circle.setAttribute('stroke-width', '1.5');
          node.circle.setAttribute('r', String(s.nodeR));
          node.num.setAttribute('fill', ctx.cc('muted'));
          node.num.setAttribute('font-weight', '400');
        }
      }

      // inner sub-loop: medium tempo, one item lit per 1.2 s, only while its parent step runs
      if(s.innerItems.length){
        var on = (curStep === s.innerStep);
        var lit = Math.floor(t / 1.2) % s.innerItems.length;
        for(var j=0;j<s.innerItems.length;j++){
          var hot = on && j === lit;
          s.innerItems[j].setAttribute('fill', hot ? ctx.cc('fg') : ctx.cc('muted'));
          s.innerItems[j].setAttribute('font-weight', hot ? '700' : '400');
        }
      }
      // comet pulsing (fast tempo)
      // pulse frequency is a whole number of cycles per lap, so the loop has no jump
      var pulseK = Math.max(1, Math.round(6*period/(2*Math.PI)));
      var pulse = 1 + 0.15 * Math.sin(2*Math.PI*pulseK*t/period);
      s.comet.setAttribute('r', String(s.u*1.9 * pulse));
    },

    check: function(ctx){
      var e = ctx.e;
      var msgs = [];
      if(!e.steps || !e.steps.length) msgs.push('ring: steps is required (3-8 items)');
      else if(e.steps.length < 3 || e.steps.length > 8) msgs.push('ring: steps must have 3-8 items');
      return msgs;
    }
  });
})();
