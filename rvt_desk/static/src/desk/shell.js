/* Shell: preview bar, stage, guide, the actions behind every button, rendering. */
const devOf=el=>{const d=el.closest('[data-dev]');return d?UI.devs[d.dataset.dev]:UI.devs.desk};
function toast(t,k){UI.toast={t,k:k||'ok'};clearTimeout(toast.h);toast.h=setTimeout(()=>{UI.toast=null;const el=document.getElementById('toast');if(el)el.innerHTML=''},4200)}
/* the splash plays over the first screen; that screen's own entrance waits for it (--sd in the stylesheet) */
function splash(dev,quick){dev.splash=quick?'quick':true;dev.spT=performance.now();dev._k='';clearTimeout(dev.sh);dev.sh=setTimeout(()=>{dev.splash=false;document.querySelectorAll('.dv-'+dev.id+' .splash').forEach(e=>e.remove())},quick?2900:5300)}
function flash(dev,t,i,party){dev.flash={t,i};if(i==='stamp'||party)dev.party=true;clearTimeout(dev.fh);dev.fh=setTimeout(()=>{dev.flash=null;document.querySelectorAll('.flash').forEach(e=>e.remove())},1600)}
const openSheet=(dev,k,o)=>{dev.sheet=Object.assign({k},o||{})};
const sent=()=>DB.set.sending?'sent on WhatsApp':DB.set.testcopy?(DB.set.testsend?'test copy: only its test numbers get it':'held: this is a test copy'):'held: sending is off in Setup';
function openProj(dev,pid,tab){dev.pid=+pid;if(tab)dev.ptab=tab;dev.vid='';if(dev.phone){if(!(top(dev).s==='project'&&top(dev).id==pid))dev.stack.push({s:'project',id:+pid})}else dev.sec='projects'}
function openDwg(dev,id){const d=dOf(id);if(dev.phone){if(!(top(dev).s==='dwg'&&top(dev).id===id))dev.stack.push({s:'dwg',id})}
 else{dev.sec='drawings';dev.drawer=id;dev.dmine='all';dev.dtab=d.st==='awaiting'?'awaiting':d.st==='approved'?'release':d.st==='released'?'released':'draw'}}
function relPrefill(dev,d){const p=pOf(d.pid),own=d.t&&planOf(p,d.t)&&planOf(p,d.t).ag;Object.keys(dev.f).filter(k=>k.startsWith('rc_')).forEach(k=>delete dev.f[k]);
 if(own)dev.f['rc_'+own]=true;else if(!d.t)p.plan.filter(x=>x.ag&&['carp','civ'].includes(x.t)).forEach(x=>dev.f['rc_'+x.ag]=true);if(d.forClient)dev.f.rc_client=true;openSheet(dev,'release',{id:d.id})}
function setPath(o,path,v){const ks=path.split('.');let x=o;ks.slice(0,-1).forEach(k=>x=x[k]);x[ks[ks.length-1]]=v}
const guessType=n=>{const s=n.toLowerCase();return /draw|living|hall/.test(s)?'Living room':/master/.test(s)?'Master bedroom':/bed/.test(s)?'Bedroom':/kitchen/.test(s)?'Kitchen':/pu?ja|pooja/.test(s)?'Pooja room':/toilet|bath/.test(s)?'Toilet':/cabin/.test(s)?'Cabin':ETX[n]?n:'Other room'};

