#!/usr/bin/env python3
"""
Test script for answer normalization functionality
"""

import sys
import os
import unittest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.answer_normalizer import (
    detect_multiple_choice_pattern, 
    extract_multiple_choice_options,
    normalize_single_character_answer
)


class TestAnswerNormalizer(unittest.TestCase):
    
    def test_detect_numbered_pattern(self):
        """Test detection of numbered multiple choice patterns"""
        question1 = """Which do you think is right?

1. Cow
2. Moon"""
        
        self.assertEqual(detect_multiple_choice_pattern(question1), 'numbered')
        
        question2 = """What is the correct answer?

1. Always
2. Sometimes
3. Never"""
        
        self.assertEqual(detect_multiple_choice_pattern(question2), 'numbered')
    
    def test_detect_lettered_pattern(self):
        """Test detection of lettered multiple choice patterns"""
        question1 = """After learning this what is the correct answer:

A) Always
B) Only sometimes"""
        
        self.assertEqual(detect_multiple_choice_pattern(question1), 'lettered')
        
        question2 = """Choose the best option:

A. First choice
B. Second choice
C. Third choice"""
        
        self.assertEqual(detect_multiple_choice_pattern(question2), 'lettered')
    
    def test_no_pattern_detected(self):
        """Test questions without multiple choice patterns"""
        question1 = "What is your favorite color?"
        self.assertIsNone(detect_multiple_choice_pattern(question1))
        
        question2 = "Explain the concept of gravity."
        self.assertIsNone(detect_multiple_choice_pattern(question2))
    
    def test_extract_numbered_options(self):
        """Test extraction of numbered options"""
        question = """Which do you think is right?

1. Cow
2. Moon
3. Star"""
        
        options = extract_multiple_choice_options(question)
        expected = [('1', 'Cow'), ('2', 'Moon'), ('3', 'Star')]
        self.assertEqual(options, expected)
    
    def test_extract_lettered_options(self):
        """Test extraction of lettered options"""
        question1 = """After learning this what is the correct answer:

A) Always
B) Only sometimes
C) Never"""
        
        options = extract_multiple_choice_options(question1)
        expected = [('A', 'Always'), ('B', 'Only sometimes'), ('C', 'Never')]
        self.assertEqual(options, expected)
        
        question2 = """Choose the best option:

A. First choice
B. Second choice"""
        
        options = extract_multiple_choice_options(question2)
        expected = [('A', 'First choice'), ('B', 'Second choice')]
        self.assertEqual(options, expected)
    
    def test_normalize_numbered_answer(self):
        """Test normalization of numbered single character answers"""
        question = """Which do you think is right?

1. Cow
2. Moon"""
        
        # Test valid single character answers
        self.assertEqual(normalize_single_character_answer("1", question), "Cow")
        self.assertEqual(normalize_single_character_answer("2", question), "Moon")
        
        # Test invalid single character answers
        self.assertEqual(normalize_single_character_answer("3", question), "3")
        
        # Test multi-character answers (should be unchanged)
        self.assertEqual(normalize_single_character_answer("Cow", question), "Cow")
        self.assertEqual(normalize_single_character_answer("Something else", question), "Something else")
    
    def test_normalize_lettered_answer(self):
        """Test normalization of lettered single character answers"""
        question = """After learning this what is the correct answer:

A) Always
B) Only sometimes"""
        
        # Test valid single character answers (both cases)
        self.assertEqual(normalize_single_character_answer("A", question), "Always")
        self.assertEqual(normalize_single_character_answer("a", question), "Always")
        self.assertEqual(normalize_single_character_answer("B", question), "Only sometimes")
        self.assertEqual(normalize_single_character_answer("b", question), "Only sometimes")
        
        # Test invalid single character answers
        self.assertEqual(normalize_single_character_answer("C", question), "C")
        self.assertEqual(normalize_single_character_answer("c", question), "c")
        
        # Test multi-character answers (should be unchanged)
        self.assertEqual(normalize_single_character_answer("Always", question), "Always")
    
    def test_normalize_no_options(self):
        """Test normalization when question has no multiple choice options"""
        question = "What is your favorite color?"
        
        # All answers should be unchanged
        self.assertEqual(normalize_single_character_answer("1", question), "1")
        self.assertEqual(normalize_single_character_answer("A", question), "A")
        self.assertEqual(normalize_single_character_answer("Blue", question), "Blue")
    
    def test_edge_cases(self):
        """Test edge cases for answer normalization"""
        question = """Choose:

1. Option one
2. Option two"""
        
        # Test whitespace handling
        self.assertEqual(normalize_single_character_answer(" 1 ", question), "Option one")
        self.assertEqual(normalize_single_character_answer("1\n", question), "Option one")
        
        # Test empty answer
        self.assertEqual(normalize_single_character_answer("", question), "")


def main():
    """Run all answer normalization tests"""
    print("Testing answer normalization functionality...")
    print("=" * 50)
    
    # Initialize unittest and run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("✅ All answer normalization tests completed!")


if __name__ == "__main__":
    main()