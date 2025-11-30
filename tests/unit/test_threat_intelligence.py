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
Tests for Threat Intelligence Module.

Tests the real-time threat detection system including:
- IP reputation scoring
- Attack pattern detection
- Threat indicators
- Automated response
- Threat correlation
"""

import secrets
from datetime import datetime, timedelta, timezone

import pytest

from server.security.threat_intelligence import (
    AttackPattern,
    AttackPatternDetector,
    AttackPhase,
    IPReputation,
    IPReputationEngine,
    ResponseAction,
    ThreatActor,
    ThreatCategory,
    ThreatConfidence,
    ThreatEvent,
    ThreatIndicator,
    ThreatIntelligenceService,
    ThreatSeverity,
)


class TestThreatCategory:
    """Test threat category enumeration."""
    
    def test_network_threats_exist(self):
        """Test network threat categories."""
        assert ThreatCategory.BRUTE_FORCE.value == "brute_force"
        assert ThreatCategory.CREDENTIAL_STUFFING.value == "credential_stuffing"
        assert ThreatCategory.DDoS.value == "ddos"
    
    def test_auth_threats_exist(self):
        """Test authentication threat categories."""
        assert ThreatCategory.SESSION_HIJACKING.value == "session_hijacking"
        assert ThreatCategory.TOKEN_THEFT.value == "token_theft"
        assert ThreatCategory.REPLAY_ATTACK.value == "replay_attack"
    
    def test_dna_threats_exist(self):
        """Test DNA-specific threat categories."""
        assert ThreatCategory.DNA_FORGERY.value == "dna_forgery"
        assert ThreatCategory.DNA_REPLAY.value == "dna_replay"
        assert ThreatCategory.DNA_TAMPERING.value == "dna_tampering"


class TestThreatSeverity:
    """Test threat severity levels."""
    
    def test_severity_ordering(self):
        """Test severity levels are properly ordered."""
        assert ThreatSeverity.INFO < ThreatSeverity.LOW
        assert ThreatSeverity.LOW < ThreatSeverity.MEDIUM
        assert ThreatSeverity.MEDIUM < ThreatSeverity.HIGH
        assert ThreatSeverity.HIGH < ThreatSeverity.CRITICAL
    
    def test_severity_values(self):
        """Test severity integer values."""
        assert ThreatSeverity.INFO.value == 1
        assert ThreatSeverity.CRITICAL.value == 5


class TestThreatConfidence:
    """Test threat confidence levels."""
    
    def test_confidence_values(self):
        """Test confidence level values."""
        assert ThreatConfidence.SUSPECTED.value == "suspected"
        assert ThreatConfidence.LIKELY.value == "likely"
        assert ThreatConfidence.HIGH_CONFIDENCE.value == "high"
        assert ThreatConfidence.CONFIRMED.value == "confirmed"


class TestResponseAction:
    """Test response action enumeration."""
    
    def test_response_actions_exist(self):
        """Test all response actions exist."""
        assert ResponseAction.LOG_ONLY.value == "log_only"
        assert ResponseAction.ALERT.value == "alert"
        assert ResponseAction.CHALLENGE.value == "challenge"
        assert ResponseAction.RATE_LIMIT.value == "rate_limit"
        assert ResponseAction.TEMPORARY_BLOCK.value == "temporary_block"
        assert ResponseAction.PERMANENT_BLOCK.value == "permanent_block"
        assert ResponseAction.ACCOUNT_LOCK.value == "account_lock"


class TestThreatIndicator:
    """Test threat indicator functionality."""
    
    def test_create_indicator(self):
        """Test creating a threat indicator."""
        indicator = ThreatIndicator(
            indicator_id="ioc-001",
            indicator_type="ip",
            value="192.168.1.100",
            threat_category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.HIGH,
            confidence=ThreatConfidence.CONFIRMED,
            source="internal",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc)
        )
        
        assert indicator.indicator_id == "ioc-001"
        assert indicator.indicator_type == "ip"
        assert indicator.is_active is True
    
    def test_indicator_expiration(self):
        """Test indicator expiration."""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        indicator = ThreatIndicator(
            indicator_id="ioc-002",
            indicator_type="ip",
            value="10.0.0.1",
            threat_category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.MEDIUM,
            confidence=ThreatConfidence.LIKELY,
            source="internal",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            expires_at=past_time
        )
        
        assert indicator.is_expired() is True
    
    def test_indicator_not_expired(self):
        """Test indicator not expired."""
        future_time = datetime.now(timezone.utc) + timedelta(hours=24)
        
        indicator = ThreatIndicator(
            indicator_id="ioc-003",
            indicator_type="ip",
            value="10.0.0.2",
            threat_category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.MEDIUM,
            confidence=ThreatConfidence.LIKELY,
            source="internal",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            expires_at=future_time
        )
        
        assert indicator.is_expired() is False
    
    def test_indicator_to_dict(self):
        """Test indicator serialization."""
        indicator = ThreatIndicator(
            indicator_id="ioc-004",
            indicator_type="domain",
            value="malicious.com",
            threat_category=ThreatCategory.APT,
            severity=ThreatSeverity.CRITICAL,
            confidence=ThreatConfidence.CONFIRMED,
            source="threat_feed",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc)
        )
        
        result = indicator.to_dict()
        
        assert result["indicator_id"] == "ioc-004"
        assert result["indicator_type"] == "domain"
        assert result["threat_category"] == "apt"


class TestThreatEvent:
    """Test threat event functionality."""
    
    def test_create_event(self):
        """Test creating a threat event."""
        event = ThreatEvent(
            event_id="evt-001",
            timestamp=datetime.now(timezone.utc),
            threat_category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.HIGH,
            confidence=ThreatConfidence.HIGH_CONFIDENCE,
            source_ip="192.168.1.100",
            description="Multiple failed login attempts"
        )
        
        assert event.event_id == "evt-001"
        assert event.threat_category == ThreatCategory.BRUTE_FORCE
        assert event.response_action == ResponseAction.LOG_ONLY
    
    def test_event_to_dict(self):
        """Test event serialization."""
        event = ThreatEvent(
            event_id="evt-002",
            timestamp=datetime.now(timezone.utc),
            threat_category=ThreatCategory.CREDENTIAL_STUFFING,
            severity=ThreatSeverity.CRITICAL,
            confidence=ThreatConfidence.CONFIRMED,
            source_ip="10.0.0.1",
            source_user="attacker",
            description="Credential stuffing detected"
        )
        
        result = event.to_dict()
        
        assert result["event_id"] == "evt-002"
        assert result["threat_category"] == "credential_stuffing"
        assert result["severity"] == 5


class TestIPReputationEngine:
    """Test IP reputation engine."""
    
    def test_create_engine(self):
        """Test creating reputation engine."""
        engine = IPReputationEngine()
        assert engine is not None
    
    def test_get_reputation_new_ip(self):
        """Test getting reputation for new IP."""
        engine = IPReputationEngine()
        
        rep = engine.get_reputation("192.168.1.100")
        
        assert isinstance(rep, IPReputation)
        assert rep.ip_address == "192.168.1.100"
        assert rep.reputation_score >= 0
        assert rep.reputation_score <= 100
    
    def test_blocklist_reduces_reputation(self):
        """Test that blocklisted IPs have low reputation."""
        engine = IPReputationEngine()
        
        engine.add_to_blocklist("10.0.0.1", "test")
        rep = engine.get_reputation("10.0.0.1")
        
        assert rep.on_blocklist is True
        assert rep.reputation_score < 50
    
    def test_allowlist_gives_high_reputation(self):
        """Test that allowlisted IPs have high reputation."""
        engine = IPReputationEngine()
        
        engine.add_to_allowlist("192.168.1.1")
        rep = engine.get_reputation("192.168.1.1")
        
        assert rep.reputation_score == 100
        assert rep.risk_level == ThreatSeverity.INFO
    
    def test_threat_history_reduces_reputation(self):
        """Test that threat history reduces reputation."""
        engine = IPReputationEngine()
        
        # First get baseline
        rep1 = engine.get_reputation("10.0.0.5")
        initial_score = rep1.reputation_score
        
        # Record threats
        for i in range(3):
            event = ThreatEvent(
                event_id=f"evt-{i}",
                timestamp=datetime.now(timezone.utc),
                threat_category=ThreatCategory.BRUTE_FORCE,
                severity=ThreatSeverity.HIGH,
                confidence=ThreatConfidence.CONFIRMED
            )
            engine.record_threat("10.0.0.5", event)
        
        # Get new reputation
        rep2 = engine.get_reputation("10.0.0.5")
        
        assert rep2.reputation_score < initial_score
        assert rep2.threat_count_24h >= 3


class TestAttackPatternDetector:
    """Test attack pattern detector."""
    
    def test_create_detector(self):
        """Test creating pattern detector."""
        detector = AttackPatternDetector()
        assert detector is not None
        assert len(detector._patterns) > 0
    
    def test_builtin_patterns_exist(self):
        """Test built-in patterns are loaded."""
        detector = AttackPatternDetector()
        
        assert "BRUTE_FORCE_SINGLE_USER" in detector._patterns
        assert "CREDENTIAL_STUFFING" in detector._patterns
        assert "DNA_REPLAY_ATTACK" in detector._patterns
    
    def test_add_custom_pattern(self):
        """Test adding custom pattern."""
        detector = AttackPatternDetector()
        
        pattern = AttackPattern(
            pattern_id="CUSTOM_PATTERN",
            name="Custom Pattern",
            description="Test pattern",
            category=ThreatCategory.APT,
            severity=ThreatSeverity.CRITICAL,
            threshold_count=3
        )
        
        detector.add_pattern(pattern)
        
        assert "CUSTOM_PATTERN" in detector._patterns
    
    def test_single_event_no_detection(self):
        """Test that single event doesn't trigger detection."""
        detector = AttackPatternDetector()
        
        threats = detector.analyze_event(
            event_type="login_attempt",
            source_ip="192.168.1.100",
            user_id="user123",
            success=False
        )
        
        # Single event shouldn't trigger anything
        assert len(threats) == 0
    
    def test_brute_force_detection(self):
        """Test brute force attack detection."""
        detector = AttackPatternDetector()
        
        # Simulate multiple failed login attempts
        threats = []
        for i in range(10):
            result = detector.analyze_event(
                event_type="login_attempt",
                source_ip="10.0.0.1",
                user_id="victim_user",
                success=False
            )
            threats.extend(result)
        
        # Should detect brute force
        assert len(threats) > 0
        categories = [t.threat_category for t in threats]
        assert ThreatCategory.BRUTE_FORCE in categories


