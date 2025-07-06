#!/bin/bash
# Démonstration du watch mode PyPM2 avec FastAPI

echo "🚀 Démonstration du Watch Mode PyPM2"
echo "====================================="

# Copier l'exemple FastAPI dans notre répertoire
cp -r ../test-fastapi/* .

echo "📦 Démarrage de l'application FastAPI avec PyPM2..."
python -m pypm2 start fastapi_server.py --name fastapi-watch

echo "⏰ Attente du démarrage (3 secondes)..."
sleep 3

echo "📊 Statut initial:"
python -m pypm2 list

echo ""
echo "🌐 Test de l'application:"
curl -s http://localhost:8000/ | jq '.' 2>/dev/null || curl -s http://localhost:8000/

echo ""
echo "🎯 Démarrage du watch mode..."
echo "💡 Dans un autre terminal, vous pouvez :"
echo "   - Modifier fastapi_server.py"
echo "   - Voir le restart automatique"
echo "   - Tester avec: curl http://localhost:8000/"
echo ""
echo "⚠️  Appuyez sur Ctrl+C pour arrêter le watch mode"
echo ""

# Démarrer le watch mode (sera interrompu par Ctrl+C)
python -m pypm2 watch fastapi-watch --watch-path .

echo ""
echo "🧹 Nettoyage final..."
python -m pypm2 stop fastapi-watch
python -m pypm2 delete fastapi-watch

echo "✅ Démonstration terminée !"