const A={
 /* preview bar */
 setview(v){UI.view=v;UI.panel=null;UI.jump=-1},
 theme(){UI.theme=UI.theme==='dark'?'light':'dark';document.documentElement.dataset.rv=UI.theme},pal(v){UI.pal=v;document.documentElement.dataset.pal=v;toast({emerald:'Accent: emerald, from “vert” and Green Building.',indigo:'Accent: indigo, the blue of a blueprint.',plum:'Accent: plum.'}[v])},
 replay(){if(UI.view==='desk')intro();else ['staff','agency','client'].forEach(k=>splash(UI.devs[k]))},motion(){UI.motion=UI.motion==='on'?'':'on';document.documentElement.dataset.motion=UI.motion;if(UI.motion==='on')toast('Animations are on for this preview.')},
 jump(v){UI.jump=+v;RAIL[UI.view][+v][1]()},
 startq(v,el,dev){const it=todayFor(me())[0];if(!it)return;A[it.act[0]](it.act[1],el,dev)},
 quick(v,el,dev){const ps=myProjects();if(!ps.some(p=>String(p.id)===String(dev.f.q_pid)))dev.f.q_pid=String((ps.find(p=>p.onb)||ps[0]).id);openSheet(dev,'quick',{})},
 qgo(v,el,dev){const pid=dev.f.q_pid;dev.sheet=null;if(v==='mom')A.startmom(pid,el,dev);if(v==='raise')A.raise(pid,el,dev);if(v==='bill')A.askbill(pid,el,dev);if(v==='new')A.onb('',el,dev)},
 room(v,el,dev){const [pid,eid]=v.split('|');openSheet(dev,'room',{pid:+pid,eid})},
 raisehere(v,el,dev){const [pid,eid]=v.split('|');A.raise(pid,el,dev);dev.f.rp_area=eid},guide(){UI.panel=UI.panel==='guide'?null:'guide'},wapanel(){UI.panel=UI.panel==='wa'?null:'wa';DB.wa.forEach(m=>m.fresh=false)},closepanel(){UI.panel=null},
 reset(){DB=seed();mastersApply(JSON.parse(M0));SCROLL={};try{localStorage.removeItem(SKEY)}catch(e){}UI.restored=false;UI.offline=false;UI.outbox=[];Object.keys(UI.devs).forEach(k=>{const ph=UI.devs[k].phone;UI.devs[k]=newDev(k,ph)});UI.devs.agency.stack=[{s:'home'}];UI.devs.client.stack=[{s:'home'}];UI.devs.wa.chat=null;toast('Demo data is back to the start.')},
 linkmode(){UI.linkMode=!UI.linkMode;UI.devs.client.stack=[{s:'home'}]},
 offline(){UI.offline=!UI.offline;if(!UI.offline){const pn=DB.points.filter(x=>x.pending);pn.forEach(x=>x.pending=false);let k=0;UI.outbox.forEach(o=>{if(OP.sendParty(visOf(o.vid),o.key))k++});UI.outbox=[];
   toast(pn.length||k?`Back online · ${plural(pn.length,'point')} synced · ${plural(k,'PDF')} ${sent()}`:'Back online. Nothing was waiting.')}else toast('Flight mode: points and photos are saved on the phone and go out when the signal returns.','wait')},
 scen(v){const s=GUIDE[+v];UI.view=s.view;if(s.user)UI.user=s.user;if(s.view==='desk')UI.devs.desk.signed=true;if(s.run)s.run();UI.panel=null;UI.guide=+v;toast(s.t+': '+s.steps[0])},
 /* generic */
 nav(v,el,dev){if(dev.phone)dev.stack=[{s:v}];else{dev.sec=v;dev.vid=''}dev.sheet=null},back(v,el,dev){if(dev.stack.length>1)dev.stack.pop();dev.sheet=null},
 go(v,el,dev){const [s,id]=v.split('|');dev.stack.push({s,id:id&&/^\d+$/.test(id)?+id:id});if(s==='point'){dev.f.ad_note='';dev.f.ad_photo=false}if(s==='bill'&&dev.id==='agency'){const b=billOf(id);dev.f.ab_no='';dev.f.ab_amt='';dev.f.ab_doc=false}},
 ui(v,el,dev){const i=v.indexOf('='),k=v.slice(0,i),val=v.slice(i+1);if(k==='vid'&&dev.phone&&val){dev.stack.push({s:'visit',id:val});return}dev[k]=val},
 set(v,el,dev){const i=v.indexOf('='),k=v.slice(0,i);dev.f[k]=v.slice(i+1);if((k+'_c') in dev.f)dev.f[k+'_c']=false;if(k==='c_cause'){dev.f.c_ref='';dev.f.c_note=''}},tog(v,el,dev){dev.f[v]=!dev.f[v]},close(v,el,dev){dev.sheet=(dev.sheet&&dev.sheet.back)||null},
 /* the calendar: for a date of the form (f|key) or for a date the screen is looked up by (ui|key|project).
    It opens on the month of the date already chosen; the sheet it was opened from comes back. */
 cal(v,el,dev){const [mode,key,pid]=v.split('|'),s={mode,key,pid:+pid||0,mo:0,back:dev.sheet&&dev.sheet.k!=='cal'?dev.sheet:null},now=calVal(dev,s);dev.f.cal_t='';if(now!=null)s.mo=calMonth(now);openSheet(dev,'cal',s);if(!dev.phone)UI.focus=dev.id+'_cal_t'},
 calmo(v,el,dev){const s=dev.sheet;if(s&&s.k==='cal'){s.mo=(s.mo||0)+(+v);s.seen=dev.f.cal_t||''}},
 calset(v,el,dev){const s=dev.sheet;if(!s||s.k!=='cal'||isNaN(+v))return;if(s.mode==='f'){dev.f[s.key+'_c']=true;dev.f[s.key+'_t']=fdmy(+v)}else dev[s.key]=String(+v);dev.f.cal_t='';dev.sheet=s.back||null},
 calclear(v,el,dev){const s=dev.sheet;if(!s||s.k!=='cal')return;dev[s.key]='';dev.f.cal_t='';dev.sheet=s.back||null},
 /* the searchable choice: who a point is for, which room; the sheet it was opened from comes back */
 pick(v,el,dev){const [src,key,pid,vendor]=v.split('|'),back=dev.sheet&&dev.sheet.k!=='pick'?dev.sheet:null;dev.f.pk_q='';openSheet(dev,'pick',{src,key,pid:+pid,vendor:vendor||'',back})},
 pickset(v,el,dev){const s=dev.sheet;if(!s)return;dev.f[s.key]=v;dev.f.pk_q='';dev.sheet=s.back||null},
 /* a point, whole */
 ptview(v,el,dev){if(dev.id==='agency'||dev.id==='client'||!ptOf(v))return;openSheet(dev,'ptview',{id:v})},
 reopenpt(v,el,dev){const x=ptOf(v);if(!x)return;OP.reopenPoint(x);dev.sheet=null;toast(`Point ${x.n} is open again.`)},
 /* the check of a point an agency marked done: solved, or back to the agency with what has to change */
 solvept(v,el,dev){const x=ptOf(v);if(!x)return;const p=pOf(x.pid);OP.solvePoint(x);dev.sheet=null;flash(dev,'Solved');toast(`Point ${x.n} is solved and closed.`);
  const l=x.e&&x.t&&p.lines.find(q=>q.e===x.e&&q.t===x.t);if(l&&l.st!=='done'&&!DB.points.some(q=>q.pid===p.id&&q.st==='open'&&q.e===x.e&&q.t===x.t))openSheet(dev,'offerdone',{pid:p.id,lid:l.id})},
 ptchange(v,el,dev){if(!ptOf(v))return;dev.f.pc_note='';openSheet(dev,'ptchange',{id:v,back:dev.sheet&&dev.sheet.k==='ptview'?dev.sheet:null});if(!dev.phone)UI.focus=dev.id+'_pc_note'},
 dochange(v,el,dev){const x=ptOf(v),t=(dev.f.pc_note||'').trim();if(!x)return;if(!t)return toast('Say what has to change.','wait');OP.changePoint(x,t);dev.f.pc_note='';dev.sheet=null;flash(dev,'Sent back','send');toast(`Point ${x.n} is back with ${partyName(pOf(x.pid),x)} · ${sent()}.`)},
 /* questions: open a thread, and write in it. An answer goes to every question of the thread that waits; with none waiting it is a line of its own. */
 thread(v,el,dev){dev.qt=v;dev.sheet=null;dev.toEnd=true;if(dev.phone){if(!(top(dev).s==='qchat'&&top(dev).id===v))dev.stack.push({s:'qchat',id:v})}else{const t=thOf(v);if(dev.sec!=='questions'&&t&&!t.open)dev.qf='all';dev.sec='questions'}},
 thsend(v,el,dev){const t=thOf(v);if(!t)return;const k=thKey(v),text=(dev.f[k]||'').trim(),open=t.qs.filter(q=>!q.ans),nm=thName(t);if(!text)return toast(open.length?'Type the answer first.':'Type the message first.','wait');
  if(open.length){const ts=Math.floor(Date.now()/1000);open.forEach(q=>{OP.answer(t.d,q.id,text);q.ansTs=ts})}else OP.say(t.d,t.by,text);dev.f[k]='';dev.toEnd=true;UI.focus=dev.id+'_'+k;toast(`${open.length?'Answered':'Sent'}. ${nm} sees it in the app.`)},
 agdone(v,el,dev){const x=ptOf(v),a=agOf(UI.agency),L=UI.lang.agency;if(!x)return;if(!dev.f.ad_photo)return toast(tr('pt_proof',L),'wait');
  OP.agencyDone(x,(dev.f.ad_note||'').trim(),true,a.people[0].n);dev.f.ad_note='';dev.f.ad_photo=false;if(dev.stack.length>1)dev.stack.pop();flash(dev,'✓');pushStaff(a.n+' marked point '+x.n+' done',[x.by,...pOf(x.pid).coords]);toast(tr('pt_sent',L))},
 /* a person's access ticks (Setup › Staff) */
 acctog(v,el,dev){if(!can('setup'))return toast('Only people with Setup change access.','wait');const [sid,k]=v.split('|'),u=stf(sid);if(!u||!u.roles)return;const acc=accOf(u),on=!acc.includes(k);
  if(!on&&k==='setup'&&sid===UI.user)return toast('You cannot take Setup away from yourself.','wait');u.acc=on?[...acc,k]:acc.filter(x=>x!==k);OP.access(u,k,on)},
 /* notifications */
 notes(v,el,dev){const fresh=(DB.notes||[]).filter(n=>!n.seen).map(n=>n.id);openSheet(dev,'notes',{fresh});if(fresh.length)OP.seenNotes()},
 noteopen(v,el,dev){const n=(DB.notes||[]).find(x=>String(x.id)===String(v)),r=n&&n.ref;if(!r)return;const [k,id]=r;dev.sheet=null;
  if(k==='dwg'&&n.ev==='drawing_question'&&dOf(id)){const th=qThreads(myPids()).find(x=>x.d.id===id&&x.open)||qThreads(myPids()).find(x=>x.d.id===id);if(th)return A.thread(th.id,el,dev)}
  if(k==='dwg'&&dOf(id))return openDwg(dev,id);if(k==='point'&&ptOf(id))return dev.id==='agency'?A.go('point|'+id,el,dev):openSheet(dev,'ptview',{id});if(k==='bill'&&billOf(id))return A.bill(id,el,dev);if(k==='visit'&&visOf(id))return A.openvisit(id,el,dev);if(k==='proj'&&pOf(id))return openProj(dev,id,'picture');
  toast('That is not on your screens any more.','wait')},
 /* the MOM as a PDF, cut by visit and by party */
 mompdf(v,el,dev){Object.assign(dev.f,{pf_v:'',pf_p:'',pf_st:'open'});openSheet(dev,'mompdf',{id:+v})},
 dopdf(v,el,dev){const f=dev.f;openSheet(dev,'pdf',{kind:'points',a:v,b:f.pf_p||'all',v:f.pf_v||'',st:f.pf_st||'open'})},
 newagency(v,el,dev){const [pid,t]=v.split('|');Object.assign(dev.f,{na_n:'',na_t:t,na_p:'',na_ph:'',na_l:'gu'});openSheet(dev,'addagency',{back:dev.sheet})},
 sheet(v,el,dev){const [k,id]=v.split('|');openSheet(dev,k,{id})},
 signin(v,el,dev){dev.signed=true;dev.sheet=null;if(dev.phone)dev.stack=[{s:'today'}];else dev.sec='today';dev._k='';flash(dev,'Welcome, '+me().n)},signout(v,el,dev){dev.signed=false;dev.sheet=null;dev.si={step:'lang'};dev.stack=[{s:dev.id==='staff'?'today':'home'}]},
 asuser(v){UI.user=v},
 /* projects, onboarding */
 proj(v,el,dev){openProj(dev,v,'picture')},
 onb(v,el,dev){obStart(dev,v?+v:null);if(dev.phone)dev.stack.push({s:'onboard'});else dev.sec='onboard'},
 onbstep(v,el,dev){const [pid,st]=v.split('|');const ob=obStart(dev,+pid);obDrawings(ob);ob.step=+st;if(dev.phone)dev.stack.push({s:'onboard'});else dev.sec='onboard'},
 obclose(v,el,dev){dev.ob=null;if(dev.phone)dev.stack.pop();else dev.sec='projects'},
 obgo(v,el,dev){const ob=dev.ob,n=+v;if(n>1&&(!ob.name.trim()||!ob.client.trim())){ob.step=1;return toast('Give the project a name and a client first.','wait')}
  if(n>3&&!ob.ents.length){ob.step=3;return toast('Add at least one room or zone. Pick a preset to start.','wait')}if(n>=5)obDrawings(ob);ob.step=n},
 obset(v,el,dev){const i=v.indexOf('=');dev.ob[v.slice(0,i)]=v.slice(i+1)},obmulti(v,el,dev){const [k,id]=v.split('='),a=dev.ob[k],i=a.indexOf(id);i<0?a.push(id):a.splice(i,1)},
 obpreset(v,el,dev){obPreset(dev.ob,v)},obtask(v,el,dev){dev.ob.ents.unshift({u:++OBU,n:v,ty:guessType(v),task:v})},obdel(v,el,dev){dev.ob.ents.splice(+v,1)},
 obadd(v,el,dev){const ob=dev.ob,ty=ETX[v]?v:'Other room',n=ob.ents.filter(e=>e.n.replace(/ \d+$/,'')===v).length;ob.ents.splice(Math.max(0,ob.ents.length-(ob.ents.some(e=>e.ty==='Whole site')?1:0)),0,{u:++OBU,n:n?v+' '+(n+1):v,ty})},
 obtrade(v,el,dev){dev.ob.tr[v].on=!dev.ob.tr[v].on},obtick(v,el,dev){const [u,t]=v.split('|'),ob=dev.ob,e=ob.ents.find(x=>x.u==u);ob.ticks[u+'|'+t]=!obTick(ob,e,t)},
 obdraw(v,el,dev){const d=dev.ob.dr[+v];d.on=!d.on},obdue(v,el,dev){const [i,n]=v.split('|');dev.ob.dr[+i].due=Math.max(0,dev.ob.dr[+i].due+ +n)},
 obflag(v,el,dev){const [i,k]=v.split('|'),d=dev.ob.dr[+i];d[k]=!d[k];if(!d.client)d.appr=false},
 obadddraw(v,el,dev){const ob=dev.ob;if(!ob.nd.trim())return toast('Type the drawing’s name first.','wait');ob.dr.push({code:'AD',n:ob.nd.trim(),t:'',on:true,ds:ob.designers[0]||(DB.staff.find(u=>has(u,'designer'))||{id:''}).id,due:14,client:false,appr:false,custom:true});ob.nd=''},
 obinv(v,el,dev){dev.ob.inv[v]=!dev.ob.inv[v]},
 obfinish(v,el,dev){const ob=dev.ob;if(!ob.name.trim())return toast('Give the project a name first.','wait');const r=obApply(ob);dev.ob=null;if(dev.phone)dev.stack=[{s:'projects'}];openProj(dev,r.p.id,'picture');
  flash(dev,r.was?'Saved':'Project started','check',!r.was);toast(`${r.p.name}: ${plural(r.nl,'work line')} and ${plural(r.nd,'drawing')} added${r.inv?' · '+plural(r.inv,'invitation')+' '+sent():''}.`)},
 taskent(v,el,dev){const [pid,n]=v.split('|'),p=pOf(pid);p.ents.push({id:'e'+p.id+'_t'+p.ents.length,n,ty:guessType(n)});p.tasks=p.tasks.filter(t=>t.n!==n);toast(`“${n}” is now a room of ${p.name}. Tick its trades in Project configuration.`)},
 /* work grid */
 cell(v,el,dev){const [pid,lid]=v.split('|'),l=pOf(pid).lines.find(x=>x.id===lid);dev.backRoom=!!(dev.sheet&&dev.sheet.k==='room');Object.assign(dev.f,{c_st:l.st,c_cause:l.cause||'',c_ref:l.ref||'',c_note:l.note||'',c_new:'',c_ag:l.ag||''});openSheet(dev,'cell',{pid:+pid,lid})},
 savecell(v,el,dev){const [pid,lid]=v.split('|'),p=pOf(pid),l=p.lines.find(x=>x.id===lid),f=dev.f;let ref=f.c_ref;
  if(f.c_st==='wait'){if(!f.c_cause)return toast('“Waiting” always names its cause. Pick one.','wait');
   if(f.c_cause==='client'&&f.c_new&&f.c_new.trim())ref=OP.addPoint({pid:p.id,kind:'client',party:'client',text:f.c_new.trim(),e:l.e,due:3}).id;
   if((f.c_cause==='drawing'||f.c_cause==='trade')&&!ref)return toast(f.c_cause==='drawing'?'Choose the drawing it waits for.':'Choose the trade it waits for.','wait');
   if((f.c_cause==='material'||f.c_cause==='other')&&!(f.c_note||'').trim())return toast('Add a short note: what is it waiting for?','wait')}
  l.ag=f.c_ag||null;OP.setLine(p,l,f.c_st,{cause:f.c_cause,ref,note:f.c_note});dev.sheet=dev.backRoom?{k:'room',pid:p.id,eid:l.e}:null;dev.backRoom=false;toast(`${entN(p,l.e)} · ${TX[l.t].n}: ${LS[l.st][0]}${l.st==='wait'?' for '+waitText(p,l):''}`)},
 markdone(v,el,dev){const [pid,lid]=v.split('|'),p=pOf(pid),l=p.lines.find(x=>x.id===lid);OP.setLine(p,l,'done');dev.sheet=null;flash(dev,'Done');toast(`${entN(p,l.e)} · ${TX[l.t].n} marked done.`)},
 assign(v,el,dev){const [pid,t]=v.split('|'),pl=planOf(pOf(pid),t);dev.f.a_ag=pl.ag||'';dev.f.a_by=7;dev.f.a_by_c=false;openSheet(dev,'assign',{pid:+pid,t})},
 saveassign(v,el,dev){const [pid,t]=v.split('|'),p=pOf(pid),by=dueOf(dev.f,'a_by');if(!dev.f.a_ag&&isNaN(by))return toast(DMYHINT,'wait');OP.assign(p,t,dev.f.a_ag,by);dev.sheet=null;toast(dev.f.a_ag?`${TX[t].n}: ${agN(dev.f.a_ag)}. Its ${plural(p.lines.filter(l=>l.t===t).length,'work line')} now carry this agency.`:`${TX[t].n} stays undecided until ${fd(by)}.`)},
 /* drawings */
 dwg(v,el,dev){openDwg(dev,v)},dstart(v){dOf(v).st='in_progress';toast('Marked in progress.')},view(v,el,dev){openSheet(dev,'view',{id:v})},
 dosend(v,el,dev){const d=dOf(v);if(!dev.f.sa_file)return toast('Choose the PDF first.','wait');OP.sendForApproval(d,dev.f.sa_note);dev.f.sa_file=false;dev.f.sa_note='';
  if(DB.set.approval){dev.sheet=null;flash(dev,'Sent','send');toast(`${sheetNo(d)} sent to ${stf(pOf(d.pid).principal).n} for approval.`)}else relPrefill(dev,d)},
 approve(v,el,dev){if(!can('approve'))return toast('Only the principal approves a release.','wait');dev.f.ap_note='';openSheet(dev,'approve',{id:v})},
 doapprove(v,el,dev){const [id,rel]=v.split('|'),d=dOf(id);OP.approve(d);if(rel)relPrefill(dev,d);else{dev.sheet=null;flash(dev,'APPROVED','stamp');toast(`${sheetNo(d)} approved. ${stf(d.ds).n} can release it now.`)}},
 sendback(v,el,dev){const d=dOf(v);if(!(dev.f.ap_note||'').trim())return toast('Say why it goes back.','wait');OP.sendBack(d,dev.f.ap_note.trim());dev.sheet=null;toast(`${sheetNo(d)} sent back to ${stf(d.ds).n}.`)},
 release(v,el,dev){relPrefill(dev,dOf(v))},
 dorelease(v,el,dev){const d=dOf(v),to=Object.keys(dev.f).filter(k=>k.startsWith('rc_')&&dev.f[k]).map(k=>k.slice(3));const fr=OP.release(d,to);dev.sheet=null;flash(dev,'RELEASED','stamp');toast(`${sheetNo(d)} rev ${cur(d).n} released to ${to.length} · ${sent()}${fr?' · '+plural(fr,'line')+' no longer waiting':''}.`)},
 newrev(v){const d=dOf(v);d.revs.push({n:cur(d).n+1,st:'draft',note:'',rc:[]});d.st='in_progress';d.due=5;toast(`Revision ${cur(d).n} started. Receivers keep seeing the released one until the new one goes out.`)},
 answer(v,el,dev){const [id,q]=v.split('|'),t=(dev.f['ans_'+q]||'').trim();if(!t)return toast('Type the answer first.','wait');OP.answer(dOf(id),q,t);dev.f['ans_'+q]='';toast('Answered. The asker sees it in the app.')},
 dologq(v,el,dev){const d=dOf(v),f=dev.f,p=pOf(d.pid);if(!f.lq_by||!(f.lq_text||'').trim())return toast('Choose who asked and type the question.','wait');OP.ask(d,f.lq_by,f.lq_by==='client'?p.client.contacts[0].n:agOf(f.lq_by).people[0].n,f.lq_text.trim(),false,'office');f.lq_text='';dev.sheet=null;toast('Question logged on the drawing.')},
 /* points and MOM */
 remind(v,el,dev){const [to,pid,...rest]=v.split('|'),p=pOf(pid);OP.remind(to,+pid,rest.join('|'));toast(`Reminder to ${to==='client'?p.client.n:agN(to)} · ${sent()}.`)},
 confirmpt(v){const x=ptOf(v);OP.confirmPoint(x);toast(`Point ${x.n} confirmed. The client sees it now · ${sent()}.`)},
 closept(v,el,dev){dev.f.cp_note='';dev.f.cp_photo=false;openSheet(dev,'closept',{id:v})},
 doclose(v,el,dev){const x=ptOf(v),p=pOf(x.pid);OP.closePoint(x,dev.f.cp_note,dev.f.cp_photo);dev.sheet=null;flash(dev,'Closed');toast(`Point ${x.n} closed.`);
  const l=x.e&&x.t&&p.lines.find(q=>q.e===x.e&&q.t===x.t);if(l&&l.st!=='done'&&!DB.points.some(q=>q.pid===p.id&&q.st==='open'&&q.e===x.e&&q.t===x.t))openSheet(dev,'offerdone',{pid:p.id,lid:l.id})},
 startmom(v,el,dev){const p=pOf(v);let vi=DB.visits.find(x=>x.pid===p.id&&x.st==='open');if(!vi){vi={id:'v'+(++DB.seq.vid),pid:p.id,no:++p.visitNo,date:0,by:UI.user,att:[me().n],st:'open'};DB.visits.push(vi)}
  if(String(dev.f.m_pid)!==String(p.id))Object.assign(dev.f,{m_for:'',m_area:null,m_vendor:'',m_due:2,m_due_c:false});Object.assign(dev.f,{m_pid:String(p.id),m_text:'',m_photo:false});if(dev.phone)dev.stack.push({s:'visit',id:vi.id});else{openProj(dev,p.id,'mom');dev.vid=vi.id}},
 openvisit(v,el,dev){const vi=visOf(v);if(dev.phone)dev.stack.push({s:'visit',id:v});else{openProj(dev,vi.pid,'mom');dev.vid=v}},
 addpt(v,el,dev){const vi=visOf(v),f=dev.f,t=(f.m_text||'').trim(),due=dueOf(f,'m_due');if(!t)return toast('Type or speak the point first.','wait');if(f.m_area==null)return toast('Choose the room first. It stays for the next points.','wait');if(isNaN(due))return toast(DMYHINT,'wait');
  const kind=agOf(f.m_for)?'agency':f.m_for==='client'?'client':f.m_for==='vendor'?'vendor':'staff',x=OP.addPoint({pid:vi.pid,vid:vi.id,kind,party:kind==='vendor'?f.m_vendor:f.m_for,text:t,e:f.m_area||null,due,photo:!!f.m_photo});
  if(UI.offline&&dev.id==='staff')x.pending=true;f.m_text='';f.m_photo=false;dev.toEnd=true;UI.focus=dev.id+'_m_text'},
 sendparty(v,el,dev){const [vid,key]=v.split('|');if(UI.offline&&dev.id==='staff'){if(!UI.outbox.some(o=>o.vid===vid&&o.key===key))UI.outbox.push({vid,key});return toast(`Saved. ${agN(key)}’s PDF goes out when the network returns.`,'wait')}
  const n=OP.sendParty(visOf(vid),key);if(n){flash(dev,'Sent','wa');toast(`${agN(key)}: ${plural(n,'point')} as a PDF · ${sent()}.`)}},
 sendall(v,el,dev){const vi=visOf(v),ks=[...new Set(DB.points.filter(x=>x.vid===v&&x.st==='open'&&x.kind==='agency').map(x=>x.party))];if(UI.offline&&dev.id==='staff'){ks.forEach(k=>{if(!UI.outbox.some(o=>o.vid===v&&o.key===k))UI.outbox.push({vid:v,key:k})});return toast('Saved. Every party’s PDF goes out when the network returns.','wait')}
  ks.forEach(k=>OP.sendParty(vi,k));flash(dev,'Sent','wa');toast(`${plural(ks.length,'party','parties')} got their own PDF · ${sent()}. Client points wait for the office.`)},
 finishvisit(v,el,dev){const vi=visOf(v);vi.st='finished';if(dev.phone)dev.stack.pop();else dev.vid='';flash(dev,'Filed');toast(`Visit ${vi.no} filed. The full MOM is with the office.`)},
 pdf(v,el,dev){const [kind,a,b]=v.split('|');openSheet(dev,'pdf',{kind,a,b})},
 dovendor(v,el,dev){const n=(dev.f.vn||'').trim();if(!n)return toast('Type the vendor’s name.','wait');dev.f.m_vendor=n;dev.f.m_for='vendor';dev.f.vn='';dev.sheet=null},
 raise(v,el,dev){const p=pOf(v),f=dev.f,same=String(f.rp_pid)===String(v),opts=forOptions(p);
  Object.assign(f,{rp_pid:String(v),rp_for:same&&opts.some(o=>o[0]===f.rp_for)?f.rp_for:opts[0][0],rp_text:'',rp_area:same&&f.rp_area!=null&&(f.rp_area===''||p.ents.some(e=>e.id===f.rp_area))?f.rp_area:null,rp_due:f.rp_due==null?2:f.rp_due,rp_photo:false});openSheet(dev,'point',{pid:+v})},
 raiseclient(v,el,dev){Object.assign(dev.f,{rp_pid:String(v),rp_for:'client',rp_text:'',rp_area:'',rp_due:3,rp_due_c:false,rp_photo:false});openSheet(dev,'point',{pid:+v})},
 doraise(v,el,dev){const f=dev.f,t=(f.rp_text||'').trim(),due=dueOf(f,'rp_due');if(!t)return toast('Say what is needed.','wait');if(f.rp_area==null)return toast('Choose the room, or “Whole site”.','wait');if(isNaN(due))return toast(DMYHINT,'wait');
  const kind=agOf(f.rp_for)?'agency':f.rp_for==='client'?'client':'staff',x=OP.addPoint({pid:+v,kind,party:f.rp_for,text:t,e:f.rp_area||null,due,photo:!!f.rp_photo});
  dev.sheet=null;if(kind==='client'&&x.confirmed)OP.confirmPoint(x);if(kind==='agency'){x.sent=1;x.fresh=false;OP.remind(f.rp_for,+v,t+' (by '+dueW(x.due)+')')}
  toast(kind==='client'&&!x.confirmed?`Point ${x.n} raised. It waits for the office to confirm before the client sees it.`:`Point ${x.n} raised for ${partyName(pOf(v),x)}${kind==='staff'?'':' · '+sent()}.`)},
 /* bills */
 askbill(v,el,dev){const p=v?pOf(v):null;Object.assign(dev.f,{ab_pid:v||'',ab_ag:'',ab_what:'',ab_upto:'',ab_to:p?p.billedTo:'client'});openSheet(dev,'askbill',{pid:v?+v:null})},
 doaskbill(v,el,dev){const f=dev.f,p=pOf(f.ab_pid||v);if(!p||!f.ab_ag||!(f.ab_what||'').trim())return toast('Choose the project and the agency, and say what the bill is for.','wait');const pl=p.plan.find(x=>x.ag===f.ab_ag);
  OP.askBill({pid:p.id,ag:f.ab_ag,t:pl.t,what:f.ab_what.trim(),upto:+String(f.ab_upto).replace(/\D/g,'')||null,billedTo:f.ab_to});dev.sheet=null;flash(dev,'Asked','wa');toast(`${agN(f.ab_ag)} is asked for a bill · ${sent()}.`)},
 bill(v,el,dev){const b=billOf(v);Object.assign(dev.f,{ub_no:'',ub_amt:'',ub_doc:false,rb_reason:'',py_amt:b.amount!=null?String(b.amount-paid(b)):'',py_by:b.billedTo,py_mode:'Bank transfer',py_proof:false});openSheet(dev,'bill',{id:v})},
 billto(v){const [id,to]=v.split('|');billOf(id).billedTo=to},
 doupload(v,el,dev){const [id]=v.split('|'),b=billOf(id),amt=+String(dev.f.ub_amt).replace(/\D/g,'');if(!amt)return toast('Enter the bill amount.','wait');OP.uploadBill(b,{no:dev.f.ub_no||'—',amount:amt});toast('Bill submitted. It is now in “To review”.')},
 doreview(v,el,dev){const [id,ok]=v.split('|'),b=billOf(id);if(ok==='0'&&!(dev.f.rb_reason||'').trim())return toast('Say why it is returned.','wait');OP.reviewBill(b,ok==='1',(dev.f.rb_reason||'').trim());dev.f.py_amt=String(b.amount);dev.f.py_by=b.billedTo;
  if(ok==='0')dev.sheet=null;toast(ok==='1'?`Accepted. ${agN(b.ag)} is told · ${sent()}.`:`Returned to ${agN(b.ag)} with the reason · ${sent()}.`)},
 dopay(v,el,dev){const b=billOf(v),amt=+String(dev.f.py_amt).replace(/\D/g,''),bal=b.amount-paid(b);if(!amt||amt>bal)return toast(amt>bal?'That is more than the balance of '+inr(bal)+'.':'Enter the amount paid.','wait');
  OP.pay(b,{amount:amt,by:dev.f.py_by,mode:dev.f.py_mode,proof:!!dev.f.py_proof});dev.f.py_amt=String(b.amount-paid(b));flash(dev,BS[b.st][0],'rupee',b.st==='paid');toast(`${inr(amt)} recorded, paid by ${dev.f.py_by==='client'?'the client':'Revert'}. ${agN(b.ag)} sees “${BS[b.st][0]}”.`)},
 /* client access */
 invite(v,el,dev){const [pid,i]=v.split('|'),p=pOf(pid);p.client.contacts[+i].inv=true;notify('invite','client:'+pid,{site:p.name});toast(`Invitation to ${p.client.contacts[+i].n} · ${sent()}.`)},
 copylink(v){toast('Secure link copied: revert.co.in/c/'+pOf(v).name.toLowerCase().replace(/\W+/g,'-')+'-7f3k')},
 /* setup */
 setting(v){DB.set[v]=!DB.set[v];toast({approval:DB.set.approval?'Releases need the principal’s approval.':'Designers now release directly.',clientConfirm:DB.set.clientConfirm?'Client points wait for the office to confirm.':'Client points now show to the client at once.',sending:DB.set.sending?'WhatsApp sending is on.':'Sending is off. Messages are logged as “held”.'}[v])},
 limit(v){const [k,n]=v.split('|');DB.set.lim[k]=Math.max(1,DB.set.lim[k]+ +n)},
 ettoggle(v){const [n,t]=v.split('|'),e=ETX[n],i=e.tr.indexOf(t);i<0?e.tr.push(t):e.tr.splice(i,1)},dtflag(v){const [i,k]=v.split('|');DTYPES[+i][k]=!DTYPES[+i][k]},
 roletog(v){if(!can('setup'))return toast('Only people with Setup change roles.','wait');const [s,r]=v.split('|'),u=stf(s),i=u.roles.indexOf(r),before=[...u.roles];i<0?u.roles.push(r):u.roles.length>1&&u.roles.splice(i,1);
  /* a role given brings its usual access; a role taken away takes what only it brought (the server does the same) */
  if(u.acc){const of=rs=>new Set(rs.flatMap(x=>ACCROLE[x]||[])),keep=of(u.roles),gone=[...of(before.filter(x=>!u.roles.includes(x)))].filter(k=>!keep.has(k)),add=[...of(u.roles.filter(x=>!before.includes(x)))];u.acc=[...new Set([...u.acc,...add])].filter(k=>!gone.includes(k))}},
 doaddtrade(v,el,dev){const f=dev.f,n=(f.nt_n||'').trim();if(!n)return toast('Type the trade’s name.','wait');const t={id:'t'+TRADES.length,n,s:n.slice(0,5),gu:f.nt_gu||n,hi:f.nt_hi||n};TRADES.push(t);TX[t.id]=t;f.nt_n=f.nt_gu=f.nt_hi='';dev.sheet=null;toast(`Trade “${n}” added. It is offered at the next onboarding.`)},
 doaddagency(v,el,dev){const f=dev.f;if(!(f.na_n||'').trim()||!f.na_t)return toast('Give the firm’s name and its trade.','wait');const g={id:'a'+(DB.agencies.length+1),n:f.na_n.trim(),tr:[f.na_t],lang:f.na_l||'gu',people:[{n:f.na_p||'Owner',ph:f.na_ph||'—'}]},back=dev.sheet&&dev.sheet.back;DB.agencies.push(g);f.na_n=f.na_p=f.na_ph='';dev.sheet=back||null;if(back&&back.k==='assign')f.a_ag=g.id;toast(back?'Agency added. Save to give it this trade.':'Agency added.')},
 /* agency and client apps */
 silang(v,el,dev){UI.lang[dev.id]=v;dev.si.step='phone';dev.f.si_ph=dev.id==='agency'?agOf(UI.agency).people[0].ph:pOf(UI.clientPid).client.contacts[0].ph},
 sicode(v,el,dev){dev.si.code=String(1000+Math.floor(Math.random()*9000));dev.si.step='otp';dev.f.si_otp='';notify('otp',dev.id==='agency'?UI.agency:'client:'+UI.clientPid,{code:dev.si.code});toast('Sign-in code '+sent()+'.')},
 sifill(v,el,dev){dev.f.si_otp=dev.si.code},
 siverify(v,el,dev){if(String(dev.f.si_otp).trim()!==dev.si.code)return toast('That code does not match. Look at the WhatsApp message.','wait');dev.signed=true;dev.si=null;dev.stack=[{s:'home'}];dev._k='';flash(dev,tr(dev.id==='agency'?'hello':'c_hi',UI.lang[dev.id]))},
 alang(v){UI.lang.agency=v},clang(){UI.lang.client=UI.lang.client==='en'?'gu':'en'},
 adwg(v,el,dev){const d=dOf(v);if(OP.open(d,UI.agency))toast(`${agN(UI.agency)} opened ${sheetNo(d)}. The desk shows “opened” now.`);dev.f.aq='';dev.f.aq_photo=false;dev.stack.push({s:'dwg',id:v})},
 aask(v,el,dev){const d=dOf(v),a=agOf(UI.agency),t=(dev.f.aq||'').trim()||(dev.f.aq_photo?tr('q_only',UI.lang.agency):'');if(!t)return toast(tr('noq',UI.lang.agency),'wait');OP.ask(d,a.id,a.people[0].n,t,dev.f.aq_photo);dev.f.aq='';dev.f.aq_photo=false;dev.toEnd=true;flash(dev,tr('send',UI.lang.agency),'send');pushStaff(a.n+' asks on '+sheetNo(d)+': '+t,[d.ds,...pOf(d.pid).coords]);toast(`Question sent. It sits on ${stf(d.ds).n}’s list until answered.`)},
 asubmit(v,el,dev){const b=billOf(v),amt=+String(dev.f.ab_amt).replace(/\D/g,'');if(!amt)return toast(tr('amount',UI.lang.agency)+'?','wait');OP.uploadBill(b,{no:dev.f.ab_no||'—',amount:amt});flash(dev,tr('submitted',UI.lang.agency));pushStaff(agN(b.ag)+' uploaded a bill · '+b.what,pOf(b.pid).coords);toast('Bill uploaded. The office sees it in “To review”.')},
 cdwg(v,el,dev){const d=dOf(v);if(OP.open(d,'client'))toast(`The client opened ${sheetNo(d)}. The desk shows “opened” now.`);dev.f.c_note='';dev.stack.push({s:'dwg',id:v})},
 capprove(v,el,dev){const d=dOf(v),c=pOf(d.pid).client.contacts[0];OP.clientDecide(d,'approved','',c.n);flash(dev,'APPROVED','stamp');pushStaff(c.n+' approved '+d.title,[d.ds,pOf(d.pid).principal,...pOf(d.pid).coords]);toast(`${d.title} approved by ${c.n}, ${fdw(0)} ${NOW}. Recorded with name, date and time.`)},
 cchange(v,el,dev){const d=dOf(v),c=pOf(d.pid).client.contacts[0],t=(dev.f.c_note||'').trim();if(!t)return toast(tr('c_note',UI.lang.client),'wait');OP.clientDecide(d,'change',t,c.n);dev.f.c_note='';dev.stack.pop();pushStaff(c.n+' asked for a change on '+d.title,[d.ds,pOf(d.pid).principal,...pOf(d.pid).coords]);toast(`Change asked. ${d.title} is back with ${stf(d.ds).n} as a new revision.`)},
 cdone(v,el,dev){const x=ptOf(v);OP.closePoint(x,'Marked done by the client',false,'client');flash(dev,'✓');toast(`The client closed “${x.text}”.`)},
 wachat(v,el,dev){dev.chat=v||null},
 wadoc(v,el,dev){const m=DB.wa[+v];if(m.doc.k==='dwg'){const d=dOf(m.doc.id),who=String(m.to).startsWith('client')?'client':m.to;if(OP.open(d,who))toast(`Link opened by ${m.name}. “Opened” is recorded on ${sheetNo(d)}.`);openSheet(dev,'view',{id:d.id})}else openSheet(dev,'pdf',{kind:'mom',a:m.doc.vid,b:m.doc.party})},
};

