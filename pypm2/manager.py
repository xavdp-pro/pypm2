import time
import threading
from typing import Dict, List, Optional, Any
from .config import Config
from .process import Process, ProcessStatus

class ProcessManager:
    """Main process manager class"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config = Config(config_dir)
        self.processes: Dict[str, Process] = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # Load saved processes
        self._load_processes()
        
        # Start monitoring
        self.start_monitoring()
    
    def start(self, name: str, script: str, **kwargs) -> bool:
        """Start a new process or restart existing one"""
        if name in self.processes:
            return self.processes[name].restart()
        
        process = Process(name, script, self.config, **kwargs)
        if process.start():
            self.processes[name] = process
            self._save_processes()
            return True
        return False
    
    def stop(self, name: str, force: bool = False) -> bool:
        """Stop a process"""
        if name not in self.processes:
            return False
        
        result = self.processes[name].stop(force)
        if result:
            self._save_processes()
        return result
    
    def restart(self, name: str) -> bool:
        """Restart a process"""
        if name not in self.processes:
            return False
        
        result = self.processes[name].restart()
        if result:
            self._save_processes()
        return result
    
    def delete(self, name: str) -> bool:
        """Delete a process"""
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        if process.status == ProcessStatus.ONLINE:
            process.stop()
        
        del self.processes[name]
        self._save_processes()
        return True
    
    def stop_all(self, force: bool = False) -> int:
        """Stop all processes"""
        stopped = 0
        for process in self.processes.values():
            if process.status == ProcessStatus.ONLINE:
                if process.stop(force):
                    stopped += 1
        
        self._save_processes()
        return stopped
    
    def restart_all(self) -> int:
        """Restart all processes"""
        restarted = 0
        for process in self.processes.values():
            if process.restart():
                restarted += 1
        
        self._save_processes()
        return restarted
    
    def delete_all(self) -> int:
        """Delete all processes"""
        count = len(self.processes)
        for name in list(self.processes.keys()):
            self.delete(name)
        return count
    
    def list(self) -> List[Dict[str, Any]]:
        """List all processes"""
        return [process.to_dict() for process in self.processes.values()]
    
    def get_process(self, name: str) -> Optional[Process]:
        """Get process by name"""
        return self.processes.get(name)
    
    def logs(self, name: str, lines: int = 20, follow: bool = False) -> List[str]:
        """Get process logs"""
        if name not in self.processes:
            return []
        
        process = self.processes[name]
        
        try:
            with open(process.log_file, 'r') as f:
                log_lines = f.readlines()
            
            if follow:
                # In a real implementation, this would tail the file
                # For now, just return the last lines
                return log_lines[-lines:] if lines > 0 else log_lines
            else:
                return log_lines[-lines:] if lines > 0 else log_lines
                
        except FileNotFoundError:
            return []
    
    def flush_logs(self, name: Optional[str] = None) -> bool:
        """Flush logs for process or all processes"""
        if name:
            if name not in self.processes:
                return False
            process = self.processes[name]
            try:
                process.log_file.unlink(missing_ok=True)
                process.error_file.unlink(missing_ok=True)
                return True
            except Exception:
                return False
        else:
            # Flush all logs
            success = True
            for process in self.processes.values():
                try:
                    process.log_file.unlink(missing_ok=True)
                    process.error_file.unlink(missing_ok=True)
                except Exception:
                    success = False
            return success
    
    def start_monitoring(self):
        """Start process monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop process monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            for process in self.processes.values():
                process.monitor()
            time.sleep(1)  # Check every second
    
    def _load_processes(self):
        """Load processes from configuration"""
        processes_config = self.config.load_processes()
        
        for name, config in processes_config.items():
            try:
                process = Process(name, config['script'], self.config, **config.get('options', {}))
                
                # Restore process state
                if config.get('pid'):
                    process.pid = config['pid']
                    if process.is_alive():
                        process.status = ProcessStatus.ONLINE
                    else:
                        process.status = ProcessStatus.STOPPED
                        process.pid = None
                
                self.processes[name] = process
            except Exception as e:
                print(f"Failed to load process {name}: {e}")
    
    def _save_processes(self):
        """Save processes to configuration"""
        processes_config = {}
        
        for name, process in self.processes.items():
            processes_config[name] = {
                'script': process.script,
                'pid': process.pid,
                'status': process.status.value,
                'options': {
                    'cwd': process.cwd,
                    'args': process.args,
                    'env': process.env,
                    'interpreter': process.interpreter,
                    'max_restarts': process.max_restarts,
                    'restart_delay': process.restart_delay,
                    'autorestart': process.autorestart,
                    'watch': process.watch,
                    'max_memory_restart': process.max_memory_restart
                }
            }
        
        self.config.save_processes(processes_config)
    
    def __del__(self):
        """Cleanup when manager is destroyed"""
        self.stop_monitoring()
