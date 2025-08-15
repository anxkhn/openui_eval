"""vLLM provider implementation."""

import json
import time
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel


from ..core.logger import get_logger
from .base_provider import LLMProvider


class vLLMProvider(LLMProvider):
    """vLLM provider implementation."""

    def __init__(
        self,
        url: str = "http://localhost:8000/v1/completions",
        model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.url = url
        self.default_model = model_name
        self.logger = get_logger()
        self.conversation_history = {}

    def is_available(self) -> bool:
        """Check if vLLM server is available."""
        try:
            # Try to get models list or health check
            health_url = self.url.replace("/v1/completions", "/health")
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            # Fallback: try a simple completion request
            test_response = requests.post(
                self.url,
                json={
                    "model": self.default_model,
                    "prompt": "test",
                    "max_tokens": 1,
                    "temperature": 0.1,
                },
                timeout=10,
            )
            return test_response.status_code == 200
        except Exception as e:
            self.logger.error(f"vLLM server not available: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models. vLLM typically serves one model."""
        try:
            models_url = self.url.replace("/v1/completions", "/v1/models")
            try:
                response = requests.get(models_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data:
                        return [model["id"] for model in data["data"]]
            except:
                pass
            
            # Fallback: return the configured model
            return [self.default_model]
        except Exception as e:
            self.logger.error(f"Failed to list vLLM models: {e}")
            return [self.default_model]

    def _prepare_prompt(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_conversation_history: bool = False,
    ) -> str:
        """Prepare prompt for vLLM completion."""
        full_prompt = ""
        
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"
        
        if use_conversation_history and model_name in self.conversation_history:
            for msg in self.conversation_history[model_name]:
                role = msg["role"].title()
                content = msg["content"]
                full_prompt += f"{role}: {content}\n\n"
        
        full_prompt += f"User: {prompt}\n\nAssistant:"
        return full_prompt

    def _update_conversation_history(
        self, model_name: str, user_prompt: str, response: str
    ):
        """Update conversation history."""
        if model_name not in self.conversation_history:
            self.conversation_history[model_name] = []
        
        self.conversation_history[model_name].extend([
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": response}
        ])

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
        """Generate response from vLLM model."""
        start_time = time.time()
        
        if image_path:
            self.logger.warning("vLLM provider does not support image inputs, ignoring image_path")
        
        try:
            full_prompt = self._prepare_prompt(
                model_name, prompt, system_prompt, use_conversation_history
            )
            
            max_tokens = num_predict if num_predict > 0 else 4096
            
            request_data = {
                "model": model_name,
                "prompt": full_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stop": ["User:", "\nUser:", "Human:", "\nHuman:"],
            }
            
            if format_schema:
                # For structured output, add instruction to the prompt
                structured_prompt = f"{full_prompt}\n\nPlease respond with valid JSON that matches this schema: {format_schema.model_json_schema()}"
                request_data["prompt"] = structured_prompt
            
            self.logger.debug(
                f"Sending request to vLLM {model_name}",
                model_name=model_name,
                prompt_length=len(prompt),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            response = requests.post(
                self.url,
                json=request_data,
                timeout=timeout,
            )
            response.raise_for_status()
            
            duration = time.time() - start_time
            response_data = response.json()
            
            if "choices" not in response_data or not response_data["choices"]:
                raise RuntimeError("No choices returned from vLLM")
            
            content = response_data["choices"][0]["text"].strip()
            
            if use_conversation_history:
                self._update_conversation_history(model_name, prompt, content)
            
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
                "model": model_name,
                "created_at": time.time(),
                "done": True,
                "duration": duration,
                "total_duration": duration * 1000,  # Convert to milliseconds
                "usage": response_data.get("usage", {}),
            }
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to generate response from vLLM {model_name}: {e}"
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
                    f"Successfully parsed structured response from vLLM {model_name}",
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
            error_msg = f"Failed to generate structured response from vLLM: {e}"
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
        return {
            "name": model_name,
            "provider": "vLLM",
            "url": self.url,
            "default_model": self.default_model,
        }
