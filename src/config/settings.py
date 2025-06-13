"""Configuration settings for Zep MCP Server."""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, ValidationInfo


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Zep Cloud Configuration
    zep_api_key: str = Field(..., description="Zep Cloud API key")
    zep_base_url: str = Field(
        default="https://api.getzep.com",
        description="Zep Cloud API base URL"
    )
    
    # MCP Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8052, description="Server port")
    transport: str = Field(default="sse", description="Transport type (sse or stdio)")
    
    # User ID Configuration
    zep_user_ids: str = Field(
        default="aaron_whaley",
        description="Comma-separated list of allowed user IDs"
    )
    zep_default_user_id: str = Field(
        default="aaron_whaley",
        description="Default user ID for multi-platform memory continuity"
    )
    
    log_level: str = Field(default="INFO", description="Logging level")
    rate_limit_per_minute: int = Field(
        default=100,
        description="Rate limit per minute per user"
    )
    memory_retention_days: int = Field(
        default=365,
        description="Days to retain memory data"
    )
    
    # Performance Settings
    max_concurrent_requests: int = Field(
        default=100,
        description="Maximum concurrent requests"
    )
    request_timeout_seconds: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    cache_ttl_seconds: int = Field(
        default=300,
        description="Cache TTL in seconds"
    )
    
    # Development Settings
    debug: bool = Field(default=False, description="Debug mode")
    enable_cors: bool = Field(default=True, description="Enable CORS")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()
    
    @field_validator("transport")
    @classmethod
    def validate_transport(cls, v):
        """Validate transport type."""
        valid_transports = ["sse", "stdio"]
        if v.lower() not in valid_transports:
            raise ValueError(f"Invalid transport: {v}")
        return v.lower()
    
    @field_validator("zep_default_user_id")
    @classmethod
    def validate_default_user_id(cls, v, info: ValidationInfo):
        """Validate that default user ID is in allowed list."""
        allowed_ids_str = info.data.get("zep_user_ids", "aaron_whaley")
        if isinstance(allowed_ids_str, str):
            allowed_ids = [uid.strip() for uid in allowed_ids_str.split(",") if uid.strip()]
        else:
            allowed_ids = allowed_ids_str
        if v not in allowed_ids:
            raise ValueError(f"Default user ID '{v}' must be in allowed user IDs: {allowed_ids}")
        return v
    
    def is_valid_user_id(self, user_id: str) -> bool:
        """Check if a user ID is in the allowed list."""
        return user_id in self.get_allowed_user_ids()
    
    def get_allowed_user_ids(self) -> List[str]:
        """Get the list of allowed user IDs."""
        if isinstance(self.zep_user_ids, str):
            return [uid.strip() for uid in self.zep_user_ids.split(",") if uid.strip()]
        return self.zep_user_ids
    
    @property
    def default_user_id(self) -> str:
        """Get the default user ID for backwards compatibility."""
        return self.zep_default_user_id


# Create a singleton settings instance
settings = Settings()