/* ---------- guide ---------- */
const GUIDE=[
 {t:'Onboard a project',view:'desk',user:'s3',run(){A.onb('',null,UI.devs.desk)},steps:['Fill the name and client, then Next.','Step 3: tap “3 BHK”. Step 4: pick agencies; leave one undecided.','Step 5: the standard drawings are already ticked. Review, then Start project.']},
 {t:'See why a project is stuck',view:'desk',user:'s3',run(){openProj(UI.devs.desk,1,'picture')},steps:['Shah Residence is Stuck: the plumber is undecided, 6 days past its date.','Tap Assign on the blocker and choose an agency. The status and the grid change at once.','Tap any grid cell: set Waiting and name the cause.']},
 {t:'Release a drawing',view:'desk',user:'s5',run(){openDwg(UI.devs.desk,'d3')},steps:['As Amit: Upload PDF and send EL-01 for approval.','Switch “Signed in as” to Pranav: approve it from Today, then release.','Open the WhatsApp view: Jay Electric got the link. Tap it and the desk shows “opened”; three waiting lines are free.']},
 {t:'MOM on site, on the phone',view:'staff',user:'s1',run(){const d=UI.devs.staff;d.signed=true;d.stack=[{s:'mom'}]},steps:['Start a MOM for Shah Residence. Earlier open points come first.','Pick “For” once, type a point, Add. Repeat. Then tap a party to send its PDF.','Try flight mode (top right): points wait on the phone and go out when you switch it back.']},
 {t:'What the agency sees',view:'agency',run(){const d=UI.devs.agency;d.signed=true;d.stack=[{s:'home'}]},steps:['Mahadev Furniture, in Gujarati: its points, new drawings, and “Revert asks”.','Open a drawing and ask a question. Upload the bill Revert asked for.','Globe icon: change the language, or sign out to see the WhatsApp code sign-in.']},
 {t:'What the client sees',view:'client',run(){const d=UI.devs.client;d.signed=true;d.stack=[{s:'home'}]},steps:['Two blocks only: Waiting for you, and Your drawings.','Open the furniture layout: Approve, or ask for a change with a note.','“Open from link” in the top bar shows the same screens in a browser, without installing.']},
 {t:'Bills and money',view:'desk',user:'s1',run(){const d=UI.devs.desk;d.sec='bills';d.btab='review'},steps:['As the owner: review the civil bill, accept it, record a part payment.','“Paid by Revert” on a bill addressed to the client shows as an amount to recover.','Switch to Meera: she sees documents and status, never the amounts.']},
 {t:'The weekly review',view:'desk',user:'s1',run(){UI.devs.desk.sec='review'},steps:['One row per project: status, four counts, blockers.','Open a project from its row. Every figure is counted from records.','Setup › Settings: turn approval off, or change the day limits, and watch the picture follow.']}];
