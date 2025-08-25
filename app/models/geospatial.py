from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index, BigInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base
import uuid
from datetime import datetime


class RoadNetwork(Base):
    """OpenStreetMap road network imported to PostGIS."""
    __tablename__ = "road_network"
    
    id = Column(Integer, primary_key=True)
    osm_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255))
    highway = Column(String(50))  # motorway, trunk, primary, etc.
    surface = Column(String(50))
    lanes = Column(Integer)
    maxspeed = Column(Integer)
    
    # PostGIS geometry
    geom = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    
    # Routing attributes
    length_meters = Column(Float)
    travel_time_seconds = Column(Float)
    
    # Indexes for spatial queries
    __table_args__ = (
        Index('idx_road_network_geom', 'geom', postgresql_using='gist'),
        Index('idx_road_network_highway', 'highway'),
        Index('idx_road_network_osm_id', 'osm_id'),
    )


class HazardZone(Base):
    """FEMA National Flood Hazard Layer and other hazard zones."""
    __tablename__ = "hazard_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hazard_type = Column(String(50), nullable=False)  # flood, wildfire, etc.
    zone_code = Column(String(10))  # AE, VE, X, etc. for FEMA
    severity = Column(String(20))  # high, medium, low
    source = Column(String(100))  # FEMA, local, etc.
    
    # PostGIS geometry
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Metadata
    effective_date = Column(DateTime)
    expiration_date = Column(DateTime)
    source_url = Column(Text)
    properties = Column(JSONB)  # Additional properties from source
    
    # Indexes
    __table_args__ = (
        Index('idx_hazard_zones_geom', 'geom', postgresql_using='gist'),
        Index('idx_hazard_zones_type', 'hazard_type'),
        Index('idx_hazard_zones_severity', 'severity'),
    )


class WeatherAlert(Base):
    """National Weather Service alerts and warnings."""
    __tablename__ = "weather_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(String(100), unique=True, nullable=False)
    event_type = Column(String(100), nullable=False)  # Flood Warning, etc.
    severity = Column(String(20), nullable=False)  # Extreme, Severe, Moderate, Minor
    urgency = Column(String(20))  # Immediate, Expected, Future, Past
    
    # PostGIS geometry
    geom = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Timing
    effective_start = Column(DateTime, nullable=False)
    effective_end = Column(DateTime, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    
    # Content
    headline = Column(Text)
    description = Column(Text)
    instruction = Column(Text)
    
    # Source
    source_url = Column(Text)
    properties = Column(JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_weather_alerts_geom', 'geom', postgresql_using='gist'),
        Index('idx_weather_alerts_type', 'event_type'),
        Index('idx_weather_alerts_severity', 'severity'),
        Index('idx_weather_alerts_effective', 'effective_start', 'effective_end'),
    )


class RiverGauge(Base):
    """USGS river gauges and NOAA NWPS forecast points."""
    __tablename__ = "river_gauges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gauge_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    river_name = Column(String(255))
    
    # Location
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Current conditions
    current_stage_feet = Column(Float)
    current_flow_cfs = Column(Float)
    current_timestamp = Column(DateTime)
    
    # Forecast data
    forecast_stage_feet = Column(Float)
    forecast_flow_cfs = Column(Float)
    forecast_timestamp = Column(DateTime)
    
    # Flood thresholds
    minor_flood_stage = Column(Float)
    moderate_flood_stage = Column(Float)
    major_flood_stage = Column(Float)
    
    # Source
    source = Column(String(50))  # USGS, NOAA
    source_url = Column(Text)
    properties = Column(JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_river_gauges_geom', 'geom', postgresql_using='gist'),
        Index('idx_river_gauges_gauge_id', 'gauge_id'),
        Index('idx_river_gauges_river', 'river_name'),
    )


class RoadHazardIntersection(Base):
    """Intersection of road segments with hazard zones for routing."""
    __tablename__ = "road_hazard_intersections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    road_id = Column(Integer, ForeignKey('road_network.id'), nullable=False)
    hazard_id = Column(UUID(as_uuid=True), ForeignKey('hazard_zones.id'), nullable=False)
    
    # Intersection geometry
    intersection_geom = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Risk scoring
    risk_score = Column(Float, nullable=False)
    risk_factors = Column(JSONB)  # Breakdown of risk components
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    road = relationship("RoadNetwork")
    hazard = relationship("HazardZone")
    
    # Indexes
    __table_args__ = (
        Index('idx_road_hazard_road', 'road_id'),
        Index('idx_road_hazard_hazard', 'hazard_id'),
        Index('idx_road_hazard_risk', 'risk_score'),
        Index('idx_road_hazard_intersection_geom', 'intersection_geom', postgresql_using='gist'),
    ) 