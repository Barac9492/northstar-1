"""
Configuration Management
Centralized settings with environment-based configuration
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import secrets


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "northstar"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    ssl_mode: str = "prefer"
    
    @property
    def url(self) -> str:
        """Get database URL"""
        if self.password:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
        return f"postgresql://{self.username}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    pool_size: int = 10
    
    @property
    def url(self) -> str:
        """Get Redis URL"""
        protocol = "rediss" if self.ssl else "redis"
        auth = f":{self.password}@" if self.password else ""
        return f"{protocol}://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class AIConfig:
    """AI service configuration"""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class AuthConfig:
    """Authentication configuration"""
    secret_key: str = field(default_factory=lambda: secrets.token_hex(32))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    session_timeout_hours: int = 24


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    default_per_minute: int = 60
    default_per_hour: int = 1000
    default_per_day: int = 10000
    
    # Tier-specific limits
    free_tier_per_hour: int = 10
    pro_tier_per_hour: int = 1000
    enterprise_tier_per_hour: int = 10000
    
    # API endpoint specific
    content_generation_per_hour: int = 100
    engagement_per_day: int = 500


@dataclass
class SocialMediaConfig:
    """Social media API configuration"""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    
    instagram_access_token: str = ""
    instagram_business_id: str = ""
    
    linkedin_access_token: str = ""
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    
    facebook_access_token: str = ""
    facebook_app_id: str = ""
    facebook_app_secret: str = ""


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    sentry_dsn: str = ""
    datadog_api_key: str = ""
    prometheus_enabled: bool = True
    prometheus_port: int = 8000
    log_level: str = "INFO"
    log_format: str = "json"
    health_check_interval: int = 30


@dataclass
class StorageConfig:
    """File storage configuration"""
    provider: str = "local"  # local, s3, gcs
    local_path: str = "./uploads"
    
    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "us-east-1"
    
    # Google Cloud Storage
    gcp_project_id: str = ""
    gcp_bucket_name: str = ""
    gcp_credentials_path: str = ""


@dataclass
class EmailConfig:
    """Email service configuration"""
    provider: str = "smtp"  # smtp, sendgrid, ses
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    
    from_email: str = "noreply@northstar.ai"
    from_name: str = "NorthStar AI"
    
    # SendGrid
    sendgrid_api_key: str = ""
    
    # AWS SES
    aws_ses_region: str = "us-east-1"


class Settings:
    """Application settings"""
    
    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug = self.environment == Environment.DEVELOPMENT
        self.testing = self.environment == Environment.TESTING
        
        # Core settings
        self.app_name = "NorthStar AI"
        self.app_version = "1.0.0"
        self.api_prefix = "/api/v1"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))
        
        # Component configurations
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.ai = self._load_ai_config()
        self.auth = self._load_auth_config()
        self.rate_limit = self._load_rate_limit_config()
        self.social_media = self._load_social_media_config()
        self.monitoring = self._load_monitoring_config()
        self.storage = self._load_storage_config()
        self.email = self._load_email_config()
        
        # Feature flags
        self.features = self._load_feature_flags()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment"""
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            name=os.getenv("DB_NAME", "northstar"),
            username=os.getenv("DB_USERNAME", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            pool_size=int(os.getenv("DB_POOL_SIZE", 10)),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 20)),
            ssl_mode=os.getenv("DB_SSL_MODE", "prefer")
        )
    
    def _load_redis_config(self) -> RedisConfig:
        """Load Redis configuration from environment"""
        return RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
            pool_size=int(os.getenv("REDIS_POOL_SIZE", 10))
        )
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration from environment"""
        return AIConfig(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            default_model=os.getenv("AI_DEFAULT_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", 1000)),
            temperature=float(os.getenv("AI_TEMPERATURE", 0.7)),
            timeout=int(os.getenv("AI_TIMEOUT", 30)),
            retry_attempts=int(os.getenv("AI_RETRY_ATTEMPTS", 3))
        )
    
    def _load_auth_config(self) -> AuthConfig:
        """Load authentication configuration from environment"""
        return AuthConfig(
            secret_key=os.getenv("SECRET_KEY", secrets.token_hex(32)),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", 8))
        )
    
    def _load_rate_limit_config(self) -> RateLimitConfig:
        """Load rate limiting configuration from environment"""
        return RateLimitConfig(
            default_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", 60)),
            default_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", 1000)),
            free_tier_per_hour=int(os.getenv("FREE_TIER_RATE_LIMIT", 10)),
            pro_tier_per_hour=int(os.getenv("PRO_TIER_RATE_LIMIT", 1000)),
            enterprise_tier_per_hour=int(os.getenv("ENTERPRISE_TIER_RATE_LIMIT", 10000))
        )
    
    def _load_social_media_config(self) -> SocialMediaConfig:
        """Load social media API configuration from environment"""
        return SocialMediaConfig(
            twitter_api_key=os.getenv("TWITTER_API_KEY", ""),
            twitter_api_secret=os.getenv("TWITTER_API_SECRET", ""),
            twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
            twitter_access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
            
            instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
            instagram_business_id=os.getenv("INSTAGRAM_BUSINESS_ID", ""),
            
            linkedin_access_token=os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
            linkedin_client_id=os.getenv("LINKEDIN_CLIENT_ID", ""),
            linkedin_client_secret=os.getenv("LINKEDIN_CLIENT_SECRET", ""),
            
            facebook_access_token=os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
            facebook_app_id=os.getenv("FACEBOOK_APP_ID", ""),
            facebook_app_secret=os.getenv("FACEBOOK_APP_SECRET", "")
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        """Load monitoring configuration from environment"""
        return MonitoringConfig(
            sentry_dsn=os.getenv("SENTRY_DSN", ""),
            datadog_api_key=os.getenv("DATADOG_API_KEY", ""),
            prometheus_enabled=os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true",
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", 8000)),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json")
        )
    
    def _load_storage_config(self) -> StorageConfig:
        """Load storage configuration from environment"""
        return StorageConfig(
            provider=os.getenv("STORAGE_PROVIDER", "local"),
            local_path=os.getenv("STORAGE_LOCAL_PATH", "./uploads"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            aws_bucket_name=os.getenv("AWS_BUCKET_NAME", ""),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            gcp_project_id=os.getenv("GCP_PROJECT_ID", ""),
            gcp_bucket_name=os.getenv("GCP_BUCKET_NAME", ""),
            gcp_credentials_path=os.getenv("GCP_CREDENTIALS_PATH", "")
        )
    
    def _load_email_config(self) -> EmailConfig:
        """Load email configuration from environment"""
        return EmailConfig(
            provider=os.getenv("EMAIL_PROVIDER", "smtp"),
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            from_email=os.getenv("FROM_EMAIL", "noreply@northstar.ai"),
            from_name=os.getenv("FROM_NAME", "NorthStar AI"),
            sendgrid_api_key=os.getenv("SENDGRID_API_KEY", ""),
            aws_ses_region=os.getenv("AWS_SES_REGION", "us-east-1")
        )
    
    def _load_feature_flags(self) -> Dict[str, bool]:
        """Load feature flags from environment"""
        return {
            "content_generation": os.getenv("FEATURE_CONTENT_GENERATION", "true").lower() == "true",
            "auto_engagement": os.getenv("FEATURE_AUTO_ENGAGEMENT", "true").lower() == "true",
            "analytics": os.getenv("FEATURE_ANALYTICS", "true").lower() == "true",
            "scheduling": os.getenv("FEATURE_SCHEDULING", "true").lower() == "true",
            "social_listening": os.getenv("FEATURE_SOCIAL_LISTENING", "false").lower() == "true",
            "competitor_analysis": os.getenv("FEATURE_COMPETITOR_ANALYSIS", "false").lower() == "true",
            "white_label": os.getenv("FEATURE_WHITE_LABEL", "false").lower() == "true"
        }
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.environment == Environment.TESTING
    
    def get_cors_origins(self) -> list:
        """Get CORS allowed origins based on environment"""
        if self.is_production():
            return [
                "https://northstar.ai",
                "https://app.northstar.ai",
                "https://dashboard.northstar.ai"
            ]
        elif self.is_development():
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8501",
                "http://localhost:8502",
                "http://localhost:8503",
                "http://localhost:8504",
                "http://localhost:8505"
            ]
        else:
            return ["*"]


# Global settings instance
settings = Settings()