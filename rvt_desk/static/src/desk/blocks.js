/* Shared blocks: the same pieces are used by the desk and by the staff app, so the two can never differ in function. */
const pill=(t,c,i)=>`<span class="pill ${c||'plain'}">${i?ic(i):''}${esc(t)}</span>`;
const Bt=(label,a,v,cls,icon)=>`<button type="button" class="btn ${cls||''}" data-a="${a}"${v!=null?` data-v="${esc(v)}"`:''}>${icon?ic(icon):''}${label?`<span>${esc(label)}</span>`:''}</button>`;
const actB=(act,cls)=>act?Bt(act[2],act[0],act[1],cls||'sm',act[0]==='remind'?'wa':null):'';
const ini=n=>String(n).replace(/^(Mr\.|Mrs\.|Dr\.|Ar\.)\s*/,'').split(/\s+/).slice(0,2).map(w=>w[0]||'').join('').toUpperCase();
const hue=n=>{let h=0;for(const c of String(n))h=(h*31+c.charCodeAt(0))%5;return h};
const av=(n,c)=>`<span class="av h${hue(n)} ${c||''}" title="${esc(n)}">${esc(ini(n))}</span>`;
const empty=(t,i)=>`<div class="empty">${ic(i||'check')}<span>${esc(t)}</span></div>`;
const card=(title,right,body,cls)=>`<section class="card ${cls||''}"><header class="hd"><h3>${title}</h3>${right||''}</header>${body}</section>`;
const fin=(dev,k,ph,num)=>`<input class="inp" id="${dev.id}_${k}" data-m="${k}" value="${esc(dev.f[k]==null?'':dev.f[k])}" placeholder="${esc(ph||'')}" ${num?'inputmode="numeric"':''} autocomplete="off">`;
const fsel=(dev,k,opts,ph)=>`<select class="inp" id="${dev.id}_${k}" data-m="${k}" data-r="1">${ph?`<option value="">${esc(ph)}</option>`:''}${opts.map(o=>`<option value="${esc(o[0])}" ${String(dev.f[k])===String(o[0])?'selected':''}>${esc(o[1])}</option>`).join('')}</select>`;
const chips=(dev,k,opts,cls)=>`<div class="chips ${cls||''}">${opts.map(o=>`<button type="button" class="chip" data-a="set" data-v="${esc(k+'='+o[0])}" aria-pressed="${String(dev.f[k])===String(o[0])}">${o[2]?ic(o[2]):''}${esc(o[1])}</button>`).join('')}</div>`;
const fld=(label,inner,hint)=>`<div class="fld"><label>${esc(label)}</label>${inner}${hint?`<small>${esc(hint)}</small>`:''}</div>`;
const tog=(dev,k,label,icon)=>`<button type="button" class="chip tg" data-a="tog" data-v="${k}" aria-pressed="${!!dev.f[k]}">${ic(icon||'check')}${esc(label)}</button>`;
const dueCls=(o,st)=>st==='closed'?'mu':o<0?'c-bad':o<=1?'c-wait':'c-ink2';
/* a date: quick choices, or any other day from the calendar (where it can also be typed as day month year) */
const DMYHINT='Type the date as day month year, for example 25 11 26.';
function dueChips(dev,k,opts,cls){const f=dev.f,o=f[k+'_c']?parseDMY(f[k+'_t']):null,own=o!=null,yr=own&&dt(o).getUTCFullYear()!==dt(0).getUTCFullYear()?' '+dt(o).getUTCFullYear():'';
 /* in a row that scrolls sideways the calendar comes first, so it is never out of sight */
 const quick=opts.map(x=>`<button type="button" class="chip" data-a="set" data-v="${k}=${x[0]}" aria-pressed="${!own&&String(f[k])===String(x[0])}">${esc(x[1])}</button>`).join(''),other=`<button type="button" class="chip calc" data-a="cal" data-v="f|${k}" aria-pressed="${own}" aria-label="Choose the date from the calendar">${ic('cal')}${own?esc(fd(o))+yr:'Date'}</button>`,side=/scroll/.test(cls||'');
 return `<div class="duew"><div class="chips ${cls||''}">${side?other+quick:quick+other}</div></div>`}
/* a photo for a field: one clear button to take it; once taken it shows, and a tap removes it */
const photoTile=(dev,k,label,done)=>{const on=!!dev.f[k],src=on?pickedImg(k):'';return `<button type="button" class="drop pht ${on?'on':''}" data-a="tog" data-v="${k}" aria-pressed="${on}">${src?`<img alt="" src="${src}">`:ic(on?'check':'cam')}<span>${on?esc(done||'Photo added')+'<small>tap to remove it</small>':esc(label)}</span></button>`};
const dueOf=(f,k)=>{if(f[k+'_c']){const o=parseDMY(f[k+'_t']);return o==null?NaN:o}return +f[k]};
const forLabel=(p,k,vendor)=>k==='vendor'?(vendor||'Vendor'):k==='client'?(p.client.n||'Client'):agOf(k)?agN(k):k?(stf(k).full||stf(k).n):'Choose';
const areaLabel=(p,id)=>id==null?'Choose the room':id===''?'Whole site':entN(p,id)||'Choose the room';
const pickBtn=(dev,src,key,pid,label,icon,vendor)=>`<button type="button" class="pickb ${src==='area'&&dev.f[key]==null?'need':''}" data-a="pick" data-v="${src}|${key}|${pid}|${vendor||''}">${ic(icon)}<span><small>${src==='area'?'Area':'For'}</small><b>${esc(label)}</b></span>${ic('down')}</button>`;
/* a point's photos: the one taken when it was raised and, once it is done, the one taken after */
const ptBA=(x,L)=>!x.photo&&!x.cphoto?'':`<div class="ba ${x.photo&&x.cphoto?'pair':''}">${x.photo?`<figure><figcaption>${x.cphoto?tr('before',L):tr('pt_photo',L)}${x.on!=null?' · '+fd(x.on):''}</figcaption>${ptPhoto(x,0)}</figure>`:''}${x.cphoto?`<figure><figcaption>${tr('after',L)}${x.doneOn!=null?' · '+fd(x.doneOn):x.closedOn!=null?' · '+fd(x.closedOn):''}</figcaption>${ptPhoto(x,1)}</figure>`:''}</div>`;
const sitePts=p=>DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&!x.e);
const pbar=(a,b,c)=>`<div class="bar ${c||''}"><i style="width:${b?Math.round(a/b*100):0}%"></i></div>`;
const money=(n,cls)=>can('money')?`<b class="num ${cls||''}">${inr(n)}</b>`:`<span class="lockd" title="Amounts are shown to the people given access to them">${ic('lock')}hidden</span>`;
const stPill=p=>{const s=STATUS[picture(p).status];return pill(s[0],s[1])};
const LI={ns:'',wait:'pause',work:'play',done:'check'};
const kpi=(label,val,cls)=>`<div class="kpi ${cls?'k-'+cls:''}"><div class="lbl">${label}</div><b class="num ${cls||''}" data-cu="${val}">${val}</b></div>`;

