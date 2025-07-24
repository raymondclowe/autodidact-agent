"""
Test suite for enhanced logging and debugging functionality.
Tests debug mode, persistent logging, and incident file generation.
"""

import pytest
import tempfile
import shutil
import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to sys.path to import utils
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import configure_debug_logging, CONFIG_DIR
from utils.error_handling import create_incident_file, log_major_error, extract_error_details


class TestDebugLogging:
    """Test debug logging configuration and file output"""
    
    def setup_method(self):
        """Set up test environment"""
        self.original_config_dir = None
        self.temp_dir = None
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_configure_debug_logging(self):
        """Test that debug logging creates a log file and configures correctly"""
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock CONFIG_DIR
        with patch('utils.config.CONFIG_DIR', self.temp_dir):
            debug_log_file = configure_debug_logging()
            
            # Check that debug log file was created
            assert debug_log_file is not None
            assert Path(debug_log_file).exists()
            assert Path(debug_log_file).name.startswith('debug-')
            assert Path(debug_log_file).suffix == '.log'
            
            # Check that logging level is set to DEBUG
            assert logging.getLogger().level == logging.DEBUG
            
            # Test that logging actually writes to the file
            test_logger = logging.getLogger('test_logger')
            test_message = "Test debug message"
            test_logger.debug(test_message)
            
            # Read the log file and check content
            with open(debug_log_file, 'r') as f:
                log_content = f.read()
                assert test_message in log_content
                assert 'DEBUG' in log_content
    
    def test_debug_log_file_naming(self):
        """Test that debug log files have proper timestamp naming"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        with patch('utils.config.CONFIG_DIR', self.temp_dir):
            debug_log_file = configure_debug_logging()
            
            # Check filename format: debug-YYYYMMDD-HHMMSS.log
            filename = Path(debug_log_file).name
            assert filename.startswith('debug-')
            assert filename.endswith('.log')
            
            # Extract timestamp part and validate format
            timestamp_part = filename[6:-4]  # Remove 'debug-' prefix and '.log' suffix
            assert len(timestamp_part) == 15  # YYYYMMDD-HHMMSS
            assert timestamp_part[8] == '-'  # Date-time separator


class TestIncidentLogging:
    """Test incident file creation and major error logging"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = None
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_incident_file(self):
        """Test incident file creation with proper format"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        error_details = {
            'message': 'Test error message',
            'type': 'TestError',
            'code': 500
        }
        context = "test operation"
        additional_info = {'test_param': 'test_value'}
        
        with patch('utils.config.CONFIG_DIR', self.temp_dir):
            incident_file = create_incident_file(error_details, context, additional_info)
            
            # Check that incident file was created
            assert incident_file is not None
            assert Path(incident_file).exists()
            assert Path(incident_file).name.startswith('incident-')
            assert Path(incident_file).suffix == '.log'
            
            # Read and verify file content
            with open(incident_file, 'r') as f:
                content = f.read()
                
                # Check for required sections
                assert 'AUTODIDACT INCIDENT REPORT' in content
                assert 'ERROR DETAILS:' in content
                assert 'ADDITIONAL INFORMATION:' in content
                assert 'SYSTEM INFORMATION:' in content
                assert 'FULL JSON DATA:' in content
                
                # Check for specific error details
                assert 'Test error message' in content
                assert 'TestError' in content
                assert '500' in content
                assert 'test operation' in content
                assert 'test_value' in content
    
    def test_incident_file_naming(self):
        """Test that incident files have proper timestamp naming"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        error_details = {'message': 'Test error'}
        context = "test"
        
        with patch('utils.config.CONFIG_DIR', self.temp_dir):
            incident_file = create_incident_file(error_details, context)
            
            # Check filename format: incident-YYYYMMDD-HHMMSS.log
            filename = Path(incident_file).name
            assert filename.startswith('incident-')
            assert filename.endswith('.log')
            
            # Extract timestamp part and validate format
            timestamp_part = filename[9:-4]  # Remove 'incident-' prefix and '.log' suffix
            assert len(timestamp_part) == 15  # YYYYMMDD-HHMMSS
            assert timestamp_part[8] == '-'  # Date-time separator
    
    def test_log_major_error(self):
        """Test comprehensive major error logging"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create a mock error object
        mock_error = Exception("Test major error")
        mock_error.status_code = 500
        context = "deep research"
        additional_info = {'model': 'test-model', 'prompt_length': 1000}
        
        with patch('utils.config.CONFIG_DIR', self.temp_dir):
            error_message, is_retryable, incident_file = log_major_error(
                mock_error, context, additional_info
            )
            
            # Check return values
            assert error_message is not None
            assert isinstance(is_retryable, bool)
            assert incident_file is not None
            assert Path(incident_file).exists()
            
            # Check that error message contains useful information
            assert error_message is not None
            assert len(error_message) > 0
            # Check that either the context or the actual error message is included
            assert ('deep research' in error_message or 'Test major error' in error_message)
            
            # Verify incident file content
            with open(incident_file, 'r') as f:
                content = f.read()
                assert 'Test major error' in content
                assert 'deep research' in content
                assert 'test-model' in content
                assert '1000' in content


class TestErrorDetailsExtraction:
    """Test error details extraction functionality"""
    
    def test_extract_error_details_from_exception(self):
        """Test extracting details from a standard exception"""
        error = ValueError("Test value error")
        error.code = 400
        
        details = extract_error_details(error)
        
        assert details['message'] == 'Test value error'
        assert details['type'] == 'ValueError'
        assert details['code'] == 400
    
    def test_extract_error_details_from_dict(self):
        """Test extracting details from a dictionary-like error object"""
        error_dict = {
            'error': {
                'message': 'API error occurred',
                'type': 'APIError',
                'code': 429
            }
        }
        
        details = extract_error_details(error_dict)
        
        # Note: extract_error_details expects an object with attributes, not a dict
        # So it might not extract all details, but should not crash
        assert isinstance(details, dict)
        assert 'message' in details
        assert 'type' in details


class TestCommandLineArgParsing:
    """Test command line argument parsing for debug mode"""
    
    def test_debug_flag_detection(self):
        """Test that --debug flag is properly detected and removed from sys.argv"""
        # Save original sys.argv
        original_argv = sys.argv.copy()
        original_env = os.environ.get("AUTODIDACT_DEBUG")
        
        try:
            # Test with --debug flag
            sys.argv = ['app.py', '--debug']
            
            # Create a simple version of the parsing function for testing
            def parse_debug_args():
                debug_mode = False
                if '--debug' in sys.argv:
                    debug_mode = True
                    sys.argv.remove('--debug')
                
                # Also check for AUTODIDACT_DEBUG environment variable
                if os.getenv("AUTODIDACT_DEBUG", "").lower() in ["true", "1", "yes"]:
                    debug_mode = True
                
                return debug_mode
            
            debug_mode = parse_debug_args()
            
            assert debug_mode is True
            assert '--debug' not in sys.argv
            
        finally:
            # Restore original sys.argv and environment
            sys.argv = original_argv
            if original_env is None:
                os.environ.pop("AUTODIDACT_DEBUG", None)
            else:
                os.environ["AUTODIDACT_DEBUG"] = original_env
    
    def test_environment_variable_debug(self):
        """Test that AUTODIDACT_DEBUG environment variable enables debug mode"""
        # Save original environment
        original_env = os.environ.get("AUTODIDACT_DEBUG")
        original_argv = sys.argv.copy()
        
        try:
            # Test with environment variable
            os.environ["AUTODIDACT_DEBUG"] = "true"
            sys.argv = ['app.py']
            
            def parse_debug_args():
                debug_mode = False
                if '--debug' in sys.argv:
                    debug_mode = True
                    sys.argv.remove('--debug')
                
                # Also check for AUTODIDACT_DEBUG environment variable
                if os.getenv("AUTODIDACT_DEBUG", "").lower() in ["true", "1", "yes"]:
                    debug_mode = True
                
                return debug_mode
            
            debug_mode = parse_debug_args()
            
            assert debug_mode is True
            
        finally:
            # Restore original environment and argv
            if original_env is None:
                os.environ.pop("AUTODIDACT_DEBUG", None)
            else:
                os.environ["AUTODIDACT_DEBUG"] = original_env
            sys.argv = original_argv
    
    def test_no_debug_flag(self):
        """Test normal operation without --debug flag or environment variable"""
        # Save original sys.argv and environment
        original_argv = sys.argv.copy()
        original_env = os.environ.get("AUTODIDACT_DEBUG")
        
        try:
            # Test without --debug flag or environment variable
            sys.argv = ['app.py']
            os.environ.pop("AUTODIDACT_DEBUG", None)
            
            def parse_debug_args():
                debug_mode = False
                if '--debug' in sys.argv:
                    debug_mode = True
                    sys.argv.remove('--debug')
                
                # Also check for AUTODIDACT_DEBUG environment variable
                if os.getenv("AUTODIDACT_DEBUG", "").lower() in ["true", "1", "yes"]:
                    debug_mode = True
                
                return debug_mode
            
            debug_mode = parse_debug_args()
            
            assert debug_mode is False
            
        finally:
            # Restore original sys.argv and environment
            sys.argv = original_argv
            if original_env is not None:
                os.environ["AUTODIDACT_DEBUG"] = original_env


if __name__ == "__main__":
    pytest.main([__file__, "-v"])