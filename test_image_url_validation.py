"""
Test suite for image URL validation functionality in Tavily integration
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from utils.tavily_integration import (
    TavilyImageSearch, 
    ImageResult, 
    search_educational_image,
    validate_image_url
)


class TestImageUrlValidation(unittest.TestCase):
    """Test URL validation functionality"""
    
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_valid_jpeg_via_head(self, mock_head):
        """Test validation of valid JPEG URL via HEAD request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_head.return_value = mock_response
        
        result = validate_image_url("https://example.com/image.jpg")
        
        self.assertTrue(result)
        mock_head.assert_called_once_with(
            "https://example.com/image.jpg", 
            timeout=10, 
            allow_redirects=True
        )
    
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_valid_png_via_head(self, mock_head):
        """Test validation of valid PNG URL via HEAD request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/png'}
        mock_head.return_value = mock_response
        
        result = validate_image_url("https://example.com/image.png")
        
        self.assertTrue(result)
    
    @patch('utils.tavily_integration.requests.get')
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_fallback_to_get(self, mock_head, mock_get):
        """Test fallback to GET request when HEAD fails"""
        # HEAD request fails
        mock_head.side_effect = Exception("HEAD failed")
        
        # GET request succeeds
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.headers = {'content-type': 'image/jpeg'}
        mock_get_response.content = b'\xff\xd8\xff'  # JPEG magic bytes
        mock_get.return_value = mock_get_response
        
        result = validate_image_url("https://example.com/image.jpg")
        
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('utils.tavily_integration.requests.get')
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_magic_bytes_validation(self, mock_head, mock_get):
        """Test validation using image magic bytes when content-type is unclear"""
        # HEAD request doesn't return clear content-type
        mock_head.side_effect = Exception("HEAD failed")
        
        # GET request returns binary content without clear content-type
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.headers = {'content-type': 'application/octet-stream'}
        mock_get_response.content = b'\x89PNG\r\n\x1a\n'  # PNG magic bytes
        mock_get.return_value = mock_get_response
        
        result = validate_image_url("https://example.com/image.png")
        
        self.assertTrue(result)
    
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_html_content(self, mock_head):
        """Test rejection of URLs serving HTML instead of images"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_head.return_value = mock_response
        
        result = validate_image_url("https://example.com/page.html")
        
        self.assertFalse(result)
    
    @patch('utils.tavily_integration.requests.get')
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_404_error(self, mock_head, mock_get):
        """Test rejection of URLs returning 404 errors"""
        mock_head.side_effect = Exception("HEAD failed")
        
        mock_get_response = Mock()
        mock_get_response.status_code = 404
        mock_get.return_value = mock_get_response
        
        result = validate_image_url("https://example.com/missing.jpg")
        
        self.assertFalse(result)
    
    def test_validate_image_url_invalid_format(self):
        """Test rejection of invalid URL formats"""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com/image.jpg",
            None
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                result = validate_image_url(url)
                self.assertFalse(result)
    
    @patch('utils.tavily_integration.requests.head')
    def test_validate_image_url_timeout(self, mock_head):
        """Test handling of request timeouts"""
        mock_head.side_effect = Exception("Timeout")
        
        result = validate_image_url("https://slow-example.com/image.jpg")
        
        self.assertFalse(result)


