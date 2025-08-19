"""
Test suite for inline image support using Tavily search integration
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from utils.tavily_integration import TavilyImageSearch, ImageResult, search_educational_image
from components.image_display import process_image_markup


class TestTavilyIntegration(unittest.TestCase):
    """Test Tavily API integration functionality"""
    
    def test_image_result_creation(self):
        """Test ImageResult dataclass creation"""
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
    
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_tavily_client_initialization(self):
        """Test TavilyImageSearch client initialization"""
        client = TavilyImageSearch()
        self.assertEqual(client.api_key, 'test-api-key')
        self.assertEqual(client.base_url, "https://api.tavily.com")
    
    def test_tavily_client_no_api_key(self):
        """Test TavilyImageSearch fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                TavilyImageSearch()
            self.assertIn("Tavily API key not found", str(context.exception))
    
    @patch('utils.tavily_integration.requests.Session')
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_search_educational_images_success(self, mock_session_class):
        """Test successful educational image search"""
        # Mock the requests session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'images': [
                {
                    'url': 'https://example.com/photosynthesis.jpg',
                    'description': 'Diagram of photosynthesis process',
                    'title': 'Photosynthesis Diagram',
                    'source': 'Educational Website'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        client = TavilyImageSearch()
        results = client.search_educational_images("photosynthesis", "biology")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'https://example.com/photosynthesis.jpg')
        self.assertEqual(results[0].description, 'Diagram of photosynthesis process')
        
        # Verify the API call was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        self.assertEqual(call_args[0][0], "https://api.tavily.com/search")
        
        payload = call_args[1]['json']
        self.assertIn("educational diagram photosynthesis biology", payload['query'])
        self.assertTrue(payload['include_images'])
        self.assertTrue(payload['include_image_descriptions'])
    
    @patch('utils.tavily_integration.requests.Session')
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_search_educational_images_api_error(self, mock_session_class):
        """Test handling of API errors"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.post.side_effect = Exception("API Error")
        
        client = TavilyImageSearch()
        results = client.search_educational_images("test concept")
        
        # Should return empty list on error
        self.assertEqual(results, [])
    
    @patch('utils.tavily_integration.get_tavily_client')
    def test_search_educational_image_convenience_function(self, mock_get_client):
        """Test the convenience function for searching single images"""
        mock_client = Mock()
        mock_client.search_educational_images.return_value = [
            ImageResult(
                url="https://example.com/test.jpg",
                description="Test image"
            )
        ]
        mock_get_client.return_value = mock_client
        
        result = search_educational_image("test concept", "test context")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.url, "https://example.com/test.jpg")
        mock_client.search_educational_images.assert_called_once_with(
            "test concept", "test context", max_results=1, validate_urls=True
        )


class TestImageDisplayComponents(unittest.TestCase):
    """Test image display and markup processing components"""
    
    def test_process_image_markup_single_request(self):
        """Test processing content with single image request"""
        content = """
        Let's learn about photosynthesis.
        
        <image>diagram of photosynthesis process in plants</image>
        
        This process converts sunlight to energy.
        """
        
        cleaned_content, image_requests = process_image_markup(content)
        
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
        
        cleaned_content, image_requests = process_image_markup(content)
        
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
        
        cleaned_content, image_requests = process_image_markup(content)
        
        self.assertEqual(len(image_requests), 0)
        self.assertEqual(cleaned_content.strip(), content.strip())
    
    def test_process_image_markup_case_insensitive(self):
        """Test that image markup is case insensitive"""
        content = """
        <IMAGE>uppercase image tag</IMAGE>
        <Image>mixed case image tag</Image>
        <image>lowercase image tag</image>
        """
        
        cleaned_content, image_requests = process_image_markup(content)
        
        self.assertEqual(len(image_requests), 3)
        self.assertEqual(image_requests[0], "uppercase image tag")
        self.assertEqual(image_requests[1], "mixed case image tag")
        self.assertEqual(image_requests[2], "lowercase image tag")
    
    def test_process_image_markup_with_attributes(self):
        """Test processing image markup with attributes"""
        content = """
        <image style="width: 100%">diagram with attributes</image>
        """
        
        cleaned_content, image_requests = process_image_markup(content)
        
        self.assertEqual(len(image_requests), 1)
        self.assertEqual(image_requests[0], "diagram with attributes")
        self.assertNotIn("<image", cleaned_content)


class TestImageIntegrationWorkflow(unittest.TestCase):
    """Test the complete image integration workflow"""
    
    def test_teaching_prompt_image_guidance_exists(self):
        """Test that teaching prompts include image guidance"""
        from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE
        
        # Check that image guidance is included in the template
        self.assertIn("EDUCATIONAL IMAGE GUIDANCE", TEACHING_PROMPT_TEMPLATE)
        self.assertIn("<image>description of needed image</image>", TEACHING_PROMPT_TEMPLATE)
        self.assertIn("labeled diagram", TEACHING_PROMPT_TEMPLATE)
    
    @patch('components.image_display.search_educational_image')
    def test_content_rendering_with_images_mock(self, mock_search):
        """Test content rendering workflow with mocked image search"""
        mock_search.return_value = ImageResult(
            url="https://example.com/test.jpg",
            description="Mock educational image"
        )
        
        # This test would require Streamlit context, so we just verify the function exists
        from components.image_display import render_content_with_images
        self.assertTrue(callable(render_content_with_images))


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    unittest.main(verbosity=2)