function guideHTML(){return `<aside class="panel" aria-label="Guide"><header><h2>Try these</h2><button type="button" class="xb" data-a="closepanel" aria-label="Close">${ic('x')}</button></header><p class="mu">Everything here runs on one shared set of invented records. An action on one screen shows on the others.</p>
 ${GUIDE.map((g,i)=>`<section class="gd ${UI.guide===i?'on':''}"><div class="gdt"><b>${i+1}. ${g.t}</b>${Bt('Take me there','scen',i,'sm gold')}</div><ol>${g.steps.map(s=>`<li>${s}</li>`).join('')}</ol></section>`).join('')}</aside>`}

/* ---------- the rail: every screen of the chosen view, one tap away ---------- */
const dv=k=>UI.devs[k],dk=()=>{const d=UI.devs.desk;d.signed=true;return d};
const RAIL={
 desk:[['Log in',()=>{UI.devs.desk.signed=false}],['Today',()=>{dk().sec='today'}],['Project picture',()=>openProj(dk(),1,'picture')],['Work · plan and schedule',()=>openProj(dk(),1,'work')],['Onboarding · six steps',()=>A.onb('',null,dk())],
  ['Drawings · approve and release',()=>{const d=dk();d.sec='drawings';d.dtab='awaiting';d.drawer='d6'}],['MOM',()=>{dk().sec='mom'}],['Bills and money',()=>{const d=dk();d.sec='bills';d.btab='all'}],['Review',()=>{dk().sec='review'}],['Setup',()=>{dk().sec='setup'}]],
 staff:[['Sign in',()=>{const d=dv('staff');d.signed=false}],['Today',()=>{const d=dv('staff');d.signed=true;d.stack=[{s:'today'}]}],['Project picture',()=>{const d=dv('staff');d.signed=true;d.ptab='picture';d.stack=[{s:'projects'},{s:'project',id:1}]}],
  ['Work · the living plan',()=>{const d=dv('staff');d.signed=true;d.ptab='work';d.wv='plan';d.stack=[{s:'projects'},{s:'project',id:1}]}],['Drawings',()=>{const d=dv('staff');d.signed=true;d.stack=[{s:'drawings'}]}],
  ['MOM on site',()=>{const d=dv('staff');d.signed=true;d.stack=[{s:'mom'}];A.startmom('1',null,d)}],['Onboarding on the phone',()=>{const d=dv('staff');d.signed=true;d.stack=[{s:'projects'}];A.onb('',null,d)}],['Bills',()=>{const d=dv('staff');d.signed=true;d.stack=[{s:'today'},{s:'bills'}]}],['More · flight mode',()=>{const d=dv('staff');d.signed=true;d.stack=[{s:'today'},{s:'more'}]}]],
 agency:[['Language and WhatsApp code',()=>{const d=dv('agency');d.signed=false;d.si={step:'lang'}}],['Home',()=>{const d=dv('agency');d.signed=true;d.stack=[{s:'home'}]}],['My sites',()=>{const d=dv('agency');d.signed=true;d.stack=[{s:'sites'}]}],
  ['A site · your rooms',()=>{const d=dv('agency');d.signed=true;d.stack=[{s:'sites'},{s:'site',id:agProjects(UI.agency)[0].id}]}],['Drawings',()=>{const d=dv('agency');d.signed=true;d.stack=[{s:'drawings'}]}],['Bills',()=>{const d=dv('agency');d.signed=true;d.stack=[{s:'bills'}]}]],
 client:[['Sign in',()=>{const d=dv('client');UI.linkMode=false;d.signed=false;d.si={step:'lang'}}],['Home',()=>{const d=dv('client');d.signed=true;d.stack=[{s:'home'}]}],['Approve a drawing',()=>{const d=dv('client'),x=DB.drawings.find(q=>q.pid==UI.clientPid&&q.st==='released'&&cur(q).client&&cur(q).client.dec==='pending')||DB.drawings.find(q=>q.pid==UI.clientPid&&q.st==='released'&&cur(q).rc.some(r=>r.to==='client'));d.signed=true;d.stack=[{s:'home'}];if(x)A.cdwg(x.id,null,d)}],
  ['Opened from the link',()=>{const d=dv('client');UI.linkMode=true;d.stack=[{s:'home'}]}]]};
