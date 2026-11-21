/* The architect's graphics. Everything here is drawn from records, never decoration for its own sake:
   tick rulers (one tick per real item), elevations that get inked from the ground up as work completes,
   the living plan (rooms fill in as their trades finish), drawing sheets with a revision mark, keynote bubbles.
   Flutter: each of these is one CustomPainter; the draw-in animation is a PathMetric sweep.
   Everything is vector, so it stays sharp at any pixel density, a 4K screen or projector included. */
let GID=0;
function ticks(a,b,cls,work){const n=Math.min(b,36),k=b?n/b:0,on=Math.round(a*k),hf=Math.min(n-on,Math.round((work||0)*k));let h='';
 for(let i=0;i<n;i++)h+=`<i class="${i<on?'on':i<on+hf?'hf':''}" style="--i:${i}"></i>`;
 return `<span class="tkb ${cls||''}" role="img" aria-label="${a} of ${b}">${h||'<i></i>'}</span>`}

const CIRC=(x,y,r)=>`M${x-r} ${y}a${r} ${r} 0 1 0 ${2*r} 0a${r} ${r} 0 1 0-${2*r} 0`;
/* ---------- elevations ----------
   Each site is a fine line elevation on the sheet. All of it is there as dashed construction lines; the part that is
   built is inked from the ground up to a datum line that stands at the share of work done. A point of light runs
   along the inked lines. Flutter: one CustomPainter; the draw-in and the running light are PathMetric sweeps. */
const ELEV={
 home:{top:16,p:['M6 100H194','M40 100V62H128V100','M56 62V30H150V62H128','M52 30H154M52 30V26H154V30','M72 26V16H92V26','M52 100V74H66V100',
  'M76 70H120V92H76ZM90.7 70V92M105.3 70V92','M66 38H112V54H66ZM81.3 38V54M96.7 38V54','M124 38H142V54H124Z','M128 72H180V75H128M175 75V100',
  'M22 100V80',CIRC(22,69,11),'M186 100V91',CIRC(186,85,6)]},
 office:{top:2,p:['M6 100H194','M30 100V78H170V100','M52 78V16H148V78','M48 16H152','M52 28.4H148M52 40.8H148M52 53.2H148M52 65.6H148','M68 16V78M84 16V78M100 16V78M116 16V78M132 16V78',
  'M88 16V8H118V16M103 8V2','M92 100V84H108V100M100 84V100','M84 82H116','M38 84H84V96H38ZM116 84H162V96H116Z','M184 100V86',CIRC(184,78,8),'M16 100V91',CIRC(16,85,6)]},
 clinic:{top:14,p:['M6 100H194','M28 100V58H172V100','M24 58H176','M60 58V34H140V58','M56 34H144','M88 100V72H112V100M100 72V100','M80 70H120V66H80Z',
  'M38 68H70V88H38ZM54 68V88','M130 68H162V88H130ZM146 68V88','M70 41H96V52H70ZM104 41H130V52H104Z',CIRC(100,23,8),'M100 18.5V27.5M95.5 23H104.5','M14 100V84',CIRC(14,76,8)]}};
/* p = share built (0..1), or null for a site that is not set up yet (construction lines only) */
function elev(kind,p,o){o=o||{};const E=ELEV[kind]||ELEV.home,on=p!=null,k=on?Math.max(0,Math.min(1,p)):0,id='ev'+(++GID),y=100-(100-E.top)*k,part=k>0&&k<1;
 const gh=E.p.map(d=>`<path d="${d}"/>`).join(''),ink=E.p.map((d,i)=>`<path d="${d}" pathLength="1" style="--i:${i}"/>`).join('');
 return `<svg class="elev ${o.cls||''}" viewBox="0 0 200 106" aria-hidden="true"><defs><clipPath id="${id}"><rect x="0" y="${(y-.8).toFixed(1)}" width="200" height="${(107-y).toFixed(1)}"/></clipPath></defs><g class="eg">${gh}</g>${k>0?`<g clip-path="url(#${id})"><g class="ei">${ink}</g>${o.still?'':`<g class="el">${ink}</g>`}</g>`:''}${part?`<g class="ed" style="--dy:${(100-y).toFixed(1)}px"><path d="M2 ${y.toFixed(1)}H190"/><path class="edm" d="M190 ${(y-6).toFixed(1)}h8l-4 6z"/></g>`:''}</svg>`}
