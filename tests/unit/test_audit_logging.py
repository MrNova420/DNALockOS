"""
Tests for Audit Logging Module.

Tests the enterprise-grade audit logging system including:
- Event logging
- Event categorization
- Query capabilities
- Compliance reporting
- Integrity verification
"""

import time
from datetime import datetime, timedelta, timezone

import pytest

from server.security.audit_logging import (
    AuditEvent,
    AuditEventCategory,
    AuditEventType,
    AuditLogger,
    AuditLogStorage,
    AuditSeverity,
)


class TestAuditEventCategory:
    """Test audit event category enumeration."""
    
    def test_categories_exist(self):
        """Test all categories exist."""
        assert AuditEventCategory.AUTHENTICATION.value == "authentication"
        assert AuditEventCategory.AUTHORIZATION.value == "authorization"
        assert AuditEventCategory.KEY_MANAGEMENT.value == "key_management"
        assert AuditEventCategory.SESSION.value == "session"
        assert AuditEventCategory.SECURITY.value == "security"
        assert AuditEventCategory.ADMINISTRATIVE.value == "administrative"
        assert AuditEventCategory.SYSTEM.value == "system"


class TestAuditEventType:
    """Test audit event type enumeration."""
    
    def test_auth_event_types(self):
        """Test authentication event types."""
        assert AuditEventType.AUTH_ATTEMPT.value == "auth_attempt"
        assert AuditEventType.AUTH_SUCCESS.value == "auth_success"
        assert AuditEventType.AUTH_FAILURE.value == "auth_failure"
        assert AuditEventType.MFA_CHALLENGE.value == "mfa_challenge"
    
    def test_key_event_types(self):
        """Test key management event types."""
        assert AuditEventType.KEY_CREATED.value == "key_created"
        assert AuditEventType.KEY_REVOKED.value == "key_revoked"
        assert AuditEventType.KEY_EXPIRED.value == "key_expired"
    
    def test_security_event_types(self):
        """Test security event types."""
        assert AuditEventType.THREAT_DETECTED.value == "threat_detected"
        assert AuditEventType.ATTACK_BLOCKED.value == "attack_blocked"
        assert AuditEventType.ANOMALY_DETECTED.value == "anomaly_detected"


class TestAuditSeverity:
    """Test audit severity enumeration."""
    
    def test_severities_exist(self):
        """Test all severities exist."""
        assert AuditSeverity.DEBUG.value == "debug"
        assert AuditSeverity.INFO.value == "info"
        assert AuditSeverity.WARNING.value == "warning"
        assert AuditSeverity.ERROR.value == "error"
        assert AuditSeverity.CRITICAL.value == "critical"


class TestAuditEvent:
    """Test audit event class."""
    
    def test_create_event(self):
        """Test creating an audit event."""
        event = AuditEvent(
            event_id="evt_123",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc),
            actor_id="user_456",
            action="authenticate",
            outcome="success"
        )
        
        assert event.event_id == "evt_123"
        assert event.event_type == AuditEventType.AUTH_SUCCESS
        assert event.actor_id == "user_456"
        assert event.outcome == "success"
    
    def test_event_hash_computed(self):
        """Test event hash is computed."""
        event = AuditEvent(
            event_id="evt_123",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc)
        )
        
        assert len(event.event_hash) == 64
    
    def test_verify_integrity(self):
        """Test event integrity verification."""
        event = AuditEvent(
            event_id="evt_123",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc)
        )
        
        assert event.verify_integrity() is True
        
        # Tamper with event
        event.action = "tampered"
        assert event.verify_integrity() is False
    
    def test_event_to_dict(self):
        """Test event serialization."""
        event = AuditEvent(
            event_id="evt_123",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc),
            actor_id="user_456"
        )
        
        result = event.to_dict()
        
        assert result["event_id"] == "evt_123"
        assert result["event_type"] == "auth_success"
        assert result["category"] == "authentication"
        assert result["actor_id"] == "user_456"
    
    def test_event_to_json(self):
        """Test event JSON serialization."""
        event = AuditEvent(
            event_id="evt_123",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc)
        )
        
        json_str = event.to_json()
        
        assert isinstance(json_str, str)
        assert "evt_123" in json_str


