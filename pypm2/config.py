import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Configuration manager for PyPM2"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            self.config_dir = Path.home() / ".pypm2"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.processes_file = self.config_dir / "processes.json"
        self.logs_dir = self.config_dir / "logs"
        self.pids_dir = self.config_dir / "pids"
        
        # Create necessary directories
        self.logs_dir.mkdir(exist_ok=True)
        self.pids_dir.mkdir(exist_ok=True)
        
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default configuration
        return {
            "daemon_port": 3000,
            "max_restarts": 10,
            "restart_delay": 1000,
            "log_level": "info",
            "max_memory_restart": "1G"
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
        self.save_config()
    
    def load_processes(self) -> Dict[str, Dict]:
        """Load saved processes configuration"""
        if self.processes_file.exists():
            try:
                with open(self.processes_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_processes(self, processes: Dict[str, Dict]):
        """Save processes configuration"""
        with open(self.processes_file, 'w') as f:
            json.dump(processes, f, indent=2)
