/* The adapter between the preview's screens and the server.
   - One snapshot fills DB and the master lists; the project picture and Today come ready-made from the server.
   - Every operation still runs locally first, exactly as in the preview, so the screen answers at once;
     it is then sent to the server, and the next snapshot is the truth.
   - The desk comes back where it was closed: section, project, tab, scroll and drafts (not the records). */
const LIVE={queue:[],busy:false,ids:{},saving:false,depth:0,img:{}},LKEY='rvt_desk_ui_v1';
/* records made on the screen before the server answers carry ids from 9,000,001 up, so they never meet a real one */
const LOCAL0=9e6,localSeq=()=>({lid:LOCAL0,did:LOCAL0,ptid:LOCAL0,bid:LOCAL0,vid:LOCAL0,pid:LOCAL0,q:LOCAL0});
const EMPTY_PIC={status:'ok',progress:{ag:[0,0],dr:[0,0],wk:[0,0,0,0],pt:[0,0,0,0]},week:{rel:0,started:0,done:0,closed:0},blockers:[],next:{revert:[],agencies:[],client:[]},noDwg:[]};

async function rpc(method,args){
 const r=await fetch('/web/dataset/call_kw/rvt.desk/'+method,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({jsonrpc:'2.0',method:'call',id:Date.now(),params:{model:'rvt.desk',method,args:args||[],kwargs:{}}})});
 let j=null;try{j=await r.json()}catch(e){}
 if(!j)throw new Error('The server did not answer. Check the connection and try again.');
 if(j.error){const d=j.error.data||{};if(j.error.code===100||/SessionExpired/.test(d.name||'')){location.href='/web/login?redirect='+encodeURIComponent('/rvt/desk');throw new Error('session')}
  throw new Error(d.message||j.error.message||'Something went wrong.')}
 return j.result}

function applySnapshot(s){LIVE.sig=JSON.stringify(s);const m=s.masters,fill=(a,b)=>{a.length=0;b.forEach(x=>a.push(x))},clear=o=>Object.keys(o).forEach(k=>delete o[k]);
 fill(TRADES,m.trades);clear(TX);TRADES.forEach(t=>TX[t.id]=t);fill(ETYPES,m.etypes);clear(ETX);ETYPES.forEach(e=>ETX[e.n]=e);
 fill(PRESETS,m.presets);fill(EXTRAS,m.extras);fill(DEFAULT_TRADES,m.default_trades);fill(DTYPES,m.dtypes);
 if(m.templates){clear(TPL);Object.assign(TPL,m.templates)}
 const [y,mo,d]=s.today_date.split('-').map(Number);BASE=Date.UTC(y,mo-1,d);
 const t=new Date(),h=t.getHours();NOW=((h%12)||12)+':'+String(t.getMinutes()).padStart(2,'0')+(h<12?' am':' pm');
 const seq=DB&&DB.seq&&DB.seq.ptid>=LOCAL0?DB.seq:localSeq();
 DB=Object.assign(seed(),{seq,set:s.set,staff:s.staff,agencies:s.agencies,projects:s.projects,drawings:s.drawings,visits:s.visits,points:s.points,bills:s.bills,wa:s.wa,notes:s.notes||[],
  features:s.features,mytasks:s.mytasks,today:s.today,company:s.company,prefix:s.prefix,admin:s.admin});
 DB.projects.forEach(p=>{if(p.pic)p.pic.noDwg=p.pic.noDwg.map(x=>p.lines.find(l=>l.id===x.id)).filter(Boolean)});
 UI.user=s.me;document.documentElement.dataset.nof=Object.keys(s.features).filter(k=>!s.features[k]).join(' ')}

/* the picture and Today are the server's: one source for the desk, the app and Review */
picture=function(p){return p.pic||EMPTY_PIC};
todayFor=function(){return DB.today.map(n=>Object.assign({p:pOf(n.pid)},n)).filter(n=>n.p)};
canSee=function(){return true};

