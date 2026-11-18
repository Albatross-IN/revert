/* Core: helpers, icons, store, the project picture and the operations every screen calls. */
let BASE=Date.UTC(2026,10,18);const MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],DOW=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
const dt=o=>new Date(BASE+o*864e5);
const fd=o=>{const d=dt(o);return d.getUTCDate()+' '+MON[d.getUTCMonth()]};
const fdw=o=>DOW[dt(o).getUTCDay()]+' '+fd(o);
const dueW=o=>o==null?'no date':o===0?'today':o===1?'tomorrow':o===-1?'yesterday':o>1&&o<7?DOW[dt(o).getUTCDay()]:fd(o);
const days=n=>n<=0?'today':n===1?'1 day':n+' days';
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const inr=n=>'₹'+Math.round(n||0).toLocaleString('en-IN');
const plural=(n,w,pl)=>n+' '+(n===1?w:(pl||w+'s'));
let NOW='10:42 am';

const IC={home:'<path d="m3 11 9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',folder:'<path d="M3 6a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>',
 dwg:'<path d="M3 21 14 3l3 5-8 13z"/><path d="M9 21h12M7 14h6"/>',mom:'<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 2h6v4H9zM9 11h6M9 15h4"/>',
 bill:'<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',review:'<path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-6"/>',setup:'<path d="M4 6h10M18 6h2M4 12h3M11 12h9M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
 check:'<path d="m5 12 5 5 9-10"/>',x:'<path d="M6 6l12 12M18 6 6 18"/>',plus:'<path d="M12 5v14M5 12h14"/>',chev:'<path d="m9 6 6 6-6 6"/>',back:'<path d="m15 6-6 6 6 6"/>',down:'<path d="m6 9 6 6 6-6"/>',
 send:'<path d="m21 3-9 18-3-8-8-3z"/>',wa:'<path d="M4 20l1.4-4.2A8 8 0 1 1 8.3 18.6z"/><path d="M9 9c.4 2.4 2.6 4.6 5 5l1.2-1.3 1.8.9-.5 1.6c-3.6.4-8.3-4-8-8.2l1.6-.4.8 1.8z" stroke-width="1.2"/>',
 cam:'<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',alert:'<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h0"/>',
 pause:'<path d="M9 5v14M15 5v14"/>',play:'<path d="M7 4v16l13-8z"/>',eye:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 file:'<path d="M14 3H6v18h12V7z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',user:'<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',users:'<circle cx="9" cy="8" r="3.5"/><path d="M2 21a7 7 0 0 1 14 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14.5a6 6 0 0 1 4 6.5"/>',
 bell:'<path d="M6 9a6 6 0 0 1 12 0c0 6 3 8 3 8H3s3-2 3-8M10 21h4"/>',phone:'<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',lock:'<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 link:'<path d="M10 14a4 4 0 0 0 6 0l3-3a4 4 0 0 0-6-6l-1 1M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 0 0 6 6l1-1"/>',search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',grid:'<path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/>',
 more:'<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>',mic:'<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
 off:'<path d="M3 3l18 18M8.5 16.5a5 5 0 0 1 7 0M5 13a10 10 0 0 1 3-2M19 13a10 10 0 0 0-5-2.7M2 9a15 15 0 0 1 4-2.6M22 9a15 15 0 0 0-9-3.9M12 20h0"/>',
 rupee:'<path d="M7 4h10M7 9h10M7 14l8 7M7 14h3a5 5 0 0 0 0-10"/>',globe:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',edit:'<path d="M4 20h4L20 8l-4-4L4 16z"/>',
 pin:'<path d="M12 22s7-6.5 7-12a7 7 0 0 0-14 0c0 5.500 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',flag:'<path d="M5 22V4h12l-2 4 2 4H5"/>',refresh:'<path d="M20 12a8 8 0 1 1-2.500-5.800L20 8M20 3v5h-5"/>',
 list:'<path d="M8 6h12M8 12h12M8 18h12M4 6h0M4 12h0M4 18h0"/>',out:'<path d="M10 4H5v16h5M15 8l4 4-4 4M19 12H9"/>',star:'<path d="m12 3 2.700 5.700 6.300.800-4.600 4.300 1.200 6.200L12 17l-5.600 3 1.200-6.200L3 9.500l6.300-.800z"/>',
 hand:'<path d="M8 12V5a1.500 1.500 0 0 1 3 0v6M11 10V4a1.500 1.500 0 0 1 3 0v6M14 10V6a1.500 1.500 0 0 1 3 0v8a7 7 0 0 1-7 7c-3 0-4.500-1.500-6-4l-2-3.500a1.500 1.500 0 0 1 2.500-1.500L8 14"/>',
 info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h0"/>',layers:'<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',tool:'<path d="M14 6a4 4 0 0 0 5 5l-9 9a2 2 0 0 1-3-3z"/><path d="M14 6l3-3 4 4-3 3"/>'};
IC.sun='<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.900 4.900l1.400 1.400M17.700 17.700l1.400 1.400M2 12h2M20 12h2M4.900 19.100l1.400-1.400M17.700 6.300l1.400-1.400"/>';IC.moon='<path d="M20 14.500A8 8 0 1 1 9.500 4a6.500 6.500 0 0 0 10.500 10.500z"/>';
const ic=(n,c)=>`<svg class="i ${c||''}" viewBox="0 0 24 24" aria-hidden="true">${IC[n]||IC.info}</svg>`;

/* ---------- store ---------- */
let DB=seed();
const newDev=(id,phone)=>({id,phone,f:{},sheet:null,sec:'today',pid:1,ptab:'picture',nt:'revert',stack:[{s:'today'}],signed:false});
const UI={theme:'light',pal:'emerald',jump:0,view:'desk',user:'s3',agency:'a5',clientPid:1,lang:{agency:'gu',client:'en'},offline:false,outbox:[],linkMode:false,panel:null,guide:0,
 devs:{desk:newDev('desk',false),staff:newDev('staff',true),agency:newDev('agency',true),client:newDev('client',true),wa:newDev('wa',true)}};
UI.devs.agency.stack=[{s:'home'}];UI.devs.client.stack=[{s:'home'}];UI.devs.wa.chat=null;

const pOf=id=>DB.projects.find(p=>p.id==id);
const stf=id=>DB.staff.find(s=>s.id===id)||{n:'Office',roles:[]};
const agOf=id=>DB.agencies.find(a=>a.id===id);
const agN=id=>(agOf(id)||{n:'Undecided'}).n;
const me=()=>stf(UI.user);
const has=(u,r)=>u.roles.includes(r);
const isOwner=()=>has(me(),'owner');
const isPrincipal=()=>has(me(),'principal')||has(me(),'owner');
const planOf=(p,t)=>p.plan.find(x=>x.t===t);
const lineAg=(p,l)=>l.ag||(planOf(p,l.t)||{}).ag||null;
const entN=(p,id)=>(p.ents.find(e=>e.id===id)||{n:''}).n;
const dOf=id=>DB.drawings.find(d=>d.id===id);
const sheetNo=d=>d.code+'-'+String(d.no).padStart(2,'0');
const cur=d=>d.revs[d.revs.length-1];
const ptOf=id=>DB.points.find(x=>x.id===id);
const billOf=id=>DB.bills.find(b=>b.id===id);
const visOf=id=>DB.visits.find(v=>v.id===id);
const paid=b=>b.pay.reduce((s,x)=>s+x.amount,0);
const roleLabel=u=>u.roles.map(r=>({owner:'Owner',principal:'Principal',designer:'Designer',coordinator:'Coordinator'}[r])).join(' · ');
const partyName=(p,x)=>x.kind==='agency'?agN(x.party):x.kind==='client'?p.client.n:x.kind==='staff'?stf(x.party).n:x.party;
const partyKey=x=>x.kind==='agency'?x.party:x.kind==='client'?'client':x.kind==='staff'?x.party:'v:'+x.party;
/* who may see a project: owners and the principal see all; others by team; a project not yet onboarded stays visible as today */
let canSee=(u,p)=>has(u,'owner')||has(u,'principal')||!p.onb||p.designers.includes(u.id)||p.coords.includes(u.id);
const myProjects=()=>DB.projects.filter(p=>canSee(me(),p));
const agProjects=a=>DB.projects.filter(p=>p.onb&&p.plan.some(x=>x.ag===a)||p.lines.some(l=>l.ag===a));

const LS={ns:['Not started','ns'],wait:['Waiting','wait'],work:['Working','work'],done:['Done','done']};
const DS={to_draw:['To draw','plain'],in_progress:['In progress','work'],awaiting:['Awaiting approval','wait'],approved:['Approved · to release','gold'],released:['Released','ok']};
const BS={asked:['Asked','plain'],submitted:['Submitted','work'],returned:['Returned','bad'],accepted:['Accepted','gold'],part_paid:['Part paid','wait'],paid:['Paid','ok']};
const STATUS={ok:['On track','ok'],attention:['Needs attention','wait'],stuck:['Stuck','bad']};
const CAUSE={drawing:'a drawing',client:'the client',trade:'another trade',material:'material',other:'another cause'};

/* ---------- the project picture: computed on reading, nothing stored (phase1_adoption §5.10, §7.1) ---------- */
function waitText(p,l){if(l.cause==='drawing'){const d=dOf(l.ref);return d?sheetNo(d)+' '+d.title:'a drawing'}
 if(l.cause==='client'){const d=dOf(l.ref),x=ptOf(l.ref);return 'client: '+(d?'approve '+d.title:x?x.text:'a decision')}
 if(l.cause==='trade')return (TX[l.ref]||{n:'another trade'}).n+(planOf(p,l.ref)&&planOf(p,l.ref).ag?' ('+agN(planOf(p,l.ref).ag)+')':'');
 return (l.cause==='material'?'material':'other')+(l.note?': '+l.note:'')}
function picture(p){
 const lim=DB.set.lim,L=p.lines,dws=DB.drawings.filter(d=>d.pid===p.id),rel=dws.filter(d=>d.st==='released');
 const pts=DB.points.filter(x=>x.pid===p.id),bills=DB.bills.filter(b=>b.pid===p.id),office=[...p.coords];
 const B=[],lineLabel=l=>entN(p,l.e)+' · '+TX[l.t].n;
 const push=b=>B.push(b);
 /* B1 a trade is undecided past its decide-by date */
 p.plan.filter(x=>!x.ag&&x.by!=null&&x.by<0).forEach(x=>push({k:'B1',crit:true,text:TX[x.t].n+' agency undecided',holds:plural(L.filter(l=>l.t===x.t).length,'work line'),actor:p.coords.map(s=>stf(s).n).join(', ')||'Coordinator',who:p.coords,age:-x.by,act:['assign',p.id+'|'+x.t,'Assign']}));
 /* B2 a work line waits for a drawing · B3 a required drawing is past its due date and not released */
 dws.filter(d=>d.st!=='released').forEach(d=>{const w=L.filter(l=>l.st==='wait'&&l.cause==='drawing'&&l.ref===d.id);if(!w.length&&d.due>=0)return;
  const age=Math.max(-d.due,...w.map(l=>l.since||0),0),appr=d.st==='awaiting',ag=d.t&&planOf(p,d.t)&&planOf(p,d.t).ag;
  push({k:w.length?'B2':'B3',text:sheetNo(d)+' '+d.title+' not released',holds:w.length?plural(w.length,'work line')+' waiting'+(ag?' · '+agN(ag):''):'lines of '+(d.t?TX[d.t].n:'all trades'),
   actor:appr?stf(p.principal).n+' (approve)':stf(d.ds).n,who:[appr?p.principal:d.ds],age,act:appr?['approve',d.id,'Approve']:d.st==='approved'?['release',d.id,'Release']:['dwg',d.id,'Open']})});
 /* B4 a client item is open past its date */
 rel.forEach(d=>{const r=cur(d);if(r.client&&r.client.dec==='pending'&&-r.relOn>=2){const w=L.filter(l=>l.st==='wait'&&l.cause==='client'&&l.ref===d.id);
  push({k:'B4',text:'Client: approve '+d.title+' rev '+r.n,holds:w.length?w.map(lineLabel).join(', '):'the drawings that follow it',actor:p.client.n,who:p.coords,age:-r.relOn,act:['remind','client|'+p.id+'|Please have a look at '+d.title+' and give your go-ahead.','Remind']})}});
 pts.filter(x=>x.kind==='client'&&x.st==='open'&&x.confirmed&&x.due<0).forEach(x=>push({k:'B4',text:'Client: '+x.text,holds:entN(p,x.e)||'the site',actor:p.client.n,who:p.coords,age:-x.due,act:['remind','client|'+p.id+'|'+x.text,'Remind']}));
 /* B5 waits for another trade · B6 waits for material or another cause */
 L.filter(l=>l.st==='wait'&&['trade','material','other'].includes(l.cause)).forEach(l=>{const tr=l.cause==='trade',ag=tr&&planOf(p,l.ref)&&planOf(p,l.ref).ag;
  push({k:tr?'B5':'B6',text:lineLabel(l)+' waits for '+waitText(p,l),holds:'this line',actor:tr?(ag?agN(ag):TX[l.ref].n):p.coords.map(s=>stf(s).n)[0]||'Coordinator',who:p.coords,age:l.since||0,act:tr&&ag?['remind',ag+'|'+p.id+'|'+entN(p,l.e)+': '+TX[l.t].n+' is waiting for your work.','Remind']:['cell',p.id+'|'+l.id,'Open']})});
 /* B7 a MOM point is past its due date */
 pts.filter(x=>x.kind!=='client'&&x.st==='open'&&x.due<0).forEach(x=>push({k:'B7',text:partyName(p,x)+': point '+x.n+' past its date',sub:x.text,holds:(entN(p,x.e)||'the site')+(x.t?' · '+TX[x.t].n:''),actor:partyName(p,x),who:p.coords,age:-x.due,
  act:x.kind==='agency'?['remind',x.party+'|'+p.id+'|Point '+x.n+': '+x.text,'Remind']:['closept',x.id,'Close']}));
 /* B8 a released drawing is not opened by an agency after N days */
 rel.forEach(d=>cur(d).rc.filter(r=>r.to!=='client'&&r.opened==null&&-r.sent>=lim.open).forEach(r=>push({k:'B8',text:agN(r.to)+' has not opened '+sheetNo(d)+' '+d.title,holds:'its '+(d.t?TX[d.t].n:'')+' lines',actor:(stf(p.coords[0]).n)+' (chase)',who:p.coords,age:-r.sent,act:['remind',r.to+'|'+p.id+'|Please open '+sheetNo(d)+' '+d.title+'.','Remind']})));
 /* B9 a question on a drawing is unanswered after N working days */
 dws.forEach(d=>d.q.filter(q=>!q.ans&&-q.on>lim.q-1&&-q.on>=lim.q).forEach(q=>push({k:'B9',text:'Question on '+sheetNo(d)+' unanswered',sub:'“'+q.text+'” · '+q.byName,holds:q.by==='client'?'the client':agN(q.by)+'’s lines',actor:stf(d.ds).n,who:[d.ds],age:-q.on,act:['dwg',d.id,'Answer']})));
 /* B10 a bill is submitted and not reviewed after N days */
 bills.filter(b=>b.st==='submitted'&&-b.subOn>=lim.bill).forEach(b=>push({k:'B10',text:'Bill from '+agN(b.ag)+' not reviewed',holds:b.what,actor:'Office',who:office,age:-b.subOn,act:['bill',b.id,'Review']}));
 B.sort((a,b)=>(b.crit?999:b.age)-(a.crit?999:a.age));

 const N={revert:[],agencies:[],client:[]},R=o=>N.revert.push(Object.assign({pid:p.id},o));
 dws.forEach(d=>{const w=L.filter(l=>l.st==='wait'&&l.cause==='drawing'&&l.ref===d.id),ag=d.t&&planOf(p,d.t)&&planOf(p,d.t).ag,wt=w.length?(ag?agN(ag):plural(w.length,'line'))+' waiting · '+days(Math.max(...w.map(l=>l.since||0))):'';
  if(d.st==='to_draw'||d.st==='in_progress'){const ch=d.revs.length>1;R({sec:ch?'change':'draw',who:[d.ds],whoN:stf(d.ds).n,text:(ch?'Revise ':'Draw and send ')+sheetNo(d)+' '+d.title,sub:'due '+dueW(d.due)+(ch?' · client asked for a change':''),warn:wt,late:d.due<0,act:['dwg',d.id,'Open']})}
  if(d.st==='awaiting')R({sec:'approve',who:[p.principal],whoN:stf(p.principal).n,text:'Approve '+sheetNo(d)+' '+d.title+' rev '+cur(d).n,sub:'sent by '+stf(cur(d).sentBy).n+' · '+(cur(d).sentOn===0?'today':fd(cur(d).sentOn)),warn:wt,act:['approve',d.id,'Approve']});
  if(d.st==='approved')R({sec:'release',who:[d.ds,p.principal],whoN:stf(d.ds).n,text:'Release '+sheetNo(d)+' '+d.title+' rev '+cur(d).n,sub:'approved by '+stf(cur(d).apprBy).n,warn:wt,act:['release',d.id,'Release']});
  d.q.filter(q=>!q.ans).forEach(q=>R({sec:'question',who:[d.ds],whoN:stf(d.ds).n,text:'Answer on '+sheetNo(d)+' '+d.title,sub:'“'+q.text+'” · '+q.byName+(q.photo?' · photo':''),late:-q.on>=lim.q,act:['dwg',d.id,'Answer']}))});
 p.plan.filter(x=>!x.ag).forEach(x=>R({sec:'decide',who:p.coords,whoN:p.coords.map(s=>stf(s).n)[0]||'Coordinator',text:'Decide the '+TX[x.t].n.toLowerCase()+' agency',sub:x.by!=null?'decide by '+fd(x.by)+' · holds '+plural(L.filter(l=>l.t===x.t).length,'line'):'',late:x.by!=null&&x.by<0,act:['assign',p.id+'|'+x.t,'Assign']}));
 bills.filter(b=>b.st==='submitted').forEach(b=>R({sec:'bill',who:office,whoN:'Office',text:'Review the bill from '+agN(b.ag),sub:b.what+' · submitted '+fd(b.subOn),late:-b.subOn>=lim.bill,act:['bill',b.id,'Review']}));
 pts.filter(x=>x.kind==='client'&&x.st==='open'&&!x.confirmed).forEach(x=>R({sec:'confirm',who:office,whoN:'Office',text:'Confirm client point '+x.n+' before the client sees it',sub:x.text,act:['confirmpt',x.id,'Confirm']}));
 pts.filter(x=>x.kind==='staff'&&x.st==='open').forEach(x=>R({sec:'point',who:[x.party],whoN:stf(x.party).n,text:x.text,sub:'point '+x.n+' · by '+dueW(x.due),late:x.due<0,act:['closept',x.id,'Close']}));
 rel.forEach(d=>cur(d).rc.filter(r=>r.to!=='client'&&r.opened==null&&-r.sent>=lim.open).forEach(r=>R({sec:'chase',who:p.coords,whoN:p.coords.map(s=>stf(s).n)[0]||'Coordinator',text:'Chase '+agN(r.to)+' to open '+sheetNo(d),sub:'released '+days(-r.sent)+' ago, not opened',late:true,act:['remind',r.to+'|'+p.id+'|Please open '+sheetNo(d)+' '+d.title+'.','Remind']})));
 [...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))].forEach(a=>{const ls=L.filter(l=>lineAg(p,l)===a),op=pts.filter(x=>x.kind==='agency'&&x.party===a&&x.st==='open'),od=op.filter(x=>x.due<0).length,c=s=>ls.filter(l=>l.st===s).length;
  const un=rel.filter(d=>cur(d).rc.some(r=>r.to===a&&r.opened==null)),w=ls.find(l=>l.st==='wait'),nx=op.slice().sort((x,y)=>x.due-y.due)[0];
  N.agencies.push({ag:a,name:agN(a),trades:p.plan.filter(x=>x.ag===a).map(x=>TX[x.t].n).join(', '),pts:op.length,od,lines:ls.length,done:c('done'),work:c('work'),wait:c('wait'),
   sub:un.length?'has not opened '+un.map(sheetNo).join(', '):w?'waiting for '+waitText(p,w):nx?'next: '+nx.text+', by '+dueW(nx.due):c('work')?plural(c('work'),'line')+' in hand':'',unopened:un.length,
   rem:un.length?'Please open '+un.map(d=>sheetNo(d)+' '+d.title).join(', ')+'.':nx?'Point '+nx.n+': '+nx.text+' (by '+dueW(nx.due)+')':'Please share where the work stands at '+p.name+'.'})});
 rel.forEach(d=>{const r=cur(d);if(r.client&&r.client.dec==='pending')N.client.push({text:'Approve '+d.title+' rev '+r.n,sub:'sent '+days(-r.relOn)+' ago',late:-r.relOn>=2,rem:'Please have a look at '+d.title+' and give your go-ahead.',dwg:d.id})});
 pts.filter(x=>x.kind==='client'&&x.st==='open'&&x.confirmed).forEach(x=>N.client.push({text:x.text,sub:'by '+dueW(x.due),late:x.due<0,rem:x.text,pt:x.id}));

 const apply=L.length,done=L.filter(l=>l.st==='done').length,working=L.filter(l=>l.st==='work').length,waiting=L.filter(l=>l.st==='wait').length;
 const closed=pts.filter(x=>x.st==='closed').length,open=pts.filter(x=>x.st==='open'),tradesWithRel=new Set(rel.map(d=>d.t));
 const noDwg=L.filter(l=>l.st==='work'&&dws.some(d=>d.t===l.t)&&!tradesWithRel.has(l.t));
 const status=!p.onb?'ok':B.some(b=>b.crit||b.age>=lim.stuck)?'stuck':B.length?'attention':'ok';
 return {progress:{ag:[p.plan.filter(x=>x.ag).length,p.plan.length],dr:[rel.length,dws.length],wk:[done,apply,working,waiting],pt:[closed,pts.length,open.length,open.filter(x=>x.due<0).length]},
  week:{rel:rel.filter(d=>cur(d).relOn>-7).length,started:L.filter(l=>l.startOn!=null&&l.startOn>-7).length,done:L.filter(l=>l.doneOn!=null&&l.doneOn>-7).length,closed:pts.filter(x=>x.st==='closed'&&x.closedOn>-7).length},
  blockers:B,next:N,status,noDwg};
}
/* Today: the same items, filtered to the signed-in person, across projects */
function todayFor(u){const out=[];DB.projects.filter(p=>p.onb&&canSee(u,p)).forEach(p=>{const pic=picture(p);
  pic.next.revert.forEach(n=>{if(n.who.includes(u.id)||(n.whoN==='Office'&&has(u,'owner')))out.push(Object.assign({p},n))});
  if(p.coords.includes(u.id))pic.next.client.filter(n=>n.late).forEach(n=>out.push({p,pid:p.id,sec:'client',text:'Chase '+p.client.n+': '+n.text,sub:n.sub,late:true,act:['remind','client|'+p.id+'|'+n.rem,'Remind']}))});
 return out}
