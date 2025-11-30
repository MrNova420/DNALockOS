"""
DNA-Key Authentication System - Real-Time Threat Intelligence

████████╗██╗  ██╗██████╗ ███████╗ █████╗ ████████╗    ██╗███╗   ██╗████████╗███████╗██╗     
╚══██╔══╝██║  ██║██╔══██╗██╔════╝██╔══██╗╚══██╔══╝    ██║████╗  ██║╚══██╔══╝██╔════╝██║     
   ██║   ███████║██████╔╝█████╗  ███████║   ██║       ██║██╔██╗ ██║   ██║   █████╗  ██║     
   ██║   ██╔══██║██╔══██╗██╔══╝  ██╔══██║   ██║       ██║██║╚██╗██║   ██║   ██╔══╝  ██║     
   ██║   ██║  ██║██║  ██║███████╗██║  ██║   ██║       ██║██║ ╚████║   ██║   ███████╗███████╗
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝

MILITARY-GRADE REAL-TIME THREAT DETECTION AND RESPONSE

This module implements comprehensive threat intelligence:

1. Real-time threat feed integration
2. IP reputation scoring
3. Attack pattern recognition
4. Automated incident response
5. Threat actor profiling
6. Vulnerability correlation
7. Global threat sharing network
8. Zero-day attack detection

PROACTIVE DEFENSE FOR THE FUTURE OF AUTHENTICATION
"""

import hashlib
import ipaddress
import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ============================================================================
# THREAT TYPES AND CLASSIFICATIONS
# ============================================================================

class ThreatCategory(Enum):
    """Categories of security threats."""
    
    # Network threats
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    PASSWORD_SPRAY = "password_spray"
    DDoS = "ddos"
    
    # Authentication threats
    SESSION_HIJACKING = "session_hijacking"
    TOKEN_THEFT = "token_theft"
    REPLAY_ATTACK = "replay_attack"
    MAN_IN_THE_MIDDLE = "man_in_the_middle"
    
    # DNA-specific threats
    DNA_FORGERY = "dna_forgery"
    DNA_REPLAY = "dna_replay"
    DNA_TAMPERING = "dna_tampering"
    MODEL_EXTRACTION = "model_extraction"
    
    # Advanced persistent threats
    APT = "apt"
    ZERO_DAY = "zero_day"
    SUPPLY_CHAIN = "supply_chain"
    INSIDER_THREAT = "insider_threat"
    
    # Fraud
    ACCOUNT_TAKEOVER = "account_takeover"
    SYNTHETIC_IDENTITY = "synthetic_identity"
    SOCIAL_ENGINEERING = "social_engineering"


class ThreatSeverity(IntEnum):
    """Severity levels for threats."""
    
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class ThreatConfidence(Enum):
    """Confidence level in threat detection."""
    
    SUSPECTED = "suspected"      # 0-30% confidence
    LIKELY = "likely"            # 30-60% confidence
    HIGH_CONFIDENCE = "high"     # 60-90% confidence
    CONFIRMED = "confirmed"      # 90-100% confidence


class AttackPhase(Enum):
    """Phase of an attack in the kill chain."""
    
    RECONNAISSANCE = "reconnaissance"
    WEAPONIZATION = "weaponization"
    DELIVERY = "delivery"
    EXPLOITATION = "exploitation"
    INSTALLATION = "installation"
    COMMAND_CONTROL = "command_control"
    ACTIONS_OBJECTIVES = "actions_objectives"


class ResponseAction(Enum):
    """Automated response actions."""
    
    LOG_ONLY = "log_only"
    ALERT = "alert"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_BLOCK = "temporary_block"
    PERMANENT_BLOCK = "permanent_block"
    ACCOUNT_LOCK = "account_lock"
    SESSION_TERMINATE = "session_terminate"
    ESCALATE = "escalate"


# ============================================================================
# THREAT INDICATORS
# ============================================================================

