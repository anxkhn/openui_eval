"""Gemini provider implementation for Google's Gemini models."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel

from models.base_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""

    def __init__(self, config: Any):
        """Initialize Gemini provider with configuration."""
        self.config = config
        # Handle both dict and object config
        if isinstance(config, dict):
            self.api_key = config.get("gemini_api_key")
            self.timeout = config.get("timeout", 300)
        else:
            self.api_key = config.gemini_api_key
            self.timeout = config.timeout
        self.client = None
        self._conversation_history = {}
        self._last_error = None

    def _initialize_client(self):
        """Initialize the Gemini client."""
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        if not self.client:
            self.client = genai.Client(
                api_key=self.api_key, http_options={"timeout": self.timeout}
            )

    def is_available(self) -> bool:
        """Check if Gemini API is available."""
        try:
            self._initialize_client()
            # Just try to list models - that's enough to verify connectivity
            models = self.list_models()
            if not models:
                self._last_error = "No models available"
                return False
            return True
        except Exception as e:
            # Store the error for debugging
            self._last_error = str(e)
            return False

    def list_models(self) -> List[str]:
        """List available Gemini models."""
        try:
            self._initialize_client()
            # Query actual available models from the API
            models = []
            for model in self.client.models.list():
                if "generateContent" in model.supported_actions:
                    models.append(model.name)
            return models
        except Exception as e:
            # Fallback to hardcoded list if API call fails
            return [
                "gemini-2.5-flash",
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-1.0-pro",
            ]

    def _prepare_image_part(self, image_path: str) -> Optional[types.Part]:
        """Prepare image for Gemini API."""
        if not image_path or not Path(image_path).exists():
            return None

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Determine MIME type based on file extension
            ext = Path(image_path).suffix.lower()
            mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

            return types.Part.from_bytes(data=image_data, mime_type=mime_type)
        except Exception as e:
            raise ValueError(f"Failed to process image {image_path}: {e}")

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
        """Generate response from Gemini model."""
        start_time = time.time()

        try:
            self._initialize_client()

            # Prepare content parts
            parts = [types.Part.from_text(text=prompt)]

            if image_path:
                image_part = self._prepare_image_part(image_path)
                if image_part:
                    parts.append(image_part)

            content = types.Content(parts=parts, role="user")

            # Handle conversation history
            if use_conversation_history and model_name in self._conversation_history:
                contents = self._conversation_history[model_name] + [content]
            else:
                contents = [content]

            # Generation config using latest API
            generation_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=num_predict if num_predict > 0 else None,
                top_p=0.95,
                top_k=40,
            )

            # System instruction if provided
            if system_prompt:
                generation_config.system_instruction = types.Part.from_text(
                    text=system_prompt
                )

            # Generate response
            response = self.client.models.generate_content(
                model=model_name, contents=contents, config=generation_config
            )

            # Extract content from response
            generated_text = ""
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        generated_text += part.text

            # Update conversation history
            if use_conversation_history:
                if model_name not in self._conversation_history:
                    self._conversation_history[model_name] = []
                self._conversation_history[model_name].extend(
                    [
                        content,
                        types.Content(
                            parts=[types.Part.from_text(text=generated_text)],
                            role="model",
                        ),
                    ]
                )

            duration = time.time() - start_time

            return {
                "content": generated_text,
                "model": model_name,
                "duration": duration,
                "usage": getattr(response, "usage_metadata", {}),
                "finish_reason": (
                    response.candidates[0].finish_reason
                    if response.candidates
                    else None
                ),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "content": "",
                "model": model_name,
                "duration": duration,
                "error": str(e),
            }

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
        # Add JSON schema instructions to the prompt
        schema = response_model.model_json_schema()

        json_prompt = f"""
{prompt}

Please respond with a valid JSON object that matches this schema:
```json
{json.dumps(schema, indent=2)}
```

Your response must be valid JSON that can be parsed according to this schema.
"""

        # Generate response
        response = self.generate(
            model_name=model_name,
            prompt=json_prompt,
            image_path=image_path,
            system_prompt=system_prompt,
            **kwargs,
        )

        try:
            # Extract JSON from the response
            content = response.get("content", "")
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            # Parse and validate
            data = json.loads(json_str)
            return response_model.model_validate(data)
        except Exception as e:
            raise ValueError(f"Failed to parse structured response: {e}")

    def clear_conversation_history(self, model_name: Optional[str] = None):
        """Clear conversation history for a model or all models."""
        if model_name:
            self._conversation_history.pop(model_name, None)
        else:
            self._conversation_history.clear()
