from fastapi import APIRouter
from app.api.endpoints import routing, hazards, explanations

# Create main API router
router = APIRouter()

# Include endpoint routers
router.include_router(routing.router, prefix="/routing", tags=["routing"])
router.include_router(hazards.router, prefix="/hazards", tags=["hazards"])
router.include_router(explanations.router, prefix="/explanations", tags=["explanations"]) 