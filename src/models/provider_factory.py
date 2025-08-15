"""Provider factory for creating LLM providers."""

import os
from typing import Dict, Any


from .base_provider import LLMProvider
from .ollama_provider import OllamaProvider
from .vllm_provider import vLLMProvider
from .openrouter_provider import OpenRouterProvider


def create_provider(provider_type: str, config: Dict[str, Any] = None) -> LLMProvider:
    """
    Create a provider instance based on the provider type and configuration.
    
    Args:
        provider_type: Type of provider ("ollama", "vllm", "openrouter")
        config: Configuration dictionary for the provider
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider type is invalid or configuration is missing
    """
    if config is None:
        config = {}
    
    provider_type = provider_type.lower()
    
    if provider_type == "ollama":
        return OllamaProvider(
            host=config.get("host", "http://localhost:11434"),
            **{k: v for k, v in config.items() if k != "host"}
        )
    
    elif provider_type == "vllm":
        return vLLMProvider(
            url=config.get("url", "http://localhost:8000/v1/completions"),
            model_name=config.get("model_name", "meta-llama/Meta-Llama-3-8B-Instruct"),
            **{k: v for k, v in config.items() if k not in ["url", "model_name"]}
        )
    
    elif provider_type == "openrouter":
        api_key = config.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable "
                "or provide it in the configuration."
            )
        
        return OpenRouterProvider(
            api_key=api_key,
            url=config.get("url", "https://openrouter.ai/api/v1/chat/completions"),
            default_model=config.get("default_model", "meta-llama/llama-3.1-8b-instruct:free"),
            requests_per_minute=config.get("requests_per_minute", 20),
            **{k: v for k, v in config.items() if k not in [
                "api_key", "url", "default_model", "requests_per_minute"
            ]}
        )
    
    else:
        raise ConfigurationError(
            f"Unknown provider type: {provider_type}. "
            f"Supported providers: ollama, vllm, openrouter"
        )


def get_available_providers() -> Dict[str, bool]:
    """
    Check which providers are available and properly configured.
    
    Returns:
        Dictionary mapping provider names to availability status
    """
    providers = {}
    
    # Check Ollama
    try:
        ollama_provider = create_provider("ollama")
        providers["ollama"] = ollama_provider.is_available()
    except Exception:
        providers["ollama"] = False
    
    # Check vLLM
    try:
        vllm_provider = create_provider("vllm")
        providers["vllm"] = vllm_provider.is_available()
    except Exception:
        providers["vllm"] = False
    
    # Check OpenRouter
    try:
        openrouter_provider = create_provider("openrouter")
        providers["openrouter"] = openrouter_provider.is_available()
    except Exception:
        providers["openrouter"] = False
    
    return providers


def get_default_provider_config(provider_type: str) -> Dict[str, Any]:
    """
    Get default configuration for a provider type.
    
    Args:
        provider_type: Type of provider
        
    Returns:
        Default configuration dictionary
    """
    provider_type = provider_type.lower()
    
    if provider_type == "ollama":
        return {
            "host": "http://localhost:11434",
            "timeout": 300,
            "models": [
                "gemma3n:e2b",
                "gemma3:4b", 
                "qwen2.5vl:7b",
                "granite3.2-vision:2b",
                "llama3.2-vision:11b",
                "minicpm-v:8b",
                "llava-phi3:3.8b"
            ]
        }
    
    elif provider_type == "vllm":
        return {
            "url": "http://localhost:8000/v1/completions",
            "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
            "timeout": 300,
        }
    
    elif provider_type == "openrouter":
        return {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "default_model": "meta-llama/llama-3.1-8b-instruct:free",
            "requests_per_minute": 20,
            "timeout": 300,
        }
    
    else:
        raise ConfigurationError(f"Unknown provider type: {provider_type}")


# Backward compatibility function similar to leetcode-compensation's get_model_predict
def get_provider_client(provider_type: str, config: Dict[str, Any] = None) -> LLMProvider:
    """
    Get a provider client instance.
    
    This function provides backward compatibility and follows the pattern from 
    leetcode-compensation's get_model_predict function.
    
    Args:
        provider_type: Type of provider ("ollama", "vllm", "openrouter")
        config: Configuration dictionary for the provider
        
    Returns:
        LLMProvider instance
    """
    return create_provider(provider_type, config)