/* ---------- a site, drawn: its elevation is inked as far as the work is done ---------- */
function siteCard(p,dev,cls){const pic=picture(p),g=pic.progress,s=STATUS[pic.status],share=p.onb?(g.wk[1]?g.wk[0]/g.wk[1]:0):null;
 return `<button type="button" class="site ${cls||''}" data-a="proj" data-v="${p.id}" ${dev&&dev.pid===p.id&&cls==='row'?'aria-current="true"':''}><div class="site-art">${elev(p.kind,share)}${p.onb?pill(s[0],s[1]):pill('to configure','gold')}</div>
  <div class="m"><h3>${esc(p.name)}</h3><p class="t2">${esc(p.label)} · ${esc(p.area)}</p>${p.onb?`${ticks(g.wk[0],g.wk[1],'ok',g.wk[2])}<div class="site-m"><span><b>${g.wk[0]}</b> of ${g.wk[1]} done</span><span><b>${g.pt[2]}</b> open</span>${pic.blockers.length?`<span class="c-bad"><b>${pic.blockers.length}</b> blocked</span>`:'<span class="c-ok">clear</span>'}</div>`:'<p class="t2">Runs the earlier way. Open it to configure.</p>'}</div></button>`}

/* ---------- to do: one list, filtered by chips with live counts ---------- */
function todoList(dev,items){if(!items.length)return `<div class="card">${empty('All clear. Nothing waits for you.')}</div>`;
 const secs=SECS.filter(s=>items.some(n=>n.sec===s[0])),f=secs.some(s=>s[0]===dev.tf)?dev.tf:'all',list=items.filter(n=>f==='all'||n.sec===f);
 return `<div class="chips scroll todo-f"><button type="button" class="chip" data-a="ui" data-v="tf=all" aria-pressed="${f==='all'}">All<b>${items.length}</b></button>${secs.map(s=>`<button type="button" class="chip" data-a="ui" data-v="tf=${s[0]}" aria-pressed="${f===s[0]}">${s[1]}<b>${items.filter(n=>n.sec===s[0]).length}</b></button>`).join('')}</div>
  <div class="tlist">${list.map(n=>{const s=SECS.find(x=>x[0]===n.sec);return `<article class="todo"><span class="mi ${SECC[n.sec]||''}">${ic(s[2])}</span><div class="m"><div class="lbl">${s[1]}${n.late?' · <span class="c-bad">late</span>':''}</div><h4>${esc(n.text)}</h4>
   <p class="t2"><b class="c-gold">${esc(n.p.name)}</b>${n.sub?' · '+esc(n.sub):''}</p>${n.warn?`<p class="t2 c-wait">${ic('alert')}${esc(n.warn)}</p>`:''}</div><div class="r">${actB(n.act,'sm gold')}</div></article>`}).join('')}</div>`}

/* ---------- project picture ---------- */
function measures(pic){const g=pic.progress,m=(l,a,b,x,c,w)=>`<div class="ms"><div class="lbl">${l}</div><div class="msn num"><b data-cu="${a}">${a}</b><span>of ${b}</span></div>${ticks(a,b,c,w)}<div class="msx">${x||'&nbsp;'}</div></div>`;
 return `<div class="mss">${m('Agencies decided',g.ag[0],g.ag[1],g.ag[1]-g.ag[0]?`<span class="c-bad">${g.ag[1]-g.ag[0]} undecided</span>`:'<span class="c-ok">all decided</span>','brz')}
  ${m('Drawings released',g.dr[0],g.dr[1],`<span class="c-ink2">${g.dr[1]-g.dr[0]} to go</span>`,'brz')}
  ${m('Work lines done',g.wk[0],g.wk[1],`<span class="c-work">${g.wk[2]} working</span>${g.wk[3]?` · <span class="c-wait">${g.wk[3]} waiting</span>`:''}`,'ok',g.wk[2])}
  ${m('Points closed',g.pt[0],g.pt[1],`<span class="c-ink2">${g.pt[2]} open</span>${g.pt[3]?` · <span class="c-bad">${g.pt[3]} past date</span>`:''}`,'ok')}</div>`}
function blockerRows(pic,dev){return pic.blockers.length?pic.blockers.map(b=>{const crit=b.crit||b.age>=DB.set.lim.stuck;return `<div class="rw blkr"><span class="ageb ${crit?'crit':''}"><b>${b.age}</b><i>${b.age===1?'day':'days'}</i></span><div class="m"><div class="t1">${esc(b.text)}</div>${b.sub?`<div class="t2">${esc(b.sub)}</div>`:''}
   <div class="t2"><span class="tag">${b.k}</span> holds <b>${esc(b.holds)}</b> · to act: <b class="c-gold">${esc(b.actor)}</b></div></div><div class="r">${actB(b.act)}</div></div>`}).join(''):empty('Nothing is blocked.')}
function nextRows(p,pic,dev){const k=dev.nt||'revert';
 if(k==='revert')return pic.next.revert.length?pic.next.revert.map(n=>`<div class="rw nx"><div class="m"><div class="who">${av(n.whoN,'sm')}${esc(n.whoN)}</div><div class="t1"><span class="tx">${esc(n.text)}</span></div><div class="t2">${esc(n.sub||'')}${n.warn?` · <span class="c-wait">${ic('alert')}${esc(n.warn)}</span>`:''}</div></div><div class="r">${n.late?pill('late','bad'):''}${actB(n.act)}</div></div>`).join(''):empty('Nothing waits on Revert.');
 if(k==='agencies')return pic.next.agencies.length?pic.next.agencies.map(n=>`<div class="rw"><div class="m"><div class="t1">${esc(n.name)} <span class="mu f12">· ${esc(n.trades)}</span></div><div class="t2"><b class="${n.od?'c-bad':'c-ink2'}">${plural(n.pts,'open point')}${n.od?' ('+n.od+' past date)':''}</b> · ${n.lines} lines: <span class="c-ok">${n.done} done</span>, <span class="c-work">${n.work} working</span>${n.wait?`, <span class="c-wait">${n.wait} waiting</span>`:''}</div>${n.sub?`<div class="t2 ${n.unopened?'c-bad':''}">${esc(n.sub)}</div>`:''}</div><div class="r">${Bt('Remind','remind',n.ag+'|'+p.id+'|'+n.rem,'sm wa','wa')}</div></div>`).join(''):empty('No agency is decided yet.','users');
 return pic.next.client.length?pic.next.client.map(n=>`<div class="rw"><div class="m"><div class="t1">${esc(n.text)}</div><div class="t2 ${n.late?'c-wait':''}">${esc(n.sub)}</div></div><div class="r">${Bt('Remind','remind','client|'+p.id+'|'+n.rem,'sm wa','wa')}${n.pt?Bt('Mark received','closept',n.pt,'sm'):''}</div></div>`).join(''):empty('Nothing is waiting on the client.')}
