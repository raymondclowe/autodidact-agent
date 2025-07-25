#!/usr/bin/env python3
"""
Test script for JSON extraction functionality.
Tests the extract_json_from_markdown function with various scenarios.
"""

import json
import unittest
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.deep_research import extract_json_from_markdown


class TestJSONExtraction(unittest.TestCase):
    """Test cases for JSON extraction functionality."""

    def test_intro_text_before_json(self):
        """Test extracting JSON when there's intro text before it."""
        content = """I'll provide a comprehensive response:

{
    "resources": [
        {
            "rid": "test",
            "title": "Test Resource",
            "type": "book",
            "url": "https://example.com"
        }
    ],
    "nodes": []
}"""
        result = extract_json_from_markdown(content)
        
        # Should extract valid JSON
        self.assertTrue(result.strip().startswith('{'))
        self.assertTrue(result.strip().endswith('}'))
        
        # Should be parseable as JSON
        parsed = json.loads(result)
        self.assertIn('resources', parsed)
        self.assertIn('nodes', parsed)

    def test_markdown_json_block(self):
        """Test extracting JSON from markdown code blocks."""
        content = """Here's the response:

```json
{
    "resources": [],
    "nodes": []
}
```"""
        result = extract_json_from_markdown(content)
        
        # Should extract valid JSON
        self.assertTrue(result.strip().startswith('{'))
        self.assertTrue(result.strip().endswith('}'))
        
        # Should be parseable as JSON
        parsed = json.loads(result)
        self.assertIn('resources', parsed)
        self.assertIn('nodes', parsed)

    def test_json_with_outro_text(self):
        """Test extracting JSON when there's outro text after it."""
        content = """Here's the JSON:

{
    "resources": [],
    "nodes": []
}

Some additional text after the JSON."""
        result = extract_json_from_markdown(content)
        
        # Should extract only the JSON part
        self.assertTrue(result.strip().startswith('{'))
        self.assertTrue(result.strip().endswith('}'))
        
        # Should be parseable as JSON
        parsed = json.loads(result)
        self.assertIn('resources', parsed)
        self.assertIn('nodes', parsed)

    def test_no_json_content(self):
        """Test handling content with no JSON."""
        content = "This is just some text without any JSON content."
        result = extract_json_from_markdown(content)
        
        # Should return original content
        self.assertEqual(result, content)

    def test_invalid_json_structure(self):
        """Test handling invalid JSON structure."""
        content = """Here's invalid JSON:

{
    "resources": [
        "missing closing brace"
    ],
    "nodes": []"""
        result = extract_json_from_markdown(content)
        
        # Should return original content since JSON is invalid
        self.assertEqual(result, content)


if __name__ == "__main__":
    unittest.main()