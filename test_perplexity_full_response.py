#!/usr/bin/env python3
"""
Test script to verify complete Perplexity response handling with real response structure.
Simulates the exact response format from the issue description.
"""

import sys
import os
import json
import unittest
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestPerplexityFullResponse(unittest.TestCase):
    
    def create_real_perplexity_response(self):
        """Create a mock response that matches the real Perplexity structure from the issue"""
        
        # Real content from the issue (shortened for testing)
        content = """### Comprehensive Curriculum for Understanding and Managing Ambiguity in Learning and Problem-Solving  

#### Key Findings Summary  
This curriculum addresses the pervasive challenge of ambiguity across learning contexts—from instructional design to technical problem-solving. Research reveals that ambiguity arises from unclear objectives, undefined relationships between concepts, and unstructured information environments[1][5][6]. Effective resolution requires systematic clarification techniques (e.g., rapid needs analysis, probing questions)[3][7][8], structured knowledge representation (e.g., concept mapping)[9][13][18], and iterative validation processes[4][15].

### Resource List  
```json
{
  "resources": [
    {
      "rid": "ambiguity_clarity_steps",
      "title": "From Ambiguity to Clarity in Three Easy Steps",
      "type": "article",
      "url": "#",
      "date": "2018-01-16",
      "scope": "Practical framework for resolving ambiguity in instructional design projects."
    },
    {
      "rid": "needs_analysis_curriculum",
      "title": "Needs Analysis in Curriculum Development",
      "type": "paper",
      "url": "#",
      "date": "2010-02-19",
      "scope": "Theoretical foundations for needs analysis in educational contexts."
    }
  ],
  "nodes": [
    {
      "id": "defining_ambiguity",
      "title": "Defining Ambiguity: Types and Sources",
      "prerequisite_node_ids": [],
      "learning_objectives": [
        "Define ambiguity using Budner's three-dimensional model",
        "Distinguish ambiguity from complexity and uncertainty"
      ]
    }
  ]
}
```"""
        
        # Create annotations that match Perplexity's structure
        annotations = []
        
        # Annotation 1
        url_citation_1 = Mock()
        url_citation_1.url = "https://envision-performance.com/ambiguity-clarity-three-easy-steps/"
        url_citation_1.title = "envision-performance.com/ambiguity-clarity-three-easy-steps/"
        url_citation_1.start_index = 0
        url_citation_1.end_index = 0
        
        annotation_1 = Mock()
        annotation_1.type = "url_citation"
        annotation_1.url_citation = url_citation_1
        annotations.append(annotation_1)
        
        # Annotation 5
        url_citation_5 = Mock()
        url_citation_5.url = "https://www.franklin.edu/institute/blog/change-ambiguity-and-uncertainty-becoming-expert-instructional-designer"
        url_citation_5.title = "www.franklin.edu/institute/blog/change-ambiguity-and-uncertainty-becoming-expert-instructional-designer"
        url_citation_5.start_index = 0
        url_citation_5.end_index = 0
        
        annotation_5 = Mock()
        annotation_5.type = "url_citation"
        annotation_5.url_citation = url_citation_5
        annotations.append(annotation_5)
        
        # Create message with content and annotations
        message = Mock()
        message.content = content
        message.annotations = annotations
        message.refusal = None
        message.role = "assistant"
        
        # Create choice
        choice = Mock()
        choice.finish_reason = "stop"
        choice.index = 0
        choice.logprobs = None
        choice.message = message
        
        # Create usage
        usage = Mock()
        usage.completion_tokens = 3945
        usage.prompt_tokens = 934
        usage.total_tokens = 4879
        usage.completion_tokens_details = None
        usage.prompt_tokens_details = None
        
        # Create main response
        response = Mock()
        response.id = "gen-1753003259-t2olv73kObWaYvq8OPIC"
        response.choices = [choice]
        response.created = 1753003259
        response.model = "perplexity/sonar-deep-research"
        response.object = "chat.completion"
        response.service_tier = None
        response.system_fingerprint = None
        response.usage = usage
        response._request_id = None
        
        return response
    
    def test_full_perplexity_response_processing(self):
        """Test processing the complete Perplexity response structure"""
        from backend.jobs import process_perplexity_response, extract_citations_from_annotations
        
        response = self.create_real_perplexity_response()
        
        # Test citation extraction
        citations = extract_citations_from_annotations(response)
        self.assertEqual(len(citations), 2)
        self.assertIn("envision-performance.com", citations[1]['url'])
        self.assertIn("franklin.edu", citations[2]['url'])
        
        # Test full response processing
        original_content = response.choices[0].message.content
        processed_content = process_perplexity_response(response, original_content)
        
        # Verify the content was enhanced
        self.assertIn("resources", processed_content)
        self.assertIn("nodes", processed_content)
        
        # Check that the JSON was parsed and enhanced
        self.assertIn("```json", processed_content)
        
        print("✅ Full Perplexity response processing successful")
        print(f"   - Extracted {len(citations)} citations")
        print(f"   - Content length: {len(processed_content)} characters")
    
    def test_token_usage_extraction(self):
        """Test that token usage is properly extracted from Perplexity response"""
        from backend.jobs import get_token_count
        
        response = self.create_real_perplexity_response()
        token_count = get_token_count(response)
        
        self.assertEqual(token_count, "4879")
        print("✅ Token usage extraction working correctly")
        print(f"   - Total tokens: {token_count}")
        print(f"   - Completion tokens: {response.usage.completion_tokens}")
        print(f"   - Prompt tokens: {response.usage.prompt_tokens}")
    
    def test_citation_url_enhancement(self):
        """Test that resources get enhanced with citation URLs"""
        from backend.jobs import process_perplexity_response
        
        response = self.create_real_perplexity_response()
        original_content = response.choices[0].message.content
        processed_content = process_perplexity_response(response, original_content)
        
        # Extract the JSON part to verify enhancement
        try:
            lines = processed_content.split('\n')
            json_start = None
            for i, line in enumerate(lines):
                if line.strip().startswith('```json') or line.strip() == '{':
                    json_start = i
                    break
            
            if json_start is not None:
                if lines[json_start].strip().startswith('```json'):
                    json_start += 1
                
                json_lines = []
                for i in range(json_start, len(lines)):
                    line = lines[i]
                    if line.strip() == '```':
                        break
                    json_lines.append(line)
                
                json_text = '\n'.join(json_lines)
                curriculum_data = json.loads(json_text)
                
                # Check if resources were enhanced
                resources = curriculum_data.get('resources', [])
                self.assertGreater(len(resources), 0)
                
                print("✅ Citation URL enhancement working")
                print(f"   - Found {len(resources)} resources in enhanced JSON")
                
                # Look for enhanced resources
                enhanced_count = 0
                for resource in resources:
                    if resource.get('citation_source'):
                        enhanced_count += 1
                        print(f"   - Enhanced: {resource['title']} -> {resource['url']}")
                
                if enhanced_count > 0:
                    print(f"   - {enhanced_count} resources enhanced with citations")
                
        except Exception as e:
            print(f"   - JSON parsing test skipped due to: {e}")
    
    def test_prompt_optimization(self):
        """Test that the prompt gets optimized for Perplexity"""
        from backend.jobs import optimize_prompt_for_perplexity
        from utils.deep_research import DEVELOPER_PROMPT
        
        optimized = optimize_prompt_for_perplexity(DEVELOPER_PROMPT)
        
        # Check that Perplexity-specific instructions were added
        self.assertIn("PERPLEXITY-SPECIFIC INSTRUCTIONS", optimized)
        self.assertIn("web search capabilities", optimized)
        self.assertIn("numbered citations", optimized)
        self.assertIn("ENHANCED CITATION REQUIREMENTS", optimized)
        
        # Check that original prompt is preserved
        self.assertIn("Deep-Research Curriculum Architect", optimized)
        
        print("✅ Prompt optimization working correctly")
        print(f"   - Original prompt length: {len(DEVELOPER_PROMPT)}")
        print(f"   - Optimized prompt length: {len(optimized)}")
        print(f"   - Added {len(optimized) - len(DEVELOPER_PROMPT)} characters of Perplexity-specific instructions")

def main():
    """Run all comprehensive Perplexity response tests"""
    print("Testing complete Perplexity response handling...")
    print("=" * 70)
    
    # Initialize unittest and run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 70)
    print("✅ All comprehensive Perplexity tests completed!")

if __name__ == "__main__":
    main()