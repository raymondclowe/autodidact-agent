#!/usr/bin/env python3
"""
Demo script showing how debug commands work in action
This simulates the debug command functionality without requiring a full session
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def demo_debug_commands():
    """Demonstrate debug command functionality"""
    print("🎬 Debug Commands Demo - Autodidact Learning Session")
    print("=" * 60)
    
    from backend.debug_commands import handle_debug_command
    
    # Simulate a learning session
    mock_session = {
        'id': 'demo-session-001',
        'node_id': 'node-python-basics',
        'project_id': 'project-python-course',
        'node_label': 'Python Fundamentals',
        'project_topic': 'Learning Python Programming'
    }
    
    print(f"📚 Current Session: {mock_session['node_label']}")
    print(f"📖 Project: {mock_session['project_topic']}")
    print(f"🆔 Session ID: {mock_session['id']}")
    print()
    
    # Simulate chat conversation
    conversation = [
        "Hello! I'm ready to learn Python fundamentals.",
        "What are variables in Python?",
        "/help",
        "/debug_mode",
        "Can you explain functions?",
        "/completed"
    ]
    
    print("💬 Chat Conversation:")
    print("-" * 40)
    
    for i, message in enumerate(conversation, 1):
        print(f"👤 User: {message}")
        
        # Handle debug commands
        debug_result = handle_debug_command(message, mock_session)
        
        if debug_result:
            if debug_result['success']:
                if debug_result.get('is_help'):
                    print("🤖 Assistant: " + debug_result['message'].replace('\n', '\n             '))
                elif debug_result.get('is_debug_mode_toggle'):
                    print("🤖 Assistant: " + debug_result['message'].replace('\n', '\n             '))
                else:
                    print("🤖 Assistant: " + debug_result['message'])
                    print("🎉 Session completed with debug command!")
                    print(f"📊 Score: {int(debug_result['score'] * 100)}%")
                    if debug_result.get('debug_info'):
                        print("🔧 Debug Info:")
                        for key, value in debug_result['debug_info'].items():
                            print(f"   {key}: {value}")
                    print("🔄 Ready to move to next topic...")
                    break
            else:
                print(f"❌ Assistant: Error - {debug_result['error']}")
        else:
            # Simulate normal tutoring response
            responses = [
                "Great! Let's start learning Python. Python is a powerful programming language...",
                "Variables in Python are containers for storing data values...",
                "Functions are reusable blocks of code that perform specific tasks...",
            ]
            if i <= len(responses):
                print(f"🤖 Assistant: {responses[i-1]}")
        
        print()
    
    print("✅ Demo completed!")
    print("\n📋 Summary of Debug Features:")
    print("• `/completed` - Instantly complete current lesson with high score")
    print("• `/help` or `/debug` - Show available debug commands")
    print("• `/debug_mode` - Toggle debug mode to see detailed scoring info") 
    print("• Case-insensitive command detection")
    print("• Non-intrusive - only activates on specific commands")
    print("• Maintains learning progress and mastery scores")
    print("• Shows scoring methodology when debug mode is enabled")

if __name__ == "__main__":
    demo_debug_commands()