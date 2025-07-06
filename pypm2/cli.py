#!/usr/bin/env python3
"""
PyPM2 Command Line Interface
A Python equivalent to PM2 for Node.js
"""

import argparse
import sys
import json
import time
from pathlib import Path
from typing import Optional, List
from tabulate import tabulate

from .manager import ProcessManager
from .process import ProcessStatus

def format_status(status: str) -> str:
    """Format status with colors"""
    colors = {
        'online': '\033[92m',   # Green
        'stopped': '\033[91m',  # Red
        'errored': '\033[91m',  # Red
        'stopping': '\033[93m', # Yellow
        'launching': '\033[93m' # Yellow
    }
    reset = '\033[0m'
    return f"{colors.get(status, '')}{status}{reset}"

def format_memory(memory: Optional[float]) -> str:
    """Format memory usage"""
    if memory is None:
        return "N/A"
    if memory > 1024:
        return f"{memory/1024:.1f}G"
    return f"{memory:.0f}M"

def format_uptime(started_at: Optional[str]) -> str:
    """Format process uptime"""
    if not started_at:
        return "N/A"
    
    from datetime import datetime
    try:
        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        uptime = datetime.now() - start_time.replace(tzinfo=None)
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"

def cmd_start(args, manager: ProcessManager):
    """Start command"""
    options = {}
    
    if args.cwd:
        options['cwd'] = args.cwd
    if args.interpreter:
        options['interpreter'] = args.interpreter
    if args.name:
        name = args.name
    else:
        name = Path(args.script).stem
    
    if args.args:
        options['args'] = args.args
    
    if args.env:
        env_dict = {}
        for env_pair in args.env:
            if '=' in env_pair:
                key, value = env_pair.split('=', 1)
                env_dict[key] = value
        options['env'] = env_dict
    
    if args.max_restarts is not None:
        options['max_restarts'] = args.max_restarts
    
    if args.restart_delay is not None:
        options['restart_delay'] = args.restart_delay
    
    if args.no_autorestart:
        options['autorestart'] = False
    
    if args.max_memory_restart:
        options['max_memory_restart'] = args.max_memory_restart
    
    if manager.start(name, args.script, **options):
        print(f"✓ Process '{name}' started successfully")
    else:
        print(f"✗ Failed to start process '{name}'")
        sys.exit(1)

def cmd_stop(args, manager: ProcessManager):
    """Stop command"""
    if args.name == 'all':
        stopped = manager.stop_all(args.force)
        print(f"✓ Stopped {stopped} processes")
    else:
        if manager.stop(args.name, args.force):
            print(f"✓ Process '{args.name}' stopped")
        else:
            print(f"✗ Failed to stop process '{args.name}' or process not found")
            sys.exit(1)

def cmd_restart(args, manager: ProcessManager):
    """Restart command"""
    if args.name == 'all':
        restarted = manager.restart_all()
        print(f"✓ Restarted {restarted} processes")
    else:
        if manager.restart(args.name):
            print(f"✓ Process '{args.name}' restarted")
        else:
            print(f"✗ Failed to restart process '{args.name}' or process not found")
            sys.exit(1)

def cmd_delete(args, manager: ProcessManager):
    """Delete command"""
    if args.name == 'all':
        deleted = manager.delete_all()
        print(f"✓ Deleted {deleted} processes")
    else:
        if manager.delete(args.name):
            print(f"✓ Process '{args.name}' deleted")
        else:
            print(f"✗ Failed to delete process '{args.name}' or process not found")
            sys.exit(1)

def cmd_list(args, manager: ProcessManager):
    """List command"""
    processes = manager.list()
    
    if not processes:
        print("No processes found")
        return
    
    if args.json:
        print(json.dumps(processes, indent=2))
        return
    
    headers = ["Name", "PID", "Status", "Restart", "Uptime", "CPU", "Memory", "Script"]
    rows = []
    
    for proc in processes:
        rows.append([
            proc['name'],
            proc['pid'] or 'N/A',
            format_status(proc['status']),
            proc['restart_count'],
            format_uptime(proc['started_at']),
            f"{proc['cpu']:.1f}%" if proc['cpu'] is not None else 'N/A',
            format_memory(proc['memory']),
            proc['script']
        ])
    
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def cmd_logs(args, manager: ProcessManager):
    """Logs command"""
    if args.name not in [p['name'] for p in manager.list()]:
        print(f"✗ Process '{args.name}' not found")
        sys.exit(1)
    
    logs = manager.logs(args.name, args.lines, args.follow)
    
    for line in logs:
        print(line.rstrip())
    
    if args.follow:
        # In a real implementation, this would continuously tail the file
        print("(Follow mode not fully implemented in this demo)")

def cmd_flush(args, manager: ProcessManager):
    """Flush logs command"""
    if args.name:
        if manager.flush_logs(args.name):
            print(f"✓ Logs flushed for process '{args.name}'")
        else:
            print(f"✗ Failed to flush logs for process '{args.name}'")
            sys.exit(1)
    else:
        if manager.flush_logs():
            print("✓ All logs flushed")
        else:
            print("✗ Failed to flush some logs")
            sys.exit(1)

