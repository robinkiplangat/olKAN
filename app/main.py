from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.weaviate_client import weaviate_client
from app.ai.vector_search import vector_search_engine
from app.api.v1 import health, datasets
from app.api.ai import search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting olKAN v2.0...")
    
    # Connect to Weaviate
    try:
        await weaviate_client.connect()
        logger.info("Connected to Weaviate")
    except Exception as e:
        logger.warning(f"Failed to connect to Weaviate: {e}")
    
    # Create vector search schema
    try:
        await vector_search_engine.create_schema()
        logger.info("Vector search schema created")
    except Exception as e:
        logger.warning(f"Failed to create vector search schema: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down olKAN v2.0...")
    await weaviate_client.disconnect()


# Create FastAPI app
app = FastAPI(
    title="olKAN v2.0",
    description="AI-Native Data Catalog with Weaviate Integration",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/ai")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to olKAN v2.0",
        "version": "2.0.0",
        "description": "AI-Native Data Catalog with Weaviate Integration",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }

@app.get("/info")
async def info():
    """Application information"""
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "debug": settings.debug,
        "storage_backend": settings.storage_backend,
        "ai_features": {
            "vector_search": True,
            "knowledge_graph": settings.knowledge_graph_enabled,
            "quality_assessment": settings.quality_assessment_enabled,
            "agents": True
        },
        "weaviate_url": settings.weaviate_url
    }
