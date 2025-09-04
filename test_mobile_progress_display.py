#!/usr/bin/env python3
"""Test mobile-friendly progress indicators for issue #128."""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import Objective, SessionState, get_objectives_progress_info


def test_progress_info_generation():
    """Test that progress info is generated correctly for display."""
    print("🧪 Testing progress info generation...")
    
    # Create sample objectives
    obj1 = Objective(id='1', description='Learn basic concepts', mastery=0.8)
    obj2 = Objective(id='2', description='Practice solving problems', mastery=0.5)
    obj3 = Objective(id='3', description='Review and understand theory', mastery=0.3)
    obj4 = Objective(id='4', description='Apply knowledge to new situations', mastery=0.2)
    
    # Create session state with progress
    state: SessionState = {
        'objectives_to_teach': [obj1, obj2, obj3, obj4],
        'objective_idx': 2,  # Currently on third objective
        'completed_objectives': ['1', '2'],  # First two completed
        'current_phase': 'teaching'
    }
    
    # Test progress info generation
    progress_info = get_objectives_progress_info(state)
    
    print(f"✅ Progress info: {progress_info}")
    
    # Verify the data structure
    assert progress_info['total'] == 4, f"Expected 4 total objectives, got {progress_info['total']}"
    assert progress_info['completed_count'] == 2, f"Expected 2 completed, got {progress_info['completed_count']}"
    assert progress_info['current_index'] == 2, f"Expected current index 2, got {progress_info['current_index']}"
    
    # Verify individual items
    items = progress_info['items']
    assert len(items) == 4, f"Expected 4 items, got {len(items)}"
    
    # Check statuses
    assert items[0]['status'] == 'completed', f"First item should be completed, got {items[0]['status']}"
    assert items[1]['status'] == 'completed', f"Second item should be completed, got {items[1]['status']}"
    assert items[2]['status'] == 'current', f"Third item should be current, got {items[2]['status']}"
    assert items[3]['status'] == 'upcoming', f"Fourth item should be upcoming, got {items[3]['status']}"
    
    print("✅ Progress info structure is correct")
    return progress_info


def test_compact_progress_text():
    """Test the compact progress text format for mobile."""
    print("🧪 Testing compact progress text format...")
    
    progress_info = test_progress_info_generation()
    
    # Test the format used in display_lesson_progress_compact
    progress_text = f"📊 {progress_info['completed_count']} out of {progress_info['total']} objectives completed"
    expected_text = "📊 2 out of 4 objectives completed"
    
    assert progress_text == expected_text, f"Expected '{expected_text}', got '{progress_text}'"
    
    print(f"✅ Compact progress text: '{progress_text}'")
    
    # Test progress percentage
    progress_percentage = (progress_info["completed_count"] / progress_info["total"]) * 100
    expected_percentage = 50.0
    
    assert progress_percentage == expected_percentage, f"Expected {expected_percentage}%, got {progress_percentage}%"
    
    print(f"✅ Progress percentage: {progress_percentage}%")


def test_should_show_progress_conditions():
    """Test when progress tracking should be shown."""
    print("🧪 Testing progress display conditions...")
    
    from components.lesson_progress import should_show_progress_tracking
    
    # Test with objectives and teaching phase
    state_with_objectives: SessionState = {
        'objectives_to_teach': [
            Objective(id='1', description='Test', mastery=0.5)
        ],
        'current_phase': 'teaching'
    }
    
    should_show = should_show_progress_tracking(state_with_objectives)
    assert should_show, "Should show progress when objectives exist and in teaching phase"
    print("✅ Shows progress during teaching phase with objectives")
    
    # Test with no objectives
    state_no_objectives: SessionState = {
        'objectives_to_teach': [],
        'current_phase': 'teaching'
    }
    
    should_show = should_show_progress_tracking(state_no_objectives)
    assert not should_show, "Should not show progress when no objectives exist"
    print("✅ Hides progress when no objectives")
    
    # Test with wrong phase
    state_wrong_phase: SessionState = {
        'objectives_to_teach': [
            Objective(id='1', description='Test', mastery=0.5)
        ],
        'current_phase': 'intro'
    }
    
    should_show = should_show_progress_tracking(state_wrong_phase)
    assert not should_show, "Should not show progress in intro phase"
    print("✅ Hides progress during intro phase")


if __name__ == "__main__":
    print("🚀 Testing mobile progress display functionality...\n")
    
    test_progress_info_generation()
    print()
    
    test_compact_progress_text()
    print()
    
    test_should_show_progress_conditions()
    print()
    
    print("✨ All mobile progress display tests passed!")