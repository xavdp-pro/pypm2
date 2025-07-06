#!/bin/bash
# Script de désinstallation du service systemd PyPM2

set -e

echo "=== Désinstallation PyPM2 Systemd Service ==="

# Vérifier les privilèges root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Ce script doit être exécuté avec sudo"
  exit 1
fi

SERVICE_NAME="pypm2"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_FILE="$SYSTEMD_DIR/pypm2.service"

# Arrêter le service s'il est en cours
echo "🛑 Arrêt du service PyPM2..."
systemctl stop $SERVICE_NAME 2>/dev/null || true

# Désactiver le service
echo "❌ Désactivation du service PyPM2..."
systemctl disable $SERVICE_NAME 2>/dev/null || true

# Supprimer le fichier service
if [ -f "$SERVICE_FILE" ]; then
  echo "🗑️ Suppression du fichier service..."
  rm -f "$SERVICE_FILE"
fi

# Recharger systemd
echo "🔄 Rechargement de systemd..."
systemctl daemon-reload

echo ""
echo "✅ Désinstallation terminée avec succès !"
echo ""
echo "Le service PyPM2 a été complètement supprimé du système."
echo "Les processus PyPM2 en cours continuent de fonctionner."
