"""
Application configuration
"""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-not-for-production")
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///familyplanner.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.environ.get("ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Security
    REMEMBER_COOKIE_SECURE = os.environ.get("ENV") == "production"
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Registration
    REGISTRATION_ENABLED = True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SECRET_KEY = "dev-secret-key"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    REGISTRATION_ENABLED = True  # Enable registration for tests
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    pass


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get("ENV", "development").lower()
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    return config_map.get(env, DevelopmentConfig)
