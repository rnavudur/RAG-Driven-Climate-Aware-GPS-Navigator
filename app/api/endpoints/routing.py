from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.schemas.routing import (
    RouteRequest, RouteResponse, RouteComparisonRequest, 
    RouteComparisonResponse, Coordinate
)
from app.services.routing_service import RoutingService
from app.services.risk_service import RiskService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/calculate", response_model=RouteResponse)
async def calculate_route(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate a hazard-aware route between origin and destination.
    
    This endpoint calculates a route that considers current weather conditions,
    flood zones, and other hazards to provide safer navigation options.
    """
    try:
        routing_service = RoutingService(db)
        risk_service = RiskService(db)
        
        # Calculate route with risk assessment
        route = await routing_service.calculate_route(
            origin_lat=request.origin.lat,
            origin_lon=request.origin.lon,
            destination_lat=request.destination.lat,
            destination_lon=request.destination.lon,
            route_type=request.route_type,
            avoid_hazards=request.avoid,
            depart_time=request.depart_time
        )
        
        return route
        
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate route")


@router.post("/compare", response_model=RouteComparisonResponse)
async def compare_routes(
    request: RouteComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare different route options (fastest, safest, balanced) for the same origin-destination.
    
    This endpoint provides a comprehensive comparison showing the trade-offs
    between speed and safety for the given route.
    """
    try:
        routing_service = RoutingService(db)
        
        # Calculate route comparison
        comparison = await routing_service.compare_routes(
            origin_lat=request.origin.lat,
            origin_lon=request.origin.lon,
            destination_lat=request.destination.lat,
            destination_lon=request.destination.lon,
            avoid_hazards=request.avoid,
            depart_time=request.depart_time
        )
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing routes: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare routes")


@router.get("/route/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a previously calculated route by ID.
    
    This endpoint allows clients to fetch route details that were
    previously calculated and stored.
    """
    try:
        routing_service = RoutingService(db)
        route = await routing_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return route
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving route: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve route")


@router.get("/nearby-hazards")
async def get_nearby_hazards(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Get hazards near a specific location.
    
    This endpoint returns all known hazards (flood zones, weather alerts,
    river gauges) within the specified radius of the given coordinates.
    """
    try:
        risk_service = RiskService(db)
        hazards = await risk_service.get_nearby_hazards(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        return {
            "location": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "hazards": hazards
        }
        
    except Exception as e:
        logger.error(f"Error retrieving nearby hazards: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve nearby hazards")


@router.get("/route-risk-analysis/{route_id}")
async def analyze_route_risk(
    route_id: str,
    db: Session = Depends(get_db)
):
    """
    Perform detailed risk analysis for a specific route.
    
    This endpoint provides comprehensive risk assessment including:
    - Hazard intersections along the route
    - Risk scoring breakdown
    - Alternative route suggestions
    - Safety recommendations
    """
    try:
        risk_service = RiskService(db)
        analysis = await risk_service.analyze_route_risk(route_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing route risk: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze route risk") 