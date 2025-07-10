"""Base provider interface for LLM providers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, **kwargs):
        """Initialize the provider with configuration."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider."""
        pass

    @abstractmethod
    def generate(
        self,
        model_name: str,
        prompt: str,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        num_ctx: int = 32768,
        num_predict: int = -1,
        format_schema: Optional[BaseModel] = None,
        use_conversation_history: bool = False,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Generate response from model.
        
        Args:
            model_name: Name of the model to use
            prompt: Text prompt
            image_path: Optional path to image file
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            num_ctx: Context window size
            num_predict: Max tokens to predict (-1 for unlimited)
            format_schema: Optional Pydantic model for structured output
            use_conversation_history: Whether to use conversation history
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with response data including:
            - content: Generated text
            - model: Model name
            - duration: Generation duration
            - Additional provider-specific metadata
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        model_name: str,
        prompt: str,
        response_model: BaseModel,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Generate structured response using Pydantic model."""
        pass

    @abstractmethod
    def clear_conversation_history(self, model_name: Optional[str] = None):
        """Clear conversation history for a model or all models."""
        pass

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        return {"name": model_name, "provider": self.__class__.__name__}

    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a model is available, downloading if necessary."""
        return model_name in self.list_models()