def cmd_monit(args, manager: ProcessManager):
    """Monitor command"""
    print("PyPM2 Process Monitor")
    print("Press Ctrl+C to exit")
    print()
    
    try:
        while True:
            # Clear screen
            print("\033[2J\033[H", end="")
            
            processes = manager.list()
            
            if not processes:
                print("No processes found")
            else:
                headers = ["Name", "PID", "Status", "CPU", "Memory", "Restarts"]
                rows = []
                
                for proc in processes:
                    rows.append([
                        proc['name'],
                        proc['pid'] or 'N/A',
                        format_status(proc['status']),
                        f"{proc['cpu']:.1f}%" if proc['cpu'] is not None else 'N/A',
                        format_memory(proc['memory']),
                        proc['restart_count']
                    ])
                
                print(tabulate(rows, headers=headers, tablefmt='grid'))
            
            print(f"\nLast updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

def cmd_resurrect(args, manager: ProcessManager):
    """Resurrect all saved processes"""
    try:
        # Load saved processes from config
        saved_processes = manager.config.load_processes()
        
        if not saved_processes:
            print("No saved processes found to resurrect")
            return
        
        print(f"Resurrecting {len(saved_processes)} processes...")
        
        resurrected = 0
        for name, proc_data in saved_processes.items():
            try:
                script = proc_data.get('script')
                
                if not script:
                    continue
                
                # Check if process is already running
                existing_process = manager.get_process(name)
                if existing_process and existing_process.status.value == 'online':
                    print(f"⚠ Process '{name}' is already running, skipping")
                    continue
                
                # Extract start parameters
                interpreter = proc_data.get('interpreter', 'python3')
                args_list = proc_data.get('args', [])
                env = proc_data.get('env', {})
                cwd = proc_data.get('cwd')
                autorestart = proc_data.get('autorestart', True)
                max_memory = proc_data.get('max_memory')
                
                # Start the process
                if manager.start(
                    name=name,
                    script=script,
                    interpreter=interpreter,
                    args=args_list,
                    env=env,
                    cwd=cwd,
                    autorestart=autorestart,
                    max_memory=max_memory
                ):
                    print(f"✓ Process '{name}' resurrected")
                    resurrected += 1
                else:
                    print(f"✗ Failed to resurrect process '{name}'")
                    
            except Exception as e:
                print(f"✗ Failed to resurrect process '{name}': {e}")
        
        print(f"\nResurrected {resurrected}/{len(saved_processes)} processes")
        
    except Exception as e:
        print(f"✗ Error during resurrection: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="PyPM2 - Process Manager for Python Applications",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start a process')
    start_parser.add_argument('script', help='Script to run')
    start_parser.add_argument('--name', help='Process name')
    start_parser.add_argument('--cwd', help='Working directory')
    start_parser.add_argument('--interpreter', default='python', help='Python interpreter')
    start_parser.add_argument('--args', nargs='*', help='Script arguments')
    start_parser.add_argument('--env', nargs='*', help='Environment variables (KEY=VALUE)')
    start_parser.add_argument('--max-restarts', type=int, help='Maximum restarts')
    start_parser.add_argument('--restart-delay', type=int, help='Restart delay in ms')
    start_parser.add_argument('--no-autorestart', action='store_true', help='Disable auto restart')
    start_parser.add_argument('--max-memory-restart', help='Restart when memory exceeds limit')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop a process')
    stop_parser.add_argument('name', help='Process name or "all"')
    stop_parser.add_argument('--force', action='store_true', help='Force kill')
    
    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart a process')
    restart_parser.add_argument('name', help='Process name or "all"')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a process')
    delete_parser.add_argument('name', help='Process name or "all"')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List processes')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show process logs')
    logs_parser.add_argument('name', help='Process name')
    logs_parser.add_argument('--lines', type=int, default=20, help='Number of lines to show')
    logs_parser.add_argument('--follow', action='store_true', help='Follow log output')
    
    # Flush command
    flush_parser = subparsers.add_parser('flush', help='Flush logs')
    flush_parser.add_argument('name', nargs='?', help='Process name (optional)')
    
    # Monitor command
    monit_parser = subparsers.add_parser('monit', help='Monitor processes')
    
    # Resurrect command
    resurrect_parser = subparsers.add_parser('resurrect', help='Resurrect all saved processes')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize process manager
    try:
        manager = ProcessManager()
    except Exception as e:
        print(f"✗ Failed to initialize PyPM2: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'start':
            cmd_start(args, manager)
        elif args.command == 'stop':
            cmd_stop(args, manager)
        elif args.command == 'restart':
            cmd_restart(args, manager)
        elif args.command == 'delete':
            cmd_delete(args, manager)
        elif args.command == 'list':
            cmd_list(args, manager)
        elif args.command == 'logs':
            cmd_logs(args, manager)
        elif args.command == 'flush':
            cmd_flush(args, manager)
        elif args.command == 'monit':
            cmd_monit(args, manager)
        elif args.command == 'resurrect':
            cmd_resurrect(args, manager)
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(130)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
