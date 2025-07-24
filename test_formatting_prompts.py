#!/usr/bin/env python3
"""
Test for formatting improvements in tutoring prompts.

This test verifies that the prompt templates include proper formatting guidelines.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.tutor_prompts import (
    TEACHING_PROMPT_TEMPLATE,
    RECAP_PROMPT_TEMPLATE,
    format_teaching_prompt,
    format_recap_prompt
)


class TestFormattingPrompts(unittest.TestCase):
    """Test that prompt templates encourage proper formatting."""
    
    def test_teaching_prompt_has_formatting_guidelines(self):
        """Test that teaching prompt includes formatting requirements."""
        # Check that formatting requirements are present
        self.assertIn("FORMATTING REQUIREMENTS", TEACHING_PROMPT_TEMPLATE)
        self.assertIn("markdown formatting", TEACHING_PROMPT_TEMPLATE)
        self.assertIn("multiple choice questions", TEACHING_PROMPT_TEMPLATE)
        self.assertIn("**A)**", TEACHING_PROMPT_TEMPLATE)
        
    def test_recap_prompt_has_formatting_guidelines(self):
        """Test that recap prompt includes formatting requirements."""
        self.assertIn("FORMATTING REQUIREMENTS", RECAP_PROMPT_TEMPLATE)
        self.assertIn("markdown formatting", RECAP_PROMPT_TEMPLATE)
        
    def test_increased_word_limit(self):
        """Test that word limits have been increased to allow formatting."""
        self.assertIn("≤ 180 words", TEACHING_PROMPT_TEMPLATE)
        self.assertIn("≤ 180 words", RECAP_PROMPT_TEMPLATE)
        
    def test_format_teaching_prompt_includes_formatting(self):
        """Test that formatted teaching prompt retains formatting guidelines."""
        # Sample data
        obj_id = "test_obj"
        obj_label = "Test Objective"
        recent = ["topic1", "topic2"]
        remaining = ["topic3", "topic4"]
        refs = [
            {"rid": "ref1", "title": "Test Reference", "section": "1.1", "type": "article", "date": "2023-01-01"}
        ]
        
        formatted = format_teaching_prompt(obj_id, obj_label, recent, remaining, refs)
        
        # Verify formatting guidelines are present in the formatted prompt
        self.assertIn("FORMATTING REQUIREMENTS", formatted)
        self.assertIn("markdown formatting", formatted)
        self.assertIn("multiple choice questions", formatted)
        
    def test_format_recap_prompt_includes_formatting(self):
        """Test that formatted recap prompt retains formatting guidelines."""
        recent_los = ["objective1", "objective2"]
        next_obj = "Next Objective"
        refs = [
            {"rid": "ref1", "title": "Test Reference", "section": "1.1", "type": "article", "date": "2023-01-01"}
        ]
        
        formatted = format_recap_prompt(recent_los, next_obj, refs)
        
        # Verify formatting guidelines are present in the formatted prompt
        self.assertIn("FORMATTING REQUIREMENTS", formatted)
        self.assertIn("markdown formatting", formatted)


if __name__ == '__main__':
    unittest.main()