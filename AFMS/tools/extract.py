#!/usr/bin/env python3
"""
Extraction pipeline: 10 .pptx TFP APS decks -> clean, deduplicated questions.json

Each question slide = 1 intitulé + 5 options (one is always "Aucune des autres réponses").
No correct answers exist in the source files: they are supplied later via the review tool.

Usage:
    python3 tools/extract.py /path/to/downloads /path/to/AFMS/data
"""
import zipfile, re, glob, os, sys, json, unicodedata, hashlib

# ---- helpers ---------------------------------------------------------------

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def norm_key(s):
    """Normalized key for deduplication."""
    s = strip_accents(s.lower())
    s = re.sub(r'[^a-z0-9]', '', s)   # keep letters+digits only
    return s

# ---- classification par contenu vers la nomenclature officielle (Fabien) ----
# ordre = priorité (règles les plus spécifiques d'abord). Les tags des decks
# ne sont PAS fiables : on classe sur le texte (intitulé + options).
CLASSIFY_RULES = [
 (14, r'seveso|\bicpe\b|\bppi\b|\bpoi\b|\bper\b|amiante|installation class|mati[eè]re.*(toxique|dangereuse|incombustible)|industriel|plan de pr[ée]vention|orsec'),
 (9,  r'palpation|inspection.*bagage|\bbagage|magn[ée]tom[eè]tre|fouille|p[ée]rim[eè]tre de protection|manifestation sportive'),
 (7,  r'terroris|attentat|vigipirate|nrbc|explosi|grenade|radicalis|garrot|h[ée]morragie|plaie par balle|colis pi[ée]g'),
 (5,  r'incendie|\bfeu\b|extincteur|triangle du feu|comburant|combusti|\bigh\b|fum[ée]e|foyer|\bco2\b'),
 (10, r'vid[ée]o|cam[ée]ra|\bcnil\b|vid[ée]osurveillance|vid[ée]oprotection|enregistrement|\bimages?\b|t[ée]l[ée]surveillance|contr[ôo]le d.acc[eè]s|\bstad\b|\becs\b|adressable'),
 (11, r'\bdati\b|\bpti\b|\bgtb\b|\bgtc\b|groupe [ée]lectrog[eè]ne|[ée]lectrique|\bcourant\b|alarme technique|verticalit[ée]|groupe [ée]lectro'),
 (6,  r'appr[ée]hend|article 73|flagran|clameur|menott|\bvoleur\b|d[ée]gradation'),
 (12, r'[ée]v[eè]nement|rassemblement|organisateur|\bgala\b|\bfoule\b|spectateur|\bvip\b'),
 (3,  r'\bconflit|\bregard\b|communication|compromis|apais|[ée]coute|politesse|agress'),
 (4,  r'consigne|main courante|permanente|particuli[eè]re|ponctuelle|compte[- ]rendu|transmission'),
 (8,  r'\bronde|d[ée]tecteur|zone de protection|volum[ée]trique|p[ée]riph[ée]rique|convoyeur|alphabet|\bpcs\b|\btenue\b|pr[ée]sentation|lev[ée]e de doute|intrusion|vuln[ée]rable|gr[eè]ve|filtrage|liaison'),
 (2,  r'carte professionnelle|\bcnaps\b|l[ée]gitime d[ée]fense|employeur|formateur|agr[ée]ment|d[ée]ontolog|pr[ée]rogative|citoyen|infraction|contravention|\bd[ée]lit\b|\bpeine\b|amende|\bcpp\b|contrat|\bloi\b|code'),
]

# corrections orthographiques SÛRES (artefacts d'extraction : accents/apostrophes perdus,
# fautes évidentes). Appliquées après l'attribution des id (les id restent stables).
SAFE_FIX = {
 "etre":"être","Etre":"Être","etat":"état","Etat":"État","ecouter":"écouter",
 "Ecouter":"Écouter","eviter":"éviter","evite":"évite","Eviter":"Éviter",
 "equipement":"équipement","systematiquement":"systématiquement","reconnait":"reconnaît",
 "reponses":"réponses","reponse":"réponse","ongtemps":"longtemps","prévendus":"prévenus",
 "conscilliante":"conciliante","cuissor":"cuisson","maitriser":"maîtriser",
 "lalarme":"l'alarme","lagent":"l'agent","dalarme":"d'alarme","lemployeur":"l'employeur",
 "letablissement":"l'établissement","létablissement":"l'établissement","tarticle":"l'article",
 "mages":"images","payet":"payer","necéssaire":"nécessaire","dnas":"dans",
}
_FIX_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k in SAFE_FIX) + r")\b")

def apply_safe_fix(text):
    return _FIX_RE.sub(lambda m: SAFE_FIX[m.group(1)], text)

