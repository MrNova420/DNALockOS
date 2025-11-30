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
DNA-Key Authentication System - Audit Logging Module

 █████╗ ██╗   ██╗██████╗ ██╗████████╗
██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
███████║██║   ██║██║  ██║██║   ██║   
██╔══██║██║   ██║██║  ██║██║   ██║   
██║  ██║╚██████╔╝██████╔╝██║   ██║   
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   

COMPREHENSIVE SECURITY AUDIT LOGGING

This module implements enterprise-grade audit logging for:

1. Authentication events
2. Authorization decisions
3. Key lifecycle events
4. Security incidents
5. Administrative actions
6. Compliance reporting
7. Forensic analysis

FULL AUDIT TRAIL FOR COMPLIANCE AND SECURITY
"""

import hashlib
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# AUDIT EVENT TYPES
# ============================================================================

class AuditEventCategory(Enum):
    """Categories of audit events."""
    
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    KEY_MANAGEMENT = "key_management"
    SESSION = "session"
    SECURITY = "security"
    ADMINISTRATIVE = "administrative"
    SYSTEM = "system"
    COMPLIANCE = "compliance"


class AuditEventType(Enum):
    """Specific types of audit events."""
    
    # Authentication events
    AUTH_ATTEMPT = "auth_attempt"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    MFA_CHALLENGE = "mfa_challenge"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILURE = "mfa_failure"
    
    # Key management events
    KEY_CREATED = "key_created"
    KEY_ACTIVATED = "key_activated"
    KEY_SUSPENDED = "key_suspended"
    KEY_REVOKED = "key_revoked"
    KEY_EXPIRED = "key_expired"
    KEY_ACCESSED = "key_accessed"
    KEY_MODIFIED = "key_modified"
    
    # Session events
    SESSION_CREATED = "session_created"
    SESSION_REFRESHED = "session_refreshed"
    SESSION_TERMINATED = "session_terminated"
    SESSION_HIJACK_DETECTED = "session_hijack_detected"
    
    # Security events
    THREAT_DETECTED = "threat_detected"
    ATTACK_BLOCKED = "attack_blocked"
    ANOMALY_DETECTED = "anomaly_detected"
    IP_BLOCKED = "ip_blocked"
    
    # Administrative events
    CONFIG_CHANGED = "config_changed"
    USER_CREATED = "user_created"
    USER_MODIFIED = "user_modified"
    USER_DELETED = "user_deleted"
    PERMISSION_CHANGED = "permission_changed"
    
    # System events
    SERVICE_STARTED = "service_started"
    SERVICE_STOPPED = "service_stopped"
    ERROR_OCCURRED = "error_occurred"
    BACKUP_CREATED = "backup_created"


class AuditSeverity(Enum):
    """Severity levels for audit events."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# AUDIT EVENT
# ============================================================================

@dataclass
class AuditEvent:
    """A single audit event."""
    
    event_id: str
    event_type: AuditEventType
    category: AuditEventCategory
    severity: AuditSeverity
    timestamp: datetime
    
    # Actor information
    actor_id: Optional[str] = None
    actor_type: str = "user"  # user, system, service
    actor_ip: Optional[str] = None
    
    # Target information
    target_type: Optional[str] = None  # key, session, user, etc.
    target_id: Optional[str] = None
    
    # Event details
    action: str = ""
    outcome: str = "success"  # success, failure, unknown
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Security
    event_hash: str = ""
    
    def __post_init__(self):
        if not self.event_hash:
            self.event_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute integrity hash for the event."""
        data = (
            f"{self.event_id}{self.event_type.value}{self.timestamp.isoformat()}"
            f"{self.actor_id}{self.target_id}{self.action}{self.outcome}"
        )
        return hashlib.sha3_256(data.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify event integrity."""
        return self._compute_hash() == self.event_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "actor_ip": self.actor_ip,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "action": self.action,
            "outcome": self.outcome,
            "message": self.message,
            "details": self.details,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "event_hash": self.event_hash
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


# ============================================================================
# AUDIT LOG STORAGE
# ============================================================================

