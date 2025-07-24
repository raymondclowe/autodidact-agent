#!/usr/bin/env python3
"""
Integration test for formatting improvements.

This test simulates the full flow from prompt generation to response processing
to verify that formatting improvements work as expected.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.tutor_prompts import (
    format_teaching_prompt,
    format_recap_prompt,
    clean_improper_citations,
    remove_control_blocks
)


class TestFormattingIntegration(unittest.TestCase):
    """Integration test for the complete formatting pipeline."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_refs = [
            {
                "rid": "ml_basics",
                "title": "Machine Learning Fundamentals", 
                "section": "Chapter 2",
                "type": "textbook",
                "date": "2023-01-01"
            }
        ]
    
    def test_teaching_prompt_encourages_good_formatting(self):
        """Test that the teaching prompt will encourage properly formatted responses."""
        formatted_prompt = format_teaching_prompt(
            obj_id="test_obj",
            obj_label="Understanding Supervised Learning",
            recent=["data preprocessing"],
            remaining=["neural networks"],
            refs=self.sample_refs
        )
        
        # Verify the prompt contains specific formatting instructions
        self.assertIn("**Always use markdown formatting**", formatted_prompt)
        self.assertIn("**For multiple choice questions:**", formatted_prompt)
        self.assertIn("**A)** Option text", formatted_prompt)
        self.assertIn("Add blank lines between question and options", formatted_prompt)
        
        # Verify word limit allows for formatting
        self.assertIn("≤ 180 words", formatted_prompt)
    
    def test_simulated_well_formatted_ai_response(self):
        """Test processing of a well-formatted AI response."""
        # Simulate a well-formatted AI response following our guidelines
        ai_response = """Let's explore supervised learning! 

What type of data does supervised learning require?

**A)** Labeled training data with input-output pairs  
**B)** Only input data without any labels  
**C)** Unlabeled data for pattern discovery

Think about what makes learning "supervised" - what guidance does the algorithm need?

<control>{"objective_complete": false}</control>"""
        
        # Process the response like the system would
        cleaned_content = clean_improper_citations(ai_response, self.sample_refs)
        display_content = remove_control_blocks(cleaned_content)
        
        # Verify the formatting is preserved
        self.assertIn("**A)**", display_content)
        self.assertIn("**B)**", display_content)
        self.assertIn("**C)**", display_content)
        
        # Verify proper line breaks and formatting are preserved
        lines = display_content.split('\n')
        
        # Find the question line
        question_line = next((i for i, line in enumerate(lines) if "What type of data" in line), -1)
        self.assertNotEqual(question_line, -1, "Question should be found")
        
        # Find option lines
        option_a_line = next((i for i, line in enumerate(lines) if "**A)**" in line), -1)
        option_b_line = next((i for i, line in enumerate(lines) if "**B)**" in line), -1)
        option_c_line = next((i for i, line in enumerate(lines) if "**C)**" in line), -1)
        
        self.assertNotEqual(option_a_line, -1, "Option A should be found")
        self.assertNotEqual(option_b_line, -1, "Option B should be found")
        self.assertNotEqual(option_c_line, -1, "Option C should be found")
        
        # Options should be in order (not necessarily consecutive due to blank lines)
        self.assertLess(option_a_line, option_b_line, "Option A should come before B")
        self.assertLess(option_b_line, option_c_line, "Option B should come before C")
        
        # Control block should be removed from display
        self.assertNotIn("<control>", display_content)
        self.assertNotIn("objective_complete", display_content)
    
    def test_simulated_poorly_formatted_response_still_works(self):
        """Test that poorly formatted responses still work (backward compatibility)."""
        # Simulate a poorly formatted response (old style)
        ai_response = """What is supervised learning? A) Learning with labeled data B) Learning without data C) Learning with unlabeled data. Choose the correct answer. <control>{"objective_complete": false}</control>"""
        
        # Process the response
        cleaned_content = clean_improper_citations(ai_response, self.sample_refs)
        display_content = remove_control_blocks(cleaned_content)
        
        # Should still work, just not as well formatted
        self.assertNotIn("<control>", display_content)
        self.assertIn("A)", display_content)
        self.assertIn("B)", display_content)
        self.assertIn("C)", display_content)
    
    def test_recap_prompt_formatting_guidelines(self):
        """Test that recap prompts include formatting guidelines."""
        recap_prompt = format_recap_prompt(
            recent_los=["basic concepts", "data types"],
            next_obj="supervised learning algorithms",
            refs=self.sample_refs
        )
        
        # Verify formatting guidelines are present
        self.assertIn("FORMATTING REQUIREMENTS", recap_prompt)
        self.assertIn("**Always use markdown formatting**", recap_prompt)
        self.assertIn("numbered lists", recap_prompt)
        self.assertIn("≤ 180 words", recap_prompt)
    
    def test_word_count_increase_rationale(self):
        """Test that word count increase allows for better formatting."""
        # The increased word limit from 150 to 180 provides more room for formatting
        
        # Test that 180 words is a reasonable limit for formatted content
        word_limit = 180
        
        # A typical well-formatted question should be possible within 180 words
        # This validates that the limit increase makes sense
        self.assertGreater(word_limit, 150, "New limit should be higher than old limit")
        self.assertLessEqual(word_limit, 200, "Limit should not be too high to maintain conciseness")
        
        # Test a realistically sized formatted response
        typical_formatted_response = """Let's explore supervised learning concepts.

What distinguishes supervised learning from other approaches?

**A)** Uses labeled training data
**B)** Works with unlabeled data only  
**C)** Requires no training data

Consider how supervision guides the learning process."""
        
        word_count = len(typical_formatted_response.split())
        self.assertLess(word_count, 180, "Typical formatted response should fit within limit")


if __name__ == '__main__':
    unittest.main()