/* ---------- sending: in order, one at a time; then a fresh snapshot ---------- */
const mapIds=v=>typeof v==='string'?(LIVE.ids[v]||v):Array.isArray(v)?v.map(mapIds):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,mapIds(x)])):v;
function remapUI(){const d=UI.devs.desk;['drawer','vid'].forEach(k=>{if(LIVE.ids[d[k]])d[k]=LIVE.ids[d[k]]});if(d.sheet)Object.keys(d.sheet).forEach(k=>{if(LIVE.ids[d.sheet[k]])d.sheet[k]=LIVE.ids[d.sheet[k]]})}
function sync(name,args,tmp){LIVE.queue.push({name,args,tmp});pump()}
async function pump(){if(LIVE.busy)return;LIVE.busy=true;document.documentElement.dataset.sync='1';let failed=null;
 while(LIVE.queue.length){const o=LIVE.queue.shift();try{const r=await rpc('op',[o.name,mapIds(o.args)]);if(o.tmp&&r&&r.id)LIVE.ids[o.tmp]=r.id}catch(e){failed=e;LIVE.queue.length=0}}
 try{applySnapshot(await rpc('snapshot'));remapUI()}catch(e){failed=failed||e}
 LIVE.busy=false;delete document.documentElement.dataset.sync;
 if(failed&&failed.message!=='session')toast(failed.message,'bad');
 if(LIVE.queue.length)return pump();
 render()}
async function reload(quiet){try{const s=await rpc('snapshot');if(quiet&&JSON.stringify(s)===LIVE.sig)return;applySnapshot(s);render()}catch(e){if(e.message!=='session'&&!quiet)toast(e.message,'bad')}}

/* an operation called inside another one (a release that frees waiting lines) is the server's work, not a second request */
function wrapOP(name,send){const orig=OP[name];if(!orig)return;OP[name]=function(){LIVE.depth++;let r;try{r=orig.apply(OP,arguments)}finally{LIVE.depth--}if(!LIVE.depth)send.apply(null,[r].concat(Array.prototype.slice.call(arguments)));return r}}
wrapOP('setLine',(r,p,l,st,x)=>sync('set_line',{line:l.id,state:st,cause:(x||{}).cause||'',ref:(x||{}).ref||'',note:(x||{}).note||'',agency:l.ag||''}));
wrapOP('assign',(r,p,t,ag,by)=>sync('assign',{project:p.id,trade:t,agency:ag||'',by:by==null||isNaN(by)?7:by}));

/* drawings */
wrapOP('sendForApproval',(r,d,note)=>{const f=LIVE.pdf;LIVE.pdf=null;sync('send_for_approval',{drawing:d.id,note:note||'',file:f?f.b64:'',name:f?f.name:''})});
wrapOP('approve',(r,d)=>sync('approve',{drawing:d.id}));
wrapOP('sendBack',(r,d,note)=>sync('send_back',{drawing:d.id,note:note||''}));
wrapOP('release',(r,d,to)=>sync('release',{drawing:d.id,to}));
wrapOP('answer',(r,d,qid,text)=>sync('answer',{question:qid,text}));
wrapOP('ask',(r,d,by,byName,text,photo,via)=>sync('ask',{drawing:d.id,by,name:byName||'',text},d.q[d.q.length-1].id));
wrapOP('say',(r,d,by,text)=>sync('say',{drawing:d.id,to:by,text},d.q[d.q.length-1].id));

/* points and MOM */
const takeImg=(...keys)=>{for(const k of keys){const g=LIVE.img[k];if(g){delete LIVE.img[k];return g.b64}}return ''};
wrapOP('addPoint',(x,o)=>sync('add_point',{pid:o.pid,vid:o.vid||'',kind:o.kind,party:o.party||'',text:o.text,e:o.e||'',t:o.t||'',due:o.due==null?null:+o.due,photo:o.photo?takeImg('m_photo','rp_photo'):''},x.id));
wrapOP('closePoint',(r,x,note,photo)=>sync('close_point',{point:x.id,note:note||'',photo:photo?takeImg('cp_photo'):''}));
wrapOP('confirmPoint',(r,x)=>sync('confirm_point',{point:x.id}));
wrapOP('reopenPoint',(r,x)=>sync('reopen_point',{point:x.id}));
/* the check of a point an agency marked done */
wrapOP('solvePoint',(r,x)=>sync('solve_point',{point:x.id}));
wrapOP('changePoint',(r,x,note)=>sync('change_point',{point:x.id,note:note||''}));
wrapOP('seenNotes',()=>sync('seen_notes',{}));
wrapOP('sendParty',(n,v,key)=>{if(n)sync('send_party',{visit:v.id,key})});

/* bills: asked, uploaded, reviewed and paid on the server; the document and the proof are real files */
const takeFile=k=>{const g=LIVE.img[k];delete LIVE.img[k];return g?{file:g.b64,name:g.name}:{file:'',name:''}};
wrapOP('askBill',(b,o)=>sync('ask_bill',{project:o.pid,agency:o.ag,trade:o.t||'',what:o.what,upto:o.upto||null,billedTo:o.billedTo||''},b.id));
wrapOP('uploadBill',(r,b,o)=>sync('upload_bill',Object.assign({bill:b.id,no:o.no==='—'?'':o.no,amount:o.amount},takeFile('ub_doc'))));
wrapOP('reviewBill',(r,b,ok,reason)=>sync('review_bill',{bill:b.id,ok:!!ok,reason:reason||''}));
wrapOP('pay',(r,b,o)=>sync('pay_bill',Object.assign({bill:b.id,amount:o.amount,by:o.by,mode:o.mode},takeFile('py_proof'))));

