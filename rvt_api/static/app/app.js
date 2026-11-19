(function(){"use strict";
/* ---- logo.js ---- */
/* The real ré-vert wordmark (vector, from the studio's logo). */
const LOGO='<svg class="logo" viewBox="1.6 1.2 150.2 37.2" role="img" aria-label="ré-vert"><path fill-rule="evenodd" d="M148.32 37.71C147.97 37.68 147.66 37.61 147.43 37.48C147.37 37.45 146.91 37.04 146.43 36.56C145.94 36.09 145.39 35.55 145.2 35.36C145 35.18 144.59 34.77 144.28 34.45C143.96 34.12 143.56 33.75 143.36 33.6C143.16 33.45 142.97 33.3 142.95 33.25C142.92 33.21 142.43 32.74 141.88 32.22C141.31 31.7 140.57 30.96 140.21 30.6C139.86 30.23 139.43 29.81 139.26 29.68C139.09 29.54 138.76 29.25 138.53 29.03C138.3 28.8 137.91 28.43 137.67 28.2C136.49 27.09 135.81 26.43 135.69 26.29C135.62 26.21 135.43 26.03 135.26 25.89C135.1 25.77 134.78 25.48 134.57 25.26C134.36 25.04 133.78 24.49 133.3 24.04C132.81 23.59 132.16 22.96 131.85 22.65C131.12 21.95 129.95 20.81 129.32 20.23C129.05 19.99 128.6 19.56 128.32 19.29C128.05 19.01 127.76 18.76 127.68 18.73C127.32 18.57 127 18.79 126.94 19.23C126.93 19.32 126.92 22.18 126.91 25.57L126.91 31.75L126.82 31.91C126.77 32 126.67 32.11 126.59 32.16L126.44 32.26L87.45 32.29C66 32.3 38.37 32.32 26.05 32.34C5.7 32.36 3.63 32.35 3.48 32.29C3.38 32.25 3.29 32.18 3.23 32.09C3.15 31.96 3.14 31.9 3.14 31.41C3.14 30.81 3.2 30.64 3.43 30.5C3.56 30.43 3.64 30.42 4.41 30.42C12.61 30.42 27.79 30.43 36.84 30.43C43.18 30.44 62.06 30.45 78.79 30.46C95.51 30.47 110.01 30.48 111 30.48C112.17 30.48 112.84 30.47 112.93 30.45C113.21 30.36 113.44 30.13 113.52 29.86C113.54 29.78 113.55 27.64 113.55 24.62C113.56 21.64 113.57 19.37 113.6 19.16C113.66 18.5 113.81 18.24 114.46 17.66C114.66 17.47 114.96 17.19 115.12 17.03C115.28 16.87 115.68 16.49 116 16.2C116.32 15.9 117.05 15.18 117.62 14.61C118.76 13.47 119.48 12.79 119.78 12.57C119.88 12.49 120.18 12.22 120.45 11.96C120.71 11.71 121.33 11.11 121.82 10.62C122.32 10.14 122.99 9.5 123.31 9.18C123.64 8.86 124.11 8.41 124.37 8.18C124.62 7.94 125.08 7.51 125.38 7.21C126.18 6.44 127.17 5.49 127.61 5.09C128.38 4.37 129.27 3.51 129.67 3.1C130.04 2.71 130.46 2.35 130.84 2.09C131.06 1.95 131.23 1.92 131.41 2.01C131.63 2.12 131.71 2.26 131.71 2.52C131.71 2.89 131.59 3.07 130.78 3.83C130.39 4.2 129.94 4.65 129.77 4.83C129.59 5.01 129.3 5.27 129.13 5.42C128.96 5.57 128.72 5.79 128.59 5.93C128.23 6.32 127.36 7.17 127.14 7.34C126.92 7.52 125.91 8.5 125.26 9.18C124.73 9.73 124.34 10.1 123.95 10.41C123.79 10.54 123.55 10.78 123.41 10.94C123.28 11.1 123.04 11.35 122.88 11.48C122.54 11.77 121.8 12.57 121.7 12.75C121.64 12.86 121.63 13.38 121.62 20.14L121.61 27.41L121.7 27.59C121.83 27.85 121.97 27.91 122.49 27.93C123.02 27.95 123.46 27.89 123.6 27.79C123.66 27.75 123.74 27.66 123.78 27.58C123.86 27.45 123.86 27.36 123.88 20.34L123.9 13.22L123.99 13.02C124.14 12.73 124.27 12.68 124.79 12.66C125.16 12.64 125.22 12.65 125.41 12.74C125.72 12.89 126.39 13.48 127.63 14.72C128.24 15.33 128.87 15.93 129.02 16.07C129.17 16.2 129.77 16.76 130.34 17.32C130.93 17.89 131.53 18.46 131.68 18.6C131.83 18.73 132.61 19.48 133.42 20.26C134.22 21.04 134.97 21.75 135.08 21.84C135.39 22.12 137.15 23.8 137.52 24.18C137.7 24.36 137.99 24.64 138.16 24.79C138.32 24.93 138.56 25.18 138.68 25.33C138.8 25.48 139.04 25.71 139.21 25.86C139.39 26 139.68 26.26 139.86 26.44C140.05 26.62 140.28 26.82 140.38 26.9C140.48 26.97 140.64 27.14 140.75 27.26C140.86 27.39 141.11 27.64 141.3 27.82C141.51 27.99 141.71 28.21 141.77 28.29C141.87 28.44 142.68 29.2 143.12 29.56C143.25 29.67 143.74 30.14 144.21 30.62C144.68 31.09 145.36 31.75 145.71 32.08C146.08 32.41 146.58 32.89 146.83 33.14C147.08 33.38 147.59 33.87 147.96 34.21C148.33 34.56 148.81 35 149.01 35.19C149.21 35.39 149.47 35.61 149.57 35.7C149.68 35.78 149.92 36.03 150.11 36.26C150.3 36.49 150.54 36.75 150.64 36.85C150.88 37.08 150.95 37.24 150.88 37.39C150.81 37.52 150.66 37.63 150.48 37.67C150.26 37.72 148.74 37.75 148.32 37.71Z"/><path fill-rule="evenodd" d="M138.2 20.31C137.31 20.27 137.21 20.21 136.21 19.2C135.48 18.46 134.8 17.82 133.98 17.11C133.38 16.58 133.04 16.26 132.46 15.69C132.18 15.41 131.76 15.02 131.54 14.84C131.31 14.64 131.02 14.35 130.87 14.2C130.73 14.04 130.48 13.78 130.3 13.61C129.8 13.14 129.72 12.87 130.02 12.7C130.14 12.64 130.33 12.63 133.01 12.63C135.36 12.63 135.89 12.64 136.02 12.69C136.12 12.72 136.32 12.89 136.62 13.18C136.87 13.42 137.13 13.66 137.21 13.72C137.28 13.78 137.73 14.21 138.19 14.67C138.66 15.13 139.15 15.6 139.29 15.71C139.72 16.07 140.49 16.76 140.82 17.09C140.98 17.25 141.25 17.5 141.41 17.61C141.79 17.9 143.33 19.38 143.49 19.6C143.65 19.83 143.66 20.02 143.52 20.16C143.32 20.35 143.22 20.36 140.89 20.35C139.69 20.34 138.48 20.33 138.2 20.31Z"/><path fill-rule="evenodd" d="M50.68 23.21C50.51 23.07 50.42 22.84 50.38 22.45C50.32 21.93 50.33 16.62 50.39 16.39C50.5 15.95 51.02 15.75 51.36 16.04C51.43 16.09 51.51 16.24 51.58 16.41C51.69 16.69 51.82 16.83 51.97 16.83C52.06 16.83 52.13 16.79 52.85 16.29C53.32 15.95 53.52 15.88 53.94 15.88C54.32 15.88 54.51 15.97 54.64 16.21C54.79 16.51 54.7 16.97 54.45 17.14C54.39 17.19 54.18 17.27 53.98 17.32C53.59 17.42 52.88 17.71 52.66 17.86C52.59 17.91 52.44 18.09 52.32 18.26C52.2 18.43 52.03 18.67 51.93 18.78C51.63 19.14 51.63 19.19 51.59 20.96C51.58 21.82 51.55 22.59 51.54 22.68C51.5 22.89 51.37 23.12 51.22 23.21C51.06 23.31 50.82 23.31 50.68 23.21Z"/><path fill-rule="evenodd" d="M60.02 23.5C59.89 23.47 59.62 23.38 59.43 23.3C59.24 23.21 58.99 23.11 58.88 23.07C58.63 22.99 58.4 22.85 58.12 22.59C57.8 22.3 57.64 22.03 57.48 21.55C57.4 21.31 57.27 21 57.2 20.86C57.03 20.51 56.95 20.18 56.95 19.77C56.95 19.3 57.01 18.98 57.17 18.59C57.25 18.41 57.38 18.07 57.45 17.85C57.66 17.18 57.84 16.94 58.49 16.46C59.22 15.91 59.57 15.8 60.61 15.83C61.54 15.86 61.56 15.87 62.34 16.47C62.64 16.71 62.67 16.75 62.84 17.1C62.94 17.3 63.09 17.57 63.17 17.71C63.36 18 63.48 18.37 63.5 18.77C63.53 19.14 63.48 19.31 63.28 19.47C63.05 19.64 62.82 19.66 61.29 19.63C59.67 19.61 59.07 19.63 58.91 19.75C58.71 19.91 58.65 20.06 58.66 20.43C58.66 20.83 58.71 21.03 58.88 21.28C59.01 21.47 59.08 21.53 59.62 21.89C60.44 22.43 60.54 22.44 61.27 21.91C61.49 21.76 61.71 21.55 61.87 21.36C62.24 20.9 62.6 20.71 62.94 20.77C63.25 20.82 63.43 21.08 63.39 21.45C63.37 21.69 63.12 22.07 62.71 22.5C62.45 22.77 62.36 22.84 61.82 23.12C61.01 23.55 60.62 23.63 60.02 23.5ZM61.48 18.48C61.9 18.18 61.59 17.44 60.96 17.21C60.58 17.08 60 17.1 59.68 17.26C59.43 17.38 59 17.75 58.93 17.91C58.84 18.09 58.87 18.23 59.02 18.38C59.22 18.57 59.41 18.59 60.43 18.58C61.32 18.57 61.35 18.57 61.48 18.48ZM60.29 15.36C59.98 15.27 59.83 14.9 59.98 14.54C60.06 14.35 60.65 13.75 60.84 13.66C61.02 13.59 61.24 13.57 61.45 13.63C61.95 13.77 61.87 14.36 61.26 14.92C60.86 15.29 60.55 15.43 60.29 15.36Z"/><path fill-rule="evenodd" d="M67.13 18.2C64.86 18.18 64.95 18.2 64.8 17.86C64.67 17.56 64.75 17.26 65.02 17.12C65.12 17.06 65.34 17.05 66.82 17.02C67.75 17 69.1 17 69.83 17.02C71.05 17.05 71.18 17.06 71.34 17.14C71.57 17.23 71.66 17.38 71.66 17.59C71.66 17.91 71.49 18.1 71.13 18.16C70.83 18.21 69.38 18.23 67.13 18.2Z"/><path fill-rule="evenodd" d="M75.64 23.47C75.47 23.39 75.45 23.35 75.14 22.74C74.91 22.29 74.8 22 74.75 21.8C74.62 21.2 74.57 21.04 74.37 20.59C74.17 20.17 74.04 19.79 73.98 19.46C73.96 19.38 73.87 19.11 73.78 18.87C73.69 18.62 73.59 18.3 73.55 18.16C73.51 18.03 73.41 17.77 73.31 17.61C73.09 17.23 73 16.91 73 16.52C73 16.23 73.01 16.21 73.11 16.09C73.32 15.88 73.62 15.85 73.91 16.02C74.04 16.1 74.49 16.75 74.62 17.05C74.67 17.14 74.73 17.43 74.77 17.68C74.84 18.09 74.88 18.2 75.07 18.56C75.27 18.96 75.35 19.22 75.42 19.77C75.43 19.87 75.5 20.07 75.57 20.22C75.87 20.84 76.22 20.95 76.45 20.51C76.49 20.41 76.62 20.01 76.73 19.61C76.98 18.72 77.08 18.43 77.34 17.83C77.45 17.57 77.61 17.16 77.68 16.91C77.89 16.15 78.13 15.92 78.66 15.95C78.91 15.96 78.94 15.97 79.04 16.09C79.17 16.23 79.19 16.43 79.1 16.74C79.07 16.85 79.01 17.07 78.98 17.25C78.89 17.7 78.82 17.88 78.61 18.22C78.41 18.54 78.39 18.62 78.29 19.26C78.26 19.52 78.21 19.66 78.05 19.95C77.94 20.17 77.83 20.45 77.77 20.7C77.71 20.92 77.57 21.31 77.46 21.58C77.34 21.84 77.2 22.21 77.14 22.41C77.01 22.84 76.93 23.01 76.74 23.21C76.55 23.42 76.34 23.53 76.05 23.55C75.86 23.56 75.78 23.55 75.64 23.47Z"/><path fill-rule="evenodd" d="M83.43 23.49C83.33 23.45 83.16 23.36 83.05 23.3C82.95 23.23 82.7 23.11 82.5 23.03C82.18 22.91 82.08 22.85 81.76 22.56C81.37 22.21 81.28 22.09 81.17 21.7C81.13 21.57 81.04 21.3 80.95 21.11C80.77 20.69 80.68 20.18 80.68 19.63C80.68 19.01 80.74 18.76 81.02 18.05C81.33 17.26 81.4 17.14 81.69 16.86C81.99 16.59 82.76 16.06 82.99 15.97C83.24 15.88 84.39 15.8 84.79 15.86C85.27 15.93 85.62 16.13 86.22 16.69C86.41 16.87 86.5 17 86.62 17.24C86.87 17.77 86.97 18.07 87.04 18.43C87.15 19.06 87.05 19.39 86.7 19.54C86.46 19.65 85.88 19.67 84.88 19.61C84.29 19.58 83.96 19.57 83.55 19.61C82.77 19.67 82.61 19.71 82.43 19.88C82.3 20.01 82.29 20.05 82.29 20.23C82.29 20.48 82.52 21.16 82.7 21.43C82.83 21.64 83.3 21.99 83.73 22.18C84.01 22.32 84.33 22.32 84.6 22.2C84.81 22.11 85.32 21.61 85.6 21.24C85.81 20.96 86.09 20.81 86.43 20.81C86.69 20.8 86.83 20.89 86.95 21.1C87.05 21.3 87.02 21.55 86.82 21.93C86.69 22.2 86.61 22.32 86.32 22.58C86.02 22.86 85.91 22.94 85.49 23.14C84.74 23.5 84.64 23.53 84.1 23.54C83.71 23.55 83.6 23.55 83.43 23.49ZM85.02 18.49C85.16 18.43 85.29 18.25 85.32 18.09C85.37 17.82 84.98 17.34 84.58 17.2C84.44 17.15 84.25 17.13 83.96 17.13C83.46 17.13 83.24 17.21 82.97 17.5C82.62 17.87 82.55 18.18 82.74 18.41C82.89 18.57 82.98 18.57 84.04 18.56C84.69 18.55 84.95 18.54 85.02 18.49Z"/><path fill-rule="evenodd" d="M90.02 23.26C89.88 23.2 89.7 22.98 89.64 22.78C89.58 22.58 89.57 22.28 89.57 19.53C89.57 17.24 89.59 16.46 89.62 16.34C89.72 16.02 90.05 15.85 90.38 15.94C90.61 16 90.75 16.16 90.81 16.44C90.87 16.74 90.98 16.98 91.07 17.01C91.18 17.04 91.3 16.98 91.5 16.82C91.6 16.74 91.79 16.61 91.93 16.54C92.08 16.45 92.33 16.3 92.5 16.18C92.84 15.95 92.96 15.91 93.43 15.88C93.71 15.85 93.79 15.86 93.95 15.93C94.2 16.04 94.3 16.26 94.28 16.62C94.25 17.05 94.05 17.21 93.43 17.32C93.03 17.39 92.5 17.59 92.2 17.78C91.95 17.94 91.56 18.43 91.26 18.98C90.83 19.75 90.87 19.55 90.85 21.2L90.82 22.64L90.71 22.86C90.64 23.01 90.56 23.12 90.47 23.17C90.33 23.25 90.12 23.3 90.02 23.26Z"/><path fill-rule="evenodd" d="M100.46 23.52C100.36 23.5 100.08 23.38 99.84 23.26C99.43 23.06 99.35 23 99.01 22.66C98.8 22.46 98.61 22.23 98.57 22.16C98.44 21.91 98.42 21.63 98.41 19.63C98.41 17.69 98.4 17.63 98.32 17.45C98.2 17.19 98.09 17.14 97.47 17.11C97.19 17.09 96.89 17.06 96.8 17.04C96.47 16.95 96.28 16.67 96.36 16.4C96.46 16.04 96.64 15.95 97.4 15.88C98.35 15.77 98.36 15.77 98.39 14.7C98.41 13.92 98.44 13.82 98.62 13.65C98.75 13.54 99.18 13.52 99.37 13.62C99.62 13.76 99.65 13.87 99.69 14.68C99.73 15.51 99.76 15.61 100 15.74C100.15 15.82 100.23 15.84 100.89 15.86C101.71 15.89 101.91 15.94 102.07 16.18C102.18 16.36 102.16 16.71 102.02 16.86C101.82 17.07 101.75 17.09 100.9 17.11C100.03 17.13 100 17.14 99.81 17.42C99.69 17.6 99.67 17.89 99.69 19.71C99.7 21.23 99.7 21.32 99.78 21.49C99.88 21.69 100.3 22.11 100.54 22.23C100.77 22.34 101.15 22.33 101.5 22.2C102.21 21.94 102.17 21.95 102.32 22.01C102.67 22.16 102.66 22.79 102.29 23.16C102.12 23.33 101.94 23.43 101.66 23.48C101.33 23.54 100.66 23.56 100.46 23.52Z"/></svg>';

/* ---- data.js ---- */
/* Master lists and records of the desk. They start empty and are filled from the server (live.js).
   The names and shapes are those of the approved preview, so the screen code is the same code. */
const TRADES=[],TX={},ETYPES=[],ETX={},PRESETS=[],EXTRAS=[],DEFAULT_TRADES=[],DTYPES=[];
function seed(){return {set:{approval:true,clientConfirm:true,lim:{open:2,q:1,bill:3,stuck:7},sending:false,number:''},staff:[],agencies:[],projects:[],drawings:[],visits:[],points:[],bills:[],wa:[],
 features:{},mytasks:[],today:[],company:'',prefix:'/odoo',admin:false,seq:{lid:0,did:0,ptid:0,bid:0,vid:0,pid:0,q:0}}}

/* ---- core.js ---- */
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

/* ---- draw.js ---- */
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

/* ---- blocks.js ---- */
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
const pbar=(a,b,c)=>`<div class="bar ${c||''}"><i style="width:${b?Math.round(a/b*100):0}%"></i></div>`;
const money=(n,cls)=>isOwner()?`<b class="num ${cls||''}">${inr(n)}</b>`:`<span class="lockd" title="Amounts are visible to the owner only">${ic('lock')}owner only</span>`;
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
  v==='plan'?`<p class="t2 hint">Each room shows its trades as dots. Tap a room to change them.</p>${planView(p,dev)}${planLegend()}`:`<p class="t2 hint">Rooms down, trades across. Tap a cell to change it.</p>${gridBlock(p,dev)}`)}
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
 if(d.st==='awaiting')act=isPrincipal()?Bt('View PDF','view',d.id,'','eye')+Bt('Approve','approve',d.id,'gold','check'):Bt('View PDF','view',d.id,'','eye')+`<span class="note wait in">${ic('clock')}Waiting for ${esc(stf(p.principal).n)} to approve</span>`;
 if(d.st==='approved')act=Bt('View PDF','view',d.id,'','eye')+Bt('Release','release',d.id,'gold','send');
 if(d.st==='released')act=Bt('View PDF','view',d.id,'','eye')+Bt('New revision','newrev',d.id,'','plus');
 const rc=d.st==='released'?r.rc.map(x=>{const cl=x.to==='client',nm=cl?p.client.n:agN(x.to);return `<div class="rw"><div class="m"><div class="t1">${av(nm,'sm')}<span>${esc(nm)}</span>${cl?pill('client','gold'):''}</div><div class="t2">sent ${fd(x.sent)} on WhatsApp and in the app</div></div><div class="r">${x.opened!=null?`<span class="c-ok f12 b">${ic('check')}opened ${fd(x.opened)}</span>`:`<span class="c-bad f12 b">not opened</span>${Bt('Remind','remind',(cl?'client':x.to)+'|'+p.id+'|Please open '+sheetNo(d)+' '+d.title+'.','sm wa','wa')}`}</div></div>`}).join(''):'';
 const cd=r.client?(r.client.dec==='pending'?`<div class="note wait">${ic('clock')}Client approval pending since ${fd(r.relOn)}.</div>`:r.client.dec==='approved'?`<div class="note ok">${ic('check')}<span>Approved by <b>${esc(r.client.by)}</b> on ${fdw(r.client.on)}, ${r.client.at}. The tap is the record; no signature.</span></div>`:''):'';
 const revs=d.revs.slice().reverse().map(x=>`<div class="tl ${x.st}"><i class="rev">${x.n}</i><div><div class="t1">Revision ${x.n} ${pill({draft:'Draft',awaiting:'Awaiting approval',approved:'Approved',released:'Released',superseded:'Superseded'}[x.st],{draft:'plain',awaiting:'wait',approved:'gold',released:'ok',superseded:'plain'}[x.st])}</div>
   <div class="t2">${x.note?esc(x.note)+'<br>':''}${x.back?'<span class="c-bad">Sent back: '+esc(x.back)+'</span><br>':''}${x.sentBy?'sent by '+esc(stf(x.sentBy).n)+' '+fd(x.sentOn):''}${x.apprBy&&x.apprOn!=null?' · approved by '+esc(stf(x.apprBy).n)+' '+fd(x.apprOn):''}${x.relOn!=null?' · released '+fd(x.relOn):''}</div>
   ${x.client&&x.client.dec==='change'?`<div class="note bad sm">${ic('edit')}<span>Change asked by ${esc(x.client.by)} on ${fd(x.client.on)}, ${x.client.at}: “${esc(x.client.note)}”</span></div>`:''}</div></div>`).join('');
 const qs=d.q.map(q=>`<div class="q"><div class="qb in"><div class="lbl">${esc(q.byName)} · ${q.by==='client'?'client':esc(agN(q.by))} · ${fd(q.on)}${q.via==='office'?' · logged from a call':''}</div>${esc(q.text)}${q.photo?phOf('question',q):''}</div>
   ${q.ans?`<div class="qb out"><div class="lbl">${esc(stf(q.ansBy).n)} · ${fd(q.ansOn)}</div>${esc(q.ans)}</div>`:`<div class="qa">${fin(dev,'ans_'+q.id,'Type the answer…')}${Bt('Answer','answer',d.id+'|'+q.id,'sm gold')}</div>`}</div>`).join('');
 return `<div class="stack dd"><div class="ddh"><button type="button" class="shtb" data-a="view" data-v="${d.id}" aria-label="View the sheet">${sht(d,'md')}</button><div class="m"><div class="lbl">${sheetNo(d)} · ${d.t?esc(TX[d.t].n):'General set'}</div><h2 class="serif">${esc(d.title)}</h2><div class="t2">${esc(p.name)} · drawn by ${esc(stf(d.ds).n)} · ${d.st==='released'?'released '+fd(r.relOn):'due '+fdw(d.due)}</div>
   <div class="chips ro">${pill(s[0],s[1])}${d.forClient?pill('for client','gold'):''}${d.needsApproval?pill('client approves','plain'):''}</div></div></div>
  <div class="actbar">${act}</div>
  ${w.length?`<div class="note wait">${ic('pause')}<span><b>${plural(w.length,'work line')} waiting</b> for this drawing: ${esc(w.map(l=>entN(p,l.e)+' ('+TX[l.t].s+')').join(', '))}</span></div>`:''}${cd}
  ${d.st==='released'?card('Sent to',`<span class="mu f12">${r.rc.filter(x=>x.opened!=null).length} of ${r.rc.length} opened</span>`,`<div class="rows">${rc}</div>`):''}
  ${card('Questions',Bt('Log a question from a call','sheet','logq|'+d.id,'sm ghost','plus'),qs||empty('No question on this drawing.','info'))}
  ${card('Revisions',`<span class="mu f12">receivers only ever see the current one</span>`,`<div class="tls">${revs}</div>`)}</div>`}

/* ---------- points and MOM ---------- */
function ptRow(x,dev,o){o=o||{};const p=pOf(x.pid),nm=partyName(p,x),v=x.vid?visOf(x.vid):null;
 return `<div class="rw pt ${x.st}">${kn(x.n)}<div class="m"><div class="t1"><span class="tx">${esc(x.text)}</span>${x.photo?`<span class="phb" role="button" tabindex="0" data-a="photo" data-v="${x.id}" aria-label="Open the photo">${ic('cam','mu')}</span>`:''}</div>
  <div class="t2">${x.fresh&&x.st==='open'&&x.vid&&x.kind!=='staff'?pill('new','gold')+' ':''}<b class="pty k-${x.kind}">${esc(nm)}</b>${x.e?' · '+esc(entN(p,x.e)):''}${o.proj?' · '+esc(p.name):''}${v?' · visit '+v.no:x.legacy?'':' · raised from the office'}${x.legacy?' · moved from the earlier MOM':''}</div>
  ${x.st==='closed'?`<div class="t2 c-ok">${ic('check')}closed ${fd(x.closedOn)}${x.note?' · '+esc(x.note):''}</div>`:x.kind==='client'&&!x.confirmed?`<div class="t2 c-wait">${ic('eye')}not shown to the client until the office confirms</div>`:x.pending?`<div class="t2 c-wait">${ic('off')}saved on the phone · waiting to go</div>`:''}</div>
  <div class="r">${x.st==='open'?`<span class="due ${dueCls(x.due)}">${dueW(x.due)}</span>${x.sent&&x.kind!=='staff'?`<span class="tick" title="sent">${ic('check')}${ic('check')}</span>`:''}${o.ro?'':x.kind==='client'&&!x.confirmed?Bt('Confirm','confirmpt',x.id,'sm gold'):Bt('Close','closept',x.id,'sm')}`:''}</div></div>`}
function forOptions(p){const o=[...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))].map(a=>[a,agN(a).split(' ')[0],'agency']);o.push(['client','Client','client']);
 [...new Set([p.principal,...p.designers,...p.coords])].forEach(s=>o.push([s,stf(s).n,'staff']));return o}
