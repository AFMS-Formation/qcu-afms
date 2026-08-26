/* ============================================================
   QCU TFP APS — moteur d'entraînement (vanilla JS, sans dépendance)
   Données : window.QCU_QUESTIONS (corpus)  +  window.QCU_ANSWERS (corrections)
   ============================================================ */
(() => {
"use strict";

const QUESTIONS = window.QCU_QUESTIONS || [];
const ANSWERS   = window.QCU_ANSWERS   || {};
const QUESTION_TIME = 45;               // secondes par question
const PASS_NOTE = 12;                   // note/20 minimale pour valider un module

/* ---- taxonomie UV officielle (TFP APS) ---- */
const UV_LABELS = {
  2:"Environnement juridique", 3:"Gestion des conflits", 4:"Stratégique",
  5:"Prévention risques incendie", 6:"Appréhension (exercice du métier)",
  7:"Risques terroristes", 8:"Professionnel", 9:"Palpation & inspection bagages",
  10:"Surveillance électronique", 11:"Gestion des risques",
  12:"Événementiel spécifique", 14:"Industriel spécifique",
};
/* composition officielle d'un examen (total 99) ; UV10+12+14 regroupés sur 15 */
const EXAM_PLAN = {2:15, 3:10, 4:5, 5:5, 6:8, 7:10, 8:15, 9:8, 11:8};
const GROUP_UVS = [10,12,14];
const GROUP_COUNT = 15;

/* ---- fusionne corpus + corrections ---- */
function enrich(q){
  const a = ANSWERS[q.id] || {};
  return {
    ...q,
    intitule: (a.intitule ?? q.intitule),          // correction de texte éventuelle
    options: (a.options ?? q.options),
    answer: (a.answer ?? null),                    // index 0-4 de la bonne réponse
    justification: (a.justification ?? ""),
    uv: (a.uv ?? q.uv ?? null),                    // la correction peut réassigner l'UV
  };
}
// questions ajoutées à la main (présentes dans answers.js mais pas dans le corpus)
const KNOWN_IDS = new Set(QUESTIONS.map(q => q.id));
const isDeleted = id => ANSWERS[id] && ANSWERS[id].deleted;
const CUSTOM_Q = Object.entries(ANSWERS)
  .filter(([id, a]) => !KNOWN_IDS.has(id) && a.options && a.intitule && !a.deleted)
  .map(([id, a]) => ({ id, intitule:a.intitule, options:a.options, uv:(a.uv ?? null), sources:["ajout manuel"] }));
const POOL = QUESTIONS.filter(q => !isDeleted(q.id)).concat(CUSTOM_Q).map(enrich);
const READY = POOL.filter(q => q.answer !== null && q.answer !== undefined);

/* ---- état de session ---- */
const cfg = { uvs:new Set(), len:10, format:"revision" };
let quiz = null;   // {items, idx, answers[], timer, remaining}

/* ---- utilitaires ---- */
const $  = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
const LETTERS = ["1","2","3","4","5"];
function shuffle(arr){ const a=arr.slice(); for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
function show(id){ ["screen-home","screen-quiz","screen-results"].forEach(s=>$("#"+s).classList.toggle("hidden", s!==id)); window.scrollTo(0,0); }

/* ============================================================
   ÉCRAN ACCUEIL
   ============================================================ */
function availableUVs(){
  const set = new Set();
  POOL.forEach(q => { if(q.uv!=null) set.add(q.uv); });
  return Array.from(set).sort((a,b)=>a-b);
}
function basePool(){ return POOL; }   // on tire toujours dans tout le corpus (corrigé ou non)
function poolFor(cfgLike){
  return basePool().filter(q=>{
    if(cfgLike.uvs.size && !cfgLike.uvs.has(q.uv)) return false;
    return true;
  });
}
/* Compose un examen blanc (composition officielle, UV10+12+14 regroupés). */
function buildExamItems(){
  const useAll = cfg.uvs.size===0;
  const draw = (uvList,count)=>{
    let pool = basePool().filter(q=> uvList.includes(q.uv));
    return shuffle(pool).slice(0,count);
  };
  // blocs UV par UV, dans l'ordre (UV2, UV3, … UV11, puis UV10+12+14 regroupés).
  // On NE mélange PAS l'ordre des blocs : les questions sont posées UV par UV.
  let items=[];
  for(const uv of Object.keys(EXAM_PLAN).map(Number)){
    if(useAll||cfg.uvs.has(uv)) items=items.concat(draw([uv],EXAM_PLAN[uv]));
  }
  if(useAll || GROUP_UVS.some(u=>cfg.uvs.has(u))){
    const sel = useAll?GROUP_UVS:GROUP_UVS.filter(u=>cfg.uvs.has(u));
    // UV10+12+14 = un seul bloc de 15 questions, mélangées entre les trois UV
    items=items.concat(draw(sel,GROUP_COUNT));
  }
  return items;
}
function plannedExamCount(){
  const useAll=cfg.uvs.size===0; let n=0;
  for(const uv of Object.keys(EXAM_PLAN).map(Number)) if(useAll||cfg.uvs.has(uv)) n+=EXAM_PLAN[uv];
  if(useAll||GROUP_UVS.some(u=>cfg.uvs.has(u))) n+=GROUP_COUNT;
  return n;
}
function renderHome(){
  const chips = $("#uv-chips"); chips.innerHTML="";
  availableUVs().forEach(uv=>{
    const n = POOL.filter(q=>q.uv===uv).length;
    const el = document.createElement("button");
    el.className="chip"+(cfg.uvs.has(uv)?" on":"");
    el.innerHTML = `UV${String(uv).padStart(2,"0")} · ${UV_LABELS[uv]||"—"}<span class="n">${n}</span>`;
    el.onclick=()=>{ cfg.uvs.has(uv)?cfg.uvs.delete(uv):cfg.uvs.add(uv); renderHome(); };
    chips.appendChild(el);
  });
  updatePoolHint();
}
function updatePoolHint(){
  const warn = READY.length===0
    ? " ⚠︎ Corrections non encore chargées : mode aperçu (bonnes réponses non garanties)."
    : "";
  let avail;
  if(cfg.format==="examen"){
    const planned = plannedExamCount();
    avail = buildExamItems().length;
    $("#pool-hint").textContent =
      `Examen : ${planned} questions prévues, ${avail} disponibles actuellement.`+warn;
  }else{
    avail = poolFor(cfg).length;
    $("#pool-hint").textContent =
      `${avail} question${avail>1?"s":""} disponible${avail>1?"s":""} avec ces critères.`+warn;
  }
  $("#btn-generate").disabled = avail===0;
}

/* segmented controls */
function bindSeg(sel, key, cast){
  $$(sel+" button").forEach(b=>{
    b.onclick=()=>{ $$(sel+" button").forEach(x=>x.classList.remove("on")); b.classList.add("on");
      cfg[key]=cast(b.dataset[key]); updatePoolHint(); };
  });
}

/* ============================================================
   QUIZ
   ============================================================ */
function startQuiz(){
  let selected;
  if(cfg.format==="examen"){
    selected = buildExamItems();
  }else{
    const pool = poolFor(cfg);
    const n = cfg.len==="max" ? pool.length : Math.min(parseInt(cfg.len,10), pool.length);
    // sélection aléatoire des questions, puis regroupées et ordonnées UV par UV
    selected = shuffle(pool).slice(0, n).sort((a,b)=>a.uv-b.uv);
  }
  const items = selected.map(q=>{
    // mélange l'ordre des propositions, en gardant l'index de la bonne
    const order = shuffle(q.options.map((_,i)=>i));
    return {
      ref:q,
      opts: order.map(i=>q.options[i]),
      correctPos: q.answer==null?null:order.indexOf(q.answer),
    };
  });
  // position de chaque question dans son bloc UV (ex : 1/5 pour l'UV5)
  const uvTotals={}; items.forEach(it=>{ uvTotals[it.ref.uv]=(uvTotals[it.ref.uv]||0)+1; });
  const uvSeen={}; items.forEach(it=>{ uvSeen[it.ref.uv]=(uvSeen[it.ref.uv]||0)+1;
    it.uvPos=uvSeen[it.ref.uv]; it.uvTotal=uvTotals[it.ref.uv]; });
  quiz = { items, idx:0, answers:new Array(items.length).fill(null), timer:null, remaining:QUESTION_TIME };
  show("screen-quiz");
  $("#q-tot").textContent = items.length;
  renderQuestion();
}

function renderQuestion(){
  const it = quiz.items[quiz.idx];
  $("#q-cur").textContent = quiz.idx+1;
  $("#progress-fill").style.width = ((quiz.idx)/quiz.items.length*100)+"%";
  const uv = it.ref.uv;
  $("#q-uv").textContent = uv!=null ? `UV${String(uv).padStart(2,"0")} · ${it.uvPos}/${it.uvTotal}` : "—";
  $("#q-uv").style.visibility = uv!=null ? "visible":"hidden";
  $("#q-text").textContent = it.ref.intitule;
  $("#q-explain").classList.add("hidden");

  const box = $("#q-options"); box.innerHTML="";
  it.opts.forEach((txt,pos)=>{
    const b=document.createElement("button");
    b.className="opt"; b.type="button";
    b.innerHTML = `<span class="mark">${LETTERS[pos]}</span><span>${escapeHtml(txt)}</span>`;
    b.onclick=()=>selectOption(pos);
    box.appendChild(b);
  });
  const next=$("#btn-next");
  next.classList.remove("hidden");
  next.textContent="Valider"; next.disabled=true; next.onclick=()=>validateAnswer();
  quiz.selected=null; quiz.advancing=false;
  startTimer();
}

function selectOption(pos){
  if(quiz.locked) return;
  quiz.selected=pos;
  $$("#q-options .opt").forEach((el,i)=>el.classList.toggle("sel", i===pos));
  $("#btn-next").disabled=false;
}

function startTimer(){
  clearInterval(quiz.timer);
  quiz.remaining=QUESTION_TIME; quiz.locked=false;
  paintTimer();
  quiz.timer=setInterval(()=>{
    quiz.remaining--; paintTimer();
    if(quiz.remaining<=0){ clearInterval(quiz.timer); validateAnswer(true); }
  },1000);
}
function paintTimer(){
  const C=2*Math.PI*19;
  const frac=Math.max(0,quiz.remaining)/QUESTION_TIME;
  const bar=$("#ring-bar");
  bar.style.strokeDasharray=C; bar.style.strokeDashoffset=C*(1-frac);
  $("#timer-num").textContent=Math.max(0,quiz.remaining);
  $("#timer").classList.toggle("low", quiz.remaining<=10);
}

function validateAnswer(timeout=false){
  if(quiz.locked) return;
  quiz.locked=true; clearInterval(quiz.timer);
  const it=quiz.items[quiz.idx];
  const chosen = timeout ? (quiz.selected) : quiz.selected;   // peut être null si temps écoulé sans choix
  quiz.answers[quiz.idx]=chosen;

  const opts=$$("#q-options .opt");
  const hasKey = it.correctPos!=null;
  opts.forEach((el,i)=>{
    el.disabled=true;
    if(!hasKey){ if(i===chosen) el.classList.add("sel"); return; } // aperçu : pas de correction
    if(i===it.correctPos) el.classList.add("correct");
    if(i===chosen && i!==it.correctPos) el.classList.add("wrong");
  });
  // justification / correction
  if(it.ref.justification){
    const ex=$("#q-explain"); ex.classList.remove("hidden");
    const good = it.correctPos!=null ? LETTERS[it.correctPos] : "?";
    ex.innerHTML = `<b>Bonne réponse : ${good}.</b> ${escapeHtml(it.ref.justification)}`;
  }
  $("#progress-fill").style.width=((quiz.idx+1)/quiz.items.length*100)+"%";

  // valider = montrer la correction ; on avance uniquement via le bouton
  const next=$("#btn-next");
  next.disabled=false;
  next.textContent = quiz.idx+1<quiz.items.length ? "Question suivante" : "Voir les résultats";
  next.onclick = advance;
}

function advance(){
  if(quiz.advancing) return; quiz.advancing=true;
  if(quiz.idx+1<quiz.items.length){ quiz.idx++; renderQuestion(); }
  else finishQuiz();
}

/* ============================================================
   RÉSULTATS
   ============================================================ */
/* stats par module (UV) : total, fautes, note/20, validé (>= PASS_NOTE) */
function moduleStats(){
  const m={};
  quiz.items.forEach((it,i)=>{
    if(it.correctPos==null) return;                 // question sans correction -> non comptée
    const uv=it.ref.uv;
    (m[uv]=m[uv]||{total:0,correct:0}).total++;
    if(quiz.answers[i]===it.correctPos) m[uv].correct++;
  });
  return Object.keys(m).map(Number).sort((a,b)=>a-b).map(uv=>{
    const s=m[uv], fautes=s.total-s.correct;
    const note=+(s.correct/s.total*20).toFixed(1);
    return {uv, total:s.total, fautes, note, valide: note>=PASS_NOTE};
  });
}
function renderModuleRecap(){
  const box=$("#module-recap"); box.innerHTML="";
  moduleStats().forEach(m=>{
    const el=document.createElement("div");
    el.className="mod "+(m.valide?"ok":"ko");
    el.innerHTML=`<span class="mod-uv">UV${String(m.uv).padStart(2,"0")}</span>`+
      `<span class="mod-name">${UV_LABELS[m.uv]||""}</span>`+
      `<span class="mod-score">${m.fautes} faute${m.fautes>1?"s":""} / ${m.total} · ${m.note}/20</span>`+
      `<span class="mod-badge">${m.valide?"✓ validé":"✗ non validé"}</span>`;
    box.appendChild(el);
  });
}

function finishQuiz(){
  show("screen-results");
  let good=0, scored=0;
  quiz.items.forEach((it,i)=>{
    if(it.correctPos==null) return;
    scored++;
    if(quiz.answers[i]===it.correctPos) good++;
  });
  $("#score-big").textContent = `${good}/${scored||quiz.items.length}`;
  const pct = scored? Math.round(good/scored*100):0;
  $("#score-sub").textContent = scored
    ? `${pct}% de bonnes réponses.` + (pct>=70?" Bravo, niveau examen atteint.":" Continue à réviser.")
    : "Corrections non disponibles pour ce lot.";

  // révision détaillée (écran)
  const list=$("#review-list"); list.innerHTML="";
  quiz.items.forEach((it,i)=>{
    const card=document.createElement("div"); card.className="rev-item";
    const chosen=quiz.answers[i];
    let html=`<div class="rev-q">${i+1}. ${escapeHtml(it.ref.intitule)}</div>`;
    it.opts.forEach((txt,pos)=>{
      let cls="rev-line", tag="";
      if(it.correctPos===pos){ cls+=" ok"; tag=" ✓ bonne réponse"; }
      if(chosen===pos && pos!==it.correctPos){ cls+=" ko"; tag=" ✗ ta réponse"; }
      html+=`<div class="${cls}">${LETTERS[pos]}. ${escapeHtml(txt)}${tag}</div>`;
    });
    if(chosen==null) html+=`<div class="rev-line ko">✗ Aucune réponse (temps écoulé)</div>`;
    if(it.ref.justification) html+=`<div class="explain" style="margin-top:10px">${escapeHtml(it.ref.justification)}</div>`;
    card.innerHTML=html; list.appendChild(card);
  });
  renderModuleRecap();
  buildPrintBlock(good,scored);
}

function buildPrintBlock(good,scored){
  const blk=$("#print-block");
  let html=`<h2 style="margin-bottom:4px">QCU TFP APS — corrigé</h2>
    <div style="color:#5b6470;margin-bottom:14px">${new Date().toLocaleDateString("fr-FR")} · ${quiz.items.length} questions · score ${good}/${scored||quiz.items.length}</div>`;
  // récap par module
  html+=`<div style="margin-bottom:18px"><b>Résultats par module</b> (validé à ${PASS_NOTE}/20)`;
  moduleStats().forEach(m=>{
    const col=m.valide?"#1a7f4b":"#c33232";
    html+=`<div style="font-size:12.5px;color:${col};padding:2px 0">`+
      `UV${String(m.uv).padStart(2,"0")} ${escapeHtml(UV_LABELS[m.uv]||"")} — ${m.fautes} faute(s)/${m.total} · ${m.note}/20 · ${m.valide?"✓ validé":"✗ non validé"}</div>`;
  });
  html+=`</div>`;
  quiz.items.forEach((it,i)=>{
    const chosen=quiz.answers[i];
    html+=`<div class="print-q"><h3>${i+1}. ${escapeHtml(it.ref.intitule)}</h3>`;
    it.opts.forEach((txt,pos)=>{
      let cls="print-opt";
      if(it.correctPos===pos) cls+=" correct";
      if(chosen===pos && pos!==it.correctPos) cls+=" wrong";
      html+=`<div class="${cls}">${LETTERS[pos]}. ${escapeHtml(txt)}</div>`;
    });
    if(it.ref.justification) html+=`<div style="font-size:12px;color:#333;margin-top:4px"><i>${escapeHtml(it.ref.justification)}</i></div>`;
    html+=`</div>`;
  });
  blk.innerHTML=html;   // visible uniquement à l'impression (voir styles.css)
}

/* ============================================================
   OUTILS
   ============================================================ */
function escapeHtml(s){ return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

/* ============================================================
   INIT
   ============================================================ */
function applyFormatUI(){
  const exam = cfg.format==="examen";
  if(exam) cfg.uvs.clear();                       // l'examen est toujours complet (99)
  $("#uv-field").classList.toggle("hidden", exam); // révision seulement
  $("#len-field").classList.toggle("hidden", exam);
  $("#exam-intro").classList.toggle("hidden", !exam);
  $("#fmt-hint").classList.toggle("hidden", exam);
  $("#fmt-hint").textContent = "Choisis tes UV et le nombre de questions.";
  $("#btn-generate").textContent = exam ? "Commencer l'examen" : "Générer le QCU";
  if(!exam) renderHome();                          // rafraîchit les chips (désélection)
  updatePoolHint();
}
function init(){
  renderHome();
  bindSeg("#len-seg","len",v=>v);
  $$("#fmt-seg button").forEach(b=>{
    b.onclick=()=>{ $$("#fmt-seg button").forEach(x=>x.classList.remove("on")); b.classList.add("on");
      cfg.format=b.dataset.fmt; applyFormatUI(); };
  });
  applyFormatUI();
  $("#btn-generate").onclick=startQuiz;
  $("#btn-restart").onclick=()=>{ show("screen-home"); renderHome(); };
  $("#btn-print").onclick=()=>window.print();
  $("#nav-home").onclick=e=>{ e.preventDefault();
    if(quiz){ clearInterval(quiz.timer); clearTimeout(quiz.advTimer); }
    cfg.format="revision"; $$("#fmt-seg button").forEach(x=>x.classList.toggle("on",x.dataset.fmt==="revision"));
    applyFormatUI(); show("screen-home"); renderHome(); };
  console.log(`QCU TFP APS — ${QUESTIONS.length} questions, ${READY.length} avec correction.`);
}
document.addEventListener("DOMContentLoaded",init);
})();
