"""
Provider abstraction for different AI providers
Supports OpenAI and OpenRouter APIs
"""

from openai import OpenAI
from typing import Dict, Optional
from utils.config import (
    load_api_key, get_current_provider, get_provider_config, 
    SUPPORTED_PROVIDERS, APP_NAME, APP_URL
)


class ProviderError(Exception):
    """Base exception for provider-related errors"""
    pass


def create_client(provider: str = None, **kwargs) -> OpenAI:
    """
    Create an API client for the specified provider.
    OpenRouter is compatible with OpenAI's API, so we can use the same client.
    
    Args:
        provider: Provider name ("openai" or "openrouter"). If None, uses current provider.
        **kwargs: Additional parameters passed to the OpenAI client constructor
        
    Returns:
        OpenAI client configured for the specified provider
        
    Raises:
        ProviderError: If provider is not supported or API key is missing
    """
    if provider is None:
        provider = get_current_provider()
    
    if provider not in SUPPORTED_PROVIDERS:
        raise ProviderError(f"Unsupported provider: {provider}. Supported: {SUPPORTED_PROVIDERS}")
    
    # Get API key for the provider
    api_key = load_api_key(provider)
    if not api_key:
        raise ProviderError(f"No API key found for provider: {provider}")
    
    # Get provider configuration
    config = get_provider_config(provider)
    
    # Create client with appropriate base URL
    client_kwargs = {"api_key": api_key}
    if config.get("base_url"):
        client_kwargs["base_url"] = config["base_url"]
    
    # Add app attribution headers for OpenRouter
    if provider == "openrouter":
        default_headers = {
            "HTTP-Referer": APP_URL,
            "X-Title": APP_NAME,
        }
        client_kwargs["default_headers"] = default_headers
    
    # Merge any additional kwargs passed by caller
    client_kwargs.update(kwargs)
    
    return OpenAI(**client_kwargs)


def get_model_for_task(task: str, provider: str = None) -> str:
    """
    Get the appropriate model for a specific task.
    
    Args:
        task: Task type ("deep_research", "chat", etc.)
        provider: Provider name. If None, uses current provider.
        
    Returns:
        Model name for the specified task
        
    Raises:
        ProviderError: If task is not supported for the provider
    """
    if provider is None:
        provider = get_current_provider()
    
    config = get_provider_config(provider)
    
    if task not in config:
        raise ProviderError(f"Task '{task}' not supported for provider '{provider}'")
    
    return config[task]


def validate_api_key(api_key: str, provider: str) -> bool:
    """
    Validate an API key for a specific provider.
    
    Args:
        api_key: The API key to validate
        provider: Provider name
        
    Returns:
        True if API key is valid, False otherwise
    """
    try:
        config = get_provider_config(provider)
        
        # Create test client with same configuration as create_client
        client_kwargs = {"api_key": api_key}
        if config.get("base_url"):
            client_kwargs["base_url"] = config["base_url"]
        
        # Add app attribution headers for OpenRouter
        if provider == "openrouter":
            default_headers = {
                "HTTP-Referer": APP_URL,
                "X-Title": APP_NAME,
            }
            client_kwargs["default_headers"] = default_headers
        
        test_client = OpenAI(**client_kwargs)
        
        # Test with a simple API call
        test_client.models.list()
        return True
        
    except Exception:
        return False


def get_provider_info(provider: str) -> Dict:
    """
    Get information about a specific provider.
    
    Args:
        provider: Provider name
        
    Returns:
        Dictionary with provider information
    """
    provider_info = {
        "openai": {
            "name": "OpenAI",
            "description": "Official OpenAI API with access to GPT models and deep research",
            "api_key_prefix": "sk-",
            "signup_url": "https://platform.openai.com/api-keys",
            "pricing_url": "https://openai.com/pricing",
            "supports_deep_research": True,
            "supports_web_search": True,
        },
        "openrouter": {
            "name": "OpenRouter",
            "description": "Access to multiple AI models including Claude, Gemini, and Perplexity Sonar Deep Research",
            "api_key_prefix": "sk-or-",
            "signup_url": "https://openrouter.ai/keys",
            "pricing_url": "https://openrouter.ai/models",
            "supports_deep_research": True,   # Now supports via Perplexity Sonar Deep Research
            "supports_web_search": True,     # Via Perplexity models
        }
    }
    
    return provider_info.get(provider, {})


def get_api_call_params(
    model: str,
    messages: list,
    provider: str = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    repetition_penalty: Optional[float] = None,
    min_p: Optional[float] = None,
    top_a: Optional[float] = None,
    seed: Optional[int] = None,
    logit_bias: Optional[Dict] = None,
    logprobs: Optional[bool] = None,
    top_logprobs: Optional[int] = None,
    response_format: Optional[Dict] = None,
    stop: Optional[list] = None,
    tools: Optional[list] = None,
    tool_choice: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Build API call parameters with optional OpenRouter-specific parameters.
    
    Args:
        model: Model name to use
        messages: List of messages for the conversation
        provider: Provider name. If None, uses current provider.
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter (0.0 to 1.0)
        top_k: Top-k sampling parameter 
        frequency_penalty: Frequency penalty (-2.0 to 2.0)
        presence_penalty: Presence penalty (-2.0 to 2.0)
        repetition_penalty: Repetition penalty (0.0 to 2.0)
        min_p: Minimum probability threshold (0.0 to 1.0)
        top_a: Top-a sampling parameter (0.0 to 1.0)
        seed: Random seed for deterministic sampling
        logit_bias: Token bias map
        logprobs: Whether to return log probabilities
        top_logprobs: Number of top log probabilities to return
        response_format: Output format specification
        stop: Stop sequences
        tools: Tool definitions for function calling
        tool_choice: Tool choice strategy
        **kwargs: Additional parameters
        
    Returns:
        Dictionary of API call parameters
    """
    if provider is None:
        provider = get_current_provider()
    
    # Start with base parameters
    params = {
        "model": model,
        "messages": messages
    }
    
    # Add optional parameters if provided
    optional_params = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "seed": seed,
        "logit_bias": logit_bias,
        "logprobs": logprobs,
        "top_logprobs": top_logprobs,
        "response_format": response_format,
        "stop": stop,
        "tools": tools,
        "tool_choice": tool_choice,
    }
    
    # Add OpenRouter-specific parameters if using OpenRouter
    if provider == "openrouter":
        openrouter_params = {
            "top_k": top_k,
            "repetition_penalty": repetition_penalty,
            "min_p": min_p,
            "top_a": top_a,
        }
        optional_params.update(openrouter_params)
    
    # Only include parameters that have values
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    
    # Add any additional kwargs
    params.update(kwargs)
    
    return params


def get_model_token_limit(model: str, provider: str = None) -> int:
    """
    Get the token limit for a specific model.
    
    Args:
        model: Model name
        provider: Provider name. If None, uses current provider.
        
    Returns:
        Token limit for the model, defaults to 128000 if not found
    """
    if provider is None:
        provider = get_current_provider()
    
    config = get_provider_config(provider)
    token_limits = config.get("token_limits", {})
    
    return token_limits.get(model, 102400)  # Default to 80% of 128k tokens (conservative)


def list_available_models(provider: str = None) -> Dict:
    """
    Get list of available models for a provider.
    
    Args:
        provider: Provider name. If None, uses current provider.
        
    Returns:
        Dictionary of available models by task
    """
    if provider is None:
        provider = get_current_provider()
    
    config = get_provider_config(provider)
    return {task: model for task, model in config.items() if task != "base_url"}