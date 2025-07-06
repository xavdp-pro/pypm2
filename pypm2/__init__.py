"""
PyPM2 - Process Manager for Python Applications
A Python equivalent to PM2 for Node.js

This package provides a complete process management solution for Python applications,
similar to PM2 for Node.js. It includes process monitoring, automatic restarts,
log management, and a command-line interface.

Features:
- Process lifecycle management (start, stop, restart, delete)
- Automatic restart on crashes
- Memory and CPU monitoring
- Log management with rotation
- Clustering support
- Systemd integration
- Persistent process configuration
"""

from .manager import ProcessManager
from .process import Process, ProcessStatus
from .config import Config
from .cli import main

__version__ = "1.0.0"
__author__ = "PyPM2 Team"
__email__ = "contact@pypm2.dev"
__license__ = "MIT"

# Export main classes
__all__ = [
    "ProcessManager",
    "Process", 
    "ProcessStatus",
    "Config",
    "main",
    "__version__"
]
