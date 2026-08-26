# Guide formateur — mettre à jour les QCU

Ce guide explique comment **modifier les questions/réponses** et **publier** les changements
pour tous, sans aide technique. Aucune connaissance en informatique nécessaire.

Tu manipules deux liens :
- 🛠️ **Console de validation** : ⟨https://qcu-afms.netlify.app/admin.html⟩
- 📄 **Fichier des réponses sur GitHub** : ⟨https://github.com/TON-COMPTE/qcu-afms/blob/main/app/answers.js⟩

---

## 1. Modifier dans la console

Ouvre la **console de validation** (1er lien). Tu peux :

| Pour… | Faire… |
|---|---|
| **Changer la bonne réponse** | **Clique sur la réponse** correcte (elle devient verte « ✓ validé »). |
| **Corriger une faute dans le texte** | **Double-clique** sur le texte de l'intitulé ou d'une réponse, corrige, `Entrée`. |
| **Changer l'UV** | Menu déroulant « UV ». |
| **Écrire l'explication** | Champ « Justification » en bas. |
| **Ajouter une question** | Bouton **« ＋ Nouvelle question »**, puis remplis intitulé + réponses + bonne réponse. |
| **Supprimer une question** | Bouton **« Supprimer »** (récupérable via ☑ « 🗑 supprimées » → « ↩ Restaurer »). |
| **Trouver une question** | Barre 🔎 (Entrée = résultat suivant). |
| **Traiter les doublons** | ☑ « 🔁 doublons » → un bandeau propose de supprimer les variantes en double. |
| **Voir ce qui reste à vérifier** | ☑ « ⚠ à confirmer ». |

👉 Tout est **sauvegardé automatiquement** dans ton navigateur au fur et à mesure.
Travaille toujours **sur le même ordinateur / navigateur** tant que tu n'as pas exporté.

## 2. Exporter

Quand tu as fini (ou avant de t'arrêter) : clique **« Exporter answers.js »** en haut à droite.
Un fichier **`answers.js`** se télécharge (dans ton dossier *Téléchargements*).

## 3. Publier (pour que tout le monde voie tes changements)

1. Ouvre le **2e lien** (fichier des réponses sur GitHub).
2. Reviens d'un niveau sur le dossier **`app`** (clic sur « app » dans le fil d'Ariane en haut).
3. Bouton **« Add file » → « Upload files »**.
4. **Glisse** ton fichier `answers.js` téléchargé dans la zone (il remplace l'ancien, même nom).
5. En bas, bouton vert **« Commit changes »**.
6. Attends **1 à 2 minutes** : le site se met à jour tout seul. Recharge le quiz pour vérifier.

✅ C'est fait — les candidats ont maintenant tes réponses à jour.

---

### Bon à savoir
- Si tu changes d'ordinateur **avant** d'avoir exporté, tu perds les modifs non exportées.
  → Exporte régulièrement.
- Tu ne peux **rien casser** de définitif : la version publiée reste celle du dernier
  `answers.js` déposé sur GitHub. En cas de souci, on peut revenir à une version précédente
  (historique GitHub).
- Une suppression est **réversible** tant que tu ne l'as pas publiée (et même après, via
  l'historique).
