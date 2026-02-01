"""
Real-Time Shared Mobility Heatmap - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from api import heatmap_router, health_router
from services.duckdb_service import get_db_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}...")
    print(f"📊 H3 Resolutions: {settings.H3_RESOLUTIONS}")
    print(f"💾 DuckDB: {settings.DUCKDB_PATH}")
    
    # Initialize database connection (read-only for API)
    db_service = get_db_service(read_only=True)
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    db_service.close()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time vehicle density heatmap with H3 spatial indexing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(heatmap_router)
app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

