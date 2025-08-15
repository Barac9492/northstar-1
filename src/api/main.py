"""
FastAPI Main Application
Enterprise-grade API with proper middleware and error handling
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

try:
    from .controllers.content_controller import router as content_router
    from .middleware.error_handler import GlobalErrorHandler
    from .middleware.rate_limiting import RateLimitMiddleware
    from ..infrastructure.config.settings import settings
    from ..infrastructure.logging.logger import get_logger, LoggerMiddleware, setup_logging
    from ..infrastructure.di.container import container, ServiceRegistry
    from ..core.domain.repositories.user_repository import UserRepository
    from ..core.domain.repositories.content_repository import ContentRepository
except ImportError:
    # Fallback for Vercel deployment
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from api.controllers.content_controller import router as content_router
    from api.middleware.error_handler import GlobalErrorHandler  
    from api.middleware.rate_limiting import RateLimitMiddleware
    from infrastructure.config.settings import settings
    from infrastructure.logging.logger import get_logger, LoggerMiddleware, setup_logging
    from infrastructure.di.container import container, ServiceRegistry
    from core.domain.repositories.user_repository import UserRepository
    from core.domain.repositories.content_repository import ContentRepository

# Setup logging
setup_logging()
logger = get_logger('northstar.main')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting NorthStar AI API")
    
    # Initialize dependency injection
    service_registry = ServiceRegistry(container)
    
    # In production, you'd register actual implementations
    # For now, we'll use mock implementations for Vercel deployment
    from ..infrastructure.persistence.repositories.user_repository_impl import PostgreSQLUserRepository
    from ..infrastructure.persistence.repositories.content_repository_impl import PostgreSQLContentRepository
    
    # Register repositories (would use actual DB in production)
    # container.register_singleton(UserRepository, PostgreSQLUserRepository)
    # container.register_singleton(ContentRepository, PostgreSQLContentRepository)
    
    logger.info("NorthStar AI API started successfully")
    
    yield
    
    logger.info("Shutting down NorthStar AI API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-grade AI-powered social media management platform",
    docs_url="/api/docs" if not settings.is_production() else None,
    redoc_url="/api/redoc" if not settings.is_production() else None,
    openapi_url="/api/openapi.json" if not settings.is_production() else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(GlobalErrorHandler)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggerMiddleware)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request"""
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Include routers
app.include_router(content_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "northstar-api",
        "version": settings.app_version,
        "environment": settings.environment.value
    }


# Metrics endpoint (for monitoring)
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {"message": "Metrics endpoint - implement Prometheus metrics here"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NorthStar AI API",
        "version": settings.app_version,
        "docs": "/api/docs" if not settings.is_production() else "Contact admin for API documentation"
    }


# For Vercel deployment
def handler(event, context):
    """Vercel serverless handler"""
    return app(event, context)


# Export for Vercel
app_instance = app