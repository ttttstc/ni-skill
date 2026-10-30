/* live-panel view: sketchboard — a hand-drawn "A vs B" explainer board (DailyDose-of-DS style):
   coloured-highlight title, a left panel (the old way: a vertical chain of cards, optionally a token stream),
   a right panel (the new way: numbered sections, each one horizontal chain of cards / chips / typed text,
   optionally closed into a loop), and a bottom comparison table. Designed in a 1280x1140 base space and
   scaled uniformly into the rect, so every preset keeps the proportions. Colours come from theme colour
   names `<hue>bg <hue>bd <hue>pill <hue>pbd <hue>card <hue>cbd <hue>tx <hue>hl` (hue g|b|y|r, see
   examples/hybrid-agent/config.json, the "sketch" look) with accent fallbacks, so it also runs on the
   built-in presets. Shared series keys live at the top level of the config: `series:{brand, name}`;
   per page: `page:"1/5"`. Pure function of t; nothing is created in seek. */
(function(){
var BW=1280, BH=1140;
var ICON={
 doc:'<rect x="7" y="3" width="22" height="30" rx="3" fill="#fff" stroke="currentColor" stroke-width="2.2"/><path d="M12 11h12M12 17h12M12 23h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
 chip:'<g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 4v4M18 4v4M24 4v4M12 28v4M18 28v4M24 28v4M4 12h4M4 18h4M4 24h4M28 12h4M28 18h4M28 24h4"/></g><rect x="8" y="8" width="20" height="20" rx="3" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2.2"/><rect x="13.5" y="13.5" width="9" height="9" rx="1.5" fill="#fff" stroke="currentColor" stroke-width="2"/>',
 wrench:'<path d="M24 4a8 8 0 0 0-7.4 11L5 26.6a3 3 0 0 0 4.3 4.3L21 19.4A8 8 0 0 0 32 12l-5 2-4-4 2-5z" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/>',
 link:'<rect x="3" y="11" width="16" height="14" rx="7" fill="none" stroke="currentColor" stroke-width="2.4"/><rect x="17" y="11" width="16" height="14" rx="7" fill="var(--sk-ic)" fill-opacity=".55" stroke="currentColor" stroke-width="2.4"/>',
 search:'<circle cx="15" cy="15" r="9" fill="#fff" stroke="currentColor" stroke-width="2.4"/><path d="M22 22l9 9" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>',
 code:'<rect x="3" y="5" width="30" height="26" rx="4" fill="#fff" stroke="currentColor" stroke-width="2.2"/><path d="M13 13l-5 5 5 5M23 13l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
 eye:'<path d="M3 18s5.5-10 15-10 15 10 15 10-5.5 10-15 10S3 18 3 18z" fill="#fff" stroke="currentColor" stroke-width="2.2"/><circle cx="18" cy="18" r="5" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2"/>',
 timer:'<circle cx="18" cy="20" r="12" fill="#fff" stroke="currentColor" stroke-width="2.2"/><path d="M18 20l5-5M14 4h8M18 4v4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
 gauge:'<path d="M5 26a13 13 0 1 1 26 0" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><path d="M18 26l7-9" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><circle cx="18" cy="26" r="3" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2"/>',
 chart:'<rect x="5" y="19" width="6" height="12" rx="1" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2"/><rect x="15" y="12" width="6" height="19" rx="1" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2"/><rect x="25" y="5" width="6" height="26" rx="1" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2"/>',
 bolt:'<path d="M20 3L7 20h9l-2 13 13-17h-9z" fill="var(--sk-ic)" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/>',
 brain:'<path d="M14 6a5 5 0 0 0-5 5 5 5 0 0 0-3 9 5 5 0 0 0 5 8 4 4 0 0 0 7 1V7a4 4 0 0 0-4-1zM22 6a5 5 0 0 1 5 5 5 5 0 0 1 3 9 5 5 0 0 1-5 8 4 4 0 0 1-7 1" fill="var(--sk-ic)" fill-opacity=".5" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
 trend:'<rect x="3" y="3" width="30" height="30" rx="6" fill="#fff" stroke="currentColor" stroke-width="2.2"/><path d="M8 24l7-7 5 4 8-9" fill="none" stroke="var(--sk-ic2)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
};
function series(){ try{ var el=document.getElementById('live-config'); var c=JSON.parse(el.textContent); return c.series||{}; }catch(_){ return {}; } }

LP.registerView('sketchboard',{
 build:function(ctx){
  var e=ctx.e, R=ctx.rect, S={pk:[],tok:[],typed:[],cnt:null,period:e.period||3};
  var s=Math.min(R.w/BW,R.h/BH), ox=(R.w-BW*s)/2, oy=(R.h-BH*s)/2;
  // colour name for a hue role with a fallback to the generic accents
  var HF={g:1,b:0,y:4,r:5};
  function C(h,role){ var n=h+role; if(ctx.col(n)) return ctx.cc(n);
    var i=HF[h]||0; return ctx.cc(role==='bg'||role==='card'||role==='hl'||role==='pill'?ctx.accf(i):role==='tx'?'fg':ctx.acc(i)); }
  var FONT='var(--font)';
  var W=ctx.el('div','', 'position:absolute;left:'+ox+'px;top:'+oy+'px;width:'+BW+'px;height:'+BH+'px;transform-origin:0 0;transform:scale('+s+');white-space:pre;font-family:'+FONT+';color:'+ctx.cc('fg'));
  ctx.root.appendChild(W);
  var svg=ctx.svg('svg',{width:BW,height:BH}); svg.style.cssText='position:absolute;left:0;top:0;overflow:visible;pointer-events:none';
  function div(parent,css,cls){ var d=ctx.el('div',cls||'','position:absolute;'+css); parent.appendChild(d); return d; }
  function txt(parent,str,css,px,maxW,bold){ var f=ctx.fit(str,px,maxW,FONT,11,bold); var d=div(parent,'font-size:'+f.size+'px;line-height:'+Math.round(f.size*1.3)+'px;'+(bold?'font-weight:700;-webkit-text-stroke:.25px currentColor;':'')+css); d.textContent=f.text; ctx.mark(d,'text'); return d; }
  function icon(parent,name,x,y,sz,hue){ var d=div(parent,'left:'+x+'px;top:'+y+'px;width:'+sz+'px;height:'+sz+'px;color:'+ctx.cc('fg')+';--sk-ic:'+C(hue,'cbd')+';--sk-ic2:'+C(hue,'tx'));
    d.innerHTML='<svg width="'+sz+'" height="'+sz+'" viewBox="0 0 36 36">'+(ICON[name]||ICON.chip)+'</svg>'; return d; }
  function pill(parent,str,x,y,w,h,hue,px){ var d=div(parent,'left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+h+'px;border-radius:'+(h/2)+'px;border:2px solid '+C(hue,'pbd')+';background:'+C(hue,'pill'));
    ctx.mark(d,'box'); var f=ctx.fit(str,px,w-30,FONT,11,true); var t=txt(d,f.text,'left:0;width:'+(w-4)+'px;text-align:center;top:'+((h-4-Math.round(f.size*1.3))/2)+'px',f.size,w-30,true); return d; }
  // ---- arrows + packets (SVG overlay, below the cards) ----
  function arrow(pts,col,opt){ opt=opt||{}; var d='M'+pts.map(function(p){return p[0]+' '+p[1]}).join(' L');
    var pa=ctx.svg('path',{d:d,fill:'none',stroke:col,'stroke-width':2.2,'stroke-linecap':'round','stroke-linejoin':'round'}); if(opt.dash) pa.setAttribute('stroke-dasharray','6 6');
    ctx.mark(pa,'edge'); svg.appendChild(pa);
    var a=pts[pts.length-2], b=pts[pts.length-1], dx=b[0]-a[0], dy=b[1]-a[1], L=Math.hypot(dx,dy)||1; dx/=L; dy/=L; var z=9;
    svg.appendChild(ctx.svg('polygon',{points:b[0]+','+b[1]+' '+(b[0]-dx*z-dy*z*.55)+','+(b[1]-dy*z+dx*z*.55)+' '+(b[0]-dx*z+dy*z*.55)+','+(b[1]-dy*z-dx*z*.55),fill:col}));
    if(opt.dot!==false) svg.appendChild(ctx.svg('circle',{cx:pts[0][0],cy:pts[0][1],r:4.5,fill:ctx.cc('gdot')||ctx.cc('ok')}));
    return pts; }
  function pkPath(pts,col,n,laps,r,lead,hide){ var seg=[],len=0; for(var i=1;i<pts.length;i++){var l=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]); seg.push(l); len+=l;}
    for(var k=0;k<n;k++){ var c=ctx.svg('circle',{r:r||5,fill:col}); var tr=ctx.svg('circle',{r:(r||5)*0.55,fill:col,'fill-opacity':.45}); svg.appendChild(tr); svg.appendChild(c);
      S.pk.push({pts:pts,seg:seg,len:len,el:c,tr:tr,off:k/n+(lead||0),laps:laps||1,hide:hide||[]}); } }
  // ---- title ----
  var TT=e.title||[], tsz=e.titleSize||54;
  var tot=TT.reduce(function(a,r){return a+ctx.measure(r.t,tsz,FONT,true)+(r.hue?28:0)+12},0); while(tot>BW-110&&tsz>30){ tsz-=2; tot=TT.reduce(function(a,r){return a+ctx.measure(r.t,tsz,FONT,true)+(r.hue?28:0)+12},0); }
  div(W,'left:34px;top:30px;width:12px;height:62px;border-radius:7px;background:'+(ctx.cc('accent')||ctx.cc('acc4')));
  var tx=62; TT.forEach(function(r){ var w=ctx.measure(r.t,tsz,FONT,true)+(r.hue?28:0);
    if(r.hue) div(W,'left:'+tx+'px;top:'+(61-tsz*0.62)+'px;width:'+w+'px;height:'+(tsz*1.18)+'px;border-radius:12px 18px 10px 16px;transform:rotate(-.6deg);background:'+C(r.hue,'hl'));
    var d=div(W,'left:'+(tx+(r.hue?14:0))+'px;top:'+(61-tsz*0.66)+'px;font-size:'+tsz+'px;line-height:'+Math.round(tsz*1.3)+'px;font-weight:700;-webkit-text-stroke:.8px currentColor;color:'+(r.hue?C(r.hue,'tx'):ctx.cc('fg')));
    d.textContent=r.t; ctx.mark(d,'text'); tx+=w+12; });
  if(e.page){ var pg=txt(W,e.page,'right:30px;top:44px;color:'+ctx.cc('muted'),18,120,true); pg.style.left='auto'; }
  // ---- panels ----
  var PT=118, PH=e.panelH||722, GAP=14, LW=Math.round((BW-48-GAP)*(e.split||0.38)), RX=24+LW+GAP, RW=BW-24-RX;
  function panel(x,w,P){ var hue=P.hue||'g', d=div(W,'left:'+x+'px;top:'+PT+'px;width:'+w+'px;height:'+PH+'px;border-radius:22px;border:2px solid '+C(hue,'bd')+';background:'+C(hue,'bg')); ctx.mark(d,'frame');
    pill(d,P.title,Math.round(w*0.08),16,Math.round(w*0.84)-4,50,hue,25);
    if(P.sub) txt(d,P.sub,'left:0;width:'+(w-4)+'px;text-align:center;top:80px',17,w-40);
    if(P.foot) txt(d,P.foot,'left:0;width:'+(w-4)+'px;text-align:center;top:'+(PH-40)+'px',16,w-30);
    return d; }
  // a card: icon + label + sub
  function card(parent,it,x,y,w,h,hue){ var st=it.style||'card', fill=st==='white'?(ctx.cc('wcard')||ctx.cc('panel')):C(it.hue||hue,'card'), bd=C(it.hue||hue,'cbd');
    var d=div(parent,'left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+h+'px;border-radius:12px;border:2px solid '+bd+';background:'+fill+(it.dashed?';border-style:dashed':'')); ctx.mark(d,'box');
    var isz=it.icon?Math.min(34,h-24):0, pad=it.icon?12:8, tw=w-pad*2-4-(isz?isz+10:0), lx=pad+(isz?isz+10:0);
    if(isz) icon(d,it.icon,pad,(h-4-isz)/2,isz,it.hue||hue);
    var lsz=it.size||17, lines=[[it.label,lsz,true]]; if(it.sub) lines.push([it.sub,13.5,false]);
    var hh=lines.reduce(function(a,l){return a+Math.round(l[1]*1.3)},0), yy=(h-4-hh)/2;
    var al=it.align||(it.icon?'left':'center');
    lines.forEach(function(l,i){ var t=txt(d,l[0],'left:'+(isz?lx:pad)+'px;width:'+tw+'px;text-align:'+al+';top:'+yy+'px;'+(i?'color:'+ctx.cc('muted'):''),l[1],tw,l[2]); if(it.mono&&!i) t.style.fontFamily='var(--font-mono,monospace)'; yy+=Math.round(l[1]*1.3); });
    return d; }
  // left: vertical chain
  var L=e.left||{}, Lp=panel(24,LW,L), lhue=L.hue||'g';
  var blocks=L.blocks||[], bh=blocks.map(function(b){return b.type==='stream'?(b.h||200):(b.h||70)});
  var top=122, bot=PH-56, free=bot-top-bh.reduce(function(a,b){return a+b},0), gap=free/Math.max(1,blocks.length-1);
  var y=top, lastBottom=null, lineCol=ctx.cc('fg');
  blocks.forEach(function(b,i){ var h=bh[i];
    if(b.type==='stream'){ var bw=LW-56, bx=26;
      var fr=div(Lp,'left:'+bx+'px;top:'+y+'px;width:'+bw+'px;height:'+h+'px;border-radius:14px;border:2px dashed '+C(lhue,'cbd')); ctx.mark(fr,'frame');
      if(b.title) txt(fr,b.title,'left:16px;top:10px;width:'+(bw-160)+'px',15.5,bw-160,true);
      var cnt=txt(fr,'000 tokens','right:16px;top:11px;text-align:right;width:130px;color:'+C(lhue,'tx'),15,130,true); cnt.style.left='auto'; cnt.style.fontVariantNumeric='tabular-nums';
      var tk=b.tokens||[], cx=16, cy=44, tks=b.tokenSize||14.5, chH=Math.round(tks*1.95), rowGap=8;
      tk.forEach(function(t,k){ var w=Math.ceil(ctx.measure(t,tks,FONT))+Math.round(tks*1.25); if(cx+w>bw-20){ cx=16; cy+=chH+rowGap; }
        var c=div(fr,'left:'+cx+'px;top:'+cy+'px;width:'+w+'px;height:'+chH+'px;border-radius:8px;border:1.6px solid '+C(lhue,'cbd')+';background:'+C(lhue,'card')); ctx.mark(c,'box');
        var tt=txt(c,t,'left:0;width:'+(w-3)+'px;text-align:center;top:'+((chH-4-Math.round(tks*1.3))/2)+'px',tks,w-6); S.tok.push(c); cx+=w+6; });
      S.cnt={el:cnt,n:tk.length,unit:b.unit||' tokens',per:b.perToken||1};
      if(b.cap){ icon(fr,b.capIcon||'timer',16,h-38,26,lhue); txt(fr,b.cap,'left:50px;top:'+(h-36)+'px;width:'+(bw-70)+'px',15,bw-70); }
      var rect={x:bx,y:y,w:bw,h:h};
    } else { var cw=b.w||Math.min(LW-150,270), cxp=(LW-4-cw)/2; card(Lp,b,cxp,y,cw,h,lhue); var rect={x:cxp,y:y,w:cw,h:h}; }
    if(lastBottom!=null){ var X=24+2+LW/2-2, p=[[X,PT+lastBottom+4],[X,PT+y-2]]; arrow(p,lineCol); pkPath(p,C(lhue,'tx'),1,2,4.5,i*0.17); }
    lastBottom=y+h; y+=h+gap; });
  // right: numbered sections
  var Rt=e.right||{}, Rp=panel(RX,RW,Rt), rhue=Rt.hue||'b';
  var secs=Rt.sections||[], sh=secs.map(function(sc){return sc.h||170}), sTop=118, sBot=PH-52, sGap=(sBot-sTop-sh.reduce(function(a,b){return a+b},0))/Math.max(1,secs.length-1);
  var sy=sTop;
  secs.forEach(function(sc,si){ var sw=RW-40, sx=18, h=sh[si];
    var fr=div(Rp,'left:'+sx+'px;top:'+sy+'px;width:'+sw+'px;height:'+h+'px;border-radius:16px;border:2px solid '+C(rhue,'cbd')+';background:'+(ctx.cc(rhue+'in')||ctx.cc('panel'))); ctx.mark(fr,'frame');
    var nb=div(fr,'left:14px;top:11px;width:34px;height:34px;border-radius:50%;border:2px solid '+C(rhue,'pbd')+';background:'+C(rhue,'pill')); ctx.mark(nb,'box');
    txt(nb,String(sc.n||si+1),'left:0;width:30px;text-align:center;top:3px',18,26,true);
    var tW=ctx.measure(sc.title,21,FONT,true)+4; var ttl=txt(fr,sc.title,'left:58px;top:14px',21,sw-80,true);
    if(sc.note){ var nx=58+Math.min(tW,sw-80)+14; txt(fr,sc.note,'left:'+nx+'px;top:19px;color:'+ctx.cc('muted'),14.5,sw-nx-16); }
    // horizontal chain
    var items=sc.items||[], aw=44, cardH=sc.cardH||62, iy=56+(sc.loop?0:((h-56-cardH-(sc.cap?22:0))/2-6));
    var fixed=items.reduce(function(a,it){return a+(it.w||0)},0), nflex=items.filter(function(it){return !it.w}).length;
    var inner=sw-32-aw*(items.length-1), flexW=nflex?(inner-fixed)/nflex:0, ix=16, boxes=[];
    items.forEach(function(it,k){ var w=it.w||flexW, hh=it.h||cardH, yy=iy+(cardH-hh)/2;
      var d=card(fr,it,ix,yy,w,hh,rhue); boxes.push({x:ix,y:yy,w:w,h:hh});
      if(it.typed){ var tt=d.querySelector('[data-t="text"]'); S.typed.push({el:tt,full:tt.textContent,lead:it.typedLead||0.12}); }
      if(it.cap) txt(fr,it.cap,'left:'+ix+'px;width:'+w+'px;text-align:center;top:'+(yy+hh+5)+'px;color:'+ctx.cc('muted'),13,w);
      ix+=w+aw; });
    var gx=RX+2+sx+2, gy=PT+2+sy+2, chainPts=[];
    for(var k=1;k<boxes.length;k++){ var a=boxes[k-1], b2=boxes[k], ay=gy+a.y+a.h/2, p=[[gx+a.x+a.w+3,ay],[gx+b2.x-4,ay]]; arrow(p,lineCol); chainPts.push(p); }
    if(sc.loop){ var A=boxes[0], Z=boxes[boxes.length-1], ly=gy+iy+cardH+20, p=[[gx+Z.x+Z.w/2,gy+Z.y+Z.h+3],[gx+Z.x+Z.w/2,ly],[gx+A.x+A.w/2,ly],[gx+A.x+A.w/2,gy+A.y+A.h+4]];
      arrow(p,C(rhue,'tx'),{dash:true,dot:false});
      if(sc.loopLabel){ var lw=ctx.measure(sc.loopLabel,13.5,FONT)+16, lx=(A.x+Z.x+Z.w)/2-lw/2; var lb=txt(fr,sc.loopLabel,'left:'+lx+'px;top:'+(iy+cardH+27)+'px;width:'+lw+'px;text-align:center;color:'+C(rhue,'tx'),13.5,lw,true); }
      // one silent loop: a packet walking chain + return path, `laps` laps per period
      var full=[]; for(var q=0;q<chainPts.length;q++){ full.push(chainPts[q][0]); full.push(chainPts[q][1]); } p.forEach(function(pp){full.push(pp)}); full.push(chainPts[0][0]);
      pkPath(full,C(rhue,'tx'),2,sc.laps||1,5.5,0,boxes.map(function(b){return {x:gx+b.x,y:gy+b.y,w:b.w,h:b.h}}));
    } else chainPts.forEach(function(p,q){ pkPath(p,C(rhue,'tx'),1,sc.laps||2,4.5,q*0.3+si*0.11); });
    if(sc.cap) txt(fr,sc.cap,'left:0;width:'+(sw-4)+'px;text-align:center;top:'+(h-30)+'px;color:'+ctx.cc('muted'),14,sw-30);
    sy+=h+sGap; });
  // ---- table ----
  var T=e.table||{}, TY=PT+PH+16, TH=BH-TY-14, thue='y';
  var tb=div(W,'left:24px;top:'+TY+'px;width:'+(BW-48)+'px;height:'+TH+'px;border-radius:22px;border:2px solid '+C(thue,'bd')+';background:'+C(thue,'bg')); ctx.mark(tb,'frame');
  var SR=series(), brand=T.brand||SR.brand;
  if(brand){ icon(tb,'trend',20,14,28,'g'); txt(tb,brand,'left:58px;top:15px',20,170,true); }
  var cols=T.cols||[], rows=T.rows||[], qx=18, qW=180, rhW=230, c0=qx+qW+8, c1=c0+rhW, cw=(BW-48-4-16-c1)/Math.max(1,cols.length), hdH=44, rTop=12+hdH+12, rH=(TH-4-rTop-14)/Math.max(1,rows.length);
  if(T.question){ var ql=String(T.question).split('\n'), qsz=28; ql.forEach(function(l,i){ txt(tb,l,'left:'+(qx+10)+'px;top:'+(rTop+(rows.length*rH-ql.length*qsz*1.3)/2+i*qsz*1.3)+'px',qsz,qW-14,true); }); }
  cols.forEach(function(c,i){ pill(tb,c.t,c1+i*cw+12,12,cw-24,hdH,c.hue||(i?'b':'g'),20); });
  var bars=[];
  rows.forEach(function(r,ri){ var yy=rTop+ri*rH;
    var rh=div(tb,'left:'+c0+'px;top:'+yy+'px;width:'+rhW+'px;height:'+rH+'px;border:1.6px solid '+C(thue,'bd')+';background:'+C(thue,'row')); ctx.mark(rh,'box');
    if(r.icon) icon(rh,r.icon,12,(rH-30)/2-1,28,'y');
    txt(rh,r.label,'left:'+(r.icon?50:14)+'px;top:'+((rH-2-22)/2)+'px',17,rhW-(r.icon?62:26),true);
    (r.cells||[]).forEach(function(cell,ci){ cell=typeof cell==='string'?{t:cell}:cell; var hue=(cols[ci]&&cols[ci].hue)||(ci?'b':'g');
      var cd=div(tb,'left:'+(c1+ci*cw)+'px;top:'+yy+'px;width:'+cw+'px;height:'+rH+'px;border:1.6px solid '+C(hue,'bd')+';background:'+C(hue,'bg')); ctx.mark(cd,'box');
      var hasBar=cell.bar!=null, ty=hasBar?(rH-2)/2-19:(rH-2-22)/2;
      txt(cd,cell.t,'left:8px;width:'+(cw-20)+'px;text-align:center;top:'+ty+'px'+(cell.b?';color:'+C(hue,'tx'):''),16.5,cw-24,!!cell.b);
      if(hasBar){ var bw0=cw*0.56, bx0=(cw-4-bw0)/2, by0=ty+26;
        div(cd,'left:'+bx0+'px;top:'+by0+'px;width:'+bw0+'px;height:10px;border-radius:5px;background:'+ctx.cc('grid'));
        var fb=div(cd,'left:'+bx0+'px;top:'+by0+'px;width:'+(bw0*cell.bar)+'px;height:10px;border-radius:5px;background:'+C(hue,'pbd'));
        bars.push({el:fb,w:bw0*cell.bar}); } }); });
  S.bars=bars;
  W.appendChild(svg);
  return S;
 },
 seek:function(t,ctx,S){
  var P=S.period, ph=((t%P)+P)%P/P;
  S.pk.forEach(function(k){ var u=ph*k.laps+k.off; u=u-Math.floor(u);
    function at(d){ for(var i=0;i<k.seg.length;i++){ if(d<=k.seg[i]){ var a=k.pts[i],b=k.pts[i+1],f=k.seg[i]?d/k.seg[i]:0; return [a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f]; } d-=k.seg[i]; } return k.pts[k.pts.length-1]; }
    var q=at(u*k.len), q2=at(Math.max(0,u*k.len-14)); k.el.setAttribute('cx',q[0]); k.el.setAttribute('cy',q[1]); k.tr.setAttribute('cx',q2[0]); k.tr.setAttribute('cy',q2[1]);
    var fade=k.hide.length?1:Math.min(1,u*12,(1-u)*12);
    k.hide.forEach(function(b){ var dx=Math.max(b.x-q[0],0,q[0]-b.x-b.w), dy=Math.max(b.y-q[1],0,q[1]-b.y-b.h); var inside=dx===0&&dy===0; fade=Math.min(fade,inside?0:Math.min(1,Math.hypot(dx,dy)/10)); }); k.el.setAttribute('opacity',fade); k.tr.setAttribute('opacity',fade); });
  // token stream: tokens are emitted one by one over 85% of the loop, then hold; frame 0 already shows most of them
  var n=S.tok.length, sp=(ph+0.55)%1, shown=Math.min(n,Math.floor(sp/0.85*n)+1);
  S.tok.forEach(function(c,i){ c.style.opacity=i<shown?1:0.12; c.style.transform=i===shown-1&&sp<0.85?'translateY(-2px)':''; });
  if(S.cnt){ var v=shown*S.cnt.per; S.cnt.el.textContent=(v<10?'00':v<100?'0':'')+v+S.cnt.unit; }
  S.typed.forEach(function(T){ var p=(ph+0.6)%1, k=Math.min(T.full.length,Math.floor(p/0.8*T.full.length)+1); T.el.textContent=T.full.slice(0,k); });
 }
});
})();