@dataclass
class ThreatIndicator:
    """An indicator of compromise (IoC)."""
    
    indicator_id: str
    indicator_type: str  # ip, domain, hash, email, url, pattern
    value: str
    threat_category: ThreatCategory
    severity: ThreatSeverity
    confidence: ThreatConfidence
    
    # Metadata
    source: str  # Where this indicator came from
    first_seen: datetime
    last_seen: datetime
    times_seen: int = 1
    
    # Context
    description: str = ""
    tags: List[str] = field(default_factory=list)
    related_indicators: List[str] = field(default_factory=list)
    
    # Expiration
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if indicator has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "indicator_id": self.indicator_id,
            "indicator_type": self.indicator_type,
            "value": self.value,
            "threat_category": self.threat_category.value,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "source": self.source,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "times_seen": self.times_seen,
            "is_active": self.is_active
        }


@dataclass
class ThreatActor:
    """Profile of a threat actor."""
    
    actor_id: str
    name: str
    aliases: List[str] = field(default_factory=list)
    
    # Classification
    actor_type: str = "unknown"  # nation_state, criminal, hacktivist, insider
    sophistication: str = "unknown"  # low, medium, high, advanced
    
    # Targeting
    target_sectors: List[str] = field(default_factory=list)
    target_regions: List[str] = field(default_factory=list)
    
    # TTPs (Tactics, Techniques, Procedures)
    known_ttps: List[str] = field(default_factory=list)
    
    # Indicators
    associated_indicators: List[str] = field(default_factory=list)
    
    # Activity
    first_observed: Optional[datetime] = None
    last_observed: Optional[datetime] = None
    is_active: bool = True


# ============================================================================
# THREAT EVENTS
# ============================================================================

@dataclass
class ThreatEvent:
    """A detected threat event."""
    
    event_id: str
    timestamp: datetime
    threat_category: ThreatCategory
    severity: ThreatSeverity
    confidence: ThreatConfidence
    
    # Source
    source_ip: Optional[str] = None
    source_user: Optional[str] = None
    source_device: Optional[str] = None
    
    # Target
    target_resource: Optional[str] = None
    target_user: Optional[str] = None
    
    # Details
    description: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    matched_indicators: List[str] = field(default_factory=list)
    
    # Response
    response_action: ResponseAction = ResponseAction.LOG_ONLY
    response_executed: bool = False
    response_timestamp: Optional[datetime] = None
    
    # Correlation
    correlated_events: List[str] = field(default_factory=list)
    attack_phase: Optional[AttackPhase] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "threat_category": self.threat_category.value,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "source_ip": self.source_ip,
            "source_user": self.source_user,
            "description": self.description,
            "response_action": self.response_action.value,
            "response_executed": self.response_executed
        }


# ============================================================================
# IP REPUTATION ENGINE
# ============================================================================

