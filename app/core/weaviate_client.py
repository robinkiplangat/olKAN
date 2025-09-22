"""
Weaviate client for olKAN v2.0
Handles connection and operations with Weaviate vector database
"""

import asyncio
from typing import List, Dict, Any, Optional
import weaviate
from weaviate import Client
import logging
from app.core.config import settings


class WeaviateClient:
    """Client for interacting with Weaviate vector database"""
    
    def __init__(self, url: str = None, api_key: str = None):
        self.url = url or settings.weaviate_url
        self.api_key = api_key or settings.weaviate_api_key
        self.client: Optional[Client] = None
        self.logger = logging.getLogger("weaviate_client")
        self._connected = False
    
    async def connect(self) -> bool:
        """Establish connection to Weaviate"""
        try:
            if self.api_key:
                self.client = Client(
                    url=self.url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=self.api_key)
                )
            else:
                self.client = Client(url=self.url)
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.schema.get
            )
            
            self._connected = True
            self.logger.info(f"Connected to Weaviate at {self.url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Weaviate: {str(e)}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected and self.client is not None
    
    async def create_schema(self, class_name: str, properties: List[Dict[str, Any]]) -> bool:
        """Create a new class schema in Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            schema = {
                "class": class_name,
                "description": f"Class for {class_name}",
                "vectorizer": "none",  # We'll provide our own vectors
                "properties": properties
            }
            
            # Check if class already exists
            existing_schema = await asyncio.get_event_loop().run_in_executor(
                None, self.client.schema.get
            )
            
            existing_classes = [cls['class'] for cls in existing_schema.get('classes', [])]
            
            if class_name not in existing_classes:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.client.schema.create_class, schema
                )
                self.logger.info(f"Created schema for class: {class_name}")
            else:
                self.logger.info(f"Schema for class {class_name} already exists")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create schema for {class_name}: {str(e)}")
            return False
    
    async def add_object(
        self, 
        class_name: str, 
        data_object: Dict[str, Any], 
        vector: List[float] = None
    ) -> Optional[str]:
        """Add an object to Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.client.data_object.create,
                data_object,
                class_name,
                vector
            )
            
            object_id = result
            self.logger.info(f"Added object to {class_name} with ID: {object_id}")
            return object_id
            
        except Exception as e:
            self.logger.error(f"Failed to add object to {class_name}: {str(e)}")
            return None
    
    async def get_object(self, class_name: str, object_id: str) -> Optional[Dict[str, Any]]:
        """Get an object from Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.data_object.get_by_id,
                object_id,
                class_name
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get object {object_id} from {class_name}: {str(e)}")
            return None
    
    async def update_object(
        self, 
        class_name: str, 
        object_id: str, 
        data_object: Dict[str, Any],
        vector: List[float] = None
    ) -> bool:
        """Update an object in Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.data_object.update,
                data_object,
                class_name,
                object_id,
                vector
            )
            
            self.logger.info(f"Updated object {object_id} in {class_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update object {object_id} in {class_name}: {str(e)}")
            return False
    
    async def delete_object(self, class_name: str, object_id: str) -> bool:
        """Delete an object from Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.data_object.delete,
                object_id,
                class_name
            )
            
            self.logger.info(f"Deleted object {object_id} from {class_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete object {object_id} from {class_name}: {str(e)}")
            return False
    
    async def search_objects(
        self, 
        class_name: str, 
        query: str = None,
        vector: List[float] = None,
        limit: int = 10,
        where_filter: Dict[str, Any] = None,
        properties: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search objects in Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            # Build query
            weaviate_query = self.client.query.get(
                class_name=class_name,
                properties=properties or ["*"]
            ).with_limit(limit)
            
            # Add search method
            if vector is not None:
                weaviate_query = weaviate_query.with_near_vector({
                    "vector": vector,
                    "certainty": 0.7
                })
            elif query is not None:
                weaviate_query = weaviate_query.with_near_text({
                    "concepts": [query],
                    "certainty": 0.7
                })
            
            # Add where filter
            if where_filter:
                weaviate_query = weaviate_query.with_where(where_filter)
            
            # Execute query
            result = await asyncio.get_event_loop().run_in_executor(
                None, weaviate_query.do
            )
            
            return result.get("data", {}).get("Get", {}).get(class_name, [])
            
        except Exception as e:
            self.logger.error(f"Failed to search objects in {class_name}: {str(e)}")
            return []
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get the current schema from Weaviate"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            schema = await asyncio.get_event_loop().run_in_executor(
                None, self.client.schema.get
            )
            return schema
            
        except Exception as e:
            self.logger.error(f"Failed to get schema: {str(e)}")
            return {}
    
    async def get_meta(self) -> Dict[str, Any]:
        """Get Weaviate meta information"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        try:
            meta = await asyncio.get_event_loop().run_in_executor(
                None, self.client.misc.get_meta
            )
            return meta
            
        except Exception as e:
            self.logger.error(f"Failed to get meta: {str(e)}")
            return {}
    
    async def batch_add_objects(
        self, 
        class_name: str, 
        objects: List[Dict[str, Any]],
        vectors: List[List[float]] = None
    ) -> List[Optional[str]]:
        """Add multiple objects in batch"""
        if not self.is_connected():
            raise ConnectionError("Not connected to Weaviate")
        
        results = []
        
        try:
            # Use batch processing
            with self.client.batch as batch:
                batch.batch_size = 100
                
                for i, obj in enumerate(objects):
                    vector = vectors[i] if vectors and i < len(vectors) else None
                    
                    batch.add_data_object(
                        data_object=obj,
                        class_name=class_name,
                        vector=vector
                    )
            
            # Note: Weaviate batch doesn't return individual IDs
            # This is a limitation of the current implementation
            results = [f"batch_{i}" for i in range(len(objects))]
            
            self.logger.info(f"Batch added {len(objects)} objects to {class_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to batch add objects to {class_name}: {str(e)}")
            results = [None] * len(objects)
        
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Weaviate connection"""
        try:
            if not self.is_connected():
                return {
                    "status": "disconnected",
                    "error": "Not connected to Weaviate"
                }
            
            # Try to get meta information
            meta = await self.get_meta()
            
            return {
                "status": "healthy",
                "url": self.url,
                "version": meta.get("version", "unknown"),
                "connected": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }
    
    async def disconnect(self):
        """Disconnect from Weaviate"""
        self._connected = False
        self.client = None
        self.logger.info("Disconnected from Weaviate")


# Global Weaviate client instance
weaviate_client = WeaviateClient()
