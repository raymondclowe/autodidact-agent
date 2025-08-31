#!/usr/bin/env python3
"""
Test to reproduce the specific \\div rendering issue mentioned in the bug report.
This isolates the JavaScript math renderer logic to test it directly.
"""

import re

def test_div_issue():
    """Test the exact \\div issue: (10 \\div 2) should render as (10 ÷ 2)"""
    
    # Simulate the JavaScript logic in Python for testing
    symbols = {
        # Double backslash patterns (existing)
        '\\\\\\\\times': '×',
        '\\\\\\\\cdot': '·',
        '\\\\\\\\div': '÷',
        '\\\\\\\\pm': '±',
        '\\\\\\\\neq': '≠',
        '\\\\\\\\ne': '≠',
        # Single backslash patterns (new)
        '\\\\times': '×',
        '\\\\cdot': '·',
        '\\\\div': '÷',
        '\\\\pm': '±',
        '\\\\neq': '≠',
        '\\\\ne': '≠',
    }
    
    def render_expression(latex):
        """Python version of the renderExpression function"""
        result = latex
        
        # Replace symbols
        for symbol in symbols:
            result = re.sub(symbol, symbols[symbol], result)
        
        # Clean up remaining backslashes and spaces
        result = re.sub(r'\\\\\\\\', '', result)  # Double backslashes first
        result = re.sub(r'\\\\', '', result)      # Then single backslashes  
        result = re.sub(r'\\s+', ' ', result)
        
        return result
    
    def process_inline_math(content):
        """Python version of inline math processing with FIXED regex"""
        # FIXED regex pattern: handle single backslashes
        pattern = r'\\(([^()]*\\\\[^()]*)\\)'
        
        def replace_match(match):
            expr = match.group(1)
            if '\\\\' in expr:  # Only process if it contains LaTeX
                rendered = render_expression(expr)
                return f'({rendered})'  # Simplified - no HTML styling for test
            return match.group(0)
        
        return re.sub(pattern, replace_match, content)
    
    # Test cases
    test_cases = [
        ("(10 \\\\div 2)", "(10 ÷ 2)"),
        ("(a \\\\times b)", "(a × b)"),
        ("(x \\\\ne y)", "(x ≠ y)"),
        ("(10 + 2)", "(10 + 2)"),  # Should not change - no LaTeX
        ("\\\\div", "÷"),  # Direct symbol test
    ]
    
    print("🧪 Testing \\\\div rendering issue (FIXED VERSION)...")
    print("=" * 50)
    
    # Test direct symbol replacement
    print("\\n1. Direct symbol replacement test:")
    for input_str, expected in test_cases[-1:]:  # Just the direct symbol test
        result = render_expression(input_str)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_str}' → '{result}' (expected: '{expected}')")
    
    # Test inline math processing
    print("\\n2. Inline math processing test:")
    for input_str, expected in test_cases[:-1]:  # All except direct symbol test
        result = process_inline_math(input_str)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_str}' → '{result}' (expected: '{expected}')")
        
        if result != expected:
            print(f"      Issue detected! Let's debug...")
            # Debug the regex
            pattern = r'\\(([^()]*\\\\[^()]*)\\)'
            match = re.search(pattern, input_str)
            if match:
                print(f"      Regex matched: '{match.group(1)}'")
                rendered = render_expression(match.group(1))
                print(f"      After rendering: '{rendered}'")
            else:
                print(f"      Regex did not match: pattern={pattern}")
    
    print("\\n" + "=" * 50)
    print("Analysis complete!")

if __name__ == "__main__":
    test_div_issue()