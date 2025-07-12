"""Google GenAI client wrapper with enhanced multimodal and structured output support."""

import base64
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from google import genai
from google.genai import types
from pydantic import BaseModel

from ..core.exceptions import ModelError
from ..core.logger import get_logger


class GoogleGenAIClient:
    """Enhanced Google GenAI client with multimodal and structured output support."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_vertex_ai: bool = False,
        project_id: Optional[str] = None,
        location: str = "us-central1",
    ):
        """
        Initialize Google GenAI client.

        Args:
            api_key: Google API key (can be set via GOOGLE_API_KEY or GEMINI_API_KEY env var)
            use_vertex_ai: Whether to use Vertex AI instead of Gemini Developer API
            project_id: Google Cloud project ID (required for Vertex AI)
            location: Google Cloud location (default: us-central1)
        """
        self.use_vertex_ai = use_vertex_ai
        self.project_id = project_id
        self.location = location
        self.logger = get_logger()
        self.conversation_history = {}  # Track conversations per model

        # Initialize client based on configuration
        try:
            if use_vertex_ai:
                if not project_id:
                    raise ModelError("project_id is required when using Vertex AI")
                self.client = genai.Client(
                    vertexai=True, project=project_id, location=location
                )
                self.logger.info(
                    f"Initialized Google GenAI client with Vertex AI (project: {project_id}, location: {location})"
                )
            else:
                # Use Gemini Developer API
                if not api_key:
                    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ModelError(
                        "API key is required. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable or pass api_key parameter"
                    )

                self.client = genai.Client(api_key=api_key)
                self.logger.info(
                    "Initialized Google GenAI client with Gemini Developer API"
                )

        except Exception as e:
            raise ModelError(f"Failed to initialize Google GenAI client: {e}")

    def is_available(self) -> bool:
        """Check if Google GenAI service is available."""
        try:
            # Try to list models to test connection
            models = list(self.client.models.list(config={"page_size": 1}))
            return len(models) > 0
        except Exception as e:
            self.logger.error(f"Google GenAI service not available: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models."""
        try:
            models = []
            for model in self.client.models.list():
                if hasattr(model, "name"):
                    # Extract model name from full path (e.g., "models/gemini-pro" -> "gemini-pro")
                    model_name = (
                        model.name.split("/")[-1] if "/" in model.name else model.name
                    )
                    models.append(model_name)
                elif hasattr(model, "model"):
                    model_name = (
                        model.model.split("/")[-1]
                        if "/" in model.model
                        else model.model
                    )
                    models.append(model_name)

            self.logger.debug(f"Available Google GenAI models: {models}")
            return models
        except Exception as e:
            self.logger.error(f"Failed to list Google GenAI models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """
        Check if model is available (Google GenAI models don't need to be pulled).

        Args:
            model_name: Name of the model to check

        Returns:
            True if model is available, False otherwise
        """
        try:
            available_models = self.list_models()
            if model_name in available_models:
                self.logger.info(f"Model {model_name} is available")
                return True
            else:
                # Try to get model info directly
                try:
                    model_info = self.client.models.get(model=model_name)
                    self.logger.info(f"Model {model_name} is available")
                    return True
                except:
                    self.logger.error(f"Model {model_name} not found")
                    return False
        except Exception as e:
            self.logger.error(f"Failed to check model {model_name} availability: {e}")
            return False

    def _prepare_contents(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        use_conversation_history: bool = True,
        model_name: str = None,
    ) -> List[Any]:
        """Prepare contents for Google GenAI API."""
        contents = []

        # Handle conversation history
        if (
            use_conversation_history
            and model_name
            and model_name in self.conversation_history
        ):
            # Add previous conversation contents
            contents.extend(self.conversation_history[model_name])

        # Prepare current user message
        user_parts = [types.Part.from_text(text=prompt)]

        # Add image if provided
        if image_path and Path(image_path).exists():
            try:
                # Read image as bytes and create a Part
                with open(image_path, "rb") as f:
                    image_bytes = f.read()

                # Determine MIME type based on file extension
                import mimetypes

                mime_type, _ = mimetypes.guess_type(image_path)
                if not mime_type or not mime_type.startswith("image/"):
                    mime_type = "image/jpeg"  # Default fallback

                user_parts.append(
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                )
            except Exception as e:
                self.logger.warning(f"Failed to load image {image_path}: {e}")

        user_content = types.Content(role="user", parts=user_parts)
        contents.append(user_content)

        return contents

    def _update_conversation_history(
        self, model_name: str, user_content: Any, response_content: str
    ):
        """Update conversation history."""
        if model_name not in self.conversation_history:
            self.conversation_history[model_name] = []

        # Add user message and assistant response
        self.conversation_history[model_name].append(user_content)
        assistant_content = types.Content(
            role="assistant", parts=[types.Part.from_text(text=response_content)]
        )
        self.conversation_history[model_name].append(assistant_content)

    def clear_conversation_history(self, model_name: Optional[str] = None):
        """Clear conversation history for a model or all models."""
        if model_name:
            self.conversation_history.pop(model_name, None)
            self.logger.info(f"Cleared conversation history for {model_name}")
        else:
            self.conversation_history.clear()
            self.logger.info("Cleared all conversation history")

    def generate(
        self,
        model_name: str,
        prompt: str,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_output_tokens: int = 4096,
        top_k: int = 40,
        top_p: float = 0.95,
        response_schema: Optional[BaseModel] = None,
        use_conversation_history: bool = False,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Generate response from Google GenAI model.

        Args:
            model_name: Name of the model to use
            prompt: Text prompt
            image_path: Optional path to image file
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_output_tokens: Maximum tokens to generate
            top_k: Top-k sampling parameter
            top_p: Top-p sampling parameter
            response_schema: Optional Pydantic model for structured output
            use_conversation_history: Whether to use conversation history
            timeout: Request timeout in seconds

        Returns:
            Dictionary with response data
        """
        start_time = time.time()

        try:
            # Prepare contents
            contents = self._prepare_contents(
                prompt, image_path, system_prompt, use_conversation_history, model_name
            )

            # Prepare generation config
            config_dict = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "top_k": top_k,
                "top_p": top_p,
            }

            # Add system instruction if provided
            if system_prompt:
                config_dict["system_instruction"] = system_prompt

            # Add structured output if schema provided
            if response_schema:
                config_dict["response_mime_type"] = "application/json"
                config_dict["response_schema"] = response_schema

            config = types.GenerateContentConfig(**config_dict)

            # Log the request
            image_attached = image_path is not None
            self.logger.debug(
                f"Sending request to {model_name}",
                model_name=model_name,
                prompt_length=len(prompt),
                image_attached=image_attached,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                has_response_schema=response_schema is not None,
            )

            # Make the API call
            response = self.client.models.generate_content(
                model=model_name, contents=contents, config=config
            )

            duration = time.time() - start_time

            # Check if response has text content
            response_text = getattr(response, "text", None)
            if response_text is None:
                # Try to get the response from candidates
                if hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, "content") and candidate.content:
                        if (
                            hasattr(candidate.content, "parts")
                            and candidate.content.parts
                        ):
                            part = candidate.content.parts[0]
                            if hasattr(part, "text"):
                                response_text = part.text

                # If still no text, check for safety ratings or other issues
                if response_text is None:
                    error_details = []
                    if hasattr(response, "candidates") and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, "finish_reason"):
                            error_details.append(
                                f"Finish reason: {candidate.finish_reason}"
                            )
                        if hasattr(candidate, "safety_ratings"):
                            for rating in candidate.safety_ratings:
                                if hasattr(rating, "category") and hasattr(
                                    rating, "probability"
                                ):
                                    error_details.append(
                                        f"Safety: {rating.category} - {rating.probability}"
                                    )

                    error_msg = "No text content in response"
                    if error_details:
                        error_msg += f" ({', '.join(error_details)})"
                    raise ModelError(error_msg)

            # Update conversation history if enabled
            if use_conversation_history and contents:
                self._update_conversation_history(
                    model_name, contents[-1], response_text
                )

            # Log the API call
            self.logger.log_api_call(
                model_name=model_name,
                prompt=prompt,
                response=response_text,
                duration=duration,
                image_attached=image_attached,
                file_attached=False,
                temperature=temperature,
                num_ctx=max_output_tokens,  # Use max_output_tokens as context size approximation
                num_predict=max_output_tokens,
            )

            # Extract metadata from response
            usage_metadata = getattr(response, "usage_metadata", None)
            prompt_token_count = (
                getattr(usage_metadata, "prompt_token_count", 0)
                if usage_metadata
                else 0
            )
            candidates_token_count = (
                getattr(usage_metadata, "candidates_token_count", 0)
                if usage_metadata
                else 0
            )
            total_token_count = (
                getattr(usage_metadata, "total_token_count", 0) if usage_metadata else 0
            )

            return {
                "content": response_text,
                "model": model_name,
                "created_at": time.time(),
                "done": True,
                "duration": duration,
                "total_duration": duration,
                "load_duration": 0,
                "prompt_eval_count": prompt_token_count,
                "prompt_eval_duration": 0,
                "eval_count": candidates_token_count,
                "eval_duration": duration,
                "total_token_count": total_token_count,
            }

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to generate response from {model_name}: {e}"
            self.logger.error(
                error_msg, model_name=model_name, duration=duration, error=str(e)
            )
            raise ModelError(error_msg)

    def generate_structured(
        self,
        model_name: str,
        prompt: str,
        response_model: BaseModel,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Generate structured response using Pydantic model.

        Args:
            model_name: Name of the model to use
            prompt: Text prompt
            response_model: Pydantic model class for structured output
            image_path: Optional path to image file
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for generate()

        Returns:
            Validated instance of response_model
        """
        try:
            response = self.generate(
                model_name=model_name,
                prompt=prompt,
                image_path=image_path,
                system_prompt=system_prompt,
                response_schema=response_model,
                **kwargs,
            )

            # Parse and validate the JSON response
            structured_response = response_model.model_validate_json(
                response["content"]
            )

            self.logger.debug(
                f"Successfully parsed structured response from {model_name}",
                model_name=model_name,
                response_type=response_model.__name__,
            )

            return structured_response

        except Exception as e:
            error_msg = f"Failed to generate structured response: {e}"
            self.logger.error(error_msg, model_name=model_name, error=str(e))
            raise ModelError(error_msg)

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            model_info = self.client.models.get(model=model_name)

            # Convert model info to dictionary
            info_dict = {
                "name": getattr(model_info, "name", model_name),
                "display_name": getattr(model_info, "display_name", ""),
                "description": getattr(model_info, "description", ""),
                "version": getattr(model_info, "version", ""),
                "input_token_limit": getattr(model_info, "input_token_limit", 0),
                "output_token_limit": getattr(model_info, "output_token_limit", 0),
                "supported_generation_methods": getattr(
                    model_info, "supported_generation_methods", []
                ),
            }

            return info_dict
        except Exception as e:
            self.logger.error(f"Failed to get info for model {model_name}: {e}")
            return {}

    def delete_model(self, model_name: str) -> bool:
        """
        Google GenAI models cannot be deleted as they are managed by Google.
        This method is included for API compatibility.
        """
        self.logger.warning(
            f"Cannot delete Google GenAI model {model_name} - models are managed by Google"
        )
        return False

    def count_tokens(
        self, model_name: str, prompt: str, image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Count tokens for the given input."""
        try:
            contents = self._prepare_contents(
                prompt, image_path, use_conversation_history=False
            )

            response = self.client.models.count_tokens(
                model=model_name, contents=contents
            )

            return {
                "total_tokens": getattr(response, "total_tokens", 0),
            }
        except Exception as e:
            self.logger.error(f"Failed to count tokens for {model_name}: {e}")
            return {"total_tokens": 0}
