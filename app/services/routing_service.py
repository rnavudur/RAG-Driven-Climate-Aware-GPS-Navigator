from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from uuid import uuid4

from app.models.geospatial import RoadNetwork, RoadHazardIntersection
from app.models.routing import Route, RouteSegment, RouteComparison
from app.services.risk_service import RiskService
from app.schemas.routing import RouteResponse, RouteSegment as RouteSegmentSchema, Coordinate

logger = logging.getLogger(__name__)


class RoutingService:
    """Service for calculating hazard-aware routes using pgRouting."""
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_service = RiskService(db)
    
    async def calculate_route(
        self,
        origin_lat: float,
        origin_lon: float,
        destination_lat: float,
        destination_lon: float,
        route_type: str = "balanced",
        avoid_hazards: List[str] = None,
        depart_time: Optional[datetime] = None
    ) -> RouteResponse:
        """
        Calculate a hazard-aware route between origin and destination.
        
        Args:
            origin_lat: Origin latitude
            origin_lon: Origin longitude
            destination_lat: Destination latitude
            destination_lon: Destination longitude
            route_type: Route preference (fastest, safest, balanced)
            avoid_hazards: List of hazard types to avoid
            depart_time: Departure time for time-dependent routing
            
        Returns:
            RouteResponse with route details and risk assessment
        """
        try:
            # Find nearest road nodes to origin and destination
            origin_node = await self._find_nearest_node(origin_lat, origin_lon)
            destination_node = await self._find_nearest_node(destination_lat, destination_lon)
            
            if not origin_node or not destination_node:
                raise ValueError("Could not find road network nodes near origin or destination")
            
            # Calculate route using pgRouting with hazard penalties
            route_result = await self._calculate_pgrouting_route(
                origin_node=origin_node,
                destination_node=destination_node,
                route_type=route_type,
                avoid_hazards=avoid_hazards or ["flood"],
                depart_time=depart_time
            )
            
            if not route_result:
                raise ValueError("No route found between origin and destination")
            
            # Create route record
            route = Route(
                id=uuid4(),
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                destination_lat=destination_lat,
                destination_lon=destination_lon,
                total_distance_meters=route_result["total_distance"],
                total_duration_seconds=route_result["total_duration"],
                risk_score=route_result["risk_score"],
                route_type=route_type,
                route_geom=route_result["geometry"],
                risk_factors=route_result["risk_factors"],
                avoided_hazards=route_result["avoided_hazards"],
                calculated_at=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(hours=1)  # Route valid for 1 hour
            )
            
            # Save route to database
            self.db.add(route)
            self.db.commit()
            self.db.refresh(route)
            
            # Create route segments
            segments = []
            for i, segment_data in enumerate(route_result["segments"]):
                segment = RouteSegment(
                    id=uuid4(),
                    route_id=route.id,
                    road_id=segment_data["road_id"],
                    segment_order=i,
                    distance_meters=segment_data["distance"],
                    duration_seconds=segment_data["duration"],
                    risk_score=segment_data["risk_score"],
                    segment_geom=segment_data["geometry"],
                    hazard_intersections=segment_data["hazards"]
                )
                segments.append(segment)
                self.db.add(segment)
            
            self.db.commit()
            
            # Convert to response schema
            return RouteResponse(
                route_id=route.id,
                route_type=route.route_type,
                total_distance_meters=route.total_distance_meters,
                total_duration_seconds=route.total_duration_seconds,
                risk_score=route.risk_score,
                segments=[self._convert_segment_to_schema(s) for s in segments],
                route_geometry=self._convert_geometry_to_coordinates(route.route_geom),
                risk_factors=route.risk_factors,
                avoided_hazards=route.avoided_hazards,
                calculated_at=route.calculated_at,
                valid_until=route.valid_until
            )
            
        except Exception as e:
            logger.error(f"Error calculating route: {e}")
            self.db.rollback()
            raise
    
    async def compare_routes(
        self,
        origin_lat: float,
        origin_lon: float,
        destination_lat: float,
        destination_lon: float,
        avoid_hazards: List[str] = None,
        depart_time: Optional[datetime] = None
    ) -> RouteComparisonResponse:
        """
        Compare different route options for the same origin-destination.
        
        Returns:
            RouteComparisonResponse with fastest, safest, and balanced routes
        """
        try:
            # Calculate different route types
            fastest_route = await self.calculate_route(
                origin_lat, origin_lon, destination_lat, destination_lon,
                route_type="fastest", avoid_hazards=avoid_hazards, depart_time=depart_time
            )
            
            safest_route = await self.calculate_route(
                origin_lat, origin_lon, destination_lat, destination_lon,
                route_type="safest", avoid_hazards=avoid_hazards, depart_time=depart_time
            )
            
            balanced_route = await self.calculate_route(
                origin_lat, origin_lon, destination_lat, destination_lon,
                route_type="balanced", avoid_hazards=avoid_hazards, depart_time=depart_time
            )
            
            # Calculate comparison metrics
            safety_trade_off = (safest_route.total_duration_seconds - fastest_route.total_duration_seconds) / 60
            risk_reduction = ((fastest_route.risk_score - safest_route.risk_score) / fastest_route.risk_score) * 100
            
            # Create comparison record
            comparison = RouteComparison(
                id=uuid4(),
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                destination_lat=destination_lat,
                destination_lon=destination_lon,
                fastest_route_id=fastest_route.route_id,
                safest_route_id=safest_route.route_id,
                balanced_route_id=balanced_route.route_id,
                fastest_duration=fastest_route.total_duration_seconds,
                safest_duration=safest_route.total_duration_seconds,
                balanced_duration=balanced_route.total_duration_seconds,
                fastest_risk=fastest_route.risk_score,
                safest_risk=safest_route.risk_score,
                balanced_risk=balanced_route.risk_score,
                safety_trade_off_minutes=safety_trade_off,
                risk_reduction_percent=risk_reduction,
                compared_at=datetime.utcnow()
            )
            
            self.db.add(comparison)
            self.db.commit()
            
            return RouteComparisonResponse(
                comparison_id=comparison.id,
                origin=Coordinate(lat=origin_lat, lon=origin_lon),
                destination=Coordinate(lat=destination_lat, lon=destination_lon),
                fastest_route=fastest_route,
                safest_route=safest_route,
                balanced_route=balanced_route,
                safety_trade_off_minutes=safety_trade_off,
                risk_reduction_percent=risk_reduction,
                compared_at=comparison.compared_at
            )
            
        except Exception as e:
            logger.error(f"Error comparing routes: {e}")
            self.db.rollback()
            raise
    
    async def get_route(self, route_id: str) -> Optional[RouteResponse]:
        """Retrieve a previously calculated route by ID."""
        try:
            route = self.db.query(Route).filter(Route.id == route_id).first()
            if not route:
                return None
            
            # Get route segments
            segments = self.db.query(RouteSegment).filter(
                RouteSegment.route_id == route_id
            ).order_by(RouteSegment.segment_order).all()
            
            return RouteResponse(
                route_id=route.id,
                route_type=route.route_type,
                total_distance_meters=route.total_distance_meters,
                total_duration_seconds=route.total_duration_seconds,
                risk_score=route.risk_score,
                segments=[self._convert_segment_to_schema(s) for s in segments],
                route_geometry=self._convert_geometry_to_coordinates(route.route_geom),
                risk_factors=route.risk_factors,
                avoided_hazards=route.avoided_hazards,
                calculated_at=route.calculated_at,
                valid_until=route.valid_until
            )
            
        except Exception as e:
            logger.error(f"Error retrieving route: {e}")
            raise
    
    async def _find_nearest_node(self, lat: float, lon: float) -> Optional[int]:
        """Find the nearest road network node to given coordinates."""
        try:
            # Use PostGIS ST_DWithin to find nearby nodes
            query = text("""
                SELECT id, ST_Distance(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)) as distance
                FROM road_network
                WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 0.01)
                ORDER BY distance
                LIMIT 1
            """)
            
            result = self.db.execute(query, {"lat": lat, "lon": lon}).first()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error finding nearest node: {e}")
            return None
    
    async def _calculate_pgrouting_route(
        self,
        origin_node: int,
        destination_node: int,
        route_type: str,
        avoid_hazards: List[str],
        depart_time: Optional[datetime]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate route using pgRouting with hazard penalties.
        
        This is a simplified implementation. In production, you would:
        1. Use pgRouting's pgr_dijkstra or pgr_astar
        2. Apply dynamic cost functions based on current hazards
        3. Handle time-dependent routing
        """
        try:
            # For MVP, use a simple approach
            # In production, implement full pgRouting integration
            
            # Placeholder implementation
            return {
                "total_distance": 10000.0,  # meters
                "total_duration": 1200.0,   # seconds
                "risk_score": 0.3,
                "geometry": None,  # PostGIS geometry
                "risk_factors": {"flood": 0.2, "weather": 0.1},
                "avoided_hazards": ["flood_zone_1", "weather_alert_2"],
                "segments": [
                    {
                        "road_id": 1,
                        "distance": 5000.0,
                        "duration": 600.0,
                        "risk_score": 0.2,
                        "geometry": None,
                        "hazards": []
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in pgRouting calculation: {e}")
            return None
    
    def _convert_segment_to_schema(self, segment: RouteSegment) -> RouteSegmentSchema:
        """Convert database segment to response schema."""
        return RouteSegmentSchema(
            segment_id=segment.id,
            road_name=None,  # Would get from road_network table
            distance_meters=segment.distance_meters,
            duration_seconds=segment.duration_seconds,
            risk_score=segment.risk_score,
            hazards=[],  # Would convert from hazard_intersections
            geometry=self._convert_geometry_to_coordinates(segment.segment_geom)
        )
    
    def _convert_geometry_to_coordinates(self, geom) -> List[Coordinate]:
        """Convert PostGIS geometry to coordinate list."""
        # Placeholder - would implement actual geometry conversion
        return [Coordinate(lat=0.0, lon=0.0)] 