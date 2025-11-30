"""
==============================================================================
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
==============================================================================

OWNERSHIP AND LEGAL NOTICE:

This software and all associated intellectual property is the exclusive
property of WeNova Interactive, legally owned and operated by:

    Kayden Shawn Massengill

COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE

This is proprietary commercial software. It is NOT free software. It is NOT
open source software. This software is developed for commercial sale and
requires a valid commercial license for ANY use.

STRICT PROHIBITION NOTICE:

Without a valid commercial license agreement, you are PROHIBITED from:
  * Using this software for any purpose
  * Copying, reproducing, or duplicating this software
  * Modifying, adapting, or creating derivative works
  * Distributing, publishing, or transferring this software
  * Reverse engineering, decompiling, or disassembling this software
  * Sublicensing or permitting any third-party access

LEGAL ENFORCEMENT:

Unauthorized use, reproduction, or distribution of this software, or any
portion thereof, may result in severe civil and criminal penalties, and
will be prosecuted to the maximum extent possible under applicable law.

For licensing inquiries: WeNova Interactive
==============================================================================
"""

"""
DNALockOS - Production Configuration
Enterprise-grade configuration for military/government deployment
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    GOVERNMENT = "government"
    MILITARY = "military"


class SecurityMode(Enum):
    """Security operation modes"""
    STANDARD = "standard"
    ENHANCED = "enhanced"
    HIGH_ASSURANCE = "high_assurance"
    CLASSIFIED = "classified"
    TOP_SECRET = "top_secret"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "dnalock"
    username: str = "dnalock"
    password: Optional[str] = None  # Must be set via environment variable
    ssl_mode: str = "require"
    connection_pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # High availability
    read_replicas: list = field(default_factory=list)
    failover_timeout: int = 30
    health_check_interval: int = 10
    
    def validate(self) -> None:
        """Validate that required configuration is present"""
        if self.password is None:
            raise ValueError("Database password must be set via DB_PASSWORD environment variable")


@dataclass
class RedisConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None  # Should be set via environment variable for production
    database: int = 0
    ssl: bool = True
    connection_pool_size: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    # Cluster mode
    cluster_mode: bool = False
    cluster_nodes: list = field(default_factory=list)


@dataclass
class SecurityConfig:
    """Security configuration"""
    # Encryption
    encryption_algorithm: str = "AES-256-GCM"
    key_derivation: str = "Argon2id"
    hash_algorithm: str = "SHA3-512"
    
    # Post-quantum cryptography
    quantum_safe_enabled: bool = True
    kem_algorithm: str = "ML-KEM-1024"
    signature_algorithm: str = "ML-DSA-87"
    hash_based_signature: str = "SLH-DSA-SHAKE-256f"
    
    # DNA strand configuration
    default_security_level: str = "ULTIMATE"
    min_segment_count: int = 1048576
    verification_barriers: int = 24
    
    # Session management
    session_timeout: int = 3600
    max_concurrent_sessions: int = 3
    session_rotation_interval: int = 900
    
    # Authentication
    max_auth_attempts: int = 5
    lockout_duration: int = 900
    require_biometric: bool = True
    require_hardware_binding: bool = True
    
    # Threat intelligence
    threat_intel_enabled: bool = True
    ip_reputation_enabled: bool = True
    behavioral_analysis_enabled: bool = True
    
    # Compliance
    fips_mode: bool = True
    common_criteria_mode: bool = True
    audit_logging: bool = True


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 60
    keepalive: int = 5
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 60
    
    # CORS
    cors_enabled: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])
    cors_methods: list = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    
    # TLS
    tls_enabled: bool = True
    tls_cert_file: str = "/etc/dnalock/certs/server.crt"
    tls_key_file: str = "/etc/dnalock/certs/server.key"
    tls_min_version: str = "TLSv1.3"
    
    # Monitoring
    metrics_enabled: bool = True
    metrics_port: int = 9090
    health_check_path: str = "/health"


@dataclass
class BlockchainConfig:
    """Distributed ledger configuration"""
    enabled: bool = True
    network: str = "private"
    node_url: str = "http://localhost:8545"
    contract_address: str = ""
    
    # Consensus
    consensus_algorithm: str = "PoA"
    block_time: int = 5
    confirmations_required: int = 3
    
    # Gas settings
    max_gas_price: int = 100000000000
    gas_limit: int = 8000000


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    # Metrics
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # Tracing
    tracing_enabled: bool = True
    tracing_endpoint: str = "http://localhost:14268/api/traces"
    tracing_sample_rate: float = 0.1
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_output: str = "stdout"
    audit_log_file: str = "/var/log/dnalock/audit.log"
    
    # Alerting
    alerting_enabled: bool = True
    alert_webhook_url: str = ""
    alert_email: str = ""


@dataclass
class HSMConfig:
    """Hardware Security Module configuration"""
    enabled: bool = True
    provider: str = "pkcs11"
    library_path: str = "/usr/lib/softhsm/libsofthsm2.so"
    slot: int = 0
    pin: Optional[str] = None  # Must be set via environment variable
    
    # Key management
    master_key_label: str = "dnalock-master"
    key_rotation_days: int = 365
    backup_enabled: bool = True
    
    def validate(self) -> None:
        """Validate that required configuration is present"""
        if self.enabled and self.pin is None:
            raise ValueError("HSM PIN must be set via HSM_PIN environment variable when HSM is enabled")


@dataclass
class ProductionConfig:
    """Complete production configuration"""
    environment: Environment = Environment.PRODUCTION
    security_mode: SecurityMode = SecurityMode.HIGH_ASSURANCE
    
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    api: APIConfig = field(default_factory=APIConfig)
    blockchain: BlockchainConfig = field(default_factory=BlockchainConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    hsm: HSMConfig = field(default_factory=HSMConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        def convert(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: convert(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, list):
                return [convert(item) for item in obj]
            else:
                return obj
        return convert(self)
    
    def to_json(self) -> str:
        """Convert configuration to JSON"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_environment(cls) -> "ProductionConfig":
        """Load configuration from environment variables"""
        config = cls()
        
        # Environment
        env = os.getenv("DNALOCK_ENVIRONMENT", "production")
        config.environment = Environment(env)
        
        # Security mode
        mode = os.getenv("DNALOCK_SECURITY_MODE", "high_assurance")
        config.security_mode = SecurityMode(mode)
        
        # Database
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", config.database.port))
        config.database.database = os.getenv("DB_NAME", config.database.database)
        config.database.username = os.getenv("DB_USER", config.database.username)
        config.database.password = os.getenv("DB_PASSWORD", "")
        
        # Redis
        config.redis.host = os.getenv("REDIS_HOST", config.redis.host)
        config.redis.port = int(os.getenv("REDIS_PORT", config.redis.port))
        config.redis.password = os.getenv("REDIS_PASSWORD", "")
        
        # API
        config.api.host = os.getenv("API_HOST", config.api.host)
        config.api.port = int(os.getenv("API_PORT", config.api.port))
        config.api.workers = int(os.getenv("API_WORKERS", config.api.workers))
        
        # HSM
        config.hsm.enabled = os.getenv("HSM_ENABLED", "true").lower() == "true"
        config.hsm.pin = os.getenv("HSM_PIN", "")
        
        # Monitoring
        config.monitoring.log_level = os.getenv("LOG_LEVEL", config.monitoring.log_level)
        config.monitoring.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL", "")
        
        return config


# Pre-configured profiles for different deployment scenarios
DEVELOPMENT_CONFIG = ProductionConfig(
    environment=Environment.DEVELOPMENT,
    security_mode=SecurityMode.STANDARD,
)
DEVELOPMENT_CONFIG.security.fips_mode = False
DEVELOPMENT_CONFIG.security.require_hardware_binding = False
DEVELOPMENT_CONFIG.hsm.enabled = False
DEVELOPMENT_CONFIG.api.tls_enabled = False

STAGING_CONFIG = ProductionConfig(
    environment=Environment.STAGING,
    security_mode=SecurityMode.ENHANCED,
)
STAGING_CONFIG.security.fips_mode = True
STAGING_CONFIG.monitoring.log_level = "DEBUG"

PRODUCTION_CONFIG = ProductionConfig(
    environment=Environment.PRODUCTION,
    security_mode=SecurityMode.HIGH_ASSURANCE,
)

GOVERNMENT_CONFIG = ProductionConfig(
    environment=Environment.GOVERNMENT,
    security_mode=SecurityMode.CLASSIFIED,
)
GOVERNMENT_CONFIG.security.verification_barriers = 24
GOVERNMENT_CONFIG.security.default_security_level = "ULTIMATE"
GOVERNMENT_CONFIG.blockchain.consensus_algorithm = "PBFT"

MILITARY_CONFIG = ProductionConfig(
    environment=Environment.MILITARY,
    security_mode=SecurityMode.TOP_SECRET,
)
MILITARY_CONFIG.security.verification_barriers = 24
MILITARY_CONFIG.security.default_security_level = "ULTIMATE"
MILITARY_CONFIG.security.require_biometric = True
MILITARY_CONFIG.security.require_hardware_binding = True
MILITARY_CONFIG.hsm.enabled = True
MILITARY_CONFIG.blockchain.enabled = True


def get_config(environment: str = None) -> ProductionConfig:
    """Get configuration for specified environment"""
    if environment is None:
        environment = os.getenv("DNALOCK_ENVIRONMENT", "production")
    
    configs = {
        "development": DEVELOPMENT_CONFIG,
        "staging": STAGING_CONFIG,
        "production": PRODUCTION_CONFIG,
        "government": GOVERNMENT_CONFIG,
        "military": MILITARY_CONFIG,
    }
    
    return configs.get(environment, PRODUCTION_CONFIG)


# Export default configuration
config = get_config()