class TestAuditLogStorage:
    """Test audit log storage."""
    
    def test_create_storage(self):
        """Test creating storage."""
        storage = AuditLogStorage()
        
        assert storage is not None
    
    def test_store_event(self):
        """Test storing an event."""
        storage = AuditLogStorage()
        event = AuditEvent(
            event_id="evt_123",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc)
        )
        
        result = storage.store(event)
        
        assert result is True
    
    def test_query_events(self):
        """Test querying events."""
        storage = AuditLogStorage()
        
        # Store multiple events
        for i in range(5):
            event = AuditEvent(
                event_id=f"evt_{i}",
                event_type=AuditEventType.AUTH_SUCCESS,
                category=AuditEventCategory.AUTHENTICATION,
                severity=AuditSeverity.INFO,
                timestamp=datetime.now(timezone.utc),
                actor_id="user_123"
            )
            storage.store(event)
        
        results = storage.query(actor_id="user_123")
        
        assert len(results) == 5
    
    def test_query_by_event_type(self):
        """Test querying by event type."""
        storage = AuditLogStorage()
        
        # Store different event types
        storage.store(AuditEvent(
            event_id="evt_1",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc)
        ))
        storage.store(AuditEvent(
            event_id="evt_2",
            event_type=AuditEventType.AUTH_FAILURE,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.WARNING,
            timestamp=datetime.now(timezone.utc)
        ))
        
        results = storage.query(event_type=AuditEventType.AUTH_SUCCESS)
        
        assert len(results) == 1
        assert results[0].event_type == AuditEventType.AUTH_SUCCESS
    
    def test_query_by_time_range(self):
        """Test querying by time range."""
        storage = AuditLogStorage()
        
        now = datetime.now(timezone.utc)
        
        storage.store(AuditEvent(
            event_id="evt_1",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=now - timedelta(hours=2)
        ))
        storage.store(AuditEvent(
            event_id="evt_2",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=now
        ))
        
        results = storage.query(start_time=now - timedelta(hours=1))
        
        assert len(results) == 1
        assert results[0].event_id == "evt_2"
    
    def test_count_events(self):
        """Test counting events."""
        storage = AuditLogStorage()
        
        for i in range(10):
            storage.store(AuditEvent(
                event_id=f"evt_{i}",
                event_type=AuditEventType.AUTH_SUCCESS,
                category=AuditEventCategory.AUTHENTICATION,
                severity=AuditSeverity.INFO,
                timestamp=datetime.now(timezone.utc)
            ))
        
        count = storage.count()
        
        assert count == 10
    
    def test_get_statistics(self):
        """Test getting statistics."""
        storage = AuditLogStorage()
        
        storage.store(AuditEvent(
            event_id="evt_1",
            event_type=AuditEventType.AUTH_SUCCESS,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.INFO,
            timestamp=datetime.now(timezone.utc),
            outcome="success"
        ))
        storage.store(AuditEvent(
            event_id="evt_2",
            event_type=AuditEventType.AUTH_FAILURE,
            category=AuditEventCategory.AUTHENTICATION,
            severity=AuditSeverity.WARNING,
            timestamp=datetime.now(timezone.utc),
            outcome="failure"
        ))
        
        stats = storage.get_statistics(hours=24)
        
        assert stats["total_events"] == 2
        assert "by_type" in stats
        assert "by_severity" in stats
        assert "by_outcome" in stats


