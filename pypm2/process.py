import os
import signal
import subprocess
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

class ProcessStatus(Enum):
    """Process status enumeration"""
    ONLINE = "online"
    STOPPED = "stopped"
    STOPPING = "stopping"
    ERRORED = "errored"
    LAUNCHING = "launching"

class Process:
    """Represents a managed process"""
    
    def __init__(self, name: str, script: str, config_manager, **kwargs):
        self.name = name
        self.script = script
        self.config = config_manager
        
        # Process configuration
        self.cwd = kwargs.get('cwd', os.getcwd())
        self.args = kwargs.get('args', [])
        self.env = kwargs.get('env', {})
        self.interpreter = kwargs.get('interpreter', 'python')
        self.max_restarts = kwargs.get('max_restarts', 10)
        self.restart_delay = kwargs.get('restart_delay', 1000)
        self.autorestart = kwargs.get('autorestart', True)
        self.watch = kwargs.get('watch', False)
        self.max_memory_restart = kwargs.get('max_memory_restart', None)
        
        # Process state
        self.pid = None
        self.status = ProcessStatus.STOPPED
        self.restart_count = 0
        self.created_at = datetime.now()
        self.started_at = None
        self.stopped_at = None
        self.process = None
        
        # Files
        self.log_file = self.config.logs_dir / f"{name}.log"
        self.error_file = self.config.logs_dir / f"{name}.error.log"
        self.pid_file = self.config.pids_dir / f"{name}.pid"
        
    def start(self) -> bool:
        """Start the process"""
        if self.status == ProcessStatus.ONLINE:
            return False
            
        self.status = ProcessStatus.LAUNCHING
        
        try:
            # Prepare command
            cmd = [self.interpreter, self.script] + self.args
            
            # Prepare environment
            env = os.environ.copy()
            env.update(self.env)
            
            # Open log files
            log_file = open(self.log_file, 'a')
            error_file = open(self.error_file, 'a')
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                cwd=self.cwd,
                env=env,
                stdout=log_file,
                stderr=error_file,
                preexec_fn=os.setsid
            )
            
            self.pid = self.process.pid
            self.status = ProcessStatus.ONLINE
            self.started_at = datetime.now()
            
            # Save PID to file
            with open(self.pid_file, 'w') as f:
                f.write(str(self.pid))
            
            return True
            
        except Exception as e:
            self.status = ProcessStatus.ERRORED
            self._log_error(f"Failed to start process: {e}")
            return False
    
    def stop(self, force: bool = False) -> bool:
        """Stop the process"""
        if self.status != ProcessStatus.ONLINE:
            return False
            
        self.status = ProcessStatus.STOPPING
        
        try:
            if self.process and self.process.poll() is None:
                if force:
                    # Force kill
                    self.process.kill()
                else:
                    # Graceful shutdown
                    self.process.terminate()
                    
                    # Wait for process to terminate
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if still alive
                        self.process.kill()
                        self.process.wait()
            
            # Additional cleanup with psutil
            if self.pid:
                try:
                    if force:
                        os.killpg(os.getpgid(self.pid), signal.SIGKILL)
                    else:
                        os.killpg(os.getpgid(self.pid), signal.SIGTERM)
                        
                        # Wait for process to terminate
                        timeout = 5
                        while timeout > 0 and self.is_alive():
                            time.sleep(0.1)
                            timeout -= 0.1
                        
                        # Force kill if still alive
                        if self.is_alive():
                            os.killpg(os.getpgid(self.pid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass  # Process already dead
            
            self.status = ProcessStatus.STOPPED
            self.stopped_at = datetime.now()
            self._cleanup_pid_file()
            
            return True
            
        except Exception as e:
            self._log_error(f"Failed to stop process: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the process"""
        self._log_info("Restarting process...")
        
        # Force stop if process is running
        if self.status == ProcessStatus.ONLINE:
            self._log_info(f"Stopping process with PID {self.pid}")
            if not self.stop():
                self._log_error("Failed to stop process gracefully, forcing kill")
                self.stop(force=True)
        
        # Wait a bit longer to ensure process is completely stopped
        time.sleep(max(1.0, self.restart_delay / 1000.0))
        
        # Check that no residual process is using the same port/resources
        self._cleanup_resources()
        
        self._log_info("Starting new process instance")
        result = self.start()
        
        if result:
            self._log_info(f"Process restarted successfully with new PID {self.pid}")
        else:
            self._log_error("Failed to restart process")
            
        return result
    
    def is_alive(self) -> bool:
        """Check if process is alive"""
        if not self.pid:
            return False
            
        try:
            process = psutil.Process(self.pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def get_memory_usage(self) -> Optional[int]:
        """Get memory usage in MB"""
        if not self.is_alive():
            return None
            
        try:
            process = psutil.Process(self.pid)
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def get_cpu_usage(self) -> Optional[float]:
        """Get CPU usage percentage"""
        if not self.is_alive():
            return None
            
        try:
            process = psutil.Process(self.pid)
            return process.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def monitor(self):
        """Monitor process for auto-restart and memory limits"""
        if not self.is_alive() and self.status == ProcessStatus.ONLINE:
            self.status = ProcessStatus.ERRORED
            
            if self.autorestart and self.restart_count < self.max_restarts:
                self.restart_count += 1
                self._log_info(f"Process crashed, restarting ({self.restart_count}/{self.max_restarts})")
                self.restart()
        
        # Check memory limit
        if self.max_memory_restart:
            memory_usage = self.get_memory_usage()
            if memory_usage and self._parse_memory_limit(self.max_memory_restart) < memory_usage:
                self._log_info(f"Memory limit exceeded ({memory_usage}MB), restarting")
                self.restart()
    
    def _parse_memory_limit(self, limit: str) -> int:
        """Parse memory limit string (e.g., '1G', '512M')"""
        if limit.endswith('G'):
            return int(limit[:-1]) * 1024
        elif limit.endswith('M'):
            return int(limit[:-1])
        else:
            return int(limit)
    
    def _log_info(self, message: str):
        """Log info message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] INFO: {message}\n")
    
    def _log_error(self, message: str):
        """Log error message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.error_file, 'a') as f:
            f.write(f"[{timestamp}] ERROR: {message}\n")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] WARNING: {message}\n")
    
    def _cleanup_pid_file(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def _cleanup_resources(self):
        """Clean up resources before restart"""
        # Nettoyer le fichier PID s'il existe encore
        self._cleanup_pid_file()
        
        # Vérifier qu'aucun processus zombie n'existe
        if self.pid:
            try:
                # Vérifier si le processus existe encore
                if psutil.pid_exists(self.pid):
                    process = psutil.Process(self.pid)
                    if process.is_running():
                        self._log_warning(f"Process {self.pid} still running, force killing")
                        try:
                            os.killpg(os.getpgid(self.pid), signal.SIGKILL)
                            time.sleep(0.5)  # Attendre que le kill prenne effet
                        except:
                            pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
                pass
        
        # Reset PID
        self.pid = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert process to dictionary"""
        return {
            "name": self.name,
            "script": self.script,
            "pid": self.pid,
            "status": self.status.value,
            "restart_count": self.restart_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "memory": self.get_memory_usage(),
            "cpu": self.get_cpu_usage(),
            "cwd": self.cwd,
            "args": self.args,
            "env": self.env,
            "interpreter": self.interpreter
        }
