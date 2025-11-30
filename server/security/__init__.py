"""
DNALockOS Security Module

This module provides enterprise-grade security components:

- Neural Authentication: AI-powered behavioral analysis
- Distributed Ledger: Blockchain-based DNA strand registry
- Threat Intelligence: Real-time threat detection
- Session Management: Secure session handling
- Audit Logging: Comprehensive audit trail
"""

# Neural Auth
from server.security.neural_auth import (
    NeuralAuthenticationCoordinator,
    TypingDynamics,
    MouseDynamics,
    SessionContext,
    NeuralAuthDecision,
    AnomalyDetectionEngine,
    FraudDetectionEngine,
)

# Distributed Ledger
from server.security.distributed_ledger import (
    DNAStrandRegistry,
    BlockchainNetwork,
    DNARegistryEntry,
    DNATransaction,
    Block,
    DNASmartContract,
)

# Threat Intelligence
from server.security.threat_intelligence import (
    ThreatIntelligenceService,
    ThreatIndicator,
    ThreatCategory,
    ThreatSeverity,
    ThreatConfidence,
    IPReputation,
    IPReputationEngine,
    AttackPatternDetector,
)

# Session Management
from server.security.session_management import (
    SessionManager,
    Session,
    SessionToken,
    SessionBinding,
    SessionState,
    SessionType,
    TerminationReason,
    TokenGenerator,
)

# Audit Logging
from server.security.audit_logging import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditEventCategory,
    AuditSeverity,
    AuditLogStorage,
)

__all__ = [
    # Neural Auth
    "NeuralAuthenticationCoordinator",
    "TypingDynamics",
    "MouseDynamics",
    "SessionContext",
    "NeuralAuthDecision",
    "AnomalyDetectionEngine",
    "FraudDetectionEngine",
    # Distributed Ledger
    "DNAStrandRegistry",
    "BlockchainNetwork",
    "DNARegistryEntry",
    "DNATransaction",
    "Block",
    "DNASmartContract",
    # Threat Intelligence
    "ThreatIntelligenceService",
    "ThreatIndicator",
    "ThreatCategory",
    "ThreatSeverity",
    "ThreatConfidence",
    "IPReputation",
    "IPReputationEngine",
    "AttackPatternDetector",
    # Session Management
    "SessionManager",
    "Session",
    "SessionToken",
    "SessionBinding",
    "SessionState",
    "SessionType",
    "TerminationReason",
    "TokenGenerator",
    # Audit Logging
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditEventCategory",
    "AuditSeverity",
    "AuditLogStorage",
]
