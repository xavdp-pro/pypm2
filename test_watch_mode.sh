#!/bin/bash
"""
Test automatisé du watch mode PyPM2
"""

echo "🎯 Test du mode watch PyPM2"
echo "============================"

# Démarrer en arrière-plan le watch mode
echo "🚀 Démarrage du watch mode en arrière-plan..."
python -m pypm2 watch test-watch &
WATCH_PID=$!

sleep 2

echo "📝 Modification du fichier de test..."
# Ajouter un commentaire au fichier pour déclencher le restart
echo "# Test modification $(date)" >> test_watch_script.py

sleep 3

echo "📊 Statut des processus après modification:"
python -m pypm2 list

sleep 2

# Arrêter le watch mode
echo "🛑 Arrêt du watch mode..."
kill $WATCH_PID 2>/dev/null

# Nettoyer le processus de test
echo "🧹 Nettoyage..."
python -m pypm2 stop test-watch

echo "✅ Test du watch mode terminé !"
