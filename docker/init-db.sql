-- Initialize Climate-Aware GPS Navigator Database
-- This script sets up PostGIS and pgRouting extensions

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable pgRouting extension
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create custom functions for hazard-aware routing
CREATE OR REPLACE FUNCTION calculate_hazard_penalty(
    hazard_type text,
    severity text,
    distance_meters float
) RETURNS float AS $$
BEGIN
    -- Base penalty based on hazard type
    DECLARE
        base_penalty float := 0.0;
        severity_multiplier float := 1.0;
    BEGIN
        -- Set base penalty by hazard type
        CASE hazard_type
            WHEN 'flood' THEN base_penalty := 0.5;
            WHEN 'weather' THEN base_penalty := 0.3;
            WHEN 'wildfire' THEN base_penalty := 0.4;
            WHEN 'ice' THEN base_penalty := 0.6;
            ELSE base_penalty := 0.1;
        END CASE;
        
        -- Apply severity multiplier
        CASE severity
            WHEN 'extreme' THEN severity_multiplier := 2.0;
            WHEN 'severe' THEN severity_multiplier := 1.5;
            WHEN 'moderate' THEN severity_multiplier := 1.2;
            WHEN 'minor' THEN severity_multiplier := 1.0;
            ELSE severity_multiplier := 1.0;
        END CASE;
        
        -- Apply distance decay (closer hazards have higher penalty)
        RETURN base_penalty * severity_multiplier * (1.0 / (1.0 + distance_meters / 1000.0));
    END;
END;
$$ LANGUAGE plpgsql;

-- Create function to get nearby hazards
CREATE OR REPLACE FUNCTION get_nearby_hazards(
    point_lat float,
    point_lon float,
    radius_meters float DEFAULT 10000
) RETURNS TABLE(
    hazard_id uuid,
    hazard_type text,
    severity text,
    distance_meters float,
    geom geometry
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.hazard_type,
        h.severity,
        ST_Distance(h.geom, ST_SetSRID(ST_MakePoint(point_lon, point_lat), 4326)) as distance,
        h.geom
    FROM hazard_zones h
    WHERE ST_DWithin(
        h.geom, 
        ST_SetSRID(ST_MakePoint(point_lon, point_lat), 4326), 
        radius_meters
    )
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- Create function to calculate route risk score
CREATE OR REPLACE FUNCTION calculate_route_risk(
    route_geom geometry
) RETURNS float AS $$
DECLARE
    total_risk float := 0.0;
    hazard_count integer := 0;
    hazard_record record;
BEGIN
    -- Calculate risk based on intersecting hazards
    FOR hazard_record IN
        SELECT 
            h.hazard_type,
            h.severity,
            ST_Length(ST_Intersection(route_geom, h.geom)) as intersection_length
        FROM hazard_zones h
        WHERE ST_Intersects(route_geom, h.geom)
    LOOP
        total_risk := total_risk + calculate_hazard_penalty(
            hazard_record.hazard_type,
            hazard_record.severity,
            0.0  -- Distance is 0 for intersections
        ) * hazard_record.intersection_length;
        hazard_count := hazard_count + 1;
    END LOOP;
    
    -- Normalize risk score
    IF hazard_count > 0 THEN
        total_risk := total_risk / hazard_count;
    END IF;
    
    RETURN LEAST(total_risk, 1.0);  -- Cap at 1.0
END;
$$ LANGUAGE plpgsql;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_hazard_zones_spatial ON hazard_zones USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_weather_alerts_spatial ON weather_alerts USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_river_gauges_spatial ON river_gauges USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_road_network_spatial ON road_network USING GIST (geom);

-- Create spatial indexes for route calculations
CREATE INDEX IF NOT EXISTS idx_routes_spatial ON routes USING GIST (route_geom);
CREATE INDEX IF NOT EXISTS idx_route_segments_spatial ON route_segments USING GIST (segment_geom);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE climate_gps TO climate_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO climate_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO climate_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO climate_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO climate_user;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Climate-Aware GPS Navigator database initialized successfully';
    RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
    RAISE NOTICE 'pgRouting version: %', pgr_version();
END $$; 