# Mise en ligne — GitHub + Netlify (à faire une seule fois, par Fabien)

Objectif : le quiz en ligne + des mises à jour possibles **par le formateur, sans toi**.

Résultat : le formateur exporte `answers.js` depuis la console, le dépose sur GitHub,
et Netlify **republie tout seul** en ~1 minute.

---

## Étape 1 — Mettre le projet sur GitHub

1. Crée un compte sur **github.com** (gratuit).
2. **New repository** → nom `qcu-afms` (peut être **Privé**, ça marche quand même avec Netlify).
3. Envoie le projet. Deux façons :
   - **Simple (souris) :** installe **GitHub Desktop** (desktop.github.com) → *Add local repository* →
     choisis le dossier `AFMS` → *Publish repository*.
   - **Terminal (git) :** dans le dossier `AFMS` :
     ```bash
     git init
     git add .
     git commit -m "QCU TFP APS"
     git branch -M main
     git remote add origin https://github.com/TON-COMPTE/qcu-afms.git
     git push -u origin main
     ```

Le fichier `netlify.toml` (déjà présent) dit à Netlify de publier le dossier `app/`.

## Étape 2 — Brancher Netlify

1. Va sur **app.netlify.com** → connecte-toi avec GitHub.
2. **Add new site → Import an existing project → GitHub** → choisis `qcu-afms`.
3. Netlify lit `netlify.toml` tout seul (dossier publié = `app`). Clique **Deploy**.
4. Tu obtiens une URL, ex. `https://qcu-afms.netlify.app`.
   - **Quiz (candidats) :** `https://qcu-afms.netlify.app`
   - **Console de validation (formateur) :** `https://qcu-afms.netlify.app/admin.html`
   *(URL discrète : elle n'est liée nulle part depuis le quiz.)*

## Étape 3 — Préparer le formateur

1. Ouvre le fichier **[GUIDE_FORMATEUR.md](GUIDE_FORMATEUR.md)**, remplace les `⟨…⟩` par tes vrais liens :
   - lien de la console : `https://qcu-afms.netlify.app/admin.html`
   - lien du fichier réponses sur GitHub :
     `https://github.com/TON-COMPTE/qcu-afms/blob/main/app/answers.js`
2. Donne ce guide au formateur + accès au repo GitHub :
   sur GitHub → repo → **Settings → Collaborators → Add people** (avec son compte GitHub).

C'est tout. À chaque mise à jour du formateur, Netlify republie automatiquement.

---

## Mot de passe de la console formateur

La console `admin.html` est protégée par un **mot de passe** (verrou côté navigateur).
- **Mot de passe par défaut : `afms-formateur`** — donne-le au formateur, et **change-le**.
- **Pour le changer :** ouvre `…/admin-setup.html`, tape ton nouveau mot de passe, copie la
  ligne obtenue, remplace la ligne dans `app/admin-config.js`, puis republie (dépose
  `admin-config.js` sur GitHub). Le mot de passe n'est jamais stocké en clair (haché SHA-256).
- ⚠️ C'est un verrou « anti-curieux », pas une sécurité inviolable. La vraie protection des
  données reste ton compte GitHub (seul lui peut publier une mise à jour).

## Notes importantes
- Le fichier `app/_headers` empêche le cache de figer les mises à jour (les visiteurs voient
  toujours la dernière version des réponses).
- `app/answers.js` porte un en-tête « VALIDÉ » : ne relance **pas** `tools/proposals.py`
  dessus (il refuse de lui-même, sauf `--force`).
- Les bonnes réponses sont dans un fichier public (`answers.js`) : visibles par qui inspecte
  le code source. Normal pour un outil d'entraînement.
