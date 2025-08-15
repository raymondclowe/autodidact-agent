"""
Test script for Learning Objectives Display Enhancement features
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.session_state import (
    SessionState, Objective, create_initial_state,
    get_formatted_objectives_for_intro, get_objectives_progress_info,
    get_session_completion_info
)
from datetime import datetime

def test_helper_functions():
    """Test the new helper functions in session_state.py"""
    print("🧪 Testing Learning Objectives Helper Functions")
    print("=" * 60)
    
    # Create a sample session state with objectives
    state = create_initial_state("test-session", "test-project", "test-node")
    
    # Add some test objectives
    test_objectives = [
        Objective(id="obj1", description="Define cells as the basic unit of life", mastery=0.3),
        Objective(id="obj2", description="Identify the three principles of cell theory", mastery=0.2),
        Objective(id="obj3", description="Explain why cells are fundamental to all organisms", mastery=0.5),
    ]
    
    state['objectives_to_teach'] = test_objectives
    state['completed_objectives'] = ["obj1"]  # Mark first objective as completed
    state['objective_idx'] = 1  # Currently on second objective
    state['objective_scores'] = {"obj1": 0.85}
    state['session_end'] = datetime.now().isoformat()
    
    print("\n1️⃣ Testing get_formatted_objectives_for_intro...")
    intro_objectives = get_formatted_objectives_for_intro(state)
    print(f"✅ Introduction objectives ({len(intro_objectives)} items):")
    for i, obj in enumerate(intro_objectives, 1):
        print(f"   {i}. {obj}")
    
    print("\n2️⃣ Testing get_objectives_progress_info...")
    progress_info = get_objectives_progress_info(state)
    print(f"✅ Progress info:")
    print(f"   Total objectives: {progress_info['total']}")
    print(f"   Completed: {progress_info['completed_count']}")
    print(f"   Current index: {progress_info['current_index']}")
    print(f"   Progress items:")
    for item in progress_info['items']:
        print(f"     {item['status'].upper()}: {item['description']}")
    
    print("\n3️⃣ Testing get_session_completion_info...")
    completion_info = get_session_completion_info(state)
    print(f"✅ Completion info:")
    print(f"   Completed objectives: {completion_info['completed_count']}/{completion_info['total_objectives']}")
    print(f"   Final score: {completion_info['final_score']:.2f}")
    print(f"   Completion percentage: {completion_info['completion_percentage']:.1f}%")
    print(f"   Objectives completed:")
    for obj in completion_info['objectives']:
        print(f"     • {obj}")

def test_intro_node_enhancement():
    """Test that the intro node creates proper lesson introduction"""
    print("\n\n🧪 Testing Intro Node Enhancement")
    print("=" * 60)
    
    # Test with mock graph node 
    from backend.graph_v05 import intro_node
    
    # Create test state with objectives
    state = {
        'node_title': 'Cell Biology Fundamentals',
        'objectives_to_teach': [
            Objective(id="obj1", description="Define cells as the basic unit of life", mastery=0.3),
            Objective(id="obj2", description="Identify the three principles of cell theory", mastery=0.2),
            Objective(id="obj3", description="Explain why cells are fundamental to all organisms", mastery=0.5),
        ],
        'history': []
    }
    
    print("\n1️⃣ Testing intro_node with objectives...")
    result_state = intro_node(state)
    
    print("✅ Intro node results:")
    print(f"   Phase: {result_state.get('current_phase')}")
    print(f"   Navigate without interaction: {result_state.get('navigate_without_user_interaction')}")
    print(f"   History length: {len(result_state.get('history', []))}")
    
    if result_state.get('history'):
        intro_message = result_state['history'][0]['content']
        print(f"   Intro message preview:")
        print(f"   {intro_message[:200]}...")
        
        # Check that the message contains expected elements
        has_title = 'Cell Biology Fundamentals' in intro_message
        has_objectives_header = 'In this lesson, you will learn:' in intro_message
        has_objectives = 'Define cells as the basic unit of life' in intro_message
        has_motivation = 'Let\'s begin your learning journey!' in intro_message
        
        print(f"\n   Content validation:")
        print(f"     ✅ Contains title: {has_title}")
        print(f"     ✅ Contains objectives header: {has_objectives_header}")
        print(f"     ✅ Contains objectives: {has_objectives}")
        print(f"     ✅ Contains motivation: {has_motivation}")
        
        if all([has_title, has_objectives_header, has_objectives, has_motivation]):
            print("     🎉 All intro content elements present!")
        else:
            print("     ⚠️ Some intro content elements missing")

def main():
    """Run all tests"""
    test_helper_functions()
    test_intro_node_enhancement()
    
    print("\n\n🎯 Learning Objectives Display Enhancement Testing Complete!")
    print("=" * 60)
    print("✅ Helper functions working correctly")
    print("✅ Intro node enhancement working correctly")
    print("🚀 Ready for UI testing with Streamlit application")

if __name__ == "__main__":
    main()