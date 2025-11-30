"""
Tests for Production Configuration
"""

import pytest
import os

from server.config.production_config import (
    Environment, SecurityMode, DatabaseConfig, RedisConfig,
    SecurityConfig, APIConfig, BlockchainConfig, MonitoringConfig,
    HSMConfig, ProductionConfig, get_config,
    DEVELOPMENT_CONFIG, STAGING_CONFIG, PRODUCTION_CONFIG,
    GOVERNMENT_CONFIG, MILITARY_CONFIG
)


class TestEnvironment:
    """Tests for Environment enum"""
    
    def test_environments_exist(self):
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.GOVERNMENT.value == "government"
        assert Environment.MILITARY.value == "military"


class TestSecurityMode:
    """Tests for SecurityMode enum"""
    
    def test_security_modes_exist(self):
        assert SecurityMode.STANDARD.value == "standard"
        assert SecurityMode.ENHANCED.value == "enhanced"
        assert SecurityMode.HIGH_ASSURANCE.value == "high_assurance"
        assert SecurityMode.CLASSIFIED.value == "classified"
        assert SecurityMode.TOP_SECRET.value == "top_secret"


class TestDatabaseConfig:
    """Tests for DatabaseConfig"""
    
    def test_default_values(self):
        config = DatabaseConfig()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "dnalock"
        assert config.ssl_mode == "require"
        assert config.connection_pool_size == 20


class TestRedisConfig:
    """Tests for RedisConfig"""
    
    def test_default_values(self):
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.ssl is True
        assert config.connection_pool_size == 50


class TestSecurityConfig:
    """Tests for SecurityConfig"""
    
    def test_default_values(self):
        config = SecurityConfig()
        assert config.encryption_algorithm == "AES-256-GCM"
        assert config.key_derivation == "Argon2id"
        assert config.quantum_safe_enabled is True
        assert config.verification_barriers == 24
        assert config.fips_mode is True
    
    def test_quantum_algorithms(self):
        config = SecurityConfig()
        assert config.kem_algorithm == "ML-KEM-1024"
        assert config.signature_algorithm == "ML-DSA-87"
        assert config.hash_based_signature == "SLH-DSA-SHAKE-256f"


class TestAPIConfig:
    """Tests for APIConfig"""
    
    def test_default_values(self):
        config = APIConfig()
        assert config.port == 8000
        assert config.workers == 4
        assert config.rate_limit_enabled is True
        assert config.tls_enabled is True
        assert config.tls_min_version == "TLSv1.3"


class TestBlockchainConfig:
    """Tests for BlockchainConfig"""
    
    def test_default_values(self):
        config = BlockchainConfig()
        assert config.enabled is True
        assert config.network == "private"
        assert config.consensus_algorithm == "PoA"
        assert config.confirmations_required == 3


class TestMonitoringConfig:
    """Tests for MonitoringConfig"""
    
    def test_default_values(self):
        config = MonitoringConfig()
        assert config.prometheus_enabled is True
        assert config.tracing_enabled is True
        assert config.log_level == "INFO"
        assert config.log_format == "json"


class TestHSMConfig:
    """Tests for HSMConfig"""
    
    def test_default_values(self):
        config = HSMConfig()
        assert config.enabled is True
        assert config.provider == "pkcs11"
        assert config.key_rotation_days == 365
        assert config.backup_enabled is True


class TestProductionConfig:
    """Tests for ProductionConfig"""
    
    def test_create_default_config(self):
        config = ProductionConfig()
        assert config.environment == Environment.PRODUCTION
        assert config.security_mode == SecurityMode.HIGH_ASSURANCE
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.security, SecurityConfig)
    
    def test_to_dict(self):
        config = ProductionConfig()
        result = config.to_dict()
        assert isinstance(result, dict)
        assert result["environment"] == "production"
        assert result["security_mode"] == "high_assurance"
        assert "database" in result
        assert "security" in result
    
    def test_to_json(self):
        config = ProductionConfig()
        result = config.to_json()
        assert isinstance(result, str)
        assert "production" in result


class TestPreConfiguredProfiles:
    """Tests for pre-configured profiles"""
    
    def test_development_config(self):
        assert DEVELOPMENT_CONFIG.environment == Environment.DEVELOPMENT
        assert DEVELOPMENT_CONFIG.security_mode == SecurityMode.STANDARD
        assert DEVELOPMENT_CONFIG.security.fips_mode is False
        assert DEVELOPMENT_CONFIG.hsm.enabled is False
    
    def test_staging_config(self):
        assert STAGING_CONFIG.environment == Environment.STAGING
        assert STAGING_CONFIG.security_mode == SecurityMode.ENHANCED
        assert STAGING_CONFIG.security.fips_mode is True
    
    def test_production_config(self):
        assert PRODUCTION_CONFIG.environment == Environment.PRODUCTION
        assert PRODUCTION_CONFIG.security_mode == SecurityMode.HIGH_ASSURANCE
    
    def test_government_config(self):
        assert GOVERNMENT_CONFIG.environment == Environment.GOVERNMENT
        assert GOVERNMENT_CONFIG.security_mode == SecurityMode.CLASSIFIED
        assert GOVERNMENT_CONFIG.security.verification_barriers == 24
    
    def test_military_config(self):
        assert MILITARY_CONFIG.environment == Environment.MILITARY
        assert MILITARY_CONFIG.security_mode == SecurityMode.TOP_SECRET
        assert MILITARY_CONFIG.security.require_biometric is True
        assert MILITARY_CONFIG.security.require_hardware_binding is True
        assert MILITARY_CONFIG.hsm.enabled is True


class TestGetConfig:
    """Tests for get_config function"""
    
    def test_get_development_config(self):
        config = get_config("development")
        assert config.environment == Environment.DEVELOPMENT
    
    def test_get_production_config(self):
        config = get_config("production")
        assert config.environment == Environment.PRODUCTION
    
    def test_get_military_config(self):
        config = get_config("military")
        assert config.environment == Environment.MILITARY
    
    def test_get_default_config(self):
        config = get_config("unknown")
        assert config.environment == Environment.PRODUCTION