/* messages: a reminder is sent by the server; the screen's own WhatsApp list is the server's log */
notify=function(){};
wrapOP('remind',(r,to,pid,text)=>sync('remind',{to,project:pid,text}));

/* ---------- actions that differ from the preview: they talk to the server or leave the desk ---------- */
const wrapA=(name,after)=>{const o=A[name];A[name]=function(v,el,dev){const r=o.apply(A,arguments);after(v,el,dev);return r}};
A.signin=function(){};A.asuser=function(){};A.reset=function(){};A.scen=function(){};A.setview=function(){};A.jump=function(){};A.guide=function(){};A.wapanel=function(){};A.replay=function(){intro()};
A.signout=function(){try{localStorage.removeItem(LKEY)}catch(e){}const f=document.createElement('form'),add=(k,v)=>{const i=document.createElement('input');i.type='hidden';i.name=k;i.value=v;f.appendChild(i)};
 f.method='post';f.action='/web/session/logout';add('csrf_token',(document.querySelector('meta[name="csrf-token"]')||{}).content||'');add('redirect','/web/login');document.body.appendChild(f);f.submit()};
A.backoffice=function(){save();location.href=DB.prefix};
A.opentask=function(v){window.open(DB.prefix+'/m-project.task/'+v,'_blank','noopener')};
A.taskboard=function(v){window.open(DB.prefix+'/project/'+v+'/tasks','_blank','noopener')};
A.refresh=function(){reload()};
A.taskent=function(v,el,dev){const [pid,tid]=v.split('|'),p=pOf(pid),t=p.tasks.find(x=>String(x.id)===tid);if(!t)return;const ty=guessType(t.n);
 p.ents.push({id:'e'+t.id,n:t.n,ty});p.tasks=p.tasks.filter(x=>x!==t);sync('task_entity',{task:t.id,type:ty});toast(`“${t.n}” is now a room of ${p.name}. Tick its trades in Project configuration.`)};

/* a real file from the computer: a drawing's PDF, a point's photo */
function pickFile(accept,max,tooBig,done){const i=document.createElement('input');i.type='file';i.accept=accept;
 i.onchange=()=>{const file=i.files[0];if(!file)return;if(file.size>max){toast(tooBig,'wait');return render()}
  const rd=new FileReader();rd.onload=()=>done(file,String(rd.result).split(',')[1]);rd.readAsDataURL(file)};i.click()}
