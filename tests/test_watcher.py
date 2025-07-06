#!/usr/bin/env python3
"""
Tests for PyPM2 watch mode functionality
"""

import unittest
import tempfile
import os
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch

# Import from parent directory
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypm2.watcher import ProcessWatcher, SimpleFileWatcher, setup_default_watch_paths

class TestSimpleFileWatcher(unittest.TestCase):
    """Test the simple file watcher functionality"""
    
    def setUp(self):
        self.callback = Mock()
        self.watcher = SimpleFileWatcher(self.callback)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_should_ignore_patterns(self):
        """Test file ignore patterns"""
        # Should ignore
        self.assertTrue(self.watcher.should_ignore("/path/file.log"))
        self.assertTrue(self.watcher.should_ignore("/path/file.pyc"))
        self.assertTrue(self.watcher.should_ignore("/path/__pycache__/file.py"))
        self.assertTrue(self.watcher.should_ignore("/path/.git/config"))
        
        # Should not ignore
        self.assertFalse(self.watcher.should_ignore("/path/file.py"))
        self.assertFalse(self.watcher.should_ignore("/path/config.json"))
        self.assertFalse(self.watcher.should_ignore("/path/app.toml"))
    
    def test_scan_directory(self):
        """Test directory scanning"""
        # Create test files
        test_files = [
            'script.py',
            'config.json',
            'readme.txt',  # Should be ignored
            'test.log',    # Should be ignored
            'subdir/module.py'
        ]
        
        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("test content")
        
        # Scan directory
        found_files = self.watcher.scan_directory(self.temp_dir)
        found_names = [os.path.basename(f) for f in found_files]
        
        # Should find Python and config files, but not log files
        self.assertIn('script.py', found_names)
        self.assertIn('config.json', found_names)
        self.assertIn('module.py', found_names)
        self.assertNotIn('test.log', found_names)
        self.assertNotIn('readme.txt', found_names)
    
    def test_check_file_changes(self):
        """Test file change detection"""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        # Initial scan
        self.assertFalse(self.watcher.check_file_changes([test_file]))
        
        # Modify file
        time.sleep(0.1)  # Ensure different mtime
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        # Should detect change
        self.assertTrue(self.watcher.check_file_changes([test_file]))

class TestProcessWatcher(unittest.TestCase):
    """Test the process watcher functionality"""
    
    def setUp(self):
        self.restart_callback = Mock(return_value=True)
        self.watcher = ProcessWatcher("test-process", self.restart_callback)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        self.watcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_watch_path(self):
        """Test adding watch paths"""
        # Add existing path
        self.watcher.add_watch_path(self.temp_dir)
        self.assertIn(os.path.realpath(self.temp_dir), self.watcher.watched_paths)
        
        # Add non-existing path (should warn but not crash)
        non_existing = os.path.join(self.temp_dir, "nonexisting")
        self.watcher.add_watch_path(non_existing)
        self.assertNotIn(non_existing, self.watcher.watched_paths)
    
    def test_file_change_callback(self):
        """Test that file changes trigger restart callback"""
        # Add watch path
        self.watcher.add_watch_path(self.temp_dir)
        
        # Create test file
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        # Start watcher in background
        watcher_thread = threading.Thread(target=self.watcher._watch_loop, daemon=True)
        self.watcher.is_running = True
        watcher_thread.start()
        
        # Give it time to scan initial files
        time.sleep(0.2)
        
        # Modify file
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        # Wait for change detection
        time.sleep(1.5)  # Longer than poll interval
        
        # Stop watcher
        self.watcher.is_running = False
        watcher_thread.join(timeout=1)
        
        # Should have called restart callback
        self.restart_callback.assert_called_with("test-process")

class TestWatcherUtils(unittest.TestCase):
    """Test watcher utility functions"""
    
    def test_setup_default_watch_paths(self):
        """Test default watch path setup"""
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            script_path = f.name
        
        try:
            paths = setup_default_watch_paths(script_path)
            
            # Should include script's directory
            script_dir = os.path.dirname(script_path)
            self.assertIn(script_dir, paths)
            
        finally:
            os.unlink(script_path)
    
    def test_setup_default_watch_paths_project_structure(self):
        """Test default watch paths for project structure"""
        # Create a temporary project structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create project files
            setup_py = os.path.join(temp_dir, 'setup.py')
            src_dir = os.path.join(temp_dir, 'src')
            script_path = os.path.join(src_dir, 'app.py')
            
            os.makedirs(src_dir)
            
            with open(setup_py, 'w') as f:
                f.write("# setup.py")
            
            with open(script_path, 'w') as f:
                f.write("# app.py")
            
            paths = setup_default_watch_paths(script_path)
            
            # Should include src directory
            self.assertIn(src_dir, paths)

def run_tests():
    """Run all watch mode tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSimpleFileWatcher))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessWatcher))
    suite.addTests(loader.loadTestsFromTestCase(TestWatcherUtils))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
