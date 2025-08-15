"""
Test the new debug commands for objective advancement
"""

import sys
import os
sys.path.append('/workspaces/autodidact-agent')

def test_debug_commands():
    """Test the new debug command functionality"""
    
    print("🔧 Testing New Debug Commands")
    print("=" * 50)
    
    try:
        from backend.debug_commands import handle_debug_command, is_debug_command
        
        # Test command detection
        print("1. Testing command detection...")
        
        test_messages = [
            "/next",
            "/got_it", 
            "/understood",
            "/completed",
            "/help",
            "regular message",
            "/invalid_command"
        ]
        
        for msg in test_messages:
            is_debug = is_debug_command(msg)
            print(f"   '{msg}' -> Debug command: {is_debug}")
        
        # Test objective advancement
        print("\n2. Testing objective advancement command...")
        
        mock_session_info = {
            'id': 'test_session_123',
            'node_id': 'test_node_456',
            'project_id': 'test_project_789'
        }
        
        for cmd in ["/next", "/got_it", "/understood"]:
            result = handle_debug_command(cmd, mock_session_info)
            
            if result:
                print(f"\n   Command: {cmd}")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Is Objective Advancement: {result.get('is_objective_advancement')}")
                print(f"   Inject Control Block: {result.get('inject_control_block')}")
                
                if result.get('simulated_ai_message'):
                    print(f"   Simulated AI Message: {result['simulated_ai_message'][:100]}...")
            else:
                print(f"   Command {cmd} returned None")
        
        # Test help command
        print("\n3. Testing help command...")
        
        help_result = handle_debug_command("/help", mock_session_info)
        if help_result and help_result.get('success'):
            print("   ✅ Help command working")
            print(f"   Message contains '/next': {'/next' in help_result['message']}")
            print(f"   Message contains '/got_it': {'/got_it' in help_result['message']}")
            print(f"   Message contains '/understood': {'/understood' in help_result['message']}")
        else:
            print("   ❌ Help command failed")
        
        # Test session completion
        print("\n4. Testing session completion command...")
        
        completion_result = handle_debug_command("/completed", mock_session_info)
        if completion_result:
            print(f"   Success: {completion_result.get('success')}")
            print(f"   Is Debug Completion: {completion_result.get('is_debug_completion')}")
            if completion_result.get('success'):
                print("   ✅ Session completion command working")
            else:
                print(f"   ❌ Session completion failed: {completion_result.get('error')}")
        
        print("\n✅ All debug command tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing debug commands: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage_instructions():
    """Show how to use the new debug commands"""
    
    print("\n" + "=" * 50)
    print("📖 USAGE INSTRUCTIONS")
    print("=" * 50)
    
    print("""
🎯 **NEW OBJECTIVE ADVANCEMENT COMMANDS**

During any active learning session, you can now use:

• `/next` - Mark current learning point as understood and move to next
• `/got_it` - Same as /next, more natural language
• `/understood` - Same as /next, alternative phrasing

🔧 **EXISTING DEBUG COMMANDS**

• `/completed` - Force complete entire session with high score
• `/help` or `/debug` - Show all available debug commands
• `/debug_mode` - Toggle detailed debug information

📋 **USAGE EXAMPLES**

1. **During Teaching Session:**
   Student: "I understand photosynthesis now"
   Developer: `/got_it`
   Result: Moves to next learning objective

2. **During Recap Session:**
   AI: "Can you explain the three principles of cell theory?"
   Developer: `/understood`
   Result: Marks objective complete, moves forward

3. **Quick Session Completion:**
   Developer: `/completed`
   Result: Completes entire session with 85% score

🎯 **BENEFITS FOR DEBUGGING**

• **Faster Iteration**: Skip through content you've already verified
• **Focused Testing**: Test specific parts of lesson flow
• **Development Speed**: Quickly reach problem areas in lessons
• **Granular Control**: Skip individual concepts vs entire sessions

⚠️ **IMPORTANT NOTES**

• These commands mark objectives as "mastered" in the database
• Use only for development/testing purposes
• Progression affects subsequent lesson availability
• Debug completions use hardcoded scores, not AI evaluation
""")

if __name__ == "__main__":
    success = test_debug_commands()
    
    if success:
        show_usage_instructions()
        print("\n🚀 **Debug Commands Ready for Use!**")
        print("\nNext time you're in a learning session, try:")
        print("• Type `/next` to skip to next learning point")
        print("• Type `/help` to see all available commands")
        print("• Type `/completed` to finish entire session")
    else:
        print("\n❌ Debug command tests failed - please check implementation")
