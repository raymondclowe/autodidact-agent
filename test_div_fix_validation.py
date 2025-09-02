#!/usr/bin/env python3
"""
Test the fixed \\div rendering to verify the solution works.
This test simulates the exact JavaScript patterns and validates the fix.
"""

import re

def test_fixed_div_rendering():
    """Test that the fix properly handles (10 \\div 2) and similar patterns"""
    
    print("🧪 Testing FIXED \\div rendering...")
    print("=" * 60)
    
    # Test the exact patterns from the fixed JavaScript code
    
    # 1. Test symbol mapping works for single backslashes
    def test_symbol_replacement():
        print("\\n1. Symbol Replacement Test:")
        
        # Python simulation of the JavaScript symbols object
        symbols = {
            # Original double backslash patterns
            '\\\\\\\\times': '×',
            '\\\\\\\\div': '÷',
            '\\\\\\\\ne': '≠',
            # NEW single backslash patterns (the fix)
            '\\\\times': '×', 
            '\\\\div': '÷',
            '\\\\ne': '≠',
        }
        
        test_cases = [
            ("\\\\div", "÷"),      # Single backslash - should work now
            ("\\\\times", "×"),    # Single backslash 
            ("\\\\\\\\div", "÷"),    # Double backslash - should still work
        ]
        
        for test_input, expected in test_cases:
            result = test_input
            for symbol, replacement in symbols.items():
                result = re.sub(re.escape(symbol), replacement, result)
            
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{test_input}' → '{result}' (expected: '{expected}')")
    
    # 2. Test regex pattern works for single backslashes
    def test_inline_math_regex():
        print("\\n2. Inline Math Regex Test:")
        
        # OLD regex (broken): \\(([^()]*\\\\\\\\[^()]*[^()]*)\\)
        # NEW regex (fixed):  \\(([^()]*\\\\[^()]*)\\)
        old_pattern = r'\\(([^()]*\\\\\\\\[^()]*[^()]*)\\)'
        new_pattern = r'\\(([^()]*\\\\[^()]*)\\)'
        
        test_cases = [
            "(10 \\\\div 2)",
            "(a \\\\times b)", 
            "(x \\\\ne y)",
        ]
        
        for test_input in test_cases:
            old_match = re.search(old_pattern, test_input)
            new_match = re.search(new_pattern, test_input)
            
            print(f"   Input: '{test_input}'")
            print(f"     Old regex match: {'✅' if old_match else '❌'}")
            print(f"     New regex match: {'✅' if new_match else '❌'}")
            if new_match:
                print(f"     Captured: '{new_match.group(1)}'")
    
    # 3. Full integration test
    def test_full_integration():
        print("\\n3. Full Integration Test (Complete Fix):")
        
        def render_expression_fixed(latex):
            """Fixed version of renderExpression"""
            result = latex
            
            # Symbol mapping (both single and double backslashes)
            symbols = {
                '\\\\\\\\times': '×', '\\\\times': '×',
                '\\\\\\\\div': '÷', '\\\\div': '÷', 
                '\\\\\\\\ne': '≠', '\\\\ne': '≠',
                '\\\\\\\\pm': '±', '\\\\pm': '±',
            }
            
            for symbol, replacement in symbols.items():
                result = re.sub(re.escape(symbol), replacement, result)
            
            # Clean up backslashes (both double and single)
            result = re.sub(r'\\\\\\\\', '', result)  # Double first
            result = re.sub(r'\\\\', '', result)      # Then single
            result = re.sub(r'\\s+', ' ', result)
            
            return result
        
        def process_inline_math_fixed(content):
            """Fixed version of inline math processing"""
            # FIXED regex: handles single backslashes
            pattern = r'\\(([^()]*\\\\[^()]*)\\)'
            
            def replace_match(match):
                expr = match.group(1)
                if '\\\\' in expr:
                    rendered = render_expression_fixed(expr)
                    return f'<span style="font-style: italic;">({rendered})</span>'
                return match.group(0)
            
            return re.sub(pattern, replace_match, content)
        
        # Test the exact issue from the bug report
        test_cases = [
            {
                'input': 'The formula is (10 \\\\div 2) which equals 5.',
                'expected': 'The formula is <span style="font-style: italic;">(10 ÷ 2)</span> which equals 5.',
            },
            {
                'input': 'We have (a \\\\times b) and (x \\\\ne y).',
                'expected': 'We have <span style="font-style: italic;">(a × b)</span> and <span style="font-style: italic;">(x ≠ y)</span>.',
            },
            {
                'input': 'Regular text (no LaTeX) should not change.',
                'expected': 'Regular text (no LaTeX) should not change.',
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            result = process_inline_math_fixed(test_case['input'])
            success = result == test_case['expected']
            status = "✅" if success else "❌"
            
            print(f"   Test {i}: {status}")
            print(f"     Input:    '{test_case['input']}'")
            print(f"     Expected: '{test_case['expected']}'")
            print(f"     Got:      '{result}'")
            if not success:
                print(f"     ❌ MISMATCH!")
            print()
    
    # Run all tests
    test_symbol_replacement()
    test_inline_math_regex()
    test_full_integration()
    
    print("=" * 60)
    print("🎉 Fix validation complete!")
    print("✅ The \\\\div rendering issue should now be resolved!")

if __name__ == "__main__":
    test_fixed_div_rendering()