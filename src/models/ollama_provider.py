"""Ollama provider implementation."""

import base64
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import ollama
from pydantic import BaseModel

from core.logger import get_logger
from models.base_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama provider implementation."""

    def __init__(self, host: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.client = ollama.Client(host=host)
        self.logger = get_logger()
        self.conversation_history = {}

    def is_available(self) -> bool:
        """Check if Ollama server is available."""
        try:
            self.client.list()
            return True
        except Exception as e:
            self.logger.error(f"Ollama server not available: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = self.client.list()
            self.logger.debug(f"Ollama list response type: {type(response)}")

            if hasattr(response, "models"):
                models = response.models
                model_names = []
                for model in models:
                    if hasattr(model, "model"):
                        model_names.append(model.model)
                    elif hasattr(model, "name"):
                        model_names.append(model.name)
                    elif isinstance(model, dict):
                        name = (
                            model.get("model") or model.get("name") or model.get("id")
                        )
                        if name:
                            model_names.append(name)
                    elif isinstance(model, str):
                        model_names.append(model)
                return model_names
            elif isinstance(response, dict) and "models" in response:
                models = response["models"]
                if isinstance(models, list):
                    model_names = []
                    for model in models:
                        if isinstance(model, dict):
                            name = (
                                model.get("model")
                                or model.get("name")
                                or model.get("id")
                            )
                            if name:
                                model_names.append(name)
                        elif isinstance(model, str):
                            model_names.append(model)
                    return model_names
            elif isinstance(response, list):
                model_names = []
                for model in response:
                    if hasattr(model, "model"):
                        model_names.append(model.model)
                    elif hasattr(model, "name"):
                        model_names.append(model.name)
                    elif isinstance(model, dict):
                        name = (
                            model.get("model") or model.get("name") or model.get("id")
                        )
                        if name:
                            model_names.append(name)
                    elif isinstance(model, str):
                        model_names.append(model)
                return model_names

            self.logger.warning(
                f"Unexpected response structure from Ollama: {response}"
            )
            return []
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []

    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure a model is available, pulling if necessary."""
        try:
            available_models = self.list_models()
            if model_name in available_models:
                self.logger.info(f"Model {model_name} already available")
                return True
            self.logger.info(f"Pulling model {model_name}...")
            self.client.pull(model_name)
            self.logger.info(f"Successfully pulled model {model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pull model {model_name}: {e}")
            return False

    def _prepare_messages(
        self,
        model_name: str,
        prompt: str,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        use_conversation_history: bool = True,
    ) -> List[Dict[str, Any]]:
        """Prepare messages for chat completion."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if use_conversation_history and model_name in self.conversation_history:
            messages.extend(self.conversation_history[model_name])

        user_message = {"role": "user", "content": prompt}

        if image_path and Path(image_path).exists():
            user_message["images"] = [image_path]

        messages.append(user_message)
        return messages

    def _update_conversation_history(
        self, model_name: str, messages: List[Dict[str, Any]], response: str
    ):
        """Update conversation history."""
        if model_name not in self.conversation_history:
            self.conversation_history[model_name] = []

        if messages:
            self.conversation_history[model_name].append(messages[-1])
            self.conversation_history[model_name].append(
                {"role": "assistant", "content": response}
            )

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
        """Generate response from model with multimodal support."""
        start_time = time.time()
        try:
            messages = self._prepare_messages(
                model_name, prompt, image_path, system_prompt, use_conversation_history
            )

            options = {
                "temperature": temperature,
                "num_ctx": num_ctx,
                "num_predict": num_predict,
            }

            request_params = {
                "model": model_name,
                "messages": messages,
                "options": options,
                "stream": False,
            }

            if format_schema:
                request_params["format"] = format_schema.model_json_schema()

            image_attached = image_path is not None
            self.logger.debug(
                f"Sending request to {model_name}",
                model_name=model_name,
                prompt_length=len(prompt),
                image_attached=image_attached,
                temperature=temperature,
                num_ctx=num_ctx,
                num_predict=num_predict,
                has_format_schema=format_schema is not None,
            )

            response = self.client.chat(**request_params)
            duration = time.time() - start_time
            response_content = response["message"]["content"]

            if use_conversation_history:
                self._update_conversation_history(
                    model_name, messages, response_content
                )

            self.logger.log_api_call(
                model_name=model_name,
                prompt=prompt,
                response=response_content,
                duration=duration,
                image_attached=image_attached,
                file_attached=False,
                temperature=temperature,
                num_ctx=num_ctx,
                num_predict=num_predict,
            )

            return {
                "content": response_content,
                "model": response["model"],
                "created_at": response["created_at"],
                "done": response["done"],
                "duration": duration,
                "total_duration": response.get("total_duration", 0),
                "load_duration": response.get("load_duration", 0),
                "prompt_eval_count": response.get("prompt_eval_count", 0),
                "prompt_eval_duration": response.get("prompt_eval_duration", 0),
                "eval_count": response.get("eval_count", 0),
                "eval_duration": response.get("eval_duration", 0),
            }
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to generate response from {model_name}: {e}"
            self.logger.error(
                error_msg, model_name=model_name, duration=duration, error=str(e)
            )
            raise RuntimeError(error_msg)

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
        try:
            response = self.generate(
                model_name=model_name,
                prompt=prompt,
                image_path=image_path,
                system_prompt=system_prompt,
                format_schema=response_model,
                **kwargs,
            )

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
            raise RuntimeError(error_msg)

    def clear_conversation_history(self, model_name: Optional[str] = None):
        """Clear conversation history for a model or all models."""
        if model_name:
            self.conversation_history.pop(model_name, None)
            self.logger.info(f"Cleared conversation history for {model_name}")
        else:
            self.conversation_history.clear()
            self.logger.info("Cleared all conversation history")

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            info = self.client.show(model_name)
            return info
        except Exception as e:
            self.logger.error(f"Failed to get info for model {model_name}: {e}")
            return super().get_model_info(model_name)

    def delete_model(self, model_name: str) -> bool:
        """Delete a model from local storage."""
        try:
            self.client.delete(model_name)
            self.logger.info(f"Deleted model {model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete model {model_name}: {e}")
            return False
