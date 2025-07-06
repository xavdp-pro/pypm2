# PyPM2 - Process Manager for Python Applications

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](tests/)

PyPM2 is a **production-ready process manager** for Python applications, inspired by PM2 for Node.js. It provides comprehensive process management capabilities including monitoring, automatic restarts, log management, and systemd integration.

![PyPM2 Demo](https://img.shields.io/badge/demo-available-brightgreen.svg)

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/pypm2/pypm2.git
cd pypm2
./install.sh

# Start managing your Python processes
pypm2 start app.py --name myapp
pypm2 list
pypm2 logs myapp
```

## ✨ Features

- ✅ **Process Lifecycle Management**: Start, stop, restart, and delete processes
- ✅ **Automatic Restart**: Restart processes on crashes with configurable limits  
- ✅ **Resource Monitoring**: Real-time CPU and memory usage tracking
- ✅ **Log Management**: Centralized logging with automatic rotation
- ✅ **Memory Limits**: Automatic restart when memory usage exceeds limits
- ✅ **Environment Variables**: Support for custom environment variables
- ✅ **Systemd Integration**: Automatic startup on system boot
- ✅ **CLI Interface**: Intuitive command-line interface similar to PM2
- ✅ **Persistence**: Process configurations survive system restarts
- ✅ **Multi-interpreter Support**: Support for different Python interpreters

## Fonctionnalités

- ✅ **Gestion des processus** : Démarrer, arrêter, redémarrer des processus Python
- ✅ **Surveillance automatique** : Redémarrage automatique en cas de crash
- ✅ **Gestion des logs** : Logs centralisés avec rotation
- ✅ **Monitoring en temps réel** : Surveillance CPU, mémoire, uptime
- ✅ **Interface en ligne de commande** : CLI similaire à PM2
- ✅ **Persistance** : Les processus survivent aux redémarrages du système
- ✅ **Limites de mémoire** : Redémarrage automatique si la mémoire dépasse une limite
- ✅ **Variables d'environnement** : Support des variables d'environnement personnalisées

## Installation

```bash
pip install pypm2
```

Ou depuis les sources :

```bash
git clone https://github.com/pypm2/pypm2.git
cd pypm2
pip install -e .
```

## Utilisation

### Démarrer une application

```bash
# Démarrer un script simple
pypm2 start app.py

# Démarrer avec un nom personnalisé
pypm2 start app.py --name myapp

# Démarrer avec des arguments
pypm2 start app.py --name myapp --args arg1 arg2

# Démarrer avec un interpréteur spécifique
pypm2 start app.py --interpreter python3.9

# Démarrer avec des variables d'environnement
pypm2 start app.py --env NODE_ENV=production DEBUG=true

# Démarrer avec une limite de mémoire
pypm2 start app.py --max-memory-restart 1G
```

### Gestion des processus

```bash
# Lister tous les processus
pypm2 list

# Arrêter un processus
pypm2 stop myapp

# Redémarrer un processus
pypm2 restart myapp

# Arrêter tous les processus
pypm2 stop all

# Redémarrer tous les processus
pypm2 restart all

# Supprimer un processus
pypm2 delete myapp

# Supprimer tous les processus
pypm2 delete all
```

### Logs et monitoring

```bash
# Voir les logs d'un processus
pypm2 logs myapp

# Suivre les logs en temps réel
pypm2 logs myapp --follow

# Voir les dernières 50 lignes
pypm2 logs myapp --lines 50

# Vider les logs
pypm2 flush myapp

# Vider tous les logs
pypm2 flush

# Monitoring en temps réel
pypm2 monit
```

### Exemples d'applications

#### Application Flask simple

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from PyPM2!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

```bash
pypm2 start app.py --name flask-app
```

#### Worker avec gestion d'erreurs

```python
# worker.py
import time
import random

def main():
    print("Worker started")
    while True:
        try:
            # Simulation de travail
            print(f"Processing task at {time.time()}")
            time.sleep(5)
            
            # Simulation d'erreur occasionnelle
            if random.random() < 0.1:
                raise Exception("Random error occurred")
                
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
```

```bash
pypm2 start worker.py --name background-worker --max-restarts 5
```

## Configuration avancée

### Options de démarrage

- `--name` : Nom du processus
- `--cwd` : Répertoire de travail
- `--interpreter` : Interpréteur Python à utiliser
- `--args` : Arguments à passer au script
- `--env` : Variables d'environnement (format KEY=VALUE)
- `--max-restarts` : Nombre maximum de redémarrages (défaut: 10)
- `--restart-delay` : Délai avant redémarrage en ms (défaut: 1000)
- `--no-autorestart` : Désactiver le redémarrage automatique
- `--max-memory-restart` : Limite de mémoire (ex: 1G, 512M)

### Structure des fichiers

PyPM2 stocke ses données dans `~/.pypm2/` :

```
~/.pypm2/
├── config.json          # Configuration globale
├── processes.json       # Configuration des processus
├── logs/               # Logs des applications
│   ├── myapp.log
│   └── myapp.error.log
└── pids/               # Fichiers PID
    └── myapp.pid
```

## API Python

Vous pouvez également utiliser PyPM2 directement dans votre code Python :

```python
from pypm2 import ProcessManager

# Créer un gestionnaire de processus
pm = ProcessManager()

# Démarrer un processus
pm.start('myapp', 'app.py', interpreter='python3')

# Lister les processus
processes = pm.list()

# Arrêter un processus
pm.stop('myapp')
```

## Comparaison avec PM2

| Fonctionnalité | PM2 (Node.js) | PyPM2 (Python) |
|----------------|---------------|-----------------|
| Démarrage de processus | ✅ | ✅ |
| Redémarrage automatique | ✅ | ✅ |
| Gestion des logs | ✅ | ✅ |
| Monitoring | ✅ | ✅ |
| Cluster mode | ✅ | ⚠️ (à venir) |
| Watch mode | ✅ | ⚠️ (à venir) |
| Déploiement | ✅ | ⚠️ (à venir) |

## Développement

### Prérequis

- Python 3.7+
- psutil
- tabulate

### Installation pour le développement

```bash
git clone https://github.com/pypm2/pypm2.git
cd pypm2
pip install -e .[dev]
```

### Tests

```bash
pytest
```

### Formatage du code

```bash
black pypm2/
```

## Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

## Licence

MIT License. Voir [LICENSE](LICENSE) pour plus de détails.

## Support

- GitHub Issues : [https://github.com/pypm2/pypm2/issues](https://github.com/pypm2/pypm2/issues)
- Documentation : [https://pypm2.readthedocs.io](https://pypm2.readthedocs.io)

## Roadmap

- [ ] Cluster mode (multiple instances)
- [ ] Watch mode (redémarrage sur changement de fichier)
- [ ] Interface web de monitoring
- [ ] Support Docker
- [ ] Intégration systemd
- [ ] Métriques Prometheus
- [ ] Configuration YAML/JSON