function statusCard(p,pic){const s=STATUS[pic.status],g=pic.progress,share=g.wk[1]?g.wk[0]/g.wk[1]:0,bl=pic.blockers;
 return `<section class="ink"><div class="tbr"><span>Project status</span><span>${bl.length?plural(bl.length,'blocker'):'no blocker'}</span></div><div class="ink-b"><div class="m"><span class="pill ${s[1]} lg"><i class="sdot"></i>${s[0]}</span>
  <p>${bl.length?esc(bl.slice(0,2).map(b=>b.text).join(' · '))+(bl.length>2?' · +'+(bl.length-2)+' more':''):'No blocker. Work, drawings and points are moving.'}</p></div>${elev(p.kind,share,{cls:'lg'})}</div></section>`}
function workView(p,dev){const v=dev.wv==='grid'?'grid':'plan';
 return card('Work',`<div class="seg sm"><button data-a="ui" data-v="wv=plan" aria-pressed="${v==='plan'}">${ic('layers')}Plan</button><button data-a="ui" data-v="wv=grid" aria-pressed="${v==='grid'}">${ic('grid')}Schedule</button></div>`,
  (v==='plan'?`<p class="t2 hint">Each room shows its trades as dots. Tap a room to change them.</p>${planView(p,dev)}${planLegend()}`:`<p class="t2 hint">Rooms down, trades across. Tap a cell to change it.</p>${gridBlock(p,dev)}`)+siteNote(p))}
/* points raised for the whole site carry no room, so no cell can show them: they are named under the plan */
function siteNote(p){const s=sitePts(p);if(!s.length)return '';const by={};s.forEach(x=>{const k=partyName(p,x);by[k]=(by[k]||0)+1});
 return `<button type="button" class="note wait lkn" data-a="sheet" data-v="sitepts|${p.id}">${ic('flag')}<span><b>${plural(s.length,'open point')} for the whole site</b>, not tied to one room: ${esc(Object.keys(by).map(k=>k+' '+by[k]).join(' · '))}</span>${ic('chev')}</button>`}
function pictureBlock(p,dev){const pic=picture(p),w=pic.week,nt=dev.nt||'revert';
 const tabs=[['revert','Revert'],['agencies','Agencies'],['client','Client']].map(t=>`<button data-a="ui" data-v="nt=${t[0]}" aria-pressed="${nt===t[0]}">${t[1]}<i>${pic.next[t[0]].length}</i></button>`).join('');
 return `<div class="stack">${statusCard(p,pic)}
  ${card('Progress','<span class="mu f12">one tick per item, counted from records</span>',measures(pic)+`<div class="week">${ic('refresh')}<span>This week</span> <b>${w.rel}</b> drawings released · <b>${w.started}</b> lines started · <b>${w.done}</b> lines done · <b>${w.closed}</b> points closed</div>`)}
  <div class="two">${card('Blockers',`<span class="cnt ${pic.blockers.length?'bad':''}">${pic.blockers.length}</span>`,`<div class="rows">${blockerRows(pic,dev)}</div>`)}
  ${card('Next actions',`<div class="seg sm">${tabs}</div>`,`<div class="rows">${nextRows(p,pic,dev)}</div>`)}</div>
  ${workView(p,dev)}${pic.noDwg.length?`<div class="note wait">${ic('alert')}Working without a drawing: ${esc([...new Set(pic.noDwg.map(l=>TX[l.t].n))].join(', '))} has work in hand but no released drawing yet.</div>`:''}
  <div class="actbar">${Bt('Start MOM','startmom',p.id,'gold','mom')}${Bt('Raise point','raise',p.id,'','plus')}${Bt('Ask for bill','askbill',p.id,'','bill')}</div></div>`}

/* ---------- schedule: rooms × trades ---------- */
function entState(p,e){const ls=p.lines.filter(l=>l.e===e.id),d=ls.filter(l=>l.st==='done').length;return !ls.length?['—','mu']:d===ls.length?['done','c-ok']:ls.some(l=>l.st!=='ns')?[d+' of '+ls.length+' done','c-work']:['not started','mu']}
function gridBlock(p,dev,ro){const tr=p.plan.map(x=>x.t);if(!p.ents.length)return empty('No rooms yet. Open Project configuration to add them.','grid');
 const head=tr.map(t=>{const pl=planOf(p,t);return `<th><div class="gh">${esc(TX[t].s)}</div><div class="ga ${pl.ag?'':'und'}">${pl.ag?esc(agN(pl.ag).split(' ')[0]):'undecided'}</div></th>`}).join('');
 const rows=p.ents.map(e=>{const es=entState(p,e);return `<tr><th><div class="ge">${esc(e.n)}</div><div class="gs ${es[1]}">${es[0]}</div></th>${tr.map(t=>{const l=p.lines.find(x=>x.e===e.id&&x.t===t);if(!l)return '<td><span class="c na">·</span></td>';
   const und=!lineAg(p,l),op=DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&x.e===e.id&&x.t===t).length,cls=l.st==='ns'&&und?'und':l.st;
   return `<td><button type="button" class="c ${cls}" ${ro?'disabled':`data-a="cell" data-v="${p.id}|${l.id}"`} title="${esc(e.n+' · '+TX[t].n+': '+(und&&l.st==='ns'?'agency undecided':LS[l.st][0])+(l.st==='wait'?' for '+waitText(p,l):''))}">${cls==='und'?ic('alert'):LI[l.st]?ic(LI[l.st]):'<i class="ring"></i>'}${op?kn(op,'dot'):''}</button></td>`}).join('')}</tr>`}).join('');
 return `<div class="gw" data-sc="grid${p.id}"><table class="gr"><thead><tr><th></th>${head}</tr></thead><tbody>${rows}</tbody></table></div>${planLegend()}`}
function byAgency(p){return [...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))].map(a=>{const ls=p.lines.filter(l=>lineAg(p,l)===a),c=s=>ls.filter(l=>l.st===s).length;
  return `<div class="rw"><div class="m"><div class="t1">${esc(agN(a))}</div>${ticks(c('done'),ls.length,'ok',c('work'))}<div class="t2">${plural(new Set(ls.map(l=>l.e)).size,'room')} · <span class="c-ok">${c('done')} done</span> · <span class="c-work">${c('work')} working</span> · <span class="c-wait">${c('wait')} waiting</span> · ${c('ns')} not started</div></div></div>`}).join('')}