/* three elevations side by side, fully inked: the backdrop of the splash and of the sign-in pages */
const skyline=()=>`<div class="skyl" aria-hidden="true">${['home','office','clinic'].map(k=>elev(k,1,{still:1})).join('')}</div>`;
/* the wordmark with unit-length paths, so the splash can draw it line by line before filling it */
const LOGOD=LOGO.replace(/<path /g,'<path pathLength="1" ');

/* ---------- the living plan ---------- */
const RW={'Living room':3,'Dining':2,'Kitchen':2.2,'Master bedroom':2.6,'Bedroom':2.2,'Toilet':1.1,'Pooja room':1.1,'Balcony / wash area':1.4,'Passage / foyer':1.3,'Staircase':1.2,'Garden / backyard':2.6,
 'Cabin':1.7,'Conference / board room':2.6,'Workstation area':3.2,'Reception / waiting':2.2,'Pantry':1.4,'Server / store room':1.1,'Consulting room':2.1,'Procedure room':2.1,'Lab':1.7,'Other room':1.6};
function planRects(p){const rooms=p.ents.filter(e=>e.ty!=='Whole site'),n=rooms.length;if(!n)return [];
 const wt=e=>RW[e.ty]||1.6,R=n<=2?1:n<=5?2:n<=10?3:4,tot=rooms.reduce((s,e)=>s+wt(e),0),rows=[];let cur=[],acc=0;
 rooms.forEach((e,i)=>{cur.push(e);acc+=wt(e);const left=n-i-1,need=R-rows.length-1;if(need>0&&left>0&&(acc>=tot/R*.86||left<=need)){rows.push(cur);cur=[];acc=0}});if(cur.length)rows.push(cur);
 const X=16,Y=16,W=328,H=[0,112,168,216,256][rows.length],hs=rows.map(r=>Math.sqrt(r.reduce((s,e)=>s+wt(e),0))),hT=hs.reduce((a,b)=>a+b,0),out=[];let y=Y;
 rows.forEach((r,ri)=>{const h=H*hs[ri]/hT,rt=r.reduce((s,e)=>s+wt(e),0);let x=X;r.forEach(e=>{const w=W*wt(e)/rt;out.push({e,x,y,w,h,top:ri===0,bot:ri===rows.length-1});x+=w});y+=h});return out}