function momCapture(v,dev){const p=pOf(v.pid),f=dev.f,opts=forOptions(p);if(f.m_vendor)opts.push(['vendor',f.m_vendor,'vendor']);if(!f.m_for)f.m_for=opts[0][0];if(f.m_due==null)f.m_due=2;if(!f.m_area)f.m_area=(p.ents[0]||{id:''}).id;
 const here=DB.points.filter(x=>x.vid===v.id),earlier=DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&x.vid!==v.id&&!(x.kind==='staff')),grp={};
 earlier.forEach(x=>{const k=partyName(p,x);(grp[k]=grp[k]||[]).push(x)});
 const sendKeys=[...new Set(here.filter(x=>x.st==='open'&&x.kind==='agency').map(x=>x.party))],freshOf=k=>here.filter(x=>x.party===k&&x.st==='open'&&x.fresh).length,allOf=k=>here.filter(x=>x.party===k&&x.st==='open').length;
 const pend=here.filter(x=>x.pending).length+UI.outbox.length;
 return `<div class="momc"><div class="momh"><div><div class="lbl">Visit ${v.no} · ${fdw(v.date)}</div><h2 class="serif">${esc(p.name)}</h2></div>${UI.offline?`<span class="pill wait">${ic('off')}offline · ${pend} waiting to go</span>`:`<span class="pill ok">${ic('check')}saved</span>`}</div>
  ${earlier.length?`<details class="earlier" ${f.m_early===false?'':'open'}><summary><span class="lbl">Open from earlier</span><span class="f12">${Object.keys(grp).map(k=>`${esc(k.replace(/^(Mr\.|Mrs\.|Dr\.)\s*/,'').split(' ')[0])} <b>${grp[k].length}</b>`).join(' · ')}</span></summary><div class="rows">${earlier.map(x=>ptRow(x,dev)).join('')}</div></details>`:''}
  <div class="lbl mt">This visit · ${plural(here.length,'point')}</div><div class="rows">${here.length?here.map(x=>ptRow(x,dev)).join(''):`<div class="empty sm">${ic('mom')}<span>Write the first point below. Under ten seconds each.</span></div>`}</div>
  <div class="dock"><div class="composer"><div class="cr"><span class="lbl">For</span><div class="chips scroll">${opts.map(o=>`<button type="button" class="chip k-${o[2]}" data-a="set" data-v="m_for=${o[0]}" aria-pressed="${f.m_for===o[0]}">${esc(o[1])}</button>`).join('')}<button type="button" class="chip" data-a="sheet" data-v="vendor|${v.id}">${ic('plus')}Vendor</button></div></div>
   <div class="cr"><span class="lbl">Area</span><div class="chips scroll">${p.ents.map(e=>`<button type="button" class="chip" data-a="set" data-v="m_area=${e.id}" aria-pressed="${f.m_area===e.id}">${esc(e.n)}</button>`).join('')}</div></div>
   <div class="ctext">${fin(dev,'m_text','Type or speak the point…')}<button type="button" class="ib ${f.m_photo?'on':''}" data-a="tog" data-v="m_photo" aria-label="Photo" aria-pressed="${!!f.m_photo}">${ic('cam')}</button></div>
   <div class="cr"><span class="lbl">Due</span>${chips(dev,'m_due',[[0,'Today'],[1,'Tmrw'],[2,dueW(2)],[5,dueW(5)],[7,fd(7)]],'scroll')}${Bt('Add','addpt',v.id,'gold','plus')}</div></div>
  <div class="sendbar"><span class="lbl">Send on WhatsApp</span><div class="chips">${sendKeys.map(k=>`<button type="button" class="btn sm wa" data-a="sendparty" data-v="${v.id}|${k}">${ic('wa')}<span>${esc(agN(k).split(' ')[0])} (${freshOf(k)||allOf(k)})${freshOf(k)?'':' ✓'}</span></button>`).join('')||'<span class="mu f12">Points for an agency appear here to send.</span>'}
   ${sendKeys.length>1?Bt('All','sendall',v.id,'sm wa','send'):''}${Bt('PDF','pdf','mom|'+v.id+'|all','sm ghost','file')}${v.st==='open'?Bt('Finish visit','finishvisit',v.id,'sm pri','check'):''}</div></div></div></div>`}
function pdfDoc(kind,a,b){ /* mom|vid|party  ·  open|pid */
 let p,title,meta,rows;
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

/* ---- sheets.js ---- */
/* Dialogs (desk) / bottom sheets (phone), and the onboarding wizard. */
const SHEETS={};
const cancelB=()=>Bt('Cancel','close',null,'ghost');

SHEETS.cell=(dev,s)=>{const p=pOf(s.pid),l=p.lines.find(x=>x.id===s.lid),f=dev.f,pl=planOf(p,l.t);
 const dws=DB.drawings.filter(d=>d.pid===p.id&&d.st!=='released').sort((a,b)=>(b.t===l.t)-(a.t===l.t)).map(d=>[d.id,sheetNo(d)+' '+d.title+' · '+DS[d.st][0]]);
 const ci=[...DB.drawings.filter(d=>d.pid===p.id&&d.st==='released'&&cur(d).client&&cur(d).client.dec==='pending').map(d=>[d.id,'Approve '+d.title]),...DB.points.filter(x=>x.pid===p.id&&x.kind==='client'&&x.st==='open').map(x=>[x.id,x.text])];
 const pts=DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&x.e===l.e&&x.t===l.t);
 let cause='';
 if(f.c_st==='wait'){cause=fld('Waiting for what? One tap, so the picture can say who must act',chips(dev,'c_cause',[['drawing','A drawing','dwg'],['client','The client','user'],['trade','Another trade','users'],['material','Material','layers'],['other','Other','more']]));
  if(f.c_cause==='drawing')cause+=fld('Which drawing',fsel(dev,'c_ref',dws,'Choose the drawing'),dws.length?'':'Every drawing of this project is released.');
  if(f.c_cause==='client')cause+=fld('Which client item',fsel(dev,'c_ref',ci,'Choose, or raise a new one below'))+fld('Or raise a new item for the client',fin(dev,'c_new','e.g. Choose the wardrobe laminate'));
  if(f.c_cause==='trade')cause+=fld('Which trade',fsel(dev,'c_ref',p.plan.filter(x=>x.t!==l.t).map(x=>[x.t,TX[x.t].n+(x.ag?' · '+agN(x.ag):' · undecided')]),'Choose the trade'));
  if(f.c_cause==='material'||f.c_cause==='other')cause+=fld('Note',fin(dev,'c_note',f.c_cause==='material'?'Which material, from whom':'What is it waiting for'))}
 return {title:entN(p,l.e)+' · '+TX[l.t].n,sub:p.name,body:`<div class="stseg">${['ns','work','wait','done'].map(k=>`<button type="button" class="c-btn ${k}" data-a="set" data-v="c_st=${k}" aria-pressed="${f.c_st===k}">${LI[k]?ic(LI[k]):'<i class="ring"></i>'}<span>${LS[k][0]}</span></button>`).join('')}</div>${cause}
  ${fld('Agency on this line',fsel(dev,'c_ag',DB.agencies.map(a=>[a.id,a.n+(a.tr.includes(l.t)?'':' (other trade)')]),pl.ag?'As the project: '+agN(pl.ag):'Undecided for the project'),'Change it only when this room has a different agency, e.g. a second carpenter for the kitchen.')}
  ${pts.length?`<div class="lbl mt">Open points on this cell</div><div class="rows">${pts.map(x=>ptRow(x,dev)).join('')}</div>`:''}`,foot:cancelB()+Bt('Save','savecell',s.pid+'|'+s.lid,'gold','check')}};

SHEETS.room=(dev,s)=>{const p=pOf(s.pid),e=p.ents.find(x=>x.id===s.eid),ls=p.lines.filter(l=>l.e===e.id),pts=DB.points.filter(x=>x.pid===p.id&&x.st==='open'&&x.e===e.id),done=ls.filter(l=>l.st==='done').length;
 return {title:e.n,sub:p.name+' · '+done+' of '+ls.length+' trades done',body:`${ticks(done,ls.length,'ok',ls.filter(l=>l.st==='work').length)}<div class="lbl mt">Trades in this room · tap one to change it</div><div class="rows">${ls.map(l=>{const und=!lineAg(p,l);return `<button type="button" class="rw lk" data-a="cell" data-v="${p.id}|${l.id}"><span class="c ${l.st==='ns'&&und?'und':l.st} sm">${l.st==='ns'&&und?ic('alert'):LI[l.st]?ic(LI[l.st]):'<i class="ring"></i>'}</span><div class="m"><div class="t1">${esc(TX[l.t].n)}</div><div class="t2 ${und?'c-bad':''}">${und?'agency undecided':esc(agN(lineAg(p,l)))}${l.st==='wait'?' · <span class="c-wait">waiting for '+esc(waitText(p,l))+'</span>':''}</div></div><div class="r">${pill(LS[l.st][0],LS[l.st][1])}</div></button>`}).join('')}</div>
  ${pts.length?`<div class="lbl mt">Open points here</div><div class="rows">${pts.map(x=>ptRow(x,dev)).join('')}</div>`:''}`,foot:Bt('Raise a point here','raisehere',p.id+'|'+e.id,'','plus')+Bt('Done','close',null,'gold')}};
SHEETS.quick=(dev,s)=>{const ps=myProjects(),f=dev.f,p=pOf(f.q_pid);return {title:'What do you want to do?',sub:'Pick the site, then the act',body:`<div class="chips">${ps.map(x=>`<button type="button" class="chip" data-a="set" data-v="q_pid=${x.id}" aria-pressed="${String(f.q_pid)===String(x.id)}">${esc(x.name)}</button>`).join('')}</div>
  <div class="qgrid"><button type="button" class="qtile" data-a="qgo" data-v="mom"><span class="mi brz">${ic('mom')}</span><div>Start MOM<small>visit ${p?p.visitNo+1:''} · points with photos</small></div></button><button type="button" class="qtile" data-a="qgo" data-v="raise"><span class="mi">${ic('plus')}</span><div>Raise a point<small>from the office, no visit</small></div></button>
  <button type="button" class="qtile" data-a="qgo" data-v="bill" ${p&&p.onb?'':'disabled'}><span class="mi">${ic('bill')}</span><div>Ask for a bill<small>the agency uploads against it</small></div></button><button type="button" class="qtile" data-a="qgo" data-v="new"><span class="mi">${ic('folder')}</span><div>New project<small>onboard in six steps</small></div></button></div>`}};
SHEETS.assign=(dev,s)=>{const p=pOf(s.pid),f=dev.f,a=agOf(f.a_ag),ls=p.lines.filter(l=>l.t===s.t).length;
 return {title:'Decide the '+TX[s.t].n.toLowerCase()+' agency',sub:p.name+' · applies to '+plural(ls,'work line'),body:fld('Agency',fsel(dev,'a_ag',DB.agencies.slice().sort((x,y)=>y.tr.includes(s.t)-x.tr.includes(s.t)).map(x=>[x.id,x.n+(x.tr.includes(s.t)?'':' · other trade')]),'Undecided'))
  +(a?`<div class="note ok">${ic('wa')}<span>MOM points and drawings for this trade go to <b>${esc(a.people.map(x=>x.n).join(', '))}</b> on WhatsApp, in ${({gu:'Gujarati',hi:'Hindi',en:'English'})[a.lang]}.</span></div>`
   :fld('Decide by',chips(dev,'a_by',[[3,fd(3)],[7,fd(7)],[14,fd(14)]]),'Past this date the project shows a blocker to the coordinators and the owner.')),foot:cancelB()+Bt('Save','saveassign',s.pid+'|'+s.t,'gold','check')}};

SHEETS.sendappr=(dev,s)=>{const d=dOf(s.id),f=dev.f,r=cur(d);return {title:(DB.set.approval?'Send for approval · ':'Release · ')+sheetNo(d),sub:d.title+' · revision '+r.n,body:
  `<button type="button" class="drop ${f.sa_file?'on':''}" data-a="tog" data-v="sa_file">${ic(f.sa_file?'file':'plus')}<span>${f.sa_file?`<b>${sheetNo(d)}_rev${r.n}.pdf</b> · 1.4 MB · tap to remove`:'Choose the PDF'}</span></button>`
  +fld('Note for the principal (optional)',fin(dev,'sa_note','What changed, what to check'))+(r.note&&d.revs.length>1?`<div class="note bad">${ic('edit')}${esc(r.note)}</div>`:'')
  +`<div class="note">${ic('info')}${DB.set.approval?'It goes to '+esc(stf(pOf(d.pid).principal).n)+'’s “To approve” list. Nothing reaches an agency or the client before approval.':'“Release needs approval” is off in Setup, so you choose the receivers next.'}</div>`,
  foot:cancelB()+Bt(DB.set.approval?'Send for approval':'Choose receivers','dosend',d.id,'gold','send')}};

SHEETS.approve=(dev,s)=>{const d=dOf(s.id),p=pOf(d.pid),r=cur(d),w=p.lines.filter(l=>l.st==='wait'&&l.cause==='drawing'&&l.ref===d.id);
 return {title:'Approve · '+sheetNo(d)+' '+d.title,sub:p.name+' · revision '+r.n+' · sent by '+stf(r.sentBy).n,wide:true,body:dwgPaper(d)+(r.note?`<div class="note">${ic('info')}${esc(r.note)}</div>`:'')
  +(w.length?`<div class="note wait">${ic('pause')}${plural(w.length,'work line')} waiting for this drawing.</div>`:'')+fld('If it must go back, say why',fin(dev,'ap_note','e.g. Loft depth to match the beam')),
  foot:Bt('Send back','sendback',d.id,'bad ghost')+Bt('Approve','doapprove',d.id,'','check')+Bt('Approve and release','doapprove',d.id+'|rel','gold','send')}};

SHEETS.release=(dev,s)=>{const d=dOf(s.id),p=pOf(d.pid),f=dev.f,own=d.t&&planOf(p,d.t)&&planOf(p,d.t).ag;
 const rows=[...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))].sort((a,b)=>(b===own)-(a===own)).map(a=>[a,agN(a),p.plan.filter(x=>x.ag===a).map(x=>TX[x.t].n).join(', ')+' · '+agOf(a).people.map(x=>x.n).join(', '),a===own?'this drawing’s trade':'']);
 if(d.forClient)rows.push(['client',p.client.n,'Client'+(d.needsApproval?' · will be asked to approve':''),'marked for the client']);
 const n=rows.filter(r=>f['rc_'+r[0]]).length;
 return {title:'Release · '+sheetNo(d)+' '+d.title,sub:p.name+' · revision '+cur(d).n,body:`<div class="lbl">Receivers</div><div class="rows">${rows.map(r=>`<button type="button" class="rw lk ck" data-a="tog" data-v="rc_${r[0]}" aria-pressed="${!!f['rc_'+r[0]]}"><i class="box">${ic('check')}</i><div class="m"><div class="t1">${esc(r[1])}${r[3]?pill(r[3],'gold'):''}</div><div class="t2">${esc(r[2])}</div></div></button>`).join('')}</div>
  ${!d.forClient?`<div class="note">${ic('lock')}Not marked for the client, so the client does not receive it.</div>`:''}<div class="note ok">${ic('wa')}Each receiver gets a WhatsApp message with a secure link and a notification in the app. The first opening is recorded.</div>`,
  foot:cancelB()+`<button type="button" class="btn gold" data-a="dorelease" data-v="${d.id}" ${n?'':'disabled'}>${ic('send')}<span>Release to ${n}</span></button>`}};

SHEETS.logq=(dev,s)=>{const d=dOf(s.id),p=pOf(d.pid);return {title:'Log a question from a call',sub:sheetNo(d)+' '+d.title,body:fld('Asked by',fsel(dev,'lq_by',[...[...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))].map(a=>[a,agN(a)]),['client',p.client.n+' (client)']],'Choose'))+fld('Question',fin(dev,'lq_text','What did they ask')),foot:cancelB()+Bt('Save','dologq',d.id,'gold','check')}};

SHEETS.point=(dev,s)=>{const p=pOf(s.pid),f=dev.f;return {title:'Raise a point',sub:p.name+' · from the office, without a visit',body:fld('For',`<div class="chips">${forOptions(p).map(o=>`<button type="button" class="chip k-${o[2]}" data-a="set" data-v="rp_for=${o[0]}" aria-pressed="${f.rp_for===o[0]}">${esc(o[1])}</button>`).join('')}</div>`)
  +fld('What is needed',fin(dev,'rp_text','e.g. Choose the kitchen platform stone'))+fld('Area',fsel(dev,'rp_area',p.ents.map(e=>[e.id,e.n]),'No single room'))+fld('By',chips(dev,'rp_due',[[0,'Today'],[1,'Tomorrow'],[2,dueW(2)],[5,dueW(5)],[7,fd(7)]]))
  +`<div class="chips">${tog(dev,'rp_photo','Add a photo','cam')}</div>`+(f.rp_for==='client'&&DB.set.clientConfirm?`<div class="note wait">${ic('eye')}Client points wait for the office to confirm before the client sees them (a setting).</div>`:''),foot:cancelB()+Bt('Add point','doraise',p.id,'gold','plus')}};
SHEETS.vendor=(dev,s)=>({title:'Point for a vendor',sub:'A supplier or anyone outside the project’s agencies',body:fld('Name',fin(dev,'vn','e.g. Asian Tiles')),foot:cancelB()+Bt('Use','dovendor',null,'gold')});
SHEETS.closept=(dev,s)=>{const x=ptOf(s.id),p=pOf(x.pid);return {title:'Close point '+x.n,sub:partyName(p,x)+' · '+x.text,body:fld('Closing note',fin(dev,'cp_note','e.g. Done, checked on site'))+`<div class="chips">${tog(dev,'cp_photo','Add a photo','cam')}</div>`,foot:cancelB()+Bt('Close point','doclose',x.id,'gold','check')}};
SHEETS.offerdone=(dev,s)=>{const p=pOf(s.pid),l=p.lines.find(x=>x.id===s.lid);return {title:'Mark the work done?',sub:entN(p,l.e)+' · '+TX[l.t].n,body:`<div class="note ok">${ic('check')}That was the last open point on this cell. If the work itself is finished, mark the line done now.</div>`,foot:Bt('Not yet','close',null,'ghost')+Bt('Mark done','markdone',s.pid+'|'+s.lid,'gold','check')}};

SHEETS.askbill=(dev,s)=>{const f=dev.f,p=pOf(f.ab_pid||s.pid),ags=p?[...new Set(p.plan.filter(x=>x.ag).map(x=>x.ag))]:[];
 return {title:'Ask for a bill',sub:'The agency uploads only against this request. It cannot start one.',body:(s.pid?'':fld('Project',fsel(dev,'ab_pid',myProjects().filter(x=>x.onb).map(x=>[x.id,x.name]),'Choose')))
  +fld('Agency',fsel(dev,'ab_ag',ags.map(a=>[a,agN(a)+' · '+p.plan.filter(x=>x.ag===a).map(x=>TX[x.t].n).join(', ')]),'Choose'))+fld('What is the bill for',fin(dev,'ab_what','e.g. Carpentry, stage 1'))+fld('Up to what amount (optional)',fin(dev,'ab_upto','₹',1))
  +fld('Billed to',chips(dev,'ab_to',[['client','The client'],['revert','Revert']]),p?'Default of this project: '+(p.billedTo==='client'?'the client':'Revert')+'. Change it for this bill if needed.':''),foot:cancelB()+Bt('Ask on WhatsApp','doaskbill',s.pid||'','gold','wa')}};

SHEETS.bill=(dev,s)=>{const b=billOf(s.id),p=pOf(b.pid),f=dev.f,st=BS[b.st],own=isOwner(),pd=paid(b);
 let act='',foot='';
 if(b.st==='asked'||b.st==='returned'){act=(b.st==='returned'?`<div class="note bad">${ic('alert')}Returned: ${esc(b.reason)}</div>`:`<div class="note wait">${ic('clock')}Asked ${fd(b.askedOn)}. Waiting for ${esc(agN(b.ag))} to upload.</div>`)
   +`<div class="lbl mt">Upload on the agency’s behalf</div>`+fld('Bill number',fin(dev,'ub_no','e.g. MF/118'))+fld('Amount',fin(dev,'ub_amt','₹',1))+`<div class="chips">${tog(dev,'ub_doc','Photo or PDF of the bill','cam')}</div>`;foot=Bt('Submit bill','doupload',b.id+'|staff','gold','check')}
 if(b.st==='submitted'){act=fld('If it must go back, say why',fin(dev,'rb_reason','e.g. GST number missing'));foot=Bt('Return','doreview',b.id+'|0','bad ghost')+Bt('Accept','doreview',b.id+'|1','gold','check')}
 if((b.st==='accepted'||b.st==='part_paid')){act=own?`<div class="lbl mt">Record a payment · balance ${inr(b.amount-pd)}</div>`+fld('Amount',fin(dev,'py_amt','₹',1))+fld('Paid by',chips(dev,'py_by',[['client','The client'],['revert','Revert']]))+fld('Mode',chips(dev,'py_mode',[['Bank transfer','Bank transfer'],['UPI','UPI'],['Cheque','Cheque'],['Cash','Cash']]))+`<div class="chips">${tog(dev,'py_proof','Attach proof','file')}</div>`
   :`<div class="note">${ic('lock')}Payments are recorded by the owner.</div>`;foot=own?Bt('Record payment','dopay',b.id,'gold','rupee'):''}
 return {title:agN(b.ag)+' · '+TX[b.t].n,sub:p.name+' · '+b.what,body:`<div class="kv"><div><span>Status</span>${pill(st[0],st[1])}</div><div><span>Amount</span>${b.amount!=null?money(b.amount):'<span class="mu">not uploaded</span>'}</div>${b.upto?`<div><span>Asked up to</span>${money(b.upto)}</div>`:''}<div><span>Bill</span><b>${b.no?esc(b.no)+' · '+fd(b.date):'—'}</b></div><div><span>Asked by</span><b>${esc(stf(b.askedBy).n)} · ${fd(b.askedOn)}</b></div></div>
  ${fld('Billed to',`<div class="chips">${[['client','The client'],['revert','Revert']].map(o=>`<button type="button" class="chip" data-a="billto" data-v="${b.id}|${o[0]}" aria-pressed="${b.billedTo===o[0]}" ${b.st==='paid'?'disabled':''}>${o[1]}</button>`).join('')}</div>`)}
  ${b.no?`<div class="docrow">${ic('file')}<span><b>${esc(b.no)}.jpg</b> · photographed bill</span></div>`:''}
  ${b.pay.length?`<div class="lbl mt">Payments</div><div class="rows">${b.pay.map(x=>`<div class="rw"><div class="m"><div class="t1">${money(x.amount,'c-ok')}</div><div class="t2">${fd(x.on)} · paid by <b>${x.by==='client'?'the client':'Revert'}</b> · ${esc(x.mode)}${x.proof?' · proof attached':''}${x.by==='revert'&&b.billedTo==='client'?' · <span class="c-wait">to recover from the client</span>':''}</div></div></div>`).join('')}</div>`:''}${act}`,foot:foot||Bt('Close','close',null,'ghost')}};

SHEETS.pdf=(dev,s)=>({title:s.kind==='mom'?'MOM PDF':'Open points PDF',sub:'What the party receives on WhatsApp',wide:true,body:pdfDoc(s.kind,s.a,s.b),foot:Bt('Close','close',null,'ghost')});
SHEETS.view=(dev,s)=>{const d=dOf(s.id);return {title:sheetNo(d)+' '+d.title,sub:pOf(d.pid).name,wide:true,body:dwgPaper(d),foot:Bt('Close','close',null,'ghost')}};
SHEETS.addtrade=(dev,s)=>({title:'Add a trade',sub:'Setup · trades',body:fld('Name',fin(dev,'nt_n','e.g. Modular kitchen'))+fld('Name in Gujarati',fin(dev,'nt_gu','ગુજરાતી'))+fld('Name in Hindi',fin(dev,'nt_hi','हिंदी')),foot:cancelB()+Bt('Add','doaddtrade',null,'gold','plus')});
SHEETS.addagency=(dev,s)=>({title:'Add an agency',sub:'Setup · agencies and their people',body:fld('Firm name',fin(dev,'na_n','e.g. Vishwakarma Wood Works'))+fld('Trade',fsel(dev,'na_t',TRADES.map(t=>[t.id,t.n]),'Choose'))+fld('Contact person',fin(dev,'na_p','Name'))+fld('WhatsApp number',fin(dev,'na_ph','98xxx xxxxx',1))+fld('Language',chips(dev,'na_l',[['gu','ગુજરાતી'],['hi','हिंदी'],['en','English']])),foot:cancelB()+Bt('Add','doaddagency',null,'gold','plus')});

/* ---------- onboarding: one guided screen, six steps (phase1_adoption §5.2). It calls the same two methods the API will: proposal and onboard. ---------- */
let OBU=0;
function obStart(dev,pid){const p=pid?pOf(pid):null;
 const ob={pid:p?p.id:null,step:1,name:p?p.name:'',client:p?p.client.n:'',cphone:p?p.client.contacts[0].ph:'',address:p?p.address:'',area:p?p.area:'',kind:p?p.kind:'home',label:p?p.label:'',billedTo:p?p.billedTo:'client',
  principal:p?p.principal:'s1',designers:p?[...p.designers]:[],coords:p?[...p.coords]:[],preset:null,ents:[],tr:{},ticks:{},dr:[],inv:{},nd:''};
 TRADES.forEach(t=>{const pl=p&&planOf(p,t.id);ob.tr[t.id]={on:p&&p.onb?!!pl:DEFAULT_TRADES.includes(t.id),ag:pl?pl.ag||'':'',by:pl&&pl.by!=null?pl.by:7,had:!!pl}});
 if(p){p.ents.forEach(e=>{const u=++OBU;ob.ents.push({u,n:e.n,ty:e.ty,id:e.id});TRADES.forEach(t=>{ob.ticks[u+'|'+t.id]=p.lines.some(l=>l.e===e.id&&l.t===t.id)})});
  DB.drawings.filter(d=>d.pid===p.id).forEach(d=>ob.dr.push({code:d.code,n:d.title,t:d.t||'',on:true,ds:d.ds,due:d.due,client:d.forClient,appr:d.needsApproval,exists:true}))}
 dev.ob=ob;return ob}
function obPreset(ob,name){const ps=PRESETS.find(x=>x.n===name);ob.preset=name;ob.kind=ps.kind==='other'?ob.kind:ps.kind;ob.ents=ob.ents.filter(e=>e.id||e.task);
 ps.e.forEach(([ty,c,f])=>{for(let i=1;i<=c;i++)ob.ents.push({u:++OBU,n:c>1?ty+' '+(i+(f||1)-1):ty,ty})});
 if(!ob.ents.some(e=>e.ty==='Whole site'))ob.ents.push({u:++OBU,n:'Whole site',ty:'Whole site'});if(!ob.label)ob.label=name}
const obTick=(ob,e,t)=>ob.ticks[e.u+'|'+t]!==undefined?ob.ticks[e.u+'|'+t]:(ETX[e.ty]||ETX['Other room']).tr.includes(t);
const obTrades=ob=>TRADES.filter(t=>ob.tr[t.id].on).map(t=>t.id);
function obDrawings(ob){const want=['',...obTrades(ob)],ds=ob.designers.length?ob.designers:[(DB.staff.find(u=>has(u,'designer'))||{id:''}).id];
 ob.dr=ob.dr.filter(d=>d.exists||d.custom||want.includes(d.t));
 DTYPES.filter(x=>want.includes(x.t)).forEach(x=>{if(ob.dr.some(d=>d.code===x.code))return;const first=DTYPES.find(y=>y.t===x.t)===x,svc=['elec','plmb','ac','av'].includes(x.t);
  ob.dr.push({code:x.code,n:x.n,t:x.t,on:x.client||first,ds:svc&&ds[1]?ds[1]:ds[0],due:x.off,client:x.client,appr:x.appr})});
 ob.dr.sort((a,b)=>want.indexOf(a.t)-want.indexOf(b.t))}
