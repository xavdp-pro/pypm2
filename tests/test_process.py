import pytest
import tempfile
import time
from pathlib import Path
from pypm2.config import Config
from pypm2.process import Process, ProcessStatus

class TestProcess:
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(self.temp_dir)
        
        # Create a simple test script
        self.test_script = Path(self.temp_dir) / "test_script.py"
        self.test_script.write_text("""
import time
print("Process started")
for i in range(10):
    print(f"Running {i}")
    time.sleep(0.5)
print("Process finished")
""")
    
    def test_process_creation(self):
        """Test process creation"""
        process = Process("test", str(self.test_script), self.config)
        
        assert process.name == "test"
        assert process.script == str(self.test_script)
        assert process.status == ProcessStatus.STOPPED
        assert process.pid is None
    
    def test_process_start(self):
        """Test starting a process"""
        process = Process("test", str(self.test_script), self.config)
        
        result = process.start()
        assert result == True
        assert process.status == ProcessStatus.ONLINE
        assert process.pid is not None
        assert process.is_alive() == True
    
    def test_process_stop(self):
        """Test stopping a process"""
        process = Process("test", str(self.test_script), self.config)
        process.start()
        
        # Wait a bit for process to start
        time.sleep(1)
        
        result = process.stop()
        assert result == True
        
        # Wait a bit for process to stop
        time.sleep(2)
        
        assert process.status == ProcessStatus.STOPPED
        assert process.is_alive() == False
    
    def test_process_restart(self):
        """Test restarting a process"""
        process = Process("test", str(self.test_script), self.config)
        process.start()
        old_pid = process.pid
        
        result = process.restart()
        assert result == True
        assert process.status == ProcessStatus.ONLINE
        assert process.pid != old_pid  # Should have a new PID
    
    def test_process_with_args(self):
        """Test process with arguments"""
        # Create a script that uses arguments
        script_with_args = Path(self.temp_dir) / "script_with_args.py"
        script_with_args.write_text("""
import sys
print(f"Arguments: {sys.argv[1:]}")
""")
        
        process = Process("test", str(script_with_args), self.config, args=["arg1", "arg2"])
        process.start()
        
        assert process.args == ["arg1", "arg2"]
        assert process.is_alive() == True
    
    def test_process_to_dict(self):
        """Test converting process to dictionary"""
        process = Process("test", str(self.test_script), self.config)
        process.start()
        
        data = process.to_dict()
        
        assert data['name'] == "test"
        assert data['script'] == str(self.test_script)
        assert data['status'] == ProcessStatus.ONLINE.value
        assert data['pid'] is not None