class TestAuditLogger:
    """Test audit logger."""
    
    def test_create_logger(self):
        """Test creating an audit logger."""
        logger = AuditLogger()
        
        assert logger is not None
    
    def test_log_event(self):
        """Test logging an event."""
        logger = AuditLogger()
        
        event = logger.log(
            event_type=AuditEventType.AUTH_SUCCESS,
            actor_id="user_123",
            action="authenticate",
            outcome="success"
        )
        
        assert isinstance(event, AuditEvent)
        assert event.event_type == AuditEventType.AUTH_SUCCESS
        assert event.actor_id == "user_123"
    
    def test_auto_category_detection(self):
        """Test automatic category detection."""
        logger = AuditLogger()
        
        event = logger.log(
            event_type=AuditEventType.KEY_CREATED,
            actor_id="user_123"
        )
        
        assert event.category == AuditEventCategory.KEY_MANAGEMENT
    
    def test_auto_severity_detection(self):
        """Test automatic severity detection."""
        logger = AuditLogger()
        
        # Auth failure should be warning
        event1 = logger.log(
            event_type=AuditEventType.AUTH_FAILURE,
            actor_id="user_123"
        )
        assert event1.severity == AuditSeverity.WARNING
        
        # Threat detected should be critical
        event2 = logger.log(
            event_type=AuditEventType.THREAT_DETECTED,
            actor_id="user_123"
        )
        assert event2.severity == AuditSeverity.CRITICAL
    
    def test_log_auth_success(self):
        """Test logging authentication success."""
        logger = AuditLogger()
        
        event = logger.log_auth_success(
            user_id="user_123",
            ip_address="192.168.1.100",
            session_id="sess_456"
        )
        
        assert event.event_type == AuditEventType.AUTH_SUCCESS
        assert event.actor_id == "user_123"
        assert event.actor_ip == "192.168.1.100"
    
    def test_log_auth_failure(self):
        """Test logging authentication failure."""
        logger = AuditLogger()
        
        event = logger.log_auth_failure(
            user_id="user_123",
            ip_address="192.168.1.100",
            reason="Invalid password"
        )
        
        assert event.event_type == AuditEventType.AUTH_FAILURE
        assert "Invalid password" in event.message
    
    def test_log_key_created(self):
        """Test logging key creation."""
        logger = AuditLogger()
        
        event = logger.log_key_created(
            user_id="user_123",
            key_id="dna-key-001",
            security_level="ultimate"
        )
        
        assert event.event_type == AuditEventType.KEY_CREATED
        assert event.target_id == "dna-key-001"
        assert event.details["security_level"] == "ultimate"
    
    def test_log_threat_detected(self):
        """Test logging threat detection."""
        logger = AuditLogger()
        
        event = logger.log_threat_detected(
            source_ip="10.0.0.50",
            threat_type="brute_force",
            severity="high"
        )
        
        assert event.event_type == AuditEventType.THREAT_DETECTED
        assert event.severity == AuditSeverity.CRITICAL
        assert event.details["threat_type"] == "brute_force"
    
    def test_query_events(self):
        """Test querying logged events."""
        logger = AuditLogger()
        
        logger.log(
            event_type=AuditEventType.AUTH_SUCCESS,
            actor_id="user_123"
        )
        logger.log(
            event_type=AuditEventType.AUTH_SUCCESS,
            actor_id="user_456"
        )
        
        results = logger.query(actor_id="user_123")
        
        assert len(results) == 1
        assert results[0].actor_id == "user_123"
    
    def test_get_statistics(self):
        """Test getting statistics."""
        logger = AuditLogger()
        
        logger.log(event_type=AuditEventType.AUTH_SUCCESS)
        logger.log(event_type=AuditEventType.AUTH_FAILURE)
        
        stats = logger.get_statistics()
        
        assert stats["total_events"] == 2
    
    def test_compliance_report(self):
        """Test generating compliance report."""
        logger = AuditLogger()
        
        # Log events first
        logger.log(event_type=AuditEventType.AUTH_SUCCESS)
        logger.log(event_type=AuditEventType.AUTH_FAILURE)
        logger.log(event_type=AuditEventType.KEY_CREATED, target_id="key-1")
        logger.log_threat_detected("10.0.0.1", "brute_force", "high")
        
        # Set time range to include all events
        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc) + timedelta(hours=1)
        
        report = logger.generate_compliance_report(start, end)
        
        assert report["total_events"] == 4
        assert "summary" in report
        assert "auth_statistics" in report
        assert "security_incidents" in report
    
    def test_alert_handler(self):
        """Test alert handler registration."""
        logger = AuditLogger()
        alerts = []
        
        def alert_handler(event):
            alerts.append(event)
        
        logger.register_alert_handler(alert_handler)
        
        # Critical event should trigger alert
        logger.log_threat_detected("10.0.0.1", "brute_force", "critical")
        
        assert len(alerts) == 1