const OBSTEPS=['Project','Team','Site','Trades','Drawings','Review'];
function obWizard(dev){const ob=dev.ob,s=ob.step,edit=!!ob.pid&&pOf(ob.pid).onb;let body='';
 const mo=(path,val,ph,cls)=>`<input class="inp ${cls||''}" id="ob_${dev.id}_${path.replace(/\W/g,'_')}" data-mo="${path}" value="${esc(val||'')}" placeholder="${esc(ph||'')}" autocomplete="off">`;
 const msel=(path,val,opts,ph)=>`<select class="inp" id="ob_${dev.id}_${path.replace(/\W/g,'_')}" data-mo="${path}" data-r="1">${ph!=null?`<option value="">${esc(ph)}</option>`:''}${opts.map(o=>`<option value="${esc(o[0])}" ${String(val)===String(o[0])?'selected':''}>${esc(o[1])}</option>`).join('')}</select>`;
 const pick=(key,val,opts)=>`<div class="chips">${opts.map(o=>`<button type="button" class="chip" data-a="obset" data-v="${key}=${o[0]}" aria-pressed="${String(val)===String(o[0])}">${esc(o[1])}</button>`).join('')}</div>`;
 const multi=(key,arr,list)=>`<div class="chips">${list.map(u=>`<button type="button" class="chip tg" data-a="obmulti" data-v="${key}=${u.id}" aria-pressed="${arr.includes(u.id)}">${ic('check')}${esc(u.n)}</button>`).join('')}</div>`;
 if(s===1)body=`<div class="fgrid">${fld('Project name',mo('name',ob.name,'e.g. Shah Residence'))}${fld('Client',mo('client',ob.client,'e.g. Mr. Nirav Shah'))}${fld('Client’s WhatsApp number',mo('cphone',ob.cphone,'98xxx xxxxx'),'Used for the invitation and the sign-in code.')}${fld('Area',mo('area',ob.area,'e.g. Bopal'))}</div>
  ${fld('Site address',mo('address',ob.address,'Flat, building, road'))}${fld('Type of site',pick('kind',ob.kind,[['home','Home'],['office','Office'],['clinic','Clinic / hospital'],['other','Other']]))}
  ${fld('Bills are normally addressed to',pick('billedTo',ob.billedTo,[['client','The client'],['revert','Revert']]),'A default for this project. It can be changed bill by bill.')}`;
 if(s===2){const ds=DB.staff.filter(u=>has(u,'designer')),cs=DB.staff.filter(u=>has(u,'coordinator'));
  body=fld('Principal consultant',pick('principal',ob.principal,DB.staff.filter(u=>has(u,'principal')).map(u=>[u.id,u.n])),'Approves every drawing release.')+fld('Designers',multi('designers',ob.designers,ds),'Each gets the drawings assigned to them on their list.')
   +fld('Coordinators (one or more)',multi('coords',ob.coords,cs),'Keep the agency board and chase open items.')+`<div class="note">${ic('lock')}This is where access comes from: only these people, the agencies of step 4 and the client see this project. Owners and the principal see all projects.</div>`}
 if(s===3){const tasks=ob.pid?pOf(ob.pid).tasks.filter(t=>!/^\d|MOM/i.test(t.n)&&!ob.ents.some(e=>e.task===t.n)):[];
  body=fld('Start from a preset',`<div class="chips">${PRESETS.map(x=>`<button type="button" class="chip" data-a="obpreset" data-v="${esc(x.n)}" aria-pressed="${ob.preset===x.n}">${esc(x.n)}</button>`).join('')}</div>`,'One tap fills the list; then rename, remove or add.')
   +(tasks.length?`<div class="note gold">${ic('layers')}<span>Earlier room tasks of this project. Use one as an entity instead of creating a second: ${tasks.map(t=>`<button type="button" class="chip" data-a="obtask" data-v="${esc(t.n)}">${ic('plus')}${esc(t.n)}</button>`).join(' ')}</span></div>`:'')
   +`<div class="lbl mt">Rooms and zones · ${ob.ents.length} · one task each</div><div class="entlist">${ob.ents.map((e,i)=>`<div class="entrow">${mo('ents.'+i+'.n',e.n,'Name')}${msel('ents.'+i+'.ty',e.ty,ETYPES.map(t=>[t.n,t.n]))}${e.id?pill('exists','plain'):e.task?pill('earlier task','gold'):`<button type="button" class="ib" data-a="obdel" data-v="${i}" aria-label="Remove">${ic('x')}</button>`}</div>`).join('')||empty('Pick a preset or add rooms one by one.','grid')}</div>
   <div class="lbl mt">Add</div><div class="chips">${[...new Set([...ETYPES.filter(t=>t.kind===ob.kind||t.kind==='any').map(t=>t.n),...EXTRAS])].map(n=>`<button type="button" class="chip" data-a="obadd" data-v="${esc(n)}">${ic('plus')}${esc(n)}</button>`).join('')}</div>
   <div class="note">${ic('info')}A “Whole site” entity carries work that belongs to no single room: main board, main lines, final cleaning. No measurements in this release.</div>`}
 if(s===4){const on=obTrades(ob),off=TRADES.filter(t=>!ob.tr[t.id].on);
  body=`<div class="lbl">Trades on this project · ${on.length}</div><div class="trlist">${on.map(t=>{const x=ob.tr[t],ags=DB.agencies.filter(a=>a.tr.includes(t));return `<div class="trrow"><button type="button" class="chip tg" data-a="obtrade" data-v="${t}" aria-pressed="true">${ic('check')}${esc(TX[t].n)}</button>${msel('tr.'+t+'.ag',x.ag,ags.map(a=>[a.id,a.n]),'Undecided')}
    ${x.ag?`<span class="t2">${esc(agOf(x.ag).people.map(p=>p.n).join(', '))}</span>`:`<span class="t2 c-wait">decide by</span>${msel('tr.'+t+'.by',x.by,[[3,fd(3)],[7,fd(7)],[14,fd(14)],[21,fd(21)]])}`}</div>`}).join('')}</div>
   <div class="chips mt">${off.map(t=>`<button type="button" class="chip" data-a="obtrade" data-v="${t.id}">${ic('plus')}${esc(t.n)}</button>`).join('')}</div>
   <div class="lbl mt">Which trade works in which room · pre-ticked from each room type · untick what does not apply</div>
   <div class="gw"><table class="gr tks"><thead><tr><th></th>${on.map(t=>`<th><div class="gh">${esc(TX[t].s)}</div></th>`).join('')}</tr></thead><tbody>${ob.ents.map(e=>`<tr><th><div class="ge">${esc(e.n)}</div></th>${on.map(t=>`<td><button type="button" class="tk" data-a="obtick" data-v="${e.u}|${t}" aria-pressed="${obTick(ob,e,t)}" aria-label="${esc(e.n+' '+TX[t].n)}">${ic('check')}</button></td>`).join('')}</tr>`).join('')}</tbody></table></div>
   <p class="mu f12">${ob.ents.reduce((n,e)=>n+on.filter(t=>obTick(ob,e,t)).length,0)} work lines will exist, one per tick, each carrying its trade’s agency.</p>`}
 if(s===5){const grp={};ob.dr.forEach((d,i)=>(grp[d.t]=grp[d.t]||[]).push([d,i]));const ds=DB.staff.filter(u=>ob.designers.includes(u.id)||has(u,'designer'));
  body=`<div class="lbl">Drawings needed · ${ob.dr.filter(d=>d.on).length} ticked of ${ob.dr.length}</div>${Object.keys(grp).map(t=>`<div class="dgrp"><div class="dgh">${t?esc(TX[t].n)+' · '+(ob.tr[t].ag?esc(agN(ob.tr[t].ag)):'<span class="c-bad">undecided</span>'):'General set'}</div>
   ${grp[t].map(([d,i])=>`<div class="drow ${d.on?'on':''}"><button type="button" class="tk" data-a="obdraw" data-v="${i}" aria-pressed="${d.on}" ${d.exists?'disabled':''} aria-label="${esc(d.n)}">${ic('check')}</button><span class="sheet">${d.code}</span><span class="dn">${esc(d.n)}${d.exists?' <i class="mu">(exists)</i>':''}</span>
    ${d.on&&!d.exists?`${msel('dr.'+i+'.ds',d.ds,ds.map(u=>[u.id,u.n]))}<span class="duectl"><button type="button" class="ib" data-a="obdue" data-v="${i}|-1" aria-label="Earlier">−</button><b class="mono">${fd(d.due)}</b><button type="button" class="ib" data-a="obdue" data-v="${i}|1" aria-label="Later">+</button></span>
    <button type="button" class="chip tg sm" data-a="obflag" data-v="${i}|client" aria-pressed="${d.client}">${ic('check')}client</button><button type="button" class="chip tg sm" data-a="obflag" data-v="${i}|appr" aria-pressed="${d.appr}" ${d.client?'':'disabled'}>${ic('check')}approval</button>`:''}</div>`).join('')}</div>`).join('')}
   <div class="addrow">${mo('nd',ob.nd,'Add a drawing by name, e.g. Bar counter details')}${Bt('Add','obadddraw',null,'','plus')}</div>
   <div class="note">${ic('info')}Designer and due date are pre-filled from the standard set and the team, so most rows need only the tick. “client” = the client receives it; “approval” = the client must approve it.</div>`}
 if(s===6){const on=obTrades(ob),lines=ob.ents.reduce((n,e)=>n+on.filter(t=>obTick(ob,e,t)).length,0),und=on.filter(t=>!ob.tr[t].ag),ags=[...new Set(on.map(t=>ob.tr[t].ag).filter(Boolean))];
  body=`<div class="sumgrid"><div><b class="num">${ob.ents.length}</b><span>rooms and zones</span></div><div><b class="num">${on.length}</b><span>trades${und.length?` · <i class="c-bad">${und.length} undecided</i>`:''}</span></div><div><b class="num">${lines}</b><span>work lines</span></div><div><b class="num">${ob.dr.filter(d=>d.on).length}</b><span>drawings on the list</span></div></div>
   <div class="kv"><div><span>Project</span><b>${esc(ob.name||'—')} · ${esc(ob.label||ob.kind)}</b></div><div><span>Client</span><b>${esc(ob.client||'—')}</b></div><div><span>Team</span><b>${esc([ob.principal,...ob.designers,...ob.coords].filter((v,i,a)=>a.indexOf(v)===i).map(x=>stf(x).n).join(', '))}</b></div><div><span>Bills addressed to</span><b>${ob.billedTo==='client'?'The client':'Revert'}</b></div></div>
   <div class="lbl mt">Invite now on WhatsApp</div><div class="rows">${[...ags.map(a=>[a,agN(a),agOf(a).people[0].n+' · '+agOf(a).people[0].ph]),['client',ob.client||'Client',ob.cphone||'number missing']].map(r=>`<button type="button" class="rw lk ck" data-a="obinv" data-v="${r[0]}" aria-pressed="${!!ob.inv[r[0]]}"><i class="box">${ic('check')}</i><div class="m"><div class="t1">${esc(r[1])}</div><div class="t2">${esc(r[2])}</div></div></button>`).join('')}</div>
   <div class="note ok">${ic('wa')}Nobody has to be invited today. Agencies receive drawings and MOM points on WhatsApp even if they never open the app.</div>`}
 return `<div class="ob"><div class="obh"><div><div class="lbl">${edit?'Project configuration':ob.pid?'Configure an existing project':'New project'} · step ${s} of 6</div><h2>${esc(ob.name||'New project')}</h2></div><button type="button" class="xb" data-a="obclose" aria-label="Close">${ic('x')}</button></div>
  <ol class="steps">${OBSTEPS.map((n,i)=>`<li class="${i+1===s?'on':i+1<s?'past':''}"><button type="button" data-a="obgo" data-v="${i+1}"><i>${i+1<s?ic('check'):i+1}</i><span>${n}</span></button></li>`).join('')}</ol>
  <div class="obb" data-sc="ob${s}">${body}</div><div class="obf">${s>1?Bt('Back','obgo',s-1,'ghost','back'):'<span></span>'}${s<6?Bt(s===5?'Review':'Next','obgo',s+1,'gold'):Bt(edit?'Save changes':'Start project','obfinish',null,'gold','check')}</div></div>`}
function obApply(ob){let p=ob.pid?pOf(ob.pid):null;const fresh=!p,was=p&&p.onb;
 if(!p){p={id:++DB.seq.pid,tasks:[],plan:[],ents:[],lines:[],visitNo:0,client:{n:'',contacts:[]}};DB.projects.push(p)}
 Object.assign(p,{name:ob.name,kind:ob.kind,label:ob.label||ob.kind,area:ob.area,address:ob.address,billedTo:ob.billedTo,principal:ob.principal,designers:[...ob.designers],coords:[...ob.coords],onb:true,onbOn:p.onbOn==null?0:p.onbOn});
 p.client.n=ob.client;if(!p.client.contacts.length)p.client.contacts.push({n:ob.client.replace(/^(Mr\.|Mrs\.|Dr\.)\s*/,''),ph:ob.cphone,inv:false});
 const on=obTrades(ob);on.forEach(t=>{const x=ob.tr[t];let pl=planOf(p,t);if(!pl){pl={t,ag:null,people:[],by:null};p.plan.push(pl)}pl.ag=x.ag||null;pl.by=x.ag?null:+x.by;pl.people=x.ag?[0]:[]});
 p.plan=p.plan.filter(pl=>on.includes(pl.t)||p.lines.some(l=>l.t===pl.t));let nl=0,nd=0;
 ob.ents.forEach((e,i)=>{let ent=e.id&&p.ents.find(x=>x.id===e.id);if(!ent){ent={id:'e'+p.id+'_n'+e.u,n:e.n,ty:e.ty};p.ents.push(ent)}else{ent.n=e.n;ent.ty=e.ty}
  on.forEach(t=>{const has=p.lines.find(l=>l.e===ent.id&&l.t===t);if(obTick(ob,e,t)&&!has){p.lines.push({id:'l'+(++DB.seq.lid),e:ent.id,t,ag:null,st:'ns',cause:null,ref:null,note:'',since:null,fin:null,doneOn:null,startOn:null});nl++}
   if(!obTick(ob,e,t)&&has&&has.st==='ns')p.lines.splice(p.lines.indexOf(has),1)})});
 ob.ents.filter(e=>e.task).forEach(e=>{p.tasks=p.tasks.filter(t=>t.n!==e.task)});
 ob.dr.filter(d=>d.on&&!d.exists).forEach(d=>{const no=DB.drawings.filter(x=>x.pid===p.id&&x.code===d.code).length+1;DB.drawings.push({id:'d'+(++DB.seq.did),pid:p.id,code:d.code,no,title:d.n,t:d.t||null,e:null,ds:d.ds,due:+d.due,forClient:!!d.client,needsApproval:!!(d.client&&d.appr),st:'to_draw',revs:[{n:1,st:'draft',note:'',rc:[]}],q:[]});nd++});
 let inv=0;Object.keys(ob.inv).filter(k=>ob.inv[k]).forEach(k=>{if(k==='client'){p.client.contacts[0].inv=true;notify('invite','client:'+p.id,{site:p.name})}else notify('invite',k,{site:p.name});inv++});
 return {p,nl,nd,inv,fresh,was}}

/* ---- desk.js ---- */
/* Revert Desk: the single window for staff in the browser (rvt_desk), in the Glass theme's own layout:
   a glass navbar on top, frosted panes on the colour field, one strong focus card. List on the left, the record on the right. */
const DNAV=[['today','Today','home'],['projects','Projects','folder'],['drawings','Drawings','dwg'],['mom','MOM','mom'],['bills','Bills','bill'],['review','Review','review'],['setup','Setup','setup']];
function deskCounts(){const ps=myProjects().filter(p=>p.onb).map(p=>p.id);return {today:todayFor(me()).length,projects:myProjects().length,drawings:DB.drawings.filter(d=>ps.includes(d.pid)&&d.st!=='released').length,
 mom:DB.points.filter(x=>ps.includes(x.pid)&&x.st==='open').length,bills:DB.bills.filter(b=>ps.includes(b.pid)&&['submitted','asked','accepted','part_paid'].includes(b.st)).length}}
function deskLogin(dev){const u=me();return `<div class="bw"><div class="bw-bar"><i></i><i></i><i></i><div class="url">${ic('lock')}erp.revert.co.in/office/login</div></div><div class="scr"><div class="desk"><div class="dlogin enter">
  <section class="ink dl-art"><div class="tbr"><span>Revert Desk</span><span>${fdw(0)}</span></div><div class="dl-logo">${LOGO}</div><p class="atag">Architecture · Interior · Green Building</p><h1 class="serif">Every site, <em>drawn</em> and up to date.</h1>
   <p class="hnext">Set a project up once. After that there are two daily acts: releasing a drawing, and writing a point on site. The picture of every project follows from those.</p>${street(DB.projects,workShare,p=>p.area).replace(/data-a="proj"/g,'tabindex="-1"')}</section>
  <section class="dl-form"><h2 class="serif">Welcome back</h2><p class="t2">Log in to the back office.</p>${fld('Email',`<input class="inp" id="dk_login" value="${u.login}@revert.co.in" readonly>`)}${fld('Password',`<input class="inp" id="dk_pw" type="password" value="••••••••" readonly>`)}
   ${Bt('Log in','signin',null,'gold lg blk')}<div class="lbl mt">Demo · log in as</div><div class="chips">${demoUsers()}</div><p class="mu f12">Each person sees only their own projects; money is visible to the owner alone.</p></section></div>${sheetHTML(dev)}</div></div></div>`}
function deskHTML(dev){if(!dev.signed)return deskLogin(dev);const u=me(),c=deskCounts(),sec=dev.sec==='onboard'?'projects':dev.sec,k=dev.sec+'|'+(dev.sec==='projects'?dev.pid+'|'+(dev.ptab||''):dev.sec==='onboard'&&dev.ob?dev.ob.step:''),fresh=dev._k!==k;dev._k=k;
 const body={today:deskToday,projects:deskProjects,drawings:deskDrawings,mom:deskMom,bills:deskBills,review:deskReview,setup:deskSetup,onboard:d=>`<div class="pad">${obWizard(d)}</div>`}[dev.sec](dev);
 return `<div class="bw"><div class="bw-bar"><i></i><i></i><i></i><div class="url">${ic('lock')}erp.revert.co.in/office</div></div>
 <div class="scr"><div class="desk"><header class="gnav"><button type="button" class="gn-home" data-a="nav" data-v="today" aria-label="Home">${ic('home')}</button><div class="gn-app">${LOGO}</div>
  <nav class="gn-menu" aria-label="Revert Desk">${DNAV.map(n=>`<button type="button" data-a="nav" data-v="${n[0]}" ${sec===n[0]?'aria-current="page"':''}>${ic(n[2])}<span>${n[1]}</span>${c[n[0]]?`<b>${c[n[0]]}</b>`:''}</button>`).join('')}</nav>
  <div class="gn-r"><span class="gn-co"><i></i>Revert Architects</span><div class="gn-u">${av(u.n)}<div><b>${esc(u.full)}</b><small>${roleLabel(u)}</small></div></div><button type="button" class="ib gn-out" data-a="signout" aria-label="Log out" title="Log out">${ic('out')}</button></div></header>
  <main class="dmain${fresh?' enter':''}" data-sc="dmain_${dev.sec}">${body}</main></div>${sheetHTML(dev)}</div></div>`}
const dhead=(title,sub,right)=>`<header class="dh"><div><h1 class="serif">${title}</h1>${sub?`<p>${sub}</p>`:''}</div><div class="dhr">${right||''}</div></header>`;
const tabsH=(dev,key,list)=>`<div class="tabs" role="tablist">${list.map(t=>`<button type="button" role="tab" data-a="ui" data-v="${key}=${t[0]}" aria-selected="${(dev[key]||list[0][0])===t[0]}">${esc(t[1])}${t[2]!=null?`<i>${t[2]}</i>`:''}</button>`).join('')}</div>`;

const SAY={approve:['drawing to approve','drawings to approve'],draw:['drawing to make','drawings to make'],change:['change to draw','changes to draw'],release:['drawing to release','drawings to release'],question:['question to answer','questions to answer'],decide:['agency to decide','agencies to decide'],
 confirm:['client point to confirm','client points to confirm'],bill:['bill to review','bills to review'],chase:['agency to chase','agencies to chase'],client:['client item to chase','client items to chase'],point:['open point of your own','open points of your own']};
function summary(items){const parts=SECS.map(s=>{const n=items.filter(x=>x.sec===s[0]).length;return n?n+' '+SAY[s[0]][n===1?0:1]:''}).filter(Boolean);
 return parts.length?'You have '+(parts.length>1?parts.slice(0,-1).join(', ')+' and '+parts[parts.length-1]:parts[0])+'.':'All clear. Nothing waits for you.'}
function weekLine(u){const mine=DB.drawings.filter(d=>d.st==='released'&&cur(d).relOn>-7&&(has(u,'designer')?d.ds===u.id:canSee(u,pOf(d.pid)))),rc=mine.flatMap(d=>cur(d).rc);
 return `<div class="week">${ic('refresh')}<span>This week</span> <b>${mine.length}</b> released · <b class="c-ok">${rc.filter(x=>x.opened!=null).length}</b> opened · <b class="${rc.some(x=>x.opened==null)?'c-bad':''}">${rc.filter(x=>x.opened==null).length}</b> not opened</div>`}
function deskToday(dev){const u=me(),it=todayFor(u),ps=myProjects(),on=ps.filter(p=>p.onb),pics=on.map(p=>picture(p));
 const tasks=ps.flatMap(p=>p.tasks.map(t=>[p,t])).slice(0,5).map(([p,t])=>`<div class="rw"><div class="m"><div class="t1">${esc(t.n)}</div><div class="t2">${esc(p.name)} · ${esc(t.stage)}${t.subs?' · '+t.subs+' sub-tasks':''}</div></div></div>`).join('');
 return `<div class="home"><div class="stack"><section class="ink hero"><div class="tbr"><span>${fdw(0)}</span><span>${roleLabel(u)}</span></div><h1 class="serif">Good morning, <em>${esc(u.n)}</em></h1><p class="hnext">${summary(it)}</p>
    <div class="actbar">${it.length?`<button type="button" class="btn brz" data-a="startq">${ic('play')}<span>Start with the first · ${it.length}</span></button>`:''}${Bt('New project','onb','','oni','plus')}</div>
    ${street(ps,workShare,p=>p.onb?DB.points.filter(x=>x.pid===p.id&&x.st==='open').length+' open':'configure')}</section>
   ${tasks?card('Hand-made tasks','<span class="mu f12">both ways stay</span>',`<div class="rows">${tasks}</div>`):''}</div>
  <div class="stack"><div class="kpis">${kpi('To do',it.length,'c-gold')}${kpi('Blockers',pics.reduce((n,x)=>n+x.blockers.length,0),'c-bad')}${kpi('Open points',pics.reduce((n,x)=>n+x.progress.pt[2],0))}${kpi('To release',pics.reduce((n,x)=>n+x.progress.dr[1]-x.progress.dr[0],0),'c-work')}</div>
   <div class="sech"><h3>To do</h3></div>${todoList(dev,it)}${weekLine(u)}</div>
  <aside class="stack"><div class="sech"><h3>${has(u,'coordinator')?'My sites':'Sites'}</h3>${Bt('New','onb','','sm','plus')}</div>${ps.map(p=>siteCard(p,null,'wide')).join('')}</aside></div>`}

function projHeader(p){return `<div class="prjh"><div class="m"><div class="lbl">${esc(p.label)} · ${esc(p.area)}</div><h1 class="serif">${esc(p.name)}</h1><div class="team">${[p.principal,...p.designers,...p.coords].filter((v,i,a)=>a.indexOf(v)===i).map(s=>av(stf(s).n,'sm')).join('')}<span class="t2">client <b>${esc(p.client.n)}</b>${p.coords.length?' · coordinators '+esc(p.coords.map(s=>stf(s).n).join(', ')):''}</span></div></div>
 <div class="phr">${p.onb?stPill(p):''}${Bt(p.onb?'Project configuration':'Configure this project','onb',p.id,p.onb?'sm':'gold','setup')}</div></div>`}
function projTab(p,dev){const t=dev.ptab||'picture',pic=picture(p),dws=DB.drawings.filter(d=>d.pid===p.id),pts=DB.points.filter(x=>x.pid===p.id),bills=DB.bills.filter(b=>b.pid===p.id);
 if(t==='picture')return pictureBlock(p,dev);
 if(t==='work')return `<div class="two wk">${workView(p,dev)}<div class="stack">${card('By agency','',`<div class="rows">${byAgency(p)||empty('No agency decided yet.','users')}</div>`)}
   ${card('Trades and agencies','',`<div class="rows">${p.plan.map(x=>`<div class="rw"><div class="m"><div class="t1">${esc(TX[x.t].n)}</div><div class="t2 ${x.ag?'':'c-bad'}">${x.ag?esc(agN(x.ag))+' · '+esc(agOf(x.ag).people.map(q=>q.n).join(', ')):'undecided · decide by '+fd(x.by)}</div></div><div class="r">${Bt(x.ag?'Change':'Assign','assign',p.id+'|'+x.t,x.ag?'sm':'sm gold')}</div></div>`).join('')}</div>`)}</div></div>`;
 if(t==='drawings')return card('Drawing register',Bt('Add drawings','onbstep',p.id+'|5','sm','plus'),`<div class="rows">${dws.slice().sort((a,b)=>a.due-b.due).map(d=>dwgRow(d,dev)).join('')||empty('No drawing on the list yet.','dwg')}</div>`);
 if(t==='mom'){const v=dev.vid&&visOf(dev.vid);if(v&&v.pid===p.id)return `<div class="stack">${Bt('All visits','ui','vid=','sm ghost','back')}${momCapture(v,dev)}</div>`;
  const f=dev.mf||'open',list=pts.filter(x=>f==='all'||x.st===f).sort((a,b)=>b.n-a.n),vs=DB.visits.filter(x=>x.pid===p.id).sort((a,b)=>b.no-a.no);
  return `<div class="stack">${card('Visits',Bt('Start MOM','startmom',p.id,'sm gold','plus'),`<div class="rows">${vs.map(x=>{const n=pts.filter(q=>q.vid===x.id);return `<div class="rw"><span class="cal"><i>${MON[dt(x.date).getUTCMonth()]}</i><b>${dt(x.date).getUTCDate()}</b></span><div class="m"><div class="t1">Visit ${x.no} ${x.st==='open'?pill('open','work'):''}</div><div class="t2">by ${esc(stf(x.by).n)} · ${plural(n.length,'point')} · ${n.filter(q=>q.st==='open').length} open · present: ${esc(x.att.join(', '))}</div></div><div class="r">${Bt('PDF','pdf','mom|'+x.id+'|all','sm ghost','file')}${Bt('Open','ui','vid='+x.id,'sm')}</div></div>`}).join('')||empty('No visit yet. Start the first MOM.','mom')}</div>`)}
   ${card('Points',`<div class="seg sm">${[['open','Open'],['closed','Closed'],['all','All']].map(o=>`<button data-a="ui" data-v="mf=${o[0]}" aria-pressed="${f===o[0]}">${o[1]}</button>`).join('')}</div>${Bt('PDF','pdf','open|'+p.id,'sm ghost','file')}${Bt('Raise point','raise',p.id,'sm','plus')}`,`<div class="rows">${list.map(x=>ptRow(x,dev)).join('')||empty('Nothing here.')}</div>`)}</div>`}
 if(t==='client'){const un=pts.filter(x=>x.kind==='client'&&x.st==='open'&&!x.confirmed),cd=dws.filter(d=>d.forClient);
  return `<div class="stack"><div class="two">${card('Client access','',`<div class="rows">${p.client.contacts.map((c,i)=>`<div class="rw"><div class="m"><div class="t1">${av(c.n,'sm')}<span>${esc(c.n)}</span></div><div class="t2">${esc(c.ph)} · ${c.inv?'<span class="c-ok">invited · app or link</span>':'not invited yet'}</div></div><div class="r">${c.inv?Bt('Copy link','copylink',p.id,'sm ghost','link'):Bt('Invite','invite',p.id+'|'+i,'sm wa','wa')}</div></div>`).join('')}</div>
    <div class="note">${ic('eye')}The client sees two things only: the drawings marked for the client, and what Revert needs from them.</div>`)}
   ${card('Waiting for the client',Bt('Raise item','raiseclient',p.id,'sm','plus'),`<div class="rows">${nextRows(p,pic,{nt:'client'})}${un.map(x=>ptRow(x,dev)).join('')}</div>`)}</div>
   ${card('Drawings for the client','',`<div class="rows">${cd.map(d=>dwgRow(d,dev)).join('')||empty('No drawing is marked for the client.','dwg')}</div>`)}</div>`}
 if(t==='bills')return `<div class="stack">${card('Bills',Bt('Ask for bill','askbill',p.id,'sm gold','plus'),`<div class="rows">${bills.map(b=>billRow(b,dev)).join('')||empty('No bill asked yet.','bill')}</div>`)}${isOwner()?card('Money on this project',pill('owner only','gold','lock'),moneyView(bills)):`<div class="note">${ic('lock')}Amounts and totals are visible to the owner only.</div>`}</div>`;
 return card('Earlier tasks','<span class="mu f12">made by hand · they keep working as before</span>',`<div class="rows">${p.tasks.map(x=>`<div class="rw"><div class="m"><div class="t1">${esc(x.n)}</div><div class="t2">${esc(x.stage)} · ${x.subs} sub-tasks · ${x.mom} MOM ${x.mom===1?'entry':'entries'}${x.moved?' moved to the new MOM':''}</div></div><div class="r">${/^\d|MOM/i.test(x.n)?'<span class="mu f12">date task · no longer needed for MOM</span>':Bt('Use as a room','taskent',p.id+'|'+x.id,'sm')}</div></div>`).join('')||empty('No hand-made task on this project.','list')}</div>
   <div class="note">${ic('info')}Staff can keep creating tasks by hand. “Use as a room” marks an earlier room task as an entity instead of creating a second one.</div>`)}
