"""
ReconScan API - Main application entry point
FastAPI application with full OSINT capabilities
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.models.database import init_db
from app.api.scan import router as scan_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="ReconScan - Suite OSINT complète avec recherche par pseudo, email, deep scan et corrélation",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Include API routes
    app.include_router(scan_router, prefix=settings.API_PREFIX)
    
    # Serve frontend static files
    frontend_path = Path(__file__).parent.parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_path / "css"), html=False), path="/static/css")
        app.mount("/static", StaticFiles(directory=str(frontend_path / "js"), html=False), path="/static/js")
        app.mount("/static", StaticFiles(directory=str(frontend_path / "assets"), html=False), path="/static/assets")
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize database on startup"""
        await init_db()
        print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")
    
    # Root endpoint - serve frontend
    @app.get("/")
    async def root():
        """Serve the frontend dashboard"""
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "ReconScan API", "docs": "/api/docs"}
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    return app


# Create the application
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )