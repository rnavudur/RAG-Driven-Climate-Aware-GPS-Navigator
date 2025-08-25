from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.schemas.routing import RouteExplanationRequest, RouteExplanationResponse
from app.services.explanation_service import ExplanationService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=RouteExplanationResponse)
async def generate_route_explanation(
    request: RouteExplanationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an explanation for a route using RAG (Retrieval-Augmented Generation).
    
    This endpoint generates human-readable explanations for why a route was chosen,
    including citations to relevant hazard data and safety information.
    """
    try:
        explanation_service = ExplanationService(db)
        
        explanation = await explanation_service.generate_route_explanation(
            route_id=request.route_id,
            explanation_type=request.explanation_type
        )
        
        if not explanation:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating route explanation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate route explanation")


@router.get("/route/{route_id}")
async def get_route_explanation(
    route_id: str,
    explanation_type: str = "detailed",
    db: Session = Depends(get_db)
):
    """
    Retrieve an existing explanation for a route.
    
    This endpoint returns a previously generated explanation for a route,
    or generates a new one if none exists.
    """
    try:
        explanation_service = ExplanationService(db)
        
        explanation = await explanation_service.get_or_generate_explanation(
            route_id=route_id,
            explanation_type=explanation_type
        )
        
        if not explanation:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving route explanation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve route explanation")


@router.get("/templates")
async def get_explanation_templates(db: Session = Depends(get_db)):
    """
    Get available explanation templates.
    
    This endpoint returns the available templates for generating
    different types of route explanations.
    """
    try:
        explanation_service = ExplanationService(db)
        templates = await explanation_service.get_explanation_templates()
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error retrieving explanation templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve explanation templates")


@router.get("/sources/{route_id}")
async def get_explanation_sources(
    route_id: str,
    db: Session = Depends(get_db)
):
    """
    Get source documents used to generate an explanation for a route.
    
    This endpoint returns the knowledge documents and data sources
    that were used to generate the explanation for a specific route.
    """
    try:
        explanation_service = ExplanationService(db)
        
        sources = await explanation_service.get_explanation_sources(route_id)
        
        if not sources:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "route_id": route_id,
            "sources": sources,
            "total_count": len(sources)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving explanation sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve explanation sources")


@router.post("/regenerate/{route_id}")
async def regenerate_route_explanation(
    route_id: str,
    explanation_type: str = "detailed",
    force_regenerate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Regenerate an explanation for a route.
    
    This endpoint forces regeneration of a route explanation,
    useful when new hazard data becomes available.
    """
    try:
        explanation_service = ExplanationService(db)
        
        explanation = await explanation_service.regenerate_explanation(
            route_id=route_id,
            explanation_type=explanation_type,
            force_regenerate=force_regenerate
        )
        
        if not explanation:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "message": "Explanation regenerated successfully",
            "explanation": explanation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating route explanation: {e}")
        raise HTTPException(status_code=500, detail="Failed to regenerate route explanation")


@router.get("/quality/{explanation_id}")
async def get_explanation_quality(
    explanation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get quality metrics for a route explanation.
    
    This endpoint returns quality metrics including:
    - Source relevance scores
    - Citation completeness
    - Factual accuracy indicators
    - User feedback scores
    """
    try:
        explanation_service = ExplanationService(db)
        
        quality_metrics = await explanation_service.get_explanation_quality(explanation_id)
        
        if not quality_metrics:
            raise HTTPException(status_code=404, detail="Explanation not found")
        
        return quality_metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving explanation quality: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve explanation quality") 