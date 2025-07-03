"""
Core configuration module for the Hospital Operations Platform
"""

import os
from pathlib import Path
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
    PYDANTIC_SETTINGS_AVAILABLE = True
except ImportError:
    from pydantic import BaseModel as BaseSettings
    PYDANTIC_SETTINGS_AVAILABLE = False

from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    if not PYDANTIC_SETTINGS_AVAILABLE:
        def __init__(self, **kwargs):
            # Fallback: Load from environment variables manually
            env_values = {}
            for field_name in self.__fields__:
                env_value = os.getenv(field_name.upper())
                if env_value is not None:
                    env_values[field_name] = env_value
            
            # Merge with kwargs
            env_values.update(kwargs)
            super().__init__(**env_values)
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
    
    # Application Settings
    APP_NAME: str = Field(default="Hospital Operations Platform")
    APP_VERSION: str = Field(default="1.0.0")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_PREFIX: str = Field(default="/api/v1")
    API_DOCS_URL: str = Field(default="/docs")
    API_REDOC_URL: str = Field(default="/redoc")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./hospital_platform.db"
    )
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)
    DATABASE_ECHO: bool = Field(default=False)
    
    # Time Series Database (InfluxDB)
    INFLUXDB_URL: str = Field(default="http://localhost:8086")
    INFLUXDB_TOKEN: str = Field(default="")
    INFLUXDB_ORG: str = Field(default="hospital-org")
    INFLUXDB_BUCKET: str = Field(default="hospital-metrics")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_POOL_SIZE: int = Field(default=10)
    REDIS_SOCKET_TIMEOUT: int = Field(default=5)
    
    # Message Queue (Kafka)
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_TOPIC_PREFIX: str = Field(default="hospital")
    KAFKA_GROUP_ID: str = Field(default="hospital-platform")
    
    # Security Configuration
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    ALGORITHM: str = Field(default="HS256")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]
    )
    CORS_CREDENTIALS: bool = Field(default=True)
    CORS_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    CORS_HEADERS: List[str] = Field(default=["*"])
    
    # Agent Configuration
    AGENT_MAX_CONCURRENT: int = Field(default=10)
    AGENT_TIMEOUT_SECONDS: int = Field(default=30)
    AGENT_RETRY_ATTEMPTS: int = Field(default=3)
    
    # AI/ML Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    LANGSMITH_API_KEY: Optional[str] = Field(default=None)
    LANGSMITH_PROJECT: str = Field(default="hospital-platform")
    
    # EMR Integration
    EMR_FHIR_BASE_URL: Optional[str] = Field(default=None)
    EMR_CLIENT_ID: Optional[str] = Field(default=None)
    EMR_CLIENT_SECRET: Optional[str] = Field(default=None)
    EMR_SCOPES: str = Field(default="patient/*.read,encounter/*.read,location/*.read")
    
    # IoT Device Integration
    MQTT_BROKER_HOST: str = Field(default="localhost")
    MQTT_BROKER_PORT: int = Field(default=1883)
    MQTT_USERNAME: Optional[str] = Field(default=None)
    MQTT_PASSWORD: Optional[str] = Field(default=None)
    MQTT_TOPIC_PREFIX: str = Field(default="hospital/devices")
    
    # Monitoring Configuration
    PROMETHEUS_ENABLED: bool = Field(default=True)
    PROMETHEUS_PORT: int = Field(default=9090)
    SENTRY_DSN: Optional[str] = Field(default=None)
    
    # Email Configuration
    SMTP_HOST: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=587)
    SMTP_USERNAME: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_USE_TLS: bool = Field(default=True)
    
    # File Storage
    STORAGE_TYPE: str = Field(default="local")  # local, s3, azure, gcp
    STORAGE_PATH: str = Field(default="./uploads")
    S3_BUCKET_NAME: Optional[str] = Field(default=None)
    S3_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=100)
    RATE_LIMIT_BURST_SIZE: int = Field(default=20)
    
    # Development Settings
    RELOAD: bool = Field(default=True)
    WORKERS: int = Field(default=1)
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic"""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.APP_ENV.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.APP_ENV.lower() == "development"
    
    def get_kafka_topics(self) -> dict:
        """Get Kafka topic names"""
        return {
            "bed_events": f"{self.KAFKA_TOPIC_PREFIX}.bed.events",
            "equipment_events": f"{self.KAFKA_TOPIC_PREFIX}.equipment.events",
            "staff_events": f"{self.KAFKA_TOPIC_PREFIX}.staff.events",
            "supply_events": f"{self.KAFKA_TOPIC_PREFIX}.supply.events",
            "agent_coordination": f"{self.KAFKA_TOPIC_PREFIX}.agents.coordination",
        }


# Global settings instance
settings = Settings()
