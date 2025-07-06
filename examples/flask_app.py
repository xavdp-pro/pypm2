#!/usr/bin/env python3
"""
Exemple d'application Flask pour tester PyPM2
"""

from flask import Flask, jsonify
import time
import os
import threading
import random

app = Flask(__name__)

# Compteur global pour simuler une activité
counter = 0
start_time = time.time()

def background_task():
    """Tâche en arrière-plan pour simuler une charge"""
    global counter
    while True:
        counter += 1
        time.sleep(1)
        
        # Simulation d'une erreur occasionnelle (1% de chance)
        if random.random() < 0.01:
            print(f"ERROR: Simulated error occurred at counter {counter}")

# Démarrer la tâche en arrière-plan
background_thread = threading.Thread(target=background_task, daemon=True)
background_thread.start()

@app.route('/')
def hello():
    return jsonify({
        "message": "Hello from PyPM2 Flask App!",
        "pid": os.getpid(),
        "counter": counter,
        "uptime": f"{time.time() - start_time:.2f} seconds"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "pid": os.getpid(),
        "counter": counter,
        "uptime": time.time() - start_time
    })

@app.route('/error')
def simulate_error():
    """Endpoint pour simuler une erreur"""
    raise Exception("Simulated error for testing!")

@app.route('/memory')
def memory_usage():
    """Endpoint pour voir l'usage mémoire"""
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return jsonify({
        "pid": os.getpid(),
        "memory_rss": f"{memory_info.rss / 1024 / 1024:.2f} MB",
        "memory_vms": f"{memory_info.vms / 1024 / 1024:.2f} MB",
        "cpu_percent": process.cpu_percent()
    })

if __name__ == '__main__':
    print(f"Starting Flask app with PID: {os.getpid()}")
    app.run(host='0.0.0.0', port=5000, debug=False)
