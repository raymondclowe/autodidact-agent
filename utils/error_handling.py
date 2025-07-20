"""
Error handling utilities for Autodidact
Provides enhanced error parsing and user-friendly error messages
"""

import json
import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def parse_openrouter_error(response) -> Optional[Dict]:
    """
    Parse OpenRouter error response to extract meaningful error information.
    
    OpenRouter error responses have this structure:
    {
        "error": {
            "message": "Provider returned error",
            "code": 400,
            "metadata": {
                "raw": "{\"error\":{\"message\":\"...\",\"type\":\"...\",\"code\":...}}",
                "provider_name": "Perplexity"
            }
        }
    }
    
    Args:
        response: API response object or dict
        
    Returns:
        Dict with parsed error info or None if not an OpenRouter error
    """
    try:
        # Handle both response objects and dicts
        if hasattr(response, '__dict__'):
            error_data = getattr(response, 'error', None)
        elif isinstance(response, dict):
            error_data = response.get('error')
        else:
            return None
        
        if not error_data:
            return None
        
        # Extract OpenRouter error structure
        if hasattr(error_data, '__dict__'):
            error_dict = error_data.__dict__
        elif isinstance(error_data, dict):
            error_dict = error_data
        else:
            return None
        
        # Look for metadata with raw provider error
        metadata = error_dict.get('metadata', {})
        if not metadata:
            return None
        
        provider_name = metadata.get('provider_name', 'Unknown Provider')
        raw_error = metadata.get('raw', '')
        
        if not raw_error:
            return None
        
        # Parse the raw error JSON
        try:
            raw_error_data = json.loads(raw_error)
            provider_error = raw_error_data.get('error', {})
            
            return {
                'provider_name': provider_name,
                'error_type': provider_error.get('type', 'unknown'),
                'error_message': provider_error.get('message', ''),
                'error_code': provider_error.get('code', ''),
                'raw_error': raw_error
            }
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse raw error JSON: {raw_error}")
            return {
                'provider_name': provider_name,
                'error_type': 'parse_error',
                'error_message': raw_error,
                'error_code': error_dict.get('code', ''),
                'raw_error': raw_error
            }
            
    except Exception as e:
        logger.warning(f"Error parsing OpenRouter response: {e}")
        return None


def extract_token_info(error_message: str) -> Optional[Dict]:
    """
    Extract token information from error messages.
    
    Example: "Requested 113643 to generate tokens, following a prompt of length 14657, 
             which exceeds the max limit of 128000 tokens."
    
    Args:
        error_message: The error message string
        
    Returns:
        Dict with token info or None if no token info found
    """
    try:
        # Pattern to match token limit error messages
        token_pattern = re.compile(
            r'Requested (\d+) to generate tokens, following a prompt of length (\d+), '
            r'which exceeds the max limit of (\d+) tokens'
        )
        
        match = token_pattern.search(error_message)
        if match:
            requested_tokens = int(match.group(1))
            prompt_length = int(match.group(2))
            max_limit = int(match.group(3))
            
            return {
                'requested_tokens': requested_tokens,
                'prompt_length': prompt_length,
                'max_limit': max_limit,
                'total_requested': requested_tokens + prompt_length
            }
        
        # Alternative pattern for different token error formats
        alt_pattern = re.compile(r'(\d+) tokens.*exceeds.*limit.*(\d+)', re.IGNORECASE)
        match = alt_pattern.search(error_message)
        if match:
            total_tokens = int(match.group(1))
            max_limit = int(match.group(2))
            
            return {
                'total_requested': total_tokens,
                'max_limit': max_limit
            }
        
        return None
        
    except Exception as e:
        logger.warning(f"Error extracting token info: {e}")
        return None


