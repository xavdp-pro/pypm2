# Guide d'utilisation avancée de PyPM2

## Exemples d'utilisation

### 1. Application web Django
```bash
# Démarrer une application Django
pypm2 start manage.py --name django-app --args runserver 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=myproject.settings.production

# Avec plusieurs workers
pypm2 start manage.py --name django-app-1 --args runserver 0.0.0.0:8001
pypm2 start manage.py --name django-app-2 --args runserver 0.0.0.0:8002
pypm2 start manage.py --name django-app-3 --args runserver 0.0.0.0:8003
```

### 2. Worker Celery
```bash
# Démarrer un worker Celery
pypm2 start celery --name celery-worker --args worker --loglevel=info --env CELERY_BROKER_URL=redis://localhost:6379

# Worker avec limite de mémoire
pypm2 start celery --name celery-worker --args worker --max-memory-restart 512M
```

### 3. Script de monitoring
```python
# monitoring_script.py
import psutil
import time
import json
from datetime import datetime

while True:
    stats = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
    
    print(json.dumps(stats))
    time.sleep(30)
```

```bash
pypm2 start monitoring_script.py --name system-monitor
```

### 4. API REST avec FastAPI
```python
# api_server.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from PyPM2 FastAPI!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
pypm2 start api_server.py --name fastapi-server --max-memory-restart 1G
```

### 5. Scraper web avec gestion d'erreurs
```python
# web_scraper.py
import requests
import time
import random
from datetime import datetime

def scrape_data():
    try:
        response = requests.get("https://api.github.com/users/octocat")
        data = response.json()
        print(f"[{datetime.now()}] Scraped: {data['login']}")
        
        # Simulation d'erreur réseau occasionnelle
        if random.random() < 0.1:
            raise requests.RequestException("Network error simulation")
            
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")
        time.sleep(5)

while True:
    scrape_data()
    time.sleep(60)  # Scrape every minute
```

```bash
pypm2 start web_scraper.py --name github-scraper --max-restarts 5 --restart-delay 2000
```

## Commandes utiles

### Gestion groupée
```bash
# Redémarrer tous les processus
pypm2 restart all

# Arrêter tous les processus
pypm2 stop all

# Supprimer tous les processus
pypm2 delete all
```

### Monitoring et logs
```bash
# Suivre les logs en temps réel
pypm2 logs myapp --follow

# Afficher les 100 dernières lignes de logs
pypm2 logs myapp --lines 100

# Vider tous les logs
pypm2 flush

# Monitoring en temps réel
pypm2 monit
```

### Configuration avancée
```bash
# Démarrer avec un interpréteur spécifique
pypm2 start app.py --interpreter python3.9

# Démarrer dans un répertoire spécifique
pypm2 start app.py --cwd /path/to/project

# Démarrer avec variables d'environnement
pypm2 start app.py --env DATABASE_URL=postgresql://... SECRET_KEY=...

# Désactiver le redémarrage automatique
pypm2 start app.py --no-autorestart

# Limiter les redémarrages
pypm2 start app.py --max-restarts 3
```

## Intégration avec systemd

Pour que PyPM2 démarre automatiquement au boot du système :

1. Créer un service systemd :
```bash
sudo nano /etc/systemd/system/pypm2.service
```

2. Contenu du fichier service :
```ini
[Unit]
Description=PyPM2 Process Manager
After=network.target

[Service]
Type=forking
User=your-username
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/pypm2 start ecosystem.json
ExecStop=/path/to/venv/bin/pypm2 stop all
ExecReload=/path/to/venv/bin/pypm2 restart all
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Activer le service :
```bash
sudo systemctl enable pypm2
sudo systemctl start pypm2
```

## Configuration via fichier JSON

Créer un fichier `ecosystem.json` pour définir plusieurs applications :

```json
{
  "apps": [
    {
      "name": "web-api",
      "script": "api.py",
      "cwd": "/var/www/myapp",
      "interpreter": "python3",
      "env": {
        "NODE_ENV": "production",
        "DATABASE_URL": "postgresql://..."
      },
      "max_restarts": 10,
      "max_memory_restart": "1G"
    },
    {
      "name": "worker",
      "script": "worker.py",
      "cwd": "/var/www/myapp",
      "interpreter": "python3",
      "args": ["--queue", "default"],
      "instances": 3,
      "max_restarts": 5
    }
  ]
}
```

## Bonnes pratiques

### 1. Logging
- Utilisez des logs structurés (JSON) pour faciliter l'analyse
- Implémentez la rotation des logs pour éviter de remplir le disque
- Séparez les logs d'application des logs d'erreur

### 2. Monitoring
- Surveillez l'utilisation mémoire avec `--max-memory-restart`
- Limitez les redémarrages avec `--max-restarts`
- Utilisez des délais de redémarrage appropriés avec `--restart-delay`

### 3. Sécurité
- Exécutez les processus avec des utilisateurs non-privilégiés
- Utilisez des variables d'environnement pour les secrets
- Isolez les applications dans des environnements virtuels

### 4. Performance
- Ajustez le nombre d'instances selon la charge
- Surveillez les métriques système avec `pypm2 monit`
- Optimisez les ressources pour éviter les redémarrages fréquents

## Dépannage

### Problèmes courants

1. **Processus qui ne démarre pas**
   ```bash
   pypm2 logs myapp --lines 50
   ```

2. **Redémarrages fréquents**
   ```bash
   pypm2 list  # Vérifier le nombre de redémarrages
   pypm2 logs myapp --lines 100  # Chercher les erreurs
   ```

3. **Consommation mémoire élevée**
   ```bash
   pypm2 list  # Vérifier l'utilisation mémoire
   pypm2 monit  # Surveillance en temps réel
   ```

4. **Problèmes de permissions**
   ```bash
   ls -la ~/.pypm2/
   chmod 755 ~/.pypm2/
   chmod 644 ~/.pypm2/config.json
   ```

### 9. Mode Watch pour le développement

Le mode watch permet de surveiller les changements de fichiers et de redémarrer automatiquement les processus. Idéal pour le développement !

#### Utilisation basique
```bash
# Démarrer une application
pypm2 start app.py --name dev-app

# Activer le mode watch (surveille le répertoire du script par défaut)
pypm2 watch dev-app
```

#### Surveillance de répertoires spécifiques
```bash
# Surveiller plusieurs répertoires
pypm2 watch dev-app --watch-path ./src ./config ./templates

# Surveiller tout le projet
pypm2 watch dev-app --watch-path .
```

#### Exemple complet avec FastAPI
```bash
# 1. Démarrer l'application FastAPI
pypm2 start fastapi_server.py --name fastapi-dev

# 2. Activer le watch mode dans un autre terminal
pypm2 watch fastapi-dev --watch-path .

# 3. Modifier fastapi_server.py -> restart automatique !
```

#### Fichiers surveillés
Le mode watch surveille automatiquement :
- ✅ **Fichiers Python** (`.py`, `.pyx`)
- ✅ **Fichiers de configuration** (`.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`)
- ❌ **Fichiers ignorés** (`.log`, `.tmp`, `.pyc`, `__pycache__`, `.git`)

#### Fonctionnalités du watch mode
- 🔄 **Restart automatique** lors de changements
- ⏱️ **Debouncing** (évite les restarts multiples)
- 👁️ **Surveillance récursive** des sous-répertoires
- 🚫 **Filtrage intelligent** des fichiers temporaires
- 💡 **Messages informatifs** sur les changements détectés
