"""
FastAPI application entry point.

This module initializes the FastAPI application with all necessary middleware,
routers, and configuration.
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router

# Setup logging first
setup_logging()

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Create FastAPI application with enhanced OpenAPI metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Gen Confi Backend API
    
    Enterprise-grade FastAPI backend with PostgreSQL for the Gen Confi application.
    
    ### Features
    - 🔐 JWT-based authentication
    - 👤 User management
    - 📁 File uploads (avatars)
    
    ### Authentication
    Most endpoints require authentication. Use the `/auth/login` endpoint to get an access token,
    then include it in the Authorization header: `Bearer <token>`
    
    ### API Version
    Current API version: **v1**
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    terms_of_service="https://genconfi.com/terms",
    contact={
        "name": "Gen Confi Support",
        "email": "support@genconfi.com",
    },
    license_info={
        "name": "Proprietary",
    },
    servers=[
        {
            "url": "http://localhost:8002",
            "description": "Development server"
        },
        {
            "url": "https://api.genconfi.com",
            "description": "Production server"
        }
    ]
)

# Mount uploads directory to serve static files
app.mount("/api/v1/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Configure CORS
cors_origins = ["*"] if settings.DEBUG else settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


def custom_openapi():
    """Custom OpenAPI schema with security definitions."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme for JWT Bearer token
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token obtained from /auth/login endpoint"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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
    import os
    # Use PORT environment variable or default to 8002 (to avoid conflict with port 8000)
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )

