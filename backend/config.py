"""
Configuration Settings for WatchFace Code Agent Backend
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # API Configuration
    app_name: str = "vivo BlueOS WatchFace Code Agent API"
    version: str = "2.0.0"
    DEBUG: bool = True
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 10030
    backend_port: int = 10030
    frontend_url: str = "http://10.11.17.19:10031"
    
    # MiniMax-M2 Configuration
    MINIMAX_BASE_URL: str = "https://api.minimaxi.com/v1"
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_MODEL: str = "MiniMax-M2"
    
    # 兼容小写属性名
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_api_key: Optional[str] = None
    minimax_model: str = "MiniMax-M2"
    
    # Agent Configuration
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 10000
    ENABLE_REASONING: bool = True
    default_temperature: float = 0.7
    max_tokens: int = 10000
    enable_reasoning: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:10031", 
        "http://127.0.0.1:10031",
        "http://10.11.17.19:10031",
        "http://10.11.17.19",
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 同步大小写属性
        if self.MINIMAX_API_KEY:
            self.minimax_api_key = self.MINIMAX_API_KEY
        elif self.minimax_api_key:
            self.MINIMAX_API_KEY = self.minimax_api_key
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的字段


# Create global settings instance
settings = Settings()


def validate_settings():
    """Validate required settings"""
    if not settings.minimax_api_key:
        print("⚠️  Warning: MINIMAX_API_KEY not set. Please set it in .env file")
        print("   Get your API key at: https://platform.minimaxi.com/")
    else:
        print("✅ MiniMax-M2 API key configured")


# Validate on import
validate_settings()

