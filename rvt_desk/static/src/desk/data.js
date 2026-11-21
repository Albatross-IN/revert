/* Master lists and records of the desk. They start empty and are filled from the server (live.js).
   The names and shapes are those of the approved preview, so the screen code is the same code. */
const TRADES=[],TX={},ETYPES=[],ETX={},PRESETS=[],EXTRAS=[],DEFAULT_TRADES=[],DTYPES=[];
function seed(){return {set:{approval:true,clientConfirm:true,lim:{open:2,q:1,bill:3,stuck:7},sending:false,number:''},staff:[],agencies:[],projects:[],drawings:[],visits:[],points:[],bills:[],wa:[],
 features:{},mytasks:[],today:[],company:'',prefix:'/odoo',admin:false,seq:{lid:0,did:0,ptid:0,bid:0,vid:0,pid:0,q:0}}}