/* ---------- drawings ---------- */
function planSVG(d){let s=0;for(const c of d.code+d.title)s=(s*33+c.charCodeAt(0))%997;const el=/^(CD|KD|WE|TE|DD|CS|ST)$/.test(d.code),ce=/^(FC|FCS|LT)$/.test(d.code),ee=/^(EL|SB|LC|AV|AC)$/.test(d.code);
 const k='stroke="currentColor" fill="none"';let g='';
 if(el){const n=3+s%3;g=`<rect x="40" y="40" width="320" height="200" ${k} stroke-width="2.200"/>`;for(let i=1;i<n;i++)g+=`<path d="M${40+i*320/n} 40v200" ${k}/>`;g+=`<path d="M40 90h320" ${k}/>`;for(let i=0;i<n;i++)g+=`<circle cx="${40+(i+.5)*320/n+18}" cy="165" r="3" ${k}/>`;g+=`<path d="M40 262h320M40 256v12M360 256v12M20 40v200M14 40h12M14 240h12" ${k} stroke-width=".800"/><text x="200" y="278" class="dim">${2400+s%5*150}</text><text x="12" y="144" class="dim" transform="rotate(-90 12 144)">2400</text>`}
 else{const x=140+s%80,y=120+s%50;g=`<path d="M40 40h320v200H40z" ${k} stroke-width="3"/><path d="M${x} 40v${y-40}M40 ${y}h${x-70}M${x-30} ${y}h30M${x} ${y}h${360-x-60}M${x+90} ${y}v${240-y}" ${k} stroke-width="2"/>
  <path d="M${x-70} ${y}a40 40 0 0 1 40 -40" ${k} stroke-width=".800" stroke-dasharray="3 3"/><path d="M40 262h320M40 256v12M360 256v12" ${k} stroke-width=".800"/><text x="200" y="278" class="dim">${9600+s%7*200}</text>`;
  if(ce)g+=`<rect x="60" y="60" width="${x-80}" height="${y-80}" ${k} stroke-dasharray="6 4"/><rect x="${x+20}" y="60" width="${320-x}" height="${y-80}" ${k} stroke-dasharray="6 4"/><rect x="60" y="${y+20}" width="${x+10}" height="${200-y}" ${k} stroke-dasharray="6 4"/>`;
  if(ee)for(let i=0;i<9;i++)g+=`<circle cx="${60+(s*(i+3)*17)%280}" cy="${55+(s*(i+5)*13)%170}" r="4" ${k}/><path d="M${60+(s*(i+3)*17)%280-4} ${55+(s*(i+5)*13)%170}h8" ${k}/>`;
  if(!ce&&!ee)g+=`<rect x="56" y="56" width="50" height="26" ${k}/><rect x="${x+30}" y="60" width="70" height="40" ${k}/><circle cx="${x+65}" cy="${y+60}" r="18" ${k}/><rect x="60" y="${y+30}" width="60" height="34" ${k}/>`}
 return `<svg viewBox="0 0 400 290" class="plan" aria-hidden="true">${g}</svg>`}
function dwgPaper(d,rev){const p=pOf(d.pid),r=rev||cur(d),st=r.st==='released'?'RELEASED':r.st==='superseded'?'SUPERSEDED':r.st==='approved'?'APPROVED':'NOT RELEASED';
 return `<div class="paper"><div class="stamp ${r.st}">${st}<small>REV ${r.n}${r.relOn!=null?' · '+fd(r.relOn):''}</small></div>${planSVG(d)}
  <div class="tblock"><div class="tb-logo">${LOGO}</div><div><span>Project</span><b>${esc(p.name)}</b></div><div><span>Drawing</span><b>${esc(d.title)}</b></div><div><span>Sheet</span><b class="mono">${sheetNo(d)}</b></div><div><span>Rev</span><b class="mono">${r.n}</b></div><div><span>Drawn</span><b>${esc(stf(d.ds).n)}</b></div><div><span>Checked</span><b>${r.apprBy?esc(stf(r.apprBy).n):'—'}</b></div></div></div>`}
function dwgRow(d,dev,showP){const p=pOf(d.pid),r=cur(d),s=DS[d.st],w=p.lines.filter(l=>l.st==='wait'&&l.cause==='drawing'&&l.ref===d.id).length,un=d.st==='released'?r.rc.filter(x=>x.opened==null).length:0,q=d.q.filter(x=>!x.ans).length;
 return `<button type="button" class="rw lk" data-a="dwg" data-v="${d.id}">${sht(d)}<div class="m"><div class="t1"><span class="tx">${esc(d.title)}</span></div>
  <div class="t2">${showP?esc(p.name)+' · ':''}${d.t?esc(TX[d.t].n):'General'} · ${esc(stf(d.ds).n)}${d.st!=='released'?` · <span class="${d.due<0?'c-bad':d.due<=1?'c-wait':''}">due ${dueW(d.due)}</span>`:` · released ${fd(r.relOn)}`}</div>
  ${w||un||q?`<div class="t2">${w?`<span class="c-wait">${ic('pause')}${plural(w,'line')} waiting</span> `:''}${un?`<span class="c-bad">${ic('eye')}${un} not opened</span> `:''}${q?`<span class="c-work">${ic('info')}${plural(q,'question')}</span>`:''}</div>`:''}</div>
  <div class="r">${pill(s[0],s[1])}</div></button>`}