class AuditLogStorage:
    """
    Storage backend for audit logs.
    
    In production, this would connect to:
    - Database (PostgreSQL, etc.)
    - Log aggregation (ELK, Splunk, etc.)
    - SIEM systems
    - Immutable storage (blockchain, etc.)
    """
    
    def __init__(self, max_memory_events: int = 100000):
        self._events: List[AuditEvent] = []
        self._max_events = max_memory_events
        self._index_by_actor: Dict[str, List[str]] = {}
        self._index_by_target: Dict[str, List[str]] = {}
        self._index_by_type: Dict[str, List[str]] = {}
    
    def store(self, event: AuditEvent) -> bool:
        """Store an audit event."""
        self._events.append(event)
        
        # Update indexes
        if event.actor_id:
            if event.actor_id not in self._index_by_actor:
                self._index_by_actor[event.actor_id] = []
            self._index_by_actor[event.actor_id].append(event.event_id)
        
        if event.target_id:
            if event.target_id not in self._index_by_target:
                self._index_by_target[event.target_id] = []
            self._index_by_target[event.target_id].append(event.event_id)
        
        type_key = event.event_type.value
        if type_key not in self._index_by_type:
            self._index_by_type[type_key] = []
        self._index_by_type[type_key].append(event.event_id)
        
        # Cleanup if over limit
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]
        
        return True
    
    def query(
        self,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        category: Optional[AuditEventCategory] = None,
        severity: Optional[AuditSeverity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEvent]:
        """Query audit events."""
        results = self._events
        
        if actor_id:
            results = [e for e in results if e.actor_id == actor_id]
        
        if target_id:
            results = [e for e in results if e.target_id == target_id]
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        
        if category:
            results = [e for e in results if e.category == category]
        
        if severity:
            results = [e for e in results if e.severity == severity]
        
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        
        # Sort by timestamp descending
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        return results[offset:offset + limit]
    
    def count(
        self,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Count matching events."""
        results = self._events
        
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        
        return len(results)
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit log statistics."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent = [e for e in self._events if e.timestamp >= cutoff]
        
        by_type = {}
        by_severity = {}
        by_outcome = {}
        
        for event in recent:
            type_key = event.event_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
            
            sev_key = event.severity.value
            by_severity[sev_key] = by_severity.get(sev_key, 0) + 1
            
            by_outcome[event.outcome] = by_outcome.get(event.outcome, 0) + 1
        
        return {
            "total_events": len(recent),
            "time_period_hours": hours,
            "by_type": by_type,
            "by_severity": by_severity,
            "by_outcome": by_outcome
        }


# ============================================================================
# AUDIT LOGGER
# ============================================================================

class AuditLogger:
    """
    Main audit logging service.
    
    Provides:
    - Event logging with automatic categorization
    - Tamper detection through hashing
    - Query and search capabilities
    - Compliance reporting
    - Alert generation
    """
    
    def __init__(self, storage: Optional[AuditLogStorage] = None):
        self._storage = storage or AuditLogStorage()
        self._alert_handlers: List[callable] = []
    
    def log(
        self,
        event_type: AuditEventType,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
        action: str = "",
        outcome: str = "success",
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        severity: Optional[AuditSeverity] = None,
        actor_ip: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            actor_id: Who performed the action
            target_id: What was affected
            target_type: Type of target
            action: Description of action
            outcome: success, failure, unknown
            message: Human-readable message
            details: Additional details
            severity: Event severity (auto-detected if not provided)
            actor_ip: IP address of actor
            session_id: Session ID if applicable
            request_id: Request ID for correlation
            
        Returns:
            The created AuditEvent
        """
        # Auto-detect category
        category = self._determine_category(event_type)
        
        # Auto-detect severity if not provided
        if severity is None:
            severity = self._determine_severity(event_type, outcome)
        
        # Create event
        event = AuditEvent(
            event_id=f"evt_{secrets.token_hex(12)}",
            event_type=event_type,
            category=category,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            actor_id=actor_id,
            actor_ip=actor_ip,
            target_type=target_type,
            target_id=target_id,
            action=action,
            outcome=outcome,
            message=message,
            details=details or {},
            session_id=session_id,
            request_id=request_id
        )
        
        # Store event
        self._storage.store(event)
        
        # Check for alerts
        self._check_alerts(event)
        
        return event
    
    def _determine_category(self, event_type: AuditEventType) -> AuditEventCategory:
        """Determine category from event type."""
        type_to_category = {
            AuditEventType.AUTH_ATTEMPT: AuditEventCategory.AUTHENTICATION,
            AuditEventType.AUTH_SUCCESS: AuditEventCategory.AUTHENTICATION,
            AuditEventType.AUTH_FAILURE: AuditEventCategory.AUTHENTICATION,
            AuditEventType.MFA_CHALLENGE: AuditEventCategory.AUTHENTICATION,
            AuditEventType.MFA_SUCCESS: AuditEventCategory.AUTHENTICATION,
            AuditEventType.MFA_FAILURE: AuditEventCategory.AUTHENTICATION,
            AuditEventType.KEY_CREATED: AuditEventCategory.KEY_MANAGEMENT,
            AuditEventType.KEY_ACTIVATED: AuditEventCategory.KEY_MANAGEMENT,
            AuditEventType.KEY_SUSPENDED: AuditEventCategory.KEY_MANAGEMENT,
            AuditEventType.KEY_REVOKED: AuditEventCategory.KEY_MANAGEMENT,
            AuditEventType.KEY_EXPIRED: AuditEventCategory.KEY_MANAGEMENT,
            AuditEventType.KEY_ACCESSED: AuditEventCategory.KEY_MANAGEMENT,
            AuditEventType.SESSION_CREATED: AuditEventCategory.SESSION,
            AuditEventType.SESSION_REFRESHED: AuditEventCategory.SESSION,
            AuditEventType.SESSION_TERMINATED: AuditEventCategory.SESSION,
            AuditEventType.SESSION_HIJACK_DETECTED: AuditEventCategory.SECURITY,
            AuditEventType.THREAT_DETECTED: AuditEventCategory.SECURITY,
            AuditEventType.ATTACK_BLOCKED: AuditEventCategory.SECURITY,
            AuditEventType.ANOMALY_DETECTED: AuditEventCategory.SECURITY,
            AuditEventType.IP_BLOCKED: AuditEventCategory.SECURITY,
            AuditEventType.CONFIG_CHANGED: AuditEventCategory.ADMINISTRATIVE,
            AuditEventType.USER_CREATED: AuditEventCategory.ADMINISTRATIVE,
            AuditEventType.USER_MODIFIED: AuditEventCategory.ADMINISTRATIVE,
            AuditEventType.USER_DELETED: AuditEventCategory.ADMINISTRATIVE,
            AuditEventType.SERVICE_STARTED: AuditEventCategory.SYSTEM,
            AuditEventType.SERVICE_STOPPED: AuditEventCategory.SYSTEM,
            AuditEventType.ERROR_OCCURRED: AuditEventCategory.SYSTEM,
        }
        return type_to_category.get(event_type, AuditEventCategory.SYSTEM)
    
    def _determine_severity(self, event_type: AuditEventType, outcome: str) -> AuditSeverity:
        """Determine severity from event type and outcome."""
        # High severity events
        high_severity = {
            AuditEventType.SESSION_HIJACK_DETECTED,
            AuditEventType.THREAT_DETECTED,
            AuditEventType.ATTACK_BLOCKED,
            AuditEventType.KEY_REVOKED,
        }
        
        if event_type in high_severity:
            return AuditSeverity.CRITICAL if outcome == "success" else AuditSeverity.ERROR
        
        # Warning level events
        warning_events = {
            AuditEventType.AUTH_FAILURE,
            AuditEventType.MFA_FAILURE,
            AuditEventType.ANOMALY_DETECTED,
            AuditEventType.KEY_SUSPENDED,
        }
        
        if event_type in warning_events:
            return AuditSeverity.WARNING
        
        # Error outcomes
        if outcome == "failure":
            return AuditSeverity.ERROR
        
        return AuditSeverity.INFO
    
    def _check_alerts(self, event: AuditEvent):
        """Check if event should trigger alerts."""
        # Critical events always alert
        if event.severity == AuditSeverity.CRITICAL:
            for handler in self._alert_handlers:
                try:
                    handler(event)
                except Exception:
                    pass
    
    def register_alert_handler(self, handler: callable):
        """Register an alert handler."""
        self._alert_handlers.append(handler)
    
    # Convenience methods
    def log_auth_success(
        self,
        user_id: str,
        ip_address: str,
        session_id: str,
        details: Optional[Dict] = None
    ) -> AuditEvent:
        """Log successful authentication."""
        return self.log(
            event_type=AuditEventType.AUTH_SUCCESS,
            actor_id=user_id,
            actor_ip=ip_address,
            session_id=session_id,
            action="authenticate",
            outcome="success",
            message=f"User {user_id} authenticated successfully",
            details=details
        )
    
    def log_auth_failure(
        self,
        user_id: str,
        ip_address: str,
        reason: str,
        details: Optional[Dict] = None
    ) -> AuditEvent:
        """Log failed authentication."""
        return self.log(
            event_type=AuditEventType.AUTH_FAILURE,
            actor_id=user_id,
            actor_ip=ip_address,
            action="authenticate",
            outcome="failure",
            message=f"Authentication failed for {user_id}: {reason}",
            details=details
        )
    
    def log_key_created(
        self,
        user_id: str,
        key_id: str,
        security_level: str,
        details: Optional[Dict] = None
    ) -> AuditEvent:
        """Log key creation."""
        return self.log(
            event_type=AuditEventType.KEY_CREATED,
            actor_id=user_id,
            target_type="dna_key",
            target_id=key_id,
            action="create_key",
            outcome="success",
            message=f"DNA key {key_id} created with security level {security_level}",
            details={"security_level": security_level, **(details or {})}
        )
    
    def log_threat_detected(
        self,
        source_ip: str,
        threat_type: str,
        severity: str,
        details: Optional[Dict] = None
    ) -> AuditEvent:
        """Log threat detection."""
        return self.log(
            event_type=AuditEventType.THREAT_DETECTED,
            actor_ip=source_ip,
            action="threat_detection",
            outcome="success",
            message=f"Threat detected from {source_ip}: {threat_type}",
            severity=AuditSeverity.CRITICAL,
            details={"threat_type": threat_type, "severity": severity, **(details or {})}
        )
    
    def query(self, **kwargs) -> List[AuditEvent]:
        """Query audit events."""
        return self._storage.query(**kwargs)
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit statistics."""
        return self._storage.get_statistics(hours)
    
    def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Generate a compliance report."""
        events = self._storage.query(
            start_time=start_time,
            end_time=end_time,
            limit=100000
        )
        
        report = {
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "period_start": start_time.isoformat(),
            "period_end": end_time.isoformat(),
            "total_events": len(events),
            "summary": {
                "authentication_events": 0,
                "key_management_events": 0,
                "security_events": 0,
                "administrative_events": 0
            },
            "auth_statistics": {
                "total_attempts": 0,
                "successful": 0,
                "failed": 0,
                "mfa_challenges": 0
            },
            "security_incidents": [],
            "compliance_status": "compliant"
        }
        
        for event in events:
            if event.category == AuditEventCategory.AUTHENTICATION:
                report["summary"]["authentication_events"] += 1
                if event.event_type == AuditEventType.AUTH_ATTEMPT:
                    report["auth_statistics"]["total_attempts"] += 1
                elif event.event_type == AuditEventType.AUTH_SUCCESS:
                    report["auth_statistics"]["successful"] += 1
                elif event.event_type == AuditEventType.AUTH_FAILURE:
                    report["auth_statistics"]["failed"] += 1
                elif event.event_type == AuditEventType.MFA_CHALLENGE:
                    report["auth_statistics"]["mfa_challenges"] += 1
            
            elif event.category == AuditEventCategory.KEY_MANAGEMENT:
                report["summary"]["key_management_events"] += 1
            
            elif event.category == AuditEventCategory.SECURITY:
                report["summary"]["security_events"] += 1
                if event.severity in [AuditSeverity.CRITICAL, AuditSeverity.ERROR]:
                    incident = {
                        "event_id": event.event_id,
                        "timestamp": event.timestamp.isoformat(),
                        "type": event.event_type.value,
                        "message": event.message
                    }
                    if include_details:
                        incident["details"] = event.details
                    report["security_incidents"].append(incident)
            
            elif event.category == AuditEventCategory.ADMINISTRATIVE:
                report["summary"]["administrative_events"] += 1
        
        return report


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "AuditEventCategory",
    "AuditEventType",
    "AuditSeverity",
    "AuditEvent",
    "AuditLogStorage",
    "AuditLogger",
]
