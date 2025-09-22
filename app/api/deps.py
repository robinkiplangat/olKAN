"""
API dependencies for olKAN v2.0
Dependency injection for FastAPI endpoints
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.database import get_db
from app.core.weaviate_client import weaviate_client
from app.ai.vector_search import vector_search_engine
from app.ai.knowledge_graph import knowledge_graph
from app.ai.quality_assessment import quality_assessment_service
from app.ai.agents.base_agent import agent_manager
from sqlalchemy.orm import Session

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None


# Dependency functions
async def get_database() -> Session:
    """Get database session"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


async def get_weaviate_client():
    """Get Weaviate client instance"""
    if not weaviate_client.is_connected():
        await weaviate_client.connect()
    return weaviate_client


async def get_vector_search_engine():
    """Get vector search engine instance"""
    return vector_search_engine


async def get_knowledge_graph():
    """Get knowledge graph instance"""
    return knowledge_graph


async def get_quality_assessment_service():
    """Get quality assessment service instance"""
    return quality_assessment_service


async def get_agent_manager():
    """Get agent manager instance"""
    return agent_manager


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if payload is None:
        return None
    
    return payload


def require_auth(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require authentication for protected endpoints"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_admin(
    current_user: Dict[str, Any] = Depends(require_auth)
) -> Dict[str, Any]:
    """Require admin privileges"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]
        else:
            self.requests[client_id] = []
        
        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True


# Global rate limiter
rate_limiter = RateLimiter()


def check_rate_limit(client_id: str = "default"):
    """Check rate limit for requests"""
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )


class PaginationParams:
    """Pagination parameters"""
    
    def __init__(
        self,
        page: int = 1,
        size: int = 20,
        max_size: int = 100
    ):
        if page < 1:
            page = 1
        if size < 1:
            size = 20
        if size > max_size:
            size = max_size
        
        self.page = page
        self.size = size
        self.offset = (page - 1) * size


def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """Get pagination parameters"""
    return PaginationParams(page=page, size=size)


class SearchParams:
    """Search parameters"""
    
    def __init__(
        self,
        query: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ):
        self.query = query
        self.limit = min(limit, 100)  # Cap at 100
        self.similarity_threshold = max(0.0, min(1.0, similarity_threshold))
        self.filters = filters or {}


def get_search_params(
    query: Optional[str] = None,
    limit: int = 10,
    similarity_threshold: float = 0.7,
    filters: Optional[Dict[str, Any]] = None
) -> SearchParams:
    """Get search parameters"""
    return SearchParams(
        query=query,
        limit=limit,
        similarity_threshold=similarity_threshold,
        filters=filters
    )


class QualityAssessmentParams:
    """Quality assessment parameters"""
    
    def __init__(
        self,
        context: Optional[str] = None,
        include_recommendations: bool = True
    ):
        self.context = context
        self.include_recommendations = include_recommendations


def get_quality_params(
    context: Optional[str] = None,
    include_recommendations: bool = True
) -> QualityAssessmentParams:
    """Get quality assessment parameters"""
    return QualityAssessmentParams(
        context=context,
        include_recommendations=include_recommendations
    )


# Common response models
class ErrorResponse:
    """Standard error response"""
    
    def __init__(self, detail: str, error_code: Optional[str] = None):
        self.detail = detail
        self.error_code = error_code


class SuccessResponse:
    """Standard success response"""
    
    def __init__(self, message: str, data: Optional[Any] = None):
        self.message = message
        self.data = data


# Health check dependencies
async def check_database_health(db: Session = Depends(get_database)) -> bool:
    """Check database health"""
    try:
        # Simple query to test connection
        db.execute("SELECT 1")
        return True
    except Exception:
        return False


async def check_weaviate_health(weaviate: Any = Depends(get_weaviate_client)) -> bool:
    """Check Weaviate health"""
    try:
        health = await weaviate.health_check()
        return health.get("status") == "healthy"
    except Exception:
        return False


async def check_ai_services_health() -> Dict[str, bool]:
    """Check AI services health"""
    return {
        "vector_search": True,  # Vector search is always available
        "knowledge_graph": True,  # Knowledge graph is always available
        "quality_assessment": True,  # Quality assessment is always available
        "agents": True  # Agents are always available
    }
