"""
DNALockOS - Production Configuration
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill
ALL RIGHTS RESERVED.

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, modification, or distribution is strictly prohibited.

Production-ready configuration for enterprise, industry, and military deployment.
"""

import os
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DeploymentEnvironment(str, Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    MILITARY = "military"  # Highest security settings


class SecurityClassification(str, Enum):
    """Security classification levels."""
    UNCLASSIFIED = "unclassified"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    TOP_SECRET_SCI = "top_secret_sci"


@dataclass
class DatabaseConfig:
    """Database configuration for production deployment."""
    host: str = "localhost"
    port: int = 5432
    database: str = "dnalockos"
    username: str = "dnalockos"
    password: str = ""
    ssl_mode: str = "require"
    ssl_ca_cert: Optional[str] = None
    ssl_client_cert: Optional[str] = None
    ssl_client_key: Optional[str] = None
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    def get_connection_url(self) -> str:
        """Get SQLAlchemy connection URL."""
        ssl_params = f"?sslmode={self.ssl_mode}"
        if self.ssl_ca_cert:
            ssl_params += f"&sslrootcert={self.ssl_ca_cert}"
        if self.ssl_client_cert:
            ssl_params += f"&sslcert={self.ssl_client_cert}"
        if self.ssl_client_key:
            ssl_params += f"&sslkey={self.ssl_client_key}"
        
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}{ssl_params}"


@dataclass
class RedisConfig:
    """Redis configuration for caching and session storage."""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    ssl: bool = True
    ssl_ca_cert: Optional[str] = None
    max_connections: int = 50
    socket_timeout: int = 5
    retry_on_timeout: bool = True


@dataclass
class CryptographyConfig:
    """Cryptography configuration for security operations."""
    # Key derivation
    argon2_time_cost: int = 4
    argon2_memory_cost: int = 65536  # 64 MB
    argon2_parallelism: int = 4
    argon2_hash_len: int = 64
    
    # Encryption
    aes_key_size: int = 256
    
    # Signatures
    signature_algorithm: str = "Ed25519"
    
    # Hashing
    hash_algorithm: str = "SHA3-512"
    
    # Key rotation
    key_rotation_days: int = 90
    
    # Random generation
    entropy_pool_size: int = 4096