function railHTML(){const v=UI.view;if(v==='all')return `<aside class="rail"><div class="lbl">Try a flow</div>${GUIDE.map((g,i)=>`<button type="button" class="rj" data-a="scen" data-v="${i}"><i>${i+1}</i><span>${g.t}</span></button>`).join('')}<div class="rnote"><b>One shared record set.</b> An action on one phone shows on the others and on WhatsApp.</div></aside>`;
 return `<aside class="rail"><div class="lbl">${{desk:'Revert Desk · browser',staff:'Staff app',agency:'Agency app',client:'Client app'}[v]}</div>${RAIL[v].map((j,i)=>`<button type="button" class="rj" data-a="jump" data-v="${i}" ${UI.jump===i?'aria-current="true"':''}><i>${i+1}</i><span>${j[0]}</span></button>`).join('')}
  <div class="rnote"><b>Invented names and numbers.</b> Everything is clickable; Reset brings the demo back. ${{desk:'The desk follows the Glass theme the back office will run on.',staff:'Staff do everything from the phone that the desk can do.',agency:'Agencies also get all of this on WhatsApp without opening the app.',client:'The client sees two blocks only, in the app or from a link.'}[v]}</div></aside>`}

/* ---------- shell ---------- */
function shellHTML(){const v=UI.view,D=UI.devs,dvw=(id,html)=>`<div class="dv dv-${id}" data-dev="${id}"><div class="dvcap">${{desk:'Revert Desk · browser',staff:'Staff app',agency:'Agency app',client:UI.linkMode?'Client · opened from the link':'Client app',wa:'WhatsApp · what parties receive'}[id]}</div>${html}</div>`;
 const fresh=DB.wa.filter(m=>m.fresh).length,sel=(k,opts,val,label)=>`<label class="tsel"><span>${label}</span><select data-top="${k}">${opts.map(o=>`<option value="${o[0]}" ${String(val)===String(o[0])?'selected':''}>${esc(o[1])}</option>`).join('')}</select></label>`;
 let stage='';
 if(v==='desk')stage=dvw('desk',deskHTML(D.desk));
 if(v==='staff')stage=dvw('staff',staffHTML(D.staff))+dvw('wa',waHTML(D.wa));
 if(v==='agency')stage=dvw('agency',agencyHTML(D.agency))+dvw('wa',waHTML(D.wa));
 if(v==='client')stage=dvw('client',clientHTML(D.client))+dvw('wa',waHTML(D.wa));
 if(v==='all')stage=dvw('staff',staffHTML(D.staff))+dvw('agency',agencyHTML(D.agency))+dvw('client',clientHTML(D.client))+dvw('wa',waHTML(D.wa));
 const ctx=(v==='desk'||v==='staff'||v==='all'?sel('user',DB.staff.filter(u=>['s1','s3','s4','s5'].includes(u.id)).map(u=>[u.id,u.n+' · '+roleLabel(u)]),UI.user,'Signed in as'):'')
  +(v==='agency'||v==='all'?sel('agency',DB.agencies.filter(a=>agProjects(a.id).length).map(a=>[a.id,a.n]),UI.agency,'Agency'):'')
  +(v==='client'||v==='all'?sel('clientPid',DB.projects.filter(p=>p.onb).map(p=>[p.id,p.client.n]),UI.clientPid,'Client'):'')
  +(v==='client'?`<button type="button" class="tbtn" data-a="linkmode" aria-pressed="${UI.linkMode}">${ic('link')}<span>Open from link</span></button>`:'')
  +(v==='staff'||v==='all'?`<button type="button" class="tbtn" data-a="offline" aria-pressed="${UI.offline}">${ic('off')}<span>Flight mode</span></button>`:'');
 return `<div class="top"><div class="topin"><div class="brand">${LOGO}<span>Release 1 preview</span></div>
  <div class="vseg" role="tablist">${[['desk','Desk','grid'],['staff','Staff app','phone'],['agency','Agency app','tool'],['client','Client app','user'],['all','Together','layers']].map(x=>`<button type="button" role="tab" data-a="setview" data-v="${x[0]}" aria-selected="${v===x[0]}">${ic(x[2])}<span>${x[1]}</span></button>`).join('')}</div>
  <div class="tctx">${ctx}</div><div class="tact">${matchMedia('(prefers-reduced-motion: reduce)').matches?`<button type="button" class="tbtn" data-a="motion" aria-pressed="${UI.motion==='on'}" title="This device asks for less motion. Switch the preview’s animations on or off.">${ic('star')}<span>${UI.motion==='on'?'Animations on':'Animations off'}</span></button>`:''}${v==='desk'?`<button type="button" class="tbtn" data-a="wapanel" aria-pressed="${UI.panel==='wa'}">${ic('wa')}<span>WhatsApp</span>${fresh?`<b>${fresh}</b>`:''}</button>`:''}<button type="button" class="tbtn ic" data-a="replay" aria-label="Replay the opening animation" title="Replay the opening animation">${ic('play')}</button>
   <button type="button" class="tbtn" data-a="guide" aria-pressed="${UI.panel==='guide'}">${ic('flag')}<span>Guide</span></button><div class="pals" role="group" aria-label="Accent colour">${[['emerald','#0B7A68'],['indigo','#3F4FD0'],['plum','#8A3FA8']].map(p=>`<button type="button" data-a="pal" data-v="${p[0]}" style="--c:${p[1]}" aria-pressed="${UI.pal===p[0]}" aria-label="${p[0]} accent" title="${p[0]} accent"></button>`).join('')}</div><button type="button" class="tbtn ic" data-a="theme" aria-label="Light or dark" title="Light or dark">${ic(UI.theme==='dark'?'sun':'moon')}</button><button type="button" class="tbtn ic" data-a="reset" aria-label="Reset the demo" title="Reset the demo">${ic('refresh')}</button></div></div></div>
 <div class="work-area">${railHTML()}<div class="stage v-${v}"><div class="stagein">${stage}</div></div></div>
 ${UI.panel==='guide'?guideHTML():''}${UI.panel==='wa'?`<aside class="panel wap"><header><h2 class="serif">WhatsApp</h2><button type="button" class="xb" data-a="closepanel" aria-label="Close">${ic('x')}</button></header><div class="dv dv-wa" data-dev="wa">${waHTML(D.wa)}</div></aside>`:''}
 <div id="toast" aria-live="polite">${UI.toast?`<div class="toast ${UI.toast.k}">${ic(UI.toast.k==='wait'?'alert':'check')}<span>${esc(UI.toast.t)}</span></div>`:''}</div>`}

