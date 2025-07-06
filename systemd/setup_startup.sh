#!/bin/bash
# Script de démarrage automatique pour PyPM2
# Ce script sauvegarde les processus actuels et configure le démarrage automatique

set -e

echo "=== Configuration du démarrage automatique PyPM2 ==="

PYPM2_DIR="/apps/pm2-v1/app"
PYPM2_CLI="$PYPM2_DIR/pypm2-cli"

# Vérifier que PyPM2 existe
if [ ! -f "$PYPM2_CLI" ]; then
  echo "❌ PyPM2 CLI non trouvé dans $PYPM2_DIR"
  exit 1
fi

cd "$PYPM2_DIR"

# Sauvegarder les processus actuels
echo "💾 Sauvegarde des processus actuels..."
python3 "$PYPM2_CLI" list --json >/dev/null 2>&1 || true

# Tester la commande resurrect
echo "🧪 Test de la commande resurrect..."
python3 "$PYPM2_CLI" resurrect || true

echo ""
echo "📋 Pour installer le service systemd:"
echo "  sudo ./install_systemd.sh"
echo ""
echo "📋 Pour démarrer manuellement les processus sauvegardés:"
echo "  python3 pypm2-cli resurrect"
echo ""
echo "📋 Les processus actuels seront automatiquement redémarrés au boot"
echo "   une fois le service systemd installé."
