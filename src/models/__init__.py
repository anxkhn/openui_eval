"""Model management and interaction modules."""

from .model_manager import ModelManager
from .ollama_client import OllamaClient
from .google_genai_client import GoogleGenAIClient
from .models_catalog import MODEL_CATALOG, ModelProvider, get_model_definition

__all__ = [
    "ModelManager",
    "OllamaClient",
    "GoogleGenAIClient",
    "MODEL_CATALOG",
    "ModelProvider",
    "get_model_definition",
]
