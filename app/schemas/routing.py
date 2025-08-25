from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


class Coordinate(BaseModel):
    """Geographic coordinate."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class RouteRequest(BaseModel):
    """Request for route calculation."""
    origin: Coordinate
    destination: Coordinate
    depart_time: Optional[datetime] = Field(None, description="Departure time for time-dependent routing")
    avoid: Optional[List[str]] = Field(default=["flood"], description="Hazards to avoid")
    profile: str = Field(default="car", description="Transportation profile")
    route_type: str = Field(default="balanced", description="Route preference: fastest, safest, or balanced")
    
    @validator('route_type')
    def validate_route_type(cls, v):
        if v not in ['fastest', 'safest', 'balanced']:
            raise ValueError('route_type must be one of: fastest, safest, balanced')
        return v


class HazardInfo(BaseModel):
    """Information about a hazard affecting a route."""
    type: str = Field(..., description="Type of hazard")
    severity: str = Field(..., description="Severity level")
    description: str = Field(..., description="Description of the hazard")
    source_url: str = Field(..., description="Source URL for more information")
    source_name: str = Field(..., description="Name of the data source")


class RouteSegment(BaseModel):
    """Individual segment of a route."""
    segment_id: UUID
    road_name: Optional[str]
    distance_meters: float
    duration_seconds: float
    risk_score: float
    hazards: List[HazardInfo] = []
    geometry: List[Coordinate] = Field(..., description="Segment geometry as coordinate list")


class RouteResponse(BaseModel):
    """Response containing calculated route information."""
    route_id: UUID
    route_type: str
    total_distance_meters: float
    total_duration_seconds: float
    risk_score: float
    
    # Route details
    segments: List[RouteSegment]
    route_geometry: List[Coordinate] = Field(..., description="Full route geometry")
    
    # Risk analysis
    risk_factors: Dict[str, Any] = Field(..., description="Detailed risk breakdown")
    avoided_hazards: List[HazardInfo] = Field(..., description="Hazards avoided by this route")
    
    # Metadata
    calculated_at: datetime
    valid_until: Optional[datetime] = Field(None, description="When route becomes stale")


class RouteComparisonRequest(BaseModel):
    """Request for route comparison."""
    origin: Coordinate
    destination: Coordinate
    depart_time: Optional[datetime] = None
    avoid: Optional[List[str]] = ["flood"]
    profile: str = "car"


class RouteComparisonResponse(BaseModel):
    """Response containing comparison of different route options."""
    comparison_id: UUID
    origin: Coordinate
    destination: Coordinate
    
    # Route options
    fastest_route: Optional[RouteResponse]
    safest_route: Optional[RouteResponse]
    balanced_route: Optional[RouteResponse]
    
    # Comparison metrics
    safety_trade_off_minutes: Optional[float] = Field(None, description="Extra time for safety")
    risk_reduction_percent: Optional[float] = Field(None, description="Risk reduction vs fastest route")
    
    # Metadata
    compared_at: datetime


class RouteExplanationRequest(BaseModel):
    """Request for route explanation."""
    route_id: UUID
    explanation_type: str = Field(default="detailed", description="Type of explanation: brief, detailed, or technical")


class RouteExplanationResponse(BaseModel):
    """Response containing route explanation with sources."""
    explanation_id: UUID
    route_id: UUID
    
    # Explanation content
    explanation_markdown: str = Field(..., description="Explanation in markdown format")
    explanation_text: str = Field(..., description="Plain text explanation")
    
    # Risk summary
    risk_summary: str
    avoided_hazards_summary: str
    safety_benefits: str
    
    # Source citations
    source_documents: List[Dict[str, Any]] = Field(..., description="Cited documents with relevance scores")
    
    # Metadata
    model_used: str
    generation_timestamp: datetime
    confidence_score: Optional[float] 