function deskProjects(dev){const ps=myProjects(),p=ps.find(x=>x.id===dev.pid)||ps[0];if(!p)return dhead('Projects','')+empty('No project is visible to you yet.','folder');
 const tabs=p.onb?[['picture','Picture'],['work','Work'],['drawings','Drawings',DB.drawings.filter(d=>d.pid===p.id&&d.st!=='released').length],['mom','MOM',DB.points.filter(x=>x.pid===p.id&&x.st==='open').length],['client','Client'],['bills','Bills'],['tasks','Earlier tasks']]:[['mom','MOM'],['tasks','Earlier tasks']];
 if(!tabs.some(t=>t[0]===(dev.ptab||'picture')))dev.ptab=tabs[0][0];dev.pid=p.id;
 return `<div class="split"><aside class="sl" data-sc="plist"><div class="slh"><h2 class="serif">Projects</h2>${Bt('New','onb','','sm gold','plus')}</div>${ps.map(x=>siteCard(x,dev,'row')).join('')}</aside>
  <section class="sd" data-sc="pdetail">${projHeader(p)}${!p.onb?`<div class="note gold big">${ic('layers')}<span><b>This project runs the earlier way.</b> ${p.tasks.length} hand-made tasks and their MOM entries are here. Configure it to add rooms, trades and drawings beside what is there; nothing is converted or removed.</span></div>`:''}
  ${tabsH(dev,'ptab',tabs)}${projTab(p,dev)}</section></div>`}

function deskDrawings(dev){const ps=myProjects().map(p=>p.id),mine=dev.dmine==='mine',all=DB.drawings.filter(d=>ps.includes(d.pid)&&(!mine||d.ds===UI.user));
 const G={draw:all.filter(d=>d.st==='to_draw'||d.st==='in_progress'),awaiting:all.filter(d=>d.st==='awaiting'),release:all.filter(d=>d.st==='approved'),released:all.filter(d=>d.st==='released'),unopened:all.filter(d=>d.st==='released'&&cur(d).rc.some(r=>r.opened==null)),q:all.filter(d=>d.q.some(q=>!q.ans))};
 const t=dev.dtab||'draw',list=G[t].slice().sort((a,b)=>t==='released'?cur(b).relOn-cur(a).relOn:a.due-b.due),d=list.find(x=>x.id===dev.drawer)||dOf(dev.drawer)||list[0];
 return dhead('Drawings','All drawings across your projects. A drawing is released only through the system.',`<div class="seg sm">${[['all','All'],['mine','Mine']].map(o=>`<button data-a="ui" data-v="dmine=${o[0]}" aria-pressed="${(dev.dmine||'all')===o[0]}">${o[1]}</button>`).join('')}</div>`)
  +tabsH(dev,'dtab',[['draw','To draw',G.draw.length],['awaiting','Awaiting approval',G.awaiting.length],['release','To release',G.release.length],['released','Released',G.released.length],['unopened','Not opened',G.unopened.length],['q','Questions',G.q.length]])
  +`<div class="split in"><aside class="sl" data-sc="dlist"><div class="rows sel">${list.map(x=>dwgRow(x,dev,true).replace('class="rw lk"',`class="rw lk ${d&&d.id===x.id?'cur':''}"`)).join('')||empty('Nothing in this list.')}</div></aside><section class="sd" data-sc="ddetail">${d?dwgDetail(d,dev):empty('Choose a drawing.','dwg')}</section></div>`}

function deskMom(dev){const ps=myProjects().map(p=>p.id),pf=dev.mp?+dev.mp:0,pts=DB.points.filter(x=>ps.includes(x.pid)&&(!pf||x.pid===pf)),open=pts.filter(x=>x.st==='open'),f=dev.mf||'open';
 const by={};open.forEach(x=>{const k=partyName(pOf(x.pid),x);by[k]=by[k]||[0,0];by[k][0]++;if(x.due<0)by[k][1]++});const top7=Object.entries(by).sort((a,b)=>b[1][0]-a[1][0]).slice(0,7);
 const wk=[5,4,3,2,1,0].map(w=>{const a=-7*w-6,b=-7*w;return [fd(a),pts.filter(x=>{const v=x.vid&&visOf(x.vid),on=v?v.date:-1;return on>=a&&on<=b}).length,pts.filter(x=>x.st==='closed'&&x.closedOn>=a&&x.closedOn<=b).length]}),wm=Math.max(1,...wk.map(x=>Math.max(x[1],x[2])));
 const list=pts.filter(x=>f==='all'||(f==='late'?x.st==='open'&&x.due<0:x.st===f)).sort((a,b)=>a.due-b.due),vs=DB.visits.filter(v=>ps.includes(v.pid)&&(!pf||v.pid===pf)).sort((a,b)=>b.date-a.date);
 return dhead('MOM','Visits and points across projects. A point agreed on site is a MOM point in the app.',`<select class="inp sm" data-ui="mp" aria-label="Project"><option value="">All projects</option>${myProjects().map(p=>`<option value="${p.id}" ${pf===p.id?'selected':''}>${esc(p.name)}</option>`).join('')}</select>`)
  +`<div class="kpis">${kpi('Open points',open.length)}${kpi('Past their date',open.filter(x=>x.due<0).length,'c-bad')}${kpi('Closed this week',pts.filter(x=>x.st==='closed'&&x.closedOn>-7).length,'c-ok')}${kpi('Visits this month',vs.filter(v=>v.date>-18).length,'c-gold')}</div>
  <div class="two">${card('Open points by person','<span class="mu f12">one tick per point · red = past its date</span>',`<div class="hbars">${top7.map(e=>`<div class="hb"><span>${esc(e[0])}</span>${ticks(e[1][1],e[1][0],'split')}<b class="num">${e[1][0]}</b></div>`).join('')||empty('No open point.')}</div>`)}
  ${card('Raised and closed, by week','',`<div class="vbars">${wk.map(x=>`<div class="vb"><div class="vbt"><i style="height:${x[1]/wm*100}%" title="${x[1]} raised"></i><i class="ok" style="height:${x[2]/wm*100}%" title="${x[2]} closed"></i></div><span>${x[0]}</span></div>`).join('')}</div><div class="legend"><span><i class="sw gold"></i>raised</span><span><i class="sw done"></i>closed</span></div>`)}</div>
  <div class="two">${card('Points',`<div class="seg sm">${[['open','Open'],['late','Past date'],['closed','Closed'],['all','All']].map(o=>`<button data-a="ui" data-v="mf=${o[0]}" aria-pressed="${f===o[0]}">${o[1]}</button>`).join('')}</div>`,`<div class="rows">${list.map(x=>ptRow(x,dev,{proj:1})).join('')||empty('Nothing here.')}</div>`)}
  ${card('Visits','',`<div class="rows">${vs.map(v=>{const n=DB.points.filter(q=>q.vid===v.id);return `<div class="rw"><span class="cal"><i>${MON[dt(v.date).getUTCMonth()]}</i><b>${dt(v.date).getUTCDate()}</b></span><div class="m"><div class="t1">${esc(pOf(v.pid).name)} · visit ${v.no}</div><div class="t2">by ${esc(stf(v.by).n)} · ${plural(n.length,'point')}, ${n.filter(q=>q.st==='open').length} open</div></div><div class="r">${Bt('PDF','pdf','mom|'+v.id+'|all','sm ghost','file')}${Bt('Open','openvisit',v.id,'sm')}</div></div>`}).join('')}</div>`)}</div>`}

function deskBills(dev){const ps=myProjects().map(p=>p.id),all=DB.bills.filter(b=>ps.includes(b.pid)),G={review:all.filter(b=>b.st==='submitted'),asked:all.filter(b=>b.st==='asked'||b.st==='returned'),unpaid:all.filter(b=>b.st==='accepted'||b.st==='part_paid'),paid:all.filter(b=>b.st==='paid'),all};
 const t=dev.btab||'review';return dhead('Bills','Revert asks, the agency uploads, Revert records what is paid and by whom. No advances.',Bt('Ask for a bill','askbill','','gold','plus'))
  +tabsH(dev,'btab',[['review','To review',G.review.length],['asked','Asked',G.asked.length],['unpaid','Unpaid',G.unpaid.length],['paid','Paid',G.paid.length],['all','All',all.length]])
  +`<div class="stack">${card('Bills','',`<div class="rows">${G[t].map(b=>billRow(b,dev,true)).join('')||empty('Nothing in this list.')}</div>`)}${isOwner()?card('Money, all projects',pill('owner only','gold','lock'),moneyView(all)):`<div class="note">${ic('lock')}Amounts and totals are visible to the owner only. You see the document and the status.</div>`}</div>`}

function deskReview(dev){const ps=myProjects(),rows=ps.map(p=>[p,picture(p)]),n=k=>rows.filter(r=>r[0].onb&&r[1].status===k).length;
 const cellp=(a,b,c,w)=>`<td><div class="num"><b>${a}</b><span class="mu"> / ${b}</span></div>${ticks(a,b,c,w)}</td>`;
 return dhead('Review','The weekly board. One row per project; every count opens the project.','')
  +`<div class="kpis">${kpi('Stuck',n('stuck'),'c-bad')}${kpi('Needs attention',n('attention'),'c-wait')}${kpi('On track',n('ok'),'c-ok')}${kpi('Not configured',ps.filter(p=>!p.onb).length)}</div>
  ${card('Projects','',`<div class="tw"><table class="tb rv"><thead><tr><th>Project</th><th>Status</th><th>Agencies</th><th>Drawings</th><th>Work</th><th>Points</th><th>Blockers</th><th></th></tr></thead><tbody>${rows.map(([p,pic])=>{const g=pic.progress,old=pic.blockers[0];
   return p.onb?`<tr class="lk" data-a="proj" data-v="${p.id}"><td><b>${esc(p.name)}</b><div class="t2">${esc(p.label)}</div></td><td>${stPill(p)}</td>${cellp(g.ag[0],g.ag[1],'brz')}${cellp(g.dr[0],g.dr[1],'brz')}${cellp(g.wk[0],g.wk[1],'ok',g.wk[2])}${cellp(g.pt[0],g.pt[1],'ok')}<td>${pic.blockers.length?`<b class="c-bad num">${pic.blockers.length}</b><div class="t2">${esc(old.text)} · ${old.age} d</div>`:'<span class="c-ok b">none</span>'}</td><td>${ic('chev','mu')}</td></tr>`
    :`<tr class="lk" data-a="proj" data-v="${p.id}"><td><b>${esc(p.name)}</b><div class="t2">${esc(p.label)}</div></td><td>${pill('to configure','gold')}</td><td colspan="5" class="mu">Runs the earlier way: ${p.tasks.length} hand-made tasks. Configure it to see its picture.</td><td>${ic('chev','mu')}</td></tr>`}).join('')}</tbody></table></div>`)}`}