/* ---------- the session: the preview comes back exactly where it was closed ----------
   Everything a real app would keep is kept: who is signed in, the open screen and tab, scroll, drafts, the outbox,
   the theme. Flutter: a secure token, the route stack and the form drafts in local storage, restored before the first frame. */
const SKEY='rvt_r1_preview_s3',TRANSIENT=['flash','splash','push','party','sh','fh','pt','spT','_k','_n','_sk','toEnd','seen'];
let SCROLL={},BOOT=true;
const mastersSnap=()=>({trades:TRADES.map(t=>Object.assign({},t)),etr:ETYPES.map(e=>e.tr.slice()),dt:DTYPES.map(d=>[d.client,d.appr])});
function mastersApply(m){TRADES.slice(m.trades.length).forEach(t=>delete TX[t.id]);TRADES.length=Math.min(TRADES.length,m.trades.length);m.trades.slice(TRADES.length).forEach(t=>{TRADES.push(t);TX[t.id]=t});
 m.etr.forEach((tr,i)=>{if(ETYPES[i])ETYPES[i].tr=tr.slice()});m.dt.forEach((f,i)=>{if(DTYPES[i]){DTYPES[i].client=f[0];DTYPES[i].appr=f[1]}})}
const M0=JSON.stringify(mastersSnap());
function save(){try{document.querySelectorAll('#app [data-sc]').forEach(el=>{const d=el.closest('[data-dev]');SCROLL[(d?d.dataset.dev:'')+':'+el.dataset.sc]=[el.scrollTop,el.scrollLeft]});
  const devs={},ui={};Object.keys(UI.devs).forEach(k=>{const o={};Object.keys(UI.devs[k]).forEach(p=>{if(!TRANSIENT.includes(p))o[p]=UI.devs[k][p]});devs[k]=o});
  Object.keys(UI).forEach(k=>{if(!['devs','toast','focus','restored'].includes(k))ui[k]=UI[k]});
  localStorage.setItem(SKEY,JSON.stringify({v:3,DB,ui,devs,masters:mastersSnap(),sc:SCROLL}))}catch(e){}}
