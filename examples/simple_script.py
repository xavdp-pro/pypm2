#!/usr/bin/env python3
"""
Script simple pour tester PyPM2
"""

import time
import os
import sys
from datetime import datetime

def main():
    print(f"Simple script started with PID: {os.getpid()}")
    print(f"Arguments: {sys.argv[1:]}")
    print(f"Environment variables:")
    
    # Afficher quelques variables d'environnement importantes
    for key in ['PATH', 'HOME', 'USER', 'CUSTOM_VAR']:
        value = os.environ.get(key, 'Not set')
        print(f"  {key}: {value}")
    
    counter = 0
    
    try:
        while True:
            counter += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Iteration {counter} - PID: {os.getpid()}")
            
            # Simulation d'une activité
            time.sleep(5)
            
            # Simulation d'un crash occasionnel (très rare)
            if counter % 100 == 0:
                print(f"Milestone reached: {counter} iterations")
                
            # Simulation d'une erreur très occasionnelle
            import random
            if random.random() < 0.001:  # 0.1% de chance
                raise Exception(f"Simulated crash at iteration {counter}")
                
    except KeyboardInterrupt:
        print(f"\nScript stopped gracefully after {counter} iterations")
    except Exception as e:
        print(f"\nScript crashed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
