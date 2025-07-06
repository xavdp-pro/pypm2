#!/usr/bin/env python3
"""
Exemple de worker en arrière-plan pour tester PyPM2
"""

import time
import random
import os
import json
from datetime import datetime

class BackgroundWorker:
    def __init__(self):
        self.tasks_processed = 0
        self.start_time = datetime.now()
        self.running = True
        
    def process_task(self, task_id):
        """Simule le traitement d'une tâche"""
        print(f"[{datetime.now()}] Processing task {task_id}")
        
        # Simulation d'un travail qui prend du temps
        processing_time = random.uniform(1, 3)
        time.sleep(processing_time)
        
        # Simulation d'une erreur occasionnelle (5% de chance)
        if random.random() < 0.05:
            raise Exception(f"Failed to process task {task_id}")
        
        self.tasks_processed += 1
        print(f"[{datetime.now()}] Task {task_id} completed in {processing_time:.2f}s")
        
    def save_stats(self):
        """Sauvegarde les statistiques"""
        stats = {
            "pid": os.getpid(),
            "start_time": self.start_time.isoformat(),
            "tasks_processed": self.tasks_processed,
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
        
        with open(f"/tmp/worker_{os.getpid()}_stats.json", "w") as f:
            json.dump(stats, f, indent=2)
    
    def run(self):
        """Boucle principale du worker"""
        print(f"Worker started with PID: {os.getpid()}")
        
        task_id = 1
        
        try:
            while self.running:
                try:
                    self.process_task(task_id)
                    task_id += 1
                    
                    # Sauvegarde des stats toutes les 10 tâches
                    if self.tasks_processed % 10 == 0:
                        self.save_stats()
                        print(f"Stats saved. Total tasks processed: {self.tasks_processed}")
                    
                    # Attente avant la prochaine tâche
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    print(f"[{datetime.now()}] ERROR: {e}")
                    time.sleep(2)  # Attente avant de reprendre
                    
        except KeyboardInterrupt:
            print("\nWorker stopping gracefully...")
            self.running = False
            self.save_stats()
            print("Final stats saved.")

if __name__ == '__main__':
    worker = BackgroundWorker()
    worker.run()
