#!/usr/bin/env python3
"""
Test script for debug commands functionality
Run this to verify the debug commands work correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_debug_commands():
    """Test debug command functionality"""
    print("🧪 Testing Debug Commands Functionality")
    print("=" * 50)
    
    from backend.debug_commands import handle_debug_command, is_debug_command
    
    # Mock session info
    mock_session_info = {
        'id': 'test-session-123', 
        'node_id': 'test-node-456',
        'project_id': 'test-project-789'
    }
    
    # Test cases
    test_cases = [
        # Command detection tests
        ('/completed', True, 'Command detection'),
        ('/help', True, 'Command detection'),
        ('/debug', True, 'Command detection'),  
        ('/COMPLETED', True, 'Case insensitive'),
        ('/unknown', True, 'Unknown command detection'),
        ('normal message', False, 'Normal message detection'),
        ('What is /completed?', False, 'Message containing command'),
        
        # Command handling tests - these need actual session info
    ]
    
    print("\n📋 Testing Command Detection:")
    detection_passed = 0
    for cmd, expected, description in test_cases:
        result = is_debug_command(cmd)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {description}: '{cmd}' -> {result}")
        if result == expected:
            detection_passed += 1
    
    print(f"\n📊 Detection Tests: {detection_passed}/{len(test_cases)} passed")
    
    print("\n📋 Testing Command Handling:")
    handling_tests = [
        ('/help', 'should show help'),
        ('/debug', 'should show help'),
        ('/completed', 'should attempt completion'),
        ('/unknown', 'should show error'),
        ('normal message', 'should return None'),
    ]
    
    handling_passed = 0
    for cmd, description in handling_tests:
        try:
            result = handle_debug_command(cmd, mock_session_info)
            
            if cmd == 'normal message':
                success = result is None
                status = "✅" if success else "❌"
                print(f"  {status} {description}: {success}")
            elif cmd in ['/help', '/debug']:
                success = result and result.get('is_help', False)
                status = "✅" if success else "❌"
                print(f"  {status} {description}: {success}")
            elif cmd == '/completed':
                # Will fail with real database operations, but should return a result
                success = result is not None
                status = "✅" if success else "❌"
                print(f"  {status} {description}: {success}")
            elif cmd == '/unknown':
                success = result and not result.get('success', True)
                status = "✅" if success else "❌"
                print(f"  {status} {description}: {success}")
            
            if success:
                handling_passed += 1
                
        except Exception as e:
            print(f"  ❌ {description}: Exception - {e}")
    
    print(f"\n📊 Handling Tests: {handling_passed}/{len(handling_tests)} passed")
    
    total_tests = len(test_cases) + len(handling_tests)
    total_passed = detection_passed + handling_passed
    
    print(f"\n🎯 Overall Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! Debug commands are working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = test_debug_commands()
    sys.exit(0 if success else 1)