def classify_uv(intitule, options):
    text = strip_accents((intitule + " " + " ".join(options)).lower())
    for uv, pat in CLASSIFY_RULES:
        if re.search(pat, text):
            return uv
    return 8  # défaut : Professionnel (le plus large)

def clean_text(s):
    for a, b in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                 ('&quot;', '"'), ('&#39;', "'")]:
        s = s.replace(a, b)
    # normalize curly apostrophes / whitespace
    s = s.replace('’', "'").replace('‘', "'")
    s = re.sub(r'\s+', ' ', s).strip()
    return s

CHROME_RE = re.compile(
    r'^(45\s*sec|bonne\s+chance|questionnaire|une\s+seule\s+r|merci|fin\b|'
    r'correction|reponse\b|qcu\b|aucune\s+reponse\s+n)', re.I)

UVHDR_RE = re.compile(r'^\s*uv\s*0?\d+\b', re.I)   # "UV02 - JURIDIQUE  13 / 15"
OPTNUM_RE = re.compile(r'^\s*\d+\s*[.)\-:]\s+')     # "1.  ", "2) ", "3- "
COUNTER_RE = re.compile(r'\b\d{1,3}\s*/\s*\d{1,3}\b')  # "13 / 15"

def is_chrome(txt):
    t = strip_accents(txt.lower()).strip()
    if not t:
        return True
    if re.fullmatch(r'\d{1,3}', t):        # lone number = slide number / option label
        return True
    if UVHDR_RE.match(txt):                 # UV header line (UV captured separately)
        return True
    if CHROME_RE.match(t):
        return True
    return False

def para_texts_with_pos(sp_xml):
    """Return list of clean paragraph strings for one shape, in order."""
    out = []
    # soft line breaks (<a:br/>) inside a paragraph must become spaces, not glue words
    sp_xml = re.sub(r'<a:br\s*/?>', ' <a:t> </a:t>', sp_xml)
    for p in re.split(r'</a:p>', sp_xml):
        runs = re.findall(r'<a:t>(.*?)</a:t>', p, re.S)
        line = clean_text("".join(runs))
        if line:
            out.append(line)
    return out

def slide_paragraphs(xml):
    """Ordered (by shape vertical pos, then in-shape order) clean paragraphs."""
    items = []
    order = 0
    for m in re.finditer(r'<p:sp>.*?</p:sp>', xml, re.S):
        sp = m.group(0)
        off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"', sp)
        y = int(off.group(2)) if off else 0
        for para in para_texts_with_pos(sp):
            items.append((y, order, para))
            order += 1
    items.sort(key=lambda t: (t[0], t[1]))
    return [p for _, _, p in items]

UV_RE = re.compile(r'\bUV\s*[:\-]?\s*(\d+)\b', re.I)
QNUM_RE = re.compile(r'^\s*question\s*n?[°º]?\s*\d+\s*[.\-:)]?\s*', re.I)
# option "pivot" : soit « Aucune des autres réponses », soit « Toutes les réponses/propositions … »
ANCHOR_RE = re.compile(r'aucune des autres|toutes? (?:les|ces) (?:reponses|propositions)')

def _has_anchor(s):
    return bool(ANCHOR_RE.search(strip_accents(s.lower())))

def _clean_intitule(text):
    text = re.sub(r'^.{0,45}?question\s*n?[°º]?\s*\d+\s*[:.\-)]?\s*', '', text, flags=re.I)
    text = QNUM_RE.sub('', text)
    text = UV_RE.sub('', text)
    return re.sub(r'^[.\-:)\s]+', '', text).strip()

def _looks_like_stem(text):
    t = text.rstrip()
    return t.endswith('?') or t.endswith(':') or bool(re.match(r'^.{0,45}?question\s*\d+', text, re.I))

def parse_slide(paras):
    """Return dict(intitule, options[list], uv) or None if not a question slide."""
    # must contain a pivot option (Aucune… / Toutes les réponses…)
    if not any(_has_anchor(p) for p in paras):
        return None
    # UV detection on RAW paragraphs (incl. UV header line, dropped as chrome below)
    uv = None
    for p in paras:
        m = re.search(r'\buv\s*0?(\d+)\b', p, re.I)
        if m:
            uv = int(m.group(1))
            break
    clean = [p for p in paras if not is_chrome(p)]
    # strip leading option numbering + inline counters
    clean = [COUNTER_RE.sub('', OPTNUM_RE.sub('', p)).strip() for p in clean]
    clean = [p for p in clean if p]
    if len(clean) < 6:
        return None
    # défaut : les 5 dernières lignes = options ; le reste = intitulé
    options = clean[-5:]
    intitule = _clean_intitule(" ".join(clean[:-5]))
    # si l'intitulé par défaut ne ressemble pas à un énoncé (mise en page où l'intitulé
    # n'est pas en tête), on repère la ligne se terminant par « ? » ou « : »
    if not _looks_like_stem(intitule):
        qlines = [i for i, l in enumerate(clean) if re.search(r'[?:]\s*$', l)]
        if len(qlines) == 1:
            qi = qlines[0]
            cand = [l for j, l in enumerate(clean) if j != qi]
            if len(cand) == 5:
                options = cand
                intitule = _clean_intitule(clean[qi])
    # if the 5 options start with sequential 1..5, that's option numbering -> strip it
    lead = [re.match(r'^\s*(\d)\b', o) for o in options]
    if all(lead) and [m.group(1) for m in lead] == ["1","2","3","4","5"]:
        options = [re.sub(r'^\s*\d\s*[.)\-:]?\s*', '', o).strip() for o in options]
    # clean each option of a possible leading UV / question residue
    options = [UV_RE.sub('', o).strip() for o in options]
    # sanity: the pivot option must be inside the 5 options
    if not any(_has_anchor(o) for o in options):
        return None
    if not intitule:
        return None
    return {"intitule": intitule, "options": options, "uv": uv}

