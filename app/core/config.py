from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    
    # Redis Configuration
    redis_url: str = Field(..., env="REDIS_URL")
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # API Keys and Endpoints
    nws_api_base_url: str = Field(..., env="NWS_API_BASE_URL")
    noaa_nwps_api_key: Optional[str] = Field(None, env="NOAA_NWPS_API_KEY")
    usgs_water_api_base_url: str = Field(..., env="USGS_WATER_API_BASE_URL")
    fema_nfhl_wms_url: str = Field(..., env="FEMA_NFHL_WMS_URL")
    
    # Application Settings
    app_name: str = Field("Climate-Aware GPS Navigator", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    api_prefix: str = Field("/api/v1", env="API_PREFIX")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Data Refresh Intervals (in seconds)
    nws_alerts_refresh_interval: int = Field(300, env="NWS_ALERTS_REFRESH_INTERVAL")
    nwps_data_refresh_interval: int = Field(900, env="NWPS_DATA_REFRESH_INTERVAL")
    usgs_gauge_refresh_interval: int = Field(900, env="USGS_GAUGE_REFRESH_INTERVAL")
    
    # Vector Embeddings
    embedding_model: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_dimension: int = Field(384, env="VECTOR_DIMENSION")
    
    # Map Configuration
    default_map_center_lat: float = Field(32.7767, env="DEFAULT_MAP_CENTER_LAT")
    default_map_center_lon: float = Field(-96.7970, env="DEFAULT_MAP_CENTER_LON")
    default_map_zoom: int = Field(10, env="DEFAULT_MAP_ZOOM")
    
    # Risk Scoring Weights
    floodplain_weight: float = Field(1.0, env="FLOODPLAIN_WEIGHT")
    river_forecast_weight: float = Field(0.8, env="RIVER_FORECAST_WEIGHT")
    rain_intensity_weight: float = Field(0.6, env="RAIN_INTENSITY_WEIGHT")
    alert_severity_weight: float = Field(0.9, env="ALERT_SEVERITY_WEIGHT")
    historic_incident_weight: float = Field(0.4, env="HISTORIC_INCIDENT_WEIGHT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 