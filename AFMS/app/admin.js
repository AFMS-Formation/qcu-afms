/* ============================================================
   Console de validation des réponses (formateur)
   - propositions pré-remplies depuis answers.js (window.QCU_ANSWERS)
   - éditions sauvegardées en localStorage, exportables en answers.js
   ============================================================ */
(() => {
"use strict";
const Q = window.QCU_QUESTIONS || [];
const SEED = window.QCU_ANSWERS || {};
const LS_KEY = "qcu_answers_edits_v1";
const LETTERS = ["1","2","3","4","5"];
const UV_LABELS = {2:"Environnement juridique",3:"Gestion des conflits",4:"Stratégique",
  5:"Prévention risques incendie",6:"Appréhension (exercice du métier)",7:"Risques terroristes",
  8:"Professionnel",9:"Palpation & inspection bagages",10:"Surveillance électronique",
  11:"Gestion des risques",12:"Événementiel spécifique",14:"Industriel spécifique"};
const UV_LIST = [2,3,4,5,6,7,8,9,10,11,12,14];

const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* edits overlay */
let edits = JSON.parse(localStorage.getItem(LS_KEY) || "{}");
function record(id){ // effective record = seed <- edits
  return Object.assign({}, SEED[id]||{}, edits[id]||{});
}
function setField(id,k,v){
  edits[id] = Object.assign({}, edits[id]||{}, {[k]:v});
  localStorage.setItem(LS_KEY, JSON.stringify(edits));
  renderProgress();
}

/* ---- questions personnalisées (ajoutées à la main) ---- */
const CUSTOM_LS = "qcu_custom_v1";
let localCustom = JSON.parse(localStorage.getItem(CUSTOM_LS) || "[]");
function saveCustom(){ localStorage.setItem(CUSTOM_LS, JSON.stringify(localCustom)); }
// questions custom déjà « gravées » dans answers.js (export précédent) et absentes du corpus
const knownIds = new Set(Q.map(q=>q.id));
const seedCustom = Object.entries(SEED)
  .filter(([id,a]) => !knownIds.has(id) && a.options && a.intitule && !a.deleted)
  .map(([id,a]) => ({id, intitule:a.intitule, options:a.options.slice(), uv:(a.uv ?? null), sources:["ajout manuel"]}));
const customById = {};
seedCustom.forEach(c => customById[c.id] = c);
localCustom.forEach(c => customById[c.id] = c);     // le local prime
localCustom = Object.values(customById);
saveCustom();
const CUSTOM_IDS = new Set(localCustom.map(c=>c.id));
let ALL = Q.concat(localCustom);

/* ---- questions supprimées (masquées + marquées à l'export) ---- */
const DELETED_LS = "qcu_deleted_v1";
let deletedSet = new Set(JSON.parse(localStorage.getItem(DELETED_LS) || "[]"));
Object.entries(SEED).forEach(([id,a]) => { if(a && a.deleted) deletedSet.add(id); }); // déjà gravées
function saveDeleted(){ localStorage.setItem(DELETED_LS, JSON.stringify([...deletedSet])); }

/* ---- doublons (groupes pré-calculés dans dupes.js) ---- */
const DUPES = window.QCU_DUPES || [];
const byId = {}; ALL.forEach(q => byId[q.id] = q);
const dupGroupOf = {};
DUPES.forEach(g => g.forEach(id => { dupGroupOf[id] = g.filter(x => x !== id); }));
function livingDupSiblings(id){
  return (dupGroupOf[id] || []).filter(sid => byId[sid] && !deletedSet.has(sid));
}
function hasDup(id){ return livingDupSiblings(id).length > 0; }

let order = [];
let pos = 0;
function rebuildOrder(){
  const trash = $("#only-deleted") && $("#only-deleted").checked;
  const dups  = $("#only-dups") && $("#only-dups").checked;
  order = ALL.filter(q => {
    if(trash) return deletedSet.has(q.id);
    if(deletedSet.has(q.id)) return false;
    if(dups) return hasDup(q.id);
    return true;
  });
  if(pos >= order.length) pos = Math.max(0, order.length-1);
}
rebuildOrder();

function isDone(id){ return record(id).answer!=null; }
function isFlagged(id){ return /à confirmer/i.test(record(id).justification||""); }
function effOptions(q){ const r=record(q.id); return (r.options && r.options.length)?r.options:q.options; }
function effIntitule(q){ return record(q.id).intitule || q.intitule; }

function renderProgress(){
  const active = ALL.filter(q=>!deletedSet.has(q.id));
  const done = active.filter(q=>isDone(q.id)).length;
  const flagged = active.filter(q=>isFlagged(q.id)).length;
  const nCustom = [...CUSTOM_IDS].filter(id=>!deletedSet.has(id)).length;
  const nDel = deletedSet.size;
  let dupExtra=0;
  DUPES.forEach(g=>{ const living=g.filter(id=>byId[id]&&!deletedSet.has(id)); if(living.length>1) dupExtra+=living.length-1; });
  $("#prog").style.width = (active.length? done/active.length*100:0)+"%";
  $("#prog-txt").textContent = `${done} / ${active.length} renseignées`
    + (nCustom ? ` · +${nCustom} ajoutée${nCustom>1?"s":""}` : "")
    + (dupExtra ? ` · 🔁 ${dupExtra} doublon${dupExtra>1?"s":""}` : "")
    + (nDel ? ` · 🗑 ${nDel} supprimée${nDel>1?"s":""}` : "")
    + (flagged ? ` · ⚠ ${flagged} à confirmer` : ` · ✓ aucune à confirmer`);
}

function buildUVSelect(){
  const s=$("#uv-sel"); s.innerHTML='<option value="">— UV —</option>';
  UV_LIST.forEach(i=>{ const o=document.createElement("option"); o.value=i;
    o.textContent=`UV${String(i).padStart(2,"0")} · ${UV_LABELS[i]}`; s.appendChild(o); });
}

function current(){ return order[pos]; }

function render(){
  const q=current();
  if(!q){ $("#q-src").textContent=""; $("#q-text").textContent="(aucune question ici)";
    $("#q-options").innerHTML=""; $("#dup-banner").innerHTML=""; renderProgress(); return; }
  const r=record(q.id);
  const del = deletedSet.has(q.id);
  $("#q-src").textContent = (del?"🗑 SUPPRIMÉE · ":"") + `#${pos+1}/${order.length} · id ${q.id} · sources : ${(q.sources||[]).join(", ")}`;
  renderDupBanner(q);
  const qt=$("#q-text");
  if(qt.textContent!==effIntitule(q)) qt.textContent = effIntitule(q);
  $("#goto").value = pos+1;

  const opts=effOptions(q);
  const box=$("#q-options"); box.innerHTML="";
  opts.forEach((txt,i)=>{
    const el=document.createElement("div");
    const proposed = SEED[q.id] && SEED[q.id].answer===i;
    const chosen = r.answer===i;
    el.className="admin-opt"+(chosen?" chosen":(proposed?" proposed":""));
    el.style.cursor="pointer"; el.title="Clic = bonne réponse · double-clic sur le texte = corriger";
    // clic simple = choisir la bonne réponse, mais on attend un court instant pour
    // laisser passer un éventuel double-clic (édition du texte) sans re-dessiner.
    el.onclick=()=>{
      if(el._editing) return;
      clearTimeout(el._t);
      el._t=setTimeout(()=>{ setField(q.id,"answer",i); render(); }, 230);
    };
    const mark=document.createElement("span"); mark.className="mark";
    mark.style.cssText="flex:0 0 22px;height:22px"; mark.textContent=LETTERS[i];
    // texte : double-clic pour éditer l'orthographe
    const span=document.createElement("span");
    span.style.cssText="flex:1;outline:none"; span.spellcheck=true; span.textContent=txt;
    span.ondblclick=(e)=>{
      e.stopPropagation(); clearTimeout(el._t); el._editing=true;
      span.contentEditable="true"; span.focus();
      const rg=document.createRange(); rg.selectNodeContents(span); rg.collapse(false);
      const sel=getSelection(); sel.removeAllRanges(); sel.addRange(rg);   // curseur en fin
    };
    span.onmousedown=(e)=>{ if(span.isContentEditable) e.stopPropagation(); };
    span.onclick=(e)=>{ if(span.isContentEditable) e.stopPropagation(); };
    span.onkeydown=(e)=>{ if(e.key==="Enter"){ e.preventDefault(); span.blur(); } };
    span.onblur=()=>{ span.contentEditable="false"; el._editing=false;
      const cur=effOptions(q).slice(); if(span.textContent.trim()!==cur[i]){ cur[i]=span.textContent.trim(); setField(q.id,"options",cur);} };
    el.appendChild(mark); el.appendChild(span);
    if(proposed){ const b=document.createElement("span"); b.className="badge prop"; b.textContent="proposé"; el.appendChild(b); }
    if(chosen){ const b=document.createElement("span"); b.className="badge"; b.style.cssText="background:var(--ok-soft);color:var(--ok)"; b.textContent="✓ validé"; el.appendChild(b); }
    box.appendChild(el);
  });

  $("#uv-sel").value = r.uv!=null?r.uv:(q.uv!=null?q.uv:"");
  $("#just").value = r.justification||"";
  const custom = CUSTOM_IDS.has(q.id);
  $("#btn-del").style.display = del ? "none" : "";
  $("#btn-restore").style.display = del ? "" : "none";
  $("#reset-text").style.display = (custom||del) ? "none" : "";
  renderProgress();
}

function go(delta){
  let p=pos+delta;
  if($("#only-flagged").checked){
    // ne s'arrête que sur les questions « à confirmer »
    while(p>=0 && p<order.length && !isFlagged(order[p].id)) p+=delta;
  }
  if(p<0)p=0; if(p>=order.length)p=order.length-1;
  pos=p; render();
}
function jumpToFirstFlagged(){
  const i=order.findIndex(q=>isFlagged(q.id));
  if(i>=0){ pos=i; render(); }
}
function jumpToId(id){
  let i=order.findIndex(q=>q.id===id);
  if(i<0){ // pas dans la vue courante -> repasser en vue normale
    ["only-flagged","only-deleted","only-dups"].forEach(k=>{ const c=$("#"+k); if(c) c.checked=false; });
    rebuildOrder(); i=order.findIndex(q=>q.id===id);
  }
  if(i>=0){ pos=i; render(); }
}
function renderDupBanner(q){
  const box=$("#dup-banner"); box.innerHTML="";
  const sibs = deletedSet.has(q.id) ? [] : livingDupSiblings(q.id);
  if(!sibs.length) return;
  const div=document.createElement("div"); div.className="dup-box";
  const h=document.createElement("div"); h.className="dup-h";
  h.textContent=`🔁 Doublon probable — ${sibs.length} autre${sibs.length>1?"s":""} formulation${sibs.length>1?"s":""} de cette question. Garde-en une, supprime les autres.`;
  div.appendChild(h);
  sibs.forEach(sid=>{
    const r=document.createElement("div"); r.className="dup-row";
    const t=document.createElement("span"); t.className="dup-txt"; t.textContent="« "+effIntitule(byId[sid])+" »";
    const go=document.createElement("button"); go.className="dup-go"; go.textContent="aller"; go.onclick=()=>jumpToId(sid);
    const del=document.createElement("button"); del.className="dup-del"; del.textContent="supprimer";
    del.onclick=()=>{ deletedSet.add(sid); saveDeleted(); rebuildOrder(); render(); };
    r.appendChild(t); r.appendChild(go); r.appendChild(del);
    div.appendChild(r);
  });
  box.appendChild(div);
}
/* ---- recherche par mots-clés ---- */
let searchHits=[], searchPtr=-1, lastQuery="";
function normSearch(s){ return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,''); }
function computeHits(){
  const qy=normSearch($("#search").value.trim());
  searchHits=[];
  if(qy) order.forEach((q,i)=>{
    if(normSearch(effIntitule(q)+" "+effOptions(q).join(" ")).includes(qy)) searchHits.push(i);
  });
  return qy;
}
function searchInput(){
  const qy=computeHits(); lastQuery=qy; searchPtr=-1;
  $("#search-count").textContent = !qy ? "" : (searchHits.length ? String(searchHits.length) : "0");
}
function searchNext(){
  const qy=computeHits();
  if(qy!==lastQuery){ lastQuery=qy; searchPtr=-1; }
  if(!searchHits.length){ $("#search-count").textContent = qy?"0":""; return; }
  searchPtr=(searchPtr+1)%searchHits.length;
  pos=searchHits[searchPtr]; render();
  $("#search-count").textContent=`${searchPtr+1}/${searchHits.length}`;
}
function newQuestion(){
  const id = "c" + Date.now().toString(36);
  const q = {id, intitule:"", options:["","","","","Aucune des autres réponses"],
             uv:2, sources:["ajout manuel"]};
  localCustom.push(q); saveCustom(); CUSTOM_IDS.add(id);
  ALL.push(q);
  if($("#only-flagged").checked) $("#only-flagged").checked = false;
  if($("#only-deleted").checked) $("#only-deleted").checked = false;
  rebuildOrder(); pos = order.indexOf(q);
  render();
  const qt=$("#q-text"); qt.focus();   // prêt à taper l'intitulé
}
function deleteCurrent(){
  const q = current(); if(!q) return;
  // pas de confirm() (bloqué dans certains navigateurs, et l'action est réversible via la corbeille)
  deletedSet.add(q.id); saveDeleted();
  rebuildOrder(); render();
}
function restoreCurrent(){
  const q = current(); if(!q) return;
  deletedSet.delete(q.id); saveDeleted();
  rebuildOrder(); render();
}

/* export answers.js (merge seed + edits, only meaningful fields) */
function exportAnswers(){
  const out={};
  ALL.forEach(q=>{
    const custom = CUSTOM_IDS.has(q.id);
    if(deletedSet.has(q.id)){
      if(!custom) out[q.id]={deleted:true};   // question du corpus supprimée -> marqueur
      return;                                  // question ajoutée supprimée -> non exportée
    }
    const r=record(q.id);
    const e=edits[q.id]||{};
    if(!custom && r.answer==null && !r.justification && !e.intitule && !e.options) return;
    out[q.id]={};
    if(r.answer!=null) out[q.id].answer=r.answer;
    if(r.uv!=null && r.uv!=="") out[q.id].uv=Number(r.uv);
    else if(q.uv!=null) out[q.id].uv=q.uv;
    if(r.justification) out[q.id].justification=r.justification;
    if(custom){                       // question ajoutée : on exporte tout son contenu
      out[q.id].intitule = effIntitule(q);
      out[q.id].options  = effOptions(q);
    } else {
      if(e.intitule) out[q.id].intitule=e.intitule;   // correction de texte
      if(e.options)  out[q.id].options=e.options;
    }
  });
  const blob=new Blob(["window.QCU_ANSWERS = "+JSON.stringify(out,null,1)+";\n"],{type:"text/javascript"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob); a.download="answers.js"; a.click();
  URL.revokeObjectURL(a.href);
}

function init(){
  buildUVSelect();
  $("#prev").onclick=()=>go(-1);
  $("#next").onclick=()=>go(1);
  $("#goto").onchange=e=>{ let v=parseInt(e.target.value,10); if(v>=1&&v<=order.length){pos=v-1;render();} };
  $("#uv-sel").onchange=e=>{ setField(current().id,"uv",e.target.value===""?null:Number(e.target.value)); render(); };
  $("#just").oninput=e=>setField(current().id,"justification",e.target.value);
  $("#q-text").onblur=()=>{ const q=current(); const v=$("#q-text").textContent.trim();
    if(v && v!==q.intitule) setField(q.id,"intitule",v); };
  $("#reset-text").onclick=()=>{ const q=current();
    const e=edits[q.id]||{}; delete e.intitule; delete e.options; edits[q.id]=e;
    localStorage.setItem(LS_KEY,JSON.stringify(edits)); render(); };
  $("#btn-export").onclick=exportAnswers;
  $("#btn-new").onclick=newQuestion;
  $("#btn-del").onclick=deleteCurrent;
  $("#btn-restore").onclick=restoreCurrent;
  const otherFilters=(keep)=>["only-flagged","only-deleted","only-dups"].forEach(k=>{ if(k!==keep) $("#"+k).checked=false; });
  $("#only-flagged").onchange=e=>{
    if(e.target.checked) otherFilters("only-flagged");
    rebuildOrder(); if(e.target.checked) jumpToFirstFlagged(); else render();
  };
  $("#only-deleted").onchange=e=>{
    if(e.target.checked) otherFilters("only-deleted");
    rebuildOrder(); pos=0; render();
  };
  $("#only-dups").onchange=e=>{
    if(e.target.checked) otherFilters("only-dups");
    rebuildOrder(); pos=0; render();
  };
  $("#search").oninput=searchInput;
  $("#search").onkeydown=e=>{ if(e.key==="Enter"){ e.preventDefault(); searchNext(); } };

  document.addEventListener("keydown",e=>{
    if(e.target.tagName==="TEXTAREA"||e.target.tagName==="INPUT"||e.target.isContentEditable){
      if(e.key==="Enter"&&e.target.id==="just"){e.preventDefault();$("#just").blur();}
      return;   // ne pas capter A–E / flèches pendant l'édition de texte
    }
    const k=e.key.toUpperCase();
    if(LETTERS.includes(k)){ const i=LETTERS.indexOf(k); if(i<effOptions(current()).length){setField(current().id,"answer",i);render();} }
    else if(e.key==="ArrowLeft")go(-1);
    else if(e.key==="ArrowRight")go(1);
  });

  render();
  console.log(`Console validation — ${Q.length} questions.`);
}
document.addEventListener("DOMContentLoaded",init);
})();
