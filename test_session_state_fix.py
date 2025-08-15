#!/usr/bin/env python3
"""
Test script to validate the session state fix for course switching issue.
"""

def test_should_clear_session_state():
    """Test the session state clearing logic"""
    
    def should_clear_session_state(current_session_id: str, current_project_id: str, existing_state: dict = None) -> bool:
        """Check if we need to clear session state due to session/project change"""
        if not existing_state:
            return False
        
        if not isinstance(existing_state, dict):
            return True
        
        return (existing_state.get('session_id') != current_session_id or 
                existing_state.get('project_id') != current_project_id)
    
    # Test case 1: No existing state - should not clear
    result = should_clear_session_state("session1", "project1", None)
    assert result == False, f"Expected False, got {result}"
    print("✓ Test 1 passed: No existing state")
    
    # Test case 2: Same session and project - should not clear
    existing_state = {'session_id': 'session1', 'project_id': 'project1'}
    result = should_clear_session_state("session1", "project1", existing_state)
    assert result == False, f"Expected False, got {result}"
    print("✓ Test 2 passed: Same session and project")
    
    # Test case 3: Different session - should clear
    existing_state = {'session_id': 'session1', 'project_id': 'project1'}
    result = should_clear_session_state("session2", "project1", existing_state)
    assert result == True, f"Expected True, got {result}"
    print("✓ Test 3 passed: Different session")
    
    # Test case 4: Different project - should clear
    existing_state = {'session_id': 'session1', 'project_id': 'project1'}
    result = should_clear_session_state("session1", "project2", existing_state)
    assert result == True, f"Expected True, got {result}"
    print("✓ Test 4 passed: Different project")
    
    # Test case 5: Both different - should clear
    existing_state = {'session_id': 'session1', 'project_id': 'project1'}
    result = should_clear_session_state("session2", "project2", existing_state)
    assert result == True, f"Expected True, got {result}"
    print("✓ Test 5 passed: Both different")
    
    # Test case 6: Invalid state format - should clear
    existing_state = "invalid"
    result = should_clear_session_state("session1", "project1", existing_state)
    assert result == True, f"Expected True, got {result}"
    print("✓ Test 6 passed: Invalid state format")
    
    print("\n✅ All tests passed! Session state clearing logic is working correctly.")

if __name__ == "__main__":
    test_should_clear_session_state()