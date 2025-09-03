"""
Error handling utilities for Autodidact
Provides enhanced error parsing and user-friendly error messages
"""

import json
import re
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def _filter_sensitive_env_vars(env_vars: Dict[str, str]) -> Dict[str, str]:
    """
    Filter out sensitive environment variables from logging.
    
    Args:
        env_vars: Dictionary of environment variables
        
    Returns:
        Filtered dictionary with sensitive values removed
    """
    from utils.config import MAX_ENV_VAR_LENGTH
    
    # Define patterns for sensitive environment variables
    sensitive_patterns = [
        '_KEY', '_SECRET', '_TOKEN', '_PASSWORD', '_PASS',
        '_CREDENTIAL', '_AUTH', '_PRIVATE', '_CERT', '_SIGNATURE'
    ]
    
    # Define allowed prefixes for debugging
    allowed_prefixes = ('AUTODIDACT_', 'OPENAI_', 'OPENROUTER_')
    
    filtered = {}
    for key, value in env_vars.items():
        # Only include variables with allowed prefixes
        if key.startswith(allowed_prefixes):
            # Check if the key contains sensitive patterns
            is_sensitive = any(pattern in key.upper() for pattern in sensitive_patterns)
            if is_sensitive:
                filtered[key] = "[REDACTED]"
            else:
                # Still limit the value length for safety
                filtered[key] = value[:MAX_ENV_VAR_LENGTH] if len(value) > MAX_ENV_VAR_LENGTH else value
    
    return filtered


