#!/usr/bin/env python3
"""Debug script to test LLM response structure"""

from backend.graph_v05 import get_llm

def test_llm_response():
    try:
        llm = get_llm()
        if not llm:
            print("ERROR: LLM is None")
            return
            
        print(f"LLM type: {type(llm)}")
        
        # Test invoke
        response = llm.invoke([{"role": "user", "content": "Hello"}])
        print(f"Response type: {type(response)}")
        print(f"Response dir: {dir(response)}")
        
        # Try to access content
        try:
            content = response.content
            print(f"Content: {content}")
        except Exception as e:
            print(f"Error accessing response.content: {e}")
            print(f"Error type: {type(e)}")
            
        # Try different attributes
        for attr in ['content', 'text', 'message', 'choices']:
            if hasattr(response, attr):
                print(f"Has attribute '{attr}': {getattr(response, attr)}")
                
    except Exception as e:
        print(f"Error in test_llm_response: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_response()
