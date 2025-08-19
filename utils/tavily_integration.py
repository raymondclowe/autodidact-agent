"""
Tavily Search API integration for educational image search
Provides functionality to search for relevant educational images using Tavily API
"""

import os
import requests
import json
import logging
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from utils.config import load_tavily_api_key

logger = logging.getLogger('autodidact.tavily')

@dataclass
class ImageResult:
    """Represents an image search result from Tavily"""
    url: str
    description: str
    title: Optional[str] = None
    source: Optional[str] = None

def validate_image_url(url: str, timeout: int = 10) -> bool:
    """
    Validate that a URL actually serves an image file
    
    Args:
        url: The URL to validate
        timeout: Request timeout in seconds
        
    Returns:
        True if URL serves a valid image, False otherwise
    """
    try:
        if not url or not url.startswith(('http://', 'https://')):
            logger.debug(f"Invalid URL format: {url}")
            return False
        
        # First try HEAD request to check headers without downloading
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            
            # Check status code first
            if response.status_code != 200:
                logger.debug(f"HEAD request returned status {response.status_code} for {url}")
                # Don't return False immediately, try GET request as fallback
                raise requests.exceptions.RequestException("HEAD request failed")
            
            content_type = response.headers.get('content-type', '').lower()
            
            # Check if content type indicates an image
            if any(image_type in content_type for image_type in 
                   ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
                    'image/webp', 'image/svg+xml', 'image/bmp']):
                logger.debug(f"URL validated via HEAD request: {url}")
                return True
                
        except requests.exceptions.RequestException:
            # HEAD request failed, try GET request with small range
            logger.debug(f"HEAD request failed for {url}, trying GET request")
        
        # If HEAD fails or doesn't return clear image content-type, try GET with limited download
        response = requests.get(
            url, 
            timeout=timeout, 
            allow_redirects=True, 
            stream=True,
            headers={'Range': 'bytes=0-1023'}  # Only download first 1KB
        )
        
        # Check status code
        if response.status_code not in [200, 206]:  # 206 for partial content
            logger.debug(f"URL returned status {response.status_code}: {url}")
            return False
        
        # Check content type from response
        content_type = response.headers.get('content-type', '').lower()
        if any(image_type in content_type for image_type in 
               ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
                'image/webp', 'image/svg+xml', 'image/bmp']):
            logger.debug(f"URL validated via GET request: {url}")
            return True
        
        # Check for HTML content (common false positive)
        if 'text/html' in content_type:
            logger.debug(f"URL serves HTML instead of image: {url}")
            return False
        
        # Try to read a small portion and check for image magic bytes
        try:
            content = response.content[:20]  # Read first 20 bytes
            
            # Check for common image file signatures
            if (content.startswith(b'\xff\xd8\xff') or  # JPEG
                content.startswith(b'\x89PNG\r\n\x1a\n') or  # PNG
                content.startswith(b'GIF87a') or content.startswith(b'GIF89a') or  # GIF
                content.startswith(b'RIFF') and b'WEBP' in content[:12] or  # WebP
                content.startswith(b'BM') or  # BMP
                content.startswith(b'<svg') or content.startswith(b'<?xml')):  # SVG
                logger.debug(f"URL validated via magic bytes: {url}")
                return True
        except Exception as e:
            logger.debug(f"Could not read content from {url}: {e}")
        
        logger.debug(f"URL does not appear to serve a valid image: {url}")
        return False
        
    except requests.exceptions.Timeout:
        logger.debug(f"Timeout validating URL: {url}")
        return False
    except requests.exceptions.RequestException as e:
        logger.debug(f"Request error validating URL {url}: {e}")
        return False
    except Exception as e:
        logger.debug(f"Unexpected error validating URL {url}: {e}")
        return False