function dwgDetail(d,dev){const p=pOf(d.pid),r=cur(d),s=DS[d.st],w=p.lines.filter(l=>l.st==='wait'&&l.cause==='drawing'&&l.ref===d.id);
 let act='';
 if(d.st==='to_draw')act=Bt('Start drawing','dstart',d.id,'','edit')+Bt(DB.set.approval?'Upload PDF and send for approval':'Upload PDF and release','sheet','sendappr|'+d.id,'gold','send');
 if(d.st==='in_progress')act=Bt(DB.set.approval?'Upload PDF and send for approval':'Upload PDF and release','sheet','sendappr|'+d.id,'gold','send');
 if(d.st==='awaiting')act=can('approve')?Bt('View PDF','view',d.id,'','eye')+Bt('Approve','approve',d.id,'gold','check'):Bt('View PDF','view',d.id,'','eye')+`<span class="note wait in">${ic('clock')}Waiting for ${esc(stf(p.principal).n)} to approve</span>`;
 if(d.st==='approved')act=Bt('View PDF','view',d.id,'','eye')+Bt('Release','release',d.id,'gold','send');
 if(d.st==='released')act=Bt('View PDF','view',d.id,'','eye')+Bt('New revision','newrev',d.id,'','plus');
 const rc=d.st==='released'?r.rc.map(x=>{const cl=x.to==='client',nm=cl?p.client.n||'Client':agN(x.to);return `<div class="rw"><div class="m"><div class="t1">${av(nm,'sm')}<span>${esc(nm)}</span>${cl?pill('client','gold'):''}</div><div class="t2">sent ${fd(x.sent)} on WhatsApp and in the app</div></div><div class="r">${x.opened!=null?`<span class="c-ok f12 b">${ic('check')}opened ${fd(x.opened)}</span>`:`<span class="c-bad f12 b">not opened</span>${Bt('Remind','remind',(cl?'client':x.to)+'|'+p.id+'|Please open '+sheetNo(d)+' '+d.title+'.','sm wa','wa')}`}</div></div>`}).join(''):'';
 const cd=r.client?(r.client.dec==='pending'?`<div class="note wait">${ic('clock')}Client approval pending since ${fd(r.relOn)}.</div>`:r.client.dec==='approved'?`<div class="note ok">${ic('check')}<span>Approved by <b>${esc(r.client.by)}</b> on ${fdw(r.client.on)}, ${r.client.at}. The tap is the record; no signature.</span></div>`:''):'';
 const revs=d.revs.slice().reverse().map(x=>`<div class="tl ${x.st}"><i class="rev">${x.n}</i><div><div class="t1">Revision ${x.n} ${pill({draft:'Draft',awaiting:'Awaiting approval',approved:'Approved',released:'Released',superseded:'Superseded'}[x.st],{draft:'plain',awaiting:'wait',approved:'gold',released:'ok',superseded:'plain'}[x.st])}</div>
   <div class="t2">${x.note?esc(x.note)+'<br>':''}${x.back?'<span class="c-bad">Sent back: '+esc(x.back)+'</span><br>':''}${x.sentBy?'sent by '+esc(stf(x.sentBy).n)+' '+fd(x.sentOn):''}${x.apprBy&&x.apprOn!=null?' · approved by '+esc(stf(x.apprBy).n)+' '+fd(x.apprOn):''}${x.relOn!=null?' · released '+fd(x.relOn):''}</div>
   ${x.client&&x.client.dec==='change'?`<div class="note bad sm">${ic('edit')}<span>Change asked by ${esc(x.client.by)} on ${fd(x.client.on)}, ${x.client.at}: “${esc(x.client.note)}”</span></div>`:''}</div></div>`).join('');
 /* the questions on this drawing, one thread per asker, as the Questions section shows them: answered here, or opened there */
 const qs=qThreads([d.pid]).filter(t=>t.d.id===d.id).map(t=>`<div class="q thq"><div class="thqh"><b>${esc(thName(t))}</b>${t.open?pill(t.open>1?t.open+' to answer':'to answer','bad'):''}${Bt('Open as a chat','thread',t.id,'sm ghost','chat')}</div>${thBubbles(t)}
   ${t.open?`<div class="qa">${fin(dev,thKey(t.id),'Type the answer…')}${Bt('Answer','thsend',t.id,'sm gold')}</div>`:''}</div>`).join('');
 const nq=d.q.filter(q=>!q.ans).length,qcard=card('Questions'+(nq?` <span class="cnt bad">${nq} to answer</span>`:''),Bt('Log a question from a call','sheet','logq|'+d.id,'sm ghost','plus'),qs||empty('No question on this drawing.','info'),nq?'hot':'');
 return `<div class="stack dd"><div class="ddh"><button type="button" class="shtb" data-a="view" data-v="${d.id}" aria-label="View the sheet">${sht(d,'md')}</button><div class="m"><div class="lbl">${sheetNo(d)} · ${d.t?esc(TX[d.t].n):'General set'}</div><h2 class="serif">${esc(d.title)}</h2><div class="t2">${esc(p.name)} · drawn by ${esc(stf(d.ds).n)} · ${d.st==='released'?'released '+fd(r.relOn):'due '+fdw(d.due)}</div>
   <div class="chips ro">${pill(s[0],s[1])}${d.forClient?pill('for client','gold'):''}${d.needsApproval?pill('client approves','plain'):''}</div></div></div>
  <div class="actbar">${act}</div>${nq?qcard:''}
  ${w.length?`<div class="note wait">${ic('pause')}<span><b>${plural(w.length,'work line')} waiting</b> for this drawing: ${esc(w.map(l=>entN(p,l.e)+' ('+TX[l.t].s+')').join(', '))}</span></div>`:''}${cd}
  ${d.st==='released'?card('Sent to',`<span class="mu f12">${r.rc.filter(x=>x.opened!=null).length} of ${r.rc.length} opened</span>`,`<div class="rows">${rc}</div>`):''}
  ${nq?'':qcard}
  ${card('Revisions',`<span class="mu f12">receivers only ever see the current one</span>`,`<div class="tls">${revs}</div>`)}</div>`}

/* ---------- points and MOM ---------- */
/* a point's photos as small pictures: the one taken when it was raised and, once it is closed, the one taken after.
   On the desk the larger picture shows while the pointer rests on one; on a phone a tap opens it. */
const ptThumbs=x=>x.photo||x.cphoto?`<span class="pths">${x.photo?phOf('point',x):''}${x.cphoto?phOf('point',x,1):''}</span>`:'';
/* the desk's log of points: one line per point, as the MOM register was always kept (number, visit, area, what, for whom,
   who raised it and when, by when, the photo, where it stands), with the photo to look at without opening anything */
function ptTable(list,dev,o){o=o||{};if(!list.length)return empty('Nothing here.');
 const line=x=>{const p=pOf(x.pid),v=x.vid?visOf(x.vid):null,open=x.st==='open',late=open&&x.due!=null&&x.due<0;
  return `<tr class="${x.st}"><td class="ar">${kn(x.n)}</td><td class="nw">${v?'Visit '+v.no:x.legacy?'earlier':'office'}</td>${o.proj?`<td>${esc(p.name)}</td>`:''}<td>${x.e?esc(entN(p,x.e)):'<span class="mu">Whole site</span>'}${x.t&&TX[x.t]?`<div class="t2">${esc(TX[x.t].n)}</div>`:''}</td>
   <td class="ptc"><span class="lkm" role="button" tabindex="0" data-a="ptview" data-v="${x.id}"><span class="tx">${esc(x.text)}</span></span>${x.fresh&&open&&x.vid&&x.kind!=='staff'?' '+pill('new','gold'):''}${!open&&x.note?`<div class="t2 c-ok">${esc(x.note)}</div>`:open&&x.rev==='check'?`<div class="t2 c-gold">marked done${x.doneOn!=null?' '+fd(x.doneOn):''}${x.note?': '+esc(x.note):''}</div>`:open&&x.rev==='change'?`<div class="t2 c-bad">change asked: ${esc(x.chg)}</div>`:open&&x.kind==='client'&&!x.confirmed?'<div class="t2 c-wait">not shown to the client until the office confirms</div>':x.pending?'<div class="t2 c-wait">saved on the phone · waiting to go</div>':''}</td>
   <td><b class="pty k-${x.kind}">${esc(partyName(p,x))}</b></td><td>${x.by?esc(stf(x.by).n):''}</td><td class="nw">${x.on!=null?fd(x.on):v?fd(v.date):''}</td>
   <td class="nw">${open?`<span class="due ${dueCls(x.due)}">${dueW(x.due)}</span>`:x.closedOn!=null?`<span class="mu">closed ${fd(x.closedOn)}</span>`:''}</td><td>${ptThumbs(x)}</td>
   <td>${open?(x.kind==='client'&&!x.confirmed?pill('to confirm','wait'):x.rev==='check'?pill('to check','gold','cam'):x.rev==='change'?pill('change asked','bad'):late?pill('past date','bad'):pill('open','work')):pill(x.doneBy?'done':'closed','ok','check')}${x.doneBy&&x.rev!=='change'?`<div class="t2">${esc(x.doneBy)}</div>`:''}</td>
   <td class="ar nw">${!open||o.ro?'':x.kind==='client'&&!x.confirmed?Bt('Confirm','confirmpt',x.id,'sm gold'):x.rev==='check'?Bt('Check','ptview',x.id,'sm gold','eye'):Bt('Close','closept',x.id,'sm')}</td></tr>`};
 return `<div class="tw"><table class="tb ptlog"><thead><tr><th class="ar">No</th><th>Visit</th>${o.proj?'<th>Project</th>':''}<th>Area</th><th>Point</th><th>For</th><th>Raised by</th><th>On</th><th>Due</th><th>Photo</th><th>Status</th><th></th></tr></thead><tbody>${list.map(line).join('')}</tbody></table></div>`}
