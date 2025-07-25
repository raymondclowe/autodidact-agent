#!/usr/bin/env python3
"""
Test to verify the debug flag wrapper functionality works.
"""
import subprocess
import os

def test_basic_functionality():
    """Test the basic functionality without starting Streamlit fully."""
    print("🧪 Testing debug flag wrapper functionality...\n")
    
    # Test 1: Original command should fail
    print("1. Testing original command (should fail):")
    result = subprocess.run(
        ['streamlit', 'run', 'app.py', '--debug'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode != 0 and "No such option: --debug" in result.stderr:
        print("   ✅ Original command fails as expected")
    else:
        print(f"   ❌ Unexpected result: {result.stderr}")
        return False
    
    # Test 2: Wrapper script help
    print("\n2. Testing wrapper script help:")
    result = subprocess.run(
        ['python', 'run.py', '--help'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("   ✅ Wrapper script help works")
    else:
        print(f"   ❌ Help failed: {result.stderr}")
        return False
    
    # Test 3: Environment variable approach still works
    print("\n3. Testing environment variable approach:")
    env = os.environ.copy()
    env['AUTODIDACT_DEBUG'] = 'true'
    
    result = subprocess.run(
        ['python', '-c', 'from app import DEBUG_MODE; print("DEBUG_MODE:", DEBUG_MODE)'],
        capture_output=True,
        text=True,
        env=env,
        timeout=10
    )
    
    if result.returncode == 0 and "DEBUG_MODE: True" in result.stdout:
        print("   ✅ Environment variable method works")
    else:
        print(f"   ❌ Environment variable test failed: {result.stderr}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)