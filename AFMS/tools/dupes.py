#!/usr/bin/env python3
"""
Détecte les quasi-doublons (intitulé très proche ET même bonne réponse) et écrit
app/dupes.js = window.QCU_DUPES = [[id, id, ...], ...] (un tableau par groupe).
La console de validation s'en sert pour proposer les doublons à supprimer.
"""
import json, re, os, unicodedata
from difflib import SequenceMatcher

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = json.load(open(os.path.join(base, "data", "questions.json"), encoding="utf-8"))
# lire la clé de correction en vigueur (app/answers.js — version validée), sinon le JSON
_ajs = open(os.path.join(base, "app", "answers.js"), encoding="utf-8").read()
_ajs = _ajs[_ajs.find("window.QCU_ANSWERS"):]
_ajs = re.sub(r'^window\.QCU_ANSWERS\s*=\s*', '', _ajs.strip())
A = json.loads(re.sub(r';\s*$', '', _ajs))
DELETED = {k for k, v in A.items() if v.get("deleted")}
Q = [q for q in Q if q["id"] not in DELETED]   # on ne cherche pas de doublons parmi les supprimées

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()

def tok(s): return set(norm(s).split())

def correct_text(q):
    a = A.get(q["id"], {})
    if a.get("answer") is None: return None
    opts = a.get("options") or q["options"]
    if a["answer"] >= len(opts): return None
    return norm(opts[a["answer"]])

N = len(Q)
ni = [norm(q["intitule"]) for q in Q]
ti = [tok(q["intitule"]) for q in Q]
ct = [correct_text(q) for q in Q]

parent = list(range(N))
def find(x):
    while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[rb] = ra

for i in range(N):
    for j in range(i+1, N):
        if not ti[i] or not ti[j]: continue
        jt = len(ti[i] & ti[j]) / len(ti[i] | ti[j])
        if jt < 0.45: continue
        r = SequenceMatcher(None, ni[i], ni[j]).ratio()
        strong = r >= 0.85 or (r >= 0.7 and jt >= 0.7)
        same_ans = ct[i] is not None and ct[i] == ct[j]
        if strong and same_ans:
            union(i, j)

from collections import defaultdict
groups = defaultdict(list)
for i in range(N): groups[find(i)].append(i)
clusters = [[Q[i]["id"] for i in g] for g in groups.values() if len(g) > 1]
clusters.sort(key=lambda g: -len(g))

with open(os.path.join(base, "app", "dupes.js"), "w", encoding="utf-8") as fh:
    fh.write("window.QCU_DUPES = " + json.dumps(clusters, ensure_ascii=False) + ";\n")

extra = sum(len(g)-1 for g in clusters)
print(f"Groupes de doublons : {len(clusters)} · doublons à retirer : {extra} · corpus {N} -> {N-extra}")
print("→ app/dupes.js")
