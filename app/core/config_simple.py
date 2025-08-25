from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = Field("Climate-Aware GPS Navigator", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    api_prefix: str = Field("/api/v1", env="API_PREFIX")
    
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