const queueSave=()=>{clearTimeout(queueSave.h);queueSave.h=setTimeout(save,350)};
function restore(){try{const raw=localStorage.getItem(SKEY);if(!raw)return false;const s=JSON.parse(raw);if(!s||s.v!==3||!s.DB||!Array.isArray(s.DB.projects)||!s.devs)return false;
  DB=s.DB;Object.assign(UI,s.ui);Object.keys(UI.devs).forEach(k=>{if(s.devs[k])UI.devs[k]=Object.assign(newDev(k,UI.devs[k].phone),s.devs[k])});mastersApply(s.masters);SCROLL=s.sc||{};
  OBU=Math.max(0,...Object.values(UI.devs).flatMap(d=>d.ob?d.ob.ents.map(e=>e.u||0):[]));UI.toast=null;return true}catch(e){return false}}

/* ---------- motion that needs a script: sliding selectors, tap rings, confetti, count-ups ---------- */
/* the clock the endless animations keep their phase by; a phone stops it while they rest */
let tNow=()=>((performance.now()-T0)/1000).toFixed(2);
const T0=performance.now(),RM=()=>UI.motion!=='on'&&matchMedia('(prefers-reduced-motion: reduce)').matches,SL={};let TAP=null;
/* the opening: the same splash at the size of the whole window, once, before the log-in page */
function intro(){if(RM())return;const old=document.getElementById('intro'),app=document.getElementById('app'),d=document.createElement('div');if(old)old.remove();d.id='intro';d.className='splash big';d.setAttribute('aria-hidden','true');d.innerHTML=splashInner(false);document.body.appendChild(d);
 app.classList.add('intro');UI.devs.desk._k='';clearTimeout(intro.h);intro.h=setTimeout(()=>{d.remove();app.classList.remove('intro')},5400)}
/* one indicator per tab bar, segment and menu; it slides from where it was to where it is now */
function sliders(root){root.querySelectorAll('.tabs,.seg,.vseg,.gn-menu,.pnav').forEach(c=>{const act=c.querySelector(':scope>[aria-selected="true"],:scope>[aria-pressed="true"],:scope>[aria-current]');if(!act)return;
  const d=c.closest('[data-dev]'),first=c.querySelector('[data-a]'),key=(d?d.dataset.dev:'top')+'|'+c.classList[0]+'|'+(first?first.dataset.a+':'+String(first.dataset.v||'').split('=')[0]:'');
  const r={x:act.offsetLeft,y:act.offsetTop,w:act.offsetWidth,h:act.offsetHeight},i=document.createElement('i');i.className='sld';i.style.cssText=`left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px`;c.prepend(i);
  const o=SL[key];SL[key]=r;if(o&&(o.x!==r.x||o.w!==r.w)&&r.w&&!RM())i.animate([{transform:`translate(${o.x-r.x}px,${o.y-r.y}px) scaleX(${o.w/r.w})`},{transform:'none'}],{duration:420,easing:'cubic-bezier(.3,1.35,.5,1)'})})}