function deskSetup(dev){const t=dev.stab||'settings',s=DB.set,own=isOwner();let b='';
 const sw=(k,on,label,hint)=>`<button type="button" class="sw-row" data-a="setting" data-v="${k}" aria-pressed="${on}"><i class="switch"></i><div><b>${label}</b><small>${hint}</small></div></button>`;
 const stp=(k,label,hint)=>`<div class="sw-row"><div class="stepper"><button type="button" class="ib" data-a="limit" data-v="${k}|-1" aria-label="Less">−</button><b class="num">${s.lim[k]}</b><button type="button" class="ib" data-a="limit" data-v="${k}|1" aria-label="More">+</button></div><div><b>${label}</b><small>${hint}</small></div></div>`;
 if(t==='settings')b=`<div class="two">${card('Rules','',sw('approval',s.approval,'Release needs the principal’s approval','On: a designer sends for approval and the principal approves. Off: the designer releases directly.')+sw('clientConfirm',s.clientConfirm,'Client points need the office to confirm','On: a point for the client appears to them only after the office confirms it.'))}
   ${card('Day limits for the project picture','',stp('open','Drawing not opened','days after release before it becomes a blocker (B8)')+stp('q','Question unanswered','working days before it becomes a blocker (B9)')+stp('bill','Bill not reviewed','days after upload before it becomes a blocker (B10)')+stp('stuck','Stuck','a blocker older than this many days turns the project “Stuck”'))}</div>
   ${card('WhatsApp','',sw('sending',s.sending,'Sending is on','Off: nothing leaves; every message is logged as “held”. Always off on a test copy.')+`<div class="kv"><div><span>Dedicated number</span><b class="mono">${s.number}</b></div><div><span>Connector</span><b class="c-ok">paired · caps per minute and per day stay on</b></div></div>`)}`;
 if(t==='trades')b=card('Trades',Bt('Add a trade','sheet','addtrade','sm gold','plus'),`<div class="tw"><table class="tb"><thead><tr><th>Trade</th><th>Short</th><th>ગુજરાતી</th><th>हिंदी</th><th>Agencies</th></tr></thead><tbody>${TRADES.map(x=>`<tr><td><b>${esc(x.n)}</b></td><td class="mono">${esc(x.s)}</td><td class="gu">${esc(x.gu)}</td><td class="gu">${esc(x.hi)}</td><td>${DB.agencies.filter(a=>a.tr.includes(x.id)).length}</td></tr>`).join('')}</tbody></table></div>`);
 if(t==='rooms')b=card('Room types and their usual trades','<span class="mu f12">tap to change what is pre-ticked at onboarding</span>',`<div class="gw"><table class="gr tks"><thead><tr><th></th>${TRADES.slice(0,14).map(x=>`<th><div class="gh">${esc(x.s)}</div></th>`).join('')}</tr></thead><tbody>${ETYPES.map(e=>`<tr><th><div class="ge">${esc(e.n)}</div><div class="gs mu">${e.kind}</div></th>${TRADES.slice(0,14).map(x=>`<td><button type="button" class="tk" data-a="ettoggle" data-v="${esc(e.n)}|${x.id}" aria-pressed="${e.tr.includes(x.id)}" aria-label="${esc(e.n+' '+x.n)}">${ic('check')}</button></td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
 if(t==='presets')b=`<div class="pgrid">${PRESETS.map(p=>card(esc(p.n),pill(p.kind,'plain'),`<div class="chips ro">${p.e.map(e=>`<span class="chip">${esc(e[0])}${e[1]>1?' × '+e[1]:''}</span>`).join('')}<span class="chip">Whole site</span></div>`)).join('')}</div>`;
 if(t==='sets')b=card('Standard drawing sets','<span class="mu f12">proposed at onboarding for every ticked trade</span>',`<div class="tw"><table class="tb"><thead><tr><th>Code</th><th>Drawing</th><th>Trade</th><th>For client</th><th>Client approves</th><th class="ar">Due after</th></tr></thead><tbody>${DTYPES.map((x,i)=>`<tr><td><span class="sheet">${x.code}</span></td><td><b>${esc(x.n)}</b></td><td>${x.t?esc(TX[x.t].n):'<span class="c-gold b">General set</span>'}</td>
   <td><button type="button" class="tk" data-a="dtflag" data-v="${i}|client" aria-pressed="${x.client}" aria-label="for client">${ic('check')}</button></td><td><button type="button" class="tk" data-a="dtflag" data-v="${i}|appr" aria-pressed="${x.appr}" aria-label="client approves">${ic('check')}</button></td><td class="ar num">${x.off} d</td></tr>`).join('')}</tbody></table></div>`);
 if(t==='agencies')b=card('Agencies and their people',Bt('Add an agency','sheet','addagency','sm gold','plus'),`<div class="rows">${DB.agencies.map(a=>`<div class="rw"><div class="m"><div class="t1">${av(a.n,'sm')}<span>${esc(a.n)}</span><span class="mu f12"> · ${esc(a.tr.map(x=>TX[x].n).join(', '))}</span></div><div class="t2">${a.people.map(p=>esc(p.n)+' · <span class="mono">'+esc(p.ph)+'</span>').join(' &nbsp;|&nbsp; ')}</div></div><div class="r">${pill(({gu:'ગુજરાતી',hi:'हिंदी',en:'English'})[a.lang],'plain','globe')}${pill(plural(agProjects(a.id).length,'site'),'gold')}</div></div>`).join('')}</div>`);
 if(t==='staff')b=card('Staff and roles',own?'':pill('owner only','gold','lock'),`<div class="rows">${DB.staff.map(u=>`<div class="rw"><div class="m"><div class="t1">${av(u.n,'sm')}<span>${esc(u.full)}</span></div><div class="t2">login <span class="mono">${u.login}</span> · a person can hold both designer and coordinator</div></div><div class="r"><div class="chips">${['owner','principal','designer','coordinator'].map(r=>`<button type="button" class="chip tg sm" data-a="roletog" data-v="${u.id}|${r}" aria-pressed="${u.roles.includes(r)}" ${own?'':'disabled'}>${ic('check')}${r}</button>`).join('')}</div></div></div>`).join('')}</div>`);
 if(t==='tpl')b=card('Message templates','<span class="mu f12">one text per event and language · only this service sends</span>',`<div class="tw"><table class="tb"><thead><tr><th>Event</th><th>English</th><th>ગુજરાતી</th><th>हिंदी</th></tr></thead><tbody>${Object.keys(TPL).map(k=>`<tr><td class="mono">${k}</td><td>${esc(TPL[k].en)}</td><td class="gu">${esc(TPL[k].gu)}</td><td class="gu">${esc(TPL[k].hi)}</td></tr>`).join('')}</tbody></table></div>`);
 if(t==='etl'){const R=[['Shah Residence',64,9,55,31,6],['Mehta Office',118,14,104,52,4],['Patel Bungalow',58,21,37,24,11],['Desai Dental Clinic',22,3,19,9,2],['Vora Residence',141,26,115,66,13],['Sanghvi Hospital, OPD',203,38,165,97,17],['13 more projects',319,40,279,148,41]],T=R.reduce((a,r)=>a.map((v,i)=>v+r[i+1]),[0,0,0,0,0]);
  b=`<div class="kpis">${kpi('Entries moved',T[0])}${kpi('Open',T[1],'c-wait')}${kpi('Closed',T[2],'c-ok')}${kpi('Photos, by checksum',T[3])}${kpi('Visits',T[4])}</div>${card('Verification report','<span class="pill ok">'+ic('check')+'before = after, every project</span>',`<div class="tw"><table class="tb"><thead><tr><th>Project</th><th class="ar">Entries</th><th class="ar">Open</th><th class="ar">Closed</th><th class="ar">Photos</th><th class="ar">Visits</th><th>Check</th></tr></thead><tbody>${R.map(r=>`<tr><td><b>${r[0]}</b></td>${r.slice(1).map(v=>`<td class="ar num">${v} <span class="mu">= ${v}</span></td>`).join('')}<td>${pill('equal','ok','check')}</td></tr>`).join('')}</tbody></table></div>
   <div class="note">${ic('info')}<span>Every earlier MOM entry became a point with its text, person, photo, visit date and number, serial number, due date, state, closing note and author. A second run creates nothing. The earlier screens are switched off only after the owner compares three projects and signs off.</span></div>`)}
   ${card('People to match','<span class="mu f12">from the sheet Revert fills in</span>',`<div class="kv"><div><span>People named in earlier entries</span><b>40</b></div><div><span>Matched to an agency and trade</span><b class="c-ok">31</b></div><div><span>Kept as vendors, listed for review</span><b class="c-wait">9</b></div><div><span>Duplicate spellings merged through the sheet</span><b>4</b></div></div>`)}`}
 if(t==='log')b=card('Messages','<span class="mu f12">every send is logged</span>',`<div class="tw"><table class="tb"><thead><tr><th>When</th><th>To</th><th>Event</th><th>Message</th><th>State</th></tr></thead><tbody>${DB.wa.map(m=>`<tr><td class="mono">${m.on===0?'today':fd(m.on)} ${m.at}</td><td><b>${esc(m.name)}</b><div class="t2 mono">${esc(m.ph)}</div></td><td class="mono">${m.ev}</td><td class="gu">${esc(m.text)}${m.doc?`<div class="t2">${ic('file')}${esc(m.doc.label)}</div>`:''}</td><td>${m.held?pill('held','wait'):pill('sent','ok')}</td></tr>`).join('')}</tbody></table></div>`);
 return dhead('Setup','Master lists and rules. They are data, so they improve with every project.','')+tabsH(dev,'stab',[['settings','Settings'],['trades','Trades'],['rooms','Room types'],['presets','Site presets'],['sets','Drawing sets'],['agencies','Agencies'],['staff','Staff'],['tpl','Templates'],['log','Messages'],['etl','Earlier MOM']])+`<div class="stack">${b}</div>`}

/* ---- apps.js ---- */
/* The phone apps: staff (every desk function), agency (gu / hi / en), client (two blocks only), and what arrives on WhatsApp. */
function flashHTML(dev){const f=dev.flash;if(!f)return '';
 if(f.i==='stamp')return `<div class="flash" aria-hidden="true"><div class="stampfx">${esc(f.t)}<small>${fd(0)} · ${NOW}</small></div></div>`;
 return `<div class="flash" aria-hidden="true"><div class="okfx"><i>${ic(f.i||'check')}</i><b>${esc(f.t)}</b></div></div>`}
/* splash: construction lines cross the sheet, the mark is drawn line by line then filled in gold, a tick ruler loads, the app opens through an iris.
   'quick' is the short one shown when the app comes back to where it was closed. */
const splashInner=q=>`${skyline()}<div class="sp-in"><div class="sp-mark"><i class="ax h"></i><i class="ax v"></i><b class="gb g1">A</b><b class="gb g2">1</b><div class="sp-logo">${LOGOD}</div></div><i class="sp-dim"></i><p class="sp-tag">Architecture · Interior · Green Building</p><div class="sp-load"><span class="tkb">${Array.from({length:22},(x,i)=>`<i style="--i:${i}"></i>`).join('')}</span><small>${q?'Picking up where you left off':'Opening your sites'}</small></div></div>`;
const splashHTML=dev=>{const q=dev.splash==='quick';return dev.splash?`<div class="splash ${q?'quick':''}" aria-hidden="true">${splashInner(q)}</div>`:''};
function sheetHTML(dev){const s=dev.sheet;if(!s||!SHEETS[s.k])return flashHTML(dev);const o=SHEETS[s.k](dev,s);
 return `<div class="ovl" data-a="close"><div class="dlg ${o.wide?'wide':''}" role="dialog" aria-label="${esc(o.title)}"><header class="sh-h"><div><h3>${esc(o.title)}</h3>${o.sub?`<p>${esc(o.sub)}</p>`:''}</div><button type="button" class="xb" data-a="close" aria-label="Close">${ic('x')}</button></header><div class="sh-b" data-sc="sheet_${s.k}">${o.body}</div>${o.foot?`<footer class="sh-f">${o.foot}</footer>`:''}</div></div>${flashHTML(dev)}`}
const pushHTML=dev=>dev.push?`<div class="pushb" aria-live="polite"><i>${LOGO}</i><div><b>${esc(dev.push.t)}<small>now</small></b><span class="gu">${esc(dev.push.x)}</span></div></div>`:'';
function phone(dev,o){const fresh=dev._k!==o.key,n=dev.stack?dev.stack.length:1,dir=!fresh?'':n>(dev._n||1)?' push':n<(dev._n||1)?' pop':'';dev._k=o.key;dev._n=n;
 return `<div class="phone ${o.cls||''}"><div class="pscr scr"><div class="psb"><b>10:42</b>${o.url?`<span class="purl">${ic('lock')}${esc(o.url)}</span>`:'<i class="island"></i>'}<span class="psi">${UI.offline&&dev.id==='staff'?ic('off'):'<i class="sig"></i>'}<i class="bat"></i></span></div>
 ${o.bar||''}<div class="pbody ${o.bodyCls||''}${fresh?' enter'+dir:''}" data-sc="b_${o.key}">${o.body}</div>${o.nav||''}${pushHTML(dev)}${sheetHTML(dev)}${splashHTML(dev)}</div></div>`}
const abar=(title,sub,o)=>{o=o||{};return `<header class="pab ${o.cls||''}">${o.back?`<button type="button" class="ib" data-a="back" aria-label="Back">${ic('back')}</button>`:''}${o.left||''}<div class="m">${sub&&o.subFirst?`<p>${sub}</p>`:''}<h1 class="${o.serif?'serif':''}">${title}</h1>${sub&&!o.subFirst?`<p>${sub}</p>`:''}</div>${o.right||''}</header>`};
function bnav(dev,items,fab){const cur=dev.stack[0].s,b=n=>`<button type="button" data-a="nav" data-v="${n[0]}" ${cur===n[0]?'aria-current="page"':''}>${ic(n[2])}${n[3]?`<b>${n[3]}</b>`:''}<span>${esc(n[1])}</span></button>`,h=Math.ceil(items.length/2);
 return `<nav class="pnav">${fab?items.slice(0,h).map(b).join('')+`<button type="button" class="fab" data-a="quick" aria-label="Quick actions">${ic('plus')}</button>`+items.slice(h).map(b).join(''):items.map(b).join('')}</nav>`}
const top=dev=>dev.stack[dev.stack.length-1]||{s:''};
const demoUsers=()=>DB.staff.filter(u=>['s1','s3','s4','s5'].includes(u.id)).map(u=>`<button type="button" class="chip" data-a="asuser" data-v="${u.id}" aria-pressed="${UI.user===u.id}">${esc(u.n)} · ${roleLabel(u)}</button>`).join('');
/* the street: every site as a small elevation, inked as far as its work is done */
const authHero=tag=>`<div class="ink ahero"><div class="alogo">${LOGO}</div>${tag?'<p class="atag">Architecture · Interior · Green Building</p>':''}${skyline()}</div>`;
function street(list,share,sub,act){return `<div class="street">${list.map(p=>{const s=p.onb?STATUS[picture(p).status]:null;return `<button type="button" class="bld" data-a="${act||'proj'}" data-v="${act?'site|':''}${p.id}">${elev(p.kind,share(p))}<b>${s?`<i class="sdot ${s[1]}"></i>`:''}${esc(p.name.split(' ')[0])}</b><small>${sub(p)}</small></button>`}).join('')}</div>`}
const workShare=p=>{const n=p.lines.length;return !p.onb?null:n?p.lines.filter(l=>l.st==='done').length/n:0};

/* ---------- staff app ---------- */
function staffHTML(dev){const u=me();
 if(!dev.signed)return phone(dev,{key:'si',cls:'p-auth',body:`<div class="auth">${authHero(1)}<h2 class="serif">Welcome back</h2>${fld('Login',`<input class="inp" id="st_login" value="${u.login}" readonly>`)}${fld('Password',`<input class="inp" id="st_pw" type="password" value="••••••••" readonly>`)}${Bt('Sign in','signin',null,'gold lg blk')}<div class="lbl mt ac">Demo · sign in as</div><div class="chips cen">${demoUsers()}</div><p class="mu f12 ac">Staff use their office login. The app covers every function of the desk.</p></div>`});
 const t=top(dev),c=deskCounts(),nav=bnav(dev,[['today','Today','home',c.today],['projects','Projects','folder'],['drawings','Drawings','dwg'],['mom','MOM','mom']],true);
 let bar='',body='',key=t.s+(t.id||''),hideNav=false,bodyCls='';
 if(t.s==='today'){const it=todayFor(u),first=it[0],ps=myProjects();
  bar=abar(`Hello, ${esc(u.n)}`,fdw(0)+' · '+roleLabel(u),{cls:'hh',subFirst:1,serif:1,left:`<button type="button" class="avb" data-a="go" data-v="more" aria-label="Profile and more">${av(u.n,'lg')}</button>`,right:`<button type="button" class="ib" data-a="ui" data-v="tf=all" aria-label="Notifications">${ic('bell')}${it.length?'<i class="ndot"></i>':''}</button>`});
  body=`<section class="ink hero"><div class="tbr"><span>Today</span><span>${plural(ps.length,'site')}</span></div><div class="hnum"><b data-cu="${it.length}">${it.length}</b><span>${it.length===1?'thing':'things'} to do<br>right now</span>${first?`<button type="button" class="btn brz" data-a="startq">${ic('play')}<span>Start</span></button>`:''}</div>
    ${first?`<p class="hnext"><span class="lbl">First</span>${esc(first.text)} · ${esc(first.p.name)}</p>`:'<p class="hnext">All clear. Nothing waits for you.</p>'}${street(ps,workShare,p=>p.onb?DB.points.filter(x=>x.pid===p.id&&x.st==='open').length+' open':'configure')}</section>
   <div class="sech"><h3>To do</h3>${weekChip(u)}</div>${todoList(dev,it)}`}
 if(t.s==='projects'){bar=abar('Projects',plural(myProjects().length,'site'),{serif:1,right:Bt('New','onb','','sm gold','plus')});body=`<div class="stack">${myProjects().map(p=>siteCard(p,null,'wide')).join('')}</div>`}
 if(t.s==='project'){const p=pOf(t.id);dev.pid=p.id;hideNav=true;
  const tabs=p.onb?[['picture','Picture'],['work','Work'],['drawings','Drawings'],['mom','MOM'],['client','Client'],['bills','Bills'],['tasks','Earlier']]:[['mom','MOM'],['tasks','Earlier tasks']];if(!tabs.some(x=>x[0]===(dev.ptab||'picture')))dev.ptab=tabs[0][0];key+=dev.ptab;
  bar=abar(esc(p.name),esc(p.label)+' · '+esc(p.area),{back:1,serif:1,right:`<button type="button" class="ib" data-a="onb" data-v="${p.id}" aria-label="Project configuration">${ic('setup')}</button>`})+tabsH(dev,'ptab',tabs);
  body=(!p.onb?`<div class="note gold">${ic('layers')}<span><b>Runs the earlier way.</b> Tap the settings icon to configure rooms, trades and drawings beside what is there.</span></div>`:'')+projTab(p,dev)}
 if(t.s==='dwg'){const d=dOf(t.id);hideNav=true;bar=abar(sheetNo(d),esc(pOf(d.pid).name),{back:1});body=dwgDetail(d,dev)}
 if(t.s==='drawings'){const ps=myProjects().map(p=>p.id),all=DB.drawings.filter(d=>ps.includes(d.pid)),G={draw:all.filter(d=>d.st==='to_draw'||d.st==='in_progress'),awaiting:all.filter(d=>d.st==='awaiting'),release:all.filter(d=>d.st==='approved'),released:all.filter(d=>d.st==='released'),unopened:all.filter(d=>d.st==='released'&&cur(d).rc.some(r=>r.opened==null))};
  const k=dev.dtab&&G[dev.dtab]?dev.dtab:(isPrincipal()&&G.awaiting.length?'awaiting':'draw');dev.dtab=k;key+=k;
  bar=abar('Drawings','released only through the system',{serif:1})+tabsH(dev,'dtab',[['draw','To draw',G.draw.length],['awaiting','To approve',G.awaiting.length],['release','To release',G.release.length],['released','Released',G.released.length],['unopened','Not opened',G.unopened.length]]);
  body=`<div class="card flush"><div class="rows">${G[k].slice().sort((a,b)=>a.due-b.due).map(d=>dwgRow(d,dev,true)).join('')||empty('Nothing in this list.')}</div></div>`}
 if(t.s==='mom'){const ps=myProjects(),ids=ps.map(p=>p.id),open=DB.points.filter(x=>ids.includes(x.pid)&&x.st==='open'),ov=DB.visits.filter(v=>ids.includes(v.pid)&&v.st==='open');
  bar=abar('Site visits','write a point, send it before you leave the room',{serif:1});
  body=`<section class="ink"><div class="tbr"><span>Start a MOM</span><span>pick the site</span></div>${street(ps,workShare,p=>'visit '+(ov.find(v=>v.pid===p.id)||{no:p.visitNo+1}).no,null).replace(/data-a="proj"/g,'data-a="startmom"')}</section>
   <div class="kpis">${kpi('Open',open.length)}${kpi('Past date',open.filter(x=>x.due<0).length,'c-bad')}${kpi('Due soon',open.filter(x=>x.due===0||x.due===1).length,'c-wait')}</div>
   ${card('Open points','',`<div class="rows">${open.sort((a,b)=>a.due-b.due).map(x=>ptRow(x,dev,{proj:1})).join('')||empty('No open point.')}</div>`)}`}
 if(t.s==='visit'){const v=visOf(t.id);hideNav=true;bodyCls='momb';bar=abar('Visit '+v.no,esc(pOf(v.pid).name),{back:1,right:`<button type="button" class="ib ${UI.offline?'on':''}" data-a="offline" aria-label="Flight mode" aria-pressed="${UI.offline}">${ic('off')}</button>`});body=momCapture(v,dev)}
 if(t.s==='more'){hideNav=true;bar=abar(esc(u.full),roleLabel(u),{back:1,serif:1});const it=[['bills','Bills','bill','Ask, review, record payments'],['review','Review','review','The weekly board, one row per project'],['setup','Setup','setup','Rules, day limits, WhatsApp']];
  body=`<div class="card flush"><div class="rows">${it.map(x=>`<button type="button" class="rw lk" data-a="go" data-v="${x[0]}"><i class="mi">${ic(x[2])}</i><div class="m"><div class="t1">${x[1]}</div><div class="t2">${x[3]}</div></div><div class="r">${ic('chev','mu')}</div></button>`).join('')}
   <button type="button" class="rw lk" data-a="onb" data-v=""><i class="mi">${ic('plus')}</i><div class="m"><div class="t1">New project</div><div class="t2">Onboard in six steps, from the phone</div></div><div class="r">${ic('chev','mu')}</div></button>
   <button type="button" class="rw lk" data-a="offline"><i class="mi">${ic('off')}</i><div class="m"><div class="t1">Flight mode (preview)</div><div class="t2">${UI.offline?'Offline: points are saved on the phone':'Online. Switch off the network to try the outbox'}</div></div><div class="r"><i class="switch ${UI.offline?'on':''}"></i></div></button>
   <button type="button" class="rw lk" data-a="signout"><i class="mi">${ic('out')}</i><div class="m"><div class="t1">Sign out</div></div></button></div></div>`}
 if(t.s==='bills'){hideNav=true;const ids=myProjects().map(p=>p.id),all=DB.bills.filter(b=>ids.includes(b.pid)),G={review:all.filter(b=>b.st==='submitted'),asked:all.filter(b=>b.st==='asked'||b.st==='returned'),unpaid:all.filter(b=>b.st==='accepted'||b.st==='part_paid'),paid:all.filter(b=>b.st==='paid')},k=dev.btab&&G[dev.btab]?dev.btab:'review';key+=k;
  bar=abar('Bills','ask · review · record',{back:1,serif:1,right:Bt('Ask','askbill','','sm gold','plus')})+tabsH(dev,'btab',[['review','To review',G.review.length],['asked','Asked',G.asked.length],['unpaid','Unpaid',G.unpaid.length],['paid','Paid',G.paid.length]]);
  body=`<div class="card flush"><div class="rows">${G[k].map(b=>billRow(b,dev,true)).join('')||empty('Nothing in this list.')}</div></div>${isOwner()?card('Money, all projects',pill('owner only','gold','lock'),moneyView(all)):`<div class="note">${ic('lock')}Amounts and totals are visible to the owner only.</div>`}`}
 if(t.s==='review'){hideNav=true;bar=abar('Review','the weekly board',{back:1,serif:1});body=`<div class="stack">${myProjects().map(p=>siteCard(p,null,'wide')).join('')}</div>`}
 if(t.s==='setup'){hideNav=true;const s=DB.set,sw=(k,on,l,h)=>`<button type="button" class="sw-row" data-a="setting" data-v="${k}" aria-pressed="${on}"><i class="switch"></i><div><b>${l}</b><small>${h}</small></div></button>`;
  bar=abar('Setup','rules and messages',{back:1,serif:1});body=card('Rules','',sw('approval',s.approval,'Release needs the principal’s approval','Off: the designer releases directly.')+sw('clientConfirm',s.clientConfirm,'Client points need the office to confirm','Off: the client sees a point at once.')+sw('sending',s.sending,'WhatsApp sending is on','Off: messages are logged as “held”.'))+`<div class="note">${ic('info')}Master lists (trades, room types, drawing sets, agencies, staff) are edited on the desk.</div>`}
 if(t.s==='onboard'){hideNav=true;body=obWizard(dev);bodyCls='obp';key+=dev.ob?dev.ob.step:''}
 return phone(dev,{key,bar,body,bodyCls,nav:hideNav?'':nav})}
function weekChip(u){const mine=DB.drawings.filter(d=>d.st==='released'&&cur(d).relOn>-7&&(has(u,'designer')?d.ds===u.id:canSee(u,pOf(d.pid)))),rc=mine.flatMap(d=>cur(d).rc),un=rc.filter(x=>x.opened==null).length;
 return `<span class="wk">${ic('refresh')}this week <b>${mine.length}</b> released · <b class="${un?'c-bad':'c-ok'}">${un}</b> not opened</span>`}

/* ---------- agency app: big type, solid cards, no blur (cheap phones, sunlight) ---------- */
function signinFlow(dev,L,who,name){const si=dev.si||(dev.si={step:'lang'});
 if(si.step==='lang')return `<div class="auth">${authHero(1)}<h2 class="serif">ભાષા · भाषा · Language</h2><div class="langs">${[['gu','ગુજરાતી'],['hi','हिंदी'],['en','English']].filter(x=>who==='agency'||x[0]!=='hi').map(x=>`<button type="button" class="btn lg blk ${L===x[0]?'gold':''}" data-a="silang" data-v="${x[0]}"><span>${x[1]}</span></button>`).join('')}</div></div>`;
 if(si.step==='phone')return `<div class="auth">${authHero()}<h2 class="serif">${tr('signin',L)}</h2>${fld(tr('mobile',L),`<div class="phin"><span>+91</span>${fin(dev,'si_ph','98xxx xxxxx',1)}</div>`)}${Bt(tr('getcode',L),'sicode',null,'wa lg blk','wa')}<p class="mu f12 ac">${esc(name)}</p></div>`;
 return `<div class="auth">${authHero()}<h2 class="serif">${tr('code',L)}</h2><div class="otp">${fin(dev,'si_otp','• • • •',1)}</div>${Bt(tr('signin',L),'siverify',null,'gold lg blk','check')}<div class="note ok">${ic('wa')}<span>The code arrived on WhatsApp just now. See the WhatsApp phone beside this one, or ${Bt('fill it in','sifill',null,'sm ghost')}</span></div></div>`}
const calTile=(o,L)=>`<span class="cal ${o<0?'bad':o<=1?'soon':''}"><i>${MON[dt(o).getUTCMonth()]}</i><b>${dt(o).getUTCDate()}</b></span>`;
function agencyHTML(dev){const a=agOf(UI.agency),L=UI.lang.agency,T=k=>tr(k,L),gu=L!=='en'?'gu':'';
 if(!dev.signed)return phone(dev,{key:'si',cls:'p-auth '+gu,body:signinFlow(dev,L,'agency',a.people[0].n+' · '+a.n)});
 const ps=agProjects(a.id),pts=DB.points.filter(x=>x.kind==='agency'&&x.party===a.id&&x.st==='open'&&!x.pending).sort((x,y)=>x.due-y.due);
 const dws=DB.drawings.filter(d=>d.st==='released'&&cur(d).rc.some(r=>r.to===a.id)),nw=dws.filter(d=>cur(d).rc.find(r=>r.to===a.id).opened==null),bills=DB.bills.filter(b=>b.ag===a.id),asks=bills.filter(b=>b.st==='asked'||b.st==='returned');
 const t=top(dev),nav=bnav(dev,[['home',T('home'),'home',pts.length+nw.length+asks.length||''],['sites',T('sites'),'folder'],['drawings',T('drawings'),'dwg',nw.length||''],['bills',T('bills'),'bill',asks.length||'']]);
 const myShare=p=>{const ls=p.lines.filter(l=>lineAg(p,l)===a.id);return ls.length?ls.filter(l=>l.st==='done').length/ls.length:0};
 const prow=x=>`<div class="rw">${calTile(x.due,L)}<div class="m"><div class="t1"><span class="tx">${esc(x.text)}</span></div><div class="t2">${esc(pOf(x.pid).name)}${x.e?' · '+esc(entN(pOf(x.pid),x.e)):''}</div></div>${x.photo?phOf('point',x):''}</div>`;
 const dcard=d=>{const r=cur(d),un=r.rc.find(x=>x.to===a.id).opened==null;return `<button type="button" class="dcard" data-a="adwg" data-v="${d.id}">${sht(d,'lg')}<div class="t1"><span class="tx">${esc(d.title)}</span>${un?pill(T('new'),'gold'):''}</div><div class="t2">${T('rev')} ${r.n} · ${esc(pOf(d.pid).name)}</div></button>`};
 const brow=b=>`<button type="button" class="rw lk" data-a="go" data-v="bill|${b.id}"><span class="mi">${ic('bill')}</span><div class="m"><div class="t1">${esc(b.what)}</div><div class="t2">${esc(pOf(b.pid).name)}${b.amount!=null?' · <b class="num">'+inr(b.amount)+'</b>':''}</div>${b.st==='returned'?`<div class="t2 c-bad">${T('reason')}: ${esc(b.reason)}</div>`:''}</div><div class="r">${pill(T(b.st),BS[b.st][1])}</div></button>`;
 let bar='',body='',key=t.s+(t.id||''),hide=false;
 if(t.s==='home'){bar=abar(`${T('hello')}, ${esc(a.people[0].n.split(' ')[0])}`,esc(a.n),{cls:'hh',subFirst:1,serif:1,left:av(a.n,'lg'),right:`<button type="button" class="ib" data-a="go" data-v="profile" aria-label="${T('lang')}">${ic('globe')}</button>`});
  body=`<section class="ink hero"><div class="tbr"><span>${fdw(0)}</span><span>${plural(ps.length,'site')}</span></div><div class="h3n"><button type="button" data-a="nav" data-v="home"><b data-cu="${pts.length}">${pts.length}</b><span>${T('points')}</span></button><button type="button" data-a="nav" data-v="drawings"><b data-cu="${nw.length}">${nw.length}</b><span>${T('newdw')}</span></button><button type="button" data-a="nav" data-v="bills"><b data-cu="${asks.length}">${asks.length}</b><span>${T('asks')}</span></button></div>
    ${street(ps,myShare,p=>{const ls=p.lines.filter(l=>lineAg(p,l)===a.id);return ls.filter(l=>l.st==='done').length+'/'+ls.length},'go')}</section>
   ${asks.map(b=>`<button type="button" class="askc" data-a="go" data-v="bill|${b.id}"><span class="mi">${ic('bill')}</span><div><h3>${b.st==='returned'?T('again'):T('upload')}</h3><p>${esc(pOf(b.pid).name)} · ${esc(b.what)}</p></div>${ic('chev')}</button>`).join('')}
   <div class="sech"><h3>${T('points')}</h3><span class="cnt">${pts.length}</span></div><div class="card flush solid"><div class="rows">${pts.map(prow).join('')||empty(T('allclear'))}</div></div>
   <div class="sech"><h3>${T('newdw')}</h3><span class="cnt">${nw.length}</span></div>${nw.length?`<div class="hscroll">${nw.map(dcard).join('')}</div>`:`<div class="card solid">${empty(T('allclear'))}</div>`}`}
 if(t.s==='sites'){bar=abar(T('sites'),plural(ps.length,'site'),{serif:1});body=`<div class="stack">${ps.map(p=>{const ls=p.lines.filter(l=>lineAg(p,l)===a.id),c=s=>ls.filter(l=>l.st===s).length;return `<button type="button" class="site wide solid" data-a="go" data-v="site|${p.id}"><div class="site-art">${elev(p.kind,myShare(p))}</div><div class="m"><h3>${esc(p.name)}</h3><p class="t2">${ic('pin')}${esc(p.area)} · ${esc(p.plan.filter(x=>x.ag===a.id).map(x=>TX[x.t][L]||TX[x.t].n).join(', '))}</p>${ticks(c('done'),ls.length,'ok',c('work'))}
   <div class="site-m"><span class="c-ok"><b>${c('done')}</b> ${T('done')}</span><span class="c-work"><b>${c('work')}</b> ${T('work')}</span><span class="c-wait"><b>${c('wait')}</b> ${T('wait')}</span><span><b>${c('ns')}</b> ${T('ns')}</span></div></div></button>`}).join('')}</div>`}
 if(t.s==='site'){const p=pOf(t.id),ls=p.lines.filter(l=>lineAg(p,l)===a.id);hide=true;bar=abar(esc(p.name),esc(p.address),{back:1,serif:1});
  body=`<div class="card solid"><header class="hd"><h3>${T('rooms')}</h3></header>${planView(p,dev,{ro:1,ag:a.id})}<div class="rows">${ls.map(l=>`<div class="rw"><div class="m"><div class="t1">${esc(entN(p,l.e))}</div><div class="t2">${esc(TX[l.t][L]||TX[l.t].n)}${l.st==='wait'&&l.cause==='drawing'&&dOf(l.ref)?' · '+T('waiting4')+': '+esc(dOf(l.ref).title):''}</div></div><div class="r">${pill(T(l.st),LS[l.st][1])}</div></div>`).join('')}</div></div>
   <div class="sech"><h3>${T('points')}</h3></div><div class="card flush solid"><div class="rows">${pts.filter(x=>x.pid===p.id).map(prow).join('')||empty(T('allclear'))}</div></div>
   <div class="sech"><h3>${T('drawings')}</h3></div>${dws.some(d=>d.pid===p.id)?`<div class="dgal">${dws.filter(d=>d.pid===p.id).map(dcard).join('')}</div>`:`<div class="card solid">${empty(T('allclear'),'dwg')}</div>`}`}
 if(t.s==='drawings'){bar=abar(T('drawings'),T('current'),{serif:1});body=dws.length?`<div class="dgal">${dws.map(dcard).join('')}</div>`:`<div class="card solid">${empty(T('allclear'),'dwg')}</div>`}
 if(t.s==='dwg'){const d=dOf(t.id),r=cur(d),qs=d.q.filter(q=>q.by===a.id);hide=true;bar=abar(esc(d.title),sheetNo(d)+' · '+T('rev')+' '+r.n+' · '+esc(pOf(d.pid).name),{back:1});
  body=`<div class="viewer">${dwgPaper(d)}</div><div class="note ok">${ic('check')}${T('current')} · ${fd(r.relOn)}</div>${qs.map(q=>`<div class="q"><div class="qb out"><div class="lbl">${T('yourq')} · ${fd(q.on)}</div>${esc(q.text)}${q.photo?phOf('question',q):''}</div>${q.ans?`<div class="qb in"><div class="lbl">Revert · ${esc(stf(q.ansBy).n)}</div>${esc(q.ans)}</div>`:''}</div>`).join('')}
   <div class="composer"><div class="lbl">${T('ask')}</div><div class="ctext">${fin(dev,'aq',T('noq'))}<button type="button" class="ib ${dev.f.aq_photo?'on':''}" data-a="tog" data-v="aq_photo" aria-label="Photo">${ic('cam')}</button></div>${Bt(T('send'),'aask',d.id,'gold blk','send')}</div>`}
 if(t.s==='bills'){bar=abar(T('bills'),'',{serif:1});body=`<div class="card flush solid"><div class="rows">${bills.map(brow).join('')||empty(T('nobills'),'bill')}</div></div>`}
 if(t.s==='bill'){const b=billOf(t.id),up=b.st==='asked'||b.st==='returned';hide=true;bar=abar(esc(b.what),esc(pOf(b.pid).name),{back:1,right:pill(T(b.st),BS[b.st][1])});
  body=up?(b.st==='returned'?`<div class="note bad">${ic('alert')}${T('reason')}: ${esc(b.reason)}</div>`:'')+`<div class="card solid">${fld(T('billno'),fin(dev,'ab_no','—'))}${fld(T('amount'),fin(dev,'ab_amt','₹',1))}<button type="button" class="drop ${dev.f.ab_doc?'on':''}" data-a="tog" data-v="ab_doc">${ic(dev.f.ab_doc?'file':'cam')}<span>${T('photo')}${dev.f.ab_doc?' ✓':''}</span></button>${Bt(T('submit'),'asubmit',b.id,'gold lg blk','check')}</div>`
   :`<div class="card solid"><div class="kv"><div><span>${T('billno')}</span><b>${esc(b.no||'—')}</b></div><div><span>${T('amount')}</span><b class="num">${inr(b.amount)}</b></div></div><div class="bsteps">${['submitted','accepted','part_paid','paid'].map(s=>{const order=['submitted','accepted','part_paid','paid'],on=order.indexOf(b.st)>=order.indexOf(s);return `<div class="${on?'on':''}"><i>${on?ic('check'):''}</i><span>${T(s)}</span></div>`}).join('')}</div></div>`}
 if(t.s==='profile'){hide=true;bar=abar(esc(a.n),esc(a.people.map(p=>p.n).join(', ')),{back:1,serif:1});body=card(T('lang'),'',`<div class="langs">${[['gu','ગુજરાતી'],['hi','हिंदी'],['en','English']].map(x=>`<button type="button" class="btn lg blk ${L===x[0]?'gold':''}" data-a="alang" data-v="${x[0]}"><span>${x[1]}</span></button>`).join('')}</div>`,'solid')+Bt(T('signout'),'signout',null,'blk','out')}
 return phone(dev,{key,bar,body,cls:'ag '+gu,nav:hide?'':nav})}

/* ---------- client app: two blocks and nothing else ---------- */
function clientHTML(dev){const p=pOf(UI.clientPid),L=UI.lang.client,T=k=>tr(k,L),c=p.client.contacts[0],gu=L!=='en'?'gu':'',url=UI.linkMode?'revert.co.in/c/'+p.name.toLowerCase().replace(/\W+/g,'-')+'-7f3k':'';
 if(!dev.signed&&!UI.linkMode)return phone(dev,{key:'si',cls:'p-auth '+gu,body:signinFlow(dev,L,'client',c.n)});
 const dws=DB.drawings.filter(d=>d.pid===p.id&&d.st==='released'&&cur(d).rc.some(r=>r.to==='client')),pend=dws.filter(d=>cur(d).client&&cur(d).client.dec==='pending'),pts=DB.points.filter(x=>x.pid===p.id&&x.kind==='client'&&x.st==='open'&&x.confirmed),t=top(dev);
 let bar='',body='',key=t.s+(t.id||'');
 if(t.s==='home'){const n=pend.length+pts.length;
  body=`<section class="ink hero chero"><div class="chl">${LOGO}<button type="button" class="ib oni" data-a="clang" aria-label="${T('lang')}">${ic('globe')}<span>${L==='en'?'ગુ':'EN'}</span></button></div>
    <p class="lbl">${T('c_hi')}, ${esc(c.n.split(' ')[0])}</p><h1 class="serif">${esc(p.name)}</h1><p class="hnext">${T('c_sub')}</p>${elev(p.kind,1,{cls:'cart'})}</section>
   <div class="sech"><h3>${T('c_wait')}</h3><span class="cnt ${n?'gold':''}">${n}</span></div>
   ${pend.map(d=>`<button type="button" class="card cta" data-a="cdwg" data-v="${d.id}">${sht(d,'lg wide')}<div class="rw"><div class="m"><div class="t1">${T('c_approve')}: ${esc(d.title)}</div><div class="t2">${T('rev')} ${cur(d).n} · ${T('c_look')}</div></div><span class="btn sm gold">${ic('eye')}<span>${T('open')}</span></span></div></button>`).join('')}
   ${pts.length?`<div class="card flush"><div class="rows">${pts.map(x=>`<div class="rw"><span class="mi">${ic('hand')}</span><div class="m"><div class="t1">${esc(x.text)}</div><div class="t2">${T('by')} ${fdw(Math.max(x.due,0))}</div></div><div class="r">${Bt(T('c_done'),'cdone',x.id,'sm')}</div></div>`).join('')}</div></div>`:''}
   ${n?'':`<div class="card"><div class="empty calm">${ic('check')}<span>${T('c_none')}</span></div></div>`}
   <div class="sech"><h3>${T('c_dw')}</h3></div>${dws.length?`<div class="dgal">${dws.map(d=>{const r=cur(d),un=r.rc.find(x=>x.to==='client').opened==null;return `<button type="button" class="dcard" data-a="cdwg" data-v="${d.id}">${sht(d,'lg')}<div class="t1"><span class="tx">${esc(d.title)}</span>${un?pill(T('new'),'gold'):''}</div><div class="t2">${T('rev')} ${r.n} · ${fd(r.relOn)}${r.client&&r.client.dec==='approved'?' · <span class="c-ok">'+T('c_approved')+'</span>':''}</div></button>`}).join('')}</div>`:`<div class="card"><div class="empty calm">${ic('dwg')}<span>—</span></div></div>`}`}
 if(t.s==='dwg'){const d=dOf(t.id),r=cur(d),pd=r.client&&r.client.dec==='pending';bar=abar(esc(d.title),T('rev')+' '+r.n+' · '+fd(r.relOn),{back:1,serif:1});
  body=`<div class="viewer">${dwgPaper(d)}</div>${r.client&&r.client.dec==='approved'?`<div class="note ok">${ic('check')}<span>${T('c_approved')} · ${esc(r.client.by)} · ${fdw(r.client.on)}, ${r.client.at}</span></div>`:''}
   ${pd?`<div class="card">${Bt(T('c_approve'),'capprove',d.id,'gold lg blk','check')}<div class="or">or</div>${fld(T('c_note'),fin(dev,'c_note',''))}${Bt(T('c_change'),'cchange',d.id,'blk','edit')}<p class="mu f12 ac mt">${esc(c.n)} · ${fdw(0)} · your tap is the record, no signature needed.</p></div>`:''}`}
 return phone(dev,{key,bar,body,cls:'cl '+gu,url})}

/* ---------- what arrives on WhatsApp ---------- */
function waHTML(dev){const only=UI.view==='agency'?UI.agency:UI.view==='client'?'client:'+UI.clientPid:null,msgs=DB.wa.filter(m=>!only||m.to===only),tos=[...new Set(DB.wa.map(m=>m.to))];
 const chat=only||dev.chat,list=(chat?msgs.filter(m=>m.to===chat):msgs).slice().reverse(),nm=chat&&(DB.wa.find(m=>m.to===chat)||{}).name;
 return phone(dev,{key:'wa'+(chat||''),cls:'wa',bar:`<header class="pab wah"><i class="waav">${LOGO}</i><div class="m"><h1>Revert Architects</h1><p>${chat&&nm?'to '+esc(nm)+' · ':''}business account · ${DB.set.number}</p></div></header>
  ${only?'':`<div class="wachips"><button type="button" class="chip" data-a="wachat" data-v="" aria-pressed="${!chat}">All</button>${tos.map(k=>`<button type="button" class="chip" data-a="wachat" data-v="${k}" aria-pressed="${chat===k}">${esc(DB.wa.find(m=>m.to===k).name.split(' ')[0])}</button>`).join('')}</div>`}`,
  body:list.length?list.map(m=>{const i=DB.wa.indexOf(m);return `<div class="wam ${m.held?'held':''} ${m.fresh?'fresh':''}">${!chat?`<div class="wato">${esc(m.name)} · ${esc(m.ph)}</div>`:''}<div class="gu">${esc(m.text)}</div>${m.doc?`<button type="button" class="wadoc" data-a="wadoc" data-v="${i}">${ic(m.doc.k==='dwg'?'link':'file')}<span>${esc(m.doc.label)}</span>${ic('chev')}</button>`:''}<div class="wat">${m.on===0?'':fd(m.on)+' · '}${m.at}${m.held?' · held, sending is off':' ✓✓'}</div></div>`}).join(''):empty('No message yet.','wa')})}

/* ---- shell.js ---- */
/* Shell: preview bar, stage, guide, the actions behind every button, rendering. */
const devOf=el=>{const d=el.closest('[data-dev]');return d?UI.devs[d.dataset.dev]:UI.devs.desk};
function toast(t,k){UI.toast={t,k:k||'ok'};clearTimeout(toast.h);toast.h=setTimeout(()=>{UI.toast=null;const el=document.getElementById('toast');if(el)el.innerHTML=''},4200)}
/* the splash plays over the first screen; that screen's own entrance waits for it (--sd in the stylesheet) */
function splash(dev,quick){dev.splash=quick?'quick':true;dev.spT=performance.now();dev._k='';clearTimeout(dev.sh);dev.sh=setTimeout(()=>{dev.splash=false;document.querySelectorAll('.dv-'+dev.id+' .splash').forEach(e=>e.remove())},quick?2900:5300)}
function flash(dev,t,i,party){dev.flash={t,i};if(i==='stamp'||party)dev.party=true;clearTimeout(dev.fh);dev.fh=setTimeout(()=>{dev.flash=null;document.querySelectorAll('.flash').forEach(e=>e.remove())},1600)}
const openSheet=(dev,k,o)=>{dev.sheet=Object.assign({k},o||{})};
const sent=()=>DB.set.sending?'sent on WhatsApp':'held: sending is off in Setup';
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
 go(v,el,dev){const [s,id]=v.split('|');dev.stack.push({s,id:id&&/^\d+$/.test(id)?+id:id});if(s==='bill'&&dev.id==='agency'){const b=billOf(id);dev.f.ab_no='';dev.f.ab_amt='';dev.f.ab_doc=false}},
 ui(v,el,dev){const i=v.indexOf('='),k=v.slice(0,i),val=v.slice(i+1);if(k==='vid'&&dev.phone&&val){dev.stack.push({s:'visit',id:val});return}dev[k]=val},
 set(v,el,dev){const i=v.indexOf('='),k=v.slice(0,i);dev.f[k]=v.slice(i+1);if(k==='c_cause'){dev.f.c_ref='';dev.f.c_note=''}},tog(v,el,dev){dev.f[v]=!dev.f[v]},close(v,el,dev){dev.sheet=null},
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
 assign(v,el,dev){const [pid,t]=v.split('|'),pl=planOf(pOf(pid),t);dev.f.a_ag=pl.ag||'';dev.f.a_by=7;openSheet(dev,'assign',{pid:+pid,t})},
 saveassign(v,el,dev){const [pid,t]=v.split('|'),p=pOf(pid);OP.assign(p,t,dev.f.a_ag,+dev.f.a_by);dev.sheet=null;toast(dev.f.a_ag?`${TX[t].n}: ${agN(dev.f.a_ag)}. Its ${plural(p.lines.filter(l=>l.t===t).length,'work line')} now carry this agency.`:`${TX[t].n} stays undecided until ${fd(+dev.f.a_by)}.`)},
 /* drawings */
 dwg(v,el,dev){openDwg(dev,v)},dstart(v){dOf(v).st='in_progress';toast('Marked in progress.')},view(v,el,dev){openSheet(dev,'view',{id:v})},
 dosend(v,el,dev){const d=dOf(v);if(!dev.f.sa_file)return toast('Choose the PDF first.','wait');OP.sendForApproval(d,dev.f.sa_note);dev.f.sa_file=false;dev.f.sa_note='';
  if(DB.set.approval){dev.sheet=null;flash(dev,'Sent','send');toast(`${sheetNo(d)} sent to ${stf(pOf(d.pid).principal).n} for approval.`)}else relPrefill(dev,d)},
 approve(v,el,dev){if(!isPrincipal())return toast('Only the principal approves a release.','wait');dev.f.ap_note='';openSheet(dev,'approve',{id:v})},
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
  Object.assign(dev.f,{m_for:'',m_area:'',m_text:'',m_photo:false,m_due:2,m_vendor:''});if(dev.phone)dev.stack.push({s:'visit',id:vi.id});else{openProj(dev,p.id,'mom');dev.vid=vi.id}},
 openvisit(v,el,dev){const vi=visOf(v);if(dev.phone)dev.stack.push({s:'visit',id:v});else{openProj(dev,vi.pid,'mom');dev.vid=v}},
 addpt(v,el,dev){const vi=visOf(v),f=dev.f,t=(f.m_text||'').trim();if(!t)return toast('Type or speak the point first.','wait');
  const kind=agOf(f.m_for)?'agency':f.m_for==='client'?'client':f.m_for==='vendor'?'vendor':'staff',x=OP.addPoint({pid:vi.pid,vid:vi.id,kind,party:kind==='vendor'?f.m_vendor:f.m_for,text:t,e:f.m_area||null,due:+f.m_due,photo:!!f.m_photo});
  if(UI.offline&&dev.id==='staff')x.pending=true;f.m_text='';f.m_photo=false;UI.focus=dev.id+'_m_text'},
 sendparty(v,el,dev){const [vid,key]=v.split('|');if(UI.offline&&dev.id==='staff'){if(!UI.outbox.some(o=>o.vid===vid&&o.key===key))UI.outbox.push({vid,key});return toast(`Saved. ${agN(key)}’s PDF goes out when the network returns.`,'wait')}
  const n=OP.sendParty(visOf(vid),key);if(n){flash(dev,'Sent','wa');toast(`${agN(key)}: ${plural(n,'point')} as a PDF · ${sent()}.`)}},
 sendall(v,el,dev){const vi=visOf(v),ks=[...new Set(DB.points.filter(x=>x.vid===v&&x.st==='open'&&x.kind==='agency').map(x=>x.party))];if(UI.offline&&dev.id==='staff'){ks.forEach(k=>{if(!UI.outbox.some(o=>o.vid===v&&o.key===k))UI.outbox.push({vid:v,key:k})});return toast('Saved. Every party’s PDF goes out when the network returns.','wait')}
  ks.forEach(k=>OP.sendParty(vi,k));flash(dev,'Sent','wa');toast(`${plural(ks.length,'party','parties')} got their own PDF · ${sent()}. Client points wait for the office.`)},
 finishvisit(v,el,dev){const vi=visOf(v);vi.st='finished';if(dev.phone)dev.stack.pop();else dev.vid='';flash(dev,'Filed');toast(`Visit ${vi.no} filed. The full MOM is with the office.`)},
 pdf(v,el,dev){const [kind,a,b]=v.split('|');openSheet(dev,'pdf',{kind,a,b})},
 dovendor(v,el,dev){const n=(dev.f.vn||'').trim();if(!n)return toast('Type the vendor’s name.','wait');dev.f.m_vendor=n;dev.f.m_for='vendor';dev.f.vn='';dev.sheet=null},
 raise(v,el,dev){const p=pOf(v);Object.assign(dev.f,{rp_for:forOptions(p)[0][0],rp_text:'',rp_area:'',rp_due:2,rp_photo:false});openSheet(dev,'point',{pid:+v})},
 raiseclient(v,el,dev){Object.assign(dev.f,{rp_for:'client',rp_text:'',rp_area:'',rp_due:3,rp_photo:false});openSheet(dev,'point',{pid:+v})},
 doraise(v,el,dev){const f=dev.f,t=(f.rp_text||'').trim();if(!t)return toast('Say what is needed.','wait');const kind=agOf(f.rp_for)?'agency':f.rp_for==='client'?'client':'staff',x=OP.addPoint({pid:+v,kind,party:f.rp_for,text:t,e:f.rp_area||null,due:+f.rp_due,photo:!!f.rp_photo});
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
 roletog(v){const [s,r]=v.split('|'),u=stf(s),i=u.roles.indexOf(r);i<0?u.roles.push(r):u.roles.length>1&&u.roles.splice(i,1)},
 doaddtrade(v,el,dev){const f=dev.f,n=(f.nt_n||'').trim();if(!n)return toast('Type the trade’s name.','wait');const t={id:'t'+TRADES.length,n,s:n.slice(0,5),gu:f.nt_gu||n,hi:f.nt_hi||n};TRADES.push(t);TX[t.id]=t;f.nt_n=f.nt_gu=f.nt_hi='';dev.sheet=null;toast(`Trade “${n}” added. It is offered at the next onboarding.`)},
 doaddagency(v,el,dev){const f=dev.f;if(!(f.na_n||'').trim()||!f.na_t)return toast('Give the firm’s name and its trade.','wait');DB.agencies.push({id:'a'+(DB.agencies.length+1),n:f.na_n.trim(),tr:[f.na_t],lang:f.na_l||'gu',people:[{n:f.na_p||'Owner',ph:f.na_ph||'—'}]});f.na_n=f.na_p=f.na_ph='';dev.sheet=null;toast('Agency added.')},
 /* agency and client apps */
 silang(v,el,dev){UI.lang[dev.id]=v;dev.si.step='phone';dev.f.si_ph=dev.id==='agency'?agOf(UI.agency).people[0].ph:pOf(UI.clientPid).client.contacts[0].ph},
 sicode(v,el,dev){dev.si.code=String(1000+Math.floor(Math.random()*9000));dev.si.step='otp';dev.f.si_otp='';notify('otp',dev.id==='agency'?UI.agency:'client:'+UI.clientPid,{code:dev.si.code});toast('Sign-in code '+sent()+'.')},
 sifill(v,el,dev){dev.f.si_otp=dev.si.code},
 siverify(v,el,dev){if(String(dev.f.si_otp).trim()!==dev.si.code)return toast('That code does not match. Look at the WhatsApp message.','wait');dev.signed=true;dev.si=null;dev.stack=[{s:'home'}];dev._k='';flash(dev,tr(dev.id==='agency'?'hello':'c_hi',UI.lang[dev.id]))},
 alang(v){UI.lang.agency=v},clang(){UI.lang.client=UI.lang.client==='en'?'gu':'en'},
 adwg(v,el,dev){const d=dOf(v);if(OP.open(d,UI.agency))toast(`${agN(UI.agency)} opened ${sheetNo(d)}. The desk shows “opened” now.`);dev.f.aq='';dev.f.aq_photo=false;dev.stack.push({s:'dwg',id:v})},
 aask(v,el,dev){const d=dOf(v),t=(dev.f.aq||'').trim(),a=agOf(UI.agency);if(!t)return toast(tr('noq',UI.lang.agency),'wait');OP.ask(d,a.id,a.people[0].n,t,dev.f.aq_photo);dev.f.aq='';dev.f.aq_photo=false;flash(dev,tr('send',UI.lang.agency),'send');pushStaff(a.n+' asks on '+sheetNo(d)+': '+t,[d.ds,...pOf(d.pid).coords]);toast(`Question sent. It sits on ${stf(d.ds).n}’s list until answered.`)},
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
const SKEY='rvt_r1_preview_s3',TRANSIENT=['flash','splash','push','party','sh','fh','pt','spT','_k','_n','seen'];
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
function render(){({staff:['staff'],agency:['agency'],client:['client'],all:['staff','agency','client']}[UI.view]||[]).forEach(k=>{const d=UI.devs[k];if(!d.seen){d.seen=true;splash(d,UI.restored&&(d.signed||(k==='client'&&UI.linkMode)))}});
 const root=document.getElementById('app'),sc={},key=el=>{const d=el.closest('[data-dev]');return (d?d.dataset.dev:'')+':'+el.dataset.sc};
 root.querySelectorAll('[data-sc]').forEach(el=>{sc[key(el)]=[el.scrollTop,el.scrollLeft]});const ae=document.activeElement,fid=ae&&ae.id,ss=ae&&ae.selectionStart;
 root.style.setProperty('--t',((performance.now()-T0)/1000).toFixed(2));
 root.innerHTML=shellHTML();
 root.querySelectorAll('[data-sc]').forEach(el=>{const s=sc[key(el)]||(BOOT&&SCROLL[key(el)]);if(s){el.scrollTop=s[0];el.scrollLeft=s[1]}});afterRender(root);
 const want=UI.focus||fid;UI.focus=null;if(want){const el=document.getElementById(want);if(el&&el.tagName!=='SELECT'){el.focus({preventScroll:true});try{el.setSelectionRange(ss==null?99:ss,ss==null?99:ss)}catch(e){}}}}
function boot(){const root=document.getElementById('app'),html=document.documentElement,back=restore();
 html.dataset.rv=UI.theme==='dark'?'dark':'light';html.dataset.pal=UI.pal||'emerald';html.dataset.motion=UI.motion||'';
 if(!document.getElementById('fx')){const f=document.createElement('div');f.id='fx';f.setAttribute('aria-hidden','true');document.body.appendChild(f)}
 const run=(el,fn)=>{fn(el.dataset.v==null?'':el.dataset.v,el,devOf(el));render()};
 root.addEventListener('click',e=>{const el=e.target.closest('[data-a]');if(!el||el.disabled)return;if(el.classList.contains('ovl')&&e.target!==el)return;const fn=A[el.dataset.a];if(!fn)return;
  if(e.clientX||e.clientY)TAP={x:e.clientX,y:e.clientY};
  if(el.dataset.a==='close'&&!RM()){const ov=el.closest('.ovl');if(ov){if(ov.classList.contains('out'))return;ov.classList.add('out');TAP=null;return setTimeout(()=>run(el,fn),170)}}
  run(el,fn)});
 root.addEventListener('input',e=>{const el=e.target,dev=devOf(el);if(el.dataset.m)dev.f[el.dataset.m]=el.value;if(el.dataset.mo&&dev.ob)setPath(dev.ob,el.dataset.mo,el.value);queueSave()});
 root.addEventListener('change',e=>{const el=e.target,dev=devOf(el);if(el.dataset.top){UI[el.dataset.top]=/^\d+$/.test(el.value)?+el.value:el.value;if(el.dataset.top!=='user'){UI.devs.agency.stack=[{s:'home'}];UI.devs.client.stack=[{s:'home'}]}if(el.dataset.top==='agency')UI.lang.agency=agOf(el.value).lang;return render()}
  if(el.dataset.ui){dev[el.dataset.ui]=el.value;return render()}if(el.dataset.r)render()});
 root.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.tagName==='INPUT'){const id=e.target.id||'';const b=id.endsWith('_m_text')?'addpt':id.endsWith('_aq')?'aask':null;if(b){const btn=e.target.closest('.composer').querySelector(`[data-a="${b}"]`);if(btn){e.preventDefault();btn.click()}}}
  if((e.key==='Enter'||e.key===' ')&&e.target.matches&&e.target.matches('g[data-a]')){e.preventDefault();e.target.dispatchEvent(new MouseEvent('click',{bubbles:true}))}});
 /* a phone's bar turns to glass once its page is scrolled; on the desk a soft light follows the pointer across a card */
 root.addEventListener('scroll',e=>{const t=e.target;if(t.classList&&t.classList.contains('pbody')){const s=t.closest('.pscr');if(s)s.classList.toggle('scrolled',t.scrollTop>6)}queueSave()},true);
 root.addEventListener('pointermove',e=>{const k=e.target.closest&&e.target.closest('.ink,.card,.todo,.site,.kpi');if(!k||e.pointerType==='touch')return;const r=k.getBoundingClientRect();k.style.setProperty('--mx',Math.round(e.clientX-r.left)+'px');k.style.setProperty('--my',Math.round(e.clientY-r.top)+'px')});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){let ch=false;Object.values(UI.devs).forEach(d=>{if(d.sheet){d.sheet=null;ch=true}});if(UI.panel){UI.panel=null;ch=true}if(ch)render()}});
 window.addEventListener('pagehide',save);document.addEventListener('visibilitychange',()=>{if(document.hidden)save()});
 if(back){UI.restored=true;if(Object.values(UI.devs).some(d=>d.signed))toast('Welcome back. Everything is where you left it.')}
 if(!back)intro();
 render();BOOT=false}

/* ---- mobile.js ---- */
/* The adapter between the approved screens, the back end and the phone.
   - One snapshot per role fills DB; the project picture and Today come ready-made from the server.
   - Every operation runs on the screen first, exactly as in the preview, and is then sent. Without
     network it waits in an outbox kept on the phone and goes out, in order, when the network is back.
   - The app comes back where it was closed: screen, tab, scroll, drafts, and what is waiting to go.
   - What only a phone can do (camera, fingerprint, a drawing full screen) is asked of the app itself
     through /local/…, a small server inside the app. The sign-in token never reaches this code. */
const APP={s:null,role:null,ids:{},queue:[],busy:false,depth:0,img:{},timer:null,saved:null,at:0,devices:null,otp:null};
const EMPTY_PIC={status:'ok',progress:{ag:[0,0],dr:[0,0],wk:[0,0,0,0],pt:[0,0,0,0]},week:{rel:0,started:0,done:0,closed:0},blockers:[],next:{revert:[],agencies:[],client:[]},noDwg:[]};
const LOCAL0=9e6,localSeq=()=>({lid:LOCAL0,did:LOCAL0,ptid:LOCAL0,bid:LOCAL0,vid:LOCAL0,pid:LOCAL0,q:LOCAL0});
const API='/api/rvt/v1',SNAP={staff:'/staff/snapshot',agency:'/agency/snapshot',client:'/client/snapshot'};
const num=v=>String(v==null?'':v).replace(/\D/g,'');

/* ---------- talking to the phone and to the server ---------- */
class Refused extends Error{constructor(status,body){super(((body||{}).error||{}).message||'Something went wrong.');this.status=status;this.code=((body||{}).error||{}).code||'';this.body=body||{}}}
/* ``tag``: the mark of the copy the app holds. The server then answers "the same" with nothing else,
   and the answer comes back as {__same:true}. A fresh answer carries its own mark as __etag. */
async function ask(url,method,body,again,tag){let r;const head=body===undefined?{}:{'Content-Type':'application/json'};
 if(WEB&&WEB.access&&url.indexOf('/api/')===0)head.Authorization='Bearer '+WEB.access;
 if(tag)head['If-None-Match']=tag;
 try{r=await fetch(url,{method:method||'GET',headers:head,body:body===undefined?undefined:JSON.stringify(body)})}
 catch(e){throw new Refused(503,{error:{code:'OFFLINE',message:'No connection.'}})}
 if(r.status===401&&WEB&&!again){await webEnter();return ask(url,method,body,true,tag)}
 if(r.status===304)return {__same:true};
 let j=null;try{j=await r.json()}catch(e){}
 if(!r.ok)throw new Refused(r.status,j);
 const mark=r.headers.get('ETag');if(mark&&j&&typeof j==='object')Object.defineProperty(j,'__etag',{value:mark});return j}
const local=(name,body,method)=>WEB?webLocal(name,body):ask('/local/'+name,method||(body===undefined?'GET':'POST'),body);
const api=(method,path,body)=>ask(API+path,method,body);
const keep=(key,value)=>WEB?wset(key,value):fetch('/local/store/'+key,{method:'PUT',body:JSON.stringify(value)}).catch(()=>{});
const kept=async key=>{if(WEB)return wget(key);try{const r=await fetch('/local/store/'+key);const j=r.ok?await r.json():null;return j&&!j.empty?j:null}catch(e){return null}};
const forget=key=>WEB?wset(key,null):fetch('/local/store/'+key,{method:'DELETE'}).catch(()=>{});

/* ---------- the same screens in a browser, from the link a client was sent ----------
   No app, no sign-in: the page was served with the link's token, exchanges it for a session of one
   project, and keeps that session in memory only. What the phone's shell does is done here by the
   browser itself, or left out (camera, lock, PDF viewer: the drawing opens from its own link). */
const WEB=typeof window.RVT_LINK==='string'&&window.RVT_LINK?{token:window.RVT_LINK,access:null,me:null,blobs:{}}:null;
const wget=k=>{try{return JSON.parse(localStorage.getItem('rvt_c_'+k))}catch(e){return null}};
const wset=(k,v)=>{try{v==null?localStorage.removeItem('rvt_c_'+k):localStorage.setItem('rvt_c_'+k,JSON.stringify(v))}catch(e){}};
const WEBPREFS={theme:'light',lock:false,lockAfter:0,textSize:'normal',haptics:false,pal:'emerald'};
async function webEnter(){let d=wget('device');if(!d){d='web-'+Date.now().toString(36)+Math.random().toString(36).slice(2,10);wset('device',d)}
 let r;try{r=await fetch(API+'/auth/link',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:WEB.token,device:{uid:d,name:'Browser',platform:'web',app_version:'web'}})})}
 catch(e){throw new Refused(503,{error:{code:'OFFLINE',message:'No connection.'}})}
 let j=null;try{j=await r.json()}catch(e){}if(!r.ok)throw new Refused(r.status,j);WEB.access=j.access_token;WEB.me=j.me}
async function webLocal(name,b){b=b||{};const prefs=()=>Object.assign({},WEBPREFS,wget('prefs')||{});
 if(name==='session'){let dead='';try{await webEnter();wset('me',WEB.me)}catch(e){if(e.code==='OFFLINE')WEB.me=wget('me');else dead=e.message}
  return {signed:!!WEB.me,me:WEB.me,dead,base:location.origin,defaultBase:location.origin,version:'',build:'',insets:{top:10,bottom:0},prefs:prefs(),bio:{available:false}}}
 if(name==='prefs'){if(b.lock)throw new Refused(422,{error:{code:'NO_LOCK',message:'The lock is part of the app.'}});const p=Object.assign(prefs(),b);wset('prefs',p);return p}
 if(name==='me'){if(b.me)wset('me',b.me);return {ok:true}}
 return {ok:true}}
/* pictures need the session: they are fetched with it and shown from memory */
function hydrate(){document.querySelectorAll('[data-asrc]').forEach(el=>{const u=el.dataset.asrc;el.removeAttribute('data-asrc');
 (WEB.blobs[u]||(WEB.blobs[u]=fetch(u,{headers:{Authorization:'Bearer '+WEB.access}}).then(r=>r.ok?r.blob():Promise.reject(new Error('gone'))).then(b=>URL.createObjectURL(b))))
  .then(o=>{if(el.tagName==='IMG')el.src=o;else el.style.backgroundImage='url('+o+')'}).catch(()=>{delete WEB.blobs[u]})})}
if(WEB){document.documentElement.classList.add('web');const render0=render;render=function(){render0();hydrate()}}
const haptic=kind=>{if(!WEB&&APP.s&&APP.s.prefs.haptics)fetch('/local/haptic',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:kind||''})}).catch(()=>{})};
const myDev=()=>UI.devs[APP.role||'auth'];
const L=()=>APP.role==='staff'?'en':(UI.lang[APP.role==='client'?'client':'agency']||'en');

/* ---------- words the app adds (en · gu · hi). Gujarati and Hindi need a native check. ---------- */
Object.assign(STR,{
 staffin:{en:'Revert staff? Log in here',gu:'Revert સ્ટાફ? અહીં લોગ ઇન કરો',hi:'Revert स्टाफ़? यहाँ लॉग इन करें'},
 custin:{en:'Agency or client? Use your mobile number',gu:'એજન્સી કે ક્લાયન્ટ? મોબાઇલ નંબર વાપરો',hi:'एजेंसी या क्लाइंट? मोबाइल नंबर इस्तेमाल करें'},
 codehint:{en:'The code arrives on WhatsApp. It is valid for 10 minutes.',gu:'કોડ WhatsApp પર આવશે. 10 મિનિટ માટે માન્ય.',hi:'कोड WhatsApp पर आएगा। 10 मिनट के लिए मान्य।'},
 again2:{en:'Send again',gu:'ફરી મોકલો',hi:'फिर भेजें'},changenum:{en:'Change number',gu:'નંબર બદલો',hi:'नंबर बदलें'},
 profile:{en:'Profile and settings',gu:'પ્રોફાઇલ અને સેટિંગ્સ',hi:'प्रोफ़ाइल और सेटिंग्स'},
 notif:{en:'Notifications',gu:'સૂચનાઓ',hi:'सूचनाएँ'},n_dr:{en:'Drawings',gu:'ડ્રોઇંગ',hi:'ड्रॉइंग'},n_dr2:{en:'A drawing is released, approved or asked about',gu:'ડ્રોઇંગ રિલીઝ થાય, મંજૂર થાય કે પ્રશ્ન આવે',hi:'ड्रॉइंग रिलीज़ हो, मंज़ूर हो या सवाल आए'},
 n_pt:{en:'Points and site visits',gu:'મુદ્દા અને સાઇટ મુલાકાત',hi:'बिंदु और साइट विज़िट'},n_pt2:{en:'A point is written for you or confirmed',gu:'તમારા માટે મુદ્દો લખાય કે કન્ફર્મ થાય',hi:'आपके लिए बिंदु लिखा जाए या पुष्टि हो'},
 n_bl:{en:'Bills',gu:'બિલ',hi:'बिल'},n_bl2:{en:'A bill is asked, returned, accepted or paid',gu:'બિલ માંગવામાં આવે, પરત થાય, સ્વીકારાય કે ચૂકવાય',hi:'बिल माँगा जाए, लौटे, स्वीकार हो या भुगतान हो'},
 n_rm:{en:'Reminders',gu:'રિમાઇન્ડર',hi:'रिमाइंडर'},n_rm2:{en:'Revert reminds you of one item',gu:'Revert કોઈ એક બાબત યાદ અપાવે',hi:'Revert किसी एक बात की याद दिलाए'},
 lock:{en:'App lock',gu:'એપ લોક',hi:'ऐप लॉक'},lock1:{en:'Unlock with fingerprint or face',gu:'ફિંગરપ્રિન્ટ કે ચહેરાથી ખોલો',hi:'फ़िंगरप्रिंट या चेहरे से खोलें'},lock2:{en:'The app asks before it opens. Your phone’s own lock is used.',gu:'એપ ખૂલતાં પહેલાં પૂછશે. ફોનનું પોતાનું લોક વપરાય છે.',hi:'ऐप खुलने से पहले पूछेगा। फ़ोन का अपना लॉक इस्तेमाल होता है।'},
 lockafter:{en:'Ask again',gu:'ફરી પૂછો',hi:'फिर पूछें'},la0:{en:'At once',gu:'તરત',hi:'तुरंत'},la60:{en:'After 1 min',gu:'1 મિનિટ પછી',hi:'1 मिनट बाद'},la300:{en:'After 5 min',gu:'5 મિનિટ પછી',hi:'5 मिनट बाद'},
 look:{en:'Appearance',gu:'દેખાવ',hi:'दिखावट'},light:{en:'Light',gu:'લાઇટ',hi:'लाइट'},dark:{en:'Dark',gu:'ડાર્ક',hi:'डार्क'},tsize:{en:'Text size',gu:'અક્ષરનું કદ',hi:'अक्षर का आकार'},tnormal:{en:'Normal',gu:'સામાન્ય',hi:'सामान्य'},tlarge:{en:'Large',gu:'મોટું',hi:'बड़ा'},
 vib:{en:'Vibrate on a tap',gu:'ટચ પર વાઇબ્રેશન',hi:'टैप पर कंपन'},vib2:{en:'A light tick when a button is pressed',gu:'બટન દબાવતાં હળવું વાઇબ્રેશન',hi:'बटन दबाने पर हल्का कंपन'},
 onphone:{en:'On this phone',gu:'આ ફોન પર',hi:'इस फ़ोन पर'},waiting:{en:'Waiting to go',gu:'મોકલવાનું બાકી',hi:'भेजना बाकी'},waiting0:{en:'Everything is sent',gu:'બધું મોકલાઈ ગયું છે',hi:'सब कुछ भेज दिया गया है'},sendnow:{en:'Send now',gu:'હમણાં મોકલો',hi:'अभी भेजें'},
 refresh:{en:'Refresh now',gu:'હમણાં તાજું કરો',hi:'अभी ताज़ा करें'},refresh2:{en:'Read everything again from Revert',gu:'Revert માંથી બધું ફરી વાંચો',hi:'Revert से सब कुछ फिर पढ़ें'},
 clear:{en:'Clear what is kept on this phone',gu:'આ ફોન પર સાચવેલું સાફ કરો',hi:'इस फ़ोन पर सहेजा हुआ साफ़ करें'},clear2:{en:'Drafts and the saved copy. Nothing is removed at Revert.',gu:'ડ્રાફ્ટ અને સાચવેલી નકલ. Revert પર કંઈ દૂર થતું નથી.',hi:'ड्राफ़्ट और सहेजी प्रति। Revert पर कुछ नहीं हटता।'},
 devices:{en:'Signed-in devices',gu:'સાઇન-ઇન થયેલાં ડિવાઇસ',hi:'साइन-इन किए हुए डिवाइस'},thisdev:{en:'this phone',gu:'આ ફોન',hi:'यह फ़ोन'},
 account:{en:'Account',gu:'એકાઉન્ટ',hi:'खाता'},chpw:{en:'Change password',gu:'પાસવર્ડ બદલો',hi:'पासवर्ड बदलें'},about:{en:'About',gu:'વિશે',hi:'जानकारी'},version:{en:'Version',gu:'વર્ઝન',hi:'संस्करण'},server:{en:'Server',gu:'સર્વર',hi:'सर्वर'},
 offline:{en:'No network. What you write is kept on this phone and goes out when the network is back.',gu:'નેટવર્ક નથી. તમે જે લખો તે આ ફોન પર સચવાય છે અને નેટવર્ક આવતાં મોકલાશે.',hi:'नेटवर्क नहीं है। आप जो लिखते हैं वह इस फ़ोन पर सुरक्षित है और नेटवर्क आते ही जाएगा।'},
 camera:{en:'Camera',gu:'કેમેરા',hi:'कैमरा'},gallery:{en:'Gallery',gu:'ગેલેરી',hi:'गैलरी'},addphoto:{en:'Add a photo',gu:'ફોટો ઉમેરો',hi:'फ़ोटो जोड़ें'},zoom:{en:'Open full screen',gu:'પૂરા સ્ક્રીન પર ખોલો',hi:'पूरी स्क्रीन पर खोलें'},
 aphoto:{en:'Photo',gu:'ફોટો',hi:'फ़ोटो'},shut:{en:'Close',gu:'બંધ કરો',hi:'बंद करें'},
 q_sent:{en:'Question sent to Revert.',gu:'પ્રશ્ન Revert ને મોકલાયો.',hi:'सवाल Revert को भेजा गया।'},b_sent:{en:'Bill sent to Revert.',gu:'બિલ Revert ને મોકલાયું.',hi:'बिल Revert को भेजा गया।'},
 c_ok:{en:'Approved. Recorded with your name, the date and the time.',gu:'મંજૂર. તમારા નામ, તારીખ અને સમય સાથે નોંધાયું.',hi:'मंज़ूर। आपके नाम, तारीख और समय के साथ दर्ज हुआ।'},
 c_chg:{en:'Sent to Revert. A new revision will follow.',gu:'Revert ને મોકલાયું. નવું રિવિઝન આવશે.',hi:'Revert को भेजा गया। नया रिविज़न आएगा।'},c_dn:{en:'Marked done.',gu:'પૂર્ણ તરીકે નોંધાયું.',hi:'पूरा दर्ज हुआ।'},
 yoursites:{en:'Your sites',gu:'તમારી સાઇટ',hi:'आपकी साइट'}});
const T=k=>tr(k,L());

/* ---------- one snapshot fills everything ---------- */
function setMasters(m){if(!m)return;const fill=(a,b)=>{a.length=0;(b||[]).forEach(x=>a.push(x))},clear=o=>Object.keys(o).forEach(k=>delete o[k]);APP.masters=m;
 fill(TRADES,m.trades);clear(TX);TRADES.forEach(t=>TX[t.id]=t);fill(ETYPES,m.etypes);clear(ETX);ETYPES.forEach(e=>ETX[e.n]=e);
 fill(PRESETS,m.presets);fill(EXTRAS,m.extras);fill(DEFAULT_TRADES,m.default_trades);fill(DTYPES,m.dtypes);
 if(m.templates){clear(TPL);Object.assign(TPL,m.templates)}}
function setDay(iso){const [y,mo,d]=iso.split('-').map(Number);BASE=Date.UTC(y,mo-1,d);
 const t=new Date(),h=t.getHours();NOW=((h%12)||12)+':'+String(t.getMinutes()).padStart(2,'0')+(h<12?' am':' pm')}
const setFeatures=()=>{document.documentElement.dataset.nof=Object.keys(DB.features||{}).filter(k=>!DB.features[k]).join(' ')};
function applySnapshot(s){setMasters(s.masters);setDay(s.today_date);
 const seq=DB&&DB.seq&&DB.seq.ptid>=LOCAL0?DB.seq:localSeq();
 DB=Object.assign(seed(),{seq,set:s.set,staff:s.staff,agencies:s.agencies,projects:s.projects,drawings:s.drawings,visits:s.visits,points:s.points,bills:s.bills,wa:s.wa||[],
  features:s.features,mytasks:s.mytasks||[],today:s.today||[],company:s.company,prefix:'',admin:false,today_date:s.today_date,role:s.role||'staff'});
 DB.projects.forEach(p=>{if(p.pic)p.pic.noDwg=(p.pic.noDwg||[]).map(x=>p.lines.find(l=>l.id===x.id)).filter(Boolean)});
 if(s.me_info){APP.s.me=s.me_info;local('me',{me:s.me_info}).catch(()=>{})}
 bind(s);setFeatures();markQueue()}
/* the copy kept on the phone: what the app shows before, or without, the server */
function useKept(k){if(!k||!k.DB||!k.DB.today_date||!k.masters)return false;DB=k.DB;APP.queue=k.queue||[];APP.ids=k.ids||{};setMasters(k.masters);setDay(DB.today_date);bind({});setFeatures();if(APP.queue.length)APP.held=true;markQueue();return true}
/* what has not gone yet shows on the point itself and in the visit's pill */
function markQueue(){const waiting=new Set(APP.queue.filter(o=>o.tmp).map(o=>o.tmp));
 (DB.points||[]).forEach(x=>{x.pending=UI.offline&&waiting.has(x.id)});
 UI.outbox=UI.offline?APP.queue.filter(o=>!(o.tmp&&String(o.tmp).indexOf('pt')===0)):[];
 if(UI.offline||APP.queue.length)document.documentElement.dataset.off='1';else delete document.documentElement.dataset.off}
function bind(s){const me=APP.s.me||{};
 if(APP.role==='staff')UI.user=s.me||('s'+me.id);
 if(APP.role==='agency'){UI.agency=s.me||(DB.agencies[0]||{}).id;UI.lang.agency=(me.prefs||{}).lang||s.lang||'gu'}
 if(APP.role==='client'){if(!DB.projects.some(p=>p.id===UI.clientPid))UI.clientPid=s.clientPid||(DB.projects[0]||{}).id;UI.lang.client=(me.prefs||{}).lang||s.lang||'en'}}
picture=function(p){return p.pic||EMPTY_PIC};
todayFor=function(){return (DB.today||[]).map(n=>Object.assign({p:pOf(n.pid)},n)).filter(n=>n.p)};
canSee=function(){return true};
notify=function(){};pushStaff=function(){};

/* what is on the screen is also what is kept: the phone opens on it without network */
const stash=()=>{clearTimeout(stash.h);stash.h=setTimeout(()=>{if(APP.role&&DB.today_date)keep('data_'+APP.role,{DB,queue:APP.queue,ids:APP.ids,masters:APP.masters})},500)};
/* ``force`` after anything was sent or refused: the screen may hold a change the server did not take,
   and only a full answer puts it right. A passive refresh (coming back to the app) asks "the same?" first. */
async function load(force){const tag=!force&&APP.etag&&APP.etagFor===APP.role&&DB.today_date?APP.etag:null;
 const s=await ask(API+SNAP[APP.role],'GET',undefined,false,tag);
 if(s&&s.__same){APP.at=Date.now();setOffline(false);return}
 APP.etag=(s&&s.__etag)||null;APP.etagFor=APP.role;applySnapshot(s);APP.at=Date.now();setOffline(false);stash()}
async function reload(quiet,force){try{await load(force);render()}catch(e){if(e.code==='OFFLINE')setOffline(true);else if(e.status===401)return signedOut();else if(!quiet)toast(e.message,'bad');render()}}
function setOffline(v){v=!!v;if(!!UI.offline===v)return;UI.offline=v;clearInterval(APP.timer);if(v){APP.timer=setInterval(pump,12000);if(APP.queue.length)APP.held=true}markQueue()}

/* ---------- the outbox: in order, one at a time; kept on the phone until it has gone ---------- */
const mapIds=v=>typeof v==='string'?(APP.ids[v]||v):Array.isArray(v)?v.map(mapIds):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,mapIds(x)])):v;
function remapUI(){const d=myDev();['drawer','vid'].forEach(k=>{if(APP.ids[d[k]])d[k]=APP.ids[d[k]]});(d.stack||[]).forEach(x=>{if(APP.ids[x.id])x.id=APP.ids[x.id]});if(d.sheet)Object.keys(d.sheet).forEach(k=>{if(APP.ids[d.sheet[k]])d.sheet[k]=APP.ids[d.sheet[k]]})}
function send(method,path,body,tmp){APP.queue.push({m:method,p:path,b:body,tmp});markQueue();stash();pump()}
const sync=(name,args,tmp)=>send('POST','/staff/op',{name,args},tmp);
async function pump(){if(APP.busy||!APP.role)return;if(!APP.queue.length){if(UI.offline)reload(true);return}
 APP.busy=true;document.documentElement.dataset.sync='1';let failed=null,sent=0;
 while(APP.queue.length){const o=APP.queue[0];
  try{const r=await api(o.m,mapIds(o.p),mapIds(o.b));if(o.tmp&&r&&r.id)APP.ids[o.tmp]=r.id;APP.queue.shift();sent++}
  catch(e){if(e.code==='OFFLINE'){setOffline(true);break}if(e.status===401){APP.busy=false;return signedOut()}failed=e;APP.queue.length=0}}
 const offline=UI.offline&&APP.queue.length;
 if(!offline){try{await load(true);remapUI()}catch(e){if(e.code==='OFFLINE')setOffline(true);else failed=failed||e}}
 APP.busy=false;delete document.documentElement.dataset.sync;if(offline)APP.held=true;markQueue();stash();
 if(failed)toast(failed.message,'bad');else if(sent&&!offline&&APP.held){APP.held=false;toast(`Back online · ${plural(sent,'change')} sent.`)}
 if(APP.queue.length&&!UI.offline)return pump();render()}
function wrapOP(name,fn){const orig=OP[name];if(!orig)return;OP[name]=function(){APP.depth++;let r;try{r=orig.apply(OP,arguments)}finally{APP.depth--}if(!APP.depth)fn.apply(null,[r].concat(Array.prototype.slice.call(arguments)));return r}}
const wrapA=(name,after)=>{const o=A[name];A[name]=function(v,el,dev){const r=o.apply(A,arguments);after(v,el,dev);return r}};
const uid=()=>'m'+Date.now().toString(36)+Math.random().toString(36).slice(2,8);
const takeImg=(...keys)=>{for(const k of keys){const g=APP.img[k];if(g){delete APP.img[k];return g.b64}}return ''};

/* staff: the same operations as the desk */
wrapOP('setLine',(r,p,l,st,x)=>sync('set_line',{line:l.id,state:st,cause:(x||{}).cause||'',ref:(x||{}).ref||'',note:(x||{}).note||'',agency:l.ag||''}));
wrapOP('assign',(r,p,t,ag,by)=>sync('assign',{project:p.id,trade:t,agency:ag||'',by:by==null||isNaN(by)?7:by}));
wrapOP('sendForApproval',(r,d,note)=>{const f=APP.pdf;APP.pdf=null;sync('send_for_approval',{drawing:d.id,note:note||'',file:f?f.b64:'',name:f?f.name:''})});
wrapOP('approve',(r,d)=>sync('approve',{drawing:d.id}));
wrapOP('sendBack',(r,d,note)=>sync('send_back',{drawing:d.id,note:note||''}));
wrapOP('release',(r,d,to)=>sync('release',{drawing:d.id,to}));
wrapOP('answer',(r,d,qid,text)=>sync('answer',{question:qid,text}));
wrapOP('remind',(r,to,pid,text)=>sync('remind',{to,project:pid,text}));
wrapOP('confirmPoint',(r,x)=>sync('confirm_point',{point:x.id}));
wrapOP('sendParty',(n,v,key)=>{if(n)sync('send_party',{visit:v.id,key})});
wrapOP('addPoint',(x,o)=>{sync('add_point',{pid:o.pid,vid:o.vid||'',kind:o.kind,party:o.party||'',text:o.text,e:o.e||'',t:o.t||'',due:o.due==null?null:+o.due,photo:o.photo?takeImg('m_photo','rp_photo'):'',client_uid:uid()},x.id)});
/* a question, opening a drawing, a client's decision and closing a point differ by who is signed in */
wrapOP('ask',(r,d,by,byName,text,photo)=>{const q=d.q[d.q.length-1].id;
 if(APP.role==='agency')send('POST','/agency/drawings/'+num(d.id)+'/questions',{text,photo:photo?takeImg('aq_photo'):''},q);
 else sync('ask',{drawing:d.id,by,name:byName||'',text},q)});
wrapOP('closePoint',(r,x,note,photo)=>{if(APP.role==='client')send('POST','/client/points/'+num(x.id)+'/done',{});
 else sync('close_point',{point:x.id,note:note||'',photo:photo?takeImg('cp_photo'):''})});
wrapOP('open',(first,d)=>{if(first&&APP.role!=='staff')send('POST','/'+APP.role+'/drawings/'+num(d.id)+'/open',{})});
wrapOP('clientDecide',(r,d,dec,note)=>send('POST','/client/drawings/'+num(d.id)+'/decide',{decision:dec,note:note||''}));

/* bills: staff ask, upload for an agency, review; the owner pays; an agency uploads its own */
wrapOP('askBill',(b,o)=>sync('ask_bill',{project:o.pid,agency:o.ag,trade:o.t||'',what:o.what,upto:o.upto||null,billedTo:o.billedTo||''},b.id));
wrapOP('uploadBill',(r,b,o)=>{const no=o.no==='—'?'':o.no;
 if(APP.role==='agency')send('POST','/agency/bills/'+num(b.id)+'/upload',{no,amount:o.amount,photo:takeImg('ab_doc')});
 else sync('upload_bill',{bill:b.id,no,amount:o.amount,file:takeImg('ub_doc')})});
wrapOP('reviewBill',(r,b,ok,reason)=>sync('review_bill',{bill:b.id,ok:!!ok,reason:reason||''}));
wrapOP('pay',(r,b,o)=>sync('pay_bill',{bill:b.id,amount:o.amount,by:o.by,mode:o.mode,file:takeImg('py_proof')}));

/* ---------- actions that differ from the preview ---------- */
['asuser','reset','scen','setview','jump','guide','wapanel','replay','linkmode','wachat','wadoc','closepanel','motion'].forEach(k=>A[k]=function(){});
A.offline=function(){if(UI.offline||APP.queue.length){toast(UI.offline?T('offline'):plural(APP.queue.length,'change')+' going out…','wait');pump()}else toast('Online. Everything is sent.')};
A.taskent=function(v,el,dev){const [pid,tid]=v.split('|'),p=pOf(pid),t=p.tasks.find(x=>String(x.id)===tid);if(!t)return;const ty=guessType(t.n);
 p.ents.push({id:'e'+t.id,n:t.n,ty});p.tasks=p.tasks.filter(x=>x!==t);sync('task_entity',{task:t.id,type:ty});toast(`“${t.n}” is now a room of ${p.name}. Tick its trades in Project configuration.`)};
const startmom0=A.startmom;A.startmom=function(v,el,dev){const had=new Set(DB.visits.map(x=>x.id));startmom0.call(A,v,el,dev);const nv=DB.visits.find(x=>!had.has(x.id));if(nv)sync('start_visit',{project:nv.pid},nv.id)};
wrapA('finishvisit',v=>sync('finish_visit',{visit:v}));
wrapA('dstart',v=>sync('dstart',{drawing:v}));
wrapA('newrev',v=>sync('new_revision',{drawing:v}));
wrapA('setting',v=>sync('setting',{key:v,value:DB.set[v]}));
wrapA('billto',v=>{const [id,to]=v.split('|');sync('bill_to',{bill:id,to})});
A.sendparty=function(v,el,dev){const [vid,key]=v.split('|'),n=OP.sendParty(visOf(vid),key);if(n){flash(dev,UI.offline?'Saved':'Sent','wa');toast(UI.offline?`Saved. ${agN(key)}’s PDF goes out when the network returns.`:`${agN(key)}: ${plural(n,'point')} as a PDF · ${sent()}.`)}};
A.sendall=function(v,el,dev){const vi=visOf(v),ks=[...new Set(DB.points.filter(x=>x.vid===v&&x.st==='open'&&x.kind==='agency').map(x=>x.party))];ks.forEach(k=>OP.sendParty(vi,k));flash(dev,UI.offline?'Saved':'Sent','wa');
 toast(UI.offline?'Saved. Every party’s PDF goes out when the network returns.':`${plural(ks.length,'party','parties')} got their own PDF · ${sent()}. Client points wait for the office.`)};
A.invite=function(v,el,dev){const [pid,i]=v.split('|'),p=pOf(pid),c=p.client.contacts[+i];if(!c)return;c.inv=true;sync('invite',{project:p.id,contact:c.id});toast(`Invitation to ${c.n} · ${sent()}.`)};
A.copylink=function(v){const p=pOf(v),c=p&&p.client.contacts[0];if(!c)return;api('GET','/projects/'+p.id+'/client-link?contact_id='+c.id).then(r=>{try{navigator.clipboard.writeText(r.url)}catch(e){}toast('Link copied for '+c.n+'.')}).catch(e=>toast(e.message,'bad'))};

/* the preview narrates what the other side sees; the app speaks to the person holding the phone */
const say=(name,key)=>{const o=A[name];A[name]=function(v,el,dev){const was=UI.toast,r=o.apply(A,arguments);if(UI.toast&&UI.toast!==was&&UI.toast.k==='ok'){if(key)UI.toast.t=T(key);else UI.toast=null}return r}};
say('adwg');say('cdwg');say('aask','q_sent');say('asubmit','b_sent');say('capprove','c_ok');say('cchange','c_chg');say('cdone','c_dn');

/* onboarding: the wizard is the preview's; the result is written by the server in one go */
const obStart0=obStart;obStart=function(dev,pid){const ob=obStart0(dev,pid),u=me();
 if(!DB.staff.some(x=>x.id===ob.principal&&has(x,'principal'))){const pr=DB.staff.find(x=>has(x,'principal'))||DB.staff.find(x=>has(x,'owner'));ob.principal=pr?pr.id:''}
 if(!pid){if(has(u,'coordinator')&&!ob.coords.length)ob.coords=[u.id];if(has(u,'designer')&&!ob.designers.length)ob.designers=[u.id]}return ob};
function obPayload(ob){const p=ob.pid?pOf(ob.pid):null,on=obTrades(ob),ticks=[];ob.ents.forEach(e=>on.forEach(t=>{if(obTick(ob,e,t))ticks.push([String(e.u),t])}));
 return {pid:ob.pid||'',name:ob.name.trim(),client:ob.client.trim(),cphone:(ob.cphone||'').trim(),address:ob.address||'',area:ob.area||'',kind:ob.kind,label:ob.label||'',billedTo:ob.billedTo,
  principal:ob.principal||'',designers:ob.designers,coords:ob.coords,
  ents:ob.ents.map(e=>{const t=e.task&&p?p.tasks.find(x=>x.n===e.task):null;return {u:e.u,n:e.n,ty:e.ty,id:e.id||'',taskId:t?t.id:''}}),
  tr:ob.tr,ticks,dr:ob.dr.filter(d=>d.on&&!d.exists).map(d=>({code:d.code,n:d.n,t:d.t||'',ds:d.ds||'',due:+d.due||0,client:!!d.client,appr:!!d.appr})),inv:Object.keys(ob.inv).filter(k=>ob.inv[k])}}
A.obfinish=function(v,el,dev){const ob=dev.ob;if(!ob||APP.saving)return;if(!ob.name.trim())return toast('Give the project a name first.','wait');
 if(UI.offline)return toast('Onboarding needs the network. Your entries stay here until it is back.','wait');
 const was=!!(ob.pid&&pOf(ob.pid)&&pOf(ob.pid).onb);APP.saving=true;document.documentElement.dataset.sync='1';
 api('POST','/staff/op',{name:'onboard',args:obPayload(ob)}).then(async r=>{await load(true);dev.ob=null;dev.stack=[{s:'projects'}];openProj(dev,r.pid,'picture');flash(dev,was?'Saved':'Project started','check',!was);
   const p=pOf(r.pid);toast(`${p?p.name:'Project'}: ${plural(r.nl,'work line')} and ${plural(r.nd,'drawing')} added${r.inv?' · '+plural(r.inv,'invitation')+' '+sent():''}.`)})
  .catch(e=>toast(e.message,'bad')).finally(()=>{APP.saving=false;delete document.documentElement.dataset.sync;render()})};

/* ---------- camera, files, drawings ---------- */
const fmtSize=n=>n>=1e6?(n/1e6).toFixed(1)+' MB':Math.max(1,Math.round(n/1e3))+' KB';
async function pick(kind){const r=await local('pick',{kind});if(!r||r.cancelled)return null;const b64=await (await fetch(r.blob+'?b64=1')).text();return {name:r.name,size:r.size,b64}}
const PHOTO_KEYS=['m_photo','rp_photo','cp_photo','aq_photo','ab_doc','ub_doc','py_proof'];
const tog0=A.tog;A.tog=function(v,el,dev){if(!PHOTO_KEYS.includes(v))return tog0.call(A,v,el,dev);
 if(dev.f[v]&&APP.img[v]){dev.f[v]=false;delete APP.img[v];return}dev.f[v]=false;openSheet(dev,'picksrc',{key:v})};
SHEETS.picksrc=function(dev,s){return {title:T('addphoto'),body:`<div class="langs">${Bt(T('camera'),'pickimg',s.key+'|camera','gold lg blk','cam')}${Bt(T('gallery'),'pickimg',s.key+'|gallery','lg blk','layers')}</div>`}};
A.pickimg=function(v,el,dev){const [key,kind]=v.split('|');dev.sheet=null;pick(kind).then(g=>{if(g){APP.img[key]=g;dev.f[key]=true}render()}).catch(e=>{toast(e.message,'bad');render()})};
A.pickpdf=function(v,el,dev){pick('pdf').then(g=>{if(!g)return;if(g.size>15e6){toast('That file is larger than 15 MB. Send it from the desk.','wait')}else{APP.pdf=g;dev.f.sa_file=true}render()}).catch(e=>{toast(e.message,'bad');render()})};
A.droppdf=function(v,el,dev){APP.pdf=null;dev.f.sa_file=false};
const sendappr0=SHEETS.sendappr;SHEETS.sendappr=function(dev,s){const o=sendappr0(dev,s),f=dev.f,p=APP.pdf,r=cur(dOf(s.id)),on=!!(f.sa_file&&p);
 const label=on?`<b>${esc(p.name)}</b> · ${fmtSize(p.size)} · tap to remove`:r.file?`<b>${esc(r.fname)}</b> · on file · tap to replace`:'Choose the PDF';
 o.body=o.body.replace(/<button type="button" class="drop[^]*?<\/button>/,`<button type="button" class="drop ${on||r.file?'on':''}" data-a="${on?'droppdf':'pickpdf'}">${ic(on||r.file?'file':'plus')}<span>${label}</span></button>`);return o};
const dosend0=A.dosend;A.dosend=function(v,el,dev){const d=dOf(v);if(dev.f.sa_file&&!APP.pdf)dev.f.sa_file=false;if(!dev.f.sa_file&&cur(d).file)dev.f.sa_file=true;return dosend0.call(A,v,el,dev)};
const lastFile=d=>[...d.revs].reverse().find(x=>x.file);
const pdfPath=r=>API+'/files/revision/'+r.id+(APP.role==='staff'?'':'?open=1');
const dwgPaper0=dwgPaper;dwgPaper=function(d){const r=lastFile(d);if(!r)return dwgPaper0(d);
 if(WEB)return `<div class="pdft web" role="button" tabindex="0" data-a="openpdf" data-v="${d.id}" aria-label="${esc(T('zoom'))}">${dwgPaper0(d)}<span class="zm">${ic('eye')}${esc(T('zoom'))}</span></div>`;
 return `<button type="button" class="pdft" data-a="openpdf" data-v="${d.id}" aria-label="${esc(T('zoom'))}"><img alt="${esc(sheetNo(d)+' '+d.title)}" src="/local/pdf/thumb?path=${encodeURIComponent(API+'/files/revision/'+r.id)}"><span class="zm">${ic('eye')}${esc(T('zoom'))}</span></button>`};
A.openpdf=function(v){const d=dOf(v),r=d&&lastFile(d);if(!r)return;
 if(WEB){if(d.url)window.open(d.url,'_blank','noopener');return}   /* the receiver's own link: it also records the opening */
 local('pdf/open',{path:pdfPath(r),title:sheetNo(d)+' '+d.title,sub:pOf(d.pid).name+' · rev '+r.n}).catch(e=>toast(e.message,'bad'))};
A.view=function(v){A.openpdf(v)};
A.pdf=function(v){const [kind,a,b]=v.split('|');let path,title;
 if(kind==='open'){path=API+'/files/project/'+num(a)+'/open-points';title='Open points'}
 else{path=API+'/files/visit/'+num(a)+'/pdf'+(b&&b!=='all'&&b[0]==='a'?'?partner_id='+num(b):'');title='MOM'}
 local('pdf/open',{path,title,sub:''}).catch(e=>toast(e.message,'bad'))};
function phOf(kind,x){const id=num(x.id);if(!id||+id>=LOCAL0)return '<span class="ph"></span>';const src=`${API}/files/${kind}/${id}/photo`;
 return `<span class="ph real" role="button" tabindex="0" data-a="photo" data-v="${kind}|${x.id}" aria-label="${esc(T('aphoto'))}" ${WEB?`data-asrc="${src}"`:`style="background-image:url(${src})"`}></span>`}
A.photo=function(v,el,dev){const [a,b]=v.split('|');openSheet(dev,'photo',b?{kind:a,id:b}:{kind:'point',id:a})};
SHEETS.photo=function(dev,s){const x=s.kind==='point'?ptOf(s.id):null,b=s.kind==='bill'?billOf(s.id):null;
 return {title:b?(b.no||T('bills')):T('aphoto')+(x&&APP.role==='staff'?' · point '+x.n:''),sub:x?x.text:b?b.what:'',body:`<div class="phw"><img class="phv" alt="" ${WEB?'data-asrc':'src'}="${API}/files/${s.kind}/${num(s.id)}/${b?'document':'photo'}"></div>`,foot:Bt(T('shut'),'close',null,'ghost')}};
/* a bill's document is the file that was uploaded, or nothing: never a made-up file name */
const bill0=SHEETS.bill;SHEETS.bill=function(dev,s){const o=bill0(dev,s),b=billOf(s.id);
 o.body=o.body.replace(/<div class="docrow">[^]*?<\/div>/,b.doc&&+num(b.id)<LOCAL0?`<button type="button" class="docrow" data-a="billdoc" data-v="${b.id}">${ic('file')}<span><b>${b.doc==='pdf'?'PDF':'Photo'} of the bill</b> · open</span></button>`:'');return o};
A.billdoc=function(v,el,dev){const b=billOf(v);if(!b||!b.doc)return;
 if(b.doc==='pdf')local('pdf/open',{path:API+'/files/bill/'+num(v)+'/document',title:b.no||'Bill',sub:agN(b.ag)}).catch(e=>toast(e.message,'bad'));else openSheet(dev,'photo',{kind:'bill',id:v})};

/* ---------- sign-in: one app for everybody ---------- */
function authHTML(dev){const si=dev.si||(dev.si={step:'lang'}),lang=UI.lang.auth||'gu',t=k=>tr(k,lang),f=dev.f;let b='';
 const off=UI.offline?`<div class="offb">${ic('off')}<span>No connection to Revert.</span></div>`:'';
 if(si.step==='lang')b=`<div class="auth">${authHero(1)}<h2 class="serif">ભાષા · भाषा · Language</h2><div class="langs">${[['gu','ગુજરાતી'],['hi','हिंदी'],['en','English']].map(x=>`<button type="button" class="btn lg blk ${lang===x[0]?'gold':''}" data-a="silang" data-v="${x[0]}"><span>${x[1]}</span></button>`).join('')}</div><button type="button" class="alt" data-a="sistaff">${tr('staffin','en')}</button></div>`;
 if(si.step==='phone')b=`<div class="auth">${authHero()}<h2 class="serif">${t('signin')}</h2>${fld(t('mobile'),`<div class="phin"><span>+91</span><input class="inp" id="auth_si_ph" data-m="si_ph" type="tel" inputmode="numeric" autocomplete="tel-national" maxlength="12" value="${esc(f.si_ph||'')}" placeholder="98xxx xxxxx"></div>`)}${off}${Bt(t('getcode'),'sicode',null,'wa lg blk','wa')}<button type="button" class="alt" data-a="sistaff">${t('staffin')}</button></div>`;
 if(si.step==='otp')b=`<div class="auth">${authHero()}<h2 class="serif">${t('code')}</h2><div class="otp"><input class="inp" id="auth_si_otp" data-m="si_otp" type="tel" inputmode="numeric" autocomplete="one-time-code" maxlength="4" value="${esc(f.si_otp||'')}" placeholder="• • • •"></div>${off}${Bt(t('signin'),'siverify',null,'gold lg blk','check')}
   <div class="note ok">${ic('wa')}<span>${t('codehint')}${si.test?` <b>Test copy: the code is ${esc(si.test)}.</b>`:''}</span></div><div class="chips cen"><button type="button" class="chip" data-a="sicode">${t('again2')}</button><button type="button" class="chip" data-a="siback">${t('changenum')}</button></div></div>`;
 if(si.step==='staff')b=`<div class="auth">${authHero(1)}<h2 class="serif">Welcome back</h2>${fld('Login',`<input class="inp" id="auth_st_login" data-m="st_login" type="text" autocapitalize="off" autocomplete="username" value="${esc(f.st_login||'')}">`)}${fld('Password',`<input class="inp" id="auth_st_pw" data-m="st_pw" type="password" autocomplete="current-password" value="${esc(f.st_pw||'')}">`)}${off}${Bt('Sign in','signin',null,'gold lg blk')}
   <p class="mu f12 ac">Staff use their office login. The app covers every function of the desk.</p><button type="button" class="alt" data-a="sicust">${tr('custin','en')}</button></div>`;
 return phone(dev,{key:'si'+si.step,cls:'p-auth '+(lang!=='en'&&si.step!=='staff'?'gu':''),body:b})}
const busy=(dev,on)=>{dev.si.busy=on;document.documentElement.dataset.sync=on?'1':'';if(!on)delete document.documentElement.dataset.sync};
A.silang=function(v,el,dev){if(APP.role)return A.plang(v,el,dev);UI.lang.auth=v;dev.si.step='phone'};
A.sistaff=function(v,el,dev){dev.si.step='staff'};A.sicust=function(v,el,dev){dev.si.step=UI.lang.auth?'phone':'lang'};A.siback=function(v,el,dev){dev.si.step='phone';dev.f.si_otp=''};
A.sicode=function(v,el,dev){const ph=num(dev.f.si_ph);if(ph.length<10)return toast(tr('mobile',UI.lang.auth||'en')+'?','wait');if(dev.si.busy)return;busy(dev,true);
 local('otp/request',{phone:ph,lang:UI.lang.auth||''}).then(r=>{dev.si.step='otp';dev.si.test=r.test_code||'';dev.f.si_otp='';UI.focus='auth_si_otp';setOffline(false)})
  .catch(e=>{if(e.code==='OFFLINE')setOffline(true);toast(e.message,'bad')}).finally(()=>{busy(dev,false);render()})};
A.siverify=function(v,el,dev){const code=num(dev.f.si_otp);if(code.length<4)return toast(tr('code',UI.lang.auth||'en'),'wait');if(dev.si.busy)return;busy(dev,true);
 local('otp/verify',{phone:num(dev.f.si_ph),code,lang:UI.lang.auth||''}).then(r=>enter(r.me,true)).catch(e=>{toast(e.message,'bad');busy(dev,false);render()})};
A.signin=function(v,el,dev){const f=dev.f;if(!(f.st_login||'').trim()||!f.st_pw)return toast('Type your login and password.','wait');if(dev.si.busy)return;busy(dev,true);
 local('login',{login:f.st_login.trim(),password:f.st_pw}).then(r=>{f.st_pw='';return enter(r.me,true)}).catch(e=>{if(e.code==='OFFLINE')setOffline(true);toast(e.message,'bad');busy(dev,false);render()})};
A.signout=function(v,el,dev){APP.queue.length&&!confirmLeave()?0:local('logout',{}).then(signedOut)};
const confirmLeave=()=>{if(APP.leave)return true;APP.leave=true;toast(plural(APP.queue.length,'change')+' not sent yet. Tap Sign out again to leave anyway.','wait');setTimeout(()=>APP.leave=false,6000);return false};
function signedOut(){if(WEB){APP.dead=APP.dead||'This link is no longer valid. Ask the Revert office for a new one.';APP.role=null;return render()}
 ['staff','agency','client'].forEach(k=>{forget('data_'+k);UI.devs[k]=newDev(k,true);UI.devs[k].seen=true});UI.devs.agency.stack=[{s:'home'}];UI.devs.client.stack=[{s:'home'}];forget('ui');
 APP.role=null;APP.queue=[];APP.ids={};APP.etag=null;APP.s.signed=false;APP.s.me=null;DB=seed();UI.view='auth';const d=UI.devs.auth;d.si={step:UI.lang.auth?'phone':'lang'};d.f.st_pw='';d.f.si_otp='';d.sheet=null;setOffline(false);render()}
async function enter(me,fresh){APP.s.me=me;APP.s.signed=true;APP.role=me.role;UI.view=me.role;const dev=UI.devs[me.role];dev.signed=true;dev.seen=true;
 if(fresh){dev.stack=[{s:me.role==='staff'?'today':'home'}];dev.sheet=null;dev._k=''}
 const had=useKept(await kept('data_'+me.role));
 /* with changes still waiting, the kept copy stays on screen: the outbox goes first and reads the server after */
 if(!(had&&APP.queue.length))try{await load()}catch(e){if(e.code==='OFFLINE'&&DB.today_date)setOffline(true);else if(e.status===401)return signedOut();else if(!DB.today_date){toast(e.message,'bad');APP.role=null;UI.view='auth';busy(UI.devs.auth,false);return render()}}
 if(fresh){busy(UI.devs.auth,false);flash(dev,me.role==='staff'?'Welcome, '+me.short:tr(me.role==='agency'?'hello':'c_hi',L()))}
 if(APP.queue.length)pump();render()}

/* ---------- profile and settings (every role) ---------- */
const seenOn=iso=>{const d=new Date(String(iso||'').replace(' ','T')+(/Z|[+-]\d\d:?\d\d$/.test(iso||'')?'':'Z'));return isNaN(d)?'':d.toLocaleDateString('en-GB',{day:'numeric',month:'short'})};
const sw=(key,on,label,hint)=>`<button type="button" class="sw-row" data-a="pset" data-v="${key}" aria-pressed="${!!on}"><i class="switch"></i><div><b>${esc(label)}</b><small>${esc(hint||'')}</small></div></button>`;
function profileBody(dev){const s=APP.s,me=s.me||{},pf=s.prefs,push=(me.prefs||{}).push||{},role=APP.role,solid=role==='agency'?'solid':'',lang=L();
 const chipset=(key,val,opts)=>`<div class="chips">${opts.map(o=>`<button type="button" class="chip" data-a="pset" data-v="${key}=${o[0]}" aria-pressed="${String(val)===String(o[0])}">${esc(o[1])}</button>`).join('')}</div>`;
 const devs=APP.devices||[];if(!WEB&&!APP.devices&&!UI.offline){APP.devices=[];api('GET','/me').then(r=>{APP.devices=r.devices||[];render()}).catch(()=>{})}
 const firm=role==='agency'?(me.agency||{}).name:role==='staff'?roleLabel({roles:me.roles||[]}):(pOf(UI.clientPid)||{}).name||'';
 return `<div class="stack prof"><div class="card ${solid}"><div class="rw"><div class="m"><div class="t1">${av(me.short||me.name||'?','lg')}<span>${esc(me.name||'')}</span></div><div class="t2">${esc(firm||'')}${me.phone?' · <span class="mono">'+esc(me.phone)+'</span>':''}${role==='staff'&&me.login?' · <span class="mono">'+esc(me.login)+'</span>':''}</div></div></div></div>
  ${WEB?'':card(T('notif'),'',sw('push.drawings',push.drawings,T('n_dr'),T('n_dr2'))+sw('push.points',push.points,T('n_pt'),T('n_pt2'))+(DB.features.bills?sw('push.bills',push.bills,T('n_bl'),T('n_bl2')):'')+sw('push.reminders',push.reminders,T('n_rm'),T('n_rm2')),solid)}
  ${WEB||!(s.bio||{}).available?'':card(T('lock'),'',sw('lock',pf.lock,T('lock1'),T('lock2'))+(pf.lock?`<div class="lbl mt">${T('lockafter')}</div>${chipset('lockAfter',pf.lockAfter,[[0,T('la0')],[60,T('la60')],[300,T('la300')]])}`:''),solid)}
  ${role!=='staff'?card(T('lang'),'',`<div class="langs">${[['gu','ગુજરાતી'],['hi','हिंदी'],['en','English']].map(x=>`<button type="button" class="btn lg blk ${lang===x[0]?'gold':''}" data-a="plang" data-v="${x[0]}"><span>${x[1]}</span></button>`).join('')}</div>`,solid):''}
  ${card(T('look'),'',chipset('theme',pf.theme,[['light',T('light')],['dark',T('dark')]])+`<div class="lbl mt">${T('tsize')}</div>`+chipset('textSize',pf.textSize,[['normal',T('tnormal')],['large',T('tlarge')]])+(WEB?'':sw('haptics',pf.haptics,T('vib'),T('vib2'))),solid)}
  ${WEB?'':card(T('onphone'),'',`<div class="rows"><div class="rw"><div class="m"><div class="t1">${T('waiting')}</div><div class="t2 ${APP.queue.length?'c-wait':''}">${APP.queue.length?plural(APP.queue.length,'change')+(UI.offline?' · offline':''):T('waiting0')}</div></div><div class="r">${APP.queue.length?Bt(T('sendnow'),'psend',null,'sm gold','send'):''}</div></div>
    <button type="button" class="rw lk" data-a="prefresh"><div class="m"><div class="t1">${T('refresh')}</div><div class="t2">${T('refresh2')}</div></div><div class="r">${ic('refresh','mu')}</div></button>
    <button type="button" class="rw lk" data-a="pclear"><div class="m"><div class="t1">${T('clear')}</div><div class="t2">${T('clear2')}</div></div><div class="r">${ic('chev','mu')}</div></button></div>`,solid)}
  ${!WEB&&devs.length>1?card(T('devices'),'',`<div class="rows">${devs.map(d=>`<div class="rw"><span class="mi">${ic('phone')}</span><div class="m"><div class="t1">${esc(d.name)}</div><div class="t2">${d.this?T('thisdev'):esc(seenOn(d.last_seen))}</div></div><div class="r">${d.this?'':Bt(T('signout'),'pdevout',d.id,'sm')}</div></div>`).join('')}</div>`,solid):''}
  ${role==='staff'?card(T('account'),'',`<div class="rows"><button type="button" class="rw lk" data-a="sheet" data-v="chpw"><span class="mi">${ic('lock')}</span><div class="m"><div class="t1">${T('chpw')}</div></div><div class="r">${ic('chev','mu')}</div></button></div>`):''}
  ${WEB?'':card(T('about'),'',`<div class="kv"><div><span>${T('version')}</span><b class="mono">${esc(s.version)}${s.build?' ('+esc(s.build)+')':''}</b></div>${role==='staff'||s.base!==s.defaultBase?`<div><span>${T('server')}</span><b class="mono">${esc(s.base.replace(/^https?:\/\//,''))}</b></div>`:''}</div>`,solid)}
  ${WEB?'':Bt(T('signout'),'signout',null,'blk','out')}<p class="ver">Revert Architects · Ahmedabad</p></div>`}
A.pset=function(v,el,dev){const i=v.indexOf('='),k=i<0?v:v.slice(0,i),val=i<0?null:v.slice(i+1),pf=APP.s.prefs,me=APP.s.me;
 if(k.startsWith('push.')){const key=k.slice(5),push=(me.prefs=me.prefs||{push:{}}).push;push[key]=!push[key];api('PUT','/me/preferences',{push:{[key]:push[key]}}).catch(e=>{push[key]=!push[key];toast(e.message,'bad');render()});return}
 const body=k==='lock'?{lock:!pf.lock}:k==='haptics'?{haptics:!pf.haptics}:k==='lockAfter'?{lockAfter:+val}:{[k]:val};
 local('prefs',body).then(r=>{APP.s.prefs=r;look();render()}).catch(e=>{toast(e.message,'wait');render()})};
A.plang=function(v,el,dev){const k=APP.role==='client'?'client':'agency';UI.lang[k]=v;if(APP.s.me.prefs)APP.s.me.prefs.lang=v;api('PUT','/me/preferences',{lang:v}).catch(()=>{})};
A.alang=A.plang;A.clang=function(v,el,dev){A.plang(UI.lang.client==='en'?'gu':'en',el,dev)};
A.theme=function(){A.pset('theme='+(APP.s.prefs.theme==='dark'?'light':'dark'))};
A.psend=function(){pump();toast(UI.offline?T('offline'):'Sending…','wait')};
A.prefresh=function(){reload(false,true).then(()=>{if(!UI.offline)toast('Up to date.')})};
A.pclear=function(v,el,dev){if(APP.queue.length)return toast(plural(APP.queue.length,'change')+' still waiting to go. Send them first.','wait');forget('ui');forget('data_'+APP.role);dev.f={};toast('Cleared. The app reads everything again.');reload(false,true)};
A.pdevout=function(v){api('DELETE','/me/devices/'+v).then(()=>{APP.devices=null;render()}).catch(e=>toast(e.message,'bad'))};
SHEETS.chpw=function(dev){const f=dev.f;return {title:'Change password',sub:'Other devices are signed out',body:fld('Present password',`<input class="inp" id="staff_pw_old" data-m="pw_old" type="password" value="${esc(f.pw_old||'')}">`)+fld('New password',`<input class="inp" id="staff_pw_new" data-m="pw_new" type="password" value="${esc(f.pw_new||'')}">`,'At least 8 characters.'),foot:cancelB()+Bt('Change','dochpw',null,'gold','check')}};
A.dochpw=function(v,el,dev){const f=dev.f;api('PUT','/me/password',{old:f.pw_old||'',new:f.pw_new||''}).then(()=>{f.pw_old=f.pw_new='';dev.sheet=null;APP.devices=null;toast('Password changed.');render()}).catch(e=>{toast(e.message,'bad');render()})};
function look(){const pf=APP.s.prefs,h=document.documentElement;UI.theme=pf.theme;h.dataset.rv=pf.theme==='dark'?'dark':'light';h.dataset.pal=pf.pal||'emerald';h.dataset.text=pf.textSize||'normal';fit()}
/* The approved phone is 382 wide. Every phone shows that same layout, scaled to its own width;
   "large text" enlarges the whole of it, so nothing breaks out of its place. */
const DESIGN_W=382;
function fit(){const s=APP.s,el=document.getElementById('app');if(!s||!el)return;const z=Math.max(.8,Math.min(1.6,Math.min(window.innerWidth||DESIGN_W,WEB?430:9999)/DESIGN_W))*(s.prefs.textSize==='large'?1.12:1),st=document.documentElement.style;
 el.style.zoom=z;st.setProperty('--sat',((s.insets.top||0)/z)+'px');st.setProperty('--sab',((s.insets.bottom||0)/z)+'px')}
const profileScreen=(dev,cls)=>phone(dev,{key:'prof',cls,bar:abar(T('profile'),'',{back:1,serif:1}),body:profileBody(dev)});

/* each role's screens, with the few places where the app differs from the preview */
const offBar=()=>UI.offline?`<div class="offb">${ic('off')}<span>${T('offline')}</span></div>`:'';
const staffHTML0=staffHTML;staffHTML=function(dev){if(top(dev).s==='prof')return profileScreen(dev,'');let h=staffHTML0(dev);
 if(top(dev).s==='more')h=h.replace(/<button type="button" class="rw lk" data-a="offline">[^]*?<\/button>/,`<button type="button" class="rw lk" data-a="go" data-v="prof"><i class="mi">${ic('user')}</i><div class="m"><div class="t1">Profile and settings</div><div class="t2">Notifications, app lock, appearance, this phone</div></div><div class="r">${ic('chev','mu')}</div></button>${APP.queue.length||UI.offline?`<button type="button" class="rw lk" data-a="offline"><i class="mi">${ic('off')}</i><div class="m"><div class="t1">${UI.offline?'Offline':'Sending'}</div><div class="t2">${plural(APP.queue.length,'change')} waiting to go</div></div><div class="r">${ic('refresh','mu')}</div></button>`:''}`);
 if(UI.offline&&['today','projects','mom'].includes(top(dev).s))h=h.replace('<div class="pbody','<div class="pbody').replace(/(<div class="pbody[^>]*>)/,'$1'+offBar());return h};
const agencyHTML0=agencyHTML;agencyHTML=function(dev){const g=UI.lang.agency!=='en'?'gu':'';if(top(dev).s==='profile'||top(dev).s==='prof')return profileScreen(dev,'ag '+g);
 let h=agencyHTML0(dev);if(top(dev).s==='home')h=h.replace(/<button type="button" class="ib" data-a="go" data-v="profile"[^>]*>[^]*?<\/button>/,`<button type="button" class="ib" data-a="go" data-v="prof" aria-label="${esc(T('profile'))}">${ic('user')}</button>`);
 if(UI.offline&&top(dev).s==='home')h=h.replace(/(<div class="pbody[^>]*>)/,'$1'+offBar());return h};
const clientHTML0=clientHTML;clientHTML=function(dev){const g=UI.lang.client!=='en'?'gu':'';if(top(dev).s==='prof')return profileScreen(dev,'cl '+g);if(!pOf(UI.clientPid))return phone(dev,{key:'none',cls:'cl',body:`<div class="card"><div class="empty calm">${ic('check')}<span>${T('c_none')}</span></div></div>${WEB?'':Bt(T('signout'),'signout',null,'blk','out')}`});
 let h=clientHTML0(dev);if(top(dev).s==='home'){h=h.replace(/<button type="button" class="ib oni" data-a="clang"[^]*?<\/button>/,m=>`<span class="cbt"><button type="button" class="ib oni" data-a="go" data-v="prof" aria-label="${esc(T('profile'))}">${ic('user')}</button>${m}</span>`);
  if(DB.projects.length>1)h=h.replace('<div class="sech">',`<div class="chips scroll">${DB.projects.map(p=>`<button type="button" class="chip" data-a="csite" data-v="${p.id}" aria-pressed="${p.id===UI.clientPid}">${esc(p.name)}</button>`).join('')}</div><div class="sech">`)}
 if(UI.offline&&top(dev).s==='home')h=h.replace(/(<div class="pbody[^>]*>)/,'$1'+offBar());return h};
A.csite=function(v,el,dev){UI.clientPid=+v;dev._k=''};

/* ---------- the window: one phone, the whole screen ---------- */
shellHTML=function(){if(APP.dead)return `<div class="stage"><div class="dv dv-auth" data-dev="auth">${phone(UI.devs.auth,{key:'dead',cls:'p-auth',body:`<div class="auth">${authHero(1)}<h2 class="serif">This link has expired</h2><p class="mu ac">${esc(APP.dead)}</p><p class="mu ac gu">આ લિંક હવે માન્ય નથી. Revert ઓફિસ પાસેથી નવી લિંક માગો.</p></div>`})}</div></div><div id="toast"></div>`;
 const v=APP.role||'auth',d=UI.devs[v],html=v==='staff'?staffHTML(d):v==='agency'?agencyHTML(d):v==='client'?clientHTML(d):authHTML(d);
 return `<div class="stage"><div class="dv dv-${v}" data-dev="${v}">${html}</div></div><div id="toast" aria-live="polite">${UI.toast?`<div class="toast ${UI.toast.k}">${ic(UI.toast.k==='ok'?'check':'alert')}<span>${esc(UI.toast.t)}</span></div>`:''}</div>`};

/* ---------- the session: where the app was closed ---------- */
save=function(){try{document.querySelectorAll('#app [data-sc]').forEach(el=>{const d=el.closest('[data-dev]');SCROLL[(d?d.dataset.dev:'')+':'+el.dataset.sc]=[el.scrollTop,el.scrollLeft]});
  if(!APP.role)return keep('ui',{v:1,lang:UI.lang});const d=UI.devs[APP.role],o={};Object.keys(d).forEach(k=>{if(!TRANSIENT.includes(k))o[k]=d[k]});if(o.f){o.f=Object.assign({},o.f);delete o.f.st_pw;delete o.f.pw_old;delete o.f.pw_new}
  keep('ui',{v:1,role:APP.role,user:(APP.s.me||{}).id,lang:UI.lang,clientPid:UI.clientPid,dev:o,sc:SCROLL})}catch(e){}};
restore=function(){const s=APP.saved;if(!s||s.v!==1)return false;if(s.lang)Object.assign(UI.lang,s.lang);if(!APP.role||s.role!==APP.role||s.user!==(APP.s.me||{}).id||!s.dev)return false;
 const d=UI.devs[APP.role];Object.assign(d,s.dev);d.signed=true;d.sheet=null;if(!d.stack||!d.stack.length)d.stack=[{s:APP.role==='staff'?'today':'home'}];
 d.stack=d.stack.filter(x=>!(x.s==='onboard'&&!d.ob)&&!(x.s==='project'&&!pOf(x.id))&&!(x.s==='dwg'&&!dOf(x.id))&&!(x.s==='visit'&&!visOf(x.id))&&!(x.s==='bill'&&!billOf(x.id)));if(!d.stack.length)d.stack=[{s:APP.role==='staff'?'today':'home'}];
 if(s.clientPid)UI.clientPid=s.clientPid;SCROLL=s.sc||{};OBU=Math.max(0,...(d.ob?d.ob.ents.map(e=>e.u||0):[]));UI.toast=null;return true};
intro=function(){};

/* ---------- the phone speaks to the screens ---------- */
window.__back=function(){const d=myDev();let done=true;
 if(d.sheet)d.sheet=null;else if(d.stack&&d.stack.length>1)d.stack.pop();else if(!APP.role&&d.si&&d.si.step!=='lang'&&d.si.step!=='staff')d.si.step=d.si.step==='otp'?'phone':'lang';else if(!APP.role&&d.si&&d.si.step==='staff'&&UI.lang.auth)d.si.step='phone';else done=false;
 if(done)render();return done};
window.__pause=function(){save();stash()};
window.__resume=function(away){if(!APP.role)return;if(APP.queue.length||UI.offline)pump();else if(away>45||Date.now()-APP.at>120000)reload(true)};
window.addEventListener('online',()=>{if(APP.role)pump()});

/* ---------- start ---------- */
async function appBoot(){UI.devs.auth=newDev('auth',true);UI.devs.auth.si={step:'lang'};UI.lang.auth='';UI.view='auth';['staff','agency','client'].forEach(k=>UI.devs[k].signed=false);
 try{APP.s=await local('session');if(APP.s.dead)APP.dead=APP.s.dead}catch(e){document.getElementById('app').innerHTML='<p style="padding:40px;font:600 15px system-ui;color:#fff">The app could not start. Close it and open it again.</p>';return}
 const h=document.documentElement;look();window.addEventListener('resize',fit);
 APP.saved=await kept('ui');if(APP.saved&&APP.saved.lang)Object.assign(UI.lang,APP.saved.lang);if(UI.lang.auth)UI.devs.auth.si.step='phone';
 if(APP.s.signed&&APP.s.me){APP.role=APP.s.me.role;UI.view=APP.role;UI.devs[APP.role].signed=true;
  const had=useKept(await kept('data_'+APP.role));
  if(!(had&&APP.queue.length))try{await load()}catch(e){if(e.status===401){await local('logout',{});APP.role=null;UI.view='auth';APP.s.signed=false}else if(e.code==='OFFLINE'&&DB.today_date)setOffline(true);else if(!DB.today_date){APP.role=null;UI.view='auth';UI.offline=true}}}
 if(!APP.role)splash(UI.devs.auth,false);   /* a cold start opens with the approved splash; a session that comes back gets the short one */
 boot();
 document.addEventListener('click',e=>{const el=e.target.closest&&e.target.closest('[data-a]');if(el&&!el.disabled)haptic(el.classList.contains('gold')||el.classList.contains('fab')?'heavy':'')},true);
 if(window.visualViewport){const vv=window.visualViewport,full=vv.height;vv.addEventListener('resize',()=>h.classList.toggle('kb',vv.height<full-120))}
 local('ready',{}).catch(()=>{});if(APP.role&&APP.queue.length)pump()}

appBoot();})();