def create_incident_file(error_details: Dict, context: str, additional_info: Dict = None) -> str:
    """
    Create an incident file for major errors with unique identifier.
    
    Args:
        error_details: Dict with extracted error information
        context: Context where the error occurred
        additional_info: Additional debugging information
        
    Returns:
        Path to the created incident file
    """
    from utils.config import CONFIG_DIR, ensure_config_directory, INCIDENT_FILE_PERMISSIONS
    
    ensure_config_directory()
    
    # Create incident file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    incident_file = CONFIG_DIR / f"incident-{timestamp}.log"
    
    # Collect comprehensive incident information
    incident_data = {
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "error_details": error_details,
        "additional_info": additional_info or {},
        "system_info": {
            "python_version": f"{os.sys.version}",
            "platform": f"{os.name}",
            "working_directory": str(Path.cwd()),
            "environment_vars": _filter_sensitive_env_vars(dict(os.environ))
        }
    }
    
    # Write incident file with both JSON and human-readable format
    try:
        with open(incident_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"AUTODIDACT INCIDENT REPORT - {timestamp}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"INCIDENT TIME: {incident_data['timestamp']}\n")
            f.write(f"CONTEXT: {context}\n\n")
            
            f.write("ERROR DETAILS:\n")
            f.write("-" * 40 + "\n")
            for key, value in error_details.items():
                f.write(f"{key.upper()}: {value}\n")
            f.write("\n")
            
            if additional_info:
                f.write("ADDITIONAL INFORMATION:\n")
                f.write("-" * 40 + "\n")
                for key, value in additional_info.items():
                    f.write(f"{key.upper()}: {value}\n")
                f.write("\n")
            
            f.write("SYSTEM INFORMATION:\n")
            f.write("-" * 40 + "\n")
            for key, value in incident_data['system_info'].items():
                if isinstance(value, dict):
                    f.write(f"{key.upper()}:\n")
                    for subkey, subvalue in value.items():
                        f.write(f"  {subkey}: {subvalue}\n")
                else:
                    f.write(f"{key.upper()}: {value}\n")
            f.write("\n")
            
            f.write("FULL JSON DATA:\n")
            f.write("-" * 40 + "\n")
            f.write(json.dumps(incident_data, indent=2, default=str))
        
        # Set secure file permissions (readable only by owner)
        incident_file.chmod(INCIDENT_FILE_PERMISSIONS)
        
        logger.error(f"Incident file created: {incident_file}")
        return str(incident_file)
        
    except Exception as e:
        logger.error(f"Failed to create incident file: {e}")
        return None


def log_major_error(error_obj, context: str, additional_info: Dict = None) -> Tuple[str, bool, str]:
    """
    Log a major error and create an incident file.
    
    Args:
        error_obj: Error object or exception
        context: Context where the error occurred
        additional_info: Additional debugging information
        
    Returns:
        Tuple of (error_message, is_retryable, incident_file_path)
    """
    # Extract detailed error information
    error_details = extract_error_details(error_obj)
    
    # Create incident file for major errors
    incident_file = create_incident_file(error_details, context, additional_info)
    
    # Create enhanced error message
    error_message, is_retryable = create_enhanced_error_message(error_details, context)
    
    # Log to main logger
    logger.error(f"Major error in {context}: {error_details.get('message', 'Unknown error')}")
    if incident_file:
        logger.error(f"Incident report saved to: {incident_file}")
    
    return error_message, is_retryable, incident_file


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
        error_data = _get_error_data(response)
        if not error_data:
            return None
        
        # Extract OpenRouter error structure
        error_dict = _convert_to_dict(error_data)
        if not error_dict:
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
        return _parse_raw_error(raw_error, provider_name, error_dict)
            
    except Exception as e:
        logger.warning(f"Error parsing OpenRouter response: {e}")
        return None


def _get_error_data(response):
    """Extract error data from response object or dict."""
    if hasattr(response, '__dict__'):
        return getattr(response, 'error', None)
    elif isinstance(response, dict):
        return response.get('error')
    else:
        return None


def _convert_to_dict(error_data):
    """Convert error data to dictionary format."""
    if hasattr(error_data, '__dict__'):
        return error_data.__dict__
    elif isinstance(error_data, dict):
        return error_data
    else:
        return None


def _parse_raw_error(raw_error: str, provider_name: str, error_dict: Dict) -> Dict:
    """Parse raw error JSON from OpenRouter response."""
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


def _extract_basic_error_info(error_obj) -> Dict:
    """Extract basic error information from an error object."""
    info = {}
    
    # Try to get error message from various sources
    if hasattr(error_obj, 'message') and error_obj.message:
        info['message'] = str(error_obj.message)
    elif hasattr(error_obj, '__str__'):
        error_str = str(error_obj)
        if error_str and error_str != repr(error_obj):
            info['message'] = error_str
    
    # Extract status/error codes
    if hasattr(error_obj, 'status_code'):
        info['status_code'] = error_obj.status_code
    elif hasattr(error_obj, 'code'):
        info['code'] = error_obj.code
        
    # Extract error type
    if hasattr(error_obj, 'type'):
        info['type'] = error_obj.type
    elif hasattr(error_obj, '__class__'):
        info['type'] = error_obj.__class__.__name__
        
    # Extract request ID for debugging
    if hasattr(error_obj, 'request_id'):
        info['request_id'] = error_obj.request_id
        
    return info


def _extract_response_body_info(error_obj) -> Dict:
    """Extract information from error response body."""
    info = {}
    
    # Extract body/response content
    if hasattr(error_obj, 'body') and error_obj.body:
        info['body'] = error_obj.body
        # Try to parse JSON body for additional error information
        if isinstance(error_obj.body, str):
            try:
                body_data = json.loads(error_obj.body)
                if isinstance(body_data, dict) and 'error' in body_data:
                    error_data = body_data['error']
                    if isinstance(error_data, dict):
                        # Extract additional error details from body
                        info.update({
                            'body_message': error_data.get('message'),
                            'body_type': error_data.get('type'),
                            'body_code': error_data.get('code')
                        })
            except json.JSONDecodeError:
                pass
    elif hasattr(error_obj, 'response') and hasattr(error_obj.response, 'text'):
        info['body'] = error_obj.response.text
        
    return info


def _extract_openai_error_info(error_obj) -> Dict:
    """Extract specific information from OpenAI API errors."""
    info = {}
    
    # For openai.APIError specifically, try to extract more details
    if hasattr(error_obj, '__dict__'):
        error_dict = error_obj.__dict__
        if 'response' in error_dict:
            response = error_dict['response']
            if hasattr(response, 'status_code'):
                info['status_code'] = response.status_code
            if hasattr(response, 'json'):
                try:
                    response_json = response.json()
                    if isinstance(response_json, dict) and 'error' in response_json:
                        error_data = response_json['error']
                        if isinstance(error_data, dict):
                            info.update({
                                'api_message': error_data.get('message'),
                                'api_type': error_data.get('type'),
                                'api_code': error_data.get('code')
                            })
                except:
                    pass
                    
    return info


def extract_error_details(error_obj) -> Dict:
    """
    Extract error details from various error object types.
    
    Args:
        error_obj: Error object or exception
        
    Returns:
        Dict with extracted error information
    """
    details = {
        'message': None,
        'type': None,
        'code': None,
        'status_code': None,
        'request_id': None,
        'body': None
    }
    
    try:
        # Extract basic information
        basic_info = _extract_basic_error_info(error_obj)
        details.update(basic_info)
        
        # Extract response body information
        body_info = _extract_response_body_info(error_obj)
        details.update(body_info)
        
        # Extract OpenAI-specific information
        openai_info = _extract_openai_error_info(error_obj)
        details.update(openai_info)
        
        # Use body/API info to fill in missing details (prioritize original values)
        details['message'] = (details['message'] or 
                            details.get('body_message') or 
                            details.get('api_message'))
        details['type'] = (details['type'] or 
                         details.get('body_type') or 
                         details.get('api_type'))
        details['code'] = (details['code'] or 
                         details.get('body_code') or 
                         details.get('api_code'))
        
        # Clean up temporary fields
        for key in ['body_message', 'body_type', 'body_code', 'api_message', 'api_type', 'api_code']:
            details.pop(key, None)
                        
    except Exception as e:
        logger.warning(f"Error extracting error details: {e}")
    
    return details


def create_enhanced_error_message(error_details: Dict, context: str) -> Tuple[str, bool]:
    """
    Create an enhanced error message based on extracted error details.
    
    Args:
        error_details: Dict with extracted error information
        context: Context for the error
        
    Returns:
        Tuple of (error_message, is_retryable)
    """
    message = str(error_details.get('message', '')).strip()
    error_type = str(error_details.get('type', '')).lower()
    status_code = error_details.get('status_code')
    code = error_details.get('code')
    
    # Determine if error is retryable based on status codes and error types
    retryable_conditions = [
        status_code in [429, 503, 502, 504],  # Rate limit, service unavailable, bad gateway, timeout
        'rate_limit' in error_type,
        'timeout' in error_type,
        'temporarily_unavailable' in error_type,
        'service_unavailable' in error_type,
        'rate_limit_exceeded' in error_type
    ]
    is_retryable = any(retryable_conditions)
    
    # Create user-friendly message based on status code and error type
    if status_code == 401 or 'authentication' in error_type or 'unauthorized' in error_type:
        error_msg = f"🔑 **Authentication Failed**\n\n"
        error_msg += f"Your API key appears to be invalid or expired.\n\n"
        error_msg += f"**Solution:** Check your API key configuration in settings.\n\n"
        if message:
            error_msg += f"**Details:** {message}"
        return error_msg, False
        
    elif status_code == 403 or 'permission' in error_type or 'forbidden' in error_type:
        error_msg = f"🚫 **Permission Denied**\n\n"
        error_msg += f"Your API key doesn't have access to the requested resource.\n\n"
        error_msg += f"**Solution:** Check your API key permissions or upgrade your plan.\n\n"
        if message:
            error_msg += f"**Details:** {message}"
        return error_msg, False
        
    elif status_code == 429 or 'rate_limit' in error_type:
        error_msg = f"⏳ **Rate Limit Exceeded**\n\n"
        error_msg += f"Too many requests have been made recently.\n\n"
        error_msg += f"**Solution:** Wait a few minutes and try again.\n\n"
        if message:
            error_msg += f"**Details:** {message}"
        return error_msg, True
        
    elif status_code == 404 or 'not_found' in error_type:
        error_msg = f"🔍 **Resource Not Found**\n\n"
        error_msg += f"The requested model or endpoint is not available.\n\n"
        error_msg += f"**Solution:** Check your provider settings or try a different model.\n\n"
        if message:
            error_msg += f"**Details:** {message}"
        return error_msg, False
        
    elif status_code in [500, 502, 503, 504] or 'server_error' in error_type:
        error_msg = f"🔧 **Server Error**\n\n"
        error_msg += f"The AI provider is experiencing technical difficulties.\n\n"
        error_msg += f"**Solution:** Wait a few minutes and try again. If the problem persists, try switching providers.\n\n"
        if message:
            error_msg += f"**Details:** {message}"
        return error_msg, True
        
    elif 'timeout' in error_type or 'timeout' in message.lower():
        error_msg = f"⏱️ **Request Timeout**\n\n"
        error_msg += f"The request took too long to complete.\n\n"
        error_msg += f"**Solution:** Try again, or reduce the complexity of your request.\n\n"
        if message:
            error_msg += f"**Details:** {message}"
        return error_msg, True
        
    # Generic fallback with extracted information
    error_msg = f"❌ **Error in {context}**\n\n"
    
    if message:
        error_msg += f"**Error Message:** {message}\n\n"
    else:
        error_msg += f"An unexpected error occurred during {context}.\n\n"
    
    # Add technical details if available
    technical_details = []
    if error_type and error_type not in ['', 'none', 'nonetype']:
        technical_details.append(f"Type: {error_type}")
    if status_code:
        technical_details.append(f"Status: {status_code}")
    if code:
        technical_details.append(f"Code: {code}")
        
    if technical_details:
        error_msg += f"**Technical Details:** {', '.join(technical_details)}\n\n"
    
    # Add actionable suggestions
    error_msg += f"**Suggestions:**\n"
    error_msg += f"1. Wait a moment and try again\n"
    error_msg += f"2. Check your internet connection\n"
    error_msg += f"3. Verify your API key configuration\n"
    
    if is_retryable:
        error_msg += f"4. This error may be temporary - please retry in a few minutes\n"
    else:
        error_msg += f"4. Try switching to a different AI provider\n"
    
    return error_msg, is_retryable


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
        
        # For major errors, create incident file
        if error_type in ['requested_too_many_tokens', 'insufficient_quota', 'model_not_found']:
            additional_info = {"openrouter_error_info": error_info}
            _, _, incident_file = log_major_error(response, context, additional_info)
            if incident_file:
                user_message += f"\n\n📋 **Incident Report:** {incident_file}"
        else:
            logger.error(f"OpenRouter error in {context}: {error_info}")
        
        return user_message, is_retryable
    
    # Enhanced fallback: Extract detailed error information
    error_details = extract_error_details(response)
    
    # For unknown errors, create incident file
    additional_info = {"response_type": type(response).__name__}
    enhanced_message, is_retryable, incident_file = log_major_error(response, context, additional_info)
    
    if incident_file:
        enhanced_message += f"\n\n📋 **Incident Report:** {incident_file}"
    
    return enhanced_message, is_retryable


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


def check_token_limits(prompt: str, max_completion_tokens: int = None, model_max_tokens: int = 102400) -> Dict:
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
    
    # Calculate a reasonable recommended completion limit (cap at 8k tokens to prevent excessive requests)
    available_tokens = max(0, model_max_tokens - prompt_tokens)
    recommended_max_completion = min(8000, max(0, available_tokens - 1000))  # Cap at 8k tokens, leave 1k buffer
    
    return {
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens,
        'model_max_tokens': model_max_tokens,
        'within_limits': total_tokens <= model_max_tokens,
        'available_tokens': available_tokens,
        'recommended_max_completion': recommended_max_completion
    }