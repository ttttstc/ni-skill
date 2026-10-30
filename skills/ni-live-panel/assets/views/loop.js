// live-panel view: loop — nested loops with decision diamonds, back-edges and a walking token
// Self-registers via LP.registerView. Contract and config keys: references/views.md.
// Icons: Lucide (ISC), see assets/views/LUCIDE-LICENSE.txt and NOTICE.
(function(){
  var NS = 'http://www.w3.org/2000/svg';

  // Lucide icon bodies (24x24 viewBox, stroke currentColor); unknown names fall back to 'circle'
  var ICONS = {
    'message-square-more': '<path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z" /><path d="M12 11h.01" /><path d="M16 11h.01" /><path d="M8 11h.01" />',
    'message-square': '<path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z" />',
    'eye': '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" /><circle cx="12" cy="12" r="3" />',
    'ticket': '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z" /><path d="M13 5v2" /><path d="M13 17v2" /><path d="M13 11v2" />',
    'bug': '<path d="M12 20v-9" /><path d="M14 7a4 4 0 0 1 4 4v3a6 6 0 0 1-12 0v-3a4 4 0 0 1 4-4z" /><path d="M14.12 3.88 16 2" /><path d="M21 21a4 4 0 0 0-3.81-4" /><path d="M21 5a4 4 0 0 1-3.55 3.97" /><path d="M22 13h-4" /><path d="M3 21a4 4 0 0 1 3.81-4" /><path d="M3 5a4 4 0 0 0 3.55 3.97" /><path d="M6 13H2" /><path d="m8 2 1.88 1.88" /><path d="M9 7.13V6a3 3 0 1 1 6 0v1.13" />',
    'git-pull-request': '<circle cx="18" cy="18" r="3" /><circle cx="6" cy="6" r="3" /><path d="M13 6h3a2 2 0 0 1 2 2v7" /><line x1="6" x2="6" y1="9" y2="21" />',
    'shield-check': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" /><path d="m9 12 2 2 4-4" />',
    'bot': '<path d="M12 8V4H8" /><rect width="16" height="12" x="4" y="8" rx="2" /><path d="M2 14h2" /><path d="M20 14h2" /><path d="M15 13v2" /><path d="M9 13v2" />',
    'git-merge': '<circle cx="18" cy="18" r="3" /><circle cx="6" cy="6" r="3" /><path d="M6 21V9a9 9 0 0 0 9 9" />',
    'timer': '<line x1="10" x2="14" y1="2" y2="2" /><line x1="12" x2="15" y1="14" y2="11" /><circle cx="12" cy="14" r="8" />',
    'bell': '<path d="M10.268 21a2 2 0 0 0 3.464 0" /><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" />',
    'refresh-cw': '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" /><path d="M8 16H3v5" />',
    'info': '<circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path d="M12 8h.01" />',
    'hand': '<path d="M18 11V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2" /><path d="M14 10V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v2" /><path d="M10 10.5V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v8" /><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />',
    'circle': '<circle cx="12" cy="12" r="10" />'
  };

  // hue name -> accent index per theme (dark and light order their accents differently)
  var HUE_DARK  = {green:3, blue:2, purple:4, amber:5, cyan:1, pink:6};
  var HUE_LIGHT = {green:2, blue:1, purple:4, amber:3, cyan:5, pink:6};

  function svg(tag, attrs){
    var n = document.createElementNS(NS, tag);
    if(attrs) Object.keys(attrs).forEach(function(k){ n.setAttribute(k, attrs[k]); });
    return n;
  }
  function el(cls, style){
    var n = document.createElement('div');
    if(cls) n.className = cls;
    if(style) n.style.cssText = style;
    return n;
  }
  function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }
  function hex2rgb(h){ return [parseInt(h.substr(1,2),16), parseInt(h.substr(3,2),16), parseInt(h.substr(5,2),16)]; }
  function mixHex(a, b, k){            // opaque blend: k of b over a
    var x = hex2rgb(a), y = hex2rgb(b);
    return 'rgb(' + [0,1,2].map(function(i){ return Math.round(x[i]*(1-k) + y[i]*k); }).join(',') + ')';
  }
  function rgba(h, a){ var c = hex2rgb(h); return 'rgba('+c[0]+','+c[1]+','+c[2]+','+a+')'; }
  function modf(a, n){ return ((a % n) + n) % n; }
  // point at fraction f (0..1) along an edge's sampled path
  function along(E, f){
    var q = f*(E.sx.length - 1), k = Math.min(E.sx.length - 2, Math.floor(q)), r = q - k;
    return {x:E.sx[k] + (E.sx[k+1]-E.sx[k])*r, y:E.sy[k] + (E.sy[k+1]-E.sy[k])*r};
  }

  // polyline -> path with rounded corners
  function roundedPath(pts, r){
    var d = 'M' + pts[0].x.toFixed(1) + ',' + pts[0].y.toFixed(1);
    for(var i = 1; i < pts.length - 1; i++){
      var a = pts[i-1], b = pts[i], c = pts[i+1];
      var l1 = Math.hypot(b.x-a.x, b.y-a.y), l2 = Math.hypot(c.x-b.x, c.y-b.y);
      var rr = Math.min(r, l1/2, l2/2);
      var p1 = {x:b.x + (a.x-b.x)/l1*rr, y:b.y + (a.y-b.y)/l1*rr};
      var p2 = {x:b.x + (c.x-b.x)/l2*rr, y:b.y + (c.y-b.y)/l2*rr};
      d += 'L' + p1.x.toFixed(1) + ',' + p1.y.toFixed(1) + 'Q' + b.x.toFixed(1) + ',' + b.y.toFixed(1) + ' ' + p2.x.toFixed(1) + ',' + p2.y.toFixed(1);
    }
    var z = pts[pts.length-1];
    return d + 'L' + z.x.toFixed(1) + ',' + z.y.toFixed(1);
  }
  function dedupe(pts){
    var o = [];
    pts.forEach(function(p){
      var q = o[o.length-1];
      if(q && Math.abs(q.x-p.x) < 0.5 && Math.abs(q.y-p.y) < 0.5) return;
      o.push(p);
    });
    // drop collinear middle points
    var r = [o[0]];
    for(var i = 1; i < o.length - 1; i++){
      var a = r[r.length-1], b = o[i], c = o[i+1];
      var cross = (b.x-a.x)*(c.y-b.y) - (b.y-a.y)*(c.x-b.x);
      if(Math.abs(cross) > 0.5) r.push(b);
    }
    r.push(o[o.length-1]);
    return r;
  }

  var SIDE = {
    top:{x:0,y:-1}, bottom:{x:0,y:1}, left:{x:-1,y:0}, right:{x:1,y:0}
  };

  // card text font: the light-pastel preset's stack (CJK sans first); `font:"theme"` keeps the theme font
  var SANS = '"Noto Sans CJK SC","PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif';

  // density levels tried in order until the grid fits the rect (1:1 is the tightest canvas)
  var LEVELS = [
    {isz:4.4, tS:1.55, dS:1.22, padV:1.0,  maxDesc:3},
    {isz:4.0, tS:1.5,  dS:1.18, padV:0.85, maxDesc:3},
    {isz:3.5, tS:1.4,  dS:1.1,  padV:0.7,  maxDesc:3},
    {isz:3.2, tS:1.35, dS:1.05, padV:0.55, maxDesc:2}
  ];
  var ICON_ALIAS = {'message-square':'message-square-more'};   // the chat bubble always carries its three dots

  // easing helpers: every micro-motion runs inside a short action window of the ambient period
  function easeInOutCubic(x){ x = x < 0 ? 0 : (x > 1 ? 1 : x); return x < 0.5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3)/2; }
  function easeOutBack(x, o){ x = x < 0 ? 0 : (x > 1 ? 1 : x); var c1 = o === undefined ? 1.6 : o, c3 = c1 + 1, y = x - 1; return 1 + c3*y*y*y + c1*y*y; }
  function easeOutElastic(x){ x = x < 0 ? 0 : (x > 1 ? 1 : x); if(x === 0 || x === 1) return x; return Math.pow(2, -9*x)*Math.sin((x*8 - 0.75)*(2*Math.PI/3)) + 1; }
  function bump(x){ x = x < 0 ? 0 : (x > 1 ? 1 : x); var s = Math.sin(Math.PI*x); return s*s; }
  // rise with a slight overshoot, then settle back (0 → 1 → 0)
  function leap(x){ x = x < 0 ? 0 : (x > 1 ? 1 : x); return x < 0.5 ? easeOutBack(x*2, 1.6) : 1 - easeInOutCubic((x - 0.5)*2); }
  // action window per icon kind, as a fraction of the ambient period
  var ICON_WIN = {'message-square-more':0.4, 'timer':0.5, 'refresh-cw':0.7, 'shield-check':0.45, 'eye':0.4, 'ticket':0.35, 'bug':0.4};
  var FOCUS_AT = 0.7;                // fraction of a hop at which the focus passes from source to target

  LP.registerView('loop', {
    build: function(ctx){
      var e = ctx.e, rect = ctx.rect, root = ctx.root;
      var w = rect.w, h = rect.h, dark = ctx.dark;
      var problems = [];
      var u = Math.min(w, h)/100;
      var period = Number(e.period) || 26;
      var motion = e.motion || 'ambient';
      var amb = motion.indexOf('ambient') >= 0, walkOn = motion.indexOf('walk') >= 0;
      var weak = amb && walkOn;                       // walk laid over ambient: quieter focus
      var AP = Number(e.ambientPeriod) || 3.0;
      if(!amb && !walkOn){ problems.push('motion "'+motion+'" is not ambient | walk | ambient+walk'); }
      var HUE = dark ? HUE_DARK : HUE_LIGHT;
      var ff = e.font === 'theme' ? null : SANS;
      var ffCss = ff ? 'font-family:' + ff + ';' : '';

      var nodes = (e.nodes||[]).map(function(n){
        return {id:n.id, group:n.group||null, row:n.row||0, col:n.col||0, span:n.span||1,
                type:n.type||'card', icon:n.icon, label:n.label||'', en:n.en||'', desc:n.desc||[],
                items:n.items||[], hue:n.hue, raw:n};
      });
      var byId = {};
      nodes.forEach(function(n){ byId[n.id] = n; });
      var groups = (e.groups||[]).map(function(g){ return {id:g.id, label:g.label||'', sub:g.sub||'', hue:g.hue||'green'}; });
      var gById = {};
      groups.forEach(function(g){ gById[g.id] = g; });
      function accOf(n){
        var hue = n.hue || (n.group && gById[n.group] ? gById[n.group].hue : 'green');
        return HUE[hue] || 3;
      }
      var statusCfg = e.status || null;

      // ---- header ----
      var topPad = Math.round(u*1.6);
      var headH = topPad;
      function headline(txt, size, extra){
        var lh = Math.round(size*(extra.lh || 1.25));
        var n = el(null, 'position:absolute;left:0;right:0;top:'+headH+'px;height:'+lh+'px;line-height:'+lh+'px;text-align:center;font-size:'+size+'px;white-space:pre;'+extra.css);
        n.textContent = txt; ctx.mark(n, 'text'); root.appendChild(n);
        headH += lh;
      }
      if(e.title) headline(e.title, clamp(u*3.2, 22, 46), {css:'font-family:var(--font-title);font-weight:700;color:'+ctx.cc('fg')+';'});
      if(e.subtitle) headline(e.subtitle, clamp(u*1.6, 13, 19), {lh:1.4, css:ffCss+'color:'+ctx.cc('muted')+';letter-spacing:0.5px;'});
      headH += Math.round(u*1.8);
      var botPad = Math.round(u*1.2);

      // ---- grid columns ----
      var nCols = e.cols || Math.max.apply(null, nodes.map(function(n){ return n.col + n.span; }).concat([1]));
      var maxRow = Math.max.apply(null, nodes.map(function(n){ return n.row; }).concat([0]));
      var edgesCfg = e.edges || [];
      var laneL = edgesCfg.some(function(x){ return x.lane === 'left'; });
      var laneR = edgesCfg.some(function(x){ return x.lane === 'right'; });
      var marginX = Math.round(u*2.2);
      var gutter = Math.round(u*5.2);
      var x0 = marginX + (laneL ? gutter : 0);
      var x1 = w - marginX - (laneR ? gutter : 0);
      var gp = Math.round(u*1.5);                 // horizontal group padding
      var colGap = Math.round(u*3.4);
      var cellW = (x1 - x0 - 2*gp - (nCols-1)*colGap)/nCols;
      nodes.forEach(function(n){
        n.cellX = x0 + gp + n.col*(cellW + colGap);
        n.w = n.span*cellW + (n.span-1)*colGap;
      });

      // ---- card content: plan the text of every card at one density level ----
      var hiddenEn = 0, totalEn = 0;
      function planCard(n, L, s){
        var isNote = n.type === 'note';
        var tS = clamp(u*L.tS, 13, 20)*s, dS = clamp(u*L.dS, 11, 15.5)*s*(isNote ? 1.1 : 1);
        var pad = Math.round(u*(isNote ? 0.3 : 0.95)*s);
        var isize = n.icon != null ? Math.round(u*L.isz*(isNote ? 0.5 : 1)*s) : 0;
        var dashW = isNote && n.desc.length > 1 ? Math.round(u*2.4) : 0;   // loop-back dash legend before each note line
        var tx0 = pad + (isize ? isize + Math.round(pad*(isNote ? 1.6 : 0.9)) : 0) + dashW;
        var P = {n:n, isNote:isNote, isStatus:!!(statusCfg && statusCfg.node === n.id), tS:tS, dS:dS,
                 tLh:Math.round(tS*1.6), dLh:Math.round(dS*(isNote ? 2.05 : 1.55)), dashW:dashW, pad:pad, isize:isize, tx0:tx0, tw:n.w - tx0 - pad - 2,
                 title:null, en:null, enMode:'none', desc:[], hidden:0, total:0, padV:Math.round(u*(isNote ? 0.35 : L.padV)*s)};
        var tw = P.tw;
        function fits(txt, px, room){ return ctx.measure(txt, px, ff, false) <= room; }
        if(n.label){
          P.title = ctx.fit(n.label, tS, tw, ff, 12, true);
          if(n.en){
            // the English gloss: inline if it fits, else shrink, else its own line under the title
            var gap = Math.round(u*0.7);
            var left = tw - ctx.measure(P.title.text, P.title.size, ff, true) - gap;
            var es = Math.max(11, Math.round(P.title.size*0.74));
            while(es > 11 && !fits(n.en, es, left)) es -= 1;
            var bs = Math.max(11, Math.round(dS*0.95));
            if(fits(n.en, es, left)){ P.en = {size:es, gap:gap}; P.enMode = 'inline'; }
            else if(fits(n.en, bs, tw)){ P.en = {size:bs}; P.enMode = 'below'; }
            else P.enMode = 'hidden';
          }
        }
        // description lines wrap at the text width (cut at a space when there is one); the status card has none
        function wrapLine(str){
          var out = [], rest = String(str);
          while(rest && !fits(rest, dS, tw) && out.length < 3){
            var lo = 1, hi2 = rest.length;
            while(lo < hi2){ var mid2 = (lo + hi2 + 1) >> 1; if(fits(rest.slice(0, mid2), dS, tw)) lo = mid2; else hi2 = mid2 - 1; }
            var sp = rest.lastIndexOf(' ', lo), cut = sp > 0 ? sp : lo;
            out.push(rest.slice(0, cut).replace(/\s+$/, ''));
            rest = rest.slice(cut).replace(/^\s+/, '');
          }
          if(rest) out.push(rest);
          return out;
        }
        var all = [];
        if(!P.isStatus) n.desc.forEach(function(d){ all = all.concat(wrapLine(d)); });
        P.desc = all.slice(0, L.maxDesc); P.total = all.length; P.hidden = all.length - P.desc.length;
        P.textH = (n.label ? P.tLh : 0) + (P.enMode === 'below' ? P.dLh : 0) + P.desc.length*P.dLh;
        P.h = Math.max(isize, P.textH) + 2*P.padV;
        return P;
      }

      // status block (round counter / step / dots), sized for the worst case
      var walkSpec = (e.walks || (e.walk ? [e.walk] : [])).map(function(a){ return (a||[]).slice(); });
      var maxVisit = walkSpec.reduce(function(m, a){ return Math.max(m, a.length); }, 1);
      var rounds = Math.max(1, walkSpec.length);
      var ambientOnly = amb && !walkOn;
      var ambSub = (statusCfg && statusCfg.ambientSub) || '';
      var dotCount = ambientOnly ? (maxVisit > 1 ? maxVisit : 8) : maxVisit;
      function statusPlan(P, L){
        var n = P.n, tw = P.tw;
        var rTpl = statusCfg.round || 'Round {n}', sTpl = statusCfg.step || '{label}';
        var rS = clamp(u*2.5, 16, 32), rSize = rS;
        var rStr = []; for(var q = 1; q <= rounds; q++) rStr.push(rTpl.replace('{n}', q));
        if(ambientOnly){ rStr = [statusCfg.ambientTitle || 'Loop']; sTpl = ambSub; }
        rStr.forEach(function(s){ rSize = Math.min(rSize, ctx.fit(s, rS, tw, 'var(--font-title)', 12, true).size); });
        var sSize = Math.max(11, Math.round(P.dS));
        if(ambientOnly) sSize = Math.min(sSize, ctx.fit(ambSub, sSize, tw, ff, 11, false).size);
        else walkSpec.forEach(function(a){ a.forEach(function(id){
          if(byId[id]) sSize = Math.min(sSize, ctx.fit(sTpl.replace('{label}', byId[id].label), sSize, tw, ff, 11, false).size);
        }); });
        var dotGap = Math.min(u*1.9, tw/Math.max(1, dotCount));
        var dotR = Math.max(2.6, Math.min(u*0.42, dotGap*0.32));
        P.st = {rTpl:rTpl, sTpl:sTpl, rStr:rStr, rSize:rSize, sSize:sSize, rLh:Math.round(rSize*1.6), sLh:Math.round(sSize*1.6),
                dotGap:dotGap, dotR:dotR, dotsH:Math.round(dotR*2 + 4)};
        P.textH = (n.label ? P.tLh : 0) + P.st.rLh + P.st.sLh + P.st.dotsH + Math.round(u*0.6);
        P.h = Math.max(P.isize, P.textH) + 2*P.padV;
      }

      // ---- rows -> blocks of equal group ----
      var blocks = [];
      for(var r = 0; r <= maxRow; r++){
        var first = nodes.filter(function(n){ return n.row === r; })[0];
        var rg = first ? first.group : null, last = blocks[blocks.length-1];
        if(last && last.group && last.group === rg) last.rows.push(r);
        else blocks.push({group:rg, rows:[r]});
      }
      var gTitleSize = clamp(u*1.75, 14, 21);
      var gTitleLh = Math.round(gTitleSize*1.6);
      var gTopH = gTitleLh + Math.round(u*0.5);     // title strip inside the group frame

      // lay the grid out at one density level; returns the natural height and everything needed to place it
      function gridAt(L, s){
        var plans = {}, hs = [];
        nodes.forEach(function(n){
          if(n.type === 'diamond' || n.type === 'legend') return;
          var P = planCard(n, L, s);
          if(P.isStatus) statusPlan(P, L);
          plans[n.id] = P;
          if(!P.isNote) hs.push(P.h);
        });
        hs.sort(function(a, b){ return a - b; });
        var cardRef = hs.length ? hs[Math.floor(hs.length/2)] : Math.round(u*8);   // the typical card, not the tallest
        var dH = Math.round(cardRef*1.15);
        var rowCard = [], rowNat = [];
        for(var rr = 0; rr <= maxRow; rr++){
          var ch = 0, nat = 0;
          nodes.forEach(function(n){
            if(n.row !== rr) return;
            if(n.type === 'diamond') nat = Math.max(nat, dH);
            else if(n.type === 'legend') nat = Math.max(nat, Math.round(u*3.4));
            else { nat = Math.max(nat, plans[n.id].h); if(!plans[n.id].isNote) ch = Math.max(ch, plans[n.id].h); }
          });
          rowCard[rr] = ch; rowNat[rr] = nat;
        }
        // one title / en / desc size for every card: the smallest any card needed
        var mT = 1e9, mE = 1e9, mD = 1e9;
        nodes.forEach(function(n){
          var P = plans[n.id]; if(!P) return;
          if(P.title) mT = Math.min(mT, P.title.size);
          if(P.en) mE = Math.min(mE, P.en.size);
          P.desc.forEach(function(d){ mD = Math.min(mD, ctx.fit(d, P.dS, P.tw, ff, 11, false).size); });
        });
        nodes.forEach(function(n){
          var P = plans[n.id]; if(!P) return;
          if(P.title && mT < 1e9) P.title.size = Math.min(P.title.size, mT);
          if(P.en && mE < 1e9) P.en.size = Math.min(P.en.size, mE);
          P.descSize = mD < 1e9 && !P.isNote ? Math.min(P.dS, mD) : P.dS;
        });
        return {L:L, plans:plans, cardRef:cardRef, dH:dH, rowCard:rowCard, rowNat:rowNat};
      }
      var base = {blockGap:u*2.0, rowGap:u*1.2, gpT:u*0.7, gpB:u*1.0};
      var rowTop = [], rowH = [];
      function totalH(G, sp, grow){      // stacks blocks and rows; also records the positions of the last call
        var y = headH;
        blocks.forEach(function(b, i){
          if(i > 0) y += sp.blockGap;
          b.top = y;
          if(b.group) y += gTopH + sp.gpT;
          b.rows.forEach(function(rr, k){
            if(k > 0) y += sp.rowGap;
            rowH[rr] = G.rowNat[rr] + grow; rowTop[rr] = y; y += rowH[rr];
          });
          if(b.group) y += sp.gpB;
          b.bottom = y;
        });
        return y + botPad;
      }
      var G = null;
      for(var li = 0; li < LEVELS.length; li++){
        G = gridAt(LEVELS[li], 1);
        if(totalH(G, base, 0) <= h) break;
      }
      // vertical headroom of a tall canvas goes into the cards first: s in [1, 1.3] scales text, icons, padding, diamonds
      var scale = 1;
      if(totalH(G, base, 0) < h){
        // width guard: largest s whose cards wrap / shrink / move no more than at s=1
        var G1 = G;
        function sameAsBase(G2){
          return nodes.every(function(n){
            var A = G1.plans[n.id], B = G2.plans[n.id];
            if(!A || !B) return true;
            if(B.total > A.total || B.hidden > A.hidden || B.enMode !== A.enMode) return false;
            if(A.title && B.title && B.title.text !== A.title.text) return false;
            return true;
          });
        }
        var lo3 = 1, hi3 = 1.3;
        if(sameAsBase(gridAt(G.L, hi3))) lo3 = hi3;
        else for(var it = 0; it < 7; it++){
          var mid3 = (lo3 + hi3)/2;
          if(sameAsBase(gridAt(G.L, mid3))) lo3 = mid3; else hi3 = mid3;
        }
        for(var sc = lo3; sc > 1.001; sc -= 0.02){
          var G2 = gridAt(G.L, sc);
          if(totalH(G2, base, 0) <= h){ G = G2; scale = sc; break; }
        }
      }
      var natural = totalH(G, base, 0);
      var spare = h - natural;
      var sp = {blockGap:base.blockGap, rowGap:base.rowGap, gpT:base.gpT, gpB:base.gpB}, grow = 0;
      if(spare >= 0){
        // a little goes into the cards, the rest into group spacing and the loop-back corridors
        var nRows = maxRow + 1;
        var gwB = blocks.length - 1, gwR = 0, gwG = 0;
        blocks.forEach(function(b){ gwR += b.rows.length - 1; if(b.group) gwG += 1; });
        grow = Math.min(spare*0.6/nRows, G.cardRef*0.35);
        var rest2 = spare - grow*nRows;
        // between groups at most 4u, between rows at most ~3u; the remainder pads the group frames (title zone)
        var bAdd = gwB ? Math.min(Math.max(0, u*4 - base.blockGap), rest2*0.4/gwB) : 0;
        var rAdd = gwR ? Math.min(u*1.8, rest2*0.3/gwR) : 0;
        var left2 = rest2 - bAdd*gwB - rAdd*gwR;
        if(gwG){ var pA = left2/gwG/2; sp.gpT += pA; sp.gpB += pA; }
        else if(gwB){ bAdd += left2/gwB; }
        sp.blockGap += bAdd; sp.rowGap += rAdd;
      } else {
        var sum = base.blockGap*(blocks.length-1) + base.rowGap + base.gpT + base.gpB;
        var f = Math.max(0.5, 1 + spare/Math.max(1, sum));
        sp = {blockGap:base.blockGap*f, rowGap:base.rowGap*f, gpT:base.gpT*f, gpB:base.gpB*f};
        if(totalH(G, sp, 0) > h + 1) problems.push('content is taller than the rect at the tightest density (' + Math.round(totalH(G, sp, 0) - h) + 'px)');
      }
      totalH(G, sp, grow);

      var gapCenters = [];
      for(var bi = 0; bi < blocks.length - 1; bi++) gapCenters.push((blocks[bi].bottom + blocks[bi+1].top)/2);

      nodes.forEach(function(n){
        var rh = rowH[n.row];
        if(n.type === 'diamond'){
          // narrower than the cell, 1.15x the card height; widened only as far as the text needs
          var need = Math.max(ctx.measure(n.label, 13, ff, true), n.en ? ctx.measure(n.en, 11, ff, false) : 0);
          var dW = clamp(Math.max(0.75*cellW, need*2/0.98 + 6), 0, cellW*0.94);
          n.w = dW; n.h = Math.round((G.cardRef + grow)*1.15);
          n.x = n.cellX + (cellW*n.span + colGap*(n.span-1) - dW)/2;
        } else if(n.type === 'legend'){
          n.h = Math.round(u*3.4); n.x = n.cellX;
        } else {
          var P = G.plans[n.id];
          n.h = P.isNote ? P.h : Math.min(rh, (G.rowCard[n.row] || P.h) + grow);
          n.x = n.cellX;
        }
        n.y = rowTop[n.row] + (rh - n.h)/2;
        n.cx = n.x + n.w/2; n.cy = n.y + n.h/2;
      });

      // ---- layers ----
      var svgEl = svg('svg', {width:w, height:h});
      svgEl.style.cssText = 'position:absolute;left:0;top:0;overflow:visible;pointer-events:none;';
      var htmlLayer = el(null, 'position:absolute;left:0;top:0;width:'+w+'px;height:'+h+'px;');
      root.appendChild(svgEl); root.appendChild(htmlLayer);

      var panelHex = ctx.col('panel');
      var strokeW = Math.max(1.3, u*0.13);

      // ---- group frames (svg, so the text checker treats them as plain frames) ----
      var gBlock = {};
      blocks.forEach(function(b){ if(b.group) gBlock[b.group] = b; });
      groups.forEach(function(g){
        var b = gBlock[g.id];
        if(!b){ problems.push('group "'+g.id+'" has no nodes'); return; }
        var acc = HUE[g.hue] || 3;
        var fr = svg('rect', {x:x0, y:b.top, width:x1-x0, height:b.bottom-b.top, rx:Math.round(u*1.8), ry:Math.round(u*1.8),
          fill:ctx.cc('accf'+acc), 'fill-opacity':dark?0.5:0.55, stroke:ctx.cc('acc'+acc), 'stroke-width':strokeW});
        ctx.mark(fr, 'frame');
        svgEl.appendChild(fr);
      });

      // ---- routing ----
      var edges = edgesCfg.map(function(c, i){
        var a = byId[c.from], b = byId[c.to];
        if(!a || !b){ problems.push('edge '+i+' refers to unknown node "'+(a?c.to:c.from)+'"'); return null; }
        var kind = c.kind || 'next';
        // the final dashed flag is the one truth for "loop-back": styling, lit colour and ambient flow follow it;
        // kind only supplies the default and decides nothing else
        var dashed = c.dashed != null ? !!c.dashed : (kind === 'no' || kind === 'back');
        var fs = c.fromSide, ts = c.toSide;
        if(!fs || !ts){
          var dx = b.cx - a.cx, dy = b.cy - a.cy;
          var horiz = Math.abs(dy) < Math.min(a.h, b.h)*0.5 || (Math.abs(dx) > Math.abs(dy)*1.5);
          if(horiz){ fs = fs || (dx > 0 ? 'right' : 'left'); ts = ts || (dx > 0 ? 'left' : 'right'); }
          else { fs = fs || (dy > 0 ? 'bottom' : 'top'); ts = ts || (dy > 0 ? 'top' : 'bottom'); }
        }
        return {i:i, cfg:c, a:a, b:b, kind:kind, back:dashed, dashed:dashed, fs:fs, ts:ts, label:c.label||'', lane:c.lane||null};
      }).filter(Boolean);

      // ports: spread several edges on one side of a node; a diamond has one vertex per side
      var SPREAD = {1:[0.5], 2:[0.3, 0.7], 3:[0.2, 0.5, 0.8]};
      function spread(k, j){ return SPREAD[k] ? SPREAD[k][j] : (j+1)/(k+1); }
      var portGroups = {};
      edges.forEach(function(E){
        [['a','fs'], ['b','ts']].forEach(function(pr){
          var n = E[pr[0]], side = E[pr[1]], k = n.id + '|' + side;
          (portGroups[k] = portGroups[k] || []).push({E:E, end:pr[0]});
        });
      });
      Object.keys(portGroups).forEach(function(k){
        var list = portGroups[k];
        var node = list[0].E[list[0].end];
        var side = k.split('|')[1];
        var vert = side === 'top' || side === 'bottom';
        function otherC(it){ var o = it.E[it.end === 'a' ? 'b' : 'a']; return vert ? o.cx : o.cy; }
        list.sort(function(p, q){ return otherC(p) - otherC(q); });
        var nodeC = vert ? node.cx : node.cy;
        if(node.type === 'diamond'){
          list.forEach(function(it){ it.E['f_'+it.end] = 0.5; });
          return;
        }
        // an edge whose other end is a diamond and that faces it straight keeps the centre (a straight line)
        var forced = list.filter(function(it){
          var o = it.E[it.end === 'a' ? 'b' : 'a'];
          return o.type === 'diamond' && Math.abs(otherC(it) - nodeC) < 2;
        });
        var rest = list.filter(function(it){ return forced.indexOf(it) < 0; });
        forced.forEach(function(it){ it.E['f_'+it.end] = 0.5; });
        if(forced.length){
          var lo = rest.filter(function(it){ return otherC(it) < nodeC; });
          var hi = rest.filter(function(it){ return otherC(it) >= nodeC; });
          lo.forEach(function(it, j){ it.E['f_'+it.end] = 0.2 - 0.1*(lo.length-1-j)/Math.max(1, lo.length); });
          hi.forEach(function(it, j){ it.E['f_'+it.end] = 0.8 + 0.1*j/Math.max(1, hi.length); });
        } else {
          rest.forEach(function(it, j){ it.E['f_'+it.end] = spread(rest.length, j); });
        }
      });

      function portPt(n, side, f){
        if(side === 'top')    return {x:n.x + n.w*f, y:n.y};
        if(side === 'bottom') return {x:n.x + n.w*f, y:n.y + n.h};
        if(side === 'left')   return {x:n.x,         y:n.y + n.h*f};
        return {x:n.x + n.w, y:n.y + n.h*f};
      }

      var laneXL = marginX + gutter*0.5, laneXR = w - marginX - gutter*0.5;
      var cornerR = Math.round(u*1.3);
      edges.forEach(function(E){
        var p0 = portPt(E.a, E.fs, E.f_a), p1 = portPt(E.b, E.ts, E.f_b);
        var d0 = SIDE[E.fs], d1 = SIDE[E.ts];
        var pts;
        var h0 = d0.x !== 0, h1 = d1.x !== 0;
        if(E.lane){
          var lx = E.lane === 'left' ? laneXL : laneXR;
          pts = [p0, {x:lx, y:p0.y}, {x:lx, y:p1.y}, p1];
        } else if(h0 && h1){
          if(Math.abs(p0.y - p1.y) < 1.5) pts = [p0, p1];
          else { var mx = (p0.x + p1.x)/2; pts = [p0, {x:mx, y:p0.y}, {x:mx, y:p1.y}, p1]; }
        } else if(!h0 && !h1){
          if(Math.abs(p0.x - p1.x) < 1.5) pts = [p0, p1];
          else {
            var my = (p0.y + p1.y)/2;
            // a Z that crosses group blocks bends in the gap between them
            if(E.a.group !== E.b.group){
              var lo2 = Math.min(p0.y, p1.y), hi2 = Math.max(p0.y, p1.y), best = null;
              gapCenters.forEach(function(g){ if(g > lo2 && g < hi2 && (best == null || Math.abs(g-my) < Math.abs(best-my))) best = g; });
              if(best != null) my = best;
            }
            pts = [p0, {x:p0.x, y:my}, {x:p1.x, y:my}, p1];
          }
        } else if(h0 && !h1){
          pts = [p0, {x:p1.x, y:p0.y}, p1];
        } else {
          pts = [p0, {x:p0.x, y:p1.y}, p1];
        }
        pts = dedupe(pts);
        E.pts = pts;
        E.d = roundedPath(pts, cornerR);
        // obstacle check (corner points only matter for the sharp polyline)
        for(var s = 0; s + 1 < pts.length; s++){
          nodes.forEach(function(n){
            if(n === E.a || n === E.b) return;
            var a = pts[s], b = pts[s+1];
            var minx = Math.min(a.x,b.x), maxx = Math.max(a.x,b.x), miny = Math.min(a.y,b.y), maxy = Math.max(a.y,b.y);
            if(maxx > n.x + 2 && minx < n.x + n.w - 2 && maxy > n.y + 2 && miny < n.y + n.h - 2)
              problems.push('edge '+E.cfg.from+'→'+E.cfg.to+' passes through node "'+n.id+'"');
          });
        }
      });

      // ---- group titles: sit in the longest stretch of the title strip that no vertical edge crosses ----
      var obstacles = [];          // {l,t,r,b} rects labels must keep clear of
      var textBoxes = [];          // text boxes every edge path must keep 1.5u away from
      groups.forEach(function(g){
        var b = gBlock[g.id];
        if(!b) return;
        var ty = b.top + Math.round(u*0.8);
        var sSz = Math.max(11, Math.round(gTitleSize*0.7));
        // every edge piece that touches the strip blocks its x-range; the glow of a packet needs 2u either side
        var clr = u*2.0, blocked = [];
        edges.forEach(function(E){
          for(var k = 0; k + 1 < E.pts.length; k++){
            var A = E.pts[k], B = E.pts[k+1];
            if(Math.min(A.y,B.y) < ty + gTitleLh + 2 && Math.max(A.y,B.y) > ty - 2){
              var bl = Math.min(A.x,B.x) - clr, br = Math.max(A.x,B.x) + clr;
              if(br > x0 + gp && bl < x1 - gp) blocked.push([bl, br]);
            }
          }
        });
        blocked.sort(function(m, n2){ return m[0] - n2[0]; });
        var spans = [], cur = x0 + gp;
        blocked.forEach(function(bk){
          if(bk[0] > cur) spans.push([cur, bk[0]]);
          cur = Math.max(cur, bk[1]);
        });
        if(cur < x1 - gp) spans.push([cur, x1 - gp]);
        if(!spans.length) spans.push([x0 + gp, x1 - gp]);
        var wantW = ctx.measure(g.label, gTitleSize, ff, true) + (g.sub ? ctx.measure(g.sub, sSz, ff, false) + u*1.0 : 0);
        var pick = null;
        spans.forEach(function(sp2){
          if(!pick && sp2[1] - sp2[0] >= wantW) pick = sp2;
        });
        if(!pick) pick = spans.reduce(function(m, sp2){ return (sp2[1]-sp2[0] > m[1]-m[0]) ? sp2 : m; }, spans[0]);
        var tx = pick[0], room = pick[1] - pick[0];
        var fl = ctx.fit(g.label, gTitleSize, room*(g.sub ? 0.66 : 1), ff, 12, true);
        var tl = el(null, 'position:absolute;left:'+Math.round(tx)+'px;top:'+ty+'px;height:'+gTitleLh+'px;line-height:'+gTitleLh+'px;'+ffCss+'font-size:'+fl.size+'px;font-weight:700;color:'+ctx.cc('fg')+';white-space:pre;');
        tl.textContent = fl.text; ctx.mark(tl, 'text'); htmlLayer.appendChild(tl);
        var sw = ctx.measure(fl.text, fl.size, ff, true);
        var rEnd = tx + sw;
        if(g.sub){
          var fs = ctx.fit(g.sub, sSz, Math.max(30, room - sw - u*1.0), ff, 11, false);
          var tsEl = el(null, 'position:absolute;left:'+Math.round(tx + sw + u*1.0)+'px;top:'+ty+'px;height:'+gTitleLh+'px;line-height:'+gTitleLh+'px;'+ffCss+'font-size:'+fs.size+'px;color:'+ctx.cc('muted')+';white-space:pre;');
          tsEl.textContent = fs.text; ctx.mark(tsEl, 'text'); htmlLayer.appendChild(tsEl);
          rEnd = tx + sw + u*1.0 + ctx.measure(fs.text, fs.size, ff, false);
        }
        obstacles.push({l:tx, t:ty, r:rEnd, b:ty + gTitleLh});
        textBoxes.push({l:tx, t:ty, r:rEnd, b:ty + gTitleLh, what:'group title "'+g.id+'"'});
        // frame borders are obstacles too: labels must not straddle them
        obstacles.push({l:x0, t:b.top - 3, r:x1, b:b.top + 3});
        obstacles.push({l:x0, t:b.bottom - 3, r:x1, b:b.bottom + 3});
      });

      // ---- edge drawing (svg): base (marked) + lit overlay (unmarked, animated) + arrow + flow dots + mid dot ----
      var okCol = ctx.cc('ok'), warnCol = ctx.cc('warn');
      var dashLen = Math.round(u*1.1) + Math.round(u*0.9);        // dash pattern length
      var dashArr = Math.round(u*1.1) + ' ' + Math.round(u*0.9);
      var flowPeriod = period/Math.max(1, Math.round(period/1.15));   // ~1.15 s, divides the period
      var dashPeriod = period/Math.max(1, Math.round(period/0.5));
      var gEdges = svg('g', {}), gFlow = svg('g', {}), gLit = svg('g', {}), gTok = svg('g', {}), gNode = svg('g', {}), gNodeLit = svg('g', {});
      [gEdges, gFlow, gLit, gTok, gNode, gNodeLit].forEach(function(g){ svgEl.appendChild(g); });
      var labelNodes = [];
      var midR = Math.max(4, u*0.55);
      var arrowLen = Math.max(7, u*0.85);

      edges.forEach(function(E){
        var base = svg('path', {d:E.d, fill:'none', stroke:ctx.cc(E.back ? 'dim' : 'muted'), 'stroke-width':strokeW,
          'stroke-linejoin':'round', 'stroke-linecap':'round', opacity:E.back ? 0.85 : 0.9});
        if(E.dashed) base.setAttribute('stroke-dasharray', dashArr);
        ctx.mark(base, 'edge');
        gEdges.appendChild(base);
        E.base = base;
        // arrow head at the end
        var pe = E.pts[E.pts.length-1], pq = E.pts[E.pts.length-2];
        var L = Math.hypot(pe.x-pq.x, pe.y-pq.y) || 1;
        var ux = (pe.x-pq.x)/L, uy = (pe.y-pq.y)/L, ah = arrowLen;
        var arrow = svg('polygon', {points:[
          pe.x+','+pe.y,
          (pe.x - ux*ah + uy*ah*0.5)+','+(pe.y - uy*ah - ux*ah*0.5),
          (pe.x - ux*ah - uy*ah*0.5)+','+(pe.y - uy*ah + ux*ah*0.5)].join(' '),
          fill:ctx.cc(E.back ? 'dim' : 'muted')});
        gEdges.appendChild(arrow);
        // lit overlay
        var lit = svg('path', {d:E.d, fill:'none', stroke:E.back ? warnCol : okCol, 'stroke-width':strokeW*1.9,
          'stroke-linejoin':'round', 'stroke-linecap':'round', opacity:0});
        if(E.dashed) lit.setAttribute('stroke-dasharray', dashArr);
        gLit.appendChild(lit);
        E.lit = lit;
        // sample the real (rounded) path once so token / dots follow the drawn curve exactly
        var len = base.getTotalLength();
        var n = Math.max(2, Math.ceil(len/2));
        var sx = [], sy = [];
        for(var k = 0; k <= n; k++){ var pp = base.getPointAtLength(len*k/n); sx.push(pp.x); sy.push(pp.y); }
        E.len = len; E.sx = sx; E.sy = sy;
        // the one resident dot: middle of the longest straight stretch, kept off the arrowhead
        var li2 = 0, best2 = -1;
        for(var s3 = 0; s3 + 1 < E.pts.length; s3++){
          var sl = Math.hypot(E.pts[s3+1].x - E.pts[s3].x, E.pts[s3+1].y - E.pts[s3].y);
          if(sl > best2){ best2 = sl; li2 = s3; }
        }
        var A2 = E.pts[li2], B2 = E.pts[li2+1];
        var fr = 0.5;
        if(li2 + 2 === E.pts.length) fr = Math.max(0.2, Math.min(0.5, 1 - (u*1.5 + arrowLen)/Math.max(1, best2)));
        E.mid = {x:A2.x + (B2.x - A2.x)*fr, y:A2.y + (B2.y - A2.y)*fr};
        if(!amb){
          var md = svg('circle', {cx:E.mid.x, cy:E.mid.y, r:midR, fill:okCol});
          if(dark) md.setAttribute('opacity', 0.95);
          gFlow.appendChild(md);
        }
        // walk-only: sparse ambient flow on forward edges that are long enough to carry it
        E.dots = [];
        if(!amb && !E.back && len >= u*14){
          var nd = Math.max(1, Math.round(len/(u*9)));
          for(var j = 0; j < nd; j++){
            var dc = svg('circle', {cx:0, cy:0, r:Math.max(1.3, u*0.14), fill:okCol, opacity:dark ? 0.4 : 0.35});
            gFlow.appendChild(dc);
            E.dots.push({el:dc, off:j/nd});
          }
        }
      });

      // ---- ambient packets: one speed (px/s) on every forward edge, seamless within ambientPeriod ----
      // the flow cycle of an edge is S/k (k whole): a packet moves exactly S per period, so the lap closes
      var packets = [];
      var flowS = 0, flowV = 0;
      if(amb){
        var fl = edges.filter(function(E){ return !E.back; }).map(function(E){ return E.len; }).sort(function(a, b){ return a - b; });
        // big and few: S is at least half the longest forward edge, so no edge carries more than two packets
        flowS = Math.max(u*14, fl.length ? Math.max(fl[Math.floor(fl.length*0.7)], fl[fl.length - 1]/2) : u*16);
        flowV = flowS/AP;
        var pr = Math.max(4.4, u*0.52);
        var defs = svg('defs', {}), flt = svg('filter', {id:'lpLoopGlow', filterUnits:'userSpaceOnUse', x:0, y:0, width:w, height:h});
        flt.appendChild(svg('feGaussianBlur', {'in':'SourceGraphic', stdDeviation:(pr*0.9).toFixed(1), result:'b'}));
        var fm = svg('feMerge', {});
        fm.appendChild(svg('feMergeNode', {'in':'b'})); fm.appendChild(svg('feMergeNode', {'in':'SourceGraphic'}));
        flt.appendChild(fm); defs.appendChild(flt); svgEl.insertBefore(defs, svgEl.firstChild);
        if(dark) gFlow.setAttribute('filter', 'url(#lpLoopGlow)');
        function makePk(r0, nTr){
          var o = {head:null, halo:null, tr:[]};
          if(!dark) o.halo = gFlow.appendChild(svg('circle', {cx:-20, cy:-20, r:r0*1.9, fill:okCol, opacity:0}));
          for(var q = 0; q < nTr; q++) o.tr.push(gFlow.appendChild(svg('circle', {cx:-20, cy:-20, r:r0*(1 - 0.13*(q + 1)), fill:okCol, opacity:0})));
          o.head = gFlow.appendChild(svg('circle', {cx:-20, cy:-20, r:r0, fill:okCol, opacity:0}));
          return o;
        }
        edges.forEach(function(E){
          if(E.back){
            // one lit dot rides every loop-back dash once per period: a size smaller, translucent, two-step tail
            var bo = makePk(pr*0.72, 2);
            bo.head.setAttribute('fill', warnCol); bo.tr.forEach(function(c){ c.setAttribute('fill', warnCol); });
            E.bk = bo; E.bkTail = Math.min(E.len*0.04, u*1.2);
            return;
          }
          var k = Math.max(1, Math.ceil(flowS/E.len - 1e-6));
          var cyc = flowS/k, cnt = Math.max(1, Math.ceil(E.len/cyc - 1e-6));
          E.cyc = cyc; E.k = k;
          E.pk = [];
          for(var m = 0; m < cnt; m++){ var o = makePk(pr, 5); o.m = m; E.pk.push(o); }
          E.tail = Math.min(cyc*0.3, u*2.4);
          // arrival of the first packet at the card border, inside one cycle (period/k): drives the node ripple
          var mm = Math.floor(E.len/cyc - 1e-6);
          E.arrive = (E.len - mm*cyc)/flowV;
        });
      }

      // labels: try spots next to the source vertex first (decision labels), then along the segments (long first);
      // keep the first spot clear of nodes, other edges, frame borders, titles, mid dots and earlier labels
      function hitRect(r2, o){ return r2.l < o.r && r2.r > o.l && r2.t < o.b && r2.b > o.t; }
      var placed = [], stretches = [];
      edges.forEach(function(F){
        for(var k = 0; k + 1 < F.pts.length; k++){
          var P = F.pts[k], Q = F.pts[k+1];
          stretches.push({l:Math.min(P.x,Q.x) - 3, r:Math.max(P.x,Q.x) + 3, t:Math.min(P.y,Q.y) - 3, b:Math.max(P.y,Q.y) + 3});
        }
      });
      var dotClear = u*1.5;
      function nearDot(r2){
        return edges.some(function(E){
          var dx = Math.max(r2.l - E.mid.x, 0, E.mid.x - r2.r), dy = Math.max(r2.t - E.mid.y, 0, E.mid.y - r2.b);
          return Math.hypot(dx, dy) < dotClear;
        });
      }
      nodes.forEach(function(n){
        obstacles.push({l:n.x - 2, t:n.y - 2, r:n.x + n.w + 2, b:n.y + n.h + 2});
      });
      edges.forEach(function(E){
        if(!E.label) return;
        var ls = clamp(u*1.2, 11, 15);
        var lh = Math.round(ls*1.5);
        var fl2 = ctx.fit(E.label, ls, u*18, ff, 11, false);
        var lw = Math.round(ctx.measure(fl2.text, fl2.size, ff, false)) + 8;
        var lab = el(null, 'position:absolute;height:'+lh+'px;line-height:'+lh+'px;'+ffCss+'font-size:'+fl2.size+'px;color:'+ctx.cc('fg')+';white-space:pre;padding:0 4px;');
        lab.textContent = fl2.text;
        ctx.mark(lab, 'text');
        var cands = [];
        if(E.a.type === 'diamond' && !E.lane){
          var S0 = E.pts[0], S1 = E.pts[1];
          var sl2 = Math.hypot(S1.x - S0.x, S1.y - S0.y) || 1;
          var vx = (S1.x - S0.x)/sl2, vy = (S1.y - S0.y)/sl2;
          [5, 12, 22, 34, 48].forEach(function(dist){
            [6, 14, Math.round(dotClear + 3)].forEach(function(side){
              if(Math.abs(vx) < 0.5){
                var cy2 = S0.y + vy*(dist + lh/2);
                cands.push({l:S0.x + side, t:cy2 - lh/2});
                cands.push({l:S0.x - side - lw, t:cy2 - lh/2});
              } else {
                var cx2 = S0.x + vx*(dist + lw/2);
                cands.push({l:cx2 - lw/2, t:S0.y - lh - side});
                cands.push({l:cx2 - lw/2, t:S0.y + side});
              }
            });
          });
        }
        var segs = [];
        for(var s2 = 0; s2 + 1 < E.pts.length; s2++){
          var A = E.pts[s2], B = E.pts[s2+1];
          segs.push({A:A, B:B, len:Math.hypot(B.x-A.x, B.y-A.y), vert:Math.abs(B.x-A.x) < 1});
        }
        segs.sort(function(p, q){ return q.len - p.len; });
        var off = Math.ceil(midR) + 5;
        segs.forEach(function(sg){
          [0.5, 0.45, 0.55, 0.4, 0.6, 0.35, 0.65, 0.3, 0.7, 0.25, 0.75, 0.2, 0.8].forEach(function(fr2){
            var cx = sg.A.x + (sg.B.x - sg.A.x)*fr2, cy = sg.A.y + (sg.B.y - sg.A.y)*fr2;
            if(E.lane){ cands.push({l:cx - lw/2, t:cy - lh/2, onLine:true, rot:true}); return; }
            if(sg.vert){
              cands.push({l:cx + off, t:cy - lh/2});
              cands.push({l:cx - off - lw, t:cy - lh/2});
            } else {
              cands.push({l:cx - lw/2, t:cy - lh - off});
              cands.push({l:cx - lw/2, t:cy + off});
            }
          });
        });
        var pick = null;
        for(var ci = 0; ci < cands.length && !pick; ci++){
          var c = cands[ci];
          var r2 = c.rot ? {l:c.l + lw/2 - lh/2, t:c.t + lh/2 - lw/2, r:c.l + lw/2 + lh/2, b:c.t + lh/2 + lw/2}
                         : {l:c.l, t:c.t, r:c.l + lw, b:c.t + lh};
          if(r2.l < 0 || r2.t < 0 || r2.r > w || r2.b > h) continue;
          var bad = obstacles.some(function(o){ return hitRect(r2, o); });
          if(!bad) bad = placed.some(function(o){ return hitRect(r2, o); }) || nearDot(r2);
          if(!bad && !c.onLine){
            bad = stretches.some(function(o){ return hitRect(r2, o); });   // clear of every edge, this one included
          }
          if(!bad) pick = {c:c, r:r2};
        }
        if(!pick){
          pick = {c:cands[0], r:{l:cands[0].l, t:cands[0].t, r:cands[0].l + lw, b:cands[0].t + lh}};
          problems.push('edge label "'+E.label+'" has no clear spot');
        }
        var cc = pick.c;
        lab.style.left = Math.round(cc.l) + 'px'; lab.style.top = Math.round(cc.t) + 'px';
        if(cc.onLine) lab.style.cssText += 'width:'+lw+'px;text-align:center;background:'+ctx.cc('bg')+';transform:rotate(-90deg);';
        placed.push(pick.r);
        labelNodes.push(lab);
        textBoxes.push({l:pick.r.l, t:pick.r.t, r:pick.r.r, b:pick.r.b, own:E, what:'label "'+E.label+'"'});
      });
      // clearance: no edge path (solid or dashed) comes closer than 1.5u to a text box; a label's own edge is exempt
      function segRectDist(A, B, R){
        var best = 1e9;
        for(var q = 0; q <= 40; q++){
          var px = A.x + (B.x - A.x)*q/40, py = A.y + (B.y - A.y)*q/40;
          var dx = Math.max(R.l - px, 0, px - R.r), dy = Math.max(R.t - py, 0, py - R.b);
          best = Math.min(best, Math.hypot(dx, dy));
        }
        return best;
      }
      textBoxes.forEach(function(T){
        edges.forEach(function(E){
          if(T.own === E) return;
          for(var k = 0; k + 1 < E.pts.length; k++){
            if(segRectDist(E.pts[k], E.pts[k+1], T) < u*1.5){
              problems.push('edge '+E.cfg.from+'→'+E.cfg.to+' runs closer than 1.5u to '+T.what);
              return;
            }
          }
        });
      });

      // ---- nodes ----
      var cardR = Math.round(u*1.1);
      var hiddenLines = 0, totalLines = 0;
      var nodeLit = {};          // id -> focus overlay element
      var ripples = [];          // delivery feedback, one per node that has a forward incoming edge
      var statusRefs = null;

      var iconAnims = [];          // {kind, g, parts, ph}: driven by seek, one lap per ambient period
      var iconCount = 0;
      function iconSvg(name, size, color, animate){
        var nm = (animate && ICON_ALIAS[name]) || name;
        var body = ICONS[nm];
        if(!body){ if(name) problems.push('unknown icon "'+name+'" (using circle)'); body = ICONS.circle; nm = 'circle'; }
        var s = svg('svg', {viewBox:'0 0 24 24', width:size, height:size, fill:'none', stroke:'currentColor',
          'stroke-width':2, 'stroke-linecap':'round', 'stroke-linejoin':'round'});
        s.style.cssText = 'display:block;overflow:visible;color:'+color+';';
        if(!animate || !amb){ s.innerHTML = body; return s; }
        // split the body into top-level elements; the part that moves differently gets its own group
        var g = svg('g', {});
        var parts = null, kind = nm;
        var tmp = svg('g', {}); tmp.innerHTML = body;
        var kids = Array.prototype.slice.call(tmp.childNodes);
        if(nm === 'message-square-more'){
          parts = kids.slice(1).map(function(k){ var pg = svg('g', {}); pg.appendChild(k); return pg; });
          g.appendChild(kids[0]); parts.forEach(function(pg){ g.appendChild(pg); });
        } else if(nm === 'timer'){
          var hand = svg('g', {}), knob = svg('g', {}); hand.appendChild(kids[1]); knob.appendChild(kids[0]);
          parts = [hand, knob]; g.appendChild(knob); g.appendChild(kids[2]); g.appendChild(hand);
        } else if(nm === 'eye'){
          var pup = svg('g', {}); pup.appendChild(kids[1]);
          parts = [pup]; g.appendChild(kids[0]); g.appendChild(pup);
        } else if(nm === 'shield-check'){
          kids[1].setAttribute('pathLength', 1); kids[1].setAttribute('stroke-dasharray', '1 2');
          parts = [kids[1]]; kids.forEach(function(k){ g.appendChild(k); });
        } else {
          kids.forEach(function(k){ g.appendChild(k); });
        }
        s.appendChild(g);
        iconAnims.push({kind:kind, g:g, parts:parts, ph:modf(iconCount*0.37, 1), k:24/size});
        iconCount += 1;
        return s;
      }

      nodes.forEach(function(n){
        var acc = accOf(n);
        var accC = ctx.cc('acc'+acc), accHex = ctx.col('acc'+acc), accfHex = ctx.col('accf'+acc);
        if(n.type === 'diamond'){
          var pts = [[n.cx, n.y], [n.x+n.w, n.cy], [n.cx, n.y+n.h], [n.x, n.cy]];
          var pstr = pts.map(function(p){ return p[0]+','+p[1]; }).join(' ');
          var poly = svg('polygon', {points:pstr, fill:mixHex(panelHex, accfHex, 0.55), stroke:accC, 'stroke-width':strokeW*1.15, 'stroke-linejoin':'round'});
          ctx.mark(poly, 'box');
          gNode.appendChild(poly);
          // focus: brighter fill + 2x outline (+ a soft wide halo on dark), one group whose opacity seek drives
          var fg = svg('g', {opacity:0});
          if(dark && !weak) fg.appendChild(svg('polygon', {points:pstr, fill:'none', stroke:rgba(accHex, 0.26), 'stroke-width':strokeW*6, 'stroke-linejoin':'round'}));
          fg.appendChild(svg('polygon', {points:pstr, fill:rgba(accHex, dark ? 0.2 : 0.16), stroke:accC, 'stroke-width':strokeW*(weak ? 1.5 : 2.3), 'stroke-linejoin':'round'}));
          gNodeLit.appendChild(fg);
          nodeLit[n.id] = fg;
          if(amb){
            var rp = svg('polygon', {points:pstr, fill:'none', stroke:accC, 'stroke-width':strokeW*1.6, 'stroke-linejoin':'round', 'stroke-opacity':0});
            gNodeLit.appendChild(rp);
            ripples.push({id:n.id, poly:rp, cx:n.cx, cy:n.cy, a:n.w/2, b:n.h/2, L:Math.hypot(n.w/2, n.h/2)});
          }
          // text in the inscribed rectangle
          var iw = n.w/2*0.98, ih = n.h/2*0.96;
          var ls1 = clamp(u*1.5, 13, 19)*scale, es1 = Math.max(11, Math.round(ls1*0.72));
          var f1 = ctx.fit(n.label, ls1, iw, ff, 12, true);
          var f2 = n.en ? ctx.fit(n.en, es1, iw, ff, 11, false) : null;
          var l1h = Math.round(f1.size*1.55), l2h = f2 ? Math.round(f2.size*1.55) : 0;
          while(l1h + l2h > ih && f1.size > 12){ f1 = ctx.fit(n.label, f1.size - 1, iw, ff, 12, true); l1h = Math.round(f1.size*1.55); }
          var top = n.cy - (l1h + l2h)/2;
          var a1 = el(null, 'position:absolute;left:'+Math.round(n.cx - iw)+'px;width:'+Math.round(iw*2)+'px;top:'+Math.round(top)+'px;height:'+l1h+'px;line-height:'+l1h+'px;text-align:center;'+ffCss+'font-size:'+f1.size+'px;font-weight:700;color:'+ctx.cc('fg')+';white-space:pre;');
          a1.textContent = f1.text; a1.setAttribute('data-in', '1'); ctx.mark(a1, 'text'); htmlLayer.appendChild(a1);
          if(f2){
            var a2 = el(null, 'position:absolute;left:'+Math.round(n.cx - iw)+'px;width:'+Math.round(iw*2)+'px;top:'+Math.round(top + l1h)+'px;height:'+l2h+'px;line-height:'+l2h+'px;text-align:center;'+ffCss+'font-size:'+f2.size+'px;color:'+ctx.cc('muted')+';white-space:pre;');
            a2.textContent = f2.text; a2.setAttribute('data-in', '1'); ctx.mark(a2, 'text'); htmlLayer.appendChild(a2);
          }
          return;
        }

        if(n.type === 'legend'){
          // inline key: sample line + word, spread over the node's width
          var items = n.items.length ? n.items : [{style:'solid', text:'forward'}, {style:'dashed', text:'loop back'}, {style:'dot', text:'data passes'}];
          var lsz = clamp(u*1.25, 11, 15), llh = Math.round(lsz*1.4);
          var cw = n.w/items.length, sw2 = Math.round(u*3.2);
          items.forEach(function(it, k){
            var ix = n.x + k*cw, iy = n.cy;
            var fl3 = ctx.fit(it.text, lsz, cw - sw2 - u*1.4, ff, 11, false);
            if(it.style === 'dot'){
              gEdges.appendChild(svg('circle', {cx:ix + sw2/2, cy:iy, r:midR, fill:okCol}));
            } else {
              var ln = svg('line', {x1:ix, y1:iy, x2:ix + sw2, y2:iy, stroke:ctx.cc(it.style === 'dashed' ? 'dim' : 'muted'), 'stroke-width':strokeW, 'stroke-linecap':'round'});
              if(it.style === 'dashed') ln.setAttribute('stroke-dasharray', dashArr);
              gEdges.appendChild(ln);
            }
            var lt = el(null, 'position:absolute;left:'+Math.round(ix + sw2 + u*0.7)+'px;top:'+Math.round(iy - llh/2)+'px;height:'+llh+'px;line-height:'+llh+'px;'+ffCss+'font-size:'+fl3.size+'px;color:'+ctx.cc('muted')+';white-space:pre;');
            lt.textContent = fl3.text; ctx.mark(lt, 'text'); htmlLayer.appendChild(lt);
          });
          return;
        }

        // card / trigger / output / note
        var P = G.plans[n.id];
        var isNote = P.isNote;
        var isOut = n.type === 'output';
        var bw = strokeW*(isOut ? 1.4 : 1.1);
        var card = el(null, 'position:absolute;box-sizing:border-box;left:'+Math.round(n.x)+'px;top:'+Math.round(n.y)+'px;width:'+Math.round(n.w)+'px;height:'+Math.round(n.h)+'px;'
          + (isNote ? '' : 'border:'+bw.toFixed(2)+'px solid '+accC+';border-radius:'+cardR+'px;background:'+mixHex(panelHex, accfHex, isOut ? 0.75 : 0.45)+';'));
        // a borderless note is a plain annotation: still a marked box so frames/text checks see it, but invisible
        ctx.mark(card, 'box');
        htmlLayer.appendChild(card);

        // focus overlay lives inside the card, below the text, above the card background: 2x outline in the group colour
        if(!isNote){
          var ovw = strokeW*(weak ? 1.5 : 2.3);
          var ov = el(null, 'position:absolute;left:'+(-bw).toFixed(2)+'px;top:'+(-bw).toFixed(2)+'px;right:'+(-bw).toFixed(2)+'px;bottom:'+(-bw).toFixed(2)+'px;border-radius:'+cardR+'px;border:'+ovw.toFixed(2)+'px solid '+accC+';background:'+rgba(accHex, dark ? 0.16 : 0.14)+';opacity:0;'
            + (weak ? '' : dark ? 'box-shadow:0 0 '+Math.round(u*1.8)+'px '+rgba(accHex, 0.6)+';' : 'box-shadow:0 '+Math.round(u*0.3)+'px '+Math.round(u*1.2)+'px '+rgba(accHex, 0.35)+';'));
          card.appendChild(ov);
          nodeLit[n.id] = ov;
          if(amb){
            var ringCss = 'position:absolute;box-sizing:border-box;pointer-events:none;border-radius:'+(cardR + 3)+'px;border:'+(strokeW*1.4).toFixed(2)+'px solid '+accC+';';
            var ring = el(null, ringCss + 'opacity:0;');
            card.appendChild(ring);
            ripples.push({id:n.id, ring:ring, ringCss:ringCss, card:card, bw:bw, glow:rgba(accHex, 'A')});
          }
        }

        var hasIcon = n.icon != null;
        var isize = P.isize, pad = P.pad, tx0 = P.tx0, tw = P.tw;
        if(hasIcon){
          if(isNote){
            var nic = iconSvg(n.icon, isize, ctx.cc('muted'), true);
            nic.style.cssText += 'position:absolute;left:'+pad+'px;top:'+Math.round((n.h - isize)/2)+'px;';
            card.appendChild(nic);
          } else {
            var box = el(null, 'position:absolute;left:'+pad+'px;top:'+Math.round((n.h - isize)/2 - bw)+'px;width:'+isize+'px;height:'+isize+'px;border-radius:'+Math.round(u*0.9)+'px;background:'+(isOut ? accC : mixHex(panelHex, accfHex, 0.9))+';'+(dark && !isOut ? 'box-shadow:0 0 '+Math.round(u*0.9)+'px '+rgba(accHex, 0.28)+';' : ''));
            var ic = iconSvg(n.icon, Math.round(isize*0.56), isOut ? ctx.cc('bg') : accC, true);
            ic.style.cssText += 'position:absolute;left:'+Math.round(isize*0.22)+'px;top:'+Math.round(isize*0.22)+'px;';
            box.appendChild(ic);
            card.appendChild(box);
          }
        }
        var tLh = P.tLh, dLh = P.dLh;
        var descC = ctx.cc('muted');
        var blockH = P.textH;
        var ty0 = Math.round((n.h - blockH)/2 - (isNote ? 0 : bw));
        var tn = null;
        if(n.label){
          var tc = isNote ? descC : ctx.cc('fg');
          tn = el(null, 'position:absolute;left:'+tx0+'px;top:'+ty0+'px;height:'+tLh+'px;line-height:'+tLh+'px;'+ffCss+'font-size:'+P.title.size+'px;font-weight:700;color:'+tc+';white-space:pre;');
          tn.textContent = P.title.text; ctx.mark(tn, 'text'); card.appendChild(tn);
          if(n.en){
            totalEn += 1;
            if(P.enMode === 'inline'){
              var lwid = ctx.measure(P.title.text, P.title.size, ff, true);
              var en = el(null, 'position:absolute;left:'+Math.round(tx0 + lwid + P.en.gap)+'px;top:'+ty0+'px;height:'+tLh+'px;line-height:'+tLh+'px;'+ffCss+'font-size:'+P.en.size+'px;color:'+descC+';white-space:pre;');
              en.textContent = n.en; ctx.mark(en, 'text'); card.appendChild(en);
            } else if(P.enMode === 'below'){
              var en2 = el(null, 'position:absolute;left:'+tx0+'px;top:'+(ty0 + tLh)+'px;height:'+dLh+'px;line-height:'+dLh+'px;'+ffCss+'font-size:'+P.en.size+'px;color:'+descC+';white-space:pre;');
              en2.textContent = n.en; ctx.mark(en2, 'text'); card.appendChild(en2);
            } else {
              hiddenEn += 1;
              problems.push('English gloss "'+n.en+'" of "'+n.id+'" does not fit and is hidden');
            }
          }
        }
        if(P.isStatus){
          // dynamic lines: round counter (title font), current step, and a dot per visited node of the round
          var S = P.st;
          var base0 = Math.round((n.h - P.textH)/2 - bw);
          if(tn){ tn.style.top = base0 + 'px'; base0 += tLh; }
          var rn = el(null, 'position:absolute;left:'+tx0+'px;width:'+Math.round(tw)+'px;top:'+base0+'px;height:'+S.rLh+'px;line-height:'+S.rLh+'px;font-family:var(--font-title);font-size:'+S.rSize+'px;font-weight:700;font-variant-numeric:tabular-nums;color:'+ctx.cc('fg')+';white-space:pre;text-align:left;');
          rn.textContent = S.rStr[0]; ctx.mark(rn, 'text'); card.appendChild(rn);
          var sn = el(null, 'position:absolute;left:'+tx0+'px;width:'+Math.round(tw)+'px;top:'+(base0 + S.rLh)+'px;height:'+S.sLh+'px;line-height:'+S.sLh+'px;'+ffCss+'font-size:'+S.sSize+'px;color:'+descC+';white-space:pre;text-align:left;');
          sn.textContent = ambientOnly ? S.sTpl : S.sTpl.replace('{label}', ''); ctx.mark(sn, 'text'); card.appendChild(sn);
          // progress dots (unmarked decoration, recoloured in seek)
          var dotsSvg = svg('svg', {width:Math.round(tw), height:S.dotsH});
          dotsSvg.style.cssText = 'position:absolute;left:'+tx0+'px;top:'+(base0 + S.rLh + S.sLh + Math.round(u*0.3))+'px;overflow:visible;';
          var stepDots = [];
          for(var di = 0; di < dotCount; di++){
            var dc2 = svg('circle', {cx:S.dotR + di*S.dotGap, cy:S.dotsH/2, r:S.dotR, fill:ctx.cc('line2')});
            dotsSvg.appendChild(dc2); stepDots.push(dc2);
          }
          card.appendChild(dotsSvg);
          rn.textContent = S.rStr[0];
          statusRefs = {off:ctx.cc('line2'), round:rn, step:sn, rTpl:S.rTpl, sTpl:S.sTpl, dots:stepDots, accOn:accC};
        } else {
          var dy0 = ty0 + (n.label ? tLh + (P.enMode === 'below' ? dLh : 0) : 0);
          for(var di2 = 0; di2 < P.desc.length; di2++){
            var df = ctx.fit(P.desc[di2], P.descSize, tw, ff, 11, false);
            var dn = el(null, 'position:absolute;left:'+tx0+'px;top:'+(dy0 + di2*dLh)+'px;height:'+dLh+'px;line-height:'+dLh+'px;'+ffCss+'font-size:'+df.size+'px;color:'+descC+';white-space:pre;');
            dn.textContent = df.text; ctx.mark(dn, 'text'); card.appendChild(dn);
            if(P.dashW){
              var dsv = svg('svg', {width:P.dashW, height:dLh});
              dsv.style.cssText = 'position:absolute;left:'+(tx0 - P.dashW)+'px;top:'+(dy0 + di2*dLh)+'px;overflow:visible;';
              dsv.appendChild(svg('line', {x1:1, y1:dLh/2, x2:P.dashW - Math.round(u*0.7), y2:dLh/2, stroke:warnCol, 'stroke-width':strokeW*1.2,
                'stroke-linecap':'round', 'stroke-dasharray':Math.round(u*0.8)+' '+Math.round(u*0.5)}));
              card.appendChild(dsv);
            }
          }
          totalLines += P.total; hiddenLines += P.hidden;
        }
      });
      // first forward incoming edge decides when the ripple starts (0.15 s before the packet lands)
      ripples = ripples.filter(function(R){
        var inE = edges.filter(function(E){ return !E.back && E.b.id === R.id && E.arrive !== undefined; })[0];
        if(!inE) return false;
        R.t0 = inE.arrive - 0.15; R.inE = inE;
        return true;
      });
      // stagger delivery: spread the ripple instants evenly over the ambient period, in node order, and shift each
      // incoming edge's packet phase (whole cycle, same speed) so its first arrival lands on that instant
      if(amb){
        var gi = 0;
        edges.forEach(function(E){ if(!E.back && E.pk){ E.off = modf(gi*0.618034, 1)*E.cyc; gi += 1; } });
        var NR = ripples.length;
        ripples.forEach(function(R, i){
          var E = R.inE, target = AP*i/NR;
          E.off = modf((E.arrive - (target + 0.15))/(E.cyc/flowV), 1)*E.cyc;
          R.t0 = target;
        });
        // icon action windows: evenly spread over the period so few are active at once
        // greedy: longest windows first, each at the phase that keeps the busiest instant lowest
        var NS = 60, cover = [], order = iconAnims.slice().sort(function(a, b){ return (ICON_WIN[b.kind] || 0.35) - (ICON_WIN[a.kind] || 0.35); });
        for(var si = 0; si < NS; si++) cover.push(0);
        order.forEach(function(A){
          var win = ICON_WIN[A.kind] || 0.35, best = 0, bestV = 1e9;
          for(var c = 0; c < NS; c++){
            var peak = 0, sum = 0;
            for(var j = 0; j < NS; j++){ var on = modf(j/NS + c/NS, 1) < win ? 1 : 0; peak = Math.max(peak, cover[j] + on); sum += (cover[j] + on)*on; }
            var v = peak*1000 + sum;
            if(v < bestV){ bestV = v; best = c; }
          }
          A.ph = best/NS;
          for(var j2 = 0; j2 < NS; j2++) if(modf(j2/NS + best/NS, 1) < win) cover[j2] += 1;
        });
      }
      labelNodes.forEach(function(l){ htmlLayer.appendChild(l); });
      totalLines += totalEn; hiddenLines += hiddenEn;
      if(totalLines && hiddenLines/totalLines > 0.2) problems.push('R14: '+hiddenLines+' of '+totalLines+' description lines / English glosses hidden for lack of space (> 20%)');

      // ---- walks -> one flat list of hops (the single truth: hop = period / total hops) ----
      var hops = [], roundLen = [];
      (walkOn ? walkSpec : []).forEach(function(a, ri){
        if(a.length < 2){ problems.push('walk '+(ri+1)+' needs at least 2 nodes'); return; }
        if(a[0] !== a[a.length-1]) problems.push('walk '+(ri+1)+' must end on the node it starts from ("'+a[0]+'" vs "'+a[a.length-1]+'")');
        a.forEach(function(id){ if(!byId[id]) problems.push('walk '+(ri+1)+' refers to unknown node "'+id+'"'); });
        roundLen[ri] = a.length;
        for(var k = 0; k + 1 < a.length; k++){
          var fa = a[k], tb = a[k+1];
          var cand = edges.filter(function(E){ return E.cfg.from === fa && E.cfg.to === tb; });
          if(!cand[0]) problems.push('walk hop '+fa+' → '+tb+' has no edge');
          hops.push({from:fa, to:tb, E:cand[0] || null, round:ri, k:k, entry:false});
        }
      });
      var H = hops.length;
      if(!H && walkOn) problems.push('walks is empty');
      var T = H ? period/H : period;
      if(H && T < 1.25) problems.push('hops last '+T.toFixed(2)+'s; the focus crossfade needs ~0.3s, lengthen period or shorten the walks');

      // entry: while the last hop of a round returns to its first node, the next input arrives from `entry`
      var entryId = e.entry && byId[e.entry] ? e.entry : null;
      if(e.entry && !entryId) problems.push('entry refers to unknown node "'+e.entry+'"');
      var entryE = null;
      if(entryId){
        walkSpec.forEach(function(a){
          var cand = edges.filter(function(E){ return E.cfg.from === entryId && E.cfg.to === a[0]; })[0];
          if(!cand) problems.push('entry '+entryId+' → '+a[0]+' has no edge');
          entryE = entryE || cand || null;
        });
        hops.forEach(function(hp){ hp.entry = hp.k === roundLen[hp.round] - 2 && hp.to === walkSpec[hp.round][0]; });
      }

      // token: head (+ glow on dark) and a 3-step fading trail; the entry token is a smaller twin
      var tokR = Math.max(5, u*0.7)*(weak ? 0.8 : 1);
      function makeToken(r0, nTrail){
        var tr = [], halo = null;
        for(var k = 0; k < nTrail; k++) tr.push(gTok.appendChild(svg('circle', {cx:-20, cy:-20, r:r0*(0.82 - 0.18*k), fill:okCol, opacity:[0.55, 0.36, 0.2][k]})));
        var hd = svg('circle', {cx:-20, cy:-20, r:r0, fill:okCol, stroke:ctx.cc('bg'), 'stroke-width':1.5});
        if(dark){
          halo = gTok.insertBefore(svg('circle', {cx:-20, cy:-20, r:r0*2.1, fill:okCol, opacity:0}), gTok.firstChild);
          hd.setAttribute('stroke', okCol); hd.setAttribute('stroke-opacity', 0.35); hd.setAttribute('stroke-width', r0*0.9);
        }
        return {head:gTok.appendChild(hd), trail:tr, halo:halo};
      }
      var tok = makeToken(tokR, 3);
      var tokIn = entryE ? makeToken(tokR*0.78, 2) : null;

      return {ripples:ripples, isDark:dark, amb:amb, walkOn:walkOn, AP:AP, ambientOnly:ambientOnly, iconAnims:iconAnims, flowS:flowS, flowV:flowV, dotCount:dotCount, period:period, H:H, T:T, hops:hops, edges:edges, nodeLit:nodeLit, byId:byId, tok:tok, tokIn:tokIn,
              entryE:entryE, entryId:entryId, roundLen:roundLen, status:statusRefs, problems:problems,
              flowPeriod:flowPeriod, dashPeriod:dashPeriod, dashLen:dashLen};
    },

    seek: function(t, ctx, st){
      function ambientSeek(t, s){
        var AP = s.AP, q0 = modf(t/AP, 1);
        function smoothS(x){ x = x < 0 ? 0 : (x > 1 ? 1 : x); return x*x*(3 - 2*x); }
        function fx(v){ return v.toFixed(2); }
        // packets: position on the edge = (v*t + m*cycle) mod flowS, kept while inside the edge
        function dot(o, a, v, hv){ o.setAttribute('cx', fx(a.x)); o.setAttribute('cy', fx(a.y)); o.setAttribute('opacity', fx(v)); }
        function hide(o){ o.head.setAttribute('opacity', 0); o.tr.forEach(function(c){ c.setAttribute('opacity', 0); }); if(o.halo) o.halo.setAttribute('opacity', 0); }
        function show(o, E, pos, tail, edgeK, hv){
          var a = along(E, pos/E.len);
          dot(o.head, a, edgeK*hv);
          if(o.halo){ dot(o.halo, a, edgeK*0.14); }
          var n = o.tr.length;
          o.tr.forEach(function(c, i){
            var tp = pos - tail*(i + 1)/n;
            if(tp < 0){ c.setAttribute('opacity', 0); return; }
            dot(c, along(E, tp/E.len), edgeK*hv*(0.62 - 0.11*i));
          });
        }
        var hv = s.isDark ? 0.96 : 0.9;
        s.edges.forEach(function(E){
          if(E.back){
            E.base.setAttribute('stroke-dashoffset', fx(-modf(q0*3, 1)*s.dashLen));
            if(E.bk){
              var pos = q0*E.len;
              show(E.bk, E, pos, E.bkTail*2, Math.min(1, pos/8, (E.len - pos)/8), 0.7);
            }
            return;
          }
          E.pk.forEach(function(o){
            var pos = modf(s.flowV*t + (E.off || 0), E.cyc) + o.m*E.cyc;
            if(pos >= E.len){ hide(o); return; }
            // fade over the last/first few px so packets do not pop at the card edges
            show(o, E, pos, E.tail, Math.min(1, pos/7, (E.len - pos)/7), hv);
          });
        });
        // delivery: ripple on the node at the first arrival of its first incoming packet, a smooth >= 0.9 s bump
        s.ripples.forEach(function(R){
          var x = modf(t - R.t0, AP)/0.9, b = x < 1 ? bump(x) : 0;
          if(R.poly){
            var e = 6*Math.min(x, 1), a2 = R.a + e*R.L/R.b, b2 = R.b + e*R.L/R.a;
            R.poly.setAttribute('points', (R.cx)+','+fx(R.cy - b2)+' '+fx(R.cx + a2)+','+(R.cy)+' '+(R.cx)+','+fx(R.cy + b2)+' '+fx(R.cx - a2)+','+(R.cy));
            R.poly.setAttribute('stroke-opacity', fx(0.9*b));
          } else {
            var sp = bw2(R, x);
            R.ring.style.cssText = R.ringCss + 'opacity:' + fx(0.9*b) + ';left:' + sp + 'px;top:' + sp + 'px;right:' + sp + 'px;bottom:' + sp + 'px;';
            R.card.style.transform = 'translateY(' + fx(-2*b) + 'px)';
            R.card.style.boxShadow = s.isDark ? '0 0 ' + fx(18*b) + 'px ' + R.glow.replace('A', fx(0.55*b)) : 'none';
            R.card.style.filter = s.isDark ? '' : 'drop-shadow(0 ' + fx(3*b) + 'px ' + fx(5*b) + 'px ' + R.glow.replace('A', fx(0.28*b)) + ')';
          }
        });
        function bw2(R, x){ return (-(R.bw + 6*Math.min(x, 1))).toFixed(2); }
        // icons: one action window per ambient period (phase staggered by node order), still or breathing otherwise
        s.iconAnims.forEach(function(A){
          var k = A.kind, q = modf(q0 + A.ph, 1), win = ICON_WIN[k] || 0.35, w = q/win, on = w < 1;
          var px = A.k, tf = '', breath = on ? 1 + 0.08*bump(w) : 1;
          if(k === 'message-square-more'){
            A.parts.forEach(function(pg, i){
              var x = (w*win*AP - i*0.12*AP)/(0.4*AP), y = (on && x > 0 && x < 1) ? -5*px*leap(x) : 0;
              pg.setAttribute('transform', 'translate(0 ' + fx(y) + ')');
            });
          } else if(k === 'eye'){
            var sy = 1, dx = 0;
            if(on){
              var sec = w*win*AP;
              if(sec < 0.25) sy = 1 - 0.9*bump(sec/0.25);
              else {
                var u2 = (sec - 0.25)/(win*AP - 0.25);
                dx = u2 < 1/3 ? -2.5*easeInOutCubic(u2*3) : (u2 < 2/3 ? -2.5 + 5*easeInOutCubic(u2*3 - 1) : 2.5*(1 - easeInOutCubic(u2*3 - 2)));
              }
            }
            A.parts[0].setAttribute('transform', 'translate(' + fx(dx*px) + ' 0)');
            tf = 'translate(0 ' + fx(12*(1 - sy)) + ') scale(1 ' + sy.toFixed(3) + ')';
          } else if(k === 'ticket'){
            tf = 'rotate(' + fx(on ? 12*(w < 0.2 ? easeInOutCubic(w/0.2) : 1 - easeOutElastic((w - 0.2)/0.8)) : 0) + ' 12 12)';
          } else if(k === 'bug'){
            var bw = on ? Math.sin(2*Math.PI*w)*bump(w < 0.5 ? w*2 : 1) : 0, bh = on ? 8*Math.sin(4*Math.PI*w) : 0;
            tf = 'translate(' + fx(3*px*bw) + ' 0) rotate(' + fx(bh) + ' 12 16)';
          } else if(k === 'git-pull-request' || k === 'git-merge'){
            tf = 'translate(0 ' + fx(on ? -7*px*leap(w) : 0) + ')';
          } else if(k === 'shield-check'){
            var sc = on ? 1 + 0.18*leap(w) : 1;
            var dr = on ? (w < 0.15 ? easeInOutCubic(w/0.15) : 1 - easeInOutCubic((w - 0.15)/0.6)) : 0;
            A.parts[0].setAttribute('stroke-dashoffset', fx(Math.min(1, dr)*1.05));
            breath = 1; tf = 'translate(12 12) scale(' + sc.toFixed(3) + ') translate(-12 -12)';
          } else if(k === 'timer'){
            A.parts[0].setAttribute('transform', 'rotate(' + fx(on ? 360*easeInOutCubic(w) : 0) + ' 12 14)');
            A.parts[1].setAttribute('transform', 'translate(0 ' + fx(on && w < 0.2 ? 1.5*px*bump(w/0.2) : 0) + ')');
          } else if(k === 'refresh-cw'){
            tf = 'rotate(' + fx(on ? 360*easeInOutCubic(w) : 0) + ' 12 12)';
          }
          if(breath !== 1) tf = 'translate(12 12) scale(' + breath.toFixed(3) + ') translate(-12 -12) ' + tf;
          A.g.setAttribute('transform', tf);
        });
        // status card in pure ambient: a lit dot chases along the row, one step per AP/N
        if(s.ambientOnly && s.status){
          var N = s.status.dots.length, hi = Math.floor(q0*N) % N;
          s.status.dots.forEach(function(d, k){
            d.setAttribute('fill', k === hi ? s.status.accOn : s.status.off);
            d.setAttribute('opacity', k === hi ? 1 : (k === (hi - 1 + N) % N ? 0.6 : 0.9));
          });
        }
      }

      var s = st || (ctx && ctx.state);
      if(!s) return;
      if(s.amb) ambientSeek(t, s);
      if(!s.H) return;
      var P = s.period, T = s.T, H = s.H;
      var ease = LP.ease.inOut;
      function smooth(x){ x = x < 0 ? 0 : (x > 1 ? 1 : x); return x*x*(3 - 2*x); }

      // crossfade window of the focus, centred on FOCUS_AT, at least ~0.3 s wide
      var fw = clamp(0.3/T*1.05, 0.24, 0.8), f0 = clamp(FOCUS_AT - fw/2, 0, 1 - fw);

      // position of the token at time tt: dwell inside the node (hidden behind the card), then along the edge
      function phase(tt){ var q = modf(tt, P)/T, i = Math.floor(q); return {i:i % H, p:q - i}; }
      function posAt(tt){
        var ph = phase(tt), p = ph.p, hop = s.hops[ph.i], prev = s.hops[(ph.i - 1 + H) % H];
        if(!hop.E) return null;
        var E = hop.E;
        if(p < 0.4){
          var from = along(prev.E || E, prev.E ? 1 : 0), to = along(E, 0), q = ease(p/0.4);
          return {x:from.x + (to.x-from.x)*q, y:from.y + (to.y-from.y)*q, vis:false};
        }
        var a = along(E, ease((p - 0.4)/0.6));
        return {x:a.x, y:a.y, vis:true};
      }
      // the entry token rides trigger → first node during the closing hop of a round
      function entryAt(tt){
        var ph = phase(tt);
        if(!s.hops[ph.i].entry || ph.p < 0.4) return null;
        var p = ph.p, a = along(s.entryE, ease((p - 0.4)/0.6));
        return {x:a.x, y:a.y, vis:true};
      }
      function edgeEnv(p){ return p < 0.40 ? 0 : (p < 0.46 ? smooth((p - 0.40)/0.06) : (p < 0.88 ? 1 : 1 - smooth((p - 0.88)/0.12))); }

      // exactly one focus: the source until the token is mid-edge, then the target, crossfaded
      var now = phase(t), p = now.p, hop = s.hops[now.i];
      var m = smooth((p - f0)/fw);
      var nodeI = {}, edgeI = [];
      s.edges.forEach(function(E, k){ edgeI[k] = 0; });
      nodeI[hop.from] = 1 - m;
      nodeI[hop.to] = (nodeI[hop.to] || 0) + m;
      if(hop.E) edgeI[s.edges.indexOf(hop.E)] = edgeEnv(p);
      if(hop.entry && s.entryE){
        edgeI[s.edges.indexOf(s.entryE)] = Math.max(edgeI[s.edges.indexOf(s.entryE)], edgeEnv(p));
        // the entry card glows weakly while the next input is on its way
        var env = p < 0.9 ? smooth((p - 0.05)/0.2) : 1 - smooth((p - 0.9)/0.1);
        nodeI[s.entryId] = Math.max(nodeI[s.entryId] || 0, 0.5*env);
      }
      Object.keys(s.nodeLit).forEach(function(id){ s.nodeLit[id].style.opacity = (nodeI[id] || 0).toFixed(3); });
      function put(c, pos){ c.setAttribute('cx', pos.x.toFixed(1)); c.setAttribute('cy', pos.y.toFixed(1)); }
      var dashOff = s.amb ? -modf(t/s.AP*3, 1)*s.dashLen : -((t/s.dashPeriod) % 1) * s.dashLen;
      s.edges.forEach(function(E, k){
        E.lit.setAttribute('opacity', edgeI[k].toFixed(3));
        if(E.dashed) E.lit.setAttribute('stroke-dashoffset', dashOff.toFixed(2));
        // ambient flow: dots drift along forward edges
        E.dots.forEach(function(D){ put(D.el, along(E, ((t/s.flowPeriod) + D.off) % 1)); });
      });

      // tokens + trails
      function place(tk, fn, step){
        var pos = fn(t), on = pos && pos.vis;
        tk.head.setAttribute('opacity', on ? 1 : 0);
        if(tk.halo) tk.halo.setAttribute('opacity', on ? 0.28 : 0);
        if(on){ put(tk.head, pos); if(tk.halo) put(tk.halo, pos); }
        tk.trail.forEach(function(c, k){
          var pp = on && fn(t - step*(k+1));
          if(pp && pp.vis){ put(c, pp); c.style.display = ''; } else c.style.display = 'none';
        });
      }
      place(s.tok, posAt, 0.09*T);
      if(s.tokIn) place(s.tokIn, entryAt, 0.09*T);

      // status card: round (1..R), current step and visited-node dots; the step flips with the focus
      if(s.status && !s.ambientOnly){
        var onTarget = m >= 0.5;
        var nodeId = onTarget ? hop.to : hop.from;
        var kk2 = hop.k + (onTarget ? 1 : 0);
        s.status.round.textContent = s.status.rTpl.replace('{n}', hop.round + 1);
        s.status.step.textContent = s.status.sTpl.replace('{label}', s.byId[nodeId].label);
        var visits = s.roundLen[hop.round];
        s.status.dots.forEach(function(d, k){
          d.setAttribute('fill', k <= kk2 ? s.status.accOn : s.status.off);
          d.setAttribute('opacity', k >= visits ? 0 : (k === kk2 ? 1 : (k < kk2 ? 0.45 : 0.9)));
        });
      }
    },

    events: function(lo, hi, ctx){
      var s = ctx && ctx.state;
      if(!s || !s.H || s.ambientOnly) return [];
      var out = [];
      var k0 = Math.floor(lo/s.T), k1 = Math.ceil(hi/s.T);
      var logc = (ctx.e.log && ctx.e.log.c) || 'acc1';
      var who = (ctx.e.log && ctx.e.log.who) || 'loop';
      for(var k = k0; k <= k1; k++){
        var hop = s.hops[((k % s.H) + s.H) % s.H];
        var from = s.byId[hop.from], to = s.byId[hop.to];
        out.push({t:k*s.T, who:who, c:logc, m:from.label + ' → ' + to.label, g:hop.E && hop.E.back ? 'loop' : ''});
      }
      return out;
    },

    check: function(ctx){
      var pr = [];
      var s = ctx.state;
      if(s && s.problems) pr = pr.concat(s.problems);
      var e = ctx.e;
      var mo = e.motion || 'ambient', apc = Number(e.ambientPeriod) || 3.0;
      if(mo.indexOf('walk') >= 0 && mo.indexOf('ambient') >= 0){
        var per = Number(e.period) || 26, qq = per/apc;
        if(Math.abs(qq - Math.round(qq)) > 1e-6) pr.push('period '+per+' is not a whole multiple of ambientPeriod '+apc);
      }
      // grid cells, spans included
      var seen = {};
      (e.nodes||[]).forEach(function(n){
        for(var c = 0; c < (n.span||1); c++){
          var k = (n.row||0) + ',' + ((n.col||0) + c);
          if(seen[k]) pr.push('nodes "'+seen[k]+'" and "'+n.id+'" share grid cell '+k);
          seen[k] = n.id;
        }
      });
      return pr;
    }
  });
})();