class TestThreatIntelligenceService:
    """Test threat intelligence service."""
    
    def test_create_service(self):
        """Test creating threat intelligence service."""
        service = ThreatIntelligenceService()
        
        assert service is not None
        assert service.ip_reputation is not None
        assert service.pattern_detector is not None
    
    def test_check_ip(self):
        """Test IP check through service."""
        service = ThreatIntelligenceService()
        
        rep = service.check_ip("192.168.1.1")
        
        assert isinstance(rep, IPReputation)
    
    def test_analyze_normal_authentication(self):
        """Test analysis of normal authentication."""
        service = ThreatIntelligenceService()
        
        should_allow, threats, action = service.analyze_authentication(
            source_ip="192.168.1.100",
            user_id="normal_user",
            success=True
        )
        
        assert should_allow is True
        assert action == ResponseAction.LOG_ONLY
    
    def test_analyze_blocked_ip(self):
        """Test analysis from blocked IP."""
        service = ThreatIntelligenceService()
        
        service.ip_reputation.add_to_blocklist("10.0.0.1")
        
        should_allow, threats, action = service.analyze_authentication(
            source_ip="10.0.0.1",
            user_id="user123"
        )
        
        assert should_allow is False
        assert action == ResponseAction.PERMANENT_BLOCK
    
    def test_add_and_check_indicator(self):
        """Test adding and matching indicator."""
        service = ThreatIntelligenceService()
        
        indicator = ThreatIndicator(
            indicator_id="ioc-test",
            indicator_type="ip",
            value="10.0.0.50",
            threat_category=ThreatCategory.APT,
            severity=ThreatSeverity.CRITICAL,
            confidence=ThreatConfidence.CONFIRMED,
            source="test",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc)
        )
        
        service.add_indicator(indicator)
        
        should_allow, threats, action = service.analyze_authentication(
            source_ip="10.0.0.50",
            user_id="user123"
        )
        
        assert len(threats) > 0
        assert any(t.threat_category == ThreatCategory.APT for t in threats)
    
    def test_remove_indicator(self):
        """Test removing indicator."""
        service = ThreatIntelligenceService()
        
        indicator = ThreatIndicator(
            indicator_id="ioc-remove",
            indicator_type="ip",
            value="10.0.0.60",
            threat_category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.HIGH,
            confidence=ThreatConfidence.CONFIRMED,
            source="test",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc)
        )
        
        service.add_indicator(indicator)
        service.remove_indicator("ioc-remove")
        
        # Should no longer match
        should_allow, threats, action = service.analyze_authentication(
            source_ip="10.0.0.60",
            user_id="user123"
        )
        
        # No threats from the removed indicator
        assert all(t.threat_category != ThreatCategory.BRUTE_FORCE or 
                  "ioc-remove" not in t.matched_indicators for t in threats)
    
    def test_get_threat_summary(self):
        """Test threat summary generation."""
        service = ThreatIntelligenceService()
        
        # Generate some events
        for i in range(5):
            service.analyze_authentication(
                source_ip=f"10.0.0.{i}",
                user_id=f"user{i}",
                success=False
            )
        
        summary = service.get_threat_summary()
        
        assert "total_events_24h" in summary
        assert "by_category" in summary
        assert "by_severity" in summary
        assert "active_indicators" in summary


class TestThreatActor:
    """Test threat actor profiling."""
    
    def test_create_threat_actor(self):
        """Test creating a threat actor profile."""
        actor = ThreatActor(
            actor_id="actor-001",
            name="APT99",
            aliases=["FancyCat", "CozyKitten"],
            actor_type="nation_state",
            sophistication="advanced",
            target_sectors=["government", "defense"],
            target_regions=["NA", "EU"]
        )
        
        assert actor.actor_id == "actor-001"
        assert actor.actor_type == "nation_state"
        assert len(actor.aliases) == 2


class TestAttackPattern:
    """Test attack pattern configuration."""
    
    def test_create_attack_pattern(self):
        """Test creating an attack pattern."""
        pattern = AttackPattern(
            pattern_id="TEST_PATTERN",
            name="Test Pattern",
            description="A test pattern for unit testing",
            category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.HIGH,
            time_window_seconds=300,
            threshold_count=5,
            response_action=ResponseAction.TEMPORARY_BLOCK
        )
        
        assert pattern.pattern_id == "TEST_PATTERN"
        assert pattern.threshold_count == 5
        assert pattern.response_action == ResponseAction.TEMPORARY_BLOCK
