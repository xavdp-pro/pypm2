#!/usr/bin/env python3
"""
Advanced Background Worker Example for PyPM2
This example demonstrates a robust background worker that processes tasks
from a queue and can be managed by PyPM2.
"""

import os
import time
import json
import signal
import logging
import threading
from datetime import datetime
from typing import Dict, Any, List
from queue import Queue, Empty
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskProcessor:
    """Background task processor that can handle various types of tasks"""
    
    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or f"worker_{os.getpid()}"
        self.task_queue = Queue()
        self.running = False
        self.processed_tasks = 0
        self.failed_tasks = 0
        self.start_time = time.time()
        self.last_task_time = None
        
        # Statistics
        self.stats = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "uptime_seconds": 0,
            "average_task_time": 0,
            "last_task_time": None
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info(f"TaskProcessor {self.worker_id} initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()

    def add_task(self, task_type: str, data: Dict[str, Any]) -> None:
        """Add a task to the processing queue"""
        task = {
            "id": f"task_{int(time.time() * 1000)}",
            "type": task_type,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "retries": 0
        }
        self.task_queue.put(task)
        logger.debug(f"Added task {task['id']} to queue")

    def process_task(self, task: Dict[str, Any]) -> bool:
        """Process a single task"""
        task_start = time.time()
        task_id = task["id"]
        task_type = task["type"]
        
        try:
            logger.info(f"Processing task {task_id} of type {task_type}")
            
            # Process different types of tasks
            if task_type == "data_processing":
                self._process_data_task(task["data"])
            elif task_type == "file_processing":
                self._process_file_task(task["data"])
            elif task_type == "api_call":
                self._process_api_task(task["data"])
            elif task_type == "computation":
                self._process_computation_task(task["data"])
            else:
                logger.warning(f"Unknown task type: {task_type}")
                return False
            
            # Update statistics
            task_duration = time.time() - task_start
            self.processed_tasks += 1
            self.last_task_time = time.time()
            
            # Update average task time
            if self.stats["average_task_time"] == 0:
                self.stats["average_task_time"] = task_duration
            else:
                self.stats["average_task_time"] = (
                    self.stats["average_task_time"] * 0.9 + task_duration * 0.1
                )
            
            logger.info(f"Completed task {task_id} in {task_duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process task {task_id}: {e}")
            self.failed_tasks += 1
            return False

    def _process_data_task(self, data: Dict[str, Any]) -> None:
        """Process a data processing task"""
        # Simulate data processing
        items = data.get("items", [])
        processed_items = []
        
        for item in items:
            # Simulate processing time
            time.sleep(0.1)
            processed_items.append({
                "original": item,
                "processed": item.upper() if isinstance(item, str) else str(item),
                "timestamp": datetime.now().isoformat()
            })
        
        logger.debug(f"Processed {len(processed_items)} data items")

    def _process_file_task(self, data: Dict[str, Any]) -> None:
        """Process a file processing task"""
        file_path = data.get("file_path")
        if not file_path:
            raise ValueError("file_path is required for file processing tasks")
        
        # Simulate file processing
        time.sleep(1.0)  # Simulate I/O operations
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.debug(f"Processed file {file_path} ({file_size} bytes)")
        else:
            logger.warning(f"File not found: {file_path}")

    def _process_api_task(self, data: Dict[str, Any]) -> None:
        """Process an API call task"""
        endpoint = data.get("endpoint")
        method = data.get("method", "GET")
        
        # Simulate API call
        time.sleep(0.5)  # Simulate network latency
        
        logger.debug(f"Made {method} request to {endpoint}")

    def _process_computation_task(self, data: Dict[str, Any]) -> None:
        """Process a computation task"""
        iterations = data.get("iterations", 1000)
        
        # Simulate CPU-intensive computation
        result = 0
        for i in range(iterations):
            result += i * i
        
        logger.debug(f"Completed computation with {iterations} iterations")

    def get_stats(self) -> Dict[str, Any]:
        """Get current worker statistics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Get process information
        process = psutil.Process()
        
        return {
            "worker_id": self.worker_id,
            "pid": os.getpid(),
            "status": "running" if self.running else "stopped",
            "uptime_seconds": uptime,
            "tasks_processed": self.processed_tasks,
            "tasks_failed": self.failed_tasks,
            "queue_size": self.task_queue.qsize(),
            "average_task_time": self.stats["average_task_time"],
            "last_task_time": self.last_task_time,
            "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads()
        }

    def status_monitor(self) -> None:
        """Background thread for status monitoring and logging"""
        while self.running:
            try:
                stats = self.get_stats()
                logger.info(f"Worker stats: {stats['tasks_processed']} processed, "
                           f"{stats['queue_size']} queued, "
                           f"{stats['memory_usage_mb']:.1f}MB memory")
                time.sleep(30)  # Log stats every 30 seconds
            except Exception as e:
                logger.error(f"Error in status monitor: {e}")
                time.sleep(5)

    def run(self) -> None:
        """Main worker loop"""
        logger.info(f"Starting worker {self.worker_id}")
        self.running = True
        
        # Start status monitoring thread
        monitor_thread = threading.Thread(target=self.status_monitor, daemon=True)
        monitor_thread.start()
        
        # Add some sample tasks for demonstration
        self._add_sample_tasks()
        
        try:
            while self.running:
                try:
                    # Get task from queue with timeout
                    task = self.task_queue.get(timeout=1.0)
                    
                    # Process the task
                    success = self.process_task(task)
                    
                    if not success and task["retries"] < 3:
                        # Retry failed tasks up to 3 times
                        task["retries"] += 1
                        logger.info(f"Retrying task {task['id']} (attempt {task['retries']})")
                        self.task_queue.put(task)
                    
                    # Mark task as done
                    self.task_queue.task_done()
                    
                except Empty:
                    # No tasks in queue, continue
                    continue
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()

    def _add_sample_tasks(self) -> None:
        """Add sample tasks for demonstration"""
        sample_tasks = [
            ("data_processing", {"items": ["hello", "world", "pypm2"]}),
            ("computation", {"iterations": 5000}),
            ("api_call", {"endpoint": "https://api.example.com/data", "method": "GET"}),
            ("file_processing", {"file_path": "/tmp/sample.txt"}),
        ]
        
        for task_type, data in sample_tasks:
            self.add_task(task_type, data)
        
        logger.info(f"Added {len(sample_tasks)} sample tasks")

    def stop(self) -> None:
        """Stop the worker gracefully"""
        logger.info(f"Stopping worker {self.worker_id}")
        self.running = False
        
        # Process remaining tasks in queue
        remaining_tasks = []
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                remaining_tasks.append(task)
            except Empty:
                break
        
        if remaining_tasks:
            logger.info(f"Processing {len(remaining_tasks)} remaining tasks...")
            for task in remaining_tasks:
                self.process_task(task)
        
        # Final statistics
        final_stats = self.get_stats()
        logger.info(f"Worker {self.worker_id} stopped. Final stats: {final_stats}")

def main():
    """Main function to run the worker"""
    # Get configuration from environment variables
    worker_id = os.getenv("WORKER_ID", f"worker_{os.getpid()}")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure logging level
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Create and run worker
    worker = TaskProcessor(worker_id)
    
    try:
        worker.run()
    except Exception as e:
        logger.error(f"Worker crashed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
