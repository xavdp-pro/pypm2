#!/usr/bin/env python3
"""
File watcher module for PyPM2 watch mode
Monitors file changes and triggers process restarts
"""

import os
import time
import threading
from pathlib import Path
from typing import Set, List, Callable, Optional, Dict

class SimpleFileWatcher:
    """Simple file watcher using polling (no external dependencies)"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.file_times: Dict[str, float] = {}
        self.ignore_patterns = [
            '*.log', '*.tmp', '*.swp', '*.pyc', '__pycache__',
            '.git', 'node_modules', '.pytest_cache', '.coverage',
            '*.pid', '*.lock'
        ]
        self.last_restart = 0
        self.restart_debounce = 1.0  # Minimum 1 second between restarts
        self.poll_interval = 1.0  # Check every second
    
    def should_ignore(self, path: str) -> bool:
        """Check if file should be ignored"""
        path_obj = Path(path)
        
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if path_obj.name.endswith(pattern[1:]):
                    return True
            elif pattern in str(path_obj):
                return True
        
        return False
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """Scan directory for Python files and other relevant files"""
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.ignore_patterns)]
                
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    
                    # Only watch relevant file types
                    if (filename.endswith(('.py', '.pyx', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg')) 
                        and not self.should_ignore(filepath)):
                        files.append(filepath)
                
                if not recursive:
                    break
        except (OSError, PermissionError):
            pass
        
        return files
    
    def check_file_changes(self, files: List[str]) -> bool:
        """Check if any files have changed"""
        changed = False
        
        for filepath in files:
            try:
                current_time = os.path.getmtime(filepath)
                if filepath in self.file_times:
                    if current_time > self.file_times[filepath]:
                        print(f"📁 File changed: {filepath}")
                        changed = True
                self.file_times[filepath] = current_time
            except (OSError, FileNotFoundError):
                # File might have been deleted, ignore
                if filepath in self.file_times:
                    del self.file_times[filepath]
        
        return changed

class ProcessWatcher:
    """Watches files and restarts processes on changes"""
    
    def __init__(self, process_name: str, restart_callback: Callable):
        self.process_name = process_name
        self.restart_callback = restart_callback
        self.watched_paths: Set[str] = set()
        self.is_running = False
        self.watcher_thread = None
        self.file_watcher = SimpleFileWatcher(self._on_file_change)
    
    def add_watch_path(self, path: str, recursive: bool = True):
        """Add a path to watch for changes"""
        path_obj = Path(path).resolve()
        
        if not path_obj.exists():
            print(f"⚠️  Warning: Watch path does not exist: {path}")
            return
        
        if str(path_obj) in self.watched_paths:
            return
        
        self.watched_paths.add(str(path_obj))
        print(f"👁️  Watching: {path_obj}")
    
    def _on_file_change(self):
        """Internal callback for file changes"""
        # Debounce rapid successive changes
        current_time = time.time()
        if current_time - self.file_watcher.last_restart < self.file_watcher.restart_debounce:
            return
        
        self.file_watcher.last_restart = current_time
        print(f"🔄 Restarting '{self.process_name}' due to file changes...")
        
        try:
            if self.restart_callback(self.process_name):
                print(f"✅ Process '{self.process_name}' restarted successfully")
            else:
                print(f"❌ Failed to restart process '{self.process_name}'")
        except Exception as e:
            print(f"❌ Failed to restart process: {e}")
    
    def _watch_loop(self):
        """Main watching loop"""
        while self.is_running:
            try:
                # Collect all files to watch
                all_files = []
                for path in self.watched_paths:
                    if os.path.isfile(path):
                        all_files.append(path)
                    elif os.path.isdir(path):
                        all_files.extend(self.file_watcher.scan_directory(path))
                
                # Check for changes
                if self.file_watcher.check_file_changes(all_files):
                    self._on_file_change()
                
                time.sleep(self.file_watcher.poll_interval)
                
            except Exception as e:
                print(f"❌ Error in watch loop: {e}")
                time.sleep(1)
    
    def start(self):
        """Start watching for file changes"""
        if self.is_running:
            return
        
        if not self.watched_paths:
            print("⚠️  No paths to watch. Use --watch-path to specify paths.")
            return
        
        self.is_running = True
        self.watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watcher_thread.start()
        
        print(f"🎯 Watch mode started for process '{self.process_name}'")
        print("💡 Press Ctrl+C to stop watching")
        
        try:
            while self.is_running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop watching for file changes"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=1)
        
        print(f"🛑 Stopped watching process '{self.process_name}'")

def setup_default_watch_paths(script_path: str) -> List[str]:
    """Setup default paths to watch based on script location"""
    script_path_obj = Path(script_path).resolve()
    watch_paths = []
    
    # Watch the script's directory
    if script_path_obj.parent.exists():
        watch_paths.append(str(script_path_obj.parent))
    
    # If it's a Python project, also watch common source directories
    project_root = script_path_obj.parent
    while project_root.parent != project_root:
        if (project_root / 'setup.py').exists() or (project_root / 'pyproject.toml').exists():
            # Found project root
            for src_dir in ['src', 'lib', 'app']:
                src_path = project_root / src_dir
                if src_path.exists():
                    watch_paths.append(str(src_path))
            break
        project_root = project_root.parent
    
    return watch_paths

def create_watcher(process_name: str, restart_callback: Callable, 
                  script_path: str, watch_paths: Optional[List[str]] = None) -> ProcessWatcher:
    """Create a new file watcher for a process"""
    watcher = ProcessWatcher(process_name, restart_callback)
    
    if watch_paths:
        for path in watch_paths:
            watcher.add_watch_path(path)
    else:
        # Use default watch paths
        default_paths = setup_default_watch_paths(script_path)
        for path in default_paths:
            watcher.add_watch_path(path)
    
    return watcher
