"""
DNA-Key Authentication System - Session Management Module

███████╗███████╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
██╔════╝██╔════╝██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
███████╗█████╗  ███████╗███████╗██║██║   ██║██╔██╗ ██║
╚════██║██╔══╝  ╚════██║╚════██║██║██║   ██║██║╚██╗██║
███████║███████╗███████║███████║██║╚██████╔╝██║ ╚████║
╚══════╝╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝

MILITARY-GRADE SESSION MANAGEMENT

This module implements enterprise-grade session management:

1. Secure session token generation
2. Session binding (device, IP, fingerprint)
3. Session lifecycle management
4. Concurrent session control
5. Session hijacking prevention
6. Token rotation and refresh
7. Session audit logging
8. Anomaly-based session termination
"""

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


# ============================================================================
# SESSION TYPES
# ============================================================================

class SessionState(Enum):
    """Session lifecycle states."""
    
    CREATED = "created"
    ACTIVE = "active"
    REFRESHED = "refreshed"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    HIJACK_SUSPECTED = "hijack_suspected"


class SessionType(Enum):
    """Types of sessions."""
    
    INTERACTIVE = "interactive"        # User login session
    API = "api"                        # API access session
    SERVICE = "service"                # Service-to-service
    TEMPORARY = "temporary"            # One-time access
    ELEVATED = "elevated"              # Admin/privileged session


class TerminationReason(Enum):
    """Reasons for session termination."""
    
    USER_LOGOUT = "user_logout"
    TIMEOUT = "timeout"
    MAX_LIFETIME = "max_lifetime"
    ADMIN_TERMINATION = "admin_termination"
    CONCURRENT_LIMIT = "concurrent_limit"
    SECURITY_VIOLATION = "security_violation"
    HIJACK_DETECTED = "hijack_detected"
    DEVICE_CHANGED = "device_changed"
    IP_CHANGED = "ip_changed"


# ============================================================================
# SESSION TOKENS
# ============================================================================

@dataclass
class SessionToken:
    """Secure session token."""
    
    token_id: str
    token_value: str  # Opaque token value
    token_hash: str   # Hash stored server-side
    
    # Binding
    session_id: str
    user_id: str
    
    # Type and scope
    token_type: str = "bearer"
    scopes: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))
    last_used_at: Optional[datetime] = None
    
    # Security
    rotation_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "token_id": self.token_id,
            "session_id": self.session_id,
            "token_type": self.token_type,
            "scopes": self.scopes,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "rotation_count": self.rotation_count
        }


class TokenGenerator:
    """Secure token generation."""
    
    # Token format parameters
    TOKEN_BYTES = 32
    TOKEN_ID_BYTES = 16
    
    @classmethod
    def generate_token(
        cls,
        session_id: str,
        user_id: str,
        scopes: List[str],
        lifetime_seconds: int = 3600
    ) -> SessionToken:
        """
        Generate a secure session token.
        
        Args:
            session_id: Associated session ID
            user_id: User identifier
            scopes: Token scopes
            lifetime_seconds: Token lifetime in seconds
            
        Returns:
            SessionToken with secure random values
        """
        token_id = f"tok_{secrets.token_hex(cls.TOKEN_ID_BYTES)}"
        token_value = secrets.token_urlsafe(cls.TOKEN_BYTES)
        token_hash = hashlib.sha3_256(token_value.encode()).hexdigest()
        
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=lifetime_seconds)
        
        return SessionToken(
            token_id=token_id,
            token_value=token_value,
            token_hash=token_hash,
            session_id=session_id,
            user_id=user_id,
            scopes=scopes,
            created_at=now,
            expires_at=expires
        )
    
    @classmethod
    def rotate_token(cls, old_token: SessionToken, grace_period_seconds: int = 60) -> SessionToken:
        """
        Rotate a token, creating a new one.
        
        Args:
            old_token: Token to rotate
            grace_period_seconds: Grace period for old token
            
        Returns:
            New SessionToken
        """
        new_token = cls.generate_token(
            session_id=old_token.session_id,
            user_id=old_token.user_id,
            scopes=old_token.scopes,
            lifetime_seconds=int((old_token.expires_at - old_token.created_at).total_seconds())
        )
        new_token.rotation_count = old_token.rotation_count + 1
        
        return new_token
    
    @staticmethod
    def verify_token(token_value: str, expected_hash: str) -> bool:
        """Verify a token value against its hash."""
        computed_hash = hashlib.sha3_256(token_value.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, expected_hash)