function roomState(ls){const d=ls.filter(l=>l.st==='done').length;return !ls.length?'na':d===ls.length?'done':ls.some(l=>l.st==='wait')?'wait':ls.some(l=>l.st!=='ns')?'work':'ns'}
function planView(p,dev,o){o=o||{};const rs=planRects(p),ws=p.ents.find(e=>e.ty==='Whole site'),id='pl'+(++GID);if(!rs.length&&!ws)return empty('No rooms yet. Open Project configuration to add them.','grid');
 const bot=rs.length?Math.max(...rs.map(r=>r.y+r.h)):16,H=bot+(ws?50:22),linesOf=e=>p.lines.filter(l=>l.e===e.id&&(!o.ag||lineAg(p,l)===o.ag));
 const dots=(ls,x,y)=>ls.map((l,k)=>`<circle class="pd ${l.st==='ns'&&!lineAg(p,l)?'und':l.st}" cx="${(x+k*9).toFixed(1)}" cy="${y.toFixed(1)}" r="3"/>`).join('');
 const act=e=>o.ro?'':`data-a="room" data-v="${p.id}|${e.id}" role="button" tabindex="0"`;
 const rooms=rs.map((r,i)=>{const ls=linesOf(r.e),st=roomState(ls),done=ls.filter(l=>l.st==='done').length,out=r.e.ty==='Garden / backyard',op=o.ag?0:DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&x.e===r.e.id).length;
  const fill=st==='work'?`url(#${id}w)`:st==='wait'?`url(#${id}a)`:null,cx=r.x+r.w/2,dx=r.x+11,yb=r.y+r.h,per=Math.max(6,Math.floor((r.w-14)/5.4)),words=r.e.n.toUpperCase().split(' '),tl=[''];
  words.forEach(w=>{const c=tl[tl.length-1];if((c+' '+w).trim().length>per&&c&&tl.length<2)tl.push(w);else tl[tl.length-1]=(c+' '+w).trim()});
  const door=r.bot&&!r.top?`M${dx} ${r.y}v12M${dx} ${r.y+12}a12 12 0 0 0 12-12`:`M${dx} ${yb}v-12M${dx} ${yb-12}a12 12 0 0 1 12 12`;
  const win=(r.top?`M${cx-13} ${r.y+3.500}h26`:'')+(r.bot?`M${cx-13} ${yb-3.500}h26`:'');
  return `<g class="rm ${st}${out?' out':''}${ls.length?'':' off'}" ${ls.length?act(r.e):''} style="--i:${i}"><title>${esc(r.e.n)}: ${ls.length?done+' of '+ls.length+' trades done':'no work here'}</title>
   <rect class="rf" x="${r.x.toFixed(1)}" y="${r.y.toFixed(1)}" width="${r.w.toFixed(1)}" height="${r.h.toFixed(1)}" ${fill?`style="fill:${fill}"`:''}/><rect class="rb" x="${r.x.toFixed(1)}" y="${r.y.toFixed(1)}" width="${r.w.toFixed(1)}" height="${r.h.toFixed(1)}"/>
   ${out?`<path class="pt" d="${CIRC(r.x+r.w-22,r.y+24,9)}${CIRC(r.x+r.w-44,r.y+r.h-22,7)}"/>`:`<path class="pt" d="${door}${win}"/>`}
   ${tl.map((t,k)=>`<text class="pn" x="${(r.x+8).toFixed(1)}" y="${(r.y+17+k*10.500).toFixed(1)}">${esc(t.length>per+2?t.slice(0,per+1)+'…':t)}</text>`).join('')}
   ${dots(ls,r.x+11,yb-(r.bot&&!r.top?11:24))}${ls.length?`<text class="pc" x="${(r.x+r.w-8).toFixed(1)}" y="${(yb-8).toFixed(1)}">${done}/${ls.length}</text>`:''}
   ${st==='done'?`<path class="pk" d="M${cx-6} ${r.y+r.h/2+2}l4.500 4.500 9-10"/>`:''}${op?`<circle class="kc" cx="${(r.x+r.w-13).toFixed(1)}" cy="${(r.y+13).toFixed(1)}" r="8"/><text class="kt" x="${(r.x+r.w-13).toFixed(1)}" y="${(r.y+16.200).toFixed(1)}">${op}</text>`:''}</g>`}).join('');
 let site='';if(ws){const ls=linesOf(ws),done=ls.filter(l=>l.st==='done').length,y=bot+12;
  site=`<g class="rm ws ${roomState(ls)}" ${ls.length?act(ws):''}><rect class="sb" x="6" y="6" width="348" height="${(bot+2).toFixed(1)}" rx="3"/><rect class="rf" x="16" y="${y}" width="${Math.max(150,96+ls.length*9+34)}" height="26" rx="13"/>
   <text class="pn" x="28" y="${y+16.500}">WHOLE SITE</text>${dots(ls,100,y+13)}<text class="pc" x="${Math.max(150,96+ls.length*9+34)+6}" y="${y+16.500}">${done}/${ls.length}</text></g>`}
 return `<div class="planw"><svg class="plan2" viewBox="0 0 360 ${H.toFixed(0)}" role="group" aria-label="Plan of ${esc(p.name)}"><defs>
   <pattern id="${id}w" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect class="hb w" width="6" height="6"/><path class="hl w" d="M0 0V6"/>${RM()?'':'<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="6 0" dur="1.5s" repeatCount="indefinite" additive="sum"/>'}</pattern>
   <pattern id="${id}a" width="7" height="7" patternUnits="userSpaceOnUse"><rect class="hb a" width="7" height="7"/><circle class="hd a" cx="2" cy="2" r="1"/></pattern></defs>
  ${site}${rs.length?`<rect class="ow" x="16" y="16" width="328" height="${(bot-16).toFixed(1)}"/>`:''}${rooms}
  <g class="pnorth" transform="translate(334 ${(H-24).toFixed(0)})"><path d="M0 14V-6M-5 2 0-8 5 2"/><text x="0" y="-11">N</text></g><text class="nts" x="318" y="${(H-10).toFixed(0)}">N.T.S.</text></svg></div>`}
const planLegend=()=>`<div class="legend"><span><i class="sw done"></i>done</span><span><i class="sw work"></i>working</span><span><i class="sw wait"></i>waiting</span><span><i class="sw ns"></i>not started</span><span><i class="sw und"></i>agency undecided</span><span><b class="kn sm">2</b>open points</span></div>`;

/* ---------- sheets and keynotes ---------- */
const sht=(d,cls)=>{const r=cur(d);return `<span class="sht ${cls||''}">${planSVG(d)}<b class="sht-no">${sheetNo(d)}</b>${d.st==='released'||r.n>1?`<i class="rev" title="revision ${r.n}">${r.n}</i>`:''}</span>`};
const kn=(n,cls)=>`<span class="kn ${cls||''}">${n}</span>`;
