from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from uuid import uuid4

from app.core.config_simple import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Climate-Aware GPS Navigator (Demo Mode)...")
    yield
    # Shutdown
    logger.info("Shutting down Climate-Aware GPS Navigator...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A smart navigation system that avoids flood-prone areas and provides evidence-backed explanations (Demo Mode)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "mode": "demo"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "description": "Climate-Aware GPS Navigator API (Demo Mode)",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Demo routing endpoint
@app.post("/api/v1/routing/calculate")
async def calculate_route_demo():
    """Demo route calculation endpoint."""
    # Mock route data for Dallas to Houston
    mock_route = {
        "route_id": str(uuid4()),
        "route_type": "balanced",
        "total_distance_meters": 450000,
        "total_duration_seconds": 7200,
        "risk_score": 0.25,
        "segments": [
            {
                "segment_id": str(uuid4()),
                "road_name": "I-45 S",
                "distance_meters": 450000,
                "duration_seconds": 7200,
                "risk_score": 0.25,
                "hazards": [],
                "geometry": [
                    {"lat": 32.7767, "lon": -96.7970},  # Dallas
                    {"lat": 29.7604, "lon": -95.3698}   # Houston
                ]
            }
        ],
        "route_geometry": [
            {"lat": 32.7767, "lon": -96.7970},  # Dallas
            {"lat": 29.7604, "lon": -95.3698}   # Houston
        ],
        "risk_factors": {
            "flood": 0.15,
            "weather": 0.10
        },
        "avoided_hazards": [
            {
                "type": "flood",
                "severity": "moderate",
                "description": "FEMA AE flood zone near Trinity River",
                "source_url": "https://www.fema.gov/flood-maps",
                "source_name": "FEMA NFHL"
            },
            {
                "type": "weather",
                "severity": "minor",
                "description": "NWS flood warning for Harris County",
                "source_url": "https://www.weather.gov",
                "source_name": "National Weather Service"
            }
        ],
        "calculated_at": datetime.utcnow().isoformat(),
        "valid_until": None
    }
    
    return mock_route

# Demo hazards endpoint
@app.get("/api/v1/hazards/types")
async def get_hazard_types_demo():
    """Demo hazard types endpoint."""
    return {
        "hazard_types": [
            {
                "type": "flood",
                "count": 15,
                "description": "Flood zones and warnings"
            },
            {
                "type": "weather",
                "count": 8,
                "description": "Weather alerts and warnings"
            },
            {
                "type": "river",
                "count": 12,
                "description": "River gauge data and forecasts"
            }
        ],
        "total_count": 35
    }

# Demo nearby hazards endpoint
@app.get("/api/v1/routing/nearby-hazards")
async def get_nearby_hazards_demo():
    """Demo nearby hazards endpoint."""
    return {
        "location": {"lat": 32.7767, "lon": -96.7970},
        "radius_km": 10.0,
        "hazards": [
            {
                "id": str(uuid4()),
                "type": "flood",
                "severity": "moderate",
                "description": "FEMA AE flood zone",
                "distance_meters": 2500,
                "source": "FEMA NFHL"
            },
            {
                "id": str(uuid4()),
                "type": "weather",
                "severity": "minor",
                "description": "Flood watch in effect",
                "distance_meters": 5000,
                "source": "NWS"
            }
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

