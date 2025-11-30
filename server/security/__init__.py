"""
DNALockOS Security Module
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill
ALL RIGHTS RESERVED.

PROPRIETARY AND CONFIDENTIAL
Unauthorized copying, modification, or distribution is strictly prohibited.

This module provides enterprise-grade security components:

- Neural Authentication: AI-powered behavioral analysis
- Distributed Ledger: Blockchain-based DNA strand registry
- Threat Intelligence: Real-time threat detection
- Session Management: Secure session handling
- Audit Logging: Comprehensive audit trail
- Security Hardening: Anti-tampering and anti-reverse engineering
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

# Security Hardening
from server.security.hardening import (
    SecurityHardeningEngine,
    SecurityViolationType,
    SecurityViolation,
    SecurityError,
    secure_function,
    secure_memory_clear,
    generate_secure_random_bytes,
    get_security_engine,
    verify_system_integrity,
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
    # Security Hardening
    "SecurityHardeningEngine",
    "SecurityViolationType",
    "SecurityViolation",
    "SecurityError",
    "secure_function",
    "secure_memory_clear",
    "generate_secure_random_bytes",
    "get_security_engine",
    "verify_system_integrity",
]

__version__ = "1.0.0"
__author__ = "WeNova Interactive"
__copyright__ = "Copyright (c) 2025 WeNova Interactive - Kayden Shawn Massengill"
__license__ = "Proprietary - All Rights Reserved"