@dataclass
class AuthenticationConfig:
    """Authentication system configuration."""
    # Challenge settings
    challenge_size: int = 32
    challenge_expiry_seconds: int = 60
    max_active_challenges: int = 5
    
    # Session settings
    session_token_size: int = 64
    session_expiry_hours: int = 24
    session_max_idle_minutes: int = 30
    
    # Rate limiting
    max_auth_attempts_per_minute: int = 10
    lockout_duration_minutes: int = 15
    max_lockout_count: int = 5
    
    # Multi-factor
    mfa_code_length: int = 6
    mfa_code_expiry_seconds: int = 300
    
    # Biometric
    biometric_match_threshold: float = 0.95


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    keepalive: int = 5
    
    # CORS
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 20
    
    # Request limits
    max_request_size_mb: int = 10
    max_upload_size_mb: int = 50


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 10
    
    # Audit logging
    audit_enabled: bool = True
    audit_file_path: Optional[str] = None
    audit_retention_days: int = 365
    
    # Security logging
    security_log_enabled: bool = True
    security_log_path: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security hardening configuration."""
    # Anti-tampering
    integrity_check_enabled: bool = True
    integrity_check_interval_seconds: int = 300
    
    # Anti-debugging
    anti_debug_enabled: bool = True
    
    # Memory protection
    secure_memory_enabled: bool = True
    memory_encryption_enabled: bool = False
    
    # Network security
    tls_minimum_version: str = "TLSv1.3"
    certificate_pinning_enabled: bool = True
    
    # Input validation
    input_sanitization_enabled: bool = True
    max_input_length: int = 10000
    
    # Output encoding
    output_encoding_enabled: bool = True


@dataclass
class ProductionConfig:
    """
    Complete production configuration for DNALockOS.
    
    This configuration is designed for enterprise, industry, and military deployment
    with the highest security standards.
    """
    environment: DeploymentEnvironment = DeploymentEnvironment.PRODUCTION
    classification: SecurityClassification = SecurityClassification.CONFIDENTIAL
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    cryptography: CryptographyConfig = field(default_factory=CryptographyConfig)
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Application metadata
    app_name: str = "DNALockOS"
    app_version: str = "1.0.0"
    
    # Copyright
    copyright_owner: str = "WeNova Interactive"
    legal_name: str = "Kayden Shawn Massengill"
    
    def __post_init__(self):
        """Apply environment-specific overrides."""
        if self.environment == DeploymentEnvironment.MILITARY:
            self._apply_military_hardening()
        elif self.environment == DeploymentEnvironment.PRODUCTION:
            self._apply_production_hardening()
    
    def _apply_military_hardening(self):
        """Apply military-grade security settings."""
        # Maximum cryptographic strength
        self.cryptography.argon2_time_cost = 8
        self.cryptography.argon2_memory_cost = 131072  # 128 MB
        self.cryptography.argon2_parallelism = 8
        
        # Strict authentication
        self.authentication.challenge_expiry_seconds = 30
        self.authentication.session_expiry_hours = 8
        self.authentication.session_max_idle_minutes = 15
        self.authentication.max_auth_attempts_per_minute = 5
        self.authentication.lockout_duration_minutes = 60
        
        # Maximum security
        self.security.anti_debug_enabled = True
        self.security.memory_encryption_enabled = True
        self.security.integrity_check_interval_seconds = 60
        
        # API hardening
        self.api.rate_limit_per_minute = 30
        self.api.cors_origins = []  # No CORS in military
        
        # Enhanced logging
        self.logging.audit_retention_days = 730  # 2 years
    
    def _apply_production_hardening(self):
        """Apply production-grade security settings."""
        # Strong cryptographic settings
        self.cryptography.argon2_time_cost = 4
        self.cryptography.argon2_memory_cost = 65536  # 64 MB
        
        # Secure authentication
        self.authentication.challenge_expiry_seconds = 60
        self.authentication.session_expiry_hours = 24
        self.authentication.session_max_idle_minutes = 30
        
        # Security enabled
        self.security.anti_debug_enabled = True
        self.security.integrity_check_enabled = True
        
        # API security
        self.api.rate_limit_per_minute = 100
    
    @classmethod
    def from_environment(cls) -> "ProductionConfig":
        """Load configuration from environment variables."""
        env = os.getenv("DNALOCKOS_ENV", "production").lower()
        environment = DeploymentEnvironment(env) if env in [e.value for e in DeploymentEnvironment] else DeploymentEnvironment.PRODUCTION
        
        config = cls(environment=environment)
        
        # Database from environment
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", str(config.database.port)))
        config.database.database = os.getenv("DB_NAME", config.database.database)
        config.database.username = os.getenv("DB_USER", config.database.username)
        config.database.password = os.getenv("DB_PASSWORD", config.database.password)
        
        # Redis from environment
        config.redis.host = os.getenv("REDIS_HOST", config.redis.host)
        config.redis.port = int(os.getenv("REDIS_PORT", str(config.redis.port)))
        config.redis.password = os.getenv("REDIS_PASSWORD", config.redis.password)
        
        # API from environment
        config.api.host = os.getenv("API_HOST", config.api.host)
        config.api.port = int(os.getenv("API_PORT", str(config.api.port)))
        config.api.workers = int(os.getenv("API_WORKERS", str(config.api.workers)))
        
        return config
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Database validation
        if not self.database.password and self.environment in [DeploymentEnvironment.PRODUCTION, DeploymentEnvironment.MILITARY]:
            issues.append("Database password required for production/military deployment")
        
        # Redis validation
        if not self.redis.password and self.environment in [DeploymentEnvironment.PRODUCTION, DeploymentEnvironment.MILITARY]:
            issues.append("Redis password required for production/military deployment")
        
        # Security validation
        if not self.security.anti_debug_enabled and self.environment == DeploymentEnvironment.MILITARY:
            issues.append("Anti-debugging must be enabled for military deployment")
        
        if not self.security.integrity_check_enabled and self.environment in [DeploymentEnvironment.PRODUCTION, DeploymentEnvironment.MILITARY]:
            issues.append("Integrity checking required for production/military deployment")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (for serialization)."""
        return {
            "environment": self.environment.value,
            "classification": self.classification.value,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "copyright_owner": self.copyright_owner,
            "legal_name": self.legal_name,
            # Note: Sensitive config values are not included
        }


# Global configuration instance
_config: Optional[ProductionConfig] = None


def get_config() -> ProductionConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = ProductionConfig.from_environment()
    return _config


def set_config(config: ProductionConfig):
    """Set the global configuration instance."""
    global _config
    _config = config