/* drawings: a real PDF is chosen, kept until it is sent, and shown where the preview drew a sample sheet */
const fmtSize=n=>n>=1e6?(n/1e6).toFixed(1)+' MB':Math.max(1,Math.round(n/1e3))+' KB';
const lastFile=d=>[...d.revs].reverse().find(x=>x.file);
A.pickpdf=function(v,el,dev){pickFile('application/pdf,.pdf',25e6,'That file is larger than 25 MB. Export a lighter PDF.',(file,b64)=>{LIVE.pdf={name:file.name,size:file.size,b64};dev.f.sa_file=true;render()})};
A.droppdf=function(v,el,dev){LIVE.pdf=null;dev.f.sa_file=false};
const sendappr0=SHEETS.sendappr;SHEETS.sendappr=function(dev,s){const o=sendappr0(dev,s),f=dev.f,p=LIVE.pdf,r=cur(dOf(s.id)),on=!!(f.sa_file&&p);
 const label=on?`<b>${esc(p.name)}</b> · ${fmtSize(p.size)} · tap to remove`:r.file?`<b>${esc(r.fname)}</b> · on file · tap to replace`:'Choose the PDF';
 o.body=o.body.replace(/<button type="button" class="drop[^]*?<\/button>/,`<button type="button" class="drop ${on||r.file?'on':''}" data-a="${on?'droppdf':'pickpdf'}">${ic(on||r.file?'file':'plus')}<span>${label}</span></button>`);return o};
const dosend0=A.dosend;A.dosend=function(v,el,dev){const d=dOf(v);if(dev.f.sa_file&&!LIVE.pdf)dev.f.sa_file=false;if(!dev.f.sa_file&&cur(d).file)dev.f.sa_file=true;return dosend0.call(A,v,el,dev)};
const dwgPaper0=dwgPaper;dwgPaper=function(d){const r=lastFile(d);return r?`<div class="pdfw"><iframe class="pdfv" title="${esc(sheetNo(d)+' '+d.title)}" src="/rvt/desk/revision/${r.id}/pdf#view=FitH&toolbar=0"></iframe></div>`:dwgPaper0(d)};
wrapA('dstart',v=>sync('dstart',{drawing:v}));
wrapA('newrev',v=>sync('new_revision',{drawing:v}));

/* MOM: a visit is started on the server; a photo is a real photo; the PDF is the real PDF */
const startmom0=A.startmom;A.startmom=function(v,el,dev){const had=new Set(DB.visits.map(x=>x.id));startmom0.call(A,v,el,dev);const nv=DB.visits.find(x=>!had.has(x.id));if(nv)sync('start_visit',{project:nv.pid},nv.id)};
wrapA('finishvisit',v=>sync('finish_visit',{visit:v}));
const FILE_TOGS={m_photo:'image/*',rp_photo:'image/*',cp_photo:'image/*',ub_doc:'image/*,application/pdf',py_proof:'image/*,application/pdf'};
const tog0=A.tog;A.tog=function(v,el,dev){const accept=FILE_TOGS[v];if(!accept)return tog0.call(A,v,el,dev);
 if(dev.f[v]&&LIVE.img[v]){dev.f[v]=false;dropImg(v);return}
 dev.f[v]=false;pickFile(accept,12e6,'That file is larger than 12 MB.',(file,b64)=>{dropImg(v);LIVE.img[v]={b64,name:file.name,url:/^image\//.test(file.type)?URL.createObjectURL(file):''};dev.f[v]=true;render()})};
/* the photo just chosen shows on its button, from the file itself */
const dropImg=k=>{const g=LIVE.img[k];if(g&&g.url)try{URL.revokeObjectURL(g.url)}catch(e){}delete LIVE.img[k]};
pickedImg=function(k){const g=LIVE.img[k];return g&&g.url?g.url:''};
wrapA('billto',v=>{const [id,to]=v.split('|');sync('bill_to',{bill:id,to})});
/* a bill's document is the file that was uploaded, or nothing: never a made-up file name */
const bill0=SHEETS.bill;SHEETS.bill=function(dev,s){const o=bill0(dev,s),b=billOf(s.id),id=String(b.id).replace(/\D/g,'');
 o.body=o.body.replace(/<div class="docrow">[^]*?<\/div>/,b.doc&&+id<9e6?`<a class="docrow" href="/rvt/desk/bill/${id}/document" target="_blank" rel="noopener">${ic('file')}<span><b>${b.doc==='pdf'?'PDF':'Photo'} of the bill</b> · open</span></a>`:'');return o};
const digits=v=>String(v==null?'':v).replace(/\D/g,'');
phOf=function(kind,x,after){const id=digits(x.id);if(!id||+id>=LOCAL0)return `<span class="ph ${after?'aft':''}"></span>`;
 const q=after?'&close=1':'',cap=(x.text||'')+(kind==='point'&&x.photo&&x.cphoto?(after?' · after':' · before'):'');
 /* data-big and data-cap: the larger picture and its line, shown while the pointer rests on the small one (photoHover below) */
 return `<span class="ph real ${after?'aft':''}" role="button" tabindex="0" data-a="photo" data-v="${kind}|${x.id}${after?'|1':''}" data-big="/rvt/desk/${kind}/${id}/photo?size=view${q}" data-cap="${esc(cap)}" aria-label="${after?'Photo after: open':'Photo: open'}" style="background-image:url(/rvt/desk/${kind}/${id}/photo?size=thumb${q})"></span>`};
/* The pointer rests on a small photo: the larger one shows beside it, with what the point says, as the earlier MOM
   register did. One floating box outside the screens, so no card or table cuts it off; it never takes the pointer. */
const photoHover=(()=>{let box=null,cur=null;const hide=()=>{cur=null;if(box)box.hidden=true};
 /* the box takes its size from the photo (as large as fits: 560 wide, 72% of the window high), then goes beside the small
    photo, to its left when there is room, and never off the window. It shows once the picture is there. */
 const show=()=>{if(!box||!cur)return;const img=box.firstChild;if(!img.naturalWidth)return;
  const k=Math.min(Math.min(560,innerWidth*.42)/img.naturalWidth,Math.min(innerHeight*.72,660)/img.naturalHeight,1),w=Math.round(img.naturalWidth*k),h=Math.round(img.naturalHeight*k);
  img.style.width=w+'px';img.style.height=h+'px';box.style.width=Math.max(w+18,230)+'px';box.hidden=false;
  const r=cur.getBoundingClientRect(),q=box.getBoundingClientRect();
  box.style.left=Math.round(r.left-q.width-16>=10?r.left-q.width-16:Math.min(r.right+16,innerWidth-q.width-10))+'px';box.style.top=Math.round(Math.max(12,Math.min(r.top+r.height/2-q.height/2,innerHeight-q.height-12)))+'px'};
 document.addEventListener('mouseover',e=>{const el=e.target.closest&&e.target.closest('.ph.real[data-big]');if(!el)return hide();if(el===cur)return;
  if(!box){box=document.createElement('div');box.id='phover';box.hidden=true;box.setAttribute('aria-hidden','true');box.innerHTML='<img alt=""><p></p>';document.body.appendChild(box);box.firstChild.addEventListener('load',show)}
  const img=box.firstChild;cur=el;box.lastChild.textContent=el.dataset.cap||'';box.lastChild.hidden=!el.dataset.cap;
  if(img.dataset.src!==el.dataset.big){box.hidden=true;img.removeAttribute('src');img.dataset.src=el.dataset.big;img.src=el.dataset.big}else show()});
 document.addEventListener('scroll',hide,true);document.addEventListener('mousedown',hide,true);document.addEventListener('keydown',hide,true);return {hide}})();
/* a redraw takes the small photo away from under the pointer: the large one goes with it */
const renderD=render;render=function(){photoHover.hide();renderD()};
ptPhoto=function(x,after){const id=digits(x.id);if(!id||+id>=LOCAL0)return `<span class="ph full ${after?'aft':''}"></span>`;
 return `<img class="phv" alt="${after?'After':'Photo'}" role="button" tabindex="0" data-a="photo" data-v="point|${x.id}|${after?1:0}" src="/rvt/desk/point/${id}/photo?size=view${after?'&close=1':''}">`};
A.photo=function(v,el,dev){const [a,b,c]=String(v).split('|'),s=b?{kind:a,id:b,close:c==='1'}:{kind:'point',id:a};s.back=dev.sheet&&dev.sheet.k!=='photo'?dev.sheet:null;openSheet(dev,'photo',s)};
SHEETS.photo=function(dev,s){const x=s.kind==='point'?ptOf(s.id):null;return {title:x?(x.cphoto?(s.close?'After':'Before'):'Photo')+' · point '+x.n:'Photo sent with the question',sub:x?x.text:'',wide:true,
 body:`<div class="phw"><img class="phv" alt="Photo" src="/rvt/desk/${s.kind==='question'?'question':'point'}/${digits(s.id)}/photo?size=view${s.close?'&close=1':''}"></div>`,foot:Bt(s.back?'Back':'Close','close',null,'ghost')}};
SHEETS.pdf=function(dev,s){return {title:s.kind==='open'?'Open points PDF':'MOM PDF',sub:s.kind==='points'?'The points of the project, as chosen. Save or print it from the bar above the page.':'What the party receives on WhatsApp',wide:true,
 body:`<div class="pdfw"><iframe class="pdfv" title="PDF" src="/rvt/desk/mom/pdf?kind=${encodeURIComponent(s.kind)}&a=${encodeURIComponent(s.a||'')}&b=${encodeURIComponent(s.b||'all')}&v=${encodeURIComponent(s.v||'')}&st=${encodeURIComponent(s.st||'open')}#view=FitH"></iframe></div>`,foot:Bt('Close','close',null,'ghost')}};
/* Setup › Earlier MOM: the real verification report of the move, read when the tab is opened */
function etlReport(dev){const R=LIVE.etl;if(!isOwner()&&!DB.admin)return `<div class="note">${ic('lock')}The verification report of the move is for owners.</div>`;
 if(!R){if(!LIVE.etlBusy){LIVE.etlBusy=true;rpc('op',['etl_report',{}]).then(r=>{LIVE.etl=r}).catch(e=>{LIVE.etl={error:e.message}}).finally(()=>{LIVE.etlBusy=false;render()})}
  return `<div class="note">${ic('clock')}Reading the earlier entries…</div>`}
 if(R.error)return `<div class="note bad">${ic('alert')}${esc(R.error)}</div>`;
 const T=R.rows.reduce((a,r)=>a.map((v,i)=>v+r.b[i]),[0,0,0,0,0]),badge=!R.moved?`<span class="pill wait">${ic('clock')}not moved yet</span>`:R.all_equal&&!R.left?`<span class="pill ok">${ic('check')}before = after, every project</span>`:`<span class="pill bad">${ic('alert')}${R.left?R.left+' still to move':'not equal: see the rows'}</span>`;
 return `<div class="kpis">${kpi('Entries moved',R.moved)}${kpi('Open',T[1],'c-wait')}${kpi('Closed',T[2],'c-ok')}${kpi('Photos, by checksum',T[3])}${kpi('Visits',T[4])}</div>${card('Verification report',badge,`<div class="tw"><table class="tb"><thead><tr><th>Project</th><th class="ar">Entries</th><th class="ar">Open</th><th class="ar">Closed</th><th class="ar">Photos</th><th class="ar">Visits</th><th>Check</th></tr></thead><tbody>${R.rows.map(r=>`<tr><td><b>${esc(r.p)}</b></td>${r.b.map((v,i)=>`<td class="ar num">${v}${r.a?` <span class="mu">= ${r.a[i]}</span>`:''}</td>`).join('')}<td>${r.eq==null?pill('to move','wait'):r.eq?pill('equal','ok','check'):pill('different','bad','alert')}</td></tr>`).join('')}</tbody></table></div>
   <div class="note">${ic('info')}<span>Every earlier MOM entry became a point with its text, person, photo, visit date and number, serial number, due date, state, closing note and author. A second run creates nothing. The earlier screens are switched off only after the owner compares three projects and signs off.</span></div>`)}
  ${card('People to match','<span class="mu f12">from the sheet Revert fills in</span>',`<div class="kv"><div><span>People named in earlier entries</span><b>${R.people}</b></div><div><span>Matched through the sheet</span><b class="c-ok">${R.people-R.unmapped}</b></div><div><span>Kept as vendors, listed for review</span><b class="c-wait">${R.unmapped}</b></div><div><span>Entries without a person</span><b>${R.noperson}</b></div></div>`)}`}

A.invite=function(v,el,dev){const [pid,i]=v.split('|'),p=pOf(pid),c=p.client.contacts[+i];if(!c)return;c.inv=true;sync('invite',{project:p.id,contact:c.id});toast(`Invitation to ${c.n} · ${sent()}.`)};
/* the address a client contact opens without the app; it is made by the app's back end, when that is installed */
A.copylink=function(v,el,dev){const p=pOf(v),c=p&&p.client.contacts[0];if(!c)return toast('Add a client contact with a mobile number first.','wait');
 rpc('op',['client_link',{project:p.id,contact:c.id}]).then(r=>{const box=()=>{openSheet(dev,'linkbox',r);render()};
   if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(r.url).then(()=>{toast(`Link copied for ${r.name}. It opens ${p.name} without the app.`);render()},box);else box()})
  .catch(e=>{toast(e.message==='Unknown action.'?'The client link is switched on with the app.':e.message,'wait');render()})};
SHEETS.linkbox=function(dev,s){return {title:'Link for '+s.name,sub:'Opens this project without the app or a sign-in',body:fld('Copy this address',`<input class="inp mono" readonly value="${esc(s.url)}" onfocus="this.select()">`),foot:Bt('Close','close',null,'ghost')}};

/* onboarding: the wizard is the preview's; the result is written by the server in one go.
   A new project starts with the real principal, and with the person who sets it up on its team. */
const obStart0=obStart;obStart=function(dev,pid){const ob=obStart0(dev,pid),u=me();
 if(!DB.staff.some(x=>x.id===ob.principal&&has(x,'principal'))){const pr=DB.staff.find(x=>has(x,'principal'))||DB.staff.find(x=>has(x,'owner'));ob.principal=pr?pr.id:''}
 if(!pid){if(has(u,'coordinator')&&!ob.coords.length)ob.coords=[u.id];if(has(u,'designer')&&!ob.designers.length)ob.designers=[u.id]}return ob};
function obPayload(ob){const p=ob.pid?pOf(ob.pid):null,on=obTrades(ob),ticks=[];ob.ents.forEach(e=>on.forEach(t=>{if(obTick(ob,e,t))ticks.push([String(e.u),t])}));
 return {pid:ob.pid||'',name:ob.name.trim(),client:ob.client.trim(),cphone:(ob.cphone||'').trim(),address:ob.address||'',area:ob.area||'',kind:ob.kind,label:ob.label||'',billedTo:ob.billedTo,
  principal:ob.principal||'',designers:ob.designers,coords:ob.coords,
  ents:ob.ents.map(e=>{const t=e.task&&p?p.tasks.find(x=>x.n===e.task):null;return {u:e.u,n:e.n,ty:e.ty,id:e.id||'',taskId:t?t.id:''}}),
  tr:ob.tr,ticks,dr:DB.features.drawings?ob.dr.filter(d=>d.on&&!d.exists).map(d=>({code:d.code,n:d.n,t:d.t||'',ds:d.ds||'',due:+d.due||0,client:!!d.client,appr:!!d.appr})):[],inv:DB.features.wa?Object.keys(ob.inv).filter(k=>ob.inv[k]):[]}}
A.obfinish=function(v,el,dev){const ob=dev.ob;if(!ob||LIVE.saving)return;if(!ob.name.trim())return toast('Give the project a name first.','wait');
 const was=!!(ob.pid&&pOf(ob.pid)&&pOf(ob.pid).onb);LIVE.saving=true;document.documentElement.dataset.sync='1';
 rpc('op',['onboard',obPayload(ob)]).then(async r=>{applySnapshot(await rpc('snapshot'));dev.ob=null;openProj(dev,r.pid,'picture');dev.sec='projects';flash(dev,was?'Saved':'Project started','check',!was);
   const p=pOf(r.pid);toast(`${p?p.name:'Project'}: ${plural(r.nl,'work line')}${DB.features.drawings?' and '+plural(r.nd,'drawing'):''} added${r.inv?' · '+plural(r.inv,'invitation')+' '+sent():''}.`)})
  .catch(e=>{if(e.message!=='session')toast(e.message,'bad')}).finally(()=>{LIVE.saving=false;if(!LIVE.busy)delete document.documentElement.dataset.sync;render()})};
/* until drawings have their back end the wizard has five steps: 4 leads to the review */
const obgo0=A.obgo;A.obgo=function(v,el,dev){if(!DB.features.drawings&&+v===5)v=dev.ob.step>5?4:6;return obgo0.call(A,v,el,dev)};

/* setup: the preview changes the list on the screen; the server keeps it */
wrapA('setting',v=>sync('setting',{key:v,value:DB.set[v]}));
wrapA('limit',v=>{const k=v.split('|')[0];sync('limit',{key:k,value:DB.set.lim[k]})});
wrapA('ettoggle',v=>{const [n,t]=v.split('|');sync('etype_trade',{type:n,trade:t})});
wrapA('dtflag',v=>{const [i,k]=v.split('|');sync('dtype_flag',{id:DTYPES[+i].id,flag:k})});
const roletog0=A.roletog;A.roletog=function(v){const [s,r]=v.split('|'),u=stf(s),had=u.roles.includes(r);roletog0.apply(A,arguments);if(u.roles.includes(r)!==had)sync('role',{user:s,role:r})};
const addtrade0=A.doaddtrade;A.doaddtrade=function(v,el,dev){const f=dev.f,a={name:(f.nt_n||'').trim(),gu:f.nt_gu||'',hi:f.nt_hi||''},n=TRADES.length;addtrade0.apply(A,arguments);if(TRADES.length>n)sync('add_trade',a,TRADES[TRADES.length-1].id)};
const addagency0=A.doaddagency;A.doaddagency=function(v,el,dev){const f=dev.f,a={name:(f.na_n||'').trim(),trades:f.na_t?[f.na_t]:[],lang:f.na_l||'gu',person:f.na_p||'',phone:f.na_ph||''},n=DB.agencies.length;addagency0.apply(A,arguments);
 if(DB.agencies.length>n){const g=DB.agencies[DB.agencies.length-1],was=g.id;g.id='anew'+Date.now();if(f.a_ag===was)f.a_ag=g.id;sync('add_agency',a,g.id)}};

/* ---------- the window: the desk alone, at the size of the browser ---------- */
shellHTML=function(){const d=UI.devs.desk;d.signed=true;
 const extra=`<button type="button" class="ib" data-a="theme" aria-label="Light or dark" title="Light or dark">${ic(UI.theme==='dark'?'sun':'moon')}</button>${DB.admin?`<button type="button" class="ib" data-a="backoffice" aria-label="Back office" title="Back office">${ic('grid')}</button>`:''}`;
 const h=deskHTML(d).replace('<button type="button" class="ib gn-out"',extra+'<button type="button" class="ib gn-out"');
 return `<div class="stage v-desk"><div class="dv dv-desk" data-dev="desk">${h}</div></div><div id="toast" aria-live="polite">${UI.toast?`<div class="toast ${UI.toast.k}">${ic(UI.toast.k==='ok'?'check':'alert')}<span>${esc(UI.toast.t)}</span></div>`:''}</div>`};

/* ---------- the session: where the desk was closed (never the records) ---------- */
save=function(){try{document.querySelectorAll('#app [data-sc]').forEach(el=>{SCROLL['desk:'+el.dataset.sc]=[el.scrollTop,el.scrollLeft]});
  const d=UI.devs.desk,o={};Object.keys(d).forEach(k=>{if(!TRANSIENT.includes(k))o[k]=d[k]});
  localStorage.setItem(LKEY,JSON.stringify({v:1,user:UI.user,theme:UI.theme,pal:UI.pal,motion:UI.motion,desk:o,sc:SCROLL}))}catch(e){}};
restore=function(){try{const s=JSON.parse(localStorage.getItem(LKEY)||'null');if(!s||s.v!==1)return false;UI.theme=s.theme||'light';UI.pal=s.pal||'emerald';UI.motion=s.motion||'';
  if(s.user!==UI.user)return false;const d=UI.devs.desk;Object.assign(d,s.desk);d.sheet=null;if(d.sec==='onboard'&&!d.ob)d.sec='projects';if(d.pid&&!pOf(d.pid))d.pid=null;
  SCROLL=s.sc||{};OBU=Math.max(0,...(d.ob?d.ob.ents.map(e=>e.u||0):[]));UI.toast=null;return true}catch(e){return false}};

/* ---------- start ---------- */
async function liveBoot(){const first=(()=>{try{return !sessionStorage.getItem('rvt_desk_open')}catch(e){return false}})();UI.view='desk';UI.devs.desk.signed=true;
 try{applySnapshot(await rpc('snapshot'))}catch(e){if(e.message==='session')return;document.getElementById('app').innerHTML=`<div class="livefail"><h1>The desk could not load</h1><p>${esc(e.message)}</p><button type="button" class="btn gold" onclick="location.reload()">Try again</button></div>`;return}
 const intro0=intro;if(!first)intro=function(){};boot();intro=intro0;if(first&&UI.restored)intro();
 try{sessionStorage.setItem('rvt_desk_open','1')}catch(e){}
 document.addEventListener('visibilitychange',()=>{if(!document.hidden&&!LIVE.busy&&!LIVE.saving&&!LIVE.queue.length){reload(true);liveOpen()}});liveStart()}

/* ---------- live: the server says "something changed", and the desk reads again ----------
   The message itself carries nothing; the data comes through the signed-in session as always.
   Where the live line cannot be had, the desk asks by itself every fifteen seconds while its tab is in front. */
const LV={ws:null,on:false,last:0,wait:2000,t:null,r:null,poll:null};
function liveSoon(){clearTimeout(LV.t);LV.t=setTimeout(()=>{if(document.hidden)return;if(LIVE.busy||LIVE.saving||LIVE.queue.length)return liveSoon();reload(true)},350)}
function liveOpen(){const L=DB.set&&DB.set.live;if(!L||LV.ws||typeof WebSocket==='undefined')return;let ws;
 try{ws=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/websocket?version='+encodeURIComponent(L.v))}catch(e){return}
 LV.ws=ws;
 /* the first time the line listens from now on (a number past the newest message is brought back to the newest by the
    server, which says where that is); after a break it asks for what it missed. Either way one quiet reading follows. */
 ws.onopen=()=>{LV.on=true;LV.wait=2000;try{ws.send(JSON.stringify({event_name:'subscribe',data:{channels:[L.ch],last:LV.last||2147483647,check_outdated:false}}))}catch(e){}liveSoon()};
 ws.onmessage=e=>{let m=null;try{m=JSON.parse(e.data)}catch(x){}if(!Array.isArray(m))return;let hit=false;m.forEach(n=>{if(!n)return;if(n.internal){if(n.type==='bus/last_id_reset'&&typeof n.payload==='number')LV.last=n.payload;return}
  if(n.id>LV.last)LV.last=n.id;if(n.message&&n.message.type==='rvt.changed')hit=true});if(hit)liveSoon()};
 ws.onclose=()=>{if(LV.ws!==ws)return;LV.ws=null;LV.on=false;clearTimeout(LV.r);LV.r=setTimeout(liveOpen,LV.wait);LV.wait=Math.min(LV.wait*2,60000)};
 ws.onerror=()=>{try{ws.close()}catch(e){}}}
function liveStart(){liveOpen();if(LV.poll)return;LV.poll=setInterval(()=>{if(document.hidden)return;if(!LV.ws)liveOpen();if(!LV.on&&!LIVE.busy&&!LIVE.saving&&!LIVE.queue.length)reload(true)},15000)}