/* the same points: a log table on the desk, rows on a phone */
const ptList=(list,dev,o)=>dev&&!dev.phone?ptTable(list,dev,o):`<div class="rows">${list.map(x=>ptRow(x,dev,o)).join('')||empty('Nothing here.')}</div>`;
function ptRow(x,dev,o){o=o||{};const p=pOf(x.pid),nm=partyName(p,x),v=x.vid?visOf(x.vid):null;
 return `<div class="rw pt ${x.st}">${kn(x.n)}<div class="m lkm" role="button" tabindex="0" data-a="ptview" data-v="${x.id}"><div class="t1"><span class="tx">${esc(x.text)}</span></div>
  <div class="t2">${x.fresh&&x.st==='open'&&x.vid&&x.kind!=='staff'?pill('new','gold')+' ':''}<b class="pty k-${x.kind}">${esc(nm)}</b>${x.e?' · '+esc(entN(p,x.e)):''}${o.proj?' · '+esc(p.name):''}${v?' · visit '+v.no:x.legacy?'':' · raised from the office'}${x.legacy?' · moved from the earlier MOM':''}</div>
  ${x.st==='closed'?`<div class="t2 c-ok">${ic('check')}${x.doneBy?'done by '+esc(x.doneBy)+' · ':'closed '}${fd(x.closedOn)}${x.note?' · '+esc(x.note):''}${x.photo&&x.cphoto?' · before and after':''}</div>`:x.rev==='check'?`<div class="t2 c-gold">${ic('cam')}marked done${x.doneBy?' by '+esc(x.doneBy):''}${x.doneOn!=null?' · '+fd(x.doneOn):''} · look and decide</div>`:x.rev==='change'?`<div class="t2 c-bad">${ic('refresh')}change asked: ${esc(x.chg)}</div>`:x.kind==='client'&&!x.confirmed?`<div class="t2 c-wait">${ic('eye')}not shown to the client until the office confirms</div>`:x.pending?`<div class="t2 c-wait">${ic('off')}saved on the phone · waiting to go</div>`:''}</div>
  <div class="r">${ptThumbs(x)}${x.st==='open'?`<span class="due ${dueCls(x.due)}">${dueW(x.due)}</span>${x.sent&&x.kind!=='staff'?`<span class="tick" title="sent">${ic('check')}${ic('check')}</span>`:''}${o.ro?'':x.kind==='client'&&!x.confirmed?Bt('Confirm','confirmpt',x.id,'sm gold'):x.rev==='check'?Bt('Check','ptview',x.id,'sm gold'):Bt('Close','closept',x.id,'sm')}`:''}</div></div>`}
function forOptions(p){const o=[...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))].map(a=>[a,agN(a).split(' ')[0],'agency']);o.push(['client','Client','client']);
 [...new Set([p.principal,...p.designers,...p.coords])].forEach(s=>o.push([s,stf(s).n,'staff']));return o}
function momCapture(v,dev){const p=pOf(v.pid),f=dev.f,opts=forOptions(p);if(f.m_vendor)opts.push(['vendor',f.m_vendor,'vendor']);if(!opts.some(o=>o[0]===f.m_for))f.m_for=opts[0][0];if(f.m_due==null)f.m_due=2;if(f.m_area&&!p.ents.some(e=>e.id===f.m_area))f.m_area=null;
 const here=DB.points.filter(x=>x.vid===v.id),earlier=DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&x.vid!==v.id&&!(x.kind==='staff')),grp={};
 earlier.forEach(x=>{const k=partyName(p,x);(grp[k]=grp[k]||[]).push(x)});
 const sendKeys=[...new Set(here.filter(x=>x.st==='open'&&x.kind==='agency').map(x=>x.party))],freshOf=k=>here.filter(x=>x.party===k&&x.st==='open'&&x.fresh).length,allOf=k=>here.filter(x=>x.party===k&&x.st==='open').length;
 const pend=here.filter(x=>x.pending).length+UI.outbox.length;
 return `<div class="momc"><div class="momh"><div><div class="lbl">Visit ${v.no} · ${fdw(v.date)}</div><h2 class="serif">${esc(p.name)}</h2></div>${UI.offline?`<span class="pill wait">${ic('off')}offline · ${pend} waiting to go</span>`:`<span class="pill ok">${ic('check')}saved</span>`}</div>
  ${earlier.length?`<details class="earlier" ${f.m_early===false?'':'open'}><summary><span class="lbl">Open from earlier</span><span class="f12">${Object.keys(grp).map(k=>`${esc(k.replace(/^(Mr\.|Mrs\.|Dr\.)\s*/,'').split(' ')[0])} <b>${grp[k].length}</b>`).join(' · ')}</span></summary>${ptList(earlier,dev)}</details>`:''}
  <div class="lbl mt">This visit · ${plural(here.length,'point')}</div>${here.length?ptList(here,dev):`<div class="rows"><div class="empty sm">${ic('mom')}<span>Write the first point below. Under ten seconds each.</span></div></div>`}
  <div class="dock"><div class="composer"><div class="pickrow">${pickBtn(dev,'for','m_for',p.id,forLabel(p,f.m_for,f.m_vendor),'user',v.id)}${pickBtn(dev,'area','m_area',p.id,areaLabel(p,f.m_area),'pin')}</div>
   <p class="keep">${ic('lock')}<span>Both stay for the next points, until you change them.</span></p>
   <div class="ctext">${fin(dev,'m_text','Type or speak the point…')}<button type="button" class="camb ${f.m_photo?'on':''}" data-a="tog" data-v="m_photo" aria-label="${f.m_photo?'Photo added: tap to remove it':'Take a photo'}" aria-pressed="${!!f.m_photo}">${f.m_photo&&pickedImg('m_photo')?`<img alt="" src="${pickedImg('m_photo')}">`:ic(f.m_photo?'check':'cam')}<span>${f.m_photo?'Added':'Photo'}</span></button></div>
   <div class="cr dt"><span class="lbl">Due</span>${dueChips(dev,'m_due',[[0,'Today'],[1,'Tmrw'],[2,dueW(2)],[5,dueW(5)],[7,fd(7)]],'scroll')}${Bt('Add','addpt',v.id,'gold','plus')}</div></div>
  <div class="sendbar"><span class="lbl">Send on WhatsApp</span><div class="chips">${sendKeys.map(k=>`<button type="button" class="btn sm wa" data-a="sendparty" data-v="${v.id}|${k}">${ic('wa')}<span>${esc(agN(k).split(' ')[0])} (${freshOf(k)||allOf(k)})${freshOf(k)?'':' ✓'}</span></button>`).join('')||'<span class="mu f12">Points for an agency appear here to send.</span>'}
   ${sendKeys.length>1?Bt('All','sendall',v.id,'sm wa','send'):''}${Bt('PDF','pdf','mom|'+v.id+'|all','sm ghost','file')}${v.st==='open'?Bt('Finish visit','finishvisit',v.id,'sm pri','check'):''}</div></div></div></div>`}