class TestTavilyIntegrationWithValidation(unittest.TestCase):
    """Test Tavily integration with URL validation enabled"""
    
    @patch('utils.tavily_integration.validate_image_url')
    @patch('utils.tavily_integration.requests.Session')
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_search_educational_images_with_validation(self, mock_session_class, mock_validate):
        """Test search with URL validation enabled"""
        # Mock the requests session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'images': [
                {
                    'url': 'https://example.com/valid.jpg',
                    'description': 'Valid image',
                    'title': 'Valid Image',
                    'source': 'Educational Website'
                },
                {
                    'url': 'https://example.com/invalid.html',
                    'description': 'Invalid image',
                    'title': 'Invalid Image',
                    'source': 'Bad Website'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # Mock validation - first URL valid, second invalid
        mock_validate.side_effect = lambda url: url.endswith('.jpg')
        
        client = TavilyImageSearch()
        results = client.search_educational_images("test concept", validate_urls=True)
        
        # Should only return the valid image
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'https://example.com/valid.jpg')
        
        # Validation should have been called for both URLs (but retry logic may call it more)
        self.assertGreaterEqual(mock_validate.call_count, 2)
    
    @patch('utils.tavily_integration.validate_image_url')
    @patch('utils.tavily_integration.requests.Session')
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_search_educational_images_retry_on_invalid_urls(self, mock_session_class, mock_validate):
        """Test retry behavior when initial URLs are invalid"""
        # Mock the requests session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # First call returns invalid URLs, second call returns valid URL
        mock_responses = [
            Mock(),
            Mock()
        ]
        
        # First response - all invalid URLs
        mock_responses[0].json.return_value = {
            'images': [
                {'url': 'https://example.com/invalid1.html', 'description': 'Invalid 1'},
                {'url': 'https://example.com/invalid2.html', 'description': 'Invalid 2'}
            ]
        }
        mock_responses[0].raise_for_status.return_value = None
        
        # Second response - valid URLs
        mock_responses[1].json.return_value = {
            'images': [
                {'url': 'https://example.com/valid.jpg', 'description': 'Valid image'}
            ]
        }
        mock_responses[1].raise_for_status.return_value = None
        
        mock_session.post.side_effect = mock_responses
        
        # Mock validation - only .jpg URLs are valid
        mock_validate.side_effect = lambda url: url.endswith('.jpg')
        
        client = TavilyImageSearch()
        results = client.search_educational_images("test concept", max_results=1, validate_urls=True)
        
        # Should find the valid image after retry
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'https://example.com/valid.jpg')
        
        # Should have made multiple API calls due to retry
        self.assertEqual(mock_session.post.call_count, 2)
    
    @patch('utils.tavily_integration.validate_image_url')
    @patch('utils.tavily_integration.get_tavily_client')
    def test_search_educational_image_convenience_function_with_validation(self, mock_get_client, mock_validate):
        """Test convenience function with validation"""
        mock_client = Mock()
        mock_client.search_educational_images.return_value = [
            ImageResult(
                url="https://example.com/valid.jpg",
                description="Valid test image"
            )
        ]
        mock_get_client.return_value = mock_client
        
        result = search_educational_image("test concept", validate_url=True)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.url, "https://example.com/valid.jpg")
        
        # Verify the client was called with validation enabled
        mock_client.search_educational_images.assert_called_once_with(
            "test concept", "", max_results=1, validate_urls=True
        )
    
    @patch('utils.tavily_integration.requests.Session')
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_search_educational_images_validation_disabled(self, mock_session_class):
        """Test search with URL validation disabled"""
        # Mock the requests session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'images': [
                {
                    'url': 'https://example.com/image.jpg',
                    'description': 'Test image',
                    'title': 'Test Image',
                    'source': 'Educational Website'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        client = TavilyImageSearch()
        results = client.search_educational_images("test concept", validate_urls=False)
        
        # Should return the result without validation
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].url, 'https://example.com/image.jpg')


class TestImageSearchIntegration(unittest.TestCase):
    """Test integration scenarios"""
    
    @patch('utils.tavily_integration.validate_image_url')
    @patch('utils.tavily_integration.requests.Session')
    @patch.dict(os.environ, {'COPILOT_TAVILY_API_KEY': 'test-api-key'})
    def test_no_valid_images_found(self, mock_session_class, mock_validate):
        """Test behavior when no valid images are found after retries"""
        # Mock the requests session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.json.return_value = {
            'images': [
                {'url': 'https://example.com/invalid1.html', 'description': 'Invalid 1'},
                {'url': 'https://example.com/invalid2.html', 'description': 'Invalid 2'}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        
        # All URLs are invalid
        mock_validate.return_value = False
        
        client = TavilyImageSearch()
        results = client.search_educational_images("test concept", max_retries=2, validate_urls=True)
        
        # Should return empty list
        self.assertEqual(len(results), 0)
        
        # Should have attempted multiple searches
        self.assertGreaterEqual(mock_session.post.call_count, 2)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    unittest.main(verbosity=2)