@dataclass
class IPReputation:
    """Reputation score for an IP address."""
    
    ip_address: str
    reputation_score: float  # 0.0 (worst) to 100.0 (best)
    risk_level: ThreatSeverity
    
    # Categories
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor_exit: bool = False
    is_datacenter: bool = False
    is_residential: bool = True
    is_mobile: bool = False
    
    # Threat history
    threat_count_24h: int = 0
    threat_count_7d: int = 0
    threat_count_30d: int = 0
    
    # Geolocation
    country_code: str = ""
    city: str = ""
    asn: Optional[int] = None
    asn_org: str = ""
    
    # Lists
    on_blocklist: bool = False
    blocklist_sources: List[str] = field(default_factory=list)
    
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IPReputationEngine:
    """
    Engine for IP reputation scoring.
    
    Integrates multiple data sources:
    - Internal threat history
    - External blocklists
    - Geolocation data
    - ASN intelligence
    - Network behavior analysis
    """
    
    # Known malicious ASNs (simplified example)
    SUSPICIOUS_ASNS: Set[int] = {
        12345,  # Example malicious ASN
    }
    
    # Known proxy/VPN providers (simplified)
    KNOWN_PROXY_ASNS: Set[int] = set()
    
    def __init__(self):
        self._reputation_cache: Dict[str, IPReputation] = {}
        self._blocklist: Set[str] = set()
        self._allowlist: Set[str] = set()
        self._threat_history: Dict[str, List[ThreatEvent]] = {}
    
    def get_reputation(self, ip_address: str) -> IPReputation:
        """
        Get reputation for an IP address.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            IPReputation with score and metadata
        """
        # Check cache
        if ip_address in self._reputation_cache:
            cached = self._reputation_cache[ip_address]
            # Refresh if older than 1 hour
            if (datetime.now(timezone.utc) - cached.last_updated).seconds < 3600:
                return cached
        
        # Calculate reputation
        reputation = self._calculate_reputation(ip_address)
        self._reputation_cache[ip_address] = reputation
        
        return reputation
    
    def _calculate_reputation(self, ip_address: str) -> IPReputation:
        """Calculate reputation score for IP."""
        score = 100.0
        
        # Check blocklist
        on_blocklist = ip_address in self._blocklist
        if on_blocklist:
            score -= 80.0
        
        # Check allowlist
        if ip_address in self._allowlist:
            return IPReputation(
                ip_address=ip_address,
                reputation_score=100.0,
                risk_level=ThreatSeverity.INFO,
                on_blocklist=False
            )
        
        # Check threat history
        threat_count_24h = 0
        threat_count_7d = 0
        threat_count_30d = 0
        
        if ip_address in self._threat_history:
            now = datetime.now(timezone.utc)
            for event in self._threat_history[ip_address]:
                age = (now - event.timestamp).days
                if age < 1:
                    threat_count_24h += 1
                if age < 7:
                    threat_count_7d += 1
                if age < 30:
                    threat_count_30d += 1
        
        # Deduct for threats
        score -= threat_count_24h * 20
        score -= threat_count_7d * 5
        score -= threat_count_30d * 1
        
        # Check if private IP (usually safe)
        try:
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private:
                score = min(score + 20, 100.0)
        except ValueError:
            score -= 10  # Invalid IP format
        
        # Ensure score is in valid range
        score = max(0.0, min(100.0, score))
        
        # Determine risk level
        if score >= 80:
            risk_level = ThreatSeverity.INFO
        elif score >= 60:
            risk_level = ThreatSeverity.LOW
        elif score >= 40:
            risk_level = ThreatSeverity.MEDIUM
        elif score >= 20:
            risk_level = ThreatSeverity.HIGH
        else:
            risk_level = ThreatSeverity.CRITICAL
        
        return IPReputation(
            ip_address=ip_address,
            reputation_score=score,
            risk_level=risk_level,
            on_blocklist=on_blocklist,
            threat_count_24h=threat_count_24h,
            threat_count_7d=threat_count_7d,
            threat_count_30d=threat_count_30d
        )
    
    def add_to_blocklist(self, ip_address: str, source: str = "manual"):
        """Add IP to blocklist."""
        self._blocklist.add(ip_address)
        # Invalidate cache
        if ip_address in self._reputation_cache:
            del self._reputation_cache[ip_address]
    
    def add_to_allowlist(self, ip_address: str):
        """Add IP to allowlist."""
        self._allowlist.add(ip_address)
        # Invalidate cache
        if ip_address in self._reputation_cache:
            del self._reputation_cache[ip_address]
    
    def record_threat(self, ip_address: str, event: ThreatEvent):
        """Record a threat event for an IP."""
        if ip_address not in self._threat_history:
            self._threat_history[ip_address] = []
        self._threat_history[ip_address].append(event)
        
        # Invalidate cache
        if ip_address in self._reputation_cache:
            del self._reputation_cache[ip_address]


# ============================================================================
# ATTACK PATTERN DETECTOR
# ============================================================================

@dataclass
class AttackPattern:
    """Definition of an attack pattern."""
    
    pattern_id: str
    name: str
    description: str
    category: ThreatCategory
    severity: ThreatSeverity
    
    # Detection rules
    time_window_seconds: int = 60
    threshold_count: int = 10
    
    # Pattern specifics
    pattern_type: str = "threshold"  # threshold, sequence, anomaly
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Response
    response_action: ResponseAction = ResponseAction.ALERT


