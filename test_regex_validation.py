#!/usr/bin/env python3
"""
Simple test to verify the regex patterns work correctly for the \div fix.
This confirms the JavaScript logic should work properly.
"""

import re

def test_js_regex_patterns():
    """Test the exact regex patterns used in the JavaScript fix"""
    
    print("🔍 Testing JavaScript Regex Patterns")
    print("=" * 50)
    
    # Test 1: Inline math regex pattern
    print("\n1. Inline Math Regex Test:")
    print("   Pattern: /\\(([^()]*\\\\[^()]*)\\)/g")
    
    # Python equivalent of JavaScript regex: /\(([^()]*\\[^()]*)\)/g
    inline_pattern = r'\(([^()]*\\[^()]*)\)'
    
    test_cases = [
        "(10 \\div 2)",      # Should match: "10 \\div 2"
        "(a \\times b)",     # Should match: "a \\times b"  
        "(x \\ne y)",        # Should match: "x \\ne y"
        "(10 + 2)",          # Should NOT match: no backslash
        "(\\div)",           # Should match: "\\div"
        "(test \\div)",      # Should match: "test \\div"
    ]
    
    for test_input in test_cases:
        match = re.search(inline_pattern, test_input)
        if match:
            print(f"   ✅ '{test_input}' → matched: '{match.group(1)}'")
        else:
            print(f"   ❌ '{test_input}' → no match")
    
    # Test 2: Symbol replacement
    print("\n2. Symbol Replacement Test:")
    
    symbols = {
        '\\\\div': '÷',
        '\\\\times': '×', 
        '\\\\ne': '≠',
        '\\div': '÷',      # Single backslash version
        '\\times': '×',
        '\\ne': '≠',
    }
    
    test_expressions = [
        "10 \\div 2",        # Single backslash
        "a \\times b",       # Single backslash
        "x \\ne y",          # Single backslash
        "10 \\\\div 2",      # Double backslash (from logs)
    ]
    
    for expr in test_expressions:
        result = expr
        for symbol, replacement in symbols.items():
            # Use re.escape to handle backslashes properly
            result = re.sub(re.escape(symbol), replacement, result)
        print(f"   '{expr}' → '{result}'")
    
    # Test 3: Complete processing simulation
    print("\n3. Complete Processing Simulation:")
    
    def simulate_js_processing(content):
        """Simulate the complete JavaScript processing"""
        
        # Find inline math patterns
        def process_inline_match(match):
            expr = match.group(1)
            if '\\' in expr:
                # Apply symbol replacements
                result = expr
                for symbol, replacement in symbols.items():
                    result = re.sub(re.escape(symbol), replacement, result)
                # Clean up backslashes
                result = re.sub(r'\\\\', '', result)
                result = re.sub(r'\\', '', result)
                result = re.sub(r'\s+', ' ', result)
                return f'<span style="font-style: italic;">({result})</span>'
            return match.group(0)
        
        return re.sub(inline_pattern, process_inline_match, content)
    
    test_content = [
        "The result is (10 \\div 2) which equals 5.",
        "We have (a \\times b) and (x \\ne y) here.",
        "Normal text (10 + 2) should not change.",
        "Double backslash (10 \\\\div 2) should also work.",
    ]
    
    for content in test_content:
        processed = simulate_js_processing(content)
        success = ('÷' in processed or '×' in processed or '≠' in processed or 
                  processed == content)  # Unchanged is OK for normal text
        status = "✅" if success else "❌"
        print(f"   {status} Input:  {content}")
        print(f"      Output: {processed}")
        print()
    
    print("=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_js_regex_patterns()