# QCU TFP APS — Générateur de QCU d'entraînement

Application web qui génère des **QCU (Questionnaires à Choix Unique)** d'entraînement au
**TFP APS** (Titre à Finalité Professionnelle — Agent de Prévention et de Sécurité), à partir
d'une banque de questions extraite des supports de formation.

> Site statique, sans serveur ni base de données. Chaque visiteur génère **son propre QCU**
> (tirage aléatoire) directement dans son navigateur.

---

## 🔗 Liens

| | Lien | Pour qui |
|---|---|---|
| **Quiz** | https://afms-qcu.netlify.app/ | Les candidats / apprenants |
| **Console de validation** | https://afms-qcu.netlify.app/admin.html | Le formateur (édition des réponses) |

> ⚠️ L'URL de la console (`/admin.html`) est réservée au formateur : ne la communique pas aux candidats.

## ✨ Ce que fait l'app

- ⏱️ **45 secondes par question** (chronomètre), une seule bonne réponse, **pas de retour en arrière**.
- 🎛️ **Deux formats** : *Révision libre* (choix des UV + du nombre de questions) et
  *Examen blanc* (**99 questions**, composition officielle du TFP APS).
- 🔀 Questions posées **UV par UV**, propositions **mélangées** (1 à 5) pour éviter le par-cœur.
- ✅ **Correction immédiate** après chaque validation (bonne réponse + justification).
- 📊 **Récapitulatif par module** en fin de QCU : fautes par UV, note /20 et **validé / non validé** (seuil 12/20).
- 📄 **Export PDF** du corrigé (bonne réponse en vert, erreurs en rouge).

## 🗂️ Structure du dépôt

```
AFMS/
├── app/                  ← LE SITE (c'est ce que Netlify publie)
│   ├── index.html        ← le quiz
│   ├── admin.html        ← la console de validation (formateur)
│   ├── app.js / admin.js / styles.css
│   ├── questions.js      ← la banque de questions
│   ├── answers.js        ← ⭐ LA CLÉ DE CORRECTION (bonnes réponses) — le fichier qu'on met à jour
│   ├── dupes.js          ← groupes de doublons repérés (aide à la validation)
│   └── _headers          ← empêche le cache de figer les mises à jour (Netlify)
├── tools/                ← scripts Python (extraction, propositions, doublons) — usage ponctuel
├── data/                 ← versions JSON des données
├── netlify.toml          ← config Netlify (publie le dossier app/)
├── DEPLOIEMENT.md        ← 🚀 mise en ligne (à faire une fois)
└── GUIDE_FORMATEUR.md    ← 🔄 comment le formateur met à jour, seul
```

## 🔄 Mettre à jour les questions / réponses

Tout se fait dans la **console de validation** (`admin.html`), sans toucher au code :
clic sur la bonne réponse, double-clic pour corriger un texte, **＋ Nouvelle question**,
**Supprimer**, détection de **🔁 doublons**, recherche…

👉 Procédure complète pas-à-pas (édition → export → publication) : **[GUIDE_FORMATEUR.md](GUIDE_FORMATEUR.md)**

En résumé : *modifier dans la console → « Exporter answers.js » → déposer ce fichier sur GitHub
(dossier `app/`) → Netlify republie automatiquement en ~1 min.*

## 🚀 Déploiement (une seule fois)

GitHub + Netlify, étapes détaillées : **[DEPLOIEMENT.md](DEPLOIEMENT.md)**

## 🧠 Comment ça marche (l'essentiel)

- **Pas de serveur.** L'app tourne dans le navigateur. La « base » des bonnes réponses est le
  fichier **`app/answers.js`** — c'est le **seul** fichier à mettre à jour pour changer une
  correction, ajouter ou supprimer une question.
- **Publier une mise à jour = remplacer `app/answers.js`** sur GitHub → Netlify redéploie tout seul.
- `answers.js` peut aussi contenir des **questions ajoutées à la main** et des **suppressions**
  (`{ "deleted": true }`) : l'app en tient compte automatiquement.
- Les bonnes réponses sont dans un fichier public : visibles par qui inspecte le code source
  (normal pour un outil d'entraînement, où la correction est de toute façon affichée).

---

*Basé exclusivement sur les supports fournis et le référentiel TFP APS.*
