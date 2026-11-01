/* Interactive playback and local text edits for self-contained live-panel pages. */
window.LPInteractive = function(options) {
  'use strict';
  var stage = options.stage, cfg = options.config, views = options.views;
  var bar = document.getElementById('lp-controls'), modeButton = document.getElementById('lp-mode');
  var previous = document.getElementById('lp-prev'), next = document.getElementById('lp-next');
  var position = document.getElementById('lp-position'), editButton = document.getElementById('lp-edit'), speedControl = document.getElementById('lp-speed');
  var status = document.getElementById('lp-status'), dialog = document.getElementById('lp-dialog');
  var input = document.getElementById('lp-text'), targets = [], edits = {}, selected = null;
  var started = false, editing = false, mode = 'auto', index = 0, anchor = 0, timeOffset = 0, speed = 1, focused = null;
  var problem = '', editProblem = '', steps = findSteps(), key = storageKey();

  function numbered(count, period, label) {
    var out = [];
    for(var i=0;i<count;i++) out.push({start:i*period/count,end:(i+1)*period/count,label:label(i)});
    return out;
  }
  function findSteps() {
    var explicit = cfg.playback && cfg.playback.steps;
    if(explicit !== undefined) {
      if(!Array.isArray(explicit) || !explicit.length || explicit.some(function(s){
        return !s || typeof s.start !== 'number' || !isFinite(s.start) ||
          typeof s.end !== 'number' || !isFinite(s.end) || s.end <= s.start;
      })) {
        problem = 'playback.steps must contain steps with finite start < end';
      } else return explicit.map(function(s,i){ return {start:s.start,end:s.end,label:String(s.label||('步骤 '+(i+1)))}; });
    }
    for(var v=0;v<views.length;v++) {
      var item=views[v], s=item.state||{}, e=item.e||{};
      if(item.kind==='excalidraw' && s.steps && s.steps.length && s.starts && s.durs) {
        return s.steps.map(function(st,i){ return {start:s.starts[i]-s.t0,end:s.starts[i]-s.t0+s.durs[i],label:String((e.steps[i]&&e.steps[i].note)||st.node.n.label||('步骤 '+(i+1)))}; });
      }
      if(item.kind==='loop' && s.H && s.T) {
        return numbered(s.H,s.period,function(i){ var n=s.byId[s.hops[i].from]; return n&&n.label||s.hops[i].from; });
      }
      if(item.kind==='loop' && s.ambientOnly && s.nodeLit) {
        var hops=[];
        (e.walks||(e.walk?[e.walk]:[])).forEach(function(walk){
          for(var i=0;i+1<walk.length;i++) if(s.nodeLit[walk[i]] && s.byId[walk[i]]) hops.push(walk[i]);
        });
        if(hops.length) {
          Object.keys(s.nodeLit).forEach(function(id){s.nodeLit[id].setAttribute('data-lp-focus-node',id);});
          return numbered(hops.length,s.period,function(i){return s.byId[hops[i]].label||hops[i];})
            .map(function(step,i){step.focus=s.nodeLit[hops[i]]; return step;});
        }
      }
      if(item.kind==='ring' && s.n && s.period) {
        return numbered(s.n,s.period,function(i){ return (e.steps[i]&&e.steps[i].label)||('步骤 '+(i+1)); });
      }
      if(item.kind==='funnel' && s.n && s.period) {
        return numbered(s.n,s.period,function(i){ return (e.stages[i]&&e.stages[i].label)||('步骤 '+(i+1)); });
      }
    }
    var machines=cfg.machines||{}, ids=Object.keys(machines);
    for(var j=0;j<ids.length;j++) {
      var m=machines[ids[j]], values=m.type==='cycle'&&m.values;
      if(m.type==='triggers') values=m.items;
      if(values && values.length && Number(m.period)>0) {
        var order=m.type==='cycle' && m.order && m.order.length ? m.order : values.map(function(_,i){return i});
        return order.map(function(i,k){ var value=values[i], text=typeof value==='object'?(value.name||value.t||value.m):value;
          var start=(Number(m.t0)||0)+k*Number(m.period);
          return {start:start,end:start+Number(m.period),label:String(text||('步骤 '+(k+1)))}; });
      }
    }
    for(var k=0;k<ids.length;k++) {
      var lane=machines[ids[k]], period=Number(lane.period), run=Number(lane.run), offset=Number(lane.off)||0;
      if(lane.type==='lane' && period>run && run>0) return [
        {start:offset,end:offset+run,label:lane.busy||'运行'},
        {start:offset+run,end:offset+period,label:(lane.done&&lane.done[0])||'完成'}
      ];
    }
    return [{start:0,end:options.duration,label:'完整动画'}];
  }

  function storageKey() {
    var text=JSON.stringify(cfg), hash=2166136261;
    for(var i=0;i<text.length;i++) hash=Math.imul(hash^text.charCodeAt(i),16777619);
    return 'ni-live-panel:edits:'+location.pathname+':'+(hash>>>0).toString(36);
  }
  function loadEdits() {
    var embedded=document.getElementById('live-edits');
    try { if(embedded) edits=JSON.parse(embedded.textContent)||{}; } catch(_) { edits={}; }
    if(!options.manual) try {
      var saved=localStorage.getItem(key);
      if(saved!==null) edits=JSON.parse(saved)||{};
    } catch(_) { status.textContent='无法自动保存，请下载 HTML'; }
    if(!edits || typeof edits!=='object' || Array.isArray(edits)) edits={};
  }
  function persist() {
    try { localStorage.setItem(key,JSON.stringify(edits)); status.textContent=''; }
    catch(_) { status.textContent='无法自动保存，请下载 HTML'; }
  }
  function textNodes(el) {
    var walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT), nodes=[], n;
    while((n=walker.nextNode())) {
      var owner=n.parentElement&&n.parentElement.closest('[data-lp-text-id]');
      if(owner===el) nodes.push(n);
    }
    return nodes;
  }
  function targetFor(key,record) {
    var pair=key.split(':'), target=targets[Number(pair[0])];
    if(!record || typeof record.anchor!=='string') return null;
    if(!target || target.anchor!==record.anchor) {
      var matches=targets.filter(function(t){return t.anchor===record.anchor});
      target=matches.length===1?matches[0]:null;
    }
    return target;
  }
  function nodeFor(key,record) {
    var pair=key.split(':'), target=targetFor(key,record);
    if(!target) return null;
    var nodes=textNodes(target.el);
    return nodes.length===record.count?nodes[Number(pair[1])]:null;
  }
  function applyEdits() {
    if(!started) return;
    var focus=mode==='step'?(steps[index].focus||null):null;
    if(focus!==focused) {
      if(focused) focused.style.opacity='0';
      focused=focus||null;
      if(focused) focused.style.opacity='1';
    }
    Object.keys(edits).forEach(function(id){
      var record=edits[id], node=nodeFor(id,record);
      if(node && typeof record.text==='string' && node.nodeValue!==record.text) node.nodeValue=record.text;
    });
  }
  function findTextAt(x,y) {
    var best=null;
    targets.forEach(function(target,i){
      var el=target.el, nodes=textNodes(el);
      if(!el.getClientRects().length || getComputedStyle(el).visibility==='hidden') return;
      nodes.forEach(function(node,j){
        if(!node.nodeValue.trim()) return;
        var range=document.createRange(); range.selectNodeContents(node);
        Array.from(range.getClientRects()).forEach(function(r){
          if(r.width && r.height && x>=r.left-3 && x<=r.right+3 && y>=r.top-3 && y<=r.bottom+3) {
            var area=r.width*r.height;
            if(!best || area<best.area) best={key:i+':'+j,text:node.nodeValue,anchor:target.anchor,count:nodes.length,area:area};
          }
        });
      });
    });
    return best;
  }
  function openEditor(hit) {
    selected={key:hit.key,original:hit.text,anchor:hit.anchor,count:hit.count,had:Object.prototype.hasOwnProperty.call(edits,hit.key),previous:edits[hit.key]};
    input.value=hit.text; dialog.hidden=false; input.focus(); input.select();
  }
  function closeEditor(cancel) {
    if(!selected) return;
    if(cancel) {
      if(selected.had) edits[selected.key]=selected.previous;
      else { delete edits[selected.key]; var node=nodeFor(selected.key,selected); if(node) node.nodeValue=selected.original; }
      persist(); applyEdits(); showPosition();
    }
    selected=null; dialog.hidden=true; editButton.focus();
  }
  function exportPage() {
    var clone=document.documentElement.cloneNode(true), copyStage=clone.querySelector('#stage');
    copyStage.replaceChildren(); clone.querySelector('#lp-controls').hidden=true; clone.querySelector('#lp-dialog').hidden=true;
    clone.querySelector('#lp-text').textContent=''; clone.querySelector('body').classList.remove('lp-editing');
    var error=clone.querySelector('#err'); if(error) error.remove();
    var embedded=clone.querySelector('#live-edits');
    if(!embedded) { embedded=document.createElement('script'); embedded.id='live-edits'; embedded.type='application/json'; clone.querySelector('head').appendChild(embedded); }
    embedded.textContent=JSON.stringify(edits).replace(/</g,'\\u003c');
    var blob=new Blob(['<!doctype html>\n',clone.outerHTML],{type:'text/html;charset=utf-8'}), url=URL.createObjectURL(blob);
    var a=document.createElement('a'); a.href=url;
    a.download=String((cfg.meta&&cfg.meta.title)||'live-panel').replace(/[\\\\/:*?"<>|\x00-\x1f]/g,'_').slice(0,80)+'-edited.html';
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(function(){URL.revokeObjectURL(url)},1000);
  }
  function showPosition() {
    var label=mode==='step'?String(steps[index].label):'';
    Object.keys(edits).some(function(id){ var e=edits[id]; if(e&&e.count===1&&e.anchor===label){label=e.text; return true;} return false; });
    position.textContent=mode==='step'?(index+1)+' / '+steps.length+' · '+label:'';
    position.title=label;
    previous.disabled=next.disabled=mode!=='step'||steps.length<2;
    modeButton.textContent=mode==='step'?'自动播放':'单步模式';
    modeButton.setAttribute('aria-pressed',String(mode==='step'));
  }
  function jump(delta) {
    index=(index+delta+steps.length)%steps.length; anchor=performance.now();
    window.seek(steps[index].start); showPosition();
  }
  function tick(now) {
    var elapsed=(now-anchor)/1000*speed, t;
    if(mode==='step') { var s=steps[index]; t=s.start+(elapsed%(s.end-s.start)); }
    else t=(timeOffset+elapsed)%options.duration;
    window.seek(t); requestAnimationFrame(tick);
  }
  function start() {
    targets=Array.from(stage.querySelectorAll('[data-t="text"],[data-lp-editable],svg text')).filter(function(el){
      return !el.parentElement || !el.parentElement.closest('[data-t="text"],[data-lp-editable],svg text');
    }).map(function(el,i){
      el.setAttribute('data-lp-text-id',String(i)); return {el:el,anchor:el.textContent};
    });
    status.textContent=''; editButton.setAttribute('aria-pressed','false'); editButton.textContent='编辑文字'; if(speedControl) speedControl.value='1';
    loadEdits(); started=true;
    if(Object.keys(edits).some(function(id){return !targetFor(id,edits[id]);})) {
      editProblem='some saved text no longer matches the page';
      status.textContent='部分修改未匹配，请检查页面';
    }
    applyEdits();
    if(options.manual) return;
    bar.hidden=false; options.fit();
    if(window.ResizeObserver) new ResizeObserver(options.fit).observe(bar);
    if(problem) status.textContent='步骤配置无效，请检查 playback.steps';
    modeButton.addEventListener('click',function(){
      if(mode==='auto') {
        var t=window.__t||0, found=steps.findIndex(function(s){return t>=s.start&&t<s.end;});
        index=found<0?0:found; mode='step'; anchor=performance.now(); window.seek(steps[index].start);
      } else { mode='auto'; timeOffset=window.__t||0; anchor=performance.now(); applyEdits(); }
      showPosition();
    });
    previous.addEventListener('click',function(){jump(-1)});
    next.addEventListener('click',function(){jump(1)});
    if(speedControl) speedControl.addEventListener('change',function(){
      var nextSpeed=Number(speedControl.value); if(!isFinite(nextSpeed)||nextSpeed<=0) return;
      var now=performance.now(), elapsed=(now-anchor)/1000*speed;
      if(mode==='step') anchor=now-(elapsed%(steps[index].end-steps[index].start))*1000/nextSpeed;
      else { timeOffset=(timeOffset+elapsed)%options.duration; anchor=now; }
      speed=nextSpeed;
    });
    editButton.addEventListener('click',function(){ editing=!editing; document.body.classList.toggle('lp-editing',editing);
      editButton.setAttribute('aria-pressed',String(editing)); editButton.textContent=editing?'完成编辑':'编辑文字';
      status.textContent=editing?'点击要修改的文字':''; });
    stage.addEventListener('click',function(ev){
      if(!editing || !dialog.hidden) return;
      var hit=findTextAt(ev.clientX,ev.clientY);
      if(hit){ ev.preventDefault(); ev.stopPropagation(); openEditor(hit); }
    });
    input.addEventListener('input',function(){ if(selected){edits[selected.key]={text:input.value,anchor:selected.anchor,count:selected.count}; persist(); applyEdits(); showPosition();} });
    document.getElementById('lp-save').addEventListener('click',function(){closeEditor(false)});
    document.getElementById('lp-cancel').addEventListener('click',function(){closeEditor(true)});
    dialog.addEventListener('keydown',function(ev){if(ev.key==='Escape'){ev.preventDefault();closeEditor(true)}});
    document.getElementById('lp-export').addEventListener('click',exportPage);
    showPosition(); anchor=performance.now(); requestAnimationFrame(tick);
  }
  return {start:start,afterSeek:applyEdits,problems:function(){return [problem,editProblem].filter(Boolean);}};
};
