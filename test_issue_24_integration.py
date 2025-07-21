"""
Integration test simulating the actual session flow from issue #24.

This test simulates what happens in the teaching_node when an objective is completed
to ensure control blocks are properly handled in the actual application flow.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.tutor_prompts import (
    extract_control_block, 
    remove_control_blocks,
    clean_improper_citations,
    TEACHING_CONTROL_SCHEMA
)


class TestIssue24IntegrationFix(unittest.TestCase):
    """Integration test simulating the teaching_node flow."""
    
    def simulate_teaching_node_content_processing(self, assistant_content, refs=None):
        """Simulate the content processing pipeline from teaching_node."""
        if refs is None:
            refs = []
        
        # This is the exact flow from teaching_node in graph_v05.py:
        
        # 1. Clean up improper citations in the response  
        cleaned_content = clean_improper_citations(assistant_content, refs)
        
        # 2. Remove control blocks from user-facing content (our fix)
        cleaned_content = remove_control_blocks(cleaned_content)
        
        # 3. Create assistant message for display
        assistant_message = {"role": "assistant", "content": cleaned_content}
        
        # 4. Extract control block for internal processing (uses original content)
        ctrl = extract_control_block(assistant_content, TEACHING_CONTROL_SCHEMA)
        
        return assistant_message, ctrl
    
    def test_issue_24_scenario(self):
        """Test the exact scenario from issue #24."""
        # Simulate AI response that would cause the original issue
        ai_response = 'forward! <control>{"objective_complete": true}</control>'
        
        # Process through the pipeline
        assistant_msg, control = self.simulate_teaching_node_content_processing(ai_response)
        
        # Verify user sees clean content
        self.assertEqual(assistant_msg["content"], "forward!")
        self.assertNotIn("objective_complete", assistant_msg["content"])
        self.assertNotIn("<control>", assistant_msg["content"])
        
        # Verify system still detects completion
        self.assertIsNotNone(control)
        self.assertTrue(control.get("objective_complete"))
    
    def test_objective_advancement_message(self):
        """Test a more realistic objective completion scenario."""
        ai_response = '''Great work! You've understood the concept well. 
<control>{"objective_complete": true}</control>

Let me know if you have any questions before we move forward.'''
        
        assistant_msg, control = self.simulate_teaching_node_content_processing(ai_response)
        
        # User should see clean, natural content (whitespace normalized by remove_control_blocks)
        expected_clean = '''Great work! You've understood the concept well. Let me know if you have any questions before we move forward.'''
        
        self.assertEqual(assistant_msg["content"], expected_clean)
        
        # System should detect completion
        self.assertIsNotNone(control)
        self.assertTrue(control.get("objective_complete"))
    
    def test_no_control_block_passthrough(self):
        """Test that normal messages without control blocks work normally."""
        ai_response = "This is a normal teaching message without any control blocks."
        
        assistant_msg, control = self.simulate_teaching_node_content_processing(ai_response)
        
        # Content should pass through unchanged
        self.assertEqual(assistant_msg["content"], ai_response)
        
        # No control should be detected
        self.assertIsNone(control)
    
    def test_multiple_control_blocks(self):
        """Test handling of multiple control blocks (edge case)."""
        ai_response = '''First concept done. <control>{"objective_complete": true}</control>
Now for the next part. <control>{"objective_complete": false}</control>
Continue studying.'''
        
        assistant_msg, control = self.simulate_teaching_node_content_processing(ai_response)
        
        # All control blocks should be removed and whitespace normalized
        expected_clean = '''First concept done. Now for the next part. Continue studying.'''
        
        self.assertEqual(assistant_msg["content"], expected_clean)
        
        # Should extract the first control block found
        self.assertIsNotNone(control)
        self.assertTrue(control.get("objective_complete"))
    
    def test_with_citations_and_control(self):
        """Test the complete pipeline with both citation and control cleaning."""
        ai_response = '''Check this [research_ref] for more details. 
<control>{"objective_complete": true}</control>
Great understanding!'''
        
        # Provide a reference so citation cleaning works properly
        refs = [
            {"rid": "research_ref", "title": "Research Paper", "section": "3.1"}
        ]
        
        assistant_msg, control = self.simulate_teaching_node_content_processing(ai_response, refs)
        
        # Citation should be properly formatted, control block removed, whitespace normalized
        expected_clean = '''Check this [research_ref §3.1] for more details. Great understanding!'''
        
        self.assertEqual(assistant_msg["content"], expected_clean)
        
        # Control should still be extracted
        self.assertIsNotNone(control)
        self.assertTrue(control.get("objective_complete"))


if __name__ == '__main__':
    unittest.main()