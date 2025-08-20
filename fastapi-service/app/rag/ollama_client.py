"""
Ollama client for LLM interactions
"""
import requests
import json
from typing import Optional, Dict, Any
import os


class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def ensure_model_pulled(self) -> bool:
        """Ensure the model is downloaded"""
        try:
            # Check if model exists
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"].startswith(self.model.split(":")[0]):
                        return True
            
            # Pull model if not exists
            pull_data = {"name": self.model}
            response = requests.post(
                f"{self.base_url}/api/pull", 
                json=pull_data,
                timeout=300  # 5 minutes timeout for model download
            )
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate response using Ollama"""
        try:
            if not self.is_available():
                return None
                
            # Ensure model is available
            if not self.ensure_model_pulled():
                return None
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                data["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
        
        return None
