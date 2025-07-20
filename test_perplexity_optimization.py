#!/usr/bin/env python3
"""
Test script to verify the Perplexity optimization improvements.
Tests citation extraction, resource enhancement, and response processing.
"""

import sys
import os
import json
import unittest
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestPerplexityOptimization(unittest.TestCase):
    
    def create_mock_annotation(self, citation_num, url, title):
        """Create a mock annotation object like Perplexity returns"""
        url_citation = Mock()
        url_citation.url = url
        url_citation.title = title
        url_citation.start_index = citation_num * 50
        url_citation.end_index = citation_num * 50 + 10
        
        annotation = Mock()
        annotation.type = 'url_citation'
        annotation.url_citation = url_citation
        
        return annotation
    
    def create_mock_perplexity_response(self, content, citations_data):
        """Create a mock Perplexity response with annotations"""
        # Create annotations
        annotations = []
        for i, (url, title) in enumerate(citations_data, 1):
            annotations.append(self.create_mock_annotation(i, url, title))
        
        # Create message with annotations
        message = Mock()
        message.content = content
        message.annotations = annotations
        
        # Create choice
        choice = Mock()
        choice.message = message
        
        # Create response
        response = Mock()
        response.choices = [choice]
        response.usage = Mock()
        response.usage.total_tokens = 1000
        response.usage.completion_tokens = 800
        response.usage.prompt_tokens = 200
        
        return response
    
    def test_extract_citations_from_annotations(self):
        """Test citation extraction from Perplexity response annotations"""
        from backend.jobs import extract_citations_from_annotations
        
        citations_data = [
            ("https://example.com/resource1", "Introduction to Machine Learning"),
            ("https://example.com/resource2", "Deep Learning Fundamentals"),
            ("https://example.com/resource3", "Neural Networks Guide")
        ]
        
        response = self.create_mock_perplexity_response("Test content", citations_data)
        citations = extract_citations_from_annotations(response)
        
        self.assertEqual(len(citations), 3)
        self.assertEqual(citations[1]['url'], "https://example.com/resource1")
        self.assertEqual(citations[1]['title'], "Introduction to Machine Learning")
        self.assertEqual(citations[2]['url'], "https://example.com/resource2")
        self.assertEqual(citations[3]['url'], "https://example.com/resource3")
        
        print("✅ Citation extraction working correctly")
    
    def test_enhance_resources_with_citations(self):
        """Test enhancing resources with citation URLs"""
        from backend.jobs import enhance_resources_with_citations
        
        resources = [
            {
                "rid": "ml_intro",
                "title": "Introduction to Machine Learning",
                "type": "article",
                "url": "#",
                "scope": "Basic concepts and algorithms"
            },
            {
                "rid": "deep_learning",
                "title": "Deep Learning Guide",
                "type": "book",
                "url": "#",
                "scope": "Neural networks and deep learning"
            }
        ]
        
        citations = {
            1: {
                'url': 'https://example.com/ml-intro',
                'title': 'Introduction to Machine Learning',
                'start_index': 0,
                'end_index': 10
            },
            2: {
                'url': 'https://example.com/deep-learning',
                'title': 'Deep Learning Fundamentals',
                'start_index': 50,
                'end_index': 60
            }
        }
        
        enhanced = enhance_resources_with_citations(resources, citations, "Test content")
        
        # Check that the first resource got the matching URL
        self.assertEqual(enhanced[0]['url'], 'https://example.com/ml-intro')
        self.assertEqual(enhanced[0]['citation_source'], 'Citation [1]')
        
        # Check that second resource didn't get matched (title doesn't match exactly)
        self.assertEqual(enhanced[1]['url'], '#')  # Should remain unchanged
        
        print("✅ Resource enhancement working correctly")
    
    def test_process_perplexity_response_with_json(self):
        """Test processing a Perplexity response with embedded JSON"""
        from backend.jobs import process_perplexity_response
        
        content_with_json = """### Comprehensive Learning Curriculum

This curriculum provides a structured approach to learning[1][2].

Key findings include modern methodologies[3] and best practices.

```json
{
  "resources": [
    {
      "rid": "test_resource",
      "title": "Test Resource",
      "type": "article",
      "url": "#",
      "scope": "Testing purposes"
    }
  ],
  "nodes": [
    {
      "id": "test_node",
      "title": "Test Node",
      "learning_objectives": ["Understand testing"]
    }
  ]
}
```"""
        
        citations_data = [
            ("https://example.com/resource1", "Test Resource Guide"),
            ("https://example.com/resource2", "Learning Methodologies"),
            ("https://example.com/resource3", "Best Practices Guide")
        ]
        
        response = self.create_mock_perplexity_response(content_with_json, citations_data)
        processed_content = process_perplexity_response(response, content_with_json)
        
        # Check that the content was processed
        self.assertIn("resources", processed_content)
        self.assertIn("nodes", processed_content)
        
        # Check that citations were extracted
        self.assertIsInstance(processed_content, str)
        self.assertIn("```json", processed_content)
        
        print("✅ Perplexity response processing working correctly")
    
    def test_optimize_prompt_for_perplexity(self):
        """Test prompt optimization for Perplexity"""
        from backend.jobs import optimize_prompt_for_perplexity
        
        base_prompt = "You are a curriculum architect."
        optimized = optimize_prompt_for_perplexity(base_prompt)
        
        self.assertIn("PERPLEXITY-SPECIFIC INSTRUCTIONS", optimized)
        self.assertIn("web search capabilities", optimized)
        self.assertIn("numbered citations", optimized)
        self.assertIn(base_prompt, optimized)
        
        print("✅ Prompt optimization working correctly")
    
    def test_perplexity_response_without_annotations(self):
        """Test handling response without annotations gracefully"""
        from backend.jobs import extract_citations_from_annotations, process_perplexity_response
        
        # Create response without annotations
        message = Mock()
        message.content = "Test content without annotations"
        # No annotations attribute
        
        choice = Mock()
        choice.message = message
        
        response = Mock()
        response.choices = [choice]
        
        # Should not crash and return empty citations
        citations = extract_citations_from_annotations(response)
        self.assertEqual(len(citations), 0)
        
        # Process response should work normally
        processed = process_perplexity_response(response, "Test content")
        self.assertEqual(processed, "Test content")
        
        print("✅ Graceful handling of responses without annotations")

def main():
    """Run all Perplexity optimization tests"""
    print("Testing Perplexity optimization improvements...")
    print("=" * 60)
    
    # Initialize unittest and run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ All Perplexity optimization tests completed!")

if __name__ == "__main__":
    main()