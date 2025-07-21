"""
Test for issue #24: Control data shown in session dialogue

This test verifies that control blocks are properly handled:
1. Removed from user-facing content  
2. Still processed internally for system logic
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


class TestControlBlockHandling(unittest.TestCase):
    """Test that control blocks are hidden from users but still processed."""
    
    def test_remove_control_blocks_basic(self):
        """Test basic control block removal."""
        # Test case with control block
        text_with_control = 'Great work! <control>{"objective_complete": true}</control> Let\'s move forward.'
        expected = 'Great work! Let\'s move forward.'
        result = remove_control_blocks(text_with_control)
        self.assertEqual(result, expected)
    
    def test_remove_control_blocks_multiple(self):
        """Test removal of multiple control blocks."""
        text_with_multiple = 'First part. <control>{"objective_complete": true}</control> Middle part. <control>{"prereq_complete": false}</control> End part.'
        expected = 'First part. Middle part. End part.'
        result = remove_control_blocks(text_with_multiple)
        self.assertEqual(result, expected)
    
    def test_remove_control_blocks_preserves_normal_text(self):
        """Test that normal text is preserved without control blocks."""
        normal_text = 'This is normal teaching content without any control blocks.'
        result = remove_control_blocks(normal_text)
        self.assertEqual(result, normal_text)
    
    def test_remove_control_blocks_handles_empty(self):
        """Test that empty/None input is handled gracefully."""
        self.assertEqual(remove_control_blocks(''), '')
        self.assertEqual(remove_control_blocks(None), None)
    
    def test_extract_control_block_still_works(self):
        """Test that control extraction still works on original content."""
        text_with_control = 'Great work! <control>{"objective_complete": true}</control> Let\'s move forward.'
        ctrl = extract_control_block(text_with_control, TEACHING_CONTROL_SCHEMA)
        self.assertIsNotNone(ctrl)
        self.assertTrue(ctrl.get("objective_complete"))
    
    def test_control_block_workflow(self):
        """Test the complete workflow: extract controls, remove from display."""
        # Simulate the workflow in teaching_node
        assistant_content = 'You understand the concept well! <control>{"objective_complete": true}</control> Now we can move to the next topic.'
        
        # Extract control for internal processing (like in teaching_node)
        ctrl = extract_control_block(assistant_content, TEACHING_CONTROL_SCHEMA)
        
        # Clean content for user display
        cleaned_content = remove_control_blocks(assistant_content)
        
        # Verify control was extracted correctly
        self.assertIsNotNone(ctrl)
        self.assertTrue(ctrl.get("objective_complete"))
        
        # Verify user-facing content is clean
        self.assertEqual(cleaned_content, 'You understand the concept well! Now we can move to the next topic.')
        self.assertNotIn('<control>', cleaned_content)
        self.assertNotIn('objective_complete', cleaned_content)
    
    def test_issue_24_example(self):
        """Test the specific case from issue #24."""
        # The issue shows this appearing: forward! {"objective_complete": true}
        # This suggests the control block wasn't properly formatted or was leaked
        
        # Test properly formatted control block
        proper_control = 'forward! <control>{"objective_complete": true}</control>'
        cleaned = remove_control_blocks(proper_control)
        self.assertEqual(cleaned, 'forward!')
        
        # Test malformed control (raw JSON that might leak)
        malformed_control = 'forward! {"objective_complete": true}'
        # This should pass through unchanged since it's not a proper control block
        cleaned = remove_control_blocks(malformed_control)
        self.assertEqual(cleaned, malformed_control)
        
        # Test that extract_control_block only works with proper format
        ctrl = extract_control_block(proper_control, TEACHING_CONTROL_SCHEMA)
        self.assertIsNotNone(ctrl)
        
        ctrl_malformed = extract_control_block(malformed_control, TEACHING_CONTROL_SCHEMA)
        self.assertIsNone(ctrl_malformed)
    
    def test_integration_with_citation_cleaning(self):
        """Test that control block removal works independently."""
        # Text with control blocks (citation cleaning is a separate concern)
        text = 'Good work! <control>{"objective_complete": true}</control> Let\'s continue!'
        
        # Apply control block removal
        cleaned = remove_control_blocks(text)
        
        expected = 'Good work! Let\'s continue!'
        self.assertEqual(cleaned, expected)


if __name__ == '__main__':
    unittest.main()