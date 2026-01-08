"""
FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade FastAPI backend with PostgreSQL",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Mount uploads directory to serve static files
app.mount("/api/v1/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configure CORS
# In development, allow all localhost origins for Flutter web and mobile testing
cors_origins = settings.cors_origins_list
if settings.DEBUG:
    # Allow all localhost origins for development
    cors_origins = ["*"]  # Allow all origins in debug mode for easier development

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
def root():
    """
    Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to FastAPI PostgreSQL API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

