"""
AI-specific Pydantic models for olKAN v2.0
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    """Search type enumeration"""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"


class QualityMetric(str, Enum):
    """Quality metric enumeration"""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    RELEVANCE = "relevance"


class EntityType(str, Enum):
    """Entity type enumeration"""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    CONCEPT = "CONCEPT"
    DATE = "DATE"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    CARDINAL = "CARDINAL"
    ORDINAL = "ORDINAL"
    QUANTITY = "QUANTITY"
    TIME = "TIME"
    EVENT = "EVENT"
    FAC = "FAC"
    LANGUAGE = "LANGUAGE"
    LAW = "LAW"
    LOC = "LOC"
    NORP = "NORP"
    PRODUCT = "PRODUCT"
    WORK_OF_ART = "WORK_OF_ART"


class RelationshipType(str, Enum):
    """Relationship type enumeration"""
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    LOCATED_IN = "LOCATED_IN"
    CREATED_BY = "CREATED_BY"
    USES = "USES"
    SIMILAR_TO = "SIMILAR_TO"
    DEPENDS_ON = "DEPENDS_ON"
    CONTAINS = "CONTAINS"


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentPriority(str, Enum):
    """Agent priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# Search Models
class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    search_type: SearchType = Field(default=SearchType.SEMANTIC, description="Type of search to perform")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold for vector search")
    alpha: float = Field(default=0.7, ge=0.0, le=1.0, description="Alpha parameter for hybrid search")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters")


class SearchResult(BaseModel):
    """Search result model"""
    dataset_id: str = Field(..., description="Dataset identifier")
    title: str = Field(..., description="Dataset title")
    description: str = Field(..., description="Dataset description")
    tags: List[str] = Field(default_factory=list, description="Dataset tags")
    owner_org: str = Field(..., description="Organization that owns the dataset")
    license_id: str = Field(..., description="Dataset license")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    similarity_score: Optional[float] = Field(default=None, description="Similarity score")
    hybrid_score: Optional[float] = Field(default=None, description="Hybrid search score")


class SearchResponse(BaseModel):
    """Search response model"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results")
    search_type: SearchType = Field(..., description="Type of search performed")
    parameters: Dict[str, Any] = Field(..., description="Search parameters used")


# Quality Assessment Models
class QualityScore(BaseModel):
    """Quality score model"""
    metric: QualityMetric = Field(..., description="Quality metric")
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score (0.0 to 1.0)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the score")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")


class QualityReport(BaseModel):
    """Quality assessment report model"""
    dataset_id: str = Field(..., description="Dataset identifier")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    metric_scores: List[QualityScore] = Field(..., description="Individual metric scores")
    assessment_date: datetime = Field(..., description="Assessment timestamp")
    assessor_version: str = Field(..., description="Version of the quality assessor")
    summary: str = Field(..., description="Quality assessment summary")
    recommendations: List[str] = Field(default_factory=list, description="Overall recommendations")


class QualityAssessmentRequest(BaseModel):
    """Quality assessment request model"""
    dataset_id: str = Field(..., description="Dataset identifier")
    context: Optional[str] = Field(default=None, description="Additional context for assessment")
    include_recommendations: bool = Field(default=True, description="Include improvement recommendations")


# Knowledge Graph Models
class Entity(BaseModel):
    """Entity model"""
    id: str = Field(..., description="Entity identifier")
    name: str = Field(..., description="Entity name")
    type: EntityType = Field(..., description="Entity type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    source_dataset: str = Field(..., description="Source dataset identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class Relationship(BaseModel):
    """Relationship model"""
    id: str = Field(..., description="Relationship identifier")
    source_entity: str = Field(..., description="Source entity identifier")
    target_entity: str = Field(..., description="Target entity identifier")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    source_dataset: str = Field(..., description="Source dataset identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph response model"""
    entities: List[Entity] = Field(..., description="Extracted entities")
    relationships: List[Relationship] = Field(..., description="Extracted relationships")
    total_entities: int = Field(..., description="Total number of entities")
    total_relationships: int = Field(..., description="Total number of relationships")


