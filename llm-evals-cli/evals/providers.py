"""Provider interface and implementations for LLM evaluation."""

import json
import re
import time
from typing import Any, Dict, List, Optional, Protocol

import requests


class BaseProvider(Protocol):
    """Protocol for LLM providers."""
    
    name: str
    
    def generate(
        self, 
        model: str, 
        prompt: str, 
        temperature: Optional[float] = None, 
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """Generate text using the provider.
        
        Returns:
            dict with keys: text, tokens_in, tokens_out, raw
        """
        ...
    
    def list_models(self) -> List[str]:
        """List available models."""
        ...
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        ...


class OllamaProvider:
    """Ollama provider for local LLM inference."""
    
    name = "ollama"
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count using rough heuristic."""
        return max(1, round(len(text) / 4))
    
    def generate(
        self, 
        model: str, 
        prompt: str, 
        temperature: Optional[float] = None, 
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        
        # Remove provider prefix if present
        if model.startswith("ollama/"):
            model = model[7:]
            
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if temperature is not None:
            payload["options"] = {"temperature": temperature}
            
        start_time = time.perf_counter()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            data = response.json()
            
            # Extract text
            text = data.get("response", "")
            
            # Extract token counts (if available) or estimate
            tokens_in = data.get("prompt_eval_count")
            if tokens_in is None:
                tokens_in = self._estimate_tokens(prompt)
                
            tokens_out = data.get("eval_count")
            if tokens_out is None:
                tokens_out = self._estimate_tokens(text)
            
            return {
                "text": text,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "latency_ms": latency_ms,
                "raw": data
            }
            
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Ollama response: {e}")
            
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            models = []
            for model in data.get("models", []):
                name = model.get("name", "").split(":")[0]  # Remove tag
                if name:
                    models.append(name)
                    
            return sorted(models)
            
        except requests.RequestException:
            return []
            
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
            
    def model_exists(self, model: str) -> bool:
        """Check if a specific model exists."""
        if model.startswith("ollama/"):
            model = model[7:]
        return model in self.list_models()


def get_provider(provider_name: str) -> BaseProvider:
    """Get provider instance by name."""
    if provider_name == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}. Only 'ollama' is supported.")


def parse_model_string(model: str) -> tuple[str, str]:
    """Parse model string into provider and model name.
    
    Args:
        model: String like "ollama/llama3" or "llama3"
        
    Returns:
        tuple of (provider_name, model_name)
    """
    if "/" in model:
        provider, model_name = model.split("/", 1)
        return provider, model_name
    else:
        # Default to ollama if no provider specified
        return "ollama", model
