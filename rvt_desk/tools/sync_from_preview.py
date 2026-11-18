#!/usr/bin/env python3
"""Copy the screen code of the approved preview into this module.

    python3 rvt_desk/tools/sync_from_preview.py /path/to/revert_fe/design/src

The desk runs the preview's own files, so the layout cannot drift from what was
approved. They are copied as they are, except for the short list of changes
below; each one must match exactly once, so a change in the preview that touches
the same place stops the copy instead of passing silently.

Not copied: data.js (the preview's invented records). This module has its own
data.js (empty lists, filled from the server) and live.js / live.css (the
adapter between these screens and the server).
"""
import pathlib
import sys

FILES = ["logo.js", "core.js", "draw.js", "blocks.js", "sheets.js", "desk.js", "apps.js", "shell.js", "styles.css"]

PATCHES = {
    "core.js": [
        # today's date, the clock and the visibility rule come from the server
        ("const BASE=Date.UTC(2026,10,18),MON=", "let BASE=Date.UTC(2026,10,18);const MON="),
        ("const NOW='10:42 am';", "let NOW='10:42 am';"),
        ("const canSee=(u,p)=>", "let canSee=(u,p)=>"),
        # an owner may do what the principal does (the server agrees)
        ("const isPrincipal=()=>has(me(),'principal');", "const isPrincipal=()=>has(me(),'principal')||has(me(),'owner');"),
    ],
    "shell.js": [
        # the preview's demo hint has no place in the product
        ("return toast('Only the principal approves a release. Switch “Signed in as” to Pranav to try it.','wait')",
         "return toast('Only the principal approves a release.','wait')"),
        # a drawing added by hand goes to the project's first designer, not to an invented person
        ("ds:ob.designers[0]||'s4',due:14", "ds:ob.designers[0]||(DB.staff.find(u=>has(u,'designer'))||{id:''}).id,due:14"),
    ],
    "sheets.js": [
        ("ds=ob.designers.length?ob.designers:['s4'];", "ds=ob.designers.length?ob.designers:[(DB.staff.find(u=>has(u,'designer'))||{id:''}).id];"),
        # rooms of a preset are numbered from the master data (bedrooms beside a master bedroom start at 2)
        ("ps.e.forEach(([ty,c])=>{for(let i=1;i<=c;i++)ob.ents.push({u:++OBU,n:c>1?(ty==='Bedroom'?'Bedroom '+(i+1):ty.replace(' / bathroom','')+' '+i):ty,ty})});",
         "ps.e.forEach(([ty,c,f])=>{for(let i=1;i<=c;i++)ob.ents.push({u:++OBU,n:c>1?ty+' '+(i+(f||1)-1):ty,ty})});"),
    ],
    "desk.js": [
        # Today lists the hand-made tasks assigned to me (plan P3), not the first five of my projects
        ("const tasks=ps.flatMap(p=>p.tasks.map(t=>[p,t])).slice(0,5).map(([p,t])=>",
         "const tasks=(DB.mytasks||[]).map(t=>[{name:t.p},{n:t.n,stage:t.stage,subs:t.subs,id:t.id}]).map(([p,t])=>"),
        ("""`<div class="rw"><div class="m"><div class="t1">${esc(t.n)}</div><div class="t2">${esc(p.name)} · ${esc(t.stage)}${t.subs?' · '+t.subs+' sub-tasks':''}</div></div></div>`).join('');""",
         """`<div class="rw lk" data-a="opentask" data-v="${t.id}"><div class="m"><div class="t1">${esc(t.n)}</div><div class="t2">${esc(p.name)} · ${esc(t.stage)}${t.subs?' · '+t.subs+' sub-tasks':''}</div></div></div>`).join('');"""),
        # an earlier task is addressed by its id, can be opened in its own form, and its MOM entries are counted
        ("Bt('Use as a room','taskent',p.id+'|'+x.n,'sm')}</div></div>`",
         "Bt('Use as a room','taskent',p.id+'|'+x.id,'sm')}${Bt('Open','opentask',x.id,'sm ghost','chev')}</div></div>`"),
        ("'<span class=\"mu f12\">date task · no longer needed for MOM</span>':", "Bt('Open','opentask',x.id,'sm ghost','chev'):"),
        ("${x.mom} MOM entries moved to the new MOM</div>", "${x.mom} MOM ${x.mom===1?'entry':'entries'}${DB.features.mom?' moved to the new MOM':''}</div>"),
        ("card('Earlier tasks','<span class=\"mu f12\">made by hand · they keep working as before</span>',",
         "card('Earlier tasks','<span class=\"mu f12\">made by hand · they keep working as before</span>'+Bt('Task board','taskboard',p.id,'sm ghost','grid'),"),
    ],
}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(__file__).resolve().parent.parent / "static" / "src" / "desk"
    dst.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        text = (src / name).read_text()
        for old, new in PATCHES.get(name, []):
            if text.count(old) != 1:
                sys.exit("%s: expected exactly one match for\n  %s\nfound %s" % (name, old[:90], text.count(old)))
            text = text.replace(old, new)
        (dst / name).write_text(text)
        print("copied", name, "(%s changes)" % len(PATCHES.get(name, [])))


if __name__ == "__main__":
    main()
