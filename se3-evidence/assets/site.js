(function(){
'use strict';
const D=window.SE3_DATA;
const $=(id)=>document.getElementById(id);
window.SE3_MEDIA=window.SE3_MEDIA||{};
const media=window.SE3_MEDIA;
window.attachSE3Media=function(){
  if(media.video && $('comparison-video') && !$('comparison-video').src) {
    $('comparison-video').src=media.video; $('comparison-video').load();
  }
  if(media.gif && $('comparison-gif'))$('comparison-gif').src=media.gif;
  if(media.contact && $('comparison-sheet')) {
    $('comparison-sheet').src=media.contact;
    const video=$('comparison-video');if(video)video.poster=media.contact;
  }
};
document.querySelectorAll('.tab[data-media]').forEach(btn=>btn.addEventListener('click',()=>{
  const type=btn.getAttribute('data-media');
  document.querySelectorAll('.tab[data-media]').forEach(x=>x.classList.toggle('active',x===btn));
  ['video','gif','sheet'].forEach(n=>$(n+'-pane').classList.toggle('hidden',n!==type));
  if(type!=='video')$('comparison-video').pause();
  window.attachSE3Media();
}));
if(!D){return;}
const future=D.frames.filter(x=>x.frame>0);
const byIdx=Object.fromEntries(future.map(x=>[x.frame,x]));
const fmt=(n,d=2)=>Number(n).toFixed(d);
if($('hero-t'))$('hero-t').innerHTML=fmt(D.stats.translation_error_cm.median*10)+' <small>mm</small>';
if($('hero-r'))$('hero-r').innerHTML=fmt(D.stats.rotation_error_deg.median)+'<small>°</small>';
if($('hero-c'))$('hero-c').innerHTML=D.stats.accepted_future_frames+'<small>/'+D.stats.eligible_future_frames+'</small>';
if($('hero-s'))$('hero-s').innerHTML=fmt(100*D.stats.all_frame_correct_2cm_10deg,0)+'<small>%</small>';
const ns="http://www.w3.org/2000/svg";
function el(tag,attributes,inner){
  const node=document.createElementNS(ns,tag);
  for(const [k,v] of Object.entries(attributes||{}))node.setAttribute(k,String(v));
  if(inner!==undefined)node.textContent=inner;
  return node;
}
const charts=[
  {id:'translation-chart',key:'translation_mm',max:20,color:'#13a38d',threshold:20},
  {id:'rotation-chart',key:'rotation_deg',max:10,color:'#9173d3',threshold:10}
];
let selected=20;
function draw(c){
  const svg=$(c.id);if(!svg)return;
  while(svg.firstChild)svg.firstChild.remove();
  const W=620,H=230,left=41,right=15,top=15,bottom=34;
  const xx=n=>left+(n-1)/38*(W-left-right);
  const yy=n=>top+(1-n/c.max)*(H-top-bottom);
  for(let tick=0;tick<=4;tick++){
    const y=top+tick*(H-top-bottom)/4;
    svg.append(el('line',{x1:left,y1:y,x2:W-right,y2:y,stroke:'#dae5e6','stroke-width':1}));
    svg.append(el('text',{x:left-8,y:y+4,fill:'#73909a','text-anchor':'end','font-size':12},fmt(c.max*(1-tick/4),tick===4?0:1)));
  }
  for(const n of [1,10,20,30,39]){
    const x=xx(n);
    svg.append(el('text',{x,y:H-12,fill:'#72909a','text-anchor':'middle','font-size':12},n));
  }
  svg.append(el('line',{x1:left,y1:yy(c.threshold),x2:W-right,y2:yy(c.threshold),stroke:'#c06e5a','stroke-width':1.3,'stroke-dasharray':'5 5'}));
  const path=future.map((f,i)=>(i?'L':'M')+xx(f.frame).toFixed(1)+' '+yy(f[c.key]).toFixed(1)).join(' ');
  svg.append(el('path',{d:path,stroke:c.color,'stroke-width':2.8,fill:'none','stroke-linecap':'round','stroke-linejoin':'round'}));
  const x=xx(selected),row=byIdx[selected];
  svg.append(el('line',{x1:x,y1:top,x2:x,y2:H-bottom,stroke:'#456166','stroke-dasharray':'4 4','stroke-width':1.5}));
  svg.append(el('circle',{cx:x,cy:yy(row[c.key]),r:5.5,fill:'#fff',stroke:c.color,'stroke-width':3}));
}
function updateFrame(next){
  selected=Math.min(39,Math.max(1,Number(next)||1));
  const row=byIdx[selected];if(!row)return;
  $('frame-index').textContent=String(selected).padStart(2,'0');
  $('current-t').textContent=fmt(row.translation_mm,2);
  $('current-r').textContent=fmt(row.rotation_deg,2);
  const slider=$('frame-slider');slider.value=selected;
  slider.style.background='linear-gradient(90deg,#19a48b '+((selected-1)/38*100)+'%,#d5e4e3 '+((selected-1)/38*100)+'%)';
  charts.forEach(draw);
}
$('frame-slider')?.addEventListener('input',e=>updateFrame(e.target.value));
updateFrame(20);
const dataBlob=new Blob([JSON.stringify(D,null,2)],{type:'application/json'});
const dl=$('download-metrics');
if(dl)dl.href=URL.createObjectURL(dataBlob);
})();
