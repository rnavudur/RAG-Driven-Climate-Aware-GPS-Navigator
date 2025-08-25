from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.services.hazard_service import HazardService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tiles/{z}/{x}/{y}.mvt")
async def get_hazard_tiles(
    z: int,
    x: int,
    y: int,
    hazard_types: Optional[str] = Query(None, description="Comma-separated hazard types to include"),
    db: Session = Depends(get_db)
):
    """
    Get vector tiles for hazard overlays.
    
    This endpoint returns Mapbox Vector Tiles (MVT) containing hazard data
    for display on the frontend map. Supports filtering by hazard type.
    """
    try:
        hazard_service = HazardService(db)
        
        # Parse hazard types filter
        types_filter = None
        if hazard_types:
            types_filter = [t.strip() for t in hazard_types.split(",")]
        
        # Generate vector tile
        tile_data = await hazard_service.generate_hazard_tile(
            z=z, x=x, y=y, hazard_types=types_filter
        )
        
        if not tile_data:
            # Return empty tile if no data
            return Response(content=b"", media_type="application/x-protobuf")
        
        return Response(
            content=tile_data,
            media_type="application/x-protobuf",
            headers={"Cache-Control": "public, max-age=300"}  # Cache for 5 minutes
        )
        
    except Exception as e:
        logger.error(f"Error generating hazard tile: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate hazard tile")


@router.get("/types")
async def get_hazard_types(db: Session = Depends(get_db)):
    """
    Get available hazard types and their counts.
    
    This endpoint returns a summary of all hazard types currently
    available in the system with their counts.
    """
    try:
        hazard_service = HazardService(db)
        types = await hazard_service.get_hazard_types_summary()
        return types
        
    except Exception as e:
        logger.error(f"Error retrieving hazard types: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hazard types")


@router.get("/alerts")
async def get_weather_alerts(
    bbox: Optional[str] = Query(None, description="Bounding box as 'min_lon,min_lat,max_lon,max_lat'"),
    alert_types: Optional[str] = Query(None, description="Comma-separated alert types"),
    severity: Optional[str] = Query(None, description="Minimum severity level"),
    db: Session = Depends(get_db)
):
    """
    Get weather alerts for a geographic area.
    
    This endpoint returns active weather alerts from the National Weather Service
    for the specified bounding box or area.
    """
    try:
        hazard_service = HazardService(db)
        
        # Parse bounding box
        bbox_coords = None
        if bbox:
            try:
                coords = [float(c.strip()) for c in bbox.split(",")]
                if len(coords) == 4:
                    bbox_coords = {
                        "min_lon": coords[0],
                        "min_lat": coords[1],
                        "max_lon": coords[2],
                        "max_lat": coords[3]
                    }
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        # Parse alert types filter
        types_filter = None
        if alert_types:
            types_filter = [t.strip() for t in alert_types.split(",")]
        
        alerts = await hazard_service.get_weather_alerts(
            bbox=bbox_coords,
            alert_types=types_filter,
            severity=severity
        )
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "bbox": bbox_coords
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving weather alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weather alerts")


@router.get("/flood-zones")
async def get_flood_zones(
    bbox: Optional[str] = Query(None, description="Bounding box as 'min_lon,min_lat,max_lon,max_lat'"),
    zone_codes: Optional[str] = Query(None, description="Comma-separated FEMA zone codes (AE, VE, X, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Get flood hazard zones for a geographic area.
    
    This endpoint returns FEMA National Flood Hazard Layer data
    for the specified bounding box or area.
    """
    try:
        hazard_service = HazardService(db)
        
        # Parse bounding box
        bbox_coords = None
        if bbox:
            try:
                coords = [float(c.strip()) for c in bbox.split(",")]
                if len(coords) == 4:
                    bbox_coords = {
                        "min_lon": coords[0],
                        "min_lat": coords[1],
                        "max_lon": coords[2],
                        "max_lat": coords[3]
                    }
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        # Parse zone codes filter
        codes_filter = None
        if zone_codes:
            codes_filter = [c.strip() for c in zone_codes.split(",")]
        
        flood_zones = await hazard_service.get_flood_zones(
            bbox=bbox_coords,
            zone_codes=codes_filter
        )
        
        return {
            "flood_zones": flood_zones,
            "total_count": len(flood_zones),
            "bbox": bbox_coords
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving flood zones: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve flood zones")


@router.get("/river-gauges")
async def get_river_gauges(
    bbox: Optional[str] = Query(None, description="Bounding box as 'min_lon,min_lat,max_lon,max_lat'"),
    river_name: Optional[str] = Query(None, description="Filter by river name"),
    include_forecast: bool = Query(True, description="Include forecast data if available"),
    db: Session = Depends(get_db)
):
    """
    Get river gauge data for a geographic area.
    
    This endpoint returns USGS river gauge data and NOAA NWPS forecasts
    for the specified bounding box or area.
    """
    try:
        hazard_service = HazardService(db)
        
        # Parse bounding box
        bbox_coords = None
        if bbox:
            try:
                coords = [float(c.strip()) for c in bbox.split(",")]
                if len(coords) == 4:
                    bbox_coords = {
                        "min_lon": coords[0],
                        "min_lat": coords[1],
                        "max_lon": coords[2],
                        "max_lat": coords[3]
                    }
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        gauges = await hazard_service.get_river_gauges(
            bbox=bbox_coords,
            river_name=river_name,
            include_forecast=include_forecast
        )
        
        return {
            "river_gauges": gauges,
            "total_count": len(gauges),
            "bbox": bbox_coords,
            "include_forecast": include_forecast
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving river gauges: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve river gauges")


@router.get("/sources")
async def get_hazard_sources(
    bbox: str = Query(..., description="Bounding box as 'min_lon,min_lat,max_lon,max_lat'"),
    hazard_types: Optional[str] = Query(None, description="Comma-separated hazard types"),
    db: Session = Depends(get_db)
):
    """
    Get source documents and data sources for hazards in a geographic area.
    
    This endpoint returns metadata about the data sources used for
    hazard assessment in the specified bounding box.
    """
    try:
        hazard_service = HazardService(db)
        
        # Parse bounding box
        try:
            coords = [float(c.strip()) for c in bbox.split(",")]
            if len(coords) != 4:
                raise ValueError("Invalid coordinate count")
            bbox_coords = {
                "min_lon": coords[0],
                "min_lat": coords[1],
                "max_lon": coords[2],
                "max_lat": coords[3]
            }
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid bounding box format")
        
        # Parse hazard types filter
        types_filter = None
        if hazard_types:
            types_filter = [t.strip() for t in hazard_types.split(",")]
        
        sources = await hazard_service.get_hazard_sources(
            bbox=bbox_coords,
            hazard_types=types_filter
        )
        
        return {
            "sources": sources,
            "total_count": len(sources),
            "bbox": bbox_coords
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving hazard sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hazard sources") 