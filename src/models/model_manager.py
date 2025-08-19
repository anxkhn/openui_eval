"""Model manager for handling multiple models with memory management."""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from ..core.config import Config, ModelConfig

from ..core.logger import get_logger
from .base_provider import LLMProvider
from .provider_factory import create_provider


@dataclass
class ModelState:
    """Track the state of a model."""

    name: str
    loaded: bool = False
    last_used: float = 0.0
    memory_usage_mb: float = 0.0
    load_time: float = 0.0
    total_calls: int = 0
    total_duration: float = 0.0
    error_count: int = 0


class ModelManager:
    """Manages multiple models with memory optimization and lifecycle management."""

    def __init__(
        self,
        config: Config,
        models: Optional[List[ModelConfig]] = None,
        memory_threshold: Optional[float] = None,
        max_concurrent_models: Optional[int] = None,
    ):
        # Use config models if not provided directly
        self.models = {model.name: model for model in (models or config.models)}
        self.memory_threshold = memory_threshold or config.memory_threshold
        self.max_concurrent_models = (
            max_concurrent_models or config.max_concurrent_models
        )
        self.logger = get_logger()

        # Create provider based on config
        provider_config = {
            "host": config.provider.ollama_host,
            "url": config.provider.vllm_url,
            "model_name": config.provider.vllm_model,
            "api_key": config.provider.openrouter_api_key,
            "default_model": config.provider.openrouter_model,
            "requests_per_minute": config.provider.openrouter_requests_per_minute,
            "timeout": config.provider.timeout,
        }

        self.provider = create_provider(config.provider.provider_type, provider_config)

        # Track model states
        self.model_states = {name: ModelState(name=name) for name in self.models.keys()}
        # Currently loaded models
        self.loaded_models = set()

        # Check provider availability
        if not self.provider.is_available():
            raise RuntimeError(
                f"{config.provider.provider_type} provider is not available"
            )

        self.logger.info(
            f"ModelManager initialized with {len(self.models)} models using {config.provider.provider_type} provider"
        )

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current system memory usage."""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent": memory.percent,
            "free_gb": memory.free / (1024**3),
        }

    def check_memory_threshold(self) -> bool:
        """Check if memory usage is below threshold."""
        memory_info = self.get_memory_usage()
        return memory_info["percent"] / 100.0 < self.memory_threshold

    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a model is available locally."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        try:
            return self.provider.ensure_model_available(model_name)
        except Exception as e:
            self.logger.error(f"Failed to ensure model {model_name} availability: {e}")
            return False

    def load_model(self, model_name: str) -> bool:
        """Load a model into memory."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        state = self.model_states[model_name]
        if state.loaded:
            self.logger.debug(f"Model {model_name} already loaded")
            return True
        try:
            # Check memory before loading
            if not self.check_memory_threshold():
                self.logger.warning("Memory usage high, attempting to free memory")
                self._free_memory()
            # Ensure we don't exceed concurrent model limit
            if len(self.loaded_models) >= self.max_concurrent_models:
                self.logger.info(
                    "Max concurrent models reached, unloading least recently used"
                )
                self._unload_lru_model()
            # Ensure model is available
            if not self.ensure_model_available(model_name):
                return False
            start_time = time.time()
            memory_before = self.get_memory_usage()
            # Test model by making a simple call
            self.logger.info(f"Loading model {model_name}...")
            test_response = self.provider.generate(
                model_name=model_name,
                prompt="Hello",
                temperature=0.1,
                num_ctx=1024,  # Small context for test
                num_predict=1,
            )
            load_time = time.time() - start_time
            memory_after = self.get_memory_usage()
            memory_used = memory_after["used_gb"] - memory_before["used_gb"]
            # Update state
            state.loaded = True
            state.last_used = time.time()
            state.load_time = load_time
            state.memory_usage_mb = memory_used * 1024  # Convert to MB
            self.loaded_models.add(model_name)
            self.logger.log_model_operation(
                "load",
                model_name,
                duration=load_time,
                memory_usage=state.memory_usage_mb,
            )
            return True
        except Exception as e:
            state.error_count += 1
            error_msg = f"Failed to load model {model_name}: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def unload_model(self, model_name: str) -> bool:
        """Unload a model from memory."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        state = self.model_states[model_name]
        if not state.loaded:
            self.logger.debug(f"Model {model_name} not loaded")
            return True
        try:
            # Clear conversation history
            self.provider.clear_conversation_history(model_name)
            # Update state
            state.loaded = False
            state.memory_usage_mb = 0.0
            self.loaded_models.discard(model_name)
            self.logger.log_model_operation("unload", model_name)
            return True
        except Exception as e:
            error_msg = f"Failed to unload model {model_name}: {e}"
            self.logger.error(error_msg)
            return False

    def _unload_lru_model(self):
        """Unload the least recently used model."""
        if not self.loaded_models:
            return
        # Find LRU model
        lru_model = min(
            self.loaded_models, key=lambda name: self.model_states[name].last_used
        )
        self.logger.info(f"Unloading LRU model: {lru_model}")
        self.unload_model(lru_model)

    def _free_memory(self):
        """Free memory by unloading models."""
        # Unload all but the most recently used model
        if len(self.loaded_models) <= 1:
            return
        # Sort by last used time (oldest first)
        models_by_usage = sorted(
            self.loaded_models, key=lambda name: self.model_states[name].last_used
        )
        # Unload all but the most recent
        for model_name in models_by_usage[:-1]:
            self.unload_model(model_name)

    def generate(self, model_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response from a model, loading it if necessary."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        # Load model if not loaded
        if not self.model_states[model_name].loaded:
            if not self.load_model(model_name):
                raise RuntimeError(f"Failed to load model {model_name}")
        # Update model configuration
        model_config = self.models[model_name]
        kwargs.setdefault("temperature", model_config.temperature)
        kwargs.setdefault("num_ctx", model_config.num_ctx)
        kwargs.setdefault("num_predict", model_config.num_predict)
        kwargs.setdefault("timeout", model_config.timeout)
        try:
            start_time = time.time()
            # Generate response
            response = self.provider.generate(model_name, prompt, **kwargs)
            duration = time.time() - start_time
            # Update model state
            state = self.model_states[model_name]
            state.last_used = time.time()
            state.total_calls += 1
            state.total_duration += duration
            return response
        except Exception as e:
            state = self.model_states[model_name]
            state.error_count += 1
            # Try to reload model if there were errors
            if state.error_count >= model_config.max_retries:
                self.logger.warning(
                    f"Model {model_name} has {state.error_count} errors, reloading..."
                )
                self.unload_model(model_name)
                state.error_count = 0
            raise

    def generate_with_conversation(
        self, model_name: str, prompt: str, image_path: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate response with conversation history."""
        kwargs["use_conversation_history"] = True
        kwargs["image_path"] = image_path
        return self.generate(model_name, prompt, **kwargs)

    def generate_structured(
        self, model_name: str, prompt: str, response_model, image_path: Optional[str] = None, **kwargs
    ):
        """Generate structured response using Pydantic model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        # Load model if not loaded
        if not self.model_states[model_name].loaded:
            if not self.load_model(model_name):
                raise RuntimeError(f"Failed to load model {model_name}")
        
        # Update model configuration
        model_config = self.models[model_name]
        kwargs.setdefault("temperature", model_config.temperature)
        kwargs.setdefault("num_ctx", model_config.num_ctx)
        kwargs.setdefault("num_predict", model_config.num_predict)
        kwargs.setdefault("timeout", model_config.timeout)
        
        try:
            start_time = time.time()
            # Generate structured response using provider
            response = self.provider.generate_structured(
                model_name=model_name,
                prompt=prompt,
                response_model=response_model,
                image_path=image_path,
                **kwargs
            )
            duration = time.time() - start_time
            
            # Update model state
            state = self.model_states[model_name]
            state.last_used = time.time()
            state.total_calls += 1
            state.total_duration += duration
            
            return response
        except Exception as e:
            state = self.model_states[model_name]
            state.error_count += 1
            # Try to reload model if there were errors
            if state.error_count >= model_config.max_retries:
                self.logger.warning(
                    f"Model {model_name} has {state.error_count} errors, reloading..."
                )
                self.unload_model(model_name)
                state.error_count = 0
            raise

    def clear_conversation(self, model_name: str):
        """Clear conversation history for a model."""
        self.provider.clear_conversation_history(model_name)
        self.logger.info(f"Cleared conversation history for {model_name}")

    def get_model_stats(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a model or all models."""
        if model_name:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not configured")
            state = self.model_states[model_name]
            return {
                "name": state.name,
                "loaded": state.loaded,
                "last_used": state.last_used,
                "memory_usage_mb": state.memory_usage_mb,
                "load_time": state.load_time,
                "total_calls": state.total_calls,
                "total_duration": state.total_duration,
                "average_duration": state.total_duration / max(state.total_calls, 1),
                "error_count": state.error_count,
            }
        else:
            return {name: self.get_model_stats(name) for name in self.models.keys()}

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        memory_info = self.get_memory_usage()
        return {
            "memory": memory_info,
            "loaded_models": list(self.loaded_models),
            "total_models": len(self.models),
            "memory_threshold": self.memory_threshold,
            "max_concurrent_models": self.max_concurrent_models,
            "provider_type": type(self.provider).__name__,
        }

    def cleanup(self):
        """Clean up all loaded models."""
        self.logger.info("Cleaning up model manager...")
        for model_name in list(self.loaded_models):
            self.unload_model(model_name)
        self.logger.info("Model manager cleanup complete")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
