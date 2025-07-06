#!/bin/bash
# Script d'installation PyPM2 pour systemd
# Usage: sudo ./install_systemd.sh

set -e

echo "=== Installation PyPM2 Systemd Service ==="

# Vérifier les privilèges root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Ce script doit être exécuté avec sudo"
  exit 1
fi

# Variables
SERVICE_NAME="pypm2"
SERVICE_FILE="pypm2.service"
SYSTEMD_DIR="/etc/systemd/system"
CONFIG_FILE="/etc/default/pypm2"

# Charger la configuration
echo "⚙️  Chargement de la configuration depuis $CONFIG_FILE"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Fichier de configuration $CONFIG_FILE manquant"
  exit 1
fi
source "$CONFIG_FILE"

# Vérifier que PyPM2 existe
if [ ! -f "$PYPM2_PATH/pypm2/__main__.py" ]; then
  echo "❌ Installation PyPM2 non trouvée dans $PYPM2_PATH"
  exit 1
fi

# Copier le fichier service
echo "📋 Copie du service systemd..."
cp "$PYPM2_PATH/$SERVICE_FILE" "$SYSTEMD_DIR/"
chmod 644 "$SYSTEMD_DIR/$SERVICE_FILE"

# Recharger systemd
echo "🔄 Rechargement de systemd..."
systemctl daemon-reload

# Activer le service
echo "✅ Activation du service PyPM2..."
systemctl enable $SERVICE_NAME

echo ""
echo "🎉 Installation terminée avec succès !"
echo ""
echo "Commandes utiles:"
echo "  sudo systemctl start pypm2     # Démarrer PyPM2"
echo "  sudo systemctl stop pypm2      # Arrêter PyPM2"
echo "  sudo systemctl restart pypm2   # Redémarrer PyPM2"
echo "  sudo systemctl status pypm2    # Voir le statut"
echo "  sudo systemctl logs pypm2      # Voir les logs"
echo "  sudo systemctl disable pypm2   # Désactiver le démarrage auto"
echo ""
echo "Pour démarrer PyPM2 maintenant:"
echo "  sudo systemctl start pypm2"
