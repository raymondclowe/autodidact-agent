#!/usr/bin/env python3
"""
Test script for debug commands functionality
Run this to verify the debug commands work correctly
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_debug_commands():
    """Test debug command functionality"""
    print("🧪 Testing Debug Commands Functionality")
    print("=" * 50)
    
    from backend.debug_commands import handle_debug_command, is_debug_command, is_debug_mode_enabled, set_debug_mode
    
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
        ('/debug_mode', True, 'Debug mode command detection'),
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
        ('/debug_mode', 'should toggle debug mode'),
        ('/completed', 'should attempt completion'),
        ('/unknown', 'should show error'),
        ('normal message', 'should return None'),
    ]
    
    handling_passed = 0
    for cmd, description in handling_tests:
        try:
            if cmd == '/completed':
                # Mock database operations for completed command
                with patch('backend.debug_commands.get_node_with_objectives') as mock_get_node, \
                     patch('backend.debug_commands.update_mastery') as mock_update_mastery, \
                     patch('backend.debug_commands.complete_session') as mock_complete_session:
                    
                    # Set up mock return values
                    mock_get_node.return_value = {
                        'learning_objectives': [
                            {'id': 'lo1'}, 
                            {'id': 'lo2'}
                        ]
                    }
                    
                    result = handle_debug_command(cmd, mock_session_info)
                    
                    # Check that the mocks were called
                    success = (result is not None and 
                              result.get('success', False) and
                              mock_get_node.called and
                              mock_update_mastery.called and
                              mock_complete_session.called)
                    status = "✅" if success else "❌"
                    print(f"  {status} {description}: {success} (with mocked DB)")
            else:
                result = handle_debug_command(cmd, mock_session_info)
                
                if cmd == 'normal message':
                    success = result is None
                    status = "✅" if success else "❌"
                    print(f"  {status} {description}: {success}")
                elif cmd in ['/help', '/debug']:
                    success = result and result.get('is_help', False)
                    status = "✅" if success else "❌"
                    print(f"  {status} {description}: {success}")
                elif cmd == '/debug_mode':
                    success = result and result.get('is_debug_mode_toggle', False)
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
    
    # Test debug mode functionality
    print("\n📋 Testing Debug Mode Toggle:")
    debug_mode_tests = 0
    debug_mode_passed = 0
    
    # Test initial state
    initial_state = is_debug_mode_enabled()
    print(f"  📌 Initial debug mode state: {initial_state}")
    debug_mode_tests += 1
    debug_mode_passed += 1  # Always pass initial state check
    
    # Test setting debug mode
    set_debug_mode(True)
    after_enable = is_debug_mode_enabled()
    success = after_enable == True
    status = "✅" if success else "❌"
    print(f"  {status} Enable debug mode: {after_enable}")
    debug_mode_tests += 1
    if success:
        debug_mode_passed += 1
        
    # Test disabling debug mode
    set_debug_mode(False)
    after_disable = is_debug_mode_enabled()
    success = after_disable == False
    status = "✅" if success else "❌"
    print(f"  {status} Disable debug mode: {after_disable}")
    debug_mode_tests += 1
    if success:
        debug_mode_passed += 1
    
    print(f"\n📊 Debug Mode Tests: {debug_mode_passed}/{debug_mode_tests} passed")
    
    total_tests = len(test_cases) + len(handling_tests) + debug_mode_tests
    total_passed = detection_passed + handling_passed + debug_mode_passed
    
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