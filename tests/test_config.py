import pytest
import tempfile
import json
from pathlib import Path
from pypm2.config import Config

class TestConfig:
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(self.temp_dir)
    
    def test_config_initialization(self):
        """Test config initialization"""
        assert self.config.config_dir.exists()
        assert self.config.logs_dir.exists()
        assert self.config.pids_dir.exists()
    
    def test_default_config(self):
        """Test default configuration values"""
        assert self.config.get('daemon_port') == 3000
        assert self.config.get('max_restarts') == 10
        assert self.config.get('restart_delay') == 1000
        assert self.config.get('log_level') == 'info'
    
    def test_set_and_get_config(self):
        """Test setting and getting configuration"""
        self.config.set('test_key', 'test_value')
        assert self.config.get('test_key') == 'test_value'
        
        # Test that it persists
        new_config = Config(self.temp_dir)
        assert new_config.get('test_key') == 'test_value'
    
    def test_save_and_load_processes(self):
        """Test saving and loading processes"""
        processes = {
            'test1': {
                'script': 'test1.py',
                'pid': 1234,
                'status': 'online'
            },
            'test2': {
                'script': 'test2.py',
                'pid': 5678,
                'status': 'stopped'
            }
        }
        
        self.config.save_processes(processes)
        loaded_processes = self.config.load_processes()
        
        assert loaded_processes == processes
