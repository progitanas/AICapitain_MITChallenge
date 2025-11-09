from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    
    APP_NAME: str = "AI Captain - Maritime Route Optimization"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aicaptain")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Data
    AIS_DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ais_data.json")
    BATHYMETRY_PATH: str = "./data/bathymetry/gebco_2023.nc"
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    WEATHER_API_URL: str = "https://api.weatherapi.com/v1"
    
    # Optimization Parameters
    MAX_ROUTE_COMPUTE_TIME_SECONDS: float = 5.0
    DEFAULT_WEIGHT_TIME: float = 1.0
    DEFAULT_WEIGHT_COST: float = 1.0
    DEFAULT_WEIGHT_RISK: float = 1.0
    
    # Agent Configuration
    MONITORING_CHECK_INTERVAL_MINUTES: int = 5
    REROUTING_THRESHOLD_DEVIATION_KM: float = 50.0
    FORECAST_HORIZON_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Features
    ENABLE_REAL_TIME_MONITORING: bool = True
    ENABLE_WEATHER_INTEGRATION: bool = True
    ENABLE_PIRACY_DATABASE: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