class TavilyImageSearch:
    """Tavily API client for educational image search"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or load_tavily_api_key()
        if not self.api_key:
            raise ValueError("Tavily API key not found. Configure it in Settings or set COPILOT_TAVILY_API_KEY environment variable.")
        
        self.base_url = "https://api.tavily.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        })
    
    def search_educational_images(
        self, 
        concept: str, 
        context: str = "", 
        max_results: int = 3,
        max_retries: int = 3,
        validate_urls: bool = True
    ) -> List[ImageResult]:
        """
        Search for educational images related to a concept with URL validation
        
        Args:
            concept: The main concept to search for
            context: Additional context to improve search relevance
            max_results: Maximum number of valid image results to return
            max_retries: Maximum number of search attempts to find valid images
            validate_urls: Whether to validate that URLs actually serve images
            
        Returns:
            List of ImageResult objects with validated URLs
        """
        try:
            # Construct educational search query
            query_parts = ["educational diagram", concept]
            if context:
                query_parts.append(context)
            
            search_query = " ".join(query_parts)
            
            logger.info(f"Searching Tavily for educational images: {search_query}")
            
            valid_images = []
            attempts = 0
            
            while len(valid_images) < max_results and attempts < max_retries:
                attempts += 1
                
                # Prepare request payload - get more results than needed for validation
                batch_size = min(10, max_results * 2)  # Get 2x more than needed
                
                payload = {
                    "query": search_query,
                    "include_images": True,
                    "include_image_descriptions": True,
                    "max_results": batch_size,
                    "search_depth": "basic"  # Use basic for faster response
                }
                
                # Make API request
                response = self.session.post(
                    f"{self.base_url}/search",
                    json=payload,
                    timeout=10
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract and validate image results
                found_new_images = False
                if 'images' in data:
                    for img_data in data['images']:
                        if len(valid_images) >= max_results:
                            break
                            
                        url = img_data.get('url', '')
                        if not url:
                            continue
                        
                        # Skip if we already have this URL
                        if any(img.url == url for img in valid_images):
                            continue
                        
                        # Validate URL if requested
                        if validate_urls:
                            if not validate_image_url(url):
                                logger.debug(f"Invalid image URL skipped: {url}")
                                continue
                        
                        # Create valid image result
                        image_result = ImageResult(
                            url=url,
                            description=img_data.get('description', ''),
                            title=img_data.get('title'),
                            source=img_data.get('source')
                        )
                        valid_images.append(image_result)
                        found_new_images = True
                        logger.debug(f"Valid image found: {url}")
                
                # If we found some images or reached max results, we can stop
                if len(valid_images) >= max_results:
                    break
                
                # If no new images found in this batch and we've tried, break to avoid infinite loop
                if not found_new_images and attempts > 1:
                    logger.debug("No new valid images found, stopping search")
                    break
                
                # If we still need more images, modify search query for variety
                if len(valid_images) < max_results and attempts < max_retries:
                    # Add variety terms to get different results
                    variety_terms = ["illustration", "chart", "visual", "graphic", "textbook"]
                    if attempts <= len(variety_terms):
                        search_query = f"{' '.join(query_parts)} {variety_terms[attempts-1]}"
                    else:
                        # Use different search approach
                        search_query = f"academic {' '.join(query_parts)} educational resource"
                    
                    logger.debug(f"Attempt {attempts}: Modified search query to '{search_query}'")
                    time.sleep(0.5)  # Brief pause between requests
                
                # If no images available from API, break
                if 'images' not in data or len(data['images']) == 0:
                    logger.debug("No more images available from Tavily")
                    break
            
            logger.info(f"Found {len(valid_images)} validated educational images for concept: {concept} (after {attempts} attempts)")
            return valid_images
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Tavily image search: {e}")
            return []
    
    def search_specific_image(
        self, 
        specific_request: str, 
        subject_area: str = "",
        validate_url: bool = True
    ) -> Optional[ImageResult]:
        """
        Search for a specific image based on detailed request with URL validation
        
        Args:
            specific_request: Specific image description (e.g., "diagram of photosynthesis process")
            subject_area: Subject area for better filtering (e.g., "biology", "chemistry")
            validate_url: Whether to validate that the URL actually serves an image
            
        Returns:
            Single best matching ImageResult with validated URL or None if no suitable image found
        """
        try:
            # Construct specific search query
            query_parts = [specific_request]
            if subject_area:
                query_parts.append(subject_area)
            query_parts.extend(["educational", "diagram", "illustration"])
            
            search_query = " ".join(query_parts)
            
            # Search for multiple results to increase chances of finding a valid one
            results = self.search_educational_images(
                search_query, 
                max_results=5,  # Get more results to have options
                validate_urls=validate_url
            )
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Error searching for specific image: {e}")
            return None

# Global instance for easy access
_tavily_client: Optional[TavilyImageSearch] = None

def get_tavily_client() -> TavilyImageSearch:
    """Get or create global Tavily client instance"""
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyImageSearch()
    return _tavily_client

def search_educational_image(concept: str, context: str = "", validate_url: bool = True) -> Optional[ImageResult]:
    """
    Convenience function to search for a single educational image with URL validation
    
    Args:
        concept: Main concept to search for
        context: Additional context for better search results
        validate_url: Whether to validate that the URL actually serves an image
        
    Returns:
        Single ImageResult with validated URL or None if no suitable image found
    """
    try:
        client = get_tavily_client()
        results = client.search_educational_images(
            concept, 
            context, 
            max_results=1,
            validate_urls=validate_url
        )
        return results[0] if results else None
    except ValueError:
        # Re-raise ValueError (like missing API key) so caller can handle it appropriately
        raise
    except Exception as e:
        logger.error(f"Error in educational image search: {e}")
        return None