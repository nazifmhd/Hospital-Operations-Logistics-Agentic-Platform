"""
Hospital Operations & Logistics Agentic Platform
Main application entry point
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.core.database import init_db, populate_sample_data
from src.core.logging_config import setup_logging
from src.core.middleware import setup_middleware
from src.api.routes import api_router
from src.agents.orchestrator import AgentOrchestrator


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Hospital Operations Platform...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Populate sample data for development
        if settings.DEBUG:
            await populate_sample_data()
            logger.info("Sample data populated successfully")
        
        # Initialize agent orchestrator (optional for API-only mode)
        try:
            orchestrator = AgentOrchestrator()
            await orchestrator.initialize()
            app.state.orchestrator = orchestrator
            logger.info("Agent orchestrator initialized")
        except Exception as e:
            logger.warning(f"Agent orchestrator not available (running in API-only mode): {e}")
            app.state.orchestrator = None
        
        logger.info("Platform startup completed successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start platform: {e}")
        raise
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down Hospital Operations Platform...")
        if hasattr(app.state, 'orchestrator') and app.state.orchestrator is not None:
            await app.state.orchestrator.shutdown()
        logger.info("Platform shutdown completed")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Intelligent agent-based platform for hospital operations management",
        docs_url=settings.API_DOCS_URL if settings.DEBUG else None,
        redoc_url=settings.API_REDOC_URL if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # CORS middleware
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_CREDENTIALS,
            allow_methods=settings.CORS_METHODS,
            allow_headers=settings.CORS_HEADERS,
        )
    
    # Trusted host middleware for production
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1"]
        )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_PREFIX)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.APP_ENV
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return JSONResponse(
            content={
                "message": "Hospital Operations & Logistics Agentic Platform",
                "version": settings.APP_VERSION,
                "docs_url": settings.API_DOCS_URL,
                "health_url": "/health"
            }
        )
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception handler caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )
    
    return app


# Create the application instance
app = create_application()


def main():
    """Main entry point for running the application"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD and settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
