#!/bin/bash
# Script automatisé pour publier PyPM2 sur GitHub

echo "🚀 Publication automatique de PyPM2 sur GitHub"
echo "=============================================="

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "setup.py" ] || [ ! -d ".git" ]; then
  echo "❌ Erreur: Ce script doit être exécuté depuis le répertoire PyPM2"
  exit 1
fi

# Demander le nom d'utilisateur GitHub
echo ""
read -p "🔑 Entrez votre nom d'utilisateur GitHub: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
  echo "❌ Nom d'utilisateur requis"
  exit 1
fi

echo ""
echo "📋 Configuration du repository distant..."
echo "Repository: https://github.com/$GITHUB_USERNAME/pypm2.git"

# Vérifier si remote origin existe déjà
if git remote get-url origin >/dev/null 2>&1; then
  echo "⚠️  Remote 'origin' existe déjà. Suppression..."
  git remote remove origin
fi

# Ajouter le remote
echo "🔗 Ajout du remote GitHub..."
git remote add origin https://github.com/$GITHUB_USERNAME/pypm2.git

# Vérifier la connectivité (optionnel)
echo "🔍 Vérification de la connectivité..."
if ! git ls-remote origin >/dev/null 2>&1; then
  echo "⚠️  Attention: Impossible de se connecter au repository."
  echo "   Assurez-vous que:"
  echo "   1. Le repository 'pypm2' existe sur GitHub"
  echo "   2. Vous avez les droits d'accès"
  echo "   3. Votre authentification Git est configurée"
  echo ""
  read -p "Continuer quand même? (y/N): " CONTINUE
  if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
    echo "❌ Publication annulée"
    exit 1
  fi
fi

echo ""
echo "📤 Publication du code..."

# Push de la branche principale
echo "📤 Push de la branche main..."
if git push -u origin main; then
  echo "✅ Code publié avec succès!"
else
  echo "❌ Erreur lors du push de la branche main"
  exit 1
fi

# Push des tags
echo "🏷️  Push des tags..."
if git push --tags; then
  echo "✅ Tags publiés avec succès!"
else
  echo "⚠️  Erreur lors du push des tags (non critique)"
fi

echo ""
echo "🎉 Publication terminée avec succès!"
echo ""
echo "🔗 Votre repository PyPM2 est maintenant disponible à:"
echo "   https://github.com/$GITHUB_USERNAME/pypm2"
echo ""
echo "📋 Prochaines étapes recommandées:"
echo "   1. Aller sur GitHub et vérifier que tout est correct"
echo "   2. Ajouter la description: 'Production-ready process manager for Python applications, inspired by PM2'"
echo "   3. Ajouter les topics: python, process-manager, pm2, monitoring, systemd, production, cli"
echo "   4. Activer les Issues, Wiki, et Actions"
echo "   5. Configurer les règles de protection de branche"
echo ""
echo "🚀 PyPM2 v1.0.0 est maintenant public sur GitHub!"
