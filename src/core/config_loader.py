"""
Enhanced configuration loader that integrates with the models catalog.
This module handles loading configurations with provider-aware model definitions.
"""

import os
from typing import Any, Dict, List, Optional

from ..models.models_catalog import (
    ModelProvider,
    get_model_definition,
    is_model_available,
    get_all_model_names,
)
from .config import Config, ModelConfig, TaskConfig, RenderingConfig, EvaluationConfig
from .exceptions import ConfigurationError
from .logger import get_logger


def create_model_config_from_catalog(
    model_name: str, overrides: Optional[Dict[str, Any]] = None
) -> ModelConfig:
    """
    Create a ModelConfig using the models catalog as the source of truth.

    Args:
        model_name: Name of the model
        overrides: Dictionary of settings to override catalog defaults

    Returns:
        ModelConfig instance

    Raises:
        ConfigurationError: If model is not found in catalog
    """
    logger = get_logger()

    # Check if model exists in catalog
    if not is_model_available(model_name):
        available_models = get_all_model_names()
        raise ConfigurationError(
            f"Model '{model_name}' not found in catalog. "
            f"Available models: {', '.join(available_models)}"
        )

    # Get model definition from catalog
    model_def = get_model_definition(model_name)

    # Start with catalog defaults
    config_dict = {
        "name": model_def.name,
        "provider": model_def.provider.value,
        "temperature": model_def.default_temperature,
        "timeout": model_def.default_timeout,
        "max_retries": model_def.default_max_retries,
        "num_ctx": model_def.context_length,
        "num_predict": -1,  # Default to unlimited
    }

    # Add provider-specific settings
    if model_def.provider == ModelProvider.GOOGLE_GENAI:
        config_dict.update(
            {
                "google_api_key": os.getenv("GOOGLE_API_KEY")
                or os.getenv("GEMINI_API_KEY"),
                "use_vertex_ai": model_def.requires_vertex_ai,
                "project_id": None,
                "location": "us-central1",
            }
        )

    # Apply any overrides from the config file
    if overrides:
        # Filter out None values and invalid keys
        valid_overrides = {
            k: v
            for k, v in overrides.items()
            if v is not None and hasattr(ModelConfig, k)
        }
        config_dict.update(valid_overrides)

        if valid_overrides:
            logger.debug(f"Applied overrides for {model_name}: {valid_overrides}")

    return ModelConfig(**config_dict)


def load_models_from_yaml(models_config: Dict[str, Any]) -> List[ModelConfig]:
    """
    Load model configurations from YAML structure.

    Args:
        models_config: The 'models' section from YAML config

    Returns:
        List of ModelConfig instances
    """
    logger = get_logger()
    models = []

    # Handle different YAML structures
    if "enabled_models" in models_config:
        # New structure: models.enabled_models
        enabled_models = models_config["enabled_models"]
        provider_settings = models_config.get("providers", {})

        for model_entry in enabled_models:
            if isinstance(model_entry, str):
                # Simple string format: just model name
                model_config = create_model_config_from_catalog(model_entry)

            elif isinstance(model_entry, dict):
                # Dictionary format with potential overrides
                model_name = model_entry.get("name")
                if not model_name:
                    logger.warning("Model entry missing 'name' field, skipping")
                    continue

                # Merge with provider-specific settings
                overrides = dict(model_entry)

                # If provider is specified, merge with provider settings
                provider = model_entry.get("provider")
                if provider and provider in provider_settings:
                    provider_defaults = provider_settings[provider]
                    # Provider settings have lower priority than model-specific overrides
                    combined_overrides = {**provider_defaults, **overrides}
                    overrides = combined_overrides

                model_config = create_model_config_from_catalog(model_name, overrides)

            else:
                logger.warning(f"Invalid model entry format: {model_entry}")
                continue

            models.append(model_config)

    else:
        # Legacy structure: direct list of models
        model_list = models_config if isinstance(models_config, list) else []
        for model_entry in model_list:
            if isinstance(model_entry, str):
                model_config = create_model_config_from_catalog(model_entry)
            elif isinstance(model_entry, dict):
                model_name = model_entry.get("name")
                if model_name:
                    model_config = create_model_config_from_catalog(
                        model_name, model_entry
                    )
                else:
                    logger.warning("Model entry missing 'name' field, skipping")
                    continue
            else:
                logger.warning(f"Invalid model entry format: {model_entry}")
                continue
            models.append(model_config)

    if not models:
        raise ConfigurationError("No valid models found in configuration")

    logger.info(f"Loaded {len(models)} model configurations")
    return models


