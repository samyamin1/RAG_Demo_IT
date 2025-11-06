"""Configuration management for RAG module."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings for RAG system."""
    
    # Ollama Configuration
    ollama_model: str = "llama3:8b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_embed_model: str = "nomic-embed-text"
    
    # Storage Directories
    chroma_dir: str = ".chroma"
    bm25_dir: str = ".bm25"
    data_dir: str = "data"
    
    # Retrieval Parameters
    top_k: int = 5
    vector_top_k: int = 10
    bm25_top_k: int = 20
    rrf_k: int = 60
    
    # BM25 Parameters
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    
    # Chunking Parameters
    chunk_size: int = 800
    chunk_overlap: int = 120
    splitter: str = "recursive"
    
    # LLM Generation Parameters
    temperature: float = 0.2
    max_context_tokens: int = 6000
    max_output_tokens: int = 1024
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Evaluation
    eval_epochs: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance."""
    return settings


def print_config():
    """Print effective configuration."""
    print("\n" + "="*60)
    print("RAG SYSTEM CONFIGURATION")
    print("="*60)
    print(f"Ollama Model:        {settings.ollama_model}")
    print(f"Ollama URL:          {settings.ollama_base_url}")
    print(f"Embed Model:         {settings.ollama_embed_model}")
    print(f"\nRetrieval:")
    print(f"  TOP_K:             {settings.top_k}")
    print(f"  VECTOR_TOP_K:      {settings.vector_top_k}")
    print(f"  BM25_TOP_K:        {settings.bm25_top_k}")
    print(f"  RRF_K:             {settings.rrf_k}")
    print(f"\nBM25:")
    print(f"  K1:                {settings.bm25_k1}")
    print(f"  B:                 {settings.bm25_b}")
    print(f"\nChunking:")
    print(f"  CHUNK_SIZE:        {settings.chunk_size}")
    print(f"  CHUNK_OVERLAP:     {settings.chunk_overlap}")
    print(f"\nLLM:")
    print(f"  TEMPERATURE:       {settings.temperature}")
    print(f"  MAX_CONTEXT:       {settings.max_context_tokens}")
    print("="*60 + "\n")

