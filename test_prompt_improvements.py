#!/usr/bin/env python3
"""
Test enhanced prompts based on ChatGPT study mode principles.
Tests that the new teaching principles and improvements are included.
"""

import unittest
from backend.tutor_prompts import (
    TEACHING_PROMPT_TEMPLATE,
    RECAP_PROMPT_TEMPLATE,
    format_teaching_prompt,
    format_recap_prompt
)


class TestPromptImprovements(unittest.TestCase):
    """Test that prompt improvements from ChatGPT study mode are included."""
    
    def test_teaching_prompt_has_core_principles(self):
        """Test that the teaching prompt includes the 5 core principles."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check for core teaching principles section
        self.assertIn("## CORE TEACHING PRINCIPLES", prompt)
        
        # Check for each of the 5 principles
        self.assertIn("GET TO KNOW THE LEARNER", prompt)
        self.assertIn("BUILD ON EXISTING KNOWLEDGE", prompt)
        self.assertIn("GUIDE, DON'T GIVE ANSWERS", prompt)
        self.assertIn("CHECK AND REINFORCE UNDERSTANDING", prompt)
        self.assertIn("VARY THE RHYTHM", prompt)
        
    def test_teaching_prompt_prohibits_doing_work(self):
        """Test that the prompt explicitly prohibits doing work for students."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check for explicit prohibition
        self.assertIn("DO NOT DO THE LEARNER'S WORK FOR THEM", prompt)
        self.assertIn("Use questions, hints, and small steps so they discover answers themselves", prompt)
        self.assertIn("If they ask direct questions, respond with guiding questions instead", prompt)
        
    def test_teaching_prompt_has_interaction_patterns(self):
        """Test that the prompt includes specific interaction patterns."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check for specific interaction guidelines
        self.assertIn("Never ask more than one question at a time", prompt)
        self.assertIn("let them try twice before providing guidance", prompt)
        self.assertIn("explain concepts back to you", prompt)
        
    def test_teaching_prompt_has_tone_guidance(self):
        """Test that the prompt includes specific tone and style guidance."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check for tone guidance
        self.assertIn("TONE & INTERACTION STYLE", prompt)
        self.assertIn("Be warm, patient, and plain-spoken", prompt)
        self.assertIn("Don't use too many exclamation marks or emoji", prompt)
        self.assertIn("aim for good back-and-forth", prompt)
        
    def test_teaching_prompt_has_reinforcement_techniques(self):
        """Test that the prompt includes reinforcement and checking techniques."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check for reinforcement techniques
        self.assertIn("mnemonics, or mini-reviews", prompt)
        self.assertIn("confirm they can restate or use the idea", prompt)
        self.assertIn("role-playing scenarios, practice rounds", prompt)
        self.assertIn("asking them to teach YOU", prompt)
        
    def test_teaching_prompt_updated_version(self):
        """Test that the prompt is updated to v2."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check version update
        self.assertIn("Autodidact Tutor v2", prompt)
        self.assertIn("warm, patient, and dynamic AI instructor", prompt)
        
    def test_recap_prompt_has_improvements(self):
        """Test that the recap prompt includes improvements."""
        prompt = RECAP_PROMPT_TEMPLATE
        
        # Check version and tone update
        self.assertIn("Autodidact Tutor v2 - Recap Mode", prompt)
        self.assertIn("warm, patient instructor focused on reinforcing learning", prompt)
        
        # Check for recap principles
        self.assertIn("## CORE RECAP PRINCIPLES", prompt)
        self.assertIn("Build connections", prompt)
        self.assertIn("Use their own words", prompt)
        self.assertIn("One question at a time", prompt)
        
    def test_safety_style_improvements(self):
        """Test that safety and style section is enhanced."""
        prompt = TEACHING_PROMPT_TEMPLATE
        
        # Check for improved safety guidance
        self.assertIn("Encourage growth mindset", prompt)
        self.assertIn("never shame mistakes", prompt)
        self.assertIn("help them work through the process", prompt)
        self.assertIn("don't solve it for them", prompt)
        
    def test_formatted_teaching_prompt_works(self):
        """Test that the formatted prompt still works with parameters."""
        # Sample data for formatting
        obj_id = "test_obj_1"
        obj_label = "Understanding Test Concepts"
        recent = ["prerequisite_topic"]
        remaining = ["future_topic_1", "future_topic_2"]
        refs = [
            {
                'rid': 'test_ref',
                'title': 'Test Reference',
                'section': 'Chapter 1',
                'type': 'article',
                'date': '2024-01-01'
            }
        ]
        learner_profile = "Student prefers visual learning"
        
        # Format the prompt
        formatted = format_teaching_prompt(
            obj_id, obj_label, recent, remaining, refs, learner_profile
        )
        
        # Check that formatting worked
        self.assertIn(obj_id, formatted)
        self.assertIn(obj_label, formatted)
        self.assertIn("prerequisite_topic", formatted)
        self.assertIn("Test Reference", formatted)
        self.assertIn(learner_profile, formatted)
        
        # Check that core principles are still there
        self.assertIn("CORE TEACHING PRINCIPLES", formatted)
        
    def test_formatted_recap_prompt_works(self):
        """Test that the formatted recap prompt still works with parameters."""
        # Sample data for formatting
        recent_los = ["completed_objective_1", "completed_objective_2"]
        next_obj = "upcoming_objective"
        refs = [
            {
                'rid': 'recap_ref',
                'title': 'Recap Reference',
                'section': 'Summary',
                'type': 'book',
                'date': '2024-01-01'
            }
        ]
        learner_profile = "Student needs frequent reinforcement"
        
        # Format the prompt
        formatted = format_recap_prompt(
            recent_los, next_obj, refs, learner_profile
        )
        
        # Check that formatting worked
        self.assertIn("completed_objective_1", formatted)
        self.assertIn("upcoming_objective", formatted)
        self.assertIn("Recap Reference", formatted)
        self.assertIn(learner_profile, formatted)
        
        # Check that core principles are still there
        self.assertIn("CORE RECAP PRINCIPLES", formatted)


if __name__ == '__main__':
    unittest.main()