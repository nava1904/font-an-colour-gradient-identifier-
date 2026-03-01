"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router
from app.routes.health import router as health_router

app = FastAPI(
    title="Font and Color Identifier",
    description="ML-powered font and color extraction from images",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Font and Color Identifier API",
        "docs": "/docs",
        "health": "/health",
        "analyze": "POST /api/analyze",
    }
