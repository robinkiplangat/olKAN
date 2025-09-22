"""
Dataset management endpoints for olKAN v2.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.api.deps import (
    get_database,
    get_current_user,
    require_auth,
    get_pagination_params,
    PaginationParams,
    check_rate_limit
)
from app.models.schemas import Dataset
from app.core.hybrid_storage import get_storage_backend
from app.ai.vector_search import vector_search_engine
from app.ai.knowledge_graph import knowledge_graph
from app.ai.quality_assessment import quality_assessment_service

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/", response_model=Dataset)
async def create_dataset(
    dataset: Dataset,
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    _: None = Depends(check_rate_limit)
):
    """Create a new dataset"""
    try:
        storage = get_storage_backend()
        
        # Create dataset in storage
        created_dataset = await storage.create_dataset(dataset)
        
        # Add to vector database for semantic search
        await vector_search_engine.add_dataset(
            dataset_id=dataset.id,
            title=dataset.title,
            description=dataset.description,
            tags=dataset.tags,
            owner_org=dataset.owner_org,
            license_id=dataset.license_id,
            created_at=dataset.created_at.isoformat() if dataset.created_at else None,
            updated_at=dataset.updated_at.isoformat() if dataset.updated_at else None
        )
        
        # Process for knowledge graph
        await knowledge_graph.process_dataset(
            dataset_id=dataset.id,
            title=dataset.title,
            description=dataset.description,
            tags=dataset.tags
        )
        
        return created_dataset
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dataset: {str(e)}"
        )


@router.get("/", response_model=List[Dataset])
async def list_datasets(
    pagination: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """List datasets with pagination"""
    try:
        storage = get_storage_backend()
        datasets = await storage.list_datasets(
            offset=pagination.offset,
            limit=pagination.size
        )
        return datasets
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets: {str(e)}"
        )


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get a specific dataset by ID"""
    try:
        storage = get_storage_backend()
        dataset = await storage.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        return dataset
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset: {str(e)}"
        )


@router.put("/{dataset_id}", response_model=Dataset)
async def update_dataset(
    dataset_id: str,
    dataset_update: Dataset,
    db: Session = Depends(get_database),
    current_user: Dict[str, Any] = Depends(require_auth),
    _: None = Depends(check_rate_limit)
):
    """Update a dataset"""
    try:
        storage = get_storage_backend()
        
        # Check if dataset exists
        existing_dataset = await storage.get_dataset(dataset_id)
        if not existing_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Update dataset in storage
        updated_dataset = await storage.update_dataset(dataset_id, dataset_update)
        
        # Update in vector database
        await vector_search_engine.update_dataset(
            dataset_id=dataset_id,
            title=dataset_update.title,
            description=dataset_update.description,
            tags=dataset_update.tags,
            owner_org=dataset_update.owner_org,
            license_id=dataset_update.license_id,
            updated_at=dataset_update.updated_at.isoformat() if dataset_update.updated_at else None
        )
        
        # Reprocess for knowledge graph
        await knowledge_graph.process_dataset(
            dataset_id=dataset_id,
            title=dataset_update.title,
            description=dataset_update.description,
            tags=dataset_update.tags
        )
        
        return updated_dataset
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dataset: {str(e)}"
        )


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_database),
    current_user: Dict[str, Any] = Depends(require_auth),
    _: None = Depends(check_rate_limit)
):
    """Delete a dataset"""
    try:
        storage = get_storage_backend()
        
        # Check if dataset exists
        existing_dataset = await storage.get_dataset(dataset_id)
        if not existing_dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Delete from storage
        await storage.delete_dataset(dataset_id)
        
        # Delete from vector database
        await vector_search_engine.delete_dataset(dataset_id)
        
        return {"message": "Dataset deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset: {str(e)}"
        )


@router.get("/{dataset_id}/quality")
async def get_dataset_quality(
    dataset_id: str,
    context: Optional[str] = None,
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get quality assessment for a dataset"""
    try:
        storage = get_storage_backend()
        dataset = await storage.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Convert dataset to dict for quality assessment
        dataset_dict = {
            "title": dataset.title,
            "description": dataset.description,
            "tags": dataset.tags,
            "owner_org": dataset.owner_org,
            "license_id": dataset.license_id,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None
        }
        
        # Perform quality assessment
        quality_report = await quality_assessment_service.assess_dataset_quality(
            dataset_id=dataset_id,
            dataset_metadata=dataset_dict,
            context=context
        )
        
        return quality_report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess dataset quality: {str(e)}"
        )


@router.get("/{dataset_id}/similar")
async def get_similar_datasets(
    dataset_id: str,
    limit: int = 5,
    similarity_threshold: float = 0.7,
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get datasets similar to the specified dataset"""
    try:
        similar_datasets = await vector_search_engine.get_similar_datasets(
            dataset_id=dataset_id,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "dataset_id": dataset_id,
            "similar_datasets": similar_datasets,
            "count": len(similar_datasets)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar datasets: {str(e)}"
        )


@router.get("/{dataset_id}/entities")
async def get_dataset_entities(
    dataset_id: str,
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get entities extracted from a dataset"""
    try:
        # Get entities from knowledge graph
        entities = []
        for entity in knowledge_graph.entities.values():
            if entity.source_dataset == dataset_id:
                entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "confidence": entity.confidence,
                    "metadata": entity.metadata
                })
        
        return {
            "dataset_id": dataset_id,
            "entities": entities,
            "count": len(entities)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset entities: {str(e)}"
        )


@router.get("/{dataset_id}/related")
async def get_related_datasets(
    dataset_id: str,
    relationship_types: Optional[List[str]] = None,
    db: Session = Depends(get_database),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get datasets related through knowledge graph"""
    try:
        related_datasets = knowledge_graph.find_related_datasets(
            dataset_id=dataset_id,
            relationship_types=relationship_types
        )
        
        return {
            "dataset_id": dataset_id,
            "related_datasets": related_datasets,
            "count": len(related_datasets)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get related datasets: {str(e)}"
        )
