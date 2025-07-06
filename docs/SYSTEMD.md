# PyPM2 Systemd Integration

## Vue d'ensemble

PyPM2 peut être configuré pour démarrer automatiquement au boot de la machine en utilisant systemd. Cela garantit que tous vos processus gérés par PyPM2 seront automatiquement relancés après un redémarrage.

## Installation du Service Systemd

### 1. Configuration du démarrage automatique

```bash
# Configurer PyPM2 pour le démarrage automatique
./setup_startup.sh
```

### 2. Installation du service systemd

```bash
# Installer le service systemd (nécessite les privilèges root)
sudo ./install_systemd.sh
```

### 3. Démarrer le service

```bash
# Démarrer PyPM2 maintenant
sudo systemctl start pypm2

# Vérifier le statut
sudo systemctl status pypm2
```

## Utilisation

### Commandes Systemd

```bash
# Démarrer PyPM2
sudo systemctl start pypm2

# Arrêter PyPM2
sudo systemctl stop pypm2

# Redémarrer PyPM2
sudo systemctl restart pypm2

# Voir le statut
sudo systemctl status pypm2

# Voir les logs
sudo journalctl -u pypm2 -f

# Désactiver le démarrage automatique
sudo systemctl disable pypm2
```

### Commande Resurrect

PyPM2 inclut une commande `resurrect` qui redémarre tous les processus sauvegardés :

```bash
# Redémarrer tous les processus sauvegardés
python3 pypm2-cli resurrect
```

Cette commande :
- Charge tous les processus sauvegardés depuis la configuration
- Vérifie s'ils sont déjà en cours d'exécution
- Redémarre uniquement les processus arrêtés
- Préserve tous les paramètres (arguments, variables d'environnement, etc.)

## Configuration du Service

Le service systemd est configuré dans `/etc/systemd/system/pypm2.service` :

```ini
[Unit]
Description=PyPM2 Process Manager
Documentation=https://github.com/pypm2/pypm2
After=network.target
Wants=network.target

[Service]
Type=forking
User=root
Group=root
WorkingDirectory=/apps/pm2-v1/app
Environment=PATH=/apps/pm2-v1/app/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=VIRTUAL_ENV=/apps/pm2-v1/app/.venv
Environment=PYTHONPATH=/apps/pm2-v1/app
ExecStart=/apps/pm2-v1/app/.venv/bin/python /apps/pm2-v1/app/pypm2-cli resurrect
ExecReload=/apps/pm2-v1/app/.venv/bin/python /apps/pm2-v1/app/pypm2-cli reload all
ExecStop=/apps/pm2-v1/app/.venv/bin/python /apps/pm2-v1/app/pypm2-cli stop all
PIDFile=/apps/pm2-v1/app/.pypm2/daemon.pid
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

## Flux de Démarrage Automatique

1. **Au démarrage de la machine** :
   - systemd démarre le service `pypm2`
   - Le service exécute `pypm2-cli resurrect`
   - Tous les processus sauvegardés sont redémarrés

2. **Sauvegarde automatique** :
   - PyPM2 sauvegarde automatiquement l'état des processus
   - Les configurations incluent tous les paramètres de démarrage
   - La sauvegarde est mise à jour à chaque changement

3. **Redémarrage après crash** :
   - systemd redémarre automatiquement PyPM2 en cas d'arrêt inattendu
   - Limite de 3 tentatives en 60 secondes
   - Délai de 10 secondes entre les tentatives

## Dépannage

### Vérifier les logs

```bash
# Logs du service systemd
sudo journalctl -u pypm2 -f

# Logs des processus PyPM2
python3 pypm2-cli logs <process-name>

# Statut détaillé du service
sudo systemctl status pypm2 -l
```

### Problèmes courants

1. **Service ne démarre pas** :
   ```bash
   # Vérifier la configuration
   sudo systemctl daemon-reload
   sudo systemctl start pypm2
   ```

2. **Processus ne se lancent pas** :
   ```bash
   # Tester manuellement
   python3 pypm2-cli resurrect
   python3 pypm2-cli list
   ```

3. **Permissions insuffisantes** :
   ```bash
   # Vérifier les permissions du répertoire PyPM2
   ls -la /apps/pm2-v1/app/
   ```

## Désinstallation

Pour supprimer complètement le service systemd :

```bash
# Désinstaller le service
sudo ./uninstall_systemd.sh
```

Cette commande :
- Arrête le service
- Désactive le démarrage automatique
- Supprime le fichier service
- Recharge la configuration systemd

## Exemples d'utilisation

### Configuration d'un serveur web

```bash
# Démarrer un serveur FastAPI
python3 pypm2-cli start myapp.py --name webapp --interpreter /path/to/python

# Installer le démarrage automatique
sudo ./install_systemd.sh

# Le serveur redémarrera automatiquement au boot
```

### Surveillance des services

```bash
# Surveiller en temps réel
sudo journalctl -u pypm2 -f

# Vérifier tous les processus
python3 pypm2-cli list

# Redémarrer manuellement si nécessaire
python3 pypm2-cli resurrect
```

## Sécurité

- Le service fonctionne avec les privilèges root par défaut
- Modifiez l'utilisateur dans le fichier service si nécessaire
- Assurez-vous que les scripts PyPM2 ont les bonnes permissions
- Les logs sont accessibles via journalctl avec les privilèges appropriés
