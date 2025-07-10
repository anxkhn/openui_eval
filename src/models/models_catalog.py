"""
Models catalog defining available models from different providers.
This catalog serves as a registry of all supported models with their provider-specific configurations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ModelProvider(Enum):
    """Supported model providers."""

    OLLAMA = "ollama"
    GOOGLE_GENAI = "google_genai"
    OPENAI = "openai"


@dataclass
class ModelDefinition:
    """Definition of a model with provider-specific settings."""

    name: str
    provider: ModelProvider
    display_name: str
    description: str
    supports_vision: bool = False
    supports_function_calling: bool = False
    context_length: int = 32768

    default_temperature: float = 0.1
    default_timeout: int = 300
    default_max_retries: int = 3

    ollama_model_name: Optional[str] = None

    google_model_name: Optional[str] = None
    requires_vertex_ai: bool = False

    openai_model_name: Optional[str] = None


MODEL_CATALOG: Dict[str, ModelDefinition] = {
    "gemma3n:e2b": ModelDefinition(
        name="gemma3n:e2b",
        provider=ModelProvider.OLLAMA,
        display_name="Gemma 3N 2B",
        description="Google's Gemma 3 Nano model with enhanced capabilities",
        supports_vision=True,
        context_length=32768,
    ),
    "gemma3:4b": ModelDefinition(
        name="gemma3:4b",
        provider=ModelProvider.OLLAMA,
        display_name="Gemma 3 4B",
        description="Google's Gemma 3 model with 4B parameters",
        supports_vision=True,
        context_length=32768,
    ),
    "qwen2.5vl:7b": ModelDefinition(
        name="qwen2.5vl:7b",
        provider=ModelProvider.OLLAMA,
        display_name="Qwen 2.5 VL 7B",
        description="Alibaba's Qwen 2.5 vision-language model with 7B parameters",
        supports_vision=True,
        context_length=32768,
    ),
    "granite3.2-vision:2b": ModelDefinition(
        name="granite3.2-vision:2b",
        provider=ModelProvider.OLLAMA,
        display_name="Granite 3.2 Vision 2B",
        description="IBM's Granite 3.2 vision model with 2B parameters",
        supports_vision=True,
        context_length=32768,
    ),
    "llama3.2-vision:11b": ModelDefinition(
        name="llama3.2-vision:11b",
        provider=ModelProvider.OLLAMA,
        display_name="LLaMA 3.2 Vision 11B",
        description="Meta's LLaMA 3.2 vision model with 11B parameters",
        supports_vision=True,
        context_length=32768,
    ),
    "minicpm-v:8b": ModelDefinition(
        name="minicpm-v:8b",
        provider=ModelProvider.OLLAMA,
        display_name="MiniCPM-V 8B",
        description="OpenBMB's MiniCPM vision model with 8B parameters",
        supports_vision=True,
        context_length=32768,
    ),
    "llava-phi3:3.8b": ModelDefinition(
        name="llava-phi3:3.8b",
        provider=ModelProvider.OLLAMA,
        display_name="LLaVA Phi3 3.8B",
        description="LLaVA model based on Phi3 with 3.8B parameters",
        supports_vision=True,
        context_length=32768,
    ),
    "gemini-2.5-pro": ModelDefinition(
        name="gemini-2.5-pro",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 2.5 Pro",
        description="Enhanced thinking and reasoning, multimodal understanding, advanced coding",
        supports_vision=True,
        supports_function_calling=True,
        context_length=2000000,
        google_model_name="gemini-2.5-pro",
    ),
    "gemini-2.5-flash": ModelDefinition(
        name="gemini-2.5-flash",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 2.5 Flash",
        description="Adaptive thinking, cost efficiency with multimodal support",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-2.5-flash",
    ),
    "gemini-2.5-flash-lite-preview-06-17": ModelDefinition(
        name="gemini-2.5-flash-lite-preview-06-17",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 2.5 Flash-Lite Preview",
        description="Most cost-efficient model supporting high throughput",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-2.5-flash-lite-preview-06-17",
    ),
    "gemini-2.0-flash": ModelDefinition(
        name="gemini-2.0-flash",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 2.0 Flash",
        description="Next generation features, speed, and realtime streaming",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-2.0-flash",
    ),
    "gemini-2.0-flash-preview-image-generation": ModelDefinition(
        name="gemini-2.0-flash-preview-image-generation",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 2.0 Flash Preview Image Generation",
        description="Conversational image generation and editing",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-2.0-flash-preview-image-generation",
    ),
    "gemini-2.0-flash-lite": ModelDefinition(
        name="gemini-2.0-flash-lite",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 2.0 Flash-Lite",
        description="Cost efficiency and low latency",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-2.0-flash-lite",
    ),
    "gemini-1.5-flash": ModelDefinition(
        name="gemini-1.5-flash",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 1.5 Flash",
        description="Fast and versatile performance across a diverse variety of tasks",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-1.5-flash",
    ),
    "gemini-1.5-flash-8b": ModelDefinition(
        name="gemini-1.5-flash-8b",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 1.5 Flash-8B (Deprecated)",
        description="High volume and lower intelligence tasks (deprecated)",
        supports_vision=True,
        supports_function_calling=True,
        context_length=1000000,
        google_model_name="gemini-1.5-flash-8b",
    ),
    "gemini-1.5-pro": ModelDefinition(
        name="gemini-1.5-pro",
        provider=ModelProvider.GOOGLE_GENAI,
        display_name="Gemini 1.5 Pro (Deprecated)",
        description="Complex reasoning tasks requiring more intelligence (deprecated)",
        supports_vision=True,
        supports_function_calling=True,
        context_length=2000000,
        google_model_name="gemini-1.5-pro",
    ),
}


def get_model_definition(model_name: str) -> Optional[ModelDefinition]:
    """Get model definition by name."""
    return MODEL_CATALOG.get(model_name)


def get_models_by_provider(provider: ModelProvider) -> List[ModelDefinition]:
    """Get all models for a specific provider."""
    return [model for model in MODEL_CATALOG.values() if model.provider == provider]


def get_vision_models() -> List[ModelDefinition]:
    """Get all models that support vision."""
    return [model for model in MODEL_CATALOG.values() if model.supports_vision]


def get_all_model_names() -> List[str]:
    """Get names of all available models."""
    return list(MODEL_CATALOG.keys())


def is_model_available(model_name: str) -> bool:
    """Check if a model is available in the catalog."""
    return model_name in MODEL_CATALOG


def get_provider_for_model(model_name: str) -> Optional[ModelProvider]:
    """Get the provider for a specific model."""
    model_def = get_model_definition(model_name)
    return model_def.provider if model_def else None


def get_ollama_models() -> List[str]:
    """Get list of Ollama model names."""
    return [model.name for model in get_models_by_provider(ModelProvider.OLLAMA)]


def get_google_genai_models() -> List[str]:
    """Get list of Google GenAI model names."""
    return [model.name for model in get_models_by_provider(ModelProvider.GOOGLE_GENAI)]


def get_model_display_info() -> Dict[str, Dict[str, str]]:
    """Get display information for all models (for CLI help)."""
    info = {}
    for provider in ModelProvider:
        provider_models = get_models_by_provider(provider)
        if provider_models:
            info[provider.value] = {
                model.name: f"{model.display_name} - {model.description}"
                for model in provider_models
            }
    return info