# ---- main ------------------------------------------------------------------

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Downloads")
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data"
    os.makedirs(out_dir, exist_ok=True)

    files = sorted(glob.glob(os.path.join(src, "*.pptx")))
    dedup = {}          # norm_key -> question record
    flagged = []        # slides that looked like questions but failed parse
    per_file = {}
    total_slides_parsed = 0

    for f in files:
        base = os.path.basename(f)
        z = zipfile.ZipFile(f)
        slides = sorted(
            [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)],
            key=lambda x: int(re.search(r'(\d+)', x.split('/')[-1]).group()))
        count = 0
        for s in slides:
            xml = z.read(s).decode('utf-8', 'ignore')
            paras = slide_paragraphs(xml)
            looks_like_q = any(_has_anchor(p) for p in paras)
            rec = parse_slide(paras)
            if rec is None:
                if looks_like_q:
                    flagged.append(f"{base}:{s.split('/')[-1]}")
                continue
            count += 1
            total_slides_parsed += 1
            k = norm_key(rec["intitule"])
            if k in dedup:
                dedup[k]["sources"].append(base)
                # keep the option variant that carries a UV tag if we lacked one
                if dedup[k]["uv"] is None and rec["uv"] is not None:
                    dedup[k]["uv"] = rec["uv"]
            else:
                qid = hashlib.md5(k.encode()).hexdigest()[:10]
                dedup[k] = {
                    "id": qid,
                    "intitule": rec["intitule"],
                    "options": rec["options"],
                    "uv": rec["uv"],
                    "sources": [base],
                }
        per_file[base] = count

    questions = list(dedup.values())
    # override deck UV tags with content-based classification (Fabien's taxonomy)
    # + safe spelling fixes (id already assigned -> stays stable)
    for q in questions:
        q["uv_deck"] = q.pop("uv", None)          # keep the raw deck tag for reference
        q["uv"] = classify_uv(q["intitule"], q["options"])
        q["intitule"] = apply_safe_fix(q["intitule"])
        q["options"] = [apply_safe_fix(o) for o in q["options"]]
    # stable order: by uv then intitulé
    questions.sort(key=lambda q: (q["uv"] if q["uv"] is not None else 99, q["intitule"]))

    out_path = os.path.join(out_dir, "questions.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(questions, fh, ensure_ascii=False, indent=1)

    # also emit a JS bundle so the app works from file:// (no fetch/CORS)
    app_dir = os.path.join(os.path.dirname(out_dir), "app")
    if os.path.isdir(app_dir):
        with open(os.path.join(app_dir, "questions.js"), "w", encoding="utf-8") as fh:
            fh.write("window.QCU_QUESTIONS = ")
            json.dump(questions, fh, ensure_ascii=False)
            fh.write(";\n")
        # create an empty answers bundle only if none exists yet
        ans_js = os.path.join(app_dir, "answers.js")
        if not os.path.exists(ans_js):
            with open(ans_js, "w", encoding="utf-8") as fh:
                fh.write("window.QCU_ANSWERS = {};\n")

    # ---- report ----
    print("=== EXTRACTION REPORT ===")
    for f, c in per_file.items():
        print(f"  {f:45s} parsed {c:3d}")
    print(f"  total slides parsed : {total_slides_parsed}")
    print(f"  UNIQUE questions    : {len(questions)}")
    uv_counts = {}
    for q in questions:
        uv_counts[q["uv"]] = uv_counts.get(q["uv"], 0) + 1
    print(f"  by UV               : {dict(sorted(uv_counts.items(), key=lambda x:(x[0] is None, x[0])))}")
    multi = sum(1 for q in questions if len(q["sources"]) > 1)
    print(f"  in >1 deck          : {multi}")
    print(f"  flagged (Q-like, unparsed): {len(flagged)}")
    for x in flagged[:25]:
        print("     !", x)
    print(f"  -> wrote {out_path}")

if __name__ == "__main__":
    main()
