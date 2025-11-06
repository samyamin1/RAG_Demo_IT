"""Local LLM wrapper for Ollama integration."""

import ollama
from typing import Optional, List
from rag.config import settings
from rag.prompts.system import get_chat_template


class LocalLLMWrapper:
    """Wrapper for Ollama local LLM with chat template support."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Initialize Ollama wrapper.
        
        Args:
            model: Model name (default from settings)
            base_url: Ollama API base URL (default from settings)
            temperature: Sampling temperature (default from settings)
        """
        self.model = model or settings.ollama_model
        self.base_url = base_url or settings.ollama_base_url
        self.temperature = temperature or settings.temperature
        self.client = ollama.Client(host=self.base_url)
        
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_seqs: Optional[List[str]] = None,
    ) -> str:
        """
        Generate response using Ollama.
        
        Args:
            prompt: User prompt/question
            system_prompt: System instructions
            max_tokens: Max output tokens (default from settings)
            temperature: Override temperature
            stop_seqs: Stop sequences
            
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        options = {
            "temperature": temperature or self.temperature,
            "num_predict": max_tokens or settings.max_output_tokens,
        }
        
        if stop_seqs:
            options["stop"] = stop_seqs
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
    
    def check_available(self) -> bool:
        """Check if Ollama is available and model is pulled."""
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models.get('models', [])]
            # Check for exact match or model with tag
            return any(
                self.model in name or name.startswith(self.model.split(':')[0])
                for name in model_names
            )
        except Exception:
            return False
    
    def pull_model(self):
        """Pull the model if not already available."""
        try:
            print(f"Pulling model {self.model}...")
            self.client.pull(self.model)
            print(f"Model {self.model} pulled successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to pull model {self.model}: {str(e)}")


class OllamaEmbeddings:
    """Ollama embeddings wrapper."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize embeddings.
        
        Args:
            model: Embedding model name (default from settings)
            base_url: Ollama base URL
        """
        self.model = model or settings.ollama_embed_model
        self.base_url = base_url or settings.ollama_base_url
        self.client = ollama.Client(host=self.base_url)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                response = self.client.embeddings(
                    model=self.model,
                    prompt=text
                )
                embeddings.append(response['embedding'])
            except Exception as e:
                raise RuntimeError(f"Embedding failed for text: {str(e)}")
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            raise RuntimeError(f"Query embedding failed: {str(e)}")

