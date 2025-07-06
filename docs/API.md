# PyPM2 API Documentation

This document provides comprehensive documentation for the PyPM2 Python API.

## Table of Contents

- [ProcessManager](#processmanager)
- [Process](#process)
- [ProcessStatus](#processstatus)
- [Config](#config)
- [Examples](#examples)

## ProcessManager

The main class for managing processes in PyPM2.

### Constructor

```python
ProcessManager(config_dir: str = None)
```

**Parameters:**
- `config_dir` (str, optional): Directory for configuration files. Defaults to `~/.pypm2/`

**Example:**
```python
from pypm2 import ProcessManager

# Use default configuration directory
manager = ProcessManager()

# Use custom configuration directory
manager = ProcessManager("/path/to/config")
```

### Methods

#### start()

Start a new process.

```python
start(
    name: str,
    script: str,
    interpreter: str = "python3",
    args: List[str] = None,
    env: Dict[str, str] = None,
    cwd: str = None,
    autorestart: bool = True,
    max_memory: int = None
) -> bool
```

**Parameters:**
- `name` (str): Unique name for the process
- `script` (str): Path to the script to execute
- `interpreter` (str): Python interpreter to use
- `args` (List[str]): Command line arguments
- `env` (Dict[str, str]): Environment variables
- `cwd` (str): Working directory
- `autorestart` (bool): Enable automatic restart on crashes
- `max_memory` (int): Maximum memory usage in MB

**Returns:**
- `bool`: True if process started successfully

**Example:**
```python
success = manager.start(
    name="web-server",
    script="app.py",
    interpreter="python3.9",
    args=["--port", "8000"],
    env={"DEBUG": "true"},
    autorestart=True,
    max_memory=512
)
```

#### stop()

Stop one or more processes.

```python
stop(name: str, force: bool = False) -> bool
```

**Parameters:**
- `name` (str): Process name or "all" to stop all processes
- `force` (bool): Force kill if graceful shutdown fails

**Returns:**
- `bool`: True if process(es) stopped successfully

**Example:**
```python
# Stop a specific process
manager.stop("web-server")

# Force stop all processes
manager.stop("all", force=True)
```

#### restart()

Restart one or more processes.

```python
restart(name: str) -> bool
```

**Parameters:**
- `name` (str): Process name or "all" to restart all processes

**Returns:**
- `bool`: True if process(es) restarted successfully

**Example:**
```python
# Restart a specific process
manager.restart("web-server")

# Restart all processes
manager.restart("all")
```

#### delete()

Delete one or more processes.

```python
delete(name: str) -> bool
```

**Parameters:**
- `name` (str): Process name or "all" to delete all processes

**Returns:**
- `bool`: True if process(es) deleted successfully

**Example:**
```python
# Delete a specific process
manager.delete("web-server")

# Delete all processes
manager.delete("all")
```

#### list()

List all processes with their status.

```python
list() -> List[Dict[str, Any]]
```

**Returns:**
- `List[Dict]`: List of process information dictionaries

**Example:**
```python
processes = manager.list()
for proc in processes:
    print(f"Name: {proc['name']}, Status: {proc['status']}, PID: {proc['pid']}")
```

#### logs()

Get process logs.

```python
logs(name: str, lines: int = 50, follow: bool = False) -> List[str]
```

**Parameters:**
- `name` (str): Process name
- `lines` (int): Number of lines to return
- `follow` (bool): Follow log output (for real-time monitoring)

**Returns:**
- `List[str]`: List of log lines

**Example:**
```python
# Get last 100 lines
logs = manager.logs("web-server", lines=100)

# Follow logs in real-time
for line in manager.logs("web-server", follow=True):
    print(line)
```

## Process

Represents a single managed process.

### Constructor

```python
Process(
    name: str,
    script: str,
    config: Config,
    interpreter: str = "python3",
    args: List[str] = None,
    env: Dict[str, str] = None,
    cwd: str = None,
    autorestart: bool = True,
    max_memory: int = None
)
```

### Properties

- `name` (str): Process name
- `script` (str): Script path
- `pid` (int): Process ID
- `status` (ProcessStatus): Current status
- `started_at` (datetime): Start time
- `stopped_at` (datetime): Stop time
- `restart_count` (int): Number of restarts

### Methods

#### start()

Start the process.

```python
start() -> bool
```

#### stop()

Stop the process.

```python
stop(force: bool = False) -> bool
```

#### restart()

Restart the process.

```python
restart() -> bool
```

#### is_alive()

Check if process is running.

```python
is_alive() -> bool
```

#### get_memory_usage()

Get current memory usage.

```python
get_memory_usage() -> Optional[int]
```

#### get_cpu_usage()

Get current CPU usage.

```python
get_cpu_usage() -> Optional[float]
```

## ProcessStatus

Enumeration of possible process states.

```python
from enum import Enum

class ProcessStatus(Enum):
    LAUNCHING = "launching"
    ONLINE = "online"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERRORED = "errored"
```

## Config

Configuration management for PyPM2.

### Constructor

```python
Config(config_dir: str = None)
```

### Methods

#### get()

Get configuration value.

```python
get(key: str, default: Any = None) -> Any
```

#### set()

Set configuration value.

```python
set(key: str, value: Any) -> None
```

#### save()

Save configuration to file.

```python
save() -> None
```

#### load()

Load configuration from file.

```python
load() -> None
```

## Examples

### Basic Process Management

```python
from pypm2 import ProcessManager

# Create manager
manager = ProcessManager()

# Start a web server
manager.start(
    name="api-server",
    script="server.py",
    env={"PORT": "8000"}
)

# Monitor processes
processes = manager.list()
for proc in processes:
    if proc['status'] == 'online':
        print(f"✓ {proc['name']} is running (PID: {proc['pid']})")
    else:
        print(f"✗ {proc['name']} is {proc['status']}")

# View logs
logs = manager.logs("api-server", lines=50)
for line in logs:
    print(line)
```

### Advanced Configuration

```python
from pypm2 import ProcessManager, Config

# Custom configuration
config = Config("/opt/myapp/config")
config.set("log_level", "debug")
config.set("max_processes", 10)
config.save()

# Manager with custom config
manager = ProcessManager("/opt/myapp/config")

# Start with advanced options
manager.start(
    name="worker",
    script="worker.py",
    interpreter="/usr/bin/python3.9",
    args=["--queue", "high-priority"],
    env={
        "WORKER_TYPE": "background",
        "LOG_LEVEL": "info",
        "DATABASE_URL": "postgresql://localhost/myapp"
    },
    cwd="/opt/myapp",
    autorestart=True,
    max_memory=1024
)
```

### Process Monitoring

```python
import time
from pypm2 import ProcessManager

manager = ProcessManager()

# Monitor processes in real-time
while True:
    processes = manager.list()
    
    print("\n=== Process Status ===")
    for proc in processes:
        print(f"Name: {proc['name']}")
        print(f"Status: {proc['status']}")
        print(f"PID: {proc['pid']}")
        print(f"CPU: {proc['cpu']}%")
        print(f"Memory: {proc['memory']}MB")
        print(f"Restarts: {proc['restart_count']}")
        print("-" * 30)
    
    time.sleep(5)
```

### Error Handling

```python
from pypm2 import ProcessManager

manager = ProcessManager()

try:
    # Start process
    success = manager.start("myapp", "app.py")
    if not success:
        print("Failed to start process")
    
    # Get process status
    processes = manager.list()
    myapp = next((p for p in processes if p['name'] == 'myapp'), None)
    
    if myapp and myapp['status'] == 'errored':
        print("Process has errors, checking logs...")
        logs = manager.logs("myapp", lines=10)
        for line in logs:
            print(line)
        
        # Try to restart
        manager.restart("myapp")
    
except Exception as e:
    print(f"Error managing process: {e}")
```

## Event Handling

```python
from pypm2 import ProcessManager
import time

manager = ProcessManager()

# Start a process
manager.start("myapp", "app.py")

# Monitor for crashes and restart
while True:
    processes = manager.list()
    for proc in processes:
        if proc['status'] == 'errored':
            print(f"Process {proc['name']} crashed, restarting...")
            manager.restart(proc['name'])
    
    time.sleep(10)
```

This API provides a complete interface for managing Python processes programmatically, offering the same functionality as the command-line interface with additional flexibility for integration into larger applications.
