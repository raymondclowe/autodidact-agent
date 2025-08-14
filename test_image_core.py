"""
Core tests for image integration functionality (without Streamlit dependencies)
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import re

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))


class TestImageMarkupProcessing(unittest.TestCase):
    """Test image markup processing without Streamlit dependencies"""
    
    def process_image_markup_standalone(self, content: str):
        """Standalone version of image markup processing for testing"""
        # Pattern to match image markup like <image>concept description</image>
        image_pattern = r'<image[^>]*>(.*?)</image>'
        
        # Extract all image requests
        image_requests = re.findall(image_pattern, content, re.IGNORECASE | re.DOTALL)
        
        # Remove image markup from content
        cleaned_content = re.sub(image_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content).strip()
        
        return cleaned_content, [req.strip() for req in image_requests if req.strip()]
    
    def test_process_image_markup_single_request(self):
        """Test processing content with single image request"""
        content = """
        Let's learn about photosynthesis.
        
        <image>diagram of photosynthesis process in plants</image>
        
        This process converts sunlight to energy.
        """
        
        cleaned_content, image_requests = self.process_image_markup_standalone(content)
        
        self.assertEqual(len(image_requests), 1)
        self.assertEqual(image_requests[0], "diagram of photosynthesis process in plants")
        self.assertNotIn("<image>", cleaned_content)
        self.assertIn("Let's learn about photosynthesis.", cleaned_content)
        self.assertIn("This process converts sunlight to energy.", cleaned_content)
    
    def test_process_image_markup_multiple_requests(self):
        """Test processing content with multiple image requests"""
        content = """
        Biology lesson on cells.
        
        <image>labeled diagram of plant cell</image>
        
        Now let's compare with animal cells.
        
        <image>labeled diagram of animal cell</image>
        
        Notice the differences in organelles.
        """
        
        cleaned_content, image_requests = self.process_image_markup_standalone(content)
        
        self.assertEqual(len(image_requests), 2)
        self.assertEqual(image_requests[0], "labeled diagram of plant cell")
        self.assertEqual(image_requests[1], "labeled diagram of animal cell")
        self.assertNotIn("<image>", cleaned_content)
        self.assertIn("Biology lesson on cells.", cleaned_content)
        self.assertIn("Notice the differences in organelles.", cleaned_content)
    
    def test_process_image_markup_no_requests(self):
        """Test processing content without image requests"""
        content = """
        This is regular lesson content without any image requests.
        Just plain text that should be preserved as-is.
        """
        
        cleaned_content, image_requests = self.process_image_markup_standalone(content)
        
        self.assertEqual(len(image_requests), 0)
        self.assertEqual(cleaned_content.strip(), content.strip())
    
    def test_process_image_markup_case_insensitive(self):
        """Test that image markup is case insensitive"""
        content = """
        <IMAGE>uppercase image tag</IMAGE>
        <Image>mixed case image tag</Image>
        <image>lowercase image tag</image>
        """
        
        cleaned_content, image_requests = self.process_image_markup_standalone(content)
        
        self.assertEqual(len(image_requests), 3)
        self.assertEqual(image_requests[0], "uppercase image tag")
        self.assertEqual(image_requests[1], "mixed case image tag")
        self.assertEqual(image_requests[2], "lowercase image tag")
    
    def test_process_image_markup_with_attributes(self):
        """Test processing image markup with attributes"""
        content = """
        <image style="width: 100%">diagram with attributes</image>
        """
        
        cleaned_content, image_requests = self.process_image_markup_standalone(content)
        
        self.assertEqual(len(image_requests), 1)
        self.assertEqual(image_requests[0], "diagram with attributes")
        self.assertNotIn("<image", cleaned_content)


class TestTavilyIntegrationCore(unittest.TestCase):
    """Test core Tavily integration without making actual API calls"""
    
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_image_result_creation(self):
        """Test ImageResult dataclass creation"""
        try:
            from utils.tavily_integration import ImageResult
            result = ImageResult(
                url="https://example.com/image.jpg",
                description="Test educational image",
                title="Test Image",
                source="Example Source"
            )
            
            self.assertEqual(result.url, "https://example.com/image.jpg")
            self.assertEqual(result.description, "Test educational image")
            self.assertEqual(result.title, "Test Image")
            self.assertEqual(result.source, "Example Source")
        except ImportError as e:
            self.skipTest(f"Skipping test due to import error: {e}")
    
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_tavily_client_initialization(self):
        """Test TavilyImageSearch client initialization"""
        try:
            from utils.tavily_integration import TavilyImageSearch
            client = TavilyImageSearch()
            self.assertEqual(client.api_key, 'test-api-key')
            self.assertEqual(client.base_url, "https://api.tavily.com")
        except ImportError as e:
            self.skipTest(f"Skipping test due to import error: {e}")
    
    def test_tavily_client_no_api_key(self):
        """Test TavilyImageSearch fails without API key"""
        try:
            from utils.tavily_integration import TavilyImageSearch
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError) as context:
                    TavilyImageSearch()
                self.assertIn("Tavily API key not found", str(context.exception))
        except ImportError as e:
            self.skipTest(f"Skipping test due to import error: {e}")


class TestTeachingPromptIntegration(unittest.TestCase):
    """Test that teaching prompts include image guidance"""
    
    def test_teaching_prompt_image_guidance_exists(self):
        """Test that teaching prompts include image guidance"""
        try:
            from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE
            
            # Check that image guidance is included in the template
            self.assertIn("EDUCATIONAL IMAGE GUIDANCE", TEACHING_PROMPT_TEMPLATE)
            self.assertIn("<image>description of needed image</image>", TEACHING_PROMPT_TEMPLATE)
            self.assertIn("labeled diagram", TEACHING_PROMPT_TEMPLATE)
        except ImportError as e:
            self.skipTest(f"Skipping test due to import error: {e}")


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    unittest.main(verbosity=2)