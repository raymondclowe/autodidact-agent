#!/usr/bin/env python3
"""
Integration test for multiple choice answer normalization in testing_node
"""

import sys
import os
import unittest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.graph_v05 import testing_node
from backend.session_state import SessionState


class TestAnswerNormalizationIntegration(unittest.TestCase):
    
    def create_test_state(self, questions=None, answers=None, history=None):
        """Helper to create a test state"""
        state = SessionState()
        state["final_test_questions"] = questions or []
        state["final_test_answers"] = answers or []
        state["history"] = history or []
        state["current_phase"] = "testing"
        return state
    
    def test_numbered_multiple_choice_normalization(self):
        """Test that single digit answers are normalized for numbered multiple choice"""
        questions = [
            """Which do you think is right?

1. Cow
2. Moon
3. Star"""
        ]
        
        # Simulate user answering "1"
        history = [
            {"role": "assistant", "content": "Question 1/1:\n\nWhich do you think is right?\n\n1. Cow\n2. Moon\n3. Star"},
            {"role": "user", "content": "1"}
        ]
        
        state = self.create_test_state(questions=questions, answers=[], history=history)
        
        # Run testing_node
        result_state = testing_node(state)
        
        # Check that the answer was normalized
        self.assertEqual(result_state["final_test_answers"], ["Cow"])
    
    def test_lettered_multiple_choice_normalization(self):
        """Test that single letter answers are normalized for lettered multiple choice"""
        questions = [
            """After learning this what is the correct answer:

A) Always
B) Only sometimes
C) Never"""
        ]
        
        # Simulate user answering "b" (lowercase)
        history = [
            {"role": "assistant", "content": "Question 1/1:\n\nAfter learning this what is the correct answer:\n\nA) Always\nB) Only sometimes\nC) Never"},
            {"role": "user", "content": "b"}
        ]
        
        state = self.create_test_state(questions=questions, answers=[], history=history)
        
        # Run testing_node
        result_state = testing_node(state)
        
        # Check that the answer was normalized
        self.assertEqual(result_state["final_test_answers"], ["Only sometimes"])
    
    def test_full_answer_unchanged(self):
        """Test that full answers are not changed"""
        questions = [
            """Which do you think is right?

1. Cow
2. Moon"""
        ]
        
        # Simulate user providing full answer
        history = [
            {"role": "assistant", "content": "Question 1/1:\n\nWhich do you think is right?\n\n1. Cow\n2. Moon"},
            {"role": "user", "content": "I think the cow is the right answer"}
        ]
        
        state = self.create_test_state(questions=questions, answers=[], history=history)
        
        # Run testing_node
        result_state = testing_node(state)
        
        # Check that the answer was not changed
        self.assertEqual(result_state["final_test_answers"], ["I think the cow is the right answer"])
    
    def test_non_multiple_choice_unchanged(self):
        """Test that answers to non-multiple choice questions are unchanged"""
        questions = [
            "What is your favorite color and why?"
        ]
        
        # Simulate user answering with single character (should not be normalized)
        history = [
            {"role": "assistant", "content": "Question 1/1:\n\nWhat is your favorite color and why?"},
            {"role": "user", "content": "b"}
        ]
        
        state = self.create_test_state(questions=questions, answers=[], history=history)
        
        # Run testing_node
        result_state = testing_node(state)
        
        # Check that the answer was not changed (no multiple choice pattern)
        self.assertEqual(result_state["final_test_answers"], ["b"])
    
    def test_invalid_choice_unchanged(self):
        """Test that invalid single character choices are unchanged"""
        questions = [
            """Which do you think is right?

1. Cow
2. Moon"""
        ]
        
        # Simulate user answering "3" (invalid choice)
        history = [
            {"role": "assistant", "content": "Question 1/1:\n\nWhich do you think is right?\n\n1. Cow\n2. Moon"},
            {"role": "user", "content": "3"}
        ]
        
        state = self.create_test_state(questions=questions, answers=[], history=history)
        
        # Run testing_node
        result_state = testing_node(state)
        
        # Check that the invalid answer was not changed
        self.assertEqual(result_state["final_test_answers"], ["3"])
    
    def test_multiple_questions_normalization(self):
        """Test normalization works correctly across multiple questions"""
        questions = [
            """Question 1:

1. First option
2. Second option""",
            """Question 2:

A) Choice A
B) Choice B"""
        ]
        
        # First question answered with "1"
        state = self.create_test_state(questions=questions, answers=[], history=[
            {"role": "assistant", "content": "Question 1/2..."},
            {"role": "user", "content": "1"}
        ])
        
        result_state = testing_node(state)
        self.assertEqual(result_state["final_test_answers"], ["First option"])
        
        # Second question answered with "B"
        state_after_first = result_state.copy()
        state_after_first["history"].extend([
            {"role": "assistant", "content": "Question 2/2..."},
            {"role": "user", "content": "B"}
        ])
        
        final_state = testing_node(state_after_first)
        self.assertEqual(final_state["final_test_answers"], ["First option", "Choice B"])


def main():
    """Run all integration tests"""
    print("Testing answer normalization integration...")
    print("=" * 50)
    
    # Initialize unittest and run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("✅ All integration tests completed!")


if __name__ == "__main__":
    main()