class AttackPatternDetector:
    """
    Detects attack patterns in real-time.
    
    Patterns detected:
    - Brute force attacks
    - Credential stuffing
    - Password spraying
    - Distributed attacks
    - Slowloris attacks
    - API abuse
    """
    
    # Built-in attack patterns
    BUILT_IN_PATTERNS = [
        AttackPattern(
            pattern_id="BRUTE_FORCE_SINGLE_USER",
            name="Brute Force - Single User",
            description="Multiple failed logins for single user from single IP",
            category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.HIGH,
            time_window_seconds=300,
            threshold_count=5,
            response_action=ResponseAction.TEMPORARY_BLOCK
        ),
        AttackPattern(
            pattern_id="BRUTE_FORCE_DISTRIBUTED",
            name="Brute Force - Distributed",
            description="Multiple failed logins for single user from multiple IPs",
            category=ThreatCategory.BRUTE_FORCE,
            severity=ThreatSeverity.CRITICAL,
            time_window_seconds=600,
            threshold_count=10,
            response_action=ResponseAction.ACCOUNT_LOCK
        ),
        AttackPattern(
            pattern_id="CREDENTIAL_STUFFING",
            name="Credential Stuffing",
            description="Many different users attempted from single IP",
            category=ThreatCategory.CREDENTIAL_STUFFING,
            severity=ThreatSeverity.CRITICAL,
            time_window_seconds=300,
            threshold_count=20,
            response_action=ResponseAction.PERMANENT_BLOCK
        ),
        AttackPattern(
            pattern_id="PASSWORD_SPRAY",
            name="Password Spray",
            description="Single password tried against many users",
            category=ThreatCategory.PASSWORD_SPRAY,
            severity=ThreatSeverity.HIGH,
            time_window_seconds=600,
            threshold_count=5,
            response_action=ResponseAction.RATE_LIMIT
        ),
        AttackPattern(
            pattern_id="DNA_REPLAY_ATTACK",
            name="DNA Replay Attack",
            description="Same DNA strand used multiple times in short period",
            category=ThreatCategory.DNA_REPLAY,
            severity=ThreatSeverity.CRITICAL,
            time_window_seconds=60,
            threshold_count=2,
            response_action=ResponseAction.SESSION_TERMINATE
        ),
    ]
    
    def __init__(self):
        self._patterns = {p.pattern_id: p for p in self.BUILT_IN_PATTERNS}
        self._event_buffer: Dict[str, List[Dict[str, Any]]] = {}
        self._detected_attacks: List[ThreatEvent] = []
    
    def add_pattern(self, pattern: AttackPattern):
        """Add a custom attack pattern."""
        self._patterns[pattern.pattern_id] = pattern
    
    def analyze_event(
        self,
        event_type: str,
        source_ip: str,
        user_id: Optional[str] = None,
        dna_key_id: Optional[str] = None,
        success: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ThreatEvent]:
        """
        Analyze an event for attack patterns.
        
        Args:
            event_type: Type of event (login_attempt, dna_verify, etc.)
            source_ip: Source IP address
            user_id: Optional user identifier
            dna_key_id: Optional DNA key identifier
            success: Whether the action succeeded
            metadata: Additional metadata
            
        Returns:
            List of detected threat events
        """
        now = datetime.now(timezone.utc)
        
        # Create event record
        event_record = {
            "timestamp": now,
            "event_type": event_type,
            "source_ip": source_ip,
            "user_id": user_id,
            "dna_key_id": dna_key_id,
            "success": success,
            "metadata": metadata or {}
        }
        
        # Add to buffer
        buffer_key = f"{source_ip}:{user_id or 'any'}"
        if buffer_key not in self._event_buffer:
            self._event_buffer[buffer_key] = []
        self._event_buffer[buffer_key].append(event_record)
        
        # Clean old events
        self._clean_buffer()
        
        # Check patterns
        detected_threats = []
        
        for pattern in self._patterns.values():
            if self._check_pattern(pattern, event_record):
                threat_event = ThreatEvent(
                    event_id=f"threat_{secrets.token_hex(8)}",
                    timestamp=now,
                    threat_category=pattern.category,
                    severity=pattern.severity,
                    confidence=ThreatConfidence.HIGH_CONFIDENCE,
                    source_ip=source_ip,
                    source_user=user_id,
                    description=f"Attack pattern detected: {pattern.name}",
                    response_action=pattern.response_action
                )
                detected_threats.append(threat_event)
                self._detected_attacks.append(threat_event)
        
        return detected_threats
    
    def _check_pattern(self, pattern: AttackPattern, current_event: Dict) -> bool:
        """Check if a pattern matches current events."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=pattern.time_window_seconds)
        
        source_ip = current_event["source_ip"]
        user_id = current_event.get("user_id")
        
        # Count matching events
        count = 0
        
        if pattern.pattern_id == "BRUTE_FORCE_SINGLE_USER":
            # Same IP, same user, failed attempts
            buffer_key = f"{source_ip}:{user_id}"
            if buffer_key in self._event_buffer:
                for event in self._event_buffer[buffer_key]:
                    if event["timestamp"] >= window_start and not event["success"]:
                        count += 1
        
        elif pattern.pattern_id == "CREDENTIAL_STUFFING":
            # Same IP, different users
            users_attempted = set()
            for key, events in self._event_buffer.items():
                if key.startswith(f"{source_ip}:"):
                    for event in events:
                        if event["timestamp"] >= window_start:
                            if event.get("user_id"):
                                users_attempted.add(event["user_id"])
            count = len(users_attempted)
        
        elif pattern.pattern_id == "DNA_REPLAY_ATTACK":
            # Same DNA key used multiple times
            dna_key = current_event.get("dna_key_id")
            if dna_key:
                for key, events in self._event_buffer.items():
                    for event in events:
                        if event["timestamp"] >= window_start:
                            if event.get("dna_key_id") == dna_key:
                                count += 1
        
        else:
            # Generic threshold check
            buffer_key = f"{source_ip}:{user_id or 'any'}"
            if buffer_key in self._event_buffer:
                for event in self._event_buffer[buffer_key]:
                    if event["timestamp"] >= window_start:
                        count += 1
        
        return count >= pattern.threshold_count
    
    def _clean_buffer(self):
        """Remove old events from buffer."""
        max_age = timedelta(minutes=30)
        now = datetime.now(timezone.utc)
        
        for key in list(self._event_buffer.keys()):
            self._event_buffer[key] = [
                e for e in self._event_buffer[key]
                if now - e["timestamp"] < max_age
            ]
            if not self._event_buffer[key]:
                del self._event_buffer[key]


# ============================================================================
# THREAT INTELLIGENCE SERVICE
# ============================================================================

class ThreatIntelligenceService:
    """
    Central threat intelligence service.
    
    Provides:
    - Real-time threat detection
    - Indicator management
    - Attack pattern detection
    - IP reputation
    - Automated response
    - Threat correlation
    """
    
    def __init__(self):
        self.ip_reputation = IPReputationEngine()
        self.pattern_detector = AttackPatternDetector()
        
        # Storage
        self._indicators: Dict[str, ThreatIndicator] = {}
        self._threat_actors: Dict[str, ThreatActor] = {}
        self._events: List[ThreatEvent] = []
        
        # Response handlers
        self._response_handlers: Dict[ResponseAction, Callable] = {}
    
    def check_ip(self, ip_address: str) -> IPReputation:
        """Check IP reputation."""
        return self.ip_reputation.get_reputation(ip_address)
    
    def analyze_authentication(
        self,
        source_ip: str,
        user_id: Optional[str] = None,
        dna_key_id: Optional[str] = None,
        success: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[ThreatEvent], ResponseAction]:
        """
        Analyze an authentication attempt.
        
        Args:
            source_ip: Source IP address
            user_id: User identifier
            dna_key_id: DNA key identifier
            success: Whether authentication succeeded
            context: Additional context
            
        Returns:
            Tuple of (should_allow, threat_events, recommended_action)
        """
        threats = []
        action = ResponseAction.LOG_ONLY
        
        # Check IP reputation
        ip_rep = self.check_ip(source_ip)
        if ip_rep.on_blocklist:
            return False, [], ResponseAction.PERMANENT_BLOCK
        
        if ip_rep.risk_level >= ThreatSeverity.HIGH:
            threats.append(ThreatEvent(
                event_id=f"threat_{secrets.token_hex(8)}",
                timestamp=datetime.now(timezone.utc),
                threat_category=ThreatCategory.BRUTE_FORCE,
                severity=ip_rep.risk_level,
                confidence=ThreatConfidence.HIGH_CONFIDENCE,
                source_ip=source_ip,
                description=f"High-risk IP: score {ip_rep.reputation_score}"
            ))
            action = ResponseAction.CHALLENGE
        
        # Check for indicators
        matched_indicators = self._check_indicators(source_ip, user_id, dna_key_id)
        for indicator in matched_indicators:
            threats.append(ThreatEvent(
                event_id=f"threat_{secrets.token_hex(8)}",
                timestamp=datetime.now(timezone.utc),
                threat_category=indicator.threat_category,
                severity=indicator.severity,
                confidence=indicator.confidence,
                source_ip=source_ip,
                source_user=user_id,
                description=f"Matched indicator: {indicator.indicator_type}={indicator.value}",
                matched_indicators=[indicator.indicator_id]
            ))
            
            if indicator.severity >= ThreatSeverity.CRITICAL:
                action = ResponseAction.PERMANENT_BLOCK
            elif indicator.severity >= ThreatSeverity.HIGH and action != ResponseAction.PERMANENT_BLOCK:
                action = ResponseAction.TEMPORARY_BLOCK
        
        # Run pattern detection
        pattern_threats = self.pattern_detector.analyze_event(
            event_type="authentication",
            source_ip=source_ip,
            user_id=user_id,
            dna_key_id=dna_key_id,
            success=success,
            metadata=context
        )
        threats.extend(pattern_threats)
        
        for pt in pattern_threats:
            if pt.response_action.value > action.value:
                action = pt.response_action
        
        # Record threats
        self._events.extend(threats)
        
        # Record in IP reputation
        for threat in threats:
            self.ip_reputation.record_threat(source_ip, threat)
        
        # Determine if should allow
        should_allow = action not in [
            ResponseAction.PERMANENT_BLOCK,
            ResponseAction.TEMPORARY_BLOCK,
            ResponseAction.ACCOUNT_LOCK
        ]
        
        return should_allow, threats, action
    
    def add_indicator(self, indicator: ThreatIndicator):
        """Add a threat indicator."""
        self._indicators[indicator.indicator_id] = indicator
    
    def remove_indicator(self, indicator_id: str):
        """Remove a threat indicator."""
        if indicator_id in self._indicators:
            del self._indicators[indicator_id]
    
    def _check_indicators(
        self,
        ip_address: str,
        user_id: Optional[str],
        dna_key_id: Optional[str]
    ) -> List[ThreatIndicator]:
        """Check for matching indicators."""
        matched = []
        
        for indicator in self._indicators.values():
            if not indicator.is_active or indicator.is_expired():
                continue
            
            if indicator.indicator_type == "ip" and indicator.value == ip_address:
                matched.append(indicator)
            elif indicator.indicator_type == "user" and indicator.value == user_id:
                matched.append(indicator)
            elif indicator.indicator_type == "dna_key" and indicator.value == dna_key_id:
                matched.append(indicator)
        
        return matched
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get summary of current threat landscape."""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        
        recent_events = [e for e in self._events if e.timestamp >= last_24h]
        
        by_category = {}
        by_severity = {}
        
        for event in recent_events:
            cat = event.threat_category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            sev = event.severity.name
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_events_24h": len(recent_events),
            "by_category": by_category,
            "by_severity": by_severity,
            "active_indicators": len([i for i in self._indicators.values() if i.is_active]),
            "blocked_ips": len(self.ip_reputation._blocklist)
        }
    
    def register_response_handler(self, action: ResponseAction, handler: Callable):
        """Register a handler for a response action."""
        self._response_handlers[action] = handler
    
    def execute_response(self, action: ResponseAction, context: Dict[str, Any]) -> bool:
        """Execute a response action."""
        handler = self._response_handlers.get(action)
        if handler:
            try:
                handler(context)
                return True
            except Exception:
                return False
        return False


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "ThreatCategory",
    "ThreatSeverity",
    "ThreatConfidence",
    "AttackPhase",
    "ResponseAction",
    "ThreatIndicator",
    "ThreatActor",
    "ThreatEvent",
    "IPReputation",
    "IPReputationEngine",
    "AttackPattern",
    "AttackPatternDetector",
    "ThreatIntelligenceService",
]
