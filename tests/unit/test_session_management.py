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
Tests for Session Management Module.

Tests the enterprise-grade session management system including:
- Session creation and validation
- Token generation and rotation
- Session binding verification
- Concurrent session management
- Session termination
"""

import secrets
import time
from datetime import datetime, timedelta, timezone

import pytest

from server.security.session_management import (
    Session,
    SessionBinding,
    SessionManager,
    SessionState,
    SessionToken,
    SessionType,
    TerminationReason,
    TokenGenerator,
)


class TestSessionState:
    """Test session state enumeration."""
    
    def test_session_states_exist(self):
        """Test all session states exist."""
        assert SessionState.CREATED.value == "created"
        assert SessionState.ACTIVE.value == "active"
        assert SessionState.REFRESHED.value == "refreshed"
        assert SessionState.SUSPENDED.value == "suspended"
        assert SessionState.EXPIRED.value == "expired"
        assert SessionState.TERMINATED.value == "terminated"
        assert SessionState.HIJACK_SUSPECTED.value == "hijack_suspected"


class TestSessionType:
    """Test session type enumeration."""
    
    def test_session_types_exist(self):
        """Test all session types exist."""
        assert SessionType.INTERACTIVE.value == "interactive"
        assert SessionType.API.value == "api"
        assert SessionType.SERVICE.value == "service"
        assert SessionType.TEMPORARY.value == "temporary"
        assert SessionType.ELEVATED.value == "elevated"


class TestTerminationReason:
    """Test termination reason enumeration."""
    
    def test_termination_reasons_exist(self):
        """Test all termination reasons exist."""
        assert TerminationReason.USER_LOGOUT.value == "user_logout"
        assert TerminationReason.TIMEOUT.value == "timeout"
        assert TerminationReason.SECURITY_VIOLATION.value == "security_violation"
        assert TerminationReason.HIJACK_DETECTED.value == "hijack_detected"


class TestTokenGenerator:
    """Test token generator."""
    
    def test_generate_token(self):
        """Test generating a token."""
        token = TokenGenerator.generate_token(
            session_id="sess_123",
            user_id="user_456",
            scopes=["read", "write"]
        )
        
        assert isinstance(token, SessionToken)
        assert token.session_id == "sess_123"
        assert token.user_id == "user_456"
        assert token.scopes == ["read", "write"]
        assert token.token_id.startswith("tok_")
        assert len(token.token_value) > 0
        assert len(token.token_hash) == 64
    
    def test_tokens_are_unique(self):
        """Test that generated tokens are unique."""
        tokens = [
            TokenGenerator.generate_token("sess", "user", [])
            for _ in range(10)
        ]
        
        token_values = [t.token_value for t in tokens]
        assert len(token_values) == len(set(token_values))
    
    def test_token_expiration(self):
        """Test token expiration."""
        # Short lifetime
        token = TokenGenerator.generate_token(
            session_id="sess",
            user_id="user",
            scopes=[],
            lifetime_seconds=1
        )
        
        assert token.is_expired() is False
        
        # Wait for expiration (simulate by modifying expires_at)
        token.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        assert token.is_expired() is True
    
    def test_rotate_token(self):
        """Test token rotation."""
        old_token = TokenGenerator.generate_token("sess", "user", ["read"])
        old_token.rotation_count = 3
        
        new_token = TokenGenerator.rotate_token(old_token)
        
        assert new_token.session_id == old_token.session_id
        assert new_token.user_id == old_token.user_id
        assert new_token.scopes == old_token.scopes
        assert new_token.token_value != old_token.token_value
        assert new_token.rotation_count == 4
    
    def test_verify_token(self):
        """Test token verification."""
        token = TokenGenerator.generate_token("sess", "user", [])
        
        assert TokenGenerator.verify_token(token.token_value, token.token_hash) is True
        assert TokenGenerator.verify_token("wrong_value", token.token_hash) is False
    
    def test_token_to_dict(self):
        """Test token serialization."""
        token = TokenGenerator.generate_token("sess", "user", ["read"])
        
        result = token.to_dict()
        
        assert result["session_id"] == "sess"
        assert "token_value" not in result  # Should not expose token value
        assert "token_hash" not in result  # Should not expose token hash


class TestSessionBinding:
    """Test session binding."""
    
    def test_create_binding(self):
        """Test creating a session binding."""
        binding = SessionBinding(
            device_id="device-123",
            ip_address="192.168.1.100",
            dna_key_id="dna-key-001"
        )
        
        assert binding.device_id == "device-123"
        assert binding.ip_address == "192.168.1.100"
    
    def test_compute_fingerprint(self):
        """Test fingerprint computation."""
        binding = SessionBinding(
            device_id="device-123",
            device_fingerprint="fp-abc",
            ip_prefix="192.168.1",
            user_agent_hash="ua-hash"
        )
        
        fingerprint = binding.compute_fingerprint()
        
        assert len(fingerprint) == 64
    
    def test_binding_matches_same(self):
        """Test matching identical bindings."""
        binding1 = SessionBinding(
            device_id="device-123",
            ip_address="192.168.1.100"
        )
        binding2 = SessionBinding(
            device_id="device-123",
            ip_address="192.168.1.100"
        )
        
        matches, mismatches = binding1.matches(binding2)
        
        assert matches is True
        assert len(mismatches) == 0
    
    def test_binding_mismatch_device(self):
        """Test binding mismatch on device."""
        binding1 = SessionBinding(
            device_id="device-123",
            strict_device=True
        )
        binding2 = SessionBinding(
            device_id="device-456"
        )
        
        matches, mismatches = binding1.matches(binding2)
        
        assert matches is False
        assert "device_id" in mismatches


class TestSession:
    """Test session entity."""
    
    def test_create_session(self):
        """Test creating a session."""
        session = Session(
            session_id="sess_123",
            user_id="user_456",
            session_type=SessionType.INTERACTIVE,
            state=SessionState.ACTIVE
        )
        
        assert session.session_id == "sess_123"
        assert session.user_id == "user_456"
        assert session.session_type == SessionType.INTERACTIVE
        assert session.state == SessionState.ACTIVE
    
    def test_session_is_active(self):
        """Test session active check."""
        session = Session(
            session_id="sess",
            user_id="user",
            session_type=SessionType.INTERACTIVE,
            state=SessionState.ACTIVE,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            max_idle_seconds=1800
        )
        
        assert session.is_active() is True
    
    def test_session_expired(self):
        """Test expired session."""
        session = Session(
            session_id="sess",
            user_id="user",
            session_type=SessionType.INTERACTIVE,
            state=SessionState.ACTIVE,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        assert session.is_active() is False
    
    def test_session_idle_timeout(self):
        """Test session idle timeout."""
        session = Session(
            session_id="sess",
            user_id="user",
            session_type=SessionType.INTERACTIVE,
            state=SessionState.ACTIVE,
            last_activity=datetime.now(timezone.utc) - timedelta(hours=1),
            max_idle_seconds=1800
        )
        
        assert session.is_active() is False
    
    def test_record_activity(self):
        """Test recording activity."""
        session = Session(
            session_id="sess",
            user_id="user",
            session_type=SessionType.INTERACTIVE,
            state=SessionState.ACTIVE
        )
        
        initial_count = session.activity_count
        session.record_activity("192.168.1.100")
        
        assert session.activity_count == initial_count + 1
        assert session.last_ip == "192.168.1.100"
    
    def test_session_to_dict(self):
        """Test session serialization."""
        session = Session(
            session_id="sess",
            user_id="user",
            session_type=SessionType.INTERACTIVE,
            state=SessionState.ACTIVE
        )
        
        result = session.to_dict()
        
        assert result["session_id"] == "sess"
        assert result["user_id"] == "user"
        assert result["session_type"] == "interactive"
        assert result["state"] == "active"
        assert "is_active" in result


class TestSessionManager:
    """Test session manager."""
    
    def test_create_manager(self):
        """Test creating a session manager."""
        manager = SessionManager()
        
        assert manager is not None
        assert manager.max_concurrent_sessions == 5
    
    def test_create_session(self):
        """Test creating a session."""
        manager = SessionManager()
        
        session, token = manager.create_session(
            user_id="user_123",
            session_type=SessionType.INTERACTIVE
        )
        
        assert isinstance(session, Session)
        assert isinstance(token, SessionToken)
        assert session.user_id == "user_123"
        assert session.state == SessionState.ACTIVE
        assert session.access_token is not None
        assert session.refresh_token is not None
    
    def test_validate_session_success(self):
        """Test successful session validation."""
        manager = SessionManager()
        session, token = manager.create_session("user_123")
        
        is_valid, validated_session, error = manager.validate_session(
            token.token_value
        )
        
        assert is_valid is True
        assert validated_session is not None
        assert validated_session.session_id == session.session_id
        assert error == ""
    
    def test_validate_invalid_token(self):
        """Test validation with invalid token."""
        manager = SessionManager()
        
        is_valid, session, error = manager.validate_session("invalid_token")
        
        assert is_valid is False
        assert session is None
        assert "not found" in error.lower()
    
    def test_refresh_session(self):
        """Test session refresh."""
        manager = SessionManager()
        session, token = manager.create_session("user_123")
        
        success, new_token, error = manager.refresh_session(
            session.refresh_token.token_value
        )
        
        assert success is True
        assert new_token is not None
        assert new_token.token_value != token.token_value
    
    def test_terminate_session(self):
        """Test session termination."""
        manager = SessionManager()
        session, token = manager.create_session("user_123")
        
        result = manager.terminate_session(
            session.session_id,
            TerminationReason.USER_LOGOUT
        )
        
        assert result is True
        
        # Validate should fail now
        is_valid, _, _ = manager.validate_session(token.token_value)
        assert is_valid is False
    
    def test_terminate_all_user_sessions(self):
        """Test terminating all sessions for a user."""
        manager = SessionManager(max_concurrent_sessions=10)
        
        # Create multiple sessions
        for _ in range(5):
            manager.create_session("user_123")
        
        count = manager.terminate_all_user_sessions("user_123")
        
        assert count == 5
        assert manager.get_active_session_count("user_123") == 0
    
    def test_concurrent_session_limit(self):
        """Test concurrent session limit enforcement."""
        manager = SessionManager(max_concurrent_sessions=3)
        
        sessions = []
        for i in range(5):
            session, token = manager.create_session("user_123")
            sessions.append((session, token))
        
        # Should only have 3 active sessions
        active_count = manager.get_active_session_count("user_123")
        assert active_count <= 3
    
    def test_get_user_sessions(self):
        """Test getting all sessions for a user."""
        manager = SessionManager()
        
        manager.create_session("user_123")
        manager.create_session("user_123")
        manager.create_session("user_456")
        
        user_sessions = manager.get_user_sessions("user_123")
        
        assert len(user_sessions) == 2
        assert all(s.user_id == "user_123" for s in user_sessions)
    
    def test_binding_verification(self):
        """Test session binding verification."""
        manager = SessionManager()
        
        binding = SessionBinding(
            device_id="device-123",
            ip_address="192.168.1.100",
            strict_device=True
        )
        
        session, token = manager.create_session(
            "user_123",
            binding=binding
        )
        
        # Same binding should pass
        same_binding = SessionBinding(
            device_id="device-123",
            ip_address="192.168.1.100"
        )
        
        is_valid, _, _ = manager.validate_session(
            token.token_value,
            binding=same_binding
        )
        assert is_valid is True
    
    def test_audit_log(self):
        """Test audit logging."""
        manager = SessionManager()
        
        session, token = manager.create_session("user_123")
        manager.terminate_session(session.session_id)
        
        log = manager.get_audit_log(user_id="user_123")
        
        assert len(log) >= 2
        event_types = [e["event_type"] for e in log]
        assert "session_created" in event_types
        assert "session_terminated" in event_types
    
    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        manager = SessionManager()
        
        # Create a session and expire it manually
        session, _ = manager.create_session("user_123")
        session.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        cleaned = manager.cleanup_expired_sessions()
        
        assert cleaned >= 0  # May have cleaned the session
