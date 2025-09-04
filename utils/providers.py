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
    
    # Check for cost-effective model override
    from utils.config import get_cost_effective_models_setting
    use_cost_effective = get_cost_effective_models_setting()
    
    # For chat task, check if cost-effective alternative exists and is enabled
    if task == "chat" and use_cost_effective:
        cost_effective_key = f"{task}_cost_effective"
        if cost_effective_key in config:
            return config[cost_effective_key]
    
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
    
    # Reject max_tokens parameter to ensure default token limits are used
    if 'max_tokens' in kwargs:
        raise ValueError("max_tokens parameter is not allowed. Let the AI provider use default token limits.")
    
    # Start with base parameters
    params = {
        "model": model,
        "messages": messages
    }
    
    # Add optional parameters if provided
    optional_params = {
        "temperature": temperature,
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
        Dictionary of available models by task (showing effective models based on settings)
    """
    if provider is None:
        provider = get_current_provider()
    
    config = get_provider_config(provider)
    
    # Get the effective models considering cost-effective setting
    from utils.config import get_cost_effective_models_setting
    use_cost_effective = get_cost_effective_models_setting()
    
    effective_models = {}
    for task, model in config.items():
        if task in ["base_url", "token_limits"]:
            continue
        if task.endswith("_cost_effective"):
            continue  # Skip the cost-effective variants in the listing
            
        # Use cost-effective model if available and enabled
        if task == "chat" and use_cost_effective:
            cost_effective_key = f"{task}_cost_effective"
            if cost_effective_key in config:
                effective_models[task] = config[cost_effective_key]
                continue
        
        effective_models[task] = model
    
    return effective_models


def is_diagram_capable_model(model: str) -> bool:
    """
    Check if a model is capable of generating quality diagrams.
    
    Args:
        model: Model name to check
        
    Returns:
        True if model supports good diagram generation, False otherwise
    """
    # High-capability models that support good diagram generation
    diagram_capable_models = {
        # OpenAI models
        "gpt-5", "gpt-4o", "gpt-4-turbo", "gpt-4",
        # Anthropic Claude models  
        "anthropic/claude-opus-4.1", "anthropic/claude-3.5-sonnet", "anthropic/claude-3-opus",
        # Other high-capability models
        "openai/o1", "openai/o1-preview"
    }
    
    # Lower capability models that may struggle with diagrams
    lower_capability_models = {
        "gpt-4o-mini", "gpt-3.5-turbo", "anthropic/claude-3.5-haiku", 
        "anthropic/claude-3-haiku", "gpt-3.5-turbo-instruct"
    }
    
    # Check exact match first
    if model in diagram_capable_models:
        return True
    if model in lower_capability_models:
        return False
    
    # Check partial match for versioned models
    for capable_model in diagram_capable_models:
        if model.startswith(capable_model + "-"):
            return True
    
    # Default to False for unknown models
    return False


def get_model_capability_warning(model: str) -> str:
    """
    Get warning message for models that may not handle diagrams well.
    
    Args:
        model: Model name to check
        
    Returns:
        Warning message if model has limited diagram capabilities, empty string otherwise
    """
    if not is_diagram_capable_model(model):
        return (
            f"⚠️ **Warning**: The model '{model}' may have limited capabilities for generating "
            f"interactive diagrams and complex mathematical visualizations. For best results with "
            f"STEM subjects, consider using a more capable model like GPT-5 or Claude Opus 4.1."
        )
    return ""