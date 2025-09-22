"""
AI-powered search endpoints for olKAN v2.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.api.deps import (
    get_vector_search_engine,
    get_current_user,
    get_search_params,
    SearchParams,
    check_rate_limit
)
from app.ai.vector_search import VectorSearchEngine

router = APIRouter(prefix="/search", tags=["ai-search"])


@router.post("/semantic")
async def semantic_search(
    query: str,
    limit: int = 10,
    similarity_threshold: float = 0.7,
    filters: Optional[Dict[str, Any]] = None,
    vector_engine: VectorSearchEngine = Depends(get_vector_search_engine),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    _: None = Depends(check_rate_limit)
):
    """Perform semantic search using vector similarity"""
    try:
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        results = await vector_engine.semantic_search(
            query=query,
            limit=limit,
            similarity_threshold=similarity_threshold,
            filters=filters or {}
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "search_type": "semantic",
            "parameters": {
                "limit": limit,
                "similarity_threshold": similarity_threshold,
                "filters": filters
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/hybrid")
async def hybrid_search(
    query: str,
    limit: int = 10,
    alpha: float = 0.7,
    filters: Optional[Dict[str, Any]] = None,
    vector_engine: VectorSearchEngine = Depends(get_vector_search_engine),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    _: None = Depends(check_rate_limit)
):
    """Perform hybrid search combining vector and keyword search"""
    try:
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        if not 0.0 <= alpha <= 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alpha must be between 0.0 and 1.0"
            )
        
        results = await vector_engine.hybrid_search(
            query=query,
            limit=limit,
            alpha=alpha,
            filters=filters or {}
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "search_type": "hybrid",
            "parameters": {
                "limit": limit,
                "alpha": alpha,
                "filters": filters
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid search failed: {str(e)}"
        )


@router.get("/suggest")
async def search_suggestions(
    query: str,
    limit: int = 5,
    vector_engine: VectorSearchEngine = Depends(get_vector_search_engine),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get search suggestions based on query"""
    try:
        if not query.strip():
            return {"suggestions": [], "query": query}
        
        # Perform a quick semantic search to get suggestions
        results = await vector_engine.semantic_search(
            query=query,
            limit=limit,
            similarity_threshold=0.5
        )
        
        # Extract suggestions from results
        suggestions = []
        for result in results:
            suggestions.append({
                "text": result["title"],
                "type": "dataset",
                "dataset_id": result["dataset_id"],
                "score": result.get("similarity_score", 0.0)
            })
        
        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search suggestions: {str(e)}"
        )


@router.get("/trending")
async def trending_searches(
    limit: int = 10,
    vector_engine: VectorSearchEngine = Depends(get_vector_search_engine),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get trending search terms (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In a real system, you would track search queries and their frequency
        trending_terms = [
            "climate data",
            "economic indicators",
            "health statistics",
            "education metrics",
            "population data",
            "environmental data",
            "financial data",
            "social indicators",
            "technology trends",
            "research data"
        ]
        
        return {
            "trending_terms": trending_terms[:limit],
            "count": len(trending_terms[:limit]),
            "note": "This is a placeholder implementation"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending searches: {str(e)}"
        )


@router.post("/explore")
async def explore_datasets(
    topics: Optional[List[str]] = None,
    limit: int = 20,
    vector_engine: VectorSearchEngine = Depends(get_vector_search_engine),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Explore datasets by topics or categories"""
    try:
        if not topics:
            topics = ["data", "research", "analysis", "statistics"]
        
        all_results = []
        
        # Search for each topic
        for topic in topics:
            results = await vector_engine.semantic_search(
                query=topic,
                limit=limit // len(topics),
                similarity_threshold=0.6
            )
            
            for result in results:
                result["exploration_topic"] = topic
            
            all_results.extend(results)
        
        # Remove duplicates based on dataset_id
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["dataset_id"] not in seen_ids:
                seen_ids.add(result["dataset_id"])
                unique_results.append(result)
        
        # Sort by similarity score
        unique_results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        return {
            "topics": topics,
            "results": unique_results[:limit],
            "count": len(unique_results[:limit]),
            "search_type": "exploration"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to explore datasets: {str(e)}"
        )


@router.get("/stats")
async def search_statistics(
    vector_engine: VectorSearchEngine = Depends(get_vector_search_engine),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get search statistics"""
    try:
        # This is a placeholder implementation
        # In a real system, you would track actual search statistics
        stats = {
            "total_datasets_indexed": 0,  # Would be actual count
            "total_searches_today": 0,    # Would be actual count
            "popular_search_terms": [
                "climate data",
                "economic indicators",
                "health statistics"
            ],
            "search_performance": {
                "average_response_time_ms": 150,
                "success_rate": 0.99
            },
            "index_status": {
                "last_updated": "2024-01-01T00:00:00Z",
                "index_size_mb": 0
            }
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search statistics: {str(e)}"
        )
