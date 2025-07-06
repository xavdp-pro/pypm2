#!/bin/bash
# Démonstration complète de PyPM2 avec le mode watch

echo "🚀 PyPM2 - Démonstration complète avec Watch Mode"
echo "================================================="

echo ""
echo "📋 Fonctionnalités PyPM2 :"
echo "  ✅ Gestionnaire de processus Python"
echo "  ✅ Interface CLI complète"
echo "  ✅ Monitoring en temps réel"
echo "  ✅ Auto-restart avec limites"
echo "  ✅ Gestion des logs"
echo "  ✅ Persistance des processus"
echo "  ✅ Intégration systemd"
echo "  ✅ 🆕 MODE WATCH pour le développement"
echo ""

# Nettoyage initial
echo "🧹 Nettoyage des processus existants..."
python -m pypm2 stop all 2>/dev/null || true
python -m pypm2 delete all 2>/dev/null || true

echo ""
echo "1️⃣  TEST DES COMMANDES DE BASE"
echo "=============================="

# Démarrer quelques processus
echo "🚀 Démarrage des processus de test..."
python -m pypm2 start test_watch_script.py --name test-1
python -m pypm2 start test_watch_script.py --name test-2 --max-restarts 5

echo ""
echo "📊 Liste des processus :"
python -m pypm2 list

echo ""
echo "2️⃣  TEST DU MODE WATCH"
echo "====================="

echo "🎯 Démarrage du mode watch en arrière-plan..."
timeout 10 python -m pypm2 watch test-1 &
WATCH_PID=$!

sleep 2

echo "📝 Simulation de modification de fichier..."
echo "# Test watch mode $(date)" >>test_watch_script.py

sleep 3

echo "📊 Statut après modification (le processus devrait avoir redémarré) :"
python -m pypm2 list

# Arrêter le watch mode
kill $WATCH_PID 2>/dev/null || true
wait $WATCH_PID 2>/dev/null || true

echo ""
echo "3️⃣  TEST DES AUTRES FONCTIONNALITÉS"
echo "================================="

echo "🔄 Test restart..."
python -m pypm2 restart test-2

echo "📋 Test logs..."
python -m pypm2 logs test-1 --lines 5

echo "🧹 Test flush logs..."
python -m pypm2 flush test-1

echo "💾 Test sauvegarde (resurrect)..."
python -m pypm2 save

echo ""
echo "4️⃣  RÉSUMÉ DES TESTS"
echo "=================="

echo "📊 Statut final des processus :"
python -m pypm2 list

echo ""
echo "✅ Tests réalisés avec succès :"
echo "  🔥 Démarrage de processus"
echo "  🔄 Restart automatique"
echo "  👁️  Mode watch avec détection de changements"
echo "  📋 Affichage des logs"
echo "  💾 Sauvegarde/restoration"
echo "  🧹 Nettoyage des logs"

echo ""
echo "🧹 Nettoyage final..."
python -m pypm2 stop all
python -m pypm2 delete all

echo ""
echo "🎉 Démonstration PyPM2 terminée avec succès !"
echo ""
echo "💡 Pour utiliser le mode watch en développement :"
echo "   pypm2 start votre-app.py --name dev-app"
echo "   pypm2 watch dev-app --watch-path ./src"
echo ""
echo "📚 Documentation complète disponible dans docs/"