function tapRing(){const fx=document.getElementById('fx');if(!TAP||!fx||RM()){TAP=null;return}const i=document.createElement('i');i.className='tapr';i.style.left=TAP.x+'px';i.style.top=TAP.y+'px';fx.appendChild(i);setTimeout(()=>i.remove(),650);TAP=null}
/* a burst of gold dust for the moments that matter, drawn at the screen's own pixel density */
function confetti(rect){const fx=document.getElementById('fx');if(!fx||RM()||!rect.width)return;const dpr=Math.min(3,window.devicePixelRatio||1),c=document.createElement('canvas'),W=rect.width,H=rect.height;c.width=W*dpr;c.height=H*dpr;c.style.cssText=`left:${rect.left}px;top:${rect.top}px;width:${W}px;height:${H}px`;fx.appendChild(c);
 const g=c.getContext('2d'),cols=['#F8D074','#E2A534','#FFF3C9','#EDCB7C'],P=[];g.scale(dpr,dpr);g.globalCompositeOperation='lighter';
 for(let i=0;i<70;i++){const a=Math.random()*6.28,v=1.5+Math.random()*6.5;P.push({x:W/2,y:H*.46,vx:Math.cos(a)*v,vy:Math.sin(a)*v-1.2,r:.8+Math.random()*2.2,ph:Math.random()*6.28,c:cols[i%cols.length],star:i%5===0})}
 const t0=performance.now();(function step(t){const k=(t-t0)/1900;g.clearRect(0,0,W,H);if(k>=1||!c.isConnected){c.remove();return}
  P.forEach(p=>{p.vx*=.965;p.vy=p.vy*.965+.045;p.x+=p.vx;p.y+=p.vy;const tw=.55+.45*Math.sin(p.ph+k*22),al=Math.max(0,1-k*k)*tw;g.globalAlpha=al;g.fillStyle=p.c;g.shadowColor='#E2A534';g.shadowBlur=8;
   if(p.star){const r=p.r*2.6;g.beginPath();g.moveTo(p.x,p.y-r);g.quadraticCurveTo(p.x,p.y,p.x+r,p.y);g.quadraticCurveTo(p.x,p.y,p.x,p.y+r);g.quadraticCurveTo(p.x,p.y,p.x-r,p.y);g.quadraticCurveTo(p.x,p.y,p.x,p.y-r);g.fill()}else{g.beginPath();g.arc(p.x,p.y,p.r,0,6.28);g.fill()}});requestAnimationFrame(step)})(t0)}
function countUp(root){if(RM())return;root.querySelectorAll('.enter [data-cu]').forEach(el=>{const to=+el.dataset.cu;if(!(to>0)||to>999)return;const sc=el.closest('.pscr'),sp=(sc&&sc.querySelector('.splash'))||document.getElementById('intro'),t0=performance.now()+(sp?(sp.classList.contains('quick')?1300:3350):0)+120,d=850;el.textContent='0';
  const step=t=>{const k=Math.max(0,Math.min(1,(t-t0)/d)),e=1-Math.pow(1-k,3);el.textContent=Math.round(to*e);if(k<1&&el.isConnected)requestAnimationFrame(step)};requestAnimationFrame(step)})}
function afterRender(root){sliders(root);countUp(root);tapRing();
 root.querySelectorAll('.pbody').forEach(b=>{if(b.scrollTop>6)b.closest('.pscr').classList.add('scrolled')});
 Object.values(UI.devs).forEach(d=>{const box=root.querySelector('.dv-'+d.id+' .pscr')||root.querySelector('.dv-'+d.id+' .bw');
  if(d.splash&&d.spT){const el=root.querySelector('.dv-'+d.id+' .splash'),dt=performance.now()-d.spT;if(el&&dt>80&&el.getAnimations)el.getAnimations({subtree:true}).forEach(a=>{try{a.currentTime=(a.currentTime||0)+dt}catch(e){}})}
  if(d.party){d.party=false;if(box)confetti(box.getBoundingClientRect())}});
 queueSave()}
/* what this person may not do: the buttons of those functions are hidden (styles.css, html[data-nacc]) */
function accMark(){let n='';try{n=ACCK.map(x=>x[0]).filter(k=>!can(k)).join(' ')}catch(e){}if(document.documentElement.dataset.nacc!==n)document.documentElement.dataset.nacc=n}
function render(){accMark();({staff:['staff'],agency:['agency'],client:['client'],all:['staff','agency','client']}[UI.view]||[]).forEach(k=>{const d=UI.devs[k];if(!d.seen){d.seen=true;splash(d,UI.restored&&(d.signed||(k==='client'&&UI.linkMode)))}});
 const root=document.getElementById('app'),sc={},key=el=>{const d=el.closest('[data-dev]');return (d?d.dataset.dev:'')+':'+el.dataset.sc};
 root.querySelectorAll('[data-sc]').forEach(el=>{sc[key(el)]=[el.scrollTop,el.scrollLeft]});const ae=document.activeElement,fid=ae&&ae.id,ss=ae&&ae.selectionStart;
 root.style.setProperty('--t',tNow());
 root.innerHTML=shellHTML();
 root.querySelectorAll('[data-sc]').forEach(el=>{const s=sc[key(el)]||(BOOT&&SCROLL[key(el)]);if(s){el.scrollTop=s[0];el.scrollLeft=s[1]}});
 Object.values(UI.devs).forEach(d=>{if(d.toEnd){d.toEnd=false;const b=root.querySelector('.dv-'+d.id+' .pbody');if(b)b.scrollTop=b.scrollHeight}});afterRender(root);
 const want=UI.focus||fid;UI.focus=null;if(want){const el=document.getElementById(want);if(el&&el.tagName!=='SELECT'){el.focus({preventScroll:true});try{el.setSelectionRange(ss==null?99:ss,ss==null?99:ss)}catch(e){}}}}
function boot(){const root=document.getElementById('app'),html=document.documentElement,back=restore();
 html.dataset.rv=UI.theme==='dark'?'dark':'light';html.dataset.pal=UI.pal||'emerald';html.dataset.motion=UI.motion||'';
 if(!document.getElementById('fx')){const f=document.createElement('div');f.id='fx';f.setAttribute('aria-hidden','true');document.body.appendChild(f)}
 const run=(el,fn)=>{fn(el.dataset.v==null?'':el.dataset.v,el,devOf(el));render()};
 root.addEventListener('click',e=>{const el=e.target.closest('[data-a]');if(!el||el.disabled)return;if(el.classList.contains('ovl')&&e.target!==el)return;const fn=A[el.dataset.a];if(!fn)return;
  if(e.clientX||e.clientY)TAP={x:e.clientX,y:e.clientY};
  if(el.dataset.a==='close'&&!RM()){const ov=el.closest('.ovl');if(ov){if(ov.classList.contains('out'))return;ov.classList.add('out');TAP=null;return setTimeout(()=>run(el,fn),170)}}
  run(el,fn)});
 root.addEventListener('input',e=>{const el=e.target,dev=devOf(el);if(el.dataset.m)dev.f[el.dataset.m]=el.value;if(el.dataset.mo&&dev.ob)setPath(dev.ob,el.dataset.mo,el.value);queueSave();if(el.dataset.ri&&!e.isComposing)render()});
 root.addEventListener('change',e=>{const el=e.target,dev=devOf(el);if(el.dataset.top){UI[el.dataset.top]=/^\d+$/.test(el.value)?+el.value:el.value;if(el.dataset.top!=='user'){UI.devs.agency.stack=[{s:'home'}];UI.devs.client.stack=[{s:'home'}]}if(el.dataset.top==='agency')UI.lang.agency=agOf(el.value).lang;return render()}
  if(el.dataset.ui){dev[el.dataset.ui]=el.value;return render()}if(el.dataset.r)render()});
 root.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.tagName==='INPUT'){const id=e.target.id||'';const b=id.endsWith('_m_text')?'addpt':id.endsWith('_aq')?'aask':/_th_/.test(id)?'thsend':null;if(b){const box=e.target.closest('.composer,.qa'),btn=box&&box.querySelector(`[data-a="${b}"]`);if(btn){e.preventDefault();btn.click()}}
   /* Enter on a date typed in the calendar uses it; Enter on what has to change sends it back */
   const own=id.endsWith('_cal_t')?'.calw .use':id.endsWith('_pc_note')?'.ovl [data-a="dochange"]':null,ob=own&&e.target.closest('.dlg')&&e.target.closest('.dlg').querySelector(own);if(ob){e.preventDefault();ob.click()}}
  if((e.key==='Enter'||e.key===' ')&&e.target.matches&&e.target.matches('g[data-a]')){e.preventDefault();e.target.dispatchEvent(new MouseEvent('click',{bubbles:true}))}});
 /* a phone's bar turns to glass once its page is scrolled; on the desk a soft light follows the pointer across a card */
 root.addEventListener('scroll',e=>{const t=e.target;if(t.classList&&t.classList.contains('pbody')){const s=t.closest('.pscr');if(s)s.classList.toggle('scrolled',t.scrollTop>6)}queueSave()},true);
 root.addEventListener('pointermove',e=>{const k=e.target.closest&&e.target.closest('.ink,.card,.todo,.site,.kpi');if(!k||e.pointerType==='touch')return;const r=k.getBoundingClientRect();k.style.setProperty('--mx',Math.round(e.clientX-r.left)+'px');k.style.setProperty('--my',Math.round(e.clientY-r.top)+'px')});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){let ch=false;Object.values(UI.devs).forEach(d=>{if(d.sheet){d.sheet=null;ch=true}});if(UI.panel){UI.panel=null;ch=true}if(ch)render()}});
 window.addEventListener('pagehide',save);document.addEventListener('visibilitychange',()=>{if(document.hidden)save()});
 if(back){UI.restored=true;if(Object.values(UI.devs).some(d=>d.signed))toast('Welcome back. Everything is where you left it.')}
 if(!back)intro();
 render();BOOT=false}
