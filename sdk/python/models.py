"""
DNALockOS SDK - Data Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SecurityLevel(str, Enum):
    """Security level for DNA keys."""
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    GOVERNMENT = "government"


@dataclass
class KeyInfo:
    """Information about a DNA key."""
    key_id: str
    created_at: datetime
    expires_at: datetime
    security_level: SecurityLevel
    subject_id: str
    subject_type: str
    is_revoked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> "KeyInfo":
        return cls(
            key_id=data["key_id"],
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            expires_at=datetime.fromisoformat(data["expires_at"]) if isinstance(data["expires_at"], str) else data["expires_at"],
            security_level=SecurityLevel(data.get("security_level", "standard")),
            subject_id=data.get("subject_id", ""),
            subject_type=data.get("subject_type", "human"),
            is_revoked=data.get("is_revoked", False),
            metadata=data.get("metadata", {})
        )


@dataclass
class EnrollmentResult:
    """Result of a DNA key enrollment."""
    success: bool
    key_id: Optional[str] = None
    serialized_key: Optional[str] = None  # Base64-encoded key for storage
    visual_seed: Optional[str] = None  # Seed for visual DNA rendering
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "EnrollmentResult":
        return cls(
            success=data.get("success", False),
            key_id=data.get("key_id"),
            serialized_key=data.get("serialized_key"),
            visual_seed=data.get("visual_seed"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            error_message=data.get("error_message"),
            error_code=data.get("error_code")
        )


@dataclass
class ChallengeResult:
    """Result of a challenge request."""
    success: bool
    challenge: Optional[str] = None  # Hex-encoded challenge
    challenge_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChallengeResult":
        return cls(
            success=data.get("success", False),
            challenge=data.get("challenge"),
            challenge_id=data.get("challenge_id"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            error_message=data.get("error_message")
        )


@dataclass
class AuthenticationResult:
    """Result of an authentication attempt."""
    success: bool
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    key_id: Optional[str] = None
    is_admin: bool = False
    permissions: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "AuthenticationResult":
        return cls(
            success=data.get("success", False),
            session_token=data.get("session_token"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            key_id=data.get("key_id"),
            is_admin=data.get("is_admin", False),
            permissions=data.get("permissions", []),
            error_message=data.get("error_message")
        )


@dataclass
class RevocationResult:
    """Result of a key revocation."""
    success: bool
    key_id: Optional[str] = None
    revoked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "RevocationResult":
        return cls(
            success=data.get("success", False),
            key_id=data.get("key_id"),
            revoked_at=datetime.fromisoformat(data["revoked_at"]) if data.get("revoked_at") else None,
            error_message=data.get("error_message")
        )


@dataclass
class HealthStatus:
    """System health status."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        return "OPERATIONAL" in self.status.upper()
    
    @classmethod
    def from_dict(cls, data: dict) -> "HealthStatus":
        return cls(
            status=data.get("status", "UNKNOWN"),
            version=data.get("version", "0.0.0"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            services=data.get("services", {})
        )
