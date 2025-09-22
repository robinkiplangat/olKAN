"""
Vector search engine for olKAN v2.0
Handles semantic search using vector embeddings
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import weaviate
from weaviate import Client
import numpy as np
from app.core.config import settings
from app.ai.embeddings import embedding_service


class VectorSearchEngine:
    """Vector search engine using Weaviate"""
    
    def __init__(self, weaviate_url: str = None, api_key: str = None):
        self.weaviate_url = weaviate_url or getattr(settings, 'weaviate_url', 'http://localhost:8080')
        self.api_key = api_key or getattr(settings, 'weaviate_api_key', None)
        self.client = None
        self.class_name = "Dataset"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Weaviate client"""
        try:
            if self.api_key:
                self.client = Client(
                    url=self.weaviate_url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=self.api_key)
                )
            else:
                self.client = Client(url=self.weaviate_url)
            
            # Test connection
            self.client.schema.get()
        except Exception as e:
            raise Exception(f"Failed to connect to Weaviate: {str(e)}")
    
    async def create_schema(self):
        """Create Weaviate schema for datasets"""
        schema = {
            "class": self.class_name,
            "description": "Dataset entries for semantic search",
            "vectorizer": "none",  # We'll provide our own vectors
            "properties": [
                {
                    "name": "dataset_id",
                    "dataType": ["string"],
                    "description": "Unique dataset identifier"
                },
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "Dataset title"
                },
                {
                    "name": "description",
                    "dataType": ["string"],
                    "description": "Dataset description"
                },
                {
                    "name": "tags",
                    "dataType": ["string[]"],
                    "description": "Dataset tags"
                },
                {
                    "name": "owner_org",
                    "dataType": ["string"],
                    "description": "Organization that owns the dataset"
                },
                {
                    "name": "license_id",
                    "dataType": ["string"],
                    "description": "Dataset license"
                },
                {
                    "name": "created_at",
                    "dataType": ["date"],
                    "description": "Creation timestamp"
                },
                {
                    "name": "updated_at",
                    "dataType": ["date"],
                    "description": "Last update timestamp"
                }
            ]
        }
        
        try:
            # Check if class already exists
            existing_classes = self.client.schema.get()['classes']
            if not any(cls['class'] == self.class_name for cls in existing_classes):
                self.client.schema.create_class(schema)
        except Exception as e:
            raise Exception(f"Failed to create schema: {str(e)}")
    
    async def add_dataset(
        self, 
        dataset_id: str, 
        title: str, 
        description: str, 
        tags: List[str],
        owner_org: str,
        license_id: str,
        created_at: str = None,
        updated_at: str = None
    ):
        """Add a dataset to the vector database"""
        try:
            # Generate embedding for the dataset
            text_to_embed = f"{title} {description} {' '.join(tags)}"
            embedding = await embedding_service.generate_single_embedding(text_to_embed)
            
            # Prepare data object
            data_object = {
                "dataset_id": dataset_id,
                "title": title,
                "description": description,
                "tags": tags,
                "owner_org": owner_org,
                "license_id": license_id,
                "created_at": created_at,
                "updated_at": updated_at
            }
            
            # Add to Weaviate
            self.client.data_object.create(
                data_object=data_object,
                class_name=self.class_name,
                vector=embedding
            )
            
        except Exception as e:
            raise Exception(f"Failed to add dataset to vector database: {str(e)}")
    
    async def update_dataset(
        self, 
        dataset_id: str, 
        title: str = None, 
        description: str = None, 
        tags: List[str] = None,
        owner_org: str = None,
        license_id: str = None,
        updated_at: str = None
    ):
        """Update a dataset in the vector database"""
        try:
            # Get existing dataset
            existing = await self.get_dataset_by_id(dataset_id)
            if not existing:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # Update fields
            update_data = existing.copy()
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if tags is not None:
                update_data["tags"] = tags
            if owner_org is not None:
                update_data["owner_org"] = owner_org
            if license_id is not None:
                update_data["license_id"] = license_id
            if updated_at is not None:
                update_data["updated_at"] = updated_at
            
            # Generate new embedding
            text_to_embed = f"{update_data['title']} {update_data['description']} {' '.join(update_data['tags'])}"
            embedding = await embedding_service.generate_single_embedding(text_to_embed)
            
            # Update in Weaviate
            self.client.data_object.update(
                data_object=update_data,
                class_name=self.class_name,
                uuid=existing["uuid"],
                vector=embedding
            )
            
        except Exception as e:
            raise Exception(f"Failed to update dataset in vector database: {str(e)}")
    
    async def delete_dataset(self, dataset_id: str):
        """Delete a dataset from the vector database"""
        try:
            # Find the dataset
            result = self.client.query.get(
                class_name=self.class_name,
                properties=["dataset_id"]
            ).with_where({
                "path": ["dataset_id"],
                "operator": "Equal",
                "valueString": dataset_id
            }).do()
            
            if result["data"]["Get"][self.class_name]:
                uuid = result["data"]["Get"][self.class_name][0]["_additional"]["id"]
                self.client.data_object.delete(uuid=uuid, class_name=self.class_name)
            
        except Exception as e:
            raise Exception(f"Failed to delete dataset from vector database: {str(e)}")
    
    async def semantic_search(
        self, 
        query: str, 
        limit: int = 10, 
        similarity_threshold: float = 0.7,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = await embedding_service.generate_single_embedding(query)
            
            # Build query
            weaviate_query = self.client.query.get(
                class_name=self.class_name,
                properties=["dataset_id", "title", "description", "tags", "owner_org", "license_id", "created_at", "updated_at"]
            ).with_near_vector({
                "vector": query_embedding,
                "certainty": similarity_threshold
            }).with_limit(limit)
            
            # Add filters if provided
            if filters:
                where_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        where_conditions.append({
                            "path": [key],
                            "operator": "ContainsAny",
                            "valueStringArray": value
                        })
                    else:
                        where_conditions.append({
                            "path": [key],
                            "operator": "Equal",
                            "valueString": value
                        })
                
                if len(where_conditions) == 1:
                    weaviate_query = weaviate_query.with_where(where_conditions[0])
                else:
                    weaviate_query = weaviate_query.with_where({
                        "operator": "And",
                        "operands": where_conditions
                    })
            
            # Execute query
            result = weaviate_query.do()
            
            # Format results
            datasets = []
            for item in result["data"]["Get"][self.class_name]:
                dataset = {
                    "dataset_id": item["dataset_id"],
                    "title": item["title"],
                    "description": item["description"],
                    "tags": item["tags"],
                    "owner_org": item["owner_org"],
                    "license_id": item["license_id"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "similarity_score": item["_additional"]["certainty"]
                }
                datasets.append(dataset)
            
            return datasets
            
        except Exception as e:
            raise Exception(f"Semantic search failed: {str(e)}")
    
    async def hybrid_search(
        self, 
        query: str, 
        limit: int = 10, 
        alpha: float = 0.7,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector and keyword search"""
        try:
            # Generate query embedding
            query_embedding = await embedding_service.generate_single_embedding(query)
            
            # Build hybrid query
            weaviate_query = self.client.query.get(
                class_name=self.class_name,
                properties=["dataset_id", "title", "description", "tags", "owner_org", "license_id", "created_at", "updated_at"]
            ).with_hybrid(
                query=query,
                alpha=alpha,
                vector=query_embedding
            ).with_limit(limit)
            
            # Add filters if provided
            if filters:
                where_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        where_conditions.append({
                            "path": [key],
                            "operator": "ContainsAny",
                            "valueStringArray": value
                        })
                    else:
                        where_conditions.append({
                            "path": [key],
                            "operator": "Equal",
                            "valueString": value
                        })
                
                if len(where_conditions) == 1:
                    weaviate_query = weaviate_query.with_where(where_conditions[0])
                else:
                    weaviate_query = weaviate_query.with_where({
                        "operator": "And",
                        "operands": where_conditions
                    })
            
            # Execute query
            result = weaviate_query.do()
            
            # Format results
            datasets = []
            for item in result["data"]["Get"][self.class_name]:
                dataset = {
                    "dataset_id": item["dataset_id"],
                    "title": item["title"],
                    "description": item["description"],
                    "tags": item["tags"],
                    "owner_org": item["owner_org"],
                    "license_id": item["license_id"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "hybrid_score": item["_additional"]["score"]
                }
                datasets.append(dataset)
            
            return datasets
            
        except Exception as e:
            raise Exception(f"Hybrid search failed: {str(e)}")
    
    async def get_dataset_by_id(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific dataset by ID"""
        try:
            result = self.client.query.get(
                class_name=self.class_name,
                properties=["dataset_id", "title", "description", "tags", "owner_org", "license_id", "created_at", "updated_at"]
            ).with_where({
                "path": ["dataset_id"],
                "operator": "Equal",
                "valueString": dataset_id
            }).do()
            
            if result["data"]["Get"][self.class_name]:
                item = result["data"]["Get"][self.class_name][0]
                return {
                    "dataset_id": item["dataset_id"],
                    "title": item["title"],
                    "description": item["description"],
                    "tags": item["tags"],
                    "owner_org": item["owner_org"],
                    "license_id": item["license_id"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "uuid": item["_additional"]["id"]
                }
            
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get dataset by ID: {str(e)}")
    
    async def get_similar_datasets(
        self, 
        dataset_id: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find datasets similar to a given dataset"""
        try:
            # Get the target dataset
            target_dataset = await self.get_dataset_by_id(dataset_id)
            if not target_dataset:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # Get its vector
            result = self.client.query.get(
                class_name=self.class_name,
                properties=["dataset_id"]
            ).with_where({
                "path": ["dataset_id"],
                "operator": "Equal",
                "valueString": dataset_id
            }).with_additional(["vector"]).do()
            
            if not result["data"]["Get"][self.class_name]:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            target_vector = result["data"]["Get"][self.class_name][0]["_additional"]["vector"]
            
            # Find similar datasets
            similar_result = self.client.query.get(
                class_name=self.class_name,
                properties=["dataset_id", "title", "description", "tags", "owner_org", "license_id"]
            ).with_near_vector({
                "vector": target_vector,
                "certainty": similarity_threshold
            }).with_limit(limit + 1).do()  # +1 to exclude the original dataset
            
            # Format results (excluding the original dataset)
            datasets = []
            for item in similar_result["data"]["Get"][self.class_name]:
                if item["dataset_id"] != dataset_id:
                    dataset = {
                        "dataset_id": item["dataset_id"],
                        "title": item["title"],
                        "description": item["description"],
                        "tags": item["tags"],
                        "owner_org": item["owner_org"],
                        "license_id": item["license_id"],
                        "similarity_score": item["_additional"]["certainty"]
                    }
                    datasets.append(dataset)
            
            return datasets[:limit]
            
        except Exception as e:
            raise Exception(f"Failed to find similar datasets: {str(e)}")


# Global vector search engine instance
vector_search_engine = VectorSearchEngine()
