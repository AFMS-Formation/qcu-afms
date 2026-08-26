#!/usr/bin/env python3
"""Rapport des fautes d'orthographe probables dans le corpus (hors-ligne, FR)."""
import json, re, os, sys
from spellchecker import SpellChecker

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = json.load(open(os.path.join(base, "data", "questions.json"), encoding="utf-8"))
sp = SpellChecker(language='fr')

# termes métier / sigles à ne PAS signaler
WHITELIST = {w.lower() for w in [
 "TFP","APS","CNAPS","CPP","OPJ","APJ","DATI","PTI","ICPE","SEVESO","PPI","POI","PER",
 "IGH","ERP","SSIAP","NRBC","PLS","CO2","PCS","GTB","GTC","ECS","TGBT","DAI","CNIL","STAD",
 "ORSEC","VIP","OIV","SMS","CLAC","AFMS","QCU","UV","vigipirate","préfectoral","vidéoprotection",
 "vélocinétique","microphoniques","volumétrique","périphérique","déontologie","comburant",
 "réquisition","préfet","préfectorale","habilité","habilitation","agréés","agrément",
]}
TOKEN = re.compile(r"[A-Za-zÀ-ÿ]+(?:['’][A-Za-zÀ-ÿ]+)?")

def sig(w): return w.isupper() and len(w) <= 5   # sigle

flagged = {}   # question id -> list of (word, suggestion)
word_count = {}
for q in Q:
    texts = [q["intitule"]] + q["options"]
    bad = []
    for t in texts:
        for tok in TOKEN.findall(t):
            core = tok.strip("'’")
            if sig(tok): continue
            low = core.lower()
            if low in WHITELIST or len(low) <= 2: continue
            if any(c.isdigit() for c in core): continue
            # split on apostrophe (l'agent -> agent)
            parts = re.split(r"['’]", low)
            for p in parts:
                if len(p) <= 2 or p in WHITELIST: continue
                if p not in sp:  # unknown
                    sug = sp.correction(p)
                    bad.append((p, sug))
                    word_count[p] = word_count.get(p, 0) + 1
    if bad:
        flagged[q["id"]] = bad

print(f"Questions avec mot(s) suspect(s) : {len(flagged)} / {len(Q)}")
print(f"Mots suspects distincts : {len(word_count)}")
print("\nTop mots suspects (fréquence) :")
for w, c in sorted(word_count.items(), key=lambda x:-x[1])[:60]:
    print(f"   {c:3d}  {w!r}  → {sp.correction(w)!r}")

# write full report
with open(os.path.join(base, "data", "spellcheck_report.json"), "w", encoding="utf-8") as fh:
    json.dump({qid: bad for qid, bad in flagged.items()}, fh, ensure_ascii=False, indent=1)
print("\n→ data/spellcheck_report.json")