/* ---------- visits, by date ----------
   All of them, the latest first; or one day, chosen from the calendar: the visits held that day and, with them, the
   visits whose points fall due that day, so the person on site opens that visit and closes what was promised for today. */
function visitRow(v,dev,o){o=o||{};const p=pOf(v.pid),n=DB.points.filter(q=>q.vid===v.id),op=n.filter(q=>q.st==='open'),ck=op.filter(q=>q.rev==='check').length,late=op.filter(q=>q.due!=null&&q.due<0).length,dd=o.day!=null?op.filter(q=>q.due===o.day).length:0;
 return `<div class="rw vis"><span class="cal"><i>${MON[dt(v.date).getUTCMonth()]}</i><b>${dt(v.date).getUTCDate()}</b></span><div class="m"><div class="t1">${o.proj?esc(p.name)+' · visit '+v.no:'Visit '+v.no} ${v.st==='open'?pill('open','work'):''}${dd?pill(plural(dd,'point')+' due '+(o.day===0?'today':fd(o.day)),o.day<0?'bad':'wait','clock'):''}</div>
   <div class="t2">${fdw(v.date)}${v.by?' · by '+esc(stf(v.by).n):''} · ${plural(n.length,'point')} · ${op.length} open${ck?` · <b class="c-gold">${ck} to check</b>`:''}${late?` · <b class="c-bad">${late} past date</b>`:''}${o.att&&v.att.length?' · present: '+esc(v.att.join(', ')):''}</div></div>
  <div class="r">${Bt('PDF','pdf','mom|'+v.id+'|all','sm ghost','file')}${Bt('Open','openvisit',v.id,'sm')}</div></div>`}
function visitsCard(dev,pid,right){const pids=pid?[pid]:myPids(),day=dev.vd==null||dev.vd===''?null:+dev.vd,all=DB.visits.filter(v=>pids.includes(v.pid)).sort((a,b)=>b.date-a.date||b.no-a.no);
 const pick=`<div class="chips vdc"><button type="button" class="chip" data-a="ui" data-v="vd=" aria-pressed="${day==null}">All</button><button type="button" class="chip" data-a="ui" data-v="vd=0" aria-pressed="${day===0}">Today</button><button type="button" class="chip calc" data-a="cal" data-v="ui|vd|${pid||0}" aria-pressed="${day!=null&&day!==0}" aria-label="Choose a day from the calendar">${ic('cal')}${day!=null&&day!==0?esc(fdw(day)):'Date'}</button></div>`;
 let body;
 if(day==null){const some=dev.vall?all:all.slice(0,8);body=`<div class="rows">${some.map(v=>visitRow(v,dev,{proj:!pid,att:!!pid})).join('')||empty('No visit yet. Start the first MOM.','mom')}</div>${all.length>some.length?`<button type="button" class="btn sm ghost blk" data-a="ui" data-v="vall=1">${ic('down')}<span>Show all ${all.length} visits</span></button>`:''}`}
 else{const due=DB.points.filter(x=>pids.includes(x.pid)&&x.st==='open'&&x.due===day).sort((a,b)=>a.pid-b.pid||a.n-b.n),held=all.filter(v=>v.date===day),from=all.filter(v=>v.date!==day&&due.some(x=>x.vid===v.id));
  body=`<div class="lbl">Held on ${fdw(day)} ${dt(day).getUTCFullYear()}</div><div class="rows">${held.map(v=>visitRow(v,dev,{proj:!pid,att:!!pid,day})).join('')||`<div class="empty sm">${ic('mom')}<span>No visit on this day.</span></div>`}</div>
   <div class="lbl mt">Due on this day · ${plural(due.length,'point')}</div>${from.length?`<div class="rows">${from.map(v=>visitRow(v,dev,{proj:!pid,day})).join('')}</div>`:''}${due.length?ptList(due,dev,{proj:!pid}):`<div class="rows"><div class="empty sm">${ic('check')}<span>Nothing falls due on this day.</span></div></div>`}`}
 return card('Visits',pick+(right||''),body,'visc')}

/* ---------- questions: every conversation about a drawing, in one place ----------
   A row says who asks, what, and what it is about; the thread says it in full (the project, the drawing, the work it
   belongs to) and is answered where it stands, like a chat. */
function qRow(t,dev,cur){const d=t.d,p=pOf(d.pid),nm=thName(t),ms=thMsgs(t),l=ms[ms.length-1],when=l?(l.on===0?(l.at||'today'):fd(l.on)):'';
 return `<button type="button" class="rw lk qrow ${t.open?'unr':''} ${cur?'cur':''}" data-a="thread" data-v="${esc(t.id)}">${av(nm,'sm')}<div class="m"><div class="t1"><span class="tx">${esc(nm)}</span>${t.open?pill(t.open>1?t.open+' to answer':'to answer','bad'):''}<span class="mu f12 nw qwh">${esc(when)}</span></div>
  <div class="t2 qtx">${l?(l.k==='out'?'<b>Revert:</b> ':'')+esc(l.text||'Photo'):''}</div><div class="t2"><b class="c-gold">${esc(p.name)}</b> · ${sheetNo(d)} ${esc(d.title)}${d.t&&TX[d.t]?' · '+esc(TX[d.t].n):''}</div></div></button>`}
function thInfo(t){const d=t.d,p=pOf(d.pid),r=cur(d),nm=thName(t),who=[...new Set(t.qs.filter(q=>q.via!=='revert'&&q.byName).map(q=>q.byName))].filter(n=>n!==nm).join(', ');
 return `<div class="thinfo"><button type="button" class="shtb" data-a="view" data-v="${d.id}" aria-label="View the sheet">${sht(d,'md')}</button><div class="m"><div class="lbl">Question on a drawing · ${sheetNo(d)}</div><h3>${esc(d.title)}</h3>
  <div class="kv sm"><div><span>Project</span><b>${esc(p.name)}</b></div><div><span>Work</span><b>${d.t&&TX[d.t]?esc(TX[d.t].n):'General set'}${d.e&&entN(p,d.e)?' · '+esc(entN(p,d.e)):''}</b></div>
   <div><span>Asked by</span><b>${esc(nm)}${t.by==='client'?' · client':''}${who?' · '+esc(who):''}</b></div><div><span>Drawing</span><b>revision ${r.n} · ${DS[d.st][0].toLowerCase()}${d.st==='released'&&r.relOn!=null?' '+fd(r.relOn):''}</b></div></div>
  <div class="chips">${Bt('View the sheet','view',d.id,'sm','eye')}${Bt('Open the drawing','dwg',d.id,'sm ghost','dwg')}</div></div></div>`}
