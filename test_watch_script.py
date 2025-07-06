#!/usr/bin/env python3
"""
Simple test script for watch mode
"""

import time
import sys
from datetime import datetime

def main():
    print(f"🚀 Test script started at {datetime.now()}")
    print(f"📍 PID: {sys.argv[0] if len(sys.argv) > 0 else 'unknown'}")
    
    counter = 0
    while True:
        counter += 1
        print(f"⏰ Running... counter={counter} at {datetime.now().strftime('%H:%M:%S')}")
        time.sleep(2)

if __name__ == "__main__":
    main()
# Test modification dim. 06 juil. 2025 16:16:45 CEST
# Test watch mode dim. 06 juil. 2025 16:20:59 CEST