def enhance_config_from_dict(data: Dict[str, Any]) -> Config:
    """
    Enhanced version of Config.from_dict that uses the models catalog.

    Args:
        data: Configuration dictionary from YAML

    Returns:
        Config instance with catalog-enhanced model configurations
    """
    logger = get_logger()

    try:
        # Handle models using catalog
        if "models" in data:
            models = load_models_from_yaml(data["models"])
            data["models"] = models

        # Handle tasks (enhanced logic)
        if "tasks" in data:
            tasks = []
            for task_data in data["tasks"]:
                if isinstance(task_data, str):
                    # Simple string format: just task name
                    # Try to get task definition from task_definitions
                    try:
                        from ..tasks.task_definitions import get_task_by_name

                        task_def = get_task_by_name(task_data)
                        if task_def:
                            tasks.append(
                                TaskConfig(
                                    name=task_def.name,
                                    description=task_def.description,
                                    prompt_template=task_def.prompt,
                                    expected_elements=task_def.requirements,
                                    difficulty=task_def.difficulty.value,
                                )
                            )
                        else:
                            logger.warning(
                                f"Task '{task_data}' not found in predefined tasks"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to load task '{task_data}': {e}")
                elif isinstance(task_data, dict):
                    if "name" in task_data and len(task_data) == 1:
                        # Dictionary with only name: try to get from predefined tasks
                        task_name = task_data["name"]
                        try:
                            from ..tasks.task_definitions import get_task_by_name

                            task_def = get_task_by_name(task_name)
                            if task_def:
                                tasks.append(
                                    TaskConfig(
                                        name=task_def.name,
                                        description=task_def.description,
                                        prompt_template=task_def.prompt,
                                        expected_elements=task_def.requirements,
                                        difficulty=task_def.difficulty.value,
                                    )
                                )
                            else:
                                logger.warning(
                                    f"Task '{task_name}' not found in predefined tasks"
                                )
                        except Exception as e:
                            logger.warning(f"Failed to load task '{task_name}': {e}")
                    else:
                        # Full task configuration
                        tasks.append(TaskConfig(**task_data))
                else:
                    logger.warning(f"Invalid task entry format: {task_data}")
            data["tasks"] = tasks

        # Handle rendering config (existing logic)
        if "rendering" in data:
            data["rendering"] = RenderingConfig(**data["rendering"])

        # Handle evaluation config (existing logic)
        if "evaluation" in data:
            data["evaluation"] = EvaluationConfig(**data["evaluation"])

        return Config(**data)

    except Exception as e:
        raise ConfigurationError(f"Failed to create enhanced config from dict: {e}")


def validate_model_availability(models: List[ModelConfig]) -> None:
    """
    Validate that all configured models are available in the catalog.

    Args:
        models: List of model configurations to validate

    Raises:
        ConfigurationError: If any model is not available
    """
    logger = get_logger()
    unavailable_models = []

    for model in models:
        if not is_model_available(model.name):
            unavailable_models.append(model.name)

    if unavailable_models:
        available_models = get_all_model_names()
        raise ConfigurationError(
            f"Models not found in catalog: {', '.join(unavailable_models)}. "
            f"Available models: {', '.join(available_models)}"
        )

    logger.info(f"All {len(models)} models are available in catalog")


def get_model_info_for_cli() -> str:
    """
    Get formatted model information for CLI help.

    Returns:
        Formatted string with available models grouped by provider
    """
    from ..models.models_catalog import get_model_display_info

    info = get_model_display_info()
    lines = ["Available models:"]

    for provider, models in info.items():
        lines.append(f"\n{provider.upper()} Models:")
        for model_name, description in models.items():
            lines.append(f"  {model_name:<20} {description}")

    return "\n".join(lines)