def create_user_friendly_error_message(error_info: Dict) -> str:
    """
    Create a user-friendly error message based on parsed error information.
    
    Args:
        error_info: Parsed error information from parse_openrouter_error
        
    Returns:
        User-friendly error message with actionable guidance
    """
    provider_name = error_info.get('provider_name', 'AI Provider')
    error_type = error_info.get('error_type', '')
    error_message = error_info.get('error_message', '')
    
    if error_type == 'requested_too_many_tokens':
        token_info = extract_token_info(error_message)
        
        if token_info:
            max_limit = token_info.get('max_limit', 'unknown')
            requested = token_info.get('total_requested') or token_info.get('requested_tokens', 'unknown')
            prompt_length = token_info.get('prompt_length')
            
            message = f"❌ **Token Limit Exceeded**\n\n"
            message += f"**Provider:** {provider_name}\n"
            message += f"**Problem:** Your request requires {requested} tokens, but {provider_name} has a limit of {max_limit} tokens.\n\n"
            
            if prompt_length:
                message += f"**Breakdown:**\n"
                message += f"- Your prompt: {prompt_length} tokens\n"
                message += f"- Requested generation: {token_info.get('requested_tokens', 'unknown')} tokens\n"
                message += f"- Total needed: {requested} tokens\n"
                message += f"- Maximum allowed: {max_limit} tokens\n\n"
            
            message += f"**Solutions:**\n"
            message += f"1. **Reduce your topic scope** - Try focusing on a more specific aspect of your topic\n"
            message += f"2. **Reduce study time** - Try requesting fewer hours of content (this reduces the number of learning nodes generated)\n"
            message += f"3. **Split your topic** - Break your learning goal into smaller, separate research sessions\n"
            message += f"4. **Switch providers** - Try using OpenAI instead of OpenRouter if you have access\n\n"
            message += f"💡 **Tip:** For large topics, try starting with 2-3 hours instead of 5+ hours to stay within token limits."
            
            return message
        else:
            return f"❌ **Token Limit Exceeded**\n\n{provider_name} cannot process your request because it exceeds their token limit.\n\n**Solution:** Try making your topic more specific or requesting fewer hours of content."
    
    elif error_type == 'rate_limit_exceeded':
        return f"⏳ **Rate Limit Reached**\n\n{provider_name} is currently limiting requests.\n\n**Solution:** Please wait a few minutes and try again."
    
    elif error_type == 'insufficient_quota' or 'quota' in error_message.lower():
        return f"💳 **Quota Exceeded**\n\n{provider_name} reports that your account quota has been exceeded.\n\n**Solution:** Check your {provider_name} account billing and usage limits."
    
    elif error_type == 'invalid_api_key' or 'authentication' in error_message.lower():
        return f"🔑 **Authentication Failed**\n\n{provider_name} could not authenticate your request.\n\n**Solution:** Check that your API key is valid and properly configured."
    
    elif error_type == 'model_not_found' or 'model' in error_message.lower():
        return f"🤖 **Model Unavailable**\n\n{provider_name} reports that the requested model is not available.\n\n**Solution:** The model may be temporarily unavailable. Try again later or contact support."
    
    else:
        # Generic fallback with the actual provider error
        return f"❌ **{provider_name} Error**\n\n{error_message}\n\n**Error Type:** {error_type}\n\n**Suggestion:** If this error persists, try switching to a different provider or contact support."


def handle_api_error(response, context: str = "API call") -> Tuple[str, bool]:
    """
    Handle API errors and return user-friendly messages.
    
    Args:
        response: API response object
        context: Context for the error (e.g., "deep research", "topic clarification")
        
    Returns:
        Tuple of (error_message, is_retryable)
    """
    # First try to parse as OpenRouter error
    error_info = parse_openrouter_error(response)
    
    if error_info:
        user_message = create_user_friendly_error_message(error_info)
        
        # Determine if error is retryable
        error_type = error_info.get('error_type', '')
        is_retryable = error_type in ['rate_limit_exceeded', 'temporary_unavailable']
        
        logger.error(f"OpenRouter error in {context}: {error_info}")
        return user_message, is_retryable
    
    # Fallback for other error types
    if hasattr(response, 'error'):
        error = response.error
        if hasattr(error, 'message'):
            return f"❌ **Error in {context}**\n\n{error.message}", False
    
    return f"❌ **Unknown error in {context}**\n\nPlease try again or contact support.", False


def estimate_token_count(text: str) -> int:
    """
    Rough estimation of token count for text.
    Uses a simple heuristic: ~4 characters per token.
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # Simple heuristic: average of 4 characters per token
    # This is rough but good enough for limit checking
    return len(text) // 4


def check_token_limits(prompt: str, max_completion_tokens: int = None, model_max_tokens: int = 128000) -> Dict:
    """
    Check if a prompt would exceed token limits.
    
    Args:
        prompt: The input prompt text
        max_completion_tokens: Maximum tokens requested for completion
        model_max_tokens: Maximum total tokens for the model
        
    Returns:
        Dict with validation results
    """
    prompt_tokens = estimate_token_count(prompt)
    completion_tokens = max_completion_tokens or (model_max_tokens // 4)  # Default to 25% for completion
    total_tokens = prompt_tokens + completion_tokens
    
    return {
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens,
        'model_max_tokens': model_max_tokens,
        'within_limits': total_tokens <= model_max_tokens,
        'available_tokens': max(0, model_max_tokens - prompt_tokens),
        'recommended_max_completion': max(0, model_max_tokens - prompt_tokens - 1000)  # Leave buffer
    }