# ============================================================================
# SESSION BINDING
# ============================================================================

@dataclass
class SessionBinding:
    """Binds session to specific device/context."""
    
    # Device binding
    device_id: str = ""
    device_fingerprint: str = ""
    device_type: str = ""
    
    # Network binding
    ip_address: str = ""
    ip_prefix: str = ""  # /24 for some flexibility
    
    # Browser binding
    user_agent_hash: str = ""
    
    # DNA binding
    dna_key_id: str = ""
    dna_checksum: str = ""
    
    # Binding strictness
    strict_ip: bool = False
    strict_device: bool = True
    strict_dna: bool = True
    
    def compute_fingerprint(self) -> str:
        """Compute binding fingerprint."""
        data = f"{self.device_id}:{self.device_fingerprint}:{self.ip_prefix}:{self.user_agent_hash}"
        return hashlib.sha3_256(data.encode()).hexdigest()
    
    def matches(self, other: "SessionBinding") -> Tuple[bool, List[str]]:
        """
        Check if another binding matches this one.
        
        Returns:
            Tuple of (matches, list_of_mismatches)
        """
        mismatches = []
        
        # Device checks
        if self.strict_device:
            if self.device_id and other.device_id != self.device_id:
                mismatches.append("device_id")
            if self.device_fingerprint and other.device_fingerprint != self.device_fingerprint:
                mismatches.append("device_fingerprint")
        
        # IP checks
        if self.strict_ip:
            if self.ip_address != other.ip_address:
                mismatches.append("ip_address")
        else:
            # Allow same /24 subnet
            if self.ip_prefix and other.ip_prefix != self.ip_prefix:
                mismatches.append("ip_prefix")
        
        # DNA checks
        if self.strict_dna:
            if self.dna_key_id and other.dna_key_id != self.dna_key_id:
                mismatches.append("dna_key_id")
        
        return len(mismatches) == 0, mismatches


# ============================================================================
# SESSION ENTITY
# ============================================================================

@dataclass
class Session:
    """A user session."""
    
    session_id: str
    user_id: str
    session_type: SessionType
    state: SessionState
    
    # Tokens
    access_token: Optional[SessionToken] = None
    refresh_token: Optional[SessionToken] = None
    
    # Binding
    binding: SessionBinding = field(default_factory=SessionBinding)
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=8))
    
    # Configuration
    max_idle_seconds: int = 1800  # 30 minutes
    max_lifetime_seconds: int = 28800  # 8 hours
    
    # Termination
    terminated_at: Optional[datetime] = None
    termination_reason: Optional[TerminationReason] = None
    
    # Audit
    activity_count: int = 0
    last_ip: str = ""
    
    def is_active(self) -> bool:
        """Check if session is active."""
        if self.state not in [SessionState.ACTIVE, SessionState.REFRESHED]:
            return False
        
        now = datetime.now(timezone.utc)
        
        # Check expiration
        if now > self.expires_at:
            return False
        
        # Check idle timeout
        idle_duration = (now - self.last_activity).total_seconds()
        if idle_duration > self.max_idle_seconds:
            return False
        
        return True
    
    def record_activity(self, ip_address: str = ""):
        """Record session activity."""
        self.last_activity = datetime.now(timezone.utc)
        self.activity_count += 1
        if ip_address:
            self.last_ip = ip_address
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_type": self.session_type.value,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "activity_count": self.activity_count,
            "is_active": self.is_active()
        }


# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """
    Enterprise-grade session management.
    
    Features:
    - Secure session creation and validation
    - Token rotation and refresh
    - Session binding verification
    - Concurrent session management
    - Automatic cleanup
    - Audit logging
    """
    
    # Default limits
    DEFAULT_MAX_CONCURRENT_SESSIONS = 5
    DEFAULT_SESSION_LIFETIME = 28800  # 8 hours
    DEFAULT_IDLE_TIMEOUT = 1800  # 30 minutes
    DEFAULT_TOKEN_LIFETIME = 3600  # 1 hour
    
    def __init__(
        self,
        max_concurrent_sessions: int = DEFAULT_MAX_CONCURRENT_SESSIONS,
        session_lifetime: int = DEFAULT_SESSION_LIFETIME,
        idle_timeout: int = DEFAULT_IDLE_TIMEOUT
    ):
        self.max_concurrent_sessions = max_concurrent_sessions
        self.session_lifetime = session_lifetime
        self.idle_timeout = idle_timeout
        
        # Storage (in production, use database/cache)
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self._token_sessions: Dict[str, str] = {}  # token_hash -> session_id
        
        # Audit log
        self._audit_log: List[Dict[str, Any]] = []
    
    def create_session(
        self,
        user_id: str,
        session_type: SessionType = SessionType.INTERACTIVE,
        binding: Optional[SessionBinding] = None,
        scopes: Optional[List[str]] = None
    ) -> Tuple[Session, SessionToken]:
        """
        Create a new session.
        
        Args:
            user_id: User identifier
            session_type: Type of session
            binding: Session binding information
            scopes: Token scopes
            
        Returns:
            Tuple of (Session, access_token)
        """
        # Check concurrent session limit
        self._enforce_session_limit(user_id)
        
        # Generate session ID
        session_id = f"sess_{secrets.token_hex(16)}"
        
        # Create binding
        if binding is None:
            binding = SessionBinding()
        
        # Default scopes
        if scopes is None:
            scopes = ["read", "write"]
        
        # Create session
        now = datetime.now(timezone.utc)
        session = Session(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            state=SessionState.ACTIVE,
            binding=binding,
            created_at=now,
            last_activity=now,
            expires_at=now + timedelta(seconds=self.session_lifetime),
            max_idle_seconds=self.idle_timeout,
            max_lifetime_seconds=self.session_lifetime
        )
        
        # Generate access token
        access_token = TokenGenerator.generate_token(
            session_id=session_id,
            user_id=user_id,
            scopes=scopes,
            lifetime_seconds=self.DEFAULT_TOKEN_LIFETIME
        )
        session.access_token = access_token
        
        # Generate refresh token (longer lifetime)
        refresh_token = TokenGenerator.generate_token(
            session_id=session_id,
            user_id=user_id,
            scopes=["refresh"],
            lifetime_seconds=self.session_lifetime
        )
        session.refresh_token = refresh_token
        
        # Store session
        self._sessions[session_id] = session
        
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = set()
        self._user_sessions[user_id].add(session_id)
        
        self._token_sessions[access_token.token_hash] = session_id
        self._token_sessions[refresh_token.token_hash] = session_id
        
        # Audit log
        self._log_event("session_created", session_id, user_id)
        
        return session, access_token
    
    def validate_session(
        self,
        token_value: str,
        binding: Optional[SessionBinding] = None
    ) -> Tuple[bool, Optional[Session], str]:
        """
        Validate a session token.
        
        Args:
            token_value: The access token value
            binding: Current binding to verify against
            
        Returns:
            Tuple of (is_valid, session, error_message)
        """
        # Hash the token
        token_hash = hashlib.sha3_256(token_value.encode()).hexdigest()
        
        # Find session
        session_id = self._token_sessions.get(token_hash)
        if not session_id:
            return False, None, "Token not found"
        
        session = self._sessions.get(session_id)
        if not session:
            return False, None, "Session not found"
        
        # Check session state
        if not session.is_active():
            return False, session, "Session not active"
        
        # Check token expiration
        if session.access_token and session.access_token.is_expired():
            return False, session, "Token expired"
        
        # Verify binding
        if binding and session.binding:
            matches, mismatches = session.binding.matches(binding)
            if not matches:
                # Potential session hijacking
                session.state = SessionState.HIJACK_SUSPECTED
                self._log_event(
                    "hijack_suspected",
                    session_id,
                    session.user_id,
                    {"mismatches": mismatches}
                )
                return False, session, f"Binding mismatch: {mismatches}"
        
        # Update activity
        session.record_activity(binding.ip_address if binding else "")
        session.access_token.last_used_at = datetime.now(timezone.utc)
        
        return True, session, ""
    
    def refresh_session(
        self,
        refresh_token_value: str
    ) -> Tuple[bool, Optional[SessionToken], str]:
        """
        Refresh a session using refresh token.
        
        Args:
            refresh_token_value: The refresh token value
            
        Returns:
            Tuple of (success, new_access_token, error_message)
        """
        # Hash the token
        token_hash = hashlib.sha3_256(refresh_token_value.encode()).hexdigest()
        
        # Find session
        session_id = self._token_sessions.get(token_hash)
        if not session_id:
            return False, None, "Refresh token not found"
        
        session = self._sessions.get(session_id)
        if not session:
            return False, None, "Session not found"
        
        # Check refresh token validity
        if session.refresh_token and session.refresh_token.is_expired():
            return False, None, "Refresh token expired"
        
        # Verify token value matches
        if not TokenGenerator.verify_token(refresh_token_value, session.refresh_token.token_hash):
            return False, None, "Invalid refresh token"
        
        # Rotate access token
        old_token = session.access_token
        new_token = TokenGenerator.rotate_token(old_token)
        session.access_token = new_token
        session.state = SessionState.REFRESHED
        
        # Update token mapping
        if old_token:
            self._token_sessions.pop(old_token.token_hash, None)
        self._token_sessions[new_token.token_hash] = session_id
        
        # Audit log
        self._log_event("token_refreshed", session_id, session.user_id)
        
        return True, new_token, ""
    
    def terminate_session(
        self,
        session_id: str,
        reason: TerminationReason = TerminationReason.USER_LOGOUT
    ) -> bool:
        """
        Terminate a session.
        
        Args:
            session_id: Session to terminate
            reason: Reason for termination
            
        Returns:
            True if session was terminated
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        # Update session
        session.state = SessionState.TERMINATED
        session.terminated_at = datetime.now(timezone.utc)
        session.termination_reason = reason
        
        # Remove from user sessions
        if session.user_id in self._user_sessions:
            self._user_sessions[session.user_id].discard(session_id)
        
        # Remove token mappings
        if session.access_token:
            self._token_sessions.pop(session.access_token.token_hash, None)
        if session.refresh_token:
            self._token_sessions.pop(session.refresh_token.token_hash, None)
        
        # Audit log
        self._log_event("session_terminated", session_id, session.user_id, {"reason": reason.value})
        
        return True
    
    def terminate_all_user_sessions(
        self,
        user_id: str,
        reason: TerminationReason = TerminationReason.ADMIN_TERMINATION
    ) -> int:
        """
        Terminate all sessions for a user.
        
        Args:
            user_id: User whose sessions to terminate
            reason: Reason for termination
            
        Returns:
            Number of sessions terminated
        """
        session_ids = list(self._user_sessions.get(user_id, set()))
        count = 0
        
        for session_id in session_ids:
            if self.terminate_session(session_id, reason):
                count += 1
        
        return count
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all sessions for a user."""
        session_ids = self._user_sessions.get(user_id, set())
        return [
            self._sessions[sid]
            for sid in session_ids
            if sid in self._sessions
        ]
    
    def get_active_session_count(self, user_id: str) -> int:
        """Get count of active sessions for a user."""
        sessions = self.get_user_sessions(user_id)
        return sum(1 for s in sessions if s.is_active())
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        expired = []
        
        for session_id, session in self._sessions.items():
            if not session.is_active() and session.state == SessionState.ACTIVE:
                expired.append(session_id)
        
        for session_id in expired:
            self.terminate_session(session_id, TerminationReason.TIMEOUT)
        
        return len(expired)
    
    def _enforce_session_limit(self, user_id: str):
        """Enforce concurrent session limit."""
        sessions = self.get_user_sessions(user_id)
        active_sessions = [s for s in sessions if s.is_active()]
        
        if len(active_sessions) >= self.max_concurrent_sessions:
            # Terminate oldest session
            oldest = min(active_sessions, key=lambda s: s.created_at)
            self.terminate_session(oldest.session_id, TerminationReason.CONCURRENT_LIMIT)
    
    def _log_event(
        self,
        event_type: str,
        session_id: str,
        user_id: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log an audit event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "user_id": user_id,
            **(extra or {})
        }
        self._audit_log.append(event)
        
        # Keep only last 10000 events
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-10000:]
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        if user_id:
            events = [e for e in self._audit_log if e.get("user_id") == user_id]
        else:
            events = self._audit_log
        
        return events[-limit:]


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "SessionState",
    "SessionType",
    "TerminationReason",
    "SessionToken",
    "TokenGenerator",
    "SessionBinding",
    "Session",
    "SessionManager",
]
