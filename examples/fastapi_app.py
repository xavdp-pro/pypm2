#!/usr/bin/env python3
"""
FastAPI Application Example for PyPM2
This example demonstrates a production-ready FastAPI application
that can be managed by PyPM2.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import time
import psutil
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PyPM2 FastAPI Example",
    description="A production-ready FastAPI application for PyPM2",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
app_state = {
    "start_time": time.time(),
    "request_count": 0,
    "tasks_completed": 0,
    "health_status": "healthy"
}

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"FastAPI application starting up (PID: {os.getpid()})")
    app_state["start_time"] = time.time()

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("FastAPI application shutting down")

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with basic application info"""
    app_state["request_count"] += 1
    
    return {
        "message": "PyPM2 FastAPI Example API",
        "status": "online",
        "pid": os.getpid(),
        "uptime_seconds": time.time() - app_state["start_time"],
        "request_count": app_state["request_count"],
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring"""
    process = psutil.Process()
    
    return {
        "status": app_state["health_status"],
        "pid": os.getpid(),
        "uptime_seconds": time.time() - app_state["start_time"],
        "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
        "cpu_percent": process.cpu_percent(),
        "request_count": app_state["request_count"],
        "tasks_completed": app_state["tasks_completed"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Detailed metrics for monitoring"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "process": {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "status": process.status(),
            "create_time": process.create_time(),
            "num_threads": process.num_threads(),
        },
        "resources": {
            "cpu_percent": process.cpu_percent(),
            "memory_rss_mb": memory_info.rss / 1024 / 1024,
            "memory_vms_mb": memory_info.vms / 1024 / 1024,
            "memory_percent": process.memory_percent(),
        },
        "application": {
            "uptime_seconds": time.time() - app_state["start_time"],
            "request_count": app_state["request_count"],
            "tasks_completed": app_state["tasks_completed"],
            "health_status": app_state["health_status"],
        },
        "system": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }
    }

@app.post("/task")
async def create_background_task(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Create a background task"""
    task_id = f"task_{int(time.time())}"
    background_tasks.add_task(process_background_task, task_id)
    
    return {
        "message": "Background task created",
        "task_id": task_id,
        "status": "queued"
    }

async def process_background_task(task_id: str):
    """Process a background task"""
    logger.info(f"Starting background task: {task_id}")
    
    # Simulate some work
    await asyncio.sleep(5)
    
    app_state["tasks_completed"] += 1
    logger.info(f"Completed background task: {task_id}")

@app.get("/stress/{duration}")
async def stress_test(duration: int) -> Dict[str, Any]:
    """Stress test endpoint for testing resource usage"""
    if duration > 60:
        raise HTTPException(status_code=400, detail="Duration cannot exceed 60 seconds")
    
    start_time = time.time()
    end_time = start_time + duration
    
    # CPU intensive task
    result = 0
    while time.time() < end_time:
        result += sum(range(1000))
    
    return {
        "message": "Stress test completed",
        "duration_seconds": time.time() - start_time,
        "result": result,
        "pid": os.getpid()
    }

@app.post("/health/toggle")
async def toggle_health_status() -> Dict[str, str]:
    """Toggle health status for testing monitoring"""
    if app_state["health_status"] == "healthy":
        app_state["health_status"] = "unhealthy"
    else:
        app_state["health_status"] = "healthy"
    
    return {
        "message": "Health status toggled",
        "status": app_state["health_status"]
    }

@app.get("/error/{status_code}")
async def simulate_error(status_code: int) -> Dict[str, str]:
    """Simulate HTTP errors for testing"""
    if status_code == 500:
        raise HTTPException(status_code=500, detail="Internal server error simulation")
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Resource not found simulation")
    elif status_code == 400:
        raise HTTPException(status_code=400, detail="Bad request simulation")
    else:
        return {"message": f"Simulated status code: {status_code}"}

@app.post("/shutdown")
async def graceful_shutdown() -> Dict[str, str]:
    """Graceful shutdown endpoint"""
    logger.info("Graceful shutdown requested")
    
    # Perform cleanup tasks here
    await asyncio.sleep(1)
    
    # Send SIGTERM to self for graceful shutdown
    import signal
    os.kill(os.getpid(), signal.SIGTERM)
    
    return {"message": "Shutdown initiated"}

if __name__ == "__main__":
    # Configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    workers = int(os.getenv("WORKERS", 1))
    
    logger.info(f"Starting FastAPI server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Workers: {workers}")
    
    try:
        uvicorn.run(
            "fastapi_app:app",
            host=host,
            port=port,
            log_level="info" if not debug else "debug",
            access_log=True,
            reload=debug,
            workers=workers if not debug else 1
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