const SECC={approve:'brz',draw:'work',change:'wait',release:'ok',question:'work',decide:'bad',confirm:'wait',bill:'brz',chase:'ok',client:'work',point:'brz'};
const SECS=[['approve','To approve','check'],['draw','To draw','dwg'],['change','Change asked','edit'],['release','To release','send'],['question','Questions','info'],['decide','Agencies to decide','users'],['confirm','Client points to confirm','eye'],['bill','Bills to review','bill'],['chase','To chase','wa'],['client','Waiting on a client','user'],['point','My open points','mom']];

/* ---------- messages (rvt.notify): only this function sends ---------- */
const TPL={
 drawing_released:{en:'New drawing · {site}: {sheet} {title} · rev {rev}. Tap the link to open.',gu:'નવું ડ્રોઇંગ · {site}: {sheet} {title} · રિવિઝન {rev}. ખોલવા માટે લિંક દબાવો.',hi:'नई ड्रॉइंग · {site}: {sheet} {title} · रिविज़न {rev}. खोलने के लिए लिंक दबाएँ।'},
 drawing_client:{en:'{site}: your {title} (rev {rev}) is ready. Please have a look and give your go-ahead.',gu:'{site}: તમારું {title} (રિવિઝન {rev}) તૈયાર છે. કૃપા કરીને જોઈને મંજૂરી આપશો.',hi:'{site}: आपकी {title} (रिविज़न {rev}) तैयार है। कृपया देखकर मंज़ूरी दें।'},
 mom_party_pdf:{en:'MOM · {site} · Visit {no} · {date}: {count} for you. PDF attached.',gu:'મિનિટ્સ · {site} · મુલાકાત {no} · {date}: તમારા માટે {count}. PDF જોડેલ છે.',hi:'MOM · {site} · विज़िट {no} · {date}: आपके लिए {count}. PDF संलग्न है।'},
 client_item:{en:'{site}: we need your go-ahead on “{text}”, by {date}.',gu:'{site}: “{text}” માટે આપની મંજૂરી જોઈએ છે, {date} સુધીમાં.',hi:'{site}: “{text}” के लिए आपकी मंज़ूरी चाहिए, {date} तक।'},
 bill_asked:{en:'Please upload your bill · {site} · {what}.',gu:'કૃપા કરીને તમારું બિલ અપલોડ કરો · {site} · {what}.',hi:'कृपया अपना बिल अपलोड करें · {site} · {what}.'},
 bill_returned:{en:'Your bill for {site} needs a correction: {reason}',gu:'{site} ના બિલમાં સુધારો જોઈએ છે: {reason}',hi:'{site} के बिल में सुधार चाहिए: {reason}'},
 bill_accepted:{en:'Your bill for {site} ({what}) is accepted.',gu:'{site} નું તમારું બિલ ({what}) સ્વીકારાયું છે.',hi:'{site} का आपका बिल ({what}) स्वीकार हो गया है।'},
 bill_paid:{en:'Payment recorded on your bill · {site} · {what}: {state}.',gu:'તમારા બિલ પર ચુકવણી નોંધાઈ · {site} · {what}: {state}.',hi:'आपके बिल पर भुगतान दर्ज हुआ · {site} · {what}: {state}.'},
 invite:{en:'{site}: Revert has added you. Open the app with this number to see your drawings and points.',gu:'{site}: Revert એ તમને ઉમેર્યા છે. તમારા ડ્રોઇંગ અને મુદ્દા જોવા આ નંબરથી એપ ખોલો.',hi:'{site}: Revert ने आपको जोड़ा है। अपनी ड्रॉइंग और बिंदु देखने के लिए इस नंबर से ऐप खोलें।'},
 remind:{en:'Reminder · {site}: {text}',gu:'યાદ અપાવવા · {site}: {text}',hi:'याद दिलाने के लिए · {site}: {text}'},
 otp:{en:'{code} is your Revert sign-in code. It is valid for 10 minutes.',gu:'{code} તમારો Revert સાઇન-ઇન કોડ છે. 10 મિનિટ માટે માન્ય.',hi:'{code} आपका Revert साइन-इन कोड है। 10 मिनट के लिए मान्य।'}};
