"""OpenRouter provider implementation."""

import json
import os
import time
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from ..core.exceptions import ModelError
from ..core.logger import get_logger
from .base_provider import LLMProvider


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        url: str = "https://openrouter.ai/api/v1/chat/completions",
        default_model: str = "meta-llama/llama-3.1-8b-instruct:free",
        requests_per_minute: int = 20,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.url = url
        self.default_model = default_model
        self.requests_per_minute = requests_per_minute
        self.logger = get_logger()
        self.conversation_history = {}
        self.last_request_time = 0
        
        if not self.api_key:
            raise ModelError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

    def _rate_limit(self):
        """Apply rate limiting based on requests per minute."""
        time_since_last = time.time() - self.last_request_time
        min_interval = 60.0 / self.requests_per_minute
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def is_available(self) -> bool:
        """Check if OpenRouter API is available."""
        if not self.api_key:
            return False
        
        try:
            # Try to get models list
            models_url = "https://openrouter.ai/api/v1/models"
            response = requests.get(
                models_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"OpenRouter API not available: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models from OpenRouter."""
        try:
            models_url = "https://openrouter.ai/api/v1/models"
            response = requests.get(
                models_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    return [model["id"] for model in data["data"]]
            
            self.logger.warning("Failed to get models list from OpenRouter, using default")
            return [self.default_model]
        except Exception as e:
            self.logger.error(f"Failed to list OpenRouter models: {e}")
            return [self.default_model]

    def _prepare_messages(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_conversation_history: bool = False,
    ) -> List[Dict[str, Any]]:
        """Prepare messages for OpenRouter chat completion."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if use_conversation_history and model_name in self.conversation_history:
            messages.extend(self.conversation_history[model_name])
        
        messages.append({"role": "user", "content": prompt})
        return messages

    def _update_conversation_history(
        self, model_name: str, messages: List[Dict[str, Any]], response: str
    ):
        """Update conversation history."""
        if model_name not in self.conversation_history:
            self.conversation_history[model_name] = []
        
        # Add the last user message and response
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
        """Generate response from OpenRouter model."""
        start_time = time.time()
        
        if image_path:
            self.logger.warning("OpenRouter provider does not support image inputs in this implementation, ignoring image_path")
        
        try:
            # Apply rate limiting
            self._rate_limit()
            
            messages = self._prepare_messages(
                model_name, prompt, system_prompt, use_conversation_history
            )
            
            max_tokens = num_predict if num_predict > 0 else None
            
            request_data = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if format_schema:
                # Add JSON schema instruction for structured output
                schema_instruction = f"\n\nPlease respond with valid JSON that matches this schema: {format_schema.model_json_schema()}"
                if messages:
                    messages[-1]["content"] += schema_instruction
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "openui-eval",  # Optional: helps with rate limits
                "X-Title": "OpenUI Eval"  # Optional: title for tracking
            }
            
            self.logger.debug(
                f"Sending request to OpenRouter {model_name}",
                model_name=model_name,
                prompt_length=len(prompt),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            response = requests.post(
                self.url,
                headers=headers,
                json=request_data,
                timeout=timeout,
            )
            
            response.raise_for_status()
            duration = time.time() - start_time
            response_data = response.json()
            
            if "choices" not in response_data or not response_data["choices"]:
                raise ModelError("No choices returned from OpenRouter")
            
            content = response_data["choices"][0]["message"]["content"]
            
            if use_conversation_history:
                self._update_conversation_history(model_name, messages, content)
            
            self.logger.log_api_call(
                model_name=model_name,
                prompt=prompt,
                response=content,
                duration=duration,
                image_attached=False,
                file_attached=False,
                temperature=temperature,
                num_ctx=num_ctx,
                num_predict=num_predict,
            )
            
            return {
                "content": content,
                "model": response_data.get("model", model_name),
                "created_at": response_data.get("created", time.time()),
                "done": True,
                "duration": duration,
                "total_duration": duration * 1000,  # Convert to milliseconds
                "usage": response_data.get("usage", {}),
                "id": response_data.get("id"),
                "object": response_data.get("object"),
            }
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to generate response from OpenRouter {model_name}: {e}"
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
            
            content = response["content"]
            
            # Try to extract JSON from the response
            try:
                # Look for JSON block in markdown
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                else:
                    # Try to find JSON directly
                    json_match = re.search(r'({.*?})', content, re.DOTALL)
                    if json_match:
                        json_content = json_match.group(1)
                    else:
                        json_content = content
                
                structured_response = response_model.model_validate_json(json_content)
                self.logger.debug(
                    f"Successfully parsed structured response from OpenRouter {model_name}",
                    model_name=model_name,
                    response_type=response_model.__name__,
                )
                return structured_response
            except Exception as parse_error:
                self.logger.warning(f"Failed to parse structured response, trying direct validation: {parse_error}")
                # Try parsing the entire content as JSON
                structured_response = response_model.model_validate_json(content)
                return structured_response
                
        except Exception as e:
            error_msg = f"Failed to generate structured response from OpenRouter: {e}"
            self.logger.error(error_msg, model_name=model_name, error=str(e))
            raise ModelError(error_msg)

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
            models_url = "https://openrouter.ai/api/v1/models"
            response = requests.get(
                models_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    for model in data["data"]:
                        if model["id"] == model_name:
                            return {
                                "name": model["id"],
                                "provider": "OpenRouter",
                                "context_length": model.get("context_length"),
                                "pricing": model.get("pricing"),
                                "description": model.get("description"),
                            }
            
            return super().get_model_info(model_name)
        except Exception as e:
            self.logger.error(f"Failed to get info for OpenRouter model {model_name}: {e}")
            return super().get_model_info(model_name)
