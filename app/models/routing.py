from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base
import uuid
from datetime import datetime


class Route(Base):
    """Calculated routes with risk assessment."""
    __tablename__ = "routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Route metadata
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lon = Column(Float, nullable=False)
    
    # Route properties
    total_distance_meters = Column(Float, nullable=False)
    total_duration_seconds = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    route_type = Column(String(50), nullable=False)  # fastest, safest, balanced
    
    # Route geometry
    route_geom = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    
    # Risk breakdown
    risk_factors = Column(JSONB)  # Detailed risk analysis
    avoided_hazards = Column(JSONB)  # Hazards avoided by this route
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)  # When route becomes stale
    
    # Indexes
    __table_args__ = (
        Index('idx_routes_geom', 'route_geom', postgresql_using='gist'),
        Index('idx_routes_risk', 'risk_score'),
        Index('idx_routes_type', 'route_type'),
        Index('idx_routes_calculated', 'calculated_at'),
    )


class RouteSegment(Base):
    """Individual segments of a calculated route."""
    __tablename__ = "route_segments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey('routes.id'), nullable=False)
    road_id = Column(Integer, ForeignKey('road_network.id'), nullable=False)
    
    # Segment properties
    segment_order = Column(Integer, nullable=False)  # Order in route
    distance_meters = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    
    # Segment geometry
    segment_geom = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    
    # Risk details
    hazard_intersections = Column(JSONB)  # Hazards affecting this segment
    
    # Relationships
    route = relationship("Route")
    road = relationship("RoadNetwork")
    
    # Indexes
    __table_args__ = (
        Index('idx_route_segments_route', 'route_id'),
        Index('idx_route_segments_road', 'road_id'),
        Index('idx_route_segments_order', 'route_id', 'segment_order'),
        Index('idx_route_segments_geom', 'segment_geom', postgresql_using='gist'),
    )


class RouteComparison(Base):
    """Comparison of different route options for the same origin-destination."""
    __tablename__ = "route_comparisons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Comparison metadata
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lon = Column(Float, nullable=False)
    
    # Route options
    fastest_route_id = Column(UUID(as_uuid=True), ForeignKey('routes.id'))
    safest_route_id = Column(UUID(as_uuid=True), ForeignKey('routes.id'))
    balanced_route_id = Column(UUID(as_uuid=True), ForeignKey('routes.id'))
    
    # Comparison metrics
    fastest_duration = Column(Float)
    safest_duration = Column(Float)
    balanced_duration = Column(Float)
    
    fastest_risk = Column(Float)
    safest_risk = Column(Float)
    balanced_risk = Column(Float)
    
    # Trade-off analysis
    safety_trade_off_minutes = Column(Float)  # Extra time for safety
    risk_reduction_percent = Column(Float)  # Risk reduction vs fastest
    
    # Timestamps
    compared_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fastest_route = relationship("Route", foreign_keys=[fastest_route_id])
    safest_route = relationship("Route", foreign_keys=[safest_route_id])
    balanced_route = relationship("Route", foreign_keys=[balanced_route_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_route_comparisons_origin', 'origin_lat', 'origin_lon'),
        Index('idx_route_comparisons_destination', 'destination_lat', 'destination_lon'),
        Index('idx_route_comparisons_timestamp', 'compared_at'),
    ) 