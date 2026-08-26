#!/usr/bin/env bash
# Reconstruit toute la base à partir des PowerPoint puis régénère les propositions.
set -e
DL="${1:-$HOME/Downloads}"
cd "$(dirname "$0")"
echo "→ Extraction des .pptx depuis : $DL"
python3 tools/extract.py "$DL" data
echo "→ Génération des propositions de réponses"
python3 tools/proposals.py
echo "→ Détection des doublons"
python3 tools/dupes.py
echo "✓ Terminé. Ouvre app/index.html (quiz) ou app/admin.html (validation)."
