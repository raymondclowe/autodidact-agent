#!/usr/bin/env python3
"""
Final verification of the max_tokens fix
"""

import ast
import sys
from pathlib import Path

def extract_get_llm_function():
    """Extract and analyze the get_llm function from the source code"""
    file_path = Path(__file__).parent / "backend" / "graph_v05.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Parse the AST to analyze the function
    tree = ast.parse(content)
    
    # Find the get_llm function
    get_llm_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_llm":
            get_llm_func = node
            break
    
    if not get_llm_func:
        return None, "get_llm function not found"
    
    # Look for the llm_kwargs dictionary assignment
    llm_kwargs_dict = None
    for node in ast.walk(get_llm_func):
        if (isinstance(node, ast.Assign) and 
            len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and 
            node.targets[0].id == "llm_kwargs"):
            llm_kwargs_dict = node.value
            break
    
    if not llm_kwargs_dict or not isinstance(llm_kwargs_dict, ast.Dict):
        return None, "llm_kwargs dictionary not found"
    
    # Extract the keys and values from the dictionary
    kwargs = {}
    for key, value in zip(llm_kwargs_dict.keys, llm_kwargs_dict.values):
        if isinstance(key, ast.Constant):
            key_name = key.value
            if isinstance(value, ast.Constant):
                kwargs[key_name] = value.value
            elif isinstance(value, ast.Name):
                kwargs[key_name] = f"<variable: {value.id}>"
            else:
                kwargs[key_name] = f"<expression>"
    
    return kwargs, None

def main():
    """Verify the max_tokens fix"""
    print("🔍 Final Verification of Max Tokens Fix")
    print("=" * 45)
    
    kwargs, error = extract_get_llm_function()
    
    if error:
        print(f"❌ Error: {error}")
        return False
    
    print("📊 Analyzing llm_kwargs in get_llm function:")
    print()
    
    success = True
    expected_params = {
        "model_name": "<variable: chat_model>",
        "temperature": 0.7,
        "openai_api_key": "<variable: api_key>",
        "max_tokens": 4000
    }
    
    for param, expected_value in expected_params.items():
        if param in kwargs:
            actual_value = kwargs[param]
            if actual_value == expected_value:
                print(f"✅ {param}: {actual_value}")
            else:
                print(f"❌ {param}: expected {expected_value}, got {actual_value}")
                success = False
        else:
            print(f"❌ {param}: missing")
            success = False
    
    print()
    print("📋 All parameters in llm_kwargs:")
    for key, value in kwargs.items():
        status = "✅" if key in expected_params else "ℹ️"
        print(f"{status} {key}: {value}")
    
    print()
    print("🎯 Verification Results:")
    
    if success:
        print("✅ max_tokens parameter correctly added (4000)")
        print("✅ All required parameters present")
        print("✅ Parameter values are correct")
        print()
        print("📈 Impact Analysis:")
        print("  - 87.5% reduction from 32,000 to 4,000 tokens")
        print("  - Reasonable for lesson interactions")
        print("  - Prevents excessive API costs")
        print("  - Aligns with existing error handling (8k cap)")
        print()
        print("🎉 Fix successfully addresses Issue #124!")
    else:
        print("❌ Some parameters are missing or incorrect")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)