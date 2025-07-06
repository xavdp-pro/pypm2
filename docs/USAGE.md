# PyPM2 Advanced Usage Guide

## Usage Examples

### 1. Django Web Application
```bash
# Start a Django application
pypm2 start manage.py --name django-app --args runserver 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=myproject.settings.production

# With multiple workers
pypm2 start manage.py --name django-app-1 --args runserver 0.0.0.0:8001
pypm2 start manage.py --name django-app-2 --args runserver 0.0.0.0:8002
pypm2 start manage.py --name django-app-3 --args runserver 0.0.0.0:8003
```

### 2. Celery Worker
```bash
# Start a Celery worker
pypm2 start celery --name celery-worker --args worker --loglevel=info --env CELERY_BROKER_URL=redis://localhost:6379

# Worker with memory limit
pypm2 start celery --name celery-worker --args worker --max-memory-restart 512M
```

### 3. Monitoring Script
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

### 4. REST API with FastAPI
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

### 5. Web scraper with error handling
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
        
        # Occasional network error simulation
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

## Useful Commands

### Batch Management
```bash
# Restart all processes
pypm2 restart all

# Stop all processes
pypm2 stop all

# Delete all processes
pypm2 delete all
```

### Monitoring and Logs
```bash
# Follow logs in real-time
pypm2 logs myapp --follow

# Show last 100 log lines
pypm2 logs myapp --lines 100

# Clear all logs
pypm2 flush

# Real-time monitoring
pypm2 monit
```

### Advanced Configuration
```bash
# Start with specific interpreter
pypm2 start app.py --interpreter python3.9

# Start in specific directory
pypm2 start app.py --cwd /path/to/project

# Start with environment variables
pypm2 start app.py --env DATABASE_URL=postgresql://... SECRET_KEY=...

# Disable auto-restart
pypm2 start app.py --no-autorestart

# Limit restarts
pypm2 start app.py --max-restarts 3
```

## Systemd Integration

To make PyPM2 start automatically at system boot:

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

## Best Practices

### 1. Logging
- Use structured logs (JSON) to facilitate analysis
- Implement log rotation to avoid filling disk space
- Separate application logs from error logs

### 2. Monitoring
- Monitor memory usage with `--max-memory-restart`
- Limit restarts with `--max-restarts`
- Use appropriate restart delays with `--restart-delay`

### 3. Security
- Run processes with non-privileged users
- Use environment variables for secrets
- Isolate applications in virtual environments

### 4. Performance
- Adjust number of instances according to load
- Monitor system metrics with `pypm2 monit`
- Optimize resources to avoid frequent restarts

## Troubleshooting

### Common Issues

1. **Process won't start**
   ```bash
   pypm2 logs myapp --lines 50
   ```

2. **Frequent restarts**
   ```bash
   pypm2 list  # Check restart count
   pypm2 logs myapp --lines 100  # Look for errors
   ```

3. **High memory consumption**
   ```bash
   pypm2 list  # Check memory usage
   pypm2 monit  # Real-time monitoring
   ```

4. **Permission issues**
   ```bash
   ls -la ~/.pypm2/
   chmod 755 ~/.pypm2/
   chmod 644 ~/.pypm2/config.json
   ```

### 9. Watch Mode for Development

Watch mode allows monitoring file changes and automatically restarting processes. Perfect for development!

#### Basic Usage
```bash
# Start an application
pypm2 start app.py --name dev-app

# Enable watch mode (monitors script directory by default)
pypm2 watch dev-app
```

#### Monitoring Specific Directories
```bash
# Monitor multiple directories
pypm2 watch dev-app --watch-path ./src ./config ./templates

# Monitor entire project
pypm2 watch dev-app --watch-path .
```

#### Complete Example with FastAPI
```bash
# 1. Start FastAPI application
pypm2 start fastapi_server.py --name fastapi-dev

# 2. Enable watch mode in another terminal
pypm2 watch fastapi-dev --watch-path .

# 3. Modify fastapi_server.py -> automatic restart!
```

#### Monitored Files
Watch mode automatically monitors:
- ✅ **Python files** (`.py`, `.pyx`)
- ✅ **Configuration files** (`.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`)
- ❌ **Ignored files** (`.log`, `.tmp`, `.pyc`, `__pycache__`, `.git`)

#### Watch Mode Features
- 🔄 **Automatic restart** on changes
- ⏱️ **Debouncing** (avoids multiple restarts)
- 👁️ **Recursive monitoring** of subdirectories
- 🚫 **Smart filtering** of temporary files
- 💡 **Informative messages** about detected changes