const thKey=id=>'th_'+String(id).replace(/\W/g,'_');
const thBubbles=t=>thMsgs(t).map(m=>m.k==='in'?`<div class="qb in"><div class="lbl">${esc(m.q.byName)} · ${m.on===0?'today':fd(m.on)}${m.at?' · '+esc(m.at):''}${m.q.via==='office'?' · logged from a call':''}</div>${esc(m.text)}${m.q.photo?phOf('question',m.q):''}</div>`
   :`<div class="qb out"><div class="lbl">${esc(stf(m.q.ansBy).n)} · ${m.on===0?'today':fd(m.on)}${m.at?' · '+esc(m.at):''}</div>${esc(m.text)}</div>`).join('');
function thView(t,dev){const nm=thName(t),k=thKey(t.id);
 return `<div class="momc chat thv">${thInfo(t)}<div class="q thm">${thBubbles(t)}</div>
  <div class="dock"><div class="composer"><div class="lbl">${t.open?(t.open>1?t.open+' questions wait for your answer':'Answer '+esc(nm)):'Write to '+esc(nm)}</div>
   <div class="ctext">${fin(dev,k,t.open?'Type the answer…':'Type a message…')}<button type="button" class="ib snd" data-a="thsend" data-v="${esc(t.id)}" aria-label="Send">${ic('send')}</button></div></div></div></div>`}
function pdfDoc(kind,a,b,o){ /* mom|vid|party  ·  open|pid  ·  points|pid|party (o.v visit, o.st open or all) */
 let p,title,meta,rows;
 if(kind==='points'){o=o||{};p=pOf(a);const v=o.v?visOf(o.v):null;rows=DB.points.filter(x=>x.pid===p.id&&(!v||x.vid===v.id)&&(b==='all'||partyKey(x)===b)&&(o.st==='all'||x.st==='open'));title=v?'Minutes of meeting':'Points';
  meta=[['Project',p.name],['Visit',v?v.no+' · '+fdw(v.date):'All visits'],['For',b==='all'?'All parties':rows[0]?partyName(p,rows[0]):''],[o.st==='all'?'Points':'Open',rows.length]]}else
 if(kind==='mom'){const v=visOf(a);p=pOf(v.pid);rows=DB.points.filter(x=>x.vid===v.id&&(b==='all'||partyKey(x)===b));title='Minutes of meeting';meta=[['Project',p.name],['Visit',v.no+' · '+fdw(v.date)],['For',b==='all'?'All parties':agN(b)],['Present',v.att.join(', ')]]}
 else{p=pOf(a);rows=DB.points.filter(x=>x.pid===p.id&&x.st==='open');title='Open points';meta=[['Project',p.name],['As on',fdw(0)],['Open',rows.length],['Site',p.area]]}
 return `<div class="pdf"><div class="pdfh"><div class="pl">${LOGO}</div><div><b>${title}</b><span>Revert Architects · Ahmedabad</span></div></div><div class="pdfm">${meta.map(m=>`<div><span>${m[0]}</span><b>${esc(m[1])}</b></div>`).join('')}</div>
  <table><thead><tr><th>No</th><th>Point</th><th>For</th><th>Area</th><th>By</th></tr></thead><tbody>${rows.map(x=>`<tr><td class="mono">${x.n}</td><td>${esc(x.text)}${x.fresh&&x.st==='open'?' <b class="new">NEW</b>':''}${x.photo?phOf('point',x):''}${x.st==='closed'?' <i>(closed)</i>':''}</td><td>${esc(partyName(p,x))}</td><td>${esc(entN(p,x.e))}</td><td class="mono">${fd(x.due)}</td></tr>`).join('')||'<tr><td colspan="5">No points.</td></tr>'}</tbody></table>
  <div class="pdff">A point agreed on site is a MOM point in the app. · Page 1 of 1</div></div>`}

/* ---------- bills ---------- */
function billRow(b,dev,showP){const p=pOf(b.pid),s=BS[b.st];return `<button type="button" class="rw lk" data-a="bill" data-v="${b.id}"><span class="mi">${ic('bill')}</span><div class="m"><div class="t1">${esc(agN(b.ag))}<span class="mu f12"> · ${esc(TX[b.t].n)}</span></div><div class="t2">${showP?esc(p.name)+' · ':''}${esc(b.what)}</div>
  <div class="t2">billed to <b class="${b.billedTo==='client'?'c-gold':'c-work'}">${b.billedTo==='client'?'the client':'Revert'}</b>${b.no?' · '+esc(b.no):''}${b.st==='asked'?' · asked '+fd(b.askedOn):b.subOn!=null?' · submitted '+fd(b.subOn):''}</div></div>
  <div class="r">${b.amount!=null?money(b.amount):''}${pill(s[0],s[1])}</div></button>`}
function moneyView(list){const by={};list.filter(b=>b.amount!=null&&b.st!=='asked'&&b.st!=='returned').forEach(b=>{const k=b.ag,o=by[k]=by[k]||{billed:0,toC:0,toR:0,pC:0,pR:0,rec:0};o.billed+=b.amount;o[b.billedTo==='client'?'toC':'toR']+=b.amount;
   b.pay.forEach(x=>{o[x.by==='client'?'pC':'pR']+=x.amount;if(x.by==='revert'&&b.billedTo==='client')o.rec+=x.amount})});
 const T={billed:0,toC:0,toR:0,pC:0,pR:0,rec:0},ks=Object.keys(by);ks.forEach(k=>Object.keys(T).forEach(f=>T[f]+=by[k][f]));const un=o=>o.billed-o.pC-o.pR;
 if(!ks.length)return empty('No bill is on record yet.','bill');
 return `<div class="kpis in"><div class="kpi"><div class="lbl">Billed</div><b class="num">${inr(T.billed)}</b></div><div class="kpi"><div class="lbl">Paid</div><b class="num c-ok">${inr(T.pC+T.pR)}</b></div><div class="kpi"><div class="lbl">Unpaid</div><b class="num c-bad">${inr(un(T))}</b></div><div class="kpi"><div class="lbl">To recover from clients</div><b class="num c-wait">${inr(T.rec)}</b></div></div>
  <div class="tw"><table class="tb"><thead><tr><th>Agency</th><th class="ar">Billed</th><th class="ar">To client</th><th class="ar">To Revert</th><th class="ar">Paid by client</th><th class="ar">Paid by Revert</th><th class="ar">Unpaid</th><th class="ar">To recover</th></tr></thead><tbody>
  ${ks.map(k=>{const o=by[k];return `<tr><td><b>${esc(agN(k))}</b></td><td class="ar num">${inr(o.billed)}</td><td class="ar num">${inr(o.toC)}</td><td class="ar num">${inr(o.toR)}</td><td class="ar num c-ok">${inr(o.pC)}</td><td class="ar num c-ok">${inr(o.pR)}</td><td class="ar num ${un(o)?'c-bad b':''}">${inr(un(o))}</td><td class="ar num ${o.rec?'c-wait b':''}">${inr(o.rec)}</td></tr>`}).join('')}</tbody></table></div>
  <p class="mu f12">“To recover” = paid by Revert on a bill addressed to the client. A register only; nothing is posted to accounts.</p>`}
