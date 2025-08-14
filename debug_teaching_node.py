#!/usr/bin/env python3
"""Debug script to test teaching node objective handling"""

from backend.graph_v05 import create_initial_state, load_context_node, teaching_node
from backend.session_state import Objective

def test_teaching_node():
    print("=== Testing teaching node objective handling ===")
    
    # Create a test state with mock objectives
    state = create_initial_state(
        session_id="test-session",
        project_id="test-project", 
        node_id="test-node"
    )
    
    # Add some mock objectives as Objective instances
    test_objectives = [
        Objective(id="obj1", description="Test objective 1", mastery=0.0, node_id="test-node"),
        Objective(id="obj2", description="Test objective 2", mastery=0.0, node_id="test-node"),
    ]
    
    state["objectives_to_teach"] = test_objectives
    state["all_objectives"] = test_objectives
    state["current_phase"] = "teaching"
    state["objective_idx"] = 0
    
    print(f"Test objectives type: {type(test_objectives[0])}")
    print(f"Test objectives attributes: {dir(test_objectives[0])}")
    print(f"Test objective .id: {test_objectives[0].id}")
    print(f"Test objective .description: {test_objectives[0].description}")
    
    # Test accessing the current objective like the teaching node does
    try:
        idx = state.get("objective_idx", 0)
        objectives = state.get("objectives_to_teach", [])
        current_obj = objectives[idx]
        
        print(f"Current obj type: {type(current_obj)}")
        print(f"Current obj id: {current_obj.id}")
        print(f"Current obj description: {current_obj.description}")
        
        # Test the format_teaching_prompt call
        from backend.tutor_prompts import format_teaching_prompt
        
        sys_prompt = format_teaching_prompt(
            obj_id=current_obj.id,
            obj_label=current_obj.description,
            recent=[],
            remaining=[],
            refs=[],
            learner_profile_context=""
        )
        
        print("Successfully created system prompt")
        print(f"Prompt length: {len(sys_prompt)}")
        
    except Exception as e:
        print(f"Error in objective handling: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_teaching_node()
