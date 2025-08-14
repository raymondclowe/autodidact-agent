"""
Image display component for educational content
Provides functions to display images from Tavily search results
"""

import streamlit as st
import logging
from typing import Optional, List
from utils.tavily_integration import ImageResult

logger = logging.getLogger('autodidact.image_component')

def cache_displayed_image(image_result: ImageResult, context: str = "") -> None:
    """Cache a displayed image in the session state for AI context awareness"""
    try:
        if hasattr(st, 'session_state') and 'graph_state' in st.session_state:
            # Get current displayed images or initialize empty list
            displayed_images = st.session_state.graph_state.get('displayed_images', [])
            
            # Create image cache entry
            image_cache_entry = {
                'url': image_result.url,
                'description': image_result.description or "Educational image",
                'context': context,
                'title': getattr(image_result, 'title', None),
                'source': getattr(image_result, 'source', None)
            }
            
            # Check if this image is already cached (avoid duplicates)
            for existing in displayed_images:
                if existing.get('url') == image_result.url:
                    return
            
            # Add to cache
            displayed_images.append(image_cache_entry)
            st.session_state.graph_state['displayed_images'] = displayed_images
            
            logger.debug(f"Cached image for AI context: {image_result.description}")
            
    except Exception as e:
        logger.warning(f"Failed to cache displayed image: {e}")

def get_images_context_for_ai() -> str:
    """Get context about images currently visible to the user for AI prompts"""
    try:
        if hasattr(st, 'session_state') and 'graph_state' in st.session_state:
            displayed_images = st.session_state.graph_state.get('displayed_images', [])
            
            if not displayed_images:
                return ""
            
            context_parts = []
            for i, img in enumerate(displayed_images[-3:], 1):  # Last 3 images only
                desc = img.get('description', 'Educational image')
                context = img.get('context', '')
                context_parts.append(f"{i}. {desc}" + (f" ({context})" if context else ""))
            
            return f"\n\nIMAGES CURRENTLY VISIBLE TO STUDENT:\n" + "\n".join(context_parts)
        
    except Exception as e:
        logger.warning(f"Failed to get images context: {e}")
    
    return ""

def display_educational_image(
    image_result: ImageResult, 
    caption: Optional[str] = None,
    width: Optional[int] = None,
    use_container_width: bool = True,
    context: str = ""
) -> None:
    """
    Display an educational image from Tavily search result
    
    Args:
        image_result: ImageResult object from Tavily search
        caption: Optional custom caption (uses description if not provided)
        width: Optional width in pixels
        use_container_width: Whether to use container width for responsive display
        context: Context about when/why this image is shown (for AI awareness)
    """
    try:
        if not image_result or not image_result.url:
            logger.warning("No valid image result provided")
            return
        
        # Use provided caption or fall back to image description
        display_caption = caption or image_result.description or "Educational image"
        
        # Display the image
        st.image(
            image_result.url,
            caption=display_caption,
            width=width,
            use_container_width=use_container_width
        )
        
        # Add source attribution if available
        if image_result.source:
            st.caption(f"Source: {image_result.source}")
        
        # Cache this image for AI context awareness
        cache_displayed_image(image_result, context)
            
        logger.debug(f"Displayed educational image: {image_result.url}")
        
    except Exception as e:
        logger.error(f"Error displaying educational image: {e}")
        # Show fallback message instead of crashing
        st.info("📷 Educational image not available")

def display_image_gallery(
    image_results: List[ImageResult], 
    columns: int = 2,
    show_captions: bool = True
) -> None:
    """
    Display multiple educational images in a gallery layout
    
    Args:
        image_results: List of ImageResult objects
        columns: Number of columns in the gallery
        show_captions: Whether to show captions under images
    """
    try:
        if not image_results:
            logger.info("No images to display in gallery")
            return
        
        # Create columns for gallery layout
        cols = st.columns(columns)
        
        for idx, image_result in enumerate(image_results):
            with cols[idx % columns]:
                if show_captions:
                    display_educational_image(image_result)
                else:
                    display_educational_image(image_result, caption="")
                    
        logger.debug(f"Displayed gallery with {len(image_results)} educational images")
        
    except Exception as e:
        logger.error(f"Error displaying image gallery: {e}")
        st.info("📷 Educational images not available")

def create_image_placeholder(text: str = "Loading educational image...") -> None:
    """
    Create a placeholder while images are loading
    
    Args:
        text: Placeholder text to display
    """
    st.info(f"📷 {text}")

def process_image_markup(content: str) -> tuple[str, List[str]]:
    """
    Extract image requests from content markup and return cleaned content
    
    Args:
        content: Content string that may contain image markup
        
    Returns:
        Tuple of (cleaned_content, image_requests)
    """
    import re
    
    # Pattern to match image markup like <image>concept description</image>
    image_pattern = r'<image[^>]*>(.*?)</image>'
    
    # Extract all image requests
    image_requests = re.findall(image_pattern, content, re.IGNORECASE | re.DOTALL)
    
    # Remove image markup from content
    cleaned_content = re.sub(image_pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up extra whitespace
    cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content).strip()
    
    logger.debug(f"Extracted {len(image_requests)} image requests from content")
    
    return cleaned_content, [req.strip() for req in image_requests if req.strip()]

def render_content_with_images(
    content: str, 
    context: str = "",
    auto_search: bool = True
) -> None:
    """
    Render content and automatically fetch/display requested images
    
    Args:
        content: Content string that may contain image markup
        context: Additional context for image searches
        auto_search: Whether to automatically search for images
    """
    try:
        # Process content to extract image requests
        cleaned_content, image_requests = process_image_markup(content)
        
        # Display the main content first
        st.markdown(cleaned_content, unsafe_allow_html=True)
        
        # If there are image requests and auto search is enabled
        if image_requests and auto_search:
            st.markdown("---")
            st.markdown("**📚 Related Educational Images:**")
            
            # Search and display images for each request
            for idx, image_request in enumerate(image_requests):
                try:
                    from utils.tavily_integration import search_educational_image
                    
                    # Show loading placeholder
                    placeholder = st.empty()
                    with placeholder:
                        create_image_placeholder(f"Searching for: {image_request}")
                    
                    # Search for the image
                    image_result = search_educational_image(image_request, context)
                    
                    # Clear placeholder and display result
                    placeholder.empty()
                    
                    if image_result:
                        st.markdown(f"**{image_request.title()}**")
                        display_educational_image(image_result, context=f"Teaching context: {context}")
                    else:
                        st.info(f"📷 No suitable image found for: {image_request}")
                        
                    # Add spacing between images
                    if idx < len(image_requests) - 1:
                        st.markdown("")
                        
                except Exception as e:
                    logger.error(f"Error processing image request '{image_request}': {e}")
                    placeholder.empty()
                    st.warning(f"Could not load image for: {image_request}")
        
        logger.debug(f"Rendered content with {len(image_requests)} image requests")
        
    except Exception as e:
        logger.error(f"Error rendering content with images: {e}")
        # Fallback: just display the original content
        st.markdown(content, unsafe_allow_html=True)