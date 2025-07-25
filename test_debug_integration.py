#!/usr/bin/env python3
"""
Test script for debug command line server option functionality
"""

import subprocess
import sys
import os
import time
import tempfile
from pathlib import Path

def test_debug_flag_parsing():
    """Test that --debug flag is properly parsed"""
    print("🧪 Testing Debug Flag Parsing")
    print("=" * 50)
    
    # Test 1: Direct Python execution with --debug
    print("📋 Test 1: python app.py --debug")
    try:
        result = subprocess.run([
            sys.executable, "app.py", "--debug"
        ], capture_output=True, text=True, timeout=5, cwd=".")
        
        if "Debug mode enabled" in result.stderr:
            print("  ✅ Debug mode properly activated")
        else:
            print("  ❌ Debug mode not detected in output")
            print(f"  stderr: {result.stderr[:200]}...")
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  Timeout (expected for streamlit app)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Environment variable
    print("\n📋 Test 2: AUTODIDACT_DEBUG=true")
    try:
        env = os.environ.copy()
        env["AUTODIDACT_DEBUG"] = "true"
        
        result = subprocess.run([
            sys.executable, "app.py"
        ], capture_output=True, text=True, timeout=5, cwd=".", env=env)
        
        if "Debug mode enabled" in result.stderr:
            print("  ✅ Debug mode properly activated via environment variable")
        else:
            print("  ❌ Debug mode not detected in output")
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  Timeout (expected for streamlit app)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_debug_log_creation():
    """Test that debug log files are created"""
    print("\n🧪 Testing Debug Log Creation")
    print("=" * 50)
    
    # Import config to check debug functionality
    sys.path.insert(0, '.')
    try:
        from utils.config import configure_debug_logging, CONFIG_DIR, list_debug_log_files
        
        print("📋 Configuring debug logging...")
        log_file = configure_debug_logging()
        
        if log_file and Path(log_file).exists():
            print(f"  ✅ Debug log file created: {log_file}")
            
            # Check if file has content
            size = Path(log_file).stat().st_size
            print(f"  📊 Log file size: {size} bytes")
            
            # List all debug log files
            debug_files = list_debug_log_files()
            print(f"  📂 Total debug log files: {len(debug_files)}")
            
        else:
            print("  ❌ Debug log file not created")
            
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def test_docker_build():
    """Test that Docker builds with debug support"""
    print("\n🧪 Testing Docker Debug Support")
    print("=" * 50)
    
    # Check if docker-compose.debug.yml exists
    if Path("docker-compose.debug.yml").exists():
        print("  ✅ docker-compose.debug.yml exists")
        
        # Validate the file contains debug configuration
        with open("docker-compose.debug.yml", "r") as f:
            content = f.read()
            if "AUTODIDACT_DEBUG=true" in content:
                print("  ✅ Debug environment variable configured")
            else:
                print("  ❌ Debug environment variable not found")
                
            if "--debug" in content:
                print("  ✅ Debug flag in entrypoint")
            else:
                print("  ❌ Debug flag not found in entrypoint")
                
    else:
        print("  ❌ docker-compose.debug.yml not found")

def main():
    """Run all tests"""
    print("🚀 Autodidact Debug Functionality Test Suite")
    print("=" * 60)
    
    # Change to the repository directory
    os.chdir(Path(__file__).parent)
    
    test_debug_flag_parsing()
    test_debug_log_creation()
    test_docker_build()
    
    print("\n🎯 Test Summary")
    print("=" * 60)
    print("Debug functionality tests completed!")
    print("Check output above for any ❌ failures that need attention.")

if __name__ == "__main__":
    main()