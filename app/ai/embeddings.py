"""
Embedding generation module for olKAN v2.0
Handles vector embeddings for semantic search and AI features
"""

import asyncio
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import openai
from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        pass
    
    @abstractmethod
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            raise Exception(f"OpenAI embedding generation failed: {str(e)}")
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """HuggingFace embedding provider using sentence-transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using HuggingFace model"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self.model.encode, texts
            )
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"HuggingFace embedding generation failed: {str(e)}")
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]


class EmbeddingService:
    """Main embedding service that manages different providers"""
    
    def __init__(self):
        self.providers: Dict[str, EmbeddingProvider] = {}
        self.default_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available embedding providers"""
        # OpenAI provider
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            self.providers['openai'] = OpenAIEmbeddingProvider(
                api_key=settings.openai_api_key,
                model=getattr(settings, 'openai_embedding_model', 'text-embedding-ada-002')
            )
            self.default_provider = 'openai'
        
        # HuggingFace provider (fallback)
        self.providers['huggingface'] = HuggingFaceEmbeddingProvider(
            model_name=getattr(settings, 'hf_embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        )
        
        if not self.default_provider:
            self.default_provider = 'huggingface'
    
    async def generate_embeddings(
        self, 
        texts: List[str], 
        provider: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings using specified or default provider"""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return await self.providers[provider_name].generate_embeddings(texts)
    
    async def generate_single_embedding(
        self, 
        text: str, 
        provider: Optional[str] = None
    ) -> List[float]:
        """Generate embedding for a single text"""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available")
        
        return await self.providers[provider_name].generate_single_embedding(text)
    
    async def batch_generate_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 100,
        provider: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings in batches to handle large datasets"""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self.generate_embeddings(batch, provider)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def get_available_providers(self) -> List[str]:
        """Get list of available embedding providers"""
        return list(self.providers.keys())
    
    def get_embedding_dimension(self, provider: Optional[str] = None) -> int:
        """Get the dimension of embeddings for a provider"""
        provider_name = provider or self.default_provider
        
        if provider_name == 'openai':
            return 1536  # text-embedding-ada-002 dimension
        elif provider_name == 'huggingface':
            return 384   # all-MiniLM-L6-v2 dimension
        else:
            return 384   # default


# Global embedding service instance
embedding_service = EmbeddingService()
