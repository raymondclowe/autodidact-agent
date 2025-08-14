"""
Tavily Search API integration for educational image search
Provides functionality to search for relevant educational images using Tavily API
"""

import os
import logging
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger('autodidact.tavily')

@dataclass
class ImageResult:
    """Represents an image search result from Tavily"""
    url: str
    description: str
    title: Optional[str] = None
    source: Optional[str] = None

class TavilyImageSearch:
    """Tavily API client for educational image search"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('COPILOT_TAVILY_API_KEY')
        if not self.api_key:
            raise ValueError("Tavily API key not found. Set COPILOT_TAVILY_API_KEY environment variable.")
        
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
        max_results: int = 3
    ) -> List[ImageResult]:
        """
        Search for educational images related to a concept
        
        Args:
            concept: The main concept to search for
            context: Additional context to improve search relevance
            max_results: Maximum number of image results to return
            
        Returns:
            List of ImageResult objects
        """
        try:
            # Construct educational search query
            query_parts = ["educational diagram", concept]
            if context:
                query_parts.append(context)
            
            search_query = " ".join(query_parts)
            
            logger.info(f"Searching Tavily for educational images: {search_query}")
            
            # Prepare request payload
            payload = {
                "query": search_query,
                "include_images": True,
                "include_image_descriptions": True,
                "max_results": max_results,
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
            
            # Extract image results
            images = []
            if 'images' in data:
                for img_data in data['images'][:max_results]:
                    images.append(ImageResult(
                        url=img_data.get('url', ''),
                        description=img_data.get('description', ''),
                        title=img_data.get('title'),
                        source=img_data.get('source')
                    ))
            
            logger.info(f"Found {len(images)} educational images for concept: {concept}")
            return images
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Tavily image search: {e}")
            return []
    
    def search_specific_image(
        self, 
        specific_request: str, 
        subject_area: str = ""
    ) -> Optional[ImageResult]:
        """
        Search for a specific image based on detailed request
        
        Args:
            specific_request: Specific image description (e.g., "diagram of photosynthesis process")
            subject_area: Subject area for better filtering (e.g., "biology", "chemistry")
            
        Returns:
            Single best matching ImageResult or None if no suitable image found
        """
        try:
            # Construct specific search query
            query_parts = [specific_request]
            if subject_area:
                query_parts.append(subject_area)
            query_parts.extend(["educational", "diagram", "illustration"])
            
            search_query = " ".join(query_parts)
            
            results = self.search_educational_images(search_query, max_results=1)
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

def search_educational_image(concept: str, context: str = "") -> Optional[ImageResult]:
    """
    Convenience function to search for a single educational image
    
    Args:
        concept: Main concept to search for
        context: Additional context for better search results
        
    Returns:
        Single ImageResult or None if no suitable image found
    """
    try:
        client = get_tavily_client()
        results = client.search_educational_images(concept, context, max_results=1)
        return results[0] if results else None
    except Exception as e:
        logger.error(f"Error in educational image search: {e}")
        return None