function notify(ev,to,vars,doc){ /* to: agency id | 'client:<pid>' */
 let name,ph,lang='en';
 if(String(to).startsWith('client:')){const p=pOf(to.split(':')[1]),c=p.client.contacts[0];name=c.n;ph=c.ph;lang=UI.lang.client==='gu'?'gu':'en'}
 else{const a=agOf(to);if(!a)return;name=a.n;ph=a.people[0].ph;lang=a.lang}
 const t=(TPL[ev]||{})[lang]||(TPL[ev]||{}).en||'{text}';
 DB.wa.unshift({to,name,ph,text:t.replace(/\{(\w+)\}/g,(m,k)=>vars[k]!=null?vars[k]:''),doc:doc||null,on:0,at:NOW,ev,held:!DB.set.sending,fresh:true});
 if(DB.set.sending){const tx=DB.wa[0].text;if(to===UI.agency&&UI.devs.agency.signed)push('agency','Revert Architects',tx);if(String(to)==='client:'+UI.clientPid&&(UI.devs.client.signed||UI.linkMode))push('client','Revert Architects',tx)}
}
/* push: the same events also reach the phone as a notification (FCM in the app) */
function push(id,title,text){const d=UI.devs[id];d.push={t:title,x:text};clearTimeout(d.pt);d.pt=setTimeout(()=>{d.push=null;document.querySelectorAll('.dv-'+id+' .pushb').forEach(e=>e.remove())},4200)}
function pushStaff(text,who){if(UI.devs.staff.signed&&(who.includes(UI.user)||isOwner()))push('staff','Revert',text)}

/* ---------- operations (each one maps to a model method in the plan) ---------- */
const OP={
 setLine(p,l,st,x){x=x||{};const was=l.st;Object.assign(l,{st,cause:st==='wait'?x.cause:null,ref:st==='wait'?x.ref||null:null,note:st==='wait'?x.note||'':'',since:st==='wait'?0:null});
  if(st==='work'&&was!=='work')l.startOn=0;if(st==='done')l.doneOn=0;else l.doneOn=null},
 assign(p,t,ag,by){const pl=planOf(p,t);pl.ag=ag||null;pl.by=ag?null:(by==null?7:by);pl.people=ag?[0]:[]},
 sendForApproval(d,note){const r=cur(d);r.note=note||r.note;r.sentBy=UI.user;r.sentOn=0;r.file=true;
  if(DB.set.approval){r.st='awaiting';d.st='awaiting'}else{r.st='approved';r.apprBy=UI.user;r.apprOn=0;d.st='approved'}},
 approve(d){const r=cur(d);r.st='approved';r.apprBy=UI.user;r.apprOn=0;d.st='approved'},
 sendBack(d,note){const r=cur(d);r.st='draft';r.back=note;d.st='in_progress'},
 release(d,to){const p=pOf(d.pid),r=cur(d);d.revs.slice(0,-1).forEach(x=>{if(x.st==='released')x.st='superseded'});
  Object.assign(r,{st:'released',relBy:UI.user,relOn:0,rc:to.map(k=>({to:k,sent:0,opened:null})),client:to.includes('client')&&d.needsApproval?{dec:'pending'}:null});d.st='released';
  to.forEach(k=>{const doc={k:'dwg',id:d.id,label:sheetNo(d)+' '+d.title+' · rev '+r.n};
   if(k==='client')notify('drawing_client','client:'+p.id,{site:p.name,title:d.title,rev:r.n},doc);else notify('drawing_released',k,{site:p.name,sheet:sheetNo(d),title:d.title,rev:r.n},doc)});
  const freed=p.lines.filter(l=>l.st==='wait'&&l.cause==='drawing'&&l.ref===d.id);freed.forEach(l=>OP.setLine(p,l,'ns'));return freed.length},
 open(d,who){const r=cur(d).rc.find(x=>x.to===who);if(r&&r.opened==null){r.opened=0;r.at=NOW;return true}return false},
 clientDecide(d,dec,note,name){const p=pOf(d.pid),r=cur(d);r.client={dec,by:name,on:0,at:NOW,note:note||''};
  if(dec==='approved')p.lines.filter(l=>l.st==='wait'&&l.cause==='client'&&l.ref===d.id).forEach(l=>OP.setLine(p,l,'ns'));
  else{d.revs.push({n:r.n+1,st:'draft',note:'Change asked by the client: '+note,rc:[]});d.st='in_progress';d.due=Math.max(d.due,3)}},
 ask(d,by,byName,text,photo,via){d.q.push({id:'q'+(++DB.seq.q),by,byName,via:via||'app',text,photo:!!photo,on:0,ans:null})},
 answer(d,qid,text){const q=d.q.find(x=>x.id===qid);q.ans=text;q.ansBy=UI.user;q.ansOn=0},
 addPoint(o){const p=pOf(o.pid),n=Math.max(0,...DB.points.filter(x=>x.pid===p.id).map(x=>x.n))+1;
  const x=Object.assign({id:'pt'+(++DB.seq.ptid),n,vid:null,t:null,e:null,dwg:null,photo:false,st:'open',closedBy:null,closedOn:null,note:'',sent:0,fresh:true,by:UI.user,pending:false},o);
  x.confirmed=x.kind!=='client'||!DB.set.clientConfirm;if(x.kind==='agency'&&!x.t){const pl=p.plan.find(q=>q.ag===x.party);x.t=pl?pl.t:null}DB.points.push(x);return x},
 closePoint(x,note,photo,by){Object.assign(x,{st:'closed',closedBy:by||UI.user,closedOn:0,note:note||'',cphoto:!!photo})},
 confirmPoint(x){const p=pOf(x.pid);x.confirmed=true;x.sent=1;x.fresh=false;notify('client_item','client:'+p.id,{site:p.name,text:x.text,date:fd(x.due)})},
 sendParty(v,key){const p=pOf(v.pid),ps=DB.points.filter(x=>x.vid===v.id&&partyKey(x)===key&&x.st==='open');if(!ps.length)return 0;
  const fresh=ps.filter(x=>x.fresh).length;ps.forEach(x=>{x.sent++;x.fresh=false});
  if(agOf(key))notify('mom_party_pdf',key,{site:p.name,no:v.no,date:fd(v.date),count:plural(ps.length,'point')+(fresh&&fresh<ps.length?' ('+fresh+' new)':'')},{k:'mom',vid:v.id,party:key,label:'MOM · Visit '+v.no+' · '+agN(key)+'.pdf'});
  return ps.length},
 askBill(o){const p=pOf(o.pid),b=Object.assign({id:'b'+(++DB.seq.bid),askedBy:UI.user,askedOn:0,no:'',date:null,amount:null,billedTo:p.billedTo,st:'asked',subOn:null,reason:'',pay:[]},o);DB.bills.push(b);
  notify('bill_asked',b.ag,{site:p.name,what:b.what});return b},
 uploadBill(b,o){Object.assign(b,o,{st:'submitted',subOn:0,date:0,reason:''})},
 reviewBill(b,ok,reason){const p=pOf(b.pid);if(ok){b.st='accepted';notify('bill_accepted',b.ag,{site:p.name,what:b.what})}else{b.st='returned';b.reason=reason;notify('bill_returned',b.ag,{site:p.name,reason})}},
 pay(b,o){const p=pOf(b.pid);b.pay.push(Object.assign({on:0,proof:false},o));b.st=paid(b)>=b.amount?'paid':'part_paid';notify('bill_paid',b.ag,{site:p.name,what:b.what,state:BS[b.st][0]})},
 remind(to,pid,text){const p=pOf(pid);notify('remind',to==='client'?'client:'+pid:to,{site:p.name,text})},
};

/* ---------- words the agency and the client read (en · gu · hi). Gujarati and Hindi need a native check before release. ---------- */
const STR={
 hello:{en:'Hello',gu:'નમસ્તે',hi:'नमस्ते'},points:{en:'Your points',gu:'તમારા મુદ્દા',hi:'आपके बिंदु'},newdw:{en:'New drawings',gu:'નવા ડ્રોઇંગ',hi:'नई ड्रॉइंग'},asks:{en:'Revert asks',gu:'Revert ની વિનંતી',hi:'Revert का अनुरोध'},
 upload:{en:'Upload your bill',gu:'તમારું બિલ અપલોડ કરો',hi:'अपना बिल अपलोड करें'},home:{en:'Home',gu:'હોમ',hi:'होम'},sites:{en:'My sites',gu:'મારી સાઇટ',hi:'मेरी साइट'},drawings:{en:'Drawings',gu:'ડ્રોઇંગ',hi:'ड्रॉइंग'},bills:{en:'Bills',gu:'બિલ',hi:'बिल'},
 by:{en:'by',gu:'સુધીમાં',hi:'तक'},open:{en:'Open',gu:'ખોલો',hi:'खोलें'},allclear:{en:'Nothing pending right now.',gu:'અત્યારે કંઈ બાકી નથી.',hi:'अभी कुछ बाकी नहीं है।'},
 ask:{en:'Ask a question',gu:'પ્રશ્ન પૂછો',hi:'सवाल पूछें'},send:{en:'Send',gu:'મોકલો',hi:'भेजें'},rev:{en:'Revision',gu:'રિવિઝન',hi:'रिविज़न'},current:{en:'Current revision',gu:'હાલનું રિવિઝન',hi:'वर्तमान रिविज़न'},
 ns:{en:'Not started',gu:'શરૂ નથી',hi:'शुरू नहीं'},wait:{en:'Waiting',gu:'રાહ જોવાય છે',hi:'प्रतीक्षा में'},work:{en:'Working',gu:'કામ ચાલુ',hi:'काम चालू'},done:{en:'Done',gu:'પૂર્ણ',hi:'पूरा'},
 asked:{en:'Asked',gu:'માંગેલ',hi:'माँगा गया'},submitted:{en:'Submitted',gu:'મોકલેલ',hi:'भेजा गया'},returned:{en:'Returned',gu:'પરત',hi:'वापस'},accepted:{en:'Accepted',gu:'સ્વીકાર્ય',hi:'स्वीकृत'},part_paid:{en:'Part paid',gu:'અંશતઃ ચૂકવેલ',hi:'आंशिक भुगतान'},paid:{en:'Paid',gu:'ચૂકવેલ',hi:'भुगतान हुआ'},
 rooms:{en:'Your work here',gu:'અહીં તમારું કામ',hi:'यहाँ आपका काम'},amount:{en:'Bill amount',gu:'બિલની રકમ',hi:'बिल राशि'},billno:{en:'Bill number',gu:'બિલ નંબર',hi:'बिल नंबर'},photo:{en:'Photo of the bill',gu:'બિલનો ફોટો',hi:'बिल की फ़ोटो'},
 submit:{en:'Submit bill',gu:'બિલ મોકલો',hi:'बिल भेजें'},nobills:{en:'Bills appear here when Revert asks for one.',gu:'Revert બિલ માંગે ત્યારે અહીં દેખાશે.',hi:'Revert के माँगने पर बिल यहाँ दिखेंगे।'},
 lang:{en:'Language',gu:'ભાષા',hi:'भाषा'},signout:{en:'Sign out',gu:'સાઇન આઉટ',hi:'साइन आउट'},mobile:{en:'Mobile number',gu:'મોબાઇલ નંબર',hi:'मोबाइल नंबर'},getcode:{en:'Send code on WhatsApp',gu:'WhatsApp પર કોડ મોકલો',hi:'WhatsApp पर कोड भेजें'},
 code:{en:'Enter the 4-digit code',gu:'4 આંકડાનો કોડ લખો',hi:'4 अंकों का कोड लिखें'},signin:{en:'Sign in',gu:'સાઇન ઇન',hi:'साइन इन'},new:{en:'new',gu:'નવું',hi:'नया'},yourq:{en:'Your question',gu:'તમારો પ્રશ્ન',hi:'आपका सवाल'},
 reason:{en:'Reason',gu:'કારણ',hi:'कारण'},again:{en:'Upload again',gu:'ફરી અપલોડ કરો',hi:'फिर अपलोड करें'},waiting4:{en:'Waiting for',gu:'રાહ',hi:'प्रतीक्षा'},noq:{en:'Type your question',gu:'તમારો પ્રશ્ન લખો',hi:'अपना सवाल लिखें'},
 c_wait:{en:'Waiting for you',gu:'તમારી રાહ જોઈ રહ્યું છે',hi:'आपकी प्रतीक्षा में'},c_dw:{en:'Your drawings',gu:'તમારા ડ્રોઇંગ',hi:'आपकी ड्रॉइंग'},c_none:{en:'Nothing needed from you right now.',gu:'અત્યારે તમારી પાસેથી કંઈ જોઈતું નથી.',hi:'अभी आपसे कुछ नहीं चाहिए।'},
 c_approve:{en:'Approve',gu:'મંજૂર કરો',hi:'मंज़ूर करें'},c_change:{en:'Ask for a change',gu:'ફેરફાર માટે કહો',hi:'बदलाव के लिए कहें'},c_approved:{en:'Approved by you',gu:'તમે મંજૂર કર્યું',hi:'आपने मंज़ूर किया'},c_note:{en:'What would you like changed?',gu:'શું ફેરફાર કરવો છે?',hi:'क्या बदलना चाहेंगे?'},
 c_look:{en:'Please have a look',gu:'કૃપા કરીને જુઓ',hi:'कृपया देखें'},c_done:{en:'Mark as done',gu:'થઈ ગયું',hi:'हो गया'},c_hi:{en:'Welcome',gu:'સ્વાગત છે',hi:'स्वागत है'},c_sub:{en:'Your home, one step at a time.',gu:'તમારું ઘર, એક એક પગલે.',hi:'आपका घर, एक-एक क़दम।'}};
const tr=(k,l)=>(STR[k]||{})[l]||(STR[k]||{}).en||k;
