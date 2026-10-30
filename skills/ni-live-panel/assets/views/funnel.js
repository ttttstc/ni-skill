// live-panel view: funnel — pipeline / conversion chart
// Self-registers via LP.registerView. Contract and config keys: references/views.md.
(function(){
  var NS = 'http://www.w3.org/2000/svg';

  function svg(ctx, tag, attrs){
    var n = document.createElementNS(NS, tag);
    if(attrs){
      Object.keys(attrs).forEach(function(k){ n.setAttribute(k, attrs[k]); });
    }
    return n;
  }

  function el(tag, cls, style){
    var n = document.createElement(tag||'div');
    if(cls) n.className = cls;
    if(style) n.style.cssText = style;
    return n;
  }

  function fmtNum(v){
    // compact for population-scale numbers: 8B, 1.5B, 20M; commas below a million
    // thresholds sit where the rounded value reaches the next unit (999,960,000 -> 1B, not 1000M)
    var a = Math.abs(v);
    if(a >= 9.9995e8) return String(Math.round(v/1e8)/10) + 'B';
    if(a >= 999999.5) return String(Math.round(v/1e5)/10) + 'M';
    var s = String(Math.round(v));
    return s.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  function fmtPct(p){
    // String() switches to exponent notation below 1e-6 (8B -> 5 is 6.3e-8 %)
    var s = String(p);
    return s.indexOf('e') < 0 ? s : p.toFixed(1 - Math.floor(Math.log10(p)));
  }

  LP.registerView('funnel', {
    build: function(ctx){
      var e = ctx.e, rect = ctx.rect, root = ctx.root;
      var w = rect.w, h = rect.h;
      var dark = ctx.dark;
      var u = Math.min(w, h)/100;
      var stages = (e.stages||[]).map(function(s,i){ return {label:s.label,sub:s.sub||'',value:Number(s.value)||0,i:i}; });
      var n = stages.length;

      // ---- title block (drawn inside root) ----
      var topPad = Math.round(u*2), botPad = Math.round(u*1.5);
      var titleH = topPad, subH = 0;
      if(e.title){
        var titleSize = Math.max(22, Math.min(u*3.2, 46));
        var titleLh = Math.round(titleSize*1.25);
        var titleEl = el('div', null,
          'position:absolute;left:0;right:0;top:'+topPad+'px;height:'+titleLh+'px;line-height:'+titleLh+'px;text-align:center;font-family:var(--font-title);font-size:'+titleSize+'px;font-weight:700;color:'+ctx.cc('fg')+';white-space:pre;');
        titleEl.textContent = e.title;
        ctx.mark(titleEl,'text');
        root.appendChild(titleEl);
        titleH += titleLh;
      }
      if(e.subtitle){
        var subSize = Math.max(13, Math.min(u*1.6, 19));
        var subLh = Math.round(subSize*1.4);
        var subEl = el('div', null,
          'position:absolute;left:0;right:0;top:'+titleH+'px;height:'+subLh+'px;line-height:'+subLh+'px;text-align:center;font-size:'+subSize+'px;color:'+ctx.cc('muted')+';white-space:pre;letter-spacing:0.5px;');
        subEl.textContent = e.subtitle;
        ctx.mark(subEl,'text');
        root.appendChild(subEl);
        subH = subLh;
      }

      var headH = titleH + subH + Math.round(u*1.6);

      // ---- layout ----
      var marginX = Math.round(u*5);
      var bodyTop = headH;
      var bodyH = h - headH - botPad;
      var bodyW = w - marginX*2;
      var cy = bodyTop + bodyH/2;

      // vertical span per stage
      var convPillH0 = Math.round(u*2.8);
      var stageGap = convPillH0 + 8; // the conversion pill sits fully inside the gap
      var stageH = Math.max(22, Math.round((bodyH - stageGap*(n-1))/n));
      // vertical centers of each stage
      var stageCy = stages.map(function(_,i){ return bodyTop + stageH/2 + i*(stageH+stageGap); });

      // widths proportional to max value
      var vmax = (stages[0]&&stages[0].value>0)?stages[0].value:1;   // all-zero funnel: no NaN geometry
      var minFrac = 0.28; // minimum readable width (relative to bodyW)
      var maxBarW = bodyW*0.68;
      var labelW = Math.round(bodyW*0.18);
      var valW = Math.round(bodyW*0.12);

      var logScale = e.scale === 'log';
      // log stages stay wide near the top, so keep the bar clear of the label and value columns
      if(logScale) maxBarW = bodyW - 2*Math.max(labelW, valW) - 4*u;
      var vminPos = stages.reduce(function(m,s){ return s.value>0 ? Math.min(m,s.value) : m; }, vmax);
      function barW(v){
        if(logScale && vmax > vminPos){
          // log width for data spanning orders of magnitude (people, tokens): the smallest stage sits at the floor
          var f = v>0 ? (Math.log(v)-Math.log(vminPos))/(Math.log(vmax)-Math.log(vminPos)) : 0;
          return Math.round(maxBarW*(0.14 + 0.86*Math.max(0,f)));
        }
        // honest linear width; a floor only for stages below 14% of the top
        return Math.round(Math.max(maxBarW*0.14, maxBarW*v/vmax));
      }
      // palette: default one accent per stage; "mono" = one quiet accent, the focus stage (default last) in a hot accent
      var mono = e.palette === 'mono';
      var focusI = (typeof e.focus === 'number') ? e.focus : n-1;
      // the focus accent must stand apart from acc1 in both themes; dark acc2 is a blue next to cyan acc1
      var hot = dark ? 6 : 2;
      function stAcc(i){ return mono ? (i===focusI ? 'acc'+hot : 'acc1') : ctx.acc(i); }
      function stAccf(i){ return mono ? (i===focusI ? 'accf'+hot : 'accf1') : ctx.accf(i); }

      // centre X of funnel
      var cx = w/2;

      // ---- SVG layer for shapes / particles ----
      var svgEl = svg(ctx, 'svg', {width:w, height:h});
      svgEl.style.cssText = 'position:absolute;left:0;top:0;overflow:visible;pointer-events:none;';
      root.appendChild(svgEl);

      // ---- build each stage ----
      var state = {n:n, period:e.period||18};

      // Glow filter for dark mode (thin, crisp)
      var defs = svg(ctx,'defs',{});
      var glowId = 'fl-glow';
      var fltr = svg(ctx,'filter',{id:glowId,x:'-50%',y:'-50%',width:'200%',height:'200%'});
      var fga = svg(ctx,'feGaussianBlur',{stdDeviation:dark?'2.4':'1.4',result:'b'});
      var fmr = svg(ctx,'feMerge',{});
      var mn1 = svg(ctx,'feMergeNode',{'in':'b'});
      var mn2 = svg(ctx,'feMergeNode',{'in':'SourceGraphic'});
      fmr.appendChild(mn1); fmr.appendChild(mn2);
      fltr.appendChild(fga); fltr.appendChild(fmr);
      defs.appendChild(fltr);
      svgEl.appendChild(defs);

      // Trapezoid group (per stage): two widths = barW(v_above) top, barW(v) bottom
      // Except first: top = barW(v0), bottom = barW(v1) at transition;
      // we draw each stage as a trapezoid with top width and bottom width based on own value and next value.
      // Simpler: each stage i drawn as a trapezoid with
      //   topW = barW(stages[i].value), bottomW = barW(i<n-1? stages[i+1].value : stages[i].value*0.98)
      // Then small separator gap.
      stages.forEach(function(s,i){
        var yTop = stageCy[i] - stageH/2;
        var yBot = stageCy[i] + stageH/2;
        var tw = barW(s.value);
        var bw = (i<n-1)? barW(stages[i+1].value) : Math.round(tw*0.92);
        var pts = [
          [cx - tw/2, yTop],
          [cx + tw/2, yTop],
          [cx + bw/2, yBot],
          [cx - bw/2, yBot]
        ];
        var acc = stAcc(i);
        var accf = stAccf(i);
        var poly = svg(ctx,'polygon',{
          points: pts.map(function(p){return p[0]+','+p[1]}).join(' '),
          fill: ctx.cc(accf),
          stroke: ctx.cc(acc),
          'stroke-width': dark?'1.2':'1.5',
          'stroke-linejoin':'round'
        });
        ctx.mark(poly, 'box');
        svgEl.appendChild(poly);
      });

      // Connectors (subtle vertical lines between stages, routed around trapezoid sides)
      // Using a subtle dotted guide for each inter-stage gap on left/right edges
      for(var i=0;i<n-1;i++){
        var ln = svg(ctx,'line',{
          x1:cx, y1:stageCy[i] + stageH/2, x2:cx, y2:stageCy[i+1] - stageH/2,
          stroke: ctx.cc('grid'), 'stroke-width':'1', 'stroke-dasharray':'2 3'
        });
        ctx.mark(ln,'edge');
        svgEl.appendChild(ln);
      }

      // Labels (HTML for reliable CJK rendering)
      var ls = Number(e.labelScale)||1;
      var labelSize = Math.max(12, Math.min(u*1.55*ls, 17*ls));
      var labelLh = Math.round(labelSize*1.55);
      var subSize = Math.max(11, Math.round(labelSize*0.82));
      var subLh = Math.round(subSize*1.55);

      var vs = Number(e.valueScale)||1;
      var valSize = Math.max(14, Math.min(u*2.0*vs, 22*vs));
      var valLh = Math.round(valSize*1.3);

      stages.forEach(function(s,i){
        var yTop = stageCy[i] - stageH/2;
        // label (left-aligned, to the left of bar area)
        var labelX = marginX;
        var labelBox = el('div', null,
          'position:absolute;left:'+labelX+'px;top:'+Math.round(yTop + (stageH - labelLh - subLh)/2)+'px;width:'+labelW+'px;white-space:pre;');
        var l1 = el('div', null, 'height:'+labelLh+'px;line-height:'+labelLh+'px;font-size:'+labelSize+'px;color:'+ctx.cc('fg')+';font-weight:600;overflow:hidden;text-overflow:ellipsis;');
        var fit1 = ctx.fit(s.label, labelSize, labelW-4, null, 11, true);
        l1.style.fontSize = fit1.size+'px';
        l1.textContent = fit1.text;
        ctx.mark(l1,'text');
        labelBox.appendChild(l1);
        var l2 = el('div', null, 'height:'+subLh+'px;line-height:'+subLh+'px;font-size:'+subSize+'px;color:'+ctx.cc('muted')+';letter-spacing:0.3px;overflow:hidden;text-overflow:ellipsis;');
        var fit2 = ctx.fit(s.sub, subSize, labelW-4, null, 11, false);
        l2.style.fontSize = fit2.size+'px';
        l2.textContent = fit2.text;
        ctx.mark(l2,'text');
        labelBox.appendChild(l2);
        root.appendChild(labelBox);

        // value (right-aligned, to the right of bar area)
        var valX = w - marginX - valW;
        var valBox = el('div', null,
          'position:absolute;left:'+valX+'px;top:'+Math.round(stageCy[i]-valLh/2)+'px;width:'+valW+'px;height:'+valLh+'px;line-height:'+valLh+'px;text-align:right;font-family:var(--font);font-size:'+valSize+'px;font-variant-numeric:tabular-nums;color:'+ctx.cc('fg')+';font-weight:700;white-space:pre;');
        valBox.textContent = fmtNum(s.value);
        ctx.mark(valBox,'text');
        root.appendChild(valBox);
      });

      // Conversion % between stages (small pill)
      var convPillW = Math.round(u*7.5);
      var convPillH = convPillH0;
      var convSize = Math.max(11, Math.min(u*1.3, 14));
      var convLh = convPillH;
      for(var i=0;i<n-1;i++){
        var prevV = stages[i].value;
        var r = prevV>0 ? stages[i+1].value/prevV*100 : null;   // 0 -> 0 has no rate
        // whole percent from 1% up; below that keep two significant digits so a tiny rate never prints as 0%
        var pct = r==null ? null : (r >= 1 || r === 0 ? Math.round(r) : Number(r.toPrecision(2)));
        var y = stageCy[i] + (stageH+stageGap)/2;
        // pill
        var pillX = cx - convPillW/2;
        var pillY = y - convPillH/2;
        var rx = dark?0:Math.round(convPillH/2);
        var pill = svg(ctx,'rect',{
          x:pillX, y:pillY, width:convPillW, height:convPillH, rx:rx, ry:rx,
          fill: dark? ctx.cc('panel') : ctx.cc('bg'),
          stroke: ctx.cc('line2'), 'stroke-width':'1'
        });
        svgEl.appendChild(pill);
        // HTML text for the conversion % (centered over pill)
        var cBox = el('div', null,
          'position:absolute;left:'+(pillX)+'px;top:'+pillY+'px;width:'+convPillW+'px;height:'+convLh+'px;line-height:'+convLh+'px;text-align:center;font-size:'+convSize+'px;color:'+ctx.cc('fg')+';font-weight:600;white-space:pre;font-variant-numeric:tabular-nums;');
        cBox.textContent = (pct==null ? '—' : fmtPct(pct)+'%');
        ctx.mark(cBox,'text');
        root.appendChild(cBox);
      }

      // ---- particles: fast tempo, flowing down the funnel centre ----
      // One packet per inter-stage segment, density proportional to stage value.
      var PKG = [];
      for(var i=0;i<n;i++){
        var yA = stageCy[i] - stageH/2 + 4, yB = stageCy[i] + stageH/2 - 4;
        var twI = barW(stages[i].value), bwI = (i<n-1)? barW(stages[i+1].value) : Math.round(twI*0.92);
        var nPkg = Math.max(1, Math.round(8*stages[i].value/vmax));   // density follows the value
        for(var k=0;k<nPkg;k++){
          var colI = stAcc(i);
          var dot = svg(ctx,'circle',{cx:cx, cy:yA, r: dark? 3 : 3.4, fill: ctx.cc(colI), opacity:0.9});
          svgEl.appendChild(dot);
          var tail = svg(ctx,'circle',{cx:cx, cy:yA, r: dark? 1.7 : 2, fill: ctx.cc(colI), opacity:0.4});
          svgEl.appendChild(tail);
          PKG.push({el:dot, tail:tail, yA:yA, yB:yB, tw:twI, bw:bwI,
                    fx: (ctx.hash(7+i, k) * 1.6 - 0.8),
                    // packet periods divide the view period so the clip loops seamlessly
                    period: state.period/Math.max(1, Math.round(state.period/(2.4 + 0.6*ctx.hash(31+i, k)))), off: 3*ctx.hash(53+i, k)});
        }
      }

      // ---- stage highlight sweep (medium/slow tempo) ----
      // A vertical bar that sweeps down each stage, highlighting one stage at a time.
      // Keep it subtle: a slightly brighter stroke / glow. We'll add a highlight rect per stage
      // that we animate opacity on in seek().
      var hiRects = stages.map(function(s,i){
        var yTop = stageCy[i] - stageH/2;
        var tw = barW(s.value);
        var bw = (i<n-1)? barW(stages[i+1].value) : Math.round(tw*0.92);
        var pad = dark? 4 : 5;
        var pts = [
          [cx - tw/2 - pad, yTop - pad],
          [cx + tw/2 + pad, yTop - pad],
          [cx + bw/2 + pad, stageCy[i] + stageH/2 + pad],
          [cx - bw/2 - pad, stageCy[i] + stageH/2 + pad]
        ];
        var poly = svg(ctx,'polygon',{
          points: pts.map(function(p){return p[0]+','+p[1]}).join(' '),
          fill: dark? ctx.cc(stAcc(i)) : 'none',
          stroke: ctx.cc(stAcc(i)),
          'stroke-width': dark?'1.5':'2.5',
          'stroke-linejoin':'round',
          opacity:'0',
          'pointer-events':'none'
        });
        if(dark){ poly.setAttribute('filter','url(#'+glowId+')'); }
        svgEl.appendChild(poly);
        return poly;
      });

      // Save refs for seek
      state.pk = PKG;
      state.hiRects = hiRects;
      state.cx = cx;
      state.dark = dark;
      return state;
    },

    seek: function(t, ctx, st){
      var s = st || (ctx && ctx.state);
      if(!s) return;
      var period = s.period;
      var n = s.n;

      // ---- packets (fast) ----
      s.pk.forEach(function(p){
        var q = (t + p.off)/p.period, frac = q - Math.floor(q);
        var y = p.yA + (p.yB-p.yA)*frac;
        var half = (p.tw + (p.bw-p.tw)*frac)/2 - 10;
        var x = s.cx + p.fx*half;
        p.el.setAttribute('cy', y); p.el.setAttribute('cx', x);
        var yt = Math.max(p.yA, y - (s.dark?8:10)), ft = (yt-p.yA)/Math.max(1,(p.yB-p.yA));
        p.tail.setAttribute('cy', yt); p.tail.setAttribute('cx', s.cx + p.fx*((p.tw + (p.bw-p.tw)*ft)/2 - 10));
      });

      // ---- stage highlight (slow): each stage highlighted for period/n seconds,
      // with ~0.5 s fade, single focus at a time; first stage already lit at t=0.
      var perStage = period/n;
      var focusI = Math.floor(((t/period) - 0) * n) % n;
      if(focusI<0) focusI += n;
      var phaseInStage = (t/perStage) - Math.floor(t/perStage);
      s.hiRects.forEach(function(r,i){
        var op = 0;
        if(i===focusI){
          op = phaseInStage>0.9 ? (1-phaseInStage)/0.1 : 1;   // lit from frame 0, fades out before the next
          op *= s.dark? 0.22 : 0.55;
        }
        r.setAttribute('opacity', op.toFixed(3));
      });
    },

    check: function(ctx){
      var pr = [];
      var e = ctx.e;
      var st = e.stages||[];
      for(var i=1;i<st.length;i++){
        if(typeof st[i].value==='number' && typeof st[i-1].value==='number' && st[i].value>st[i-1].value){
          pr.push('stages['+i+'].value ('+st[i].value+') > stages['+(i-1)+'].value ('+st[i-1].value+'): funnel values must be non-increasing');
        }
      }
      return pr;
    }
  });
})();
