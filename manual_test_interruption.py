#!/usr/bin/env python3
"""Manual testing guide and simulation for session interruption functionality."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import create_initial_state, detect_session_interruption


def demonstrate_interruption_scenarios():
    """Demonstrate different interruption scenarios"""
    print("🎭 Session Interruption Demonstration")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Short Break (5 minutes)",
            "minutes_away": 5,
            "threshold": 10,
            "expected_interrupted": False
        },
        {
            "name": "Coffee Break (15 minutes)", 
            "minutes_away": 15,
            "threshold": 10,
            "expected_interrupted": True
        },
        {
            "name": "Lunch Break (45 minutes)",
            "minutes_away": 45,
            "threshold": 10,
            "expected_interrupted": True
        },
        {
            "name": "Overnight (8 hours)",
            "minutes_away": 480,
            "threshold": 10,
            "expected_interrupted": True
        },
        {
            "name": "Weekend (2 days)",
            "minutes_away": 2880,
            "threshold": 10,
            "expected_interrupted": True
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print(f"   Time away: {scenario['minutes_away']} minutes")
        
        # Create a session state with the timestamp
        state = create_initial_state("test_session", "test_project", "test_node")
        state["last_message_ts"] = (datetime.now() - timedelta(minutes=scenario['minutes_away'])).isoformat()
        
        # Check for interruption
        was_interrupted, minutes = detect_session_interruption(state, threshold_minutes=scenario['threshold'])
        
        # Format the time nicely
        if minutes < 60:
            time_str = f"{minutes:.0f} minutes"
        elif minutes < 1440:
            hours = minutes // 60
            remainder = minutes % 60
            time_str = f"{hours:.0f}h {remainder:.0f}m"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            time_str = f"{days:.0f}d {hours:.0f}h"
        
        status = "🔄 INTERRUPTED" if was_interrupted else "✅ ACTIVE"
        expected_status = "✅ CORRECT" if was_interrupted == scenario['expected_interrupted'] else "❌ UNEXPECTED"
        
        print(f"   Result: {status} after {time_str} {expected_status}")


def demonstrate_welcome_messages():
    """Demonstrate welcome back message generation"""
    print("\n\n🎭 Welcome Back Message Demonstration")
    print("=" * 50)
    
    def generate_welcome_message(minutes_away, node_title, completed_objectives=None):
        """Simulate welcome back message generation"""
        if completed_objectives is None:
            completed_objectives = []
            
        if minutes_away < 60:
            time_str = f"{minutes_away:.0f} minutes"
        elif minutes_away < 1440:
            hours = minutes_away // 60
            time_str = f"{hours:.0f} hours"
        else:
            days = minutes_away // 1440
            time_str = f"{days:.0f} days"
        
        message = f"# 🔄 **Welcome back to: {node_title}**\n\n"
        message += f"I notice you've been away for about {time_str}. No worries – let me help you get back on track! 📚\n\n"
        
        if completed_objectives:
            message += "**📋 What we've covered so far:**\n"
            for obj in completed_objectives:
                message += f"✅ {obj}\n"
            message += "\n"
        
        message += "**Welcome back! Are you ready to continue where we left off?** 🚀"
        return message
    
    scenarios = [
        {
            "name": "Short Study Break",
            "minutes": 20,
            "session": "Introduction to Python",
            "completed": ["Understanding variables", "Basic data types"]
        },
        {
            "name": "Lunch Break",
            "minutes": 60,
            "session": "JavaScript Fundamentals", 
            "completed": ["Function declarations", "Scope and closures"]
        },
        {
            "name": "Overnight Session",
            "minutes": 720,  # 12 hours
            "session": "Machine Learning Basics",
            "completed": ["Linear regression", "Data preprocessing", "Model evaluation"]
        },
        {
            "name": "Weekend Break",
            "minutes": 2160,  # 36 hours
            "session": "Advanced React Patterns",
            "completed": []
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📝 {scenario['name']} - {scenario['session']}")
        print("-" * 60)
        
        message = generate_welcome_message(
            scenario['minutes'], 
            scenario['session'], 
            scenario['completed']
        )
        
        # Show first few lines of the message
        lines = message.split('\n')
        for i, line in enumerate(lines[:6]):
            print(f"   {line}")
        if len(lines) > 6:
            print(f"   ... ({len(lines) - 6} more lines)")


def print_manual_testing_guide():
    """Print manual testing instructions"""
    print("\n\n📋 Manual Testing Guide")
    print("=" * 50)
    
    guide = """
To manually test the interruption functionality:

1. **Start a Session:**
   - Navigate to a project and start a lesson
   - Send a message to begin the session
   - Verify you see the normal welcome message

2. **Simulate Short Interruption:**
   - Close the browser tab (or navigate away)
   - Wait 1-2 minutes
   - Return to the session URL
   - Should NOT show welcome back message (under 10 min threshold)

3. **Simulate Long Interruption:**
   - Start or continue a session
   - Send a message to establish activity
   - Close browser and wait 15+ minutes
   - Return to the session URL
   - Should show "Welcome back" message with time away

4. **Test Different Time Periods:**
   - Try interruptions of: 15 min, 1 hour, 1 day
   - Verify appropriate welcome messages and time formatting

5. **Test Progress Tracking:**
   - Complete some objectives in a session
   - Interrupt for 15+ minutes
   - Return and verify welcome message shows completed work

6. **Test AI Context Awareness:**
   - After returning from interruption, interact with AI
   - Verify AI responds appropriately to returning student
   - Check that AI mentions the break naturally

Expected Behaviors:
✅ Interruptions < 10 minutes: Normal session continuation
✅ Interruptions ≥ 10 minutes: Welcome back message with context
✅ AI receives interruption context in prompts
✅ Timestamps update correctly on user/assistant messages
✅ State persists across browser sessions
✅ Progress is preserved and displayed on return
"""
    print(guide)


if __name__ == "__main__":
    demonstrate_interruption_scenarios()
    demonstrate_welcome_messages()
    print_manual_testing_guide()
    print("\n✨ Demonstration completed! Ready for manual testing.")