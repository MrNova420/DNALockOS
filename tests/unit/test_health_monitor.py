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
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill
ALL RIGHTS RESERVED.

PROPRIETARY AND CONFIDENTIAL
This is commercial software. Unauthorized copying, modification,
distribution, or use is strictly prohibited.
"""

"""
Tests for Health Monitoring System
"""

import pytest
import time
from datetime import datetime

from server.monitoring.health_monitor import (
    HealthStatus, ComponentType, HealthCheck, SystemHealth,
    HealthChecker, DatabaseHealthChecker, CacheHealthChecker,
    CryptoHealthChecker, BlockchainHealthChecker, ThreatIntelHealthChecker,
    NeuralAuthHealthChecker, SessionHealthChecker, HSMHealthChecker,
    HealthMonitor, get_health, get_readiness, get_liveness
)


class TestHealthStatus:
    """Tests for HealthStatus enum"""
    
    def test_health_statuses_exist(self):
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.CRITICAL.value == "critical"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestComponentType:
    """Tests for ComponentType enum"""
    
    def test_component_types_exist(self):
        assert ComponentType.DATABASE.value == "database"
        assert ComponentType.CACHE.value == "cache"
        assert ComponentType.CRYPTO.value == "crypto"
        assert ComponentType.BLOCKCHAIN.value == "blockchain"


class TestHealthCheck:
    """Tests for HealthCheck dataclass"""
    
    def test_create_health_check(self):
        check = HealthCheck(
            component=ComponentType.DATABASE,
            status=HealthStatus.HEALTHY,
            message="Test message",
            latency_ms=10.5
        )
        assert check.component == ComponentType.DATABASE
        assert check.status == HealthStatus.HEALTHY
        assert check.latency_ms == 10.5
    
    def test_health_check_to_dict(self):
        check = HealthCheck(
            component=ComponentType.CACHE,
            status=HealthStatus.DEGRADED,
            message="Cache is slow",
            latency_ms=100.0,
            details={"hit_rate": 0.5}
        )
        result = check.to_dict()
        assert result["component"] == "cache"
        assert result["status"] == "degraded"
        assert result["latency_ms"] == 100.0
        assert result["details"]["hit_rate"] == 0.5


class TestSystemHealth:
    """Tests for SystemHealth dataclass"""
    
    def test_create_system_health(self):
        checks = [
            HealthCheck(
                component=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                message="OK",
                latency_ms=5.0
            )
        ]
        health = SystemHealth(
            status=HealthStatus.HEALTHY,
            uptime_seconds=3600,
            version="1.0.0",
            environment="test",
            checks=checks
        )
        assert health.status == HealthStatus.HEALTHY
        assert health.uptime_seconds == 3600
    
    def test_system_health_to_dict(self):
        checks = [
            HealthCheck(
                component=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                message="OK",
                latency_ms=5.0
            ),
            HealthCheck(
                component=ComponentType.CACHE,
                status=HealthStatus.DEGRADED,
                message="Slow",
                latency_ms=50.0
            )
        ]
        health = SystemHealth(
            status=HealthStatus.DEGRADED,
            uptime_seconds=7200,
            version="1.0.0",
            environment="test",
            checks=checks
        )
        result = health.to_dict()
        assert result["status"] == "degraded"
        assert result["summary"]["total"] == 2
        assert result["summary"]["healthy"] == 1
        assert result["summary"]["degraded"] == 1


class TestDatabaseHealthChecker:
    """Tests for DatabaseHealthChecker"""
    
    def test_create_checker(self):
        checker = DatabaseHealthChecker()
        assert checker.component == ComponentType.DATABASE
    
    def test_execute_check(self):
        checker = DatabaseHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.DATABASE
        assert result.status == HealthStatus.HEALTHY
        assert result.latency_ms > 0


class TestCacheHealthChecker:
    """Tests for CacheHealthChecker"""
    
    def test_create_checker(self):
        checker = CacheHealthChecker()
        assert checker.component == ComponentType.CACHE
    
    def test_execute_check(self):
        checker = CacheHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.CACHE
        assert result.status == HealthStatus.HEALTHY


class TestCryptoHealthChecker:
    """Tests for CryptoHealthChecker"""
    
    def test_create_checker(self):
        checker = CryptoHealthChecker()
        assert checker.component == ComponentType.CRYPTO
    
    def test_execute_check(self):
        checker = CryptoHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.CRYPTO
        assert result.status == HealthStatus.HEALTHY
        assert "algorithms_available" in result.details


class TestBlockchainHealthChecker:
    """Tests for BlockchainHealthChecker"""
    
    def test_create_checker(self):
        checker = BlockchainHealthChecker()
        assert checker.component == ComponentType.BLOCKCHAIN
    
    def test_execute_check(self):
        checker = BlockchainHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.BLOCKCHAIN
        assert "block_height" in result.details


class TestThreatIntelHealthChecker:
    """Tests for ThreatIntelHealthChecker"""
    
    def test_create_checker(self):
        checker = ThreatIntelHealthChecker()
        assert checker.component == ComponentType.THREAT_INTEL
    
    def test_execute_check(self):
        checker = ThreatIntelHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.THREAT_INTEL
        assert "indicators_loaded" in result.details


class TestNeuralAuthHealthChecker:
    """Tests for NeuralAuthHealthChecker"""
    
    def test_create_checker(self):
        checker = NeuralAuthHealthChecker()
        assert checker.component == ComponentType.NEURAL_AUTH
    
    def test_execute_check(self):
        checker = NeuralAuthHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.NEURAL_AUTH
        assert "model_version" in result.details


class TestSessionHealthChecker:
    """Tests for SessionHealthChecker"""
    
    def test_create_checker(self):
        checker = SessionHealthChecker()
        assert checker.component == ComponentType.SESSION
    
    def test_execute_check(self):
        checker = SessionHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.SESSION
        assert "active_sessions" in result.details


class TestHSMHealthChecker:
    """Tests for HSMHealthChecker"""
    
    def test_create_checker(self):
        checker = HSMHealthChecker()
        assert checker.component == ComponentType.HSM
    
    def test_execute_check(self):
        checker = HSMHealthChecker()
        result = checker.execute()
        assert result.component == ComponentType.HSM
        assert "fips_validated" in result.details


class TestHealthMonitor:
    """Tests for HealthMonitor"""
    
    def test_create_monitor(self):
        monitor = HealthMonitor()
        assert len(monitor.checkers) == 8  # 8 default checkers
    
    def test_check_all(self):
        monitor = HealthMonitor()
        health = monitor.check_all()
        assert isinstance(health, SystemHealth)
        assert len(health.checks) == 8
    
    def test_check_component(self):
        monitor = HealthMonitor()
        result = monitor.check_component(ComponentType.DATABASE)
        assert result is not None
        assert result.component == ComponentType.DATABASE
    
    def test_register_unregister_checker(self):
        monitor = HealthMonitor()
        initial_count = len(monitor.checkers)
        
        # Create a custom checker that properly implements the HealthChecker interface.
        # Custom checkers must override the check() method to return a HealthCheck object.
        # The parent class execute() method handles timing and error tracking.
        class CustomChecker(HealthChecker):
            def __init__(self):
                super().__init__(ComponentType.QUEUE)
            
            def check(self) -> HealthCheck:
                """
                Perform the actual health check for this component.
                This method is called by the parent execute() method.
                """
                return HealthCheck(
                    component=self.component,
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    latency_ms=1.0
                )
        
        # Register
        monitor.register_checker(CustomChecker())
        assert len(monitor.checkers) == initial_count + 1
        
        # Unregister
        monitor.unregister_checker(ComponentType.QUEUE)
        assert len(monitor.checkers) == initial_count
    
    def test_get_uptime(self):
        monitor = HealthMonitor()
        time.sleep(0.1)  # Wait a bit
        uptime = monitor.get_uptime()
        assert uptime >= 0.1
    
    def test_get_readiness(self):
        monitor = HealthMonitor()
        result = monitor.get_readiness()
        assert "ready" in result
        assert "status" in result
        assert "critical_components" in result
    
    def test_get_liveness(self):
        monitor = HealthMonitor()
        result = monitor.get_liveness()
        assert result["alive"] is True
        assert "uptime_seconds" in result


class TestModuleFunctions:
    """Tests for module-level functions"""
    
    def test_get_health(self):
        health = get_health()
        assert isinstance(health, SystemHealth)
    
    def test_get_readiness(self):
        result = get_readiness()
        assert "ready" in result
    
    def test_get_liveness(self):
        result = get_liveness()
        assert result["alive"] is True