class EntityNetworkNode(BaseModel):
    """Entity network node model"""
    id: str = Field(..., description="Entity identifier")
    name: str = Field(..., description="Entity name")
    type: EntityType = Field(..., description="Entity type")
    confidence: float = Field(..., description="Confidence score")
    source_dataset: str = Field(..., description="Source dataset identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class EntityNetworkEdge(BaseModel):
    """Entity network edge model"""
    source: str = Field(..., description="Source entity identifier")
    target: str = Field(..., description="Target entity identifier")
    relationship_type: RelationshipType = Field(..., description="Relationship type")
    confidence: float = Field(..., description="Confidence score")


class EntityNetwork(BaseModel):
    """Entity network model"""
    entity: Entity = Field(..., description="Central entity")
    network: Dict[str, List[Union[EntityNetworkNode, EntityNetworkEdge]]] = Field(..., description="Network structure")
    statistics: Dict[str, int] = Field(..., description="Network statistics")


# Agent Models
class AgentTask(BaseModel):
    """Agent task model"""
    id: str = Field(..., description="Task identifier")
    agent_id: str = Field(..., description="Agent identifier")
    task_type: str = Field(..., description="Type of task")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    priority: AgentPriority = Field(default=AgentPriority.NORMAL, description="Task priority")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    status: AgentStatus = Field(..., description="Task status")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task result")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class AgentResult(BaseModel):
    """Agent result model"""
    task_id: str = Field(..., description="Task identifier")
    agent_id: str = Field(..., description="Agent identifier")
    success: bool = Field(..., description="Success status")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AgentStatusResponse(BaseModel):
    """Agent status response model"""
    agent_id: str = Field(..., description="Agent identifier")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    status: AgentStatus = Field(..., description="Current status")
    active_tasks: int = Field(..., description="Number of active tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    max_concurrent_tasks: int = Field(..., description="Maximum concurrent tasks")
    supported_task_types: List[str] = Field(..., description="Supported task types")
    statistics: Dict[str, int] = Field(..., description="Agent statistics")


class AgentTaskRequest(BaseModel):
    """Agent task request model"""
    task_type: str = Field(..., description="Type of task to execute")
    parameters: Dict[str, Any] = Field(..., description="Task parameters")
    priority: AgentPriority = Field(default=AgentPriority.NORMAL, description="Task priority")


# Embedding Models
class EmbeddingRequest(BaseModel):
    """Embedding generation request model"""
    texts: List[str] = Field(..., min_items=1, max_items=100, description="Texts to embed")
    provider: Optional[str] = Field(default=None, description="Embedding provider to use")
    batch_size: Optional[int] = Field(default=100, ge=1, le=1000, description="Batch size for processing")


class EmbeddingResponse(BaseModel):
    """Embedding generation response model"""
    embeddings: List[List[float]] = Field(..., description="Generated embeddings")
    provider: str = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")
    dimensions: int = Field(..., description="Embedding dimensions")
    processing_time: float = Field(..., description="Processing time in seconds")


# Similarity Models
class SimilarityRequest(BaseModel):
    """Similarity search request model"""
    dataset_id: str = Field(..., description="Reference dataset identifier")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of similar datasets")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")


class SimilarityResult(BaseModel):
    """Similarity search result model"""
    dataset_id: str = Field(..., description="Dataset identifier")
    title: str = Field(..., description="Dataset title")
    description: str = Field(..., description="Dataset description")
    tags: List[str] = Field(default_factory=list, description="Dataset tags")
    owner_org: str = Field(..., description="Organization that owns the dataset")
    license_id: str = Field(..., description="Dataset license")
    similarity_score: float = Field(..., description="Similarity score")


class SimilarityResponse(BaseModel):
    """Similarity search response model"""
    dataset_id: str = Field(..., description="Reference dataset identifier")
    similar_datasets: List[SimilarityResult] = Field(..., description="Similar datasets")
    count: int = Field(..., description="Number of similar datasets found")


# Suggestion Models
class SearchSuggestion(BaseModel):
    """Search suggestion model"""
    text: str = Field(..., description="Suggestion text")
    type: str = Field(..., description="Suggestion type")
    dataset_id: Optional[str] = Field(default=None, description="Related dataset identifier")
    score: float = Field(..., description="Suggestion score")


class SearchSuggestionsResponse(BaseModel):
    """Search suggestions response model"""
    query: str = Field(..., description="Original query")
    suggestions: List[SearchSuggestion] = Field(..., description="Search suggestions")
    count: int = Field(..., description="Number of suggestions")
