#!/usr/bin/env python3
"""
Demonstration script showing the single character answer normalization feature.
This shows the exact scenarios mentioned in the GitHub issue.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.answer_normalizer import normalize_single_character_answer


def demo_scenario(description, question, user_input, expected_behavior):
    """Demonstrate a specific scenario"""
    print(f"\n📝 {description}")
    print(f"Question: {question}")
    print(f"User input: '{user_input}'")
    
    result = normalize_single_character_answer(user_input, question)
    print(f"Normalized answer: '{result}'")
    print(f"Expected: {expected_behavior}")
    
    return result


def main():
    print("🎯 Multiple Choice Answer Normalization Demo")
    print("=" * 60)
    print("This demonstrates the fix for GitHub issue #110:")
    print("'Allow single character answer for multiple choice'")
    
    # Scenario 1: From the issue description
    scenario1_question = """Which do you think is right?

1. Cow
2. Moon"""
    
    result1 = demo_scenario(
        "Scenario 1 (from issue): Numbered choices with newlines",
        scenario1_question,
        "1",
        "Should normalize '1' to 'Cow'"
    )
    assert result1 == "Cow", f"Expected 'Cow', got '{result1}'"
    print("✅ PASS")
    
    # Scenario 2: From the issue description
    scenario2_question = """After learning this what is the correct answer:

A) Always
B) Only sometimes"""
    
    result2 = demo_scenario(
        "Scenario 2 (from issue): Lettered choices with parentheses",
        scenario2_question,
        "b",
        "Should normalize 'b' to 'Only sometimes'"
    )
    assert result2 == "Only sometimes", f"Expected 'Only sometimes', got '{result2}'"
    print("✅ PASS")
    
    # Scenario 3: Inline format
    scenario3_question = "Choose the best option: 1. Red 2. Blue 3. Green"
    
    result3 = demo_scenario(
        "Scenario 3: Inline numbered choices",
        scenario3_question,
        "2",
        "Should normalize '2' to 'Blue'"
    )
    assert result3 == "Blue", f"Expected 'Blue', got '{result3}'"
    print("✅ PASS")
    
    # Scenario 4: Mixed case letters
    scenario4_question = """Pick one:

A. First option
B. Second option
C. Third option"""
    
    result4 = demo_scenario(
        "Scenario 4: Mixed case letter input",
        scenario4_question,
        "C",
        "Should normalize 'C' to 'Third option'"
    )
    assert result4 == "Third option", f"Expected 'Third option', got '{result4}'"
    print("✅ PASS")
    
    # Scenario 5: Full answer (should not change)
    result5 = demo_scenario(
        "Scenario 5: Full answer (should remain unchanged)",
        scenario1_question,
        "I think the cow is correct",
        "Should remain unchanged"
    )
    assert result5 == "I think the cow is correct", f"Expected unchanged, got '{result5}'"
    print("✅ PASS")
    
    # Scenario 6: Invalid choice (should not change)
    result6 = demo_scenario(
        "Scenario 6: Invalid single character choice",
        scenario1_question,
        "3",
        "Should remain unchanged (invalid choice)"
    )
    assert result6 == "3", f"Expected unchanged '3', got '{result6}'"
    print("✅ PASS")
    
    # Scenario 7: Non-multiple choice question
    scenario7_question = "What is your favorite color and why?"
    
    result7 = demo_scenario(
        "Scenario 7: Non-multiple choice question",
        scenario7_question,
        "b",
        "Should remain unchanged (no multiple choice pattern)"
    )
    assert result7 == "b", f"Expected unchanged 'b', got '{result7}'"
    print("✅ PASS")
    
    print("\n" + "=" * 60)
    print("🎉 All scenarios work correctly!")
    print("\nThe feature successfully normalizes single character answers")
    print("for multiple choice questions while preserving other input types.")
    print("\nThis fixes the issue where students couldn't use shorthand")
    print("answers like '1', '2', 'a', 'b' for multiple choice questions.")


if __name__ == "__main__":
    main()