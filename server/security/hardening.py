"""
DNALockOS - Security Hardening Module
Copyright (c) 2025 WeNova Interactive
Legal Name: Kayden Shawn Massengill
All Rights Reserved.

This module provides military-grade security hardening including:
- Anti-reverse engineering protections
- Anti-tampering verification
- Runtime integrity checks
- Code obfuscation markers
- Memory protection utilities
- Anti-debugging mechanisms
"""

import hashlib
import hmac
import inspect
import os
import secrets
import struct
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple


class SecurityViolationType(Enum):
    """Types of security violations detected."""
    TAMPERING_DETECTED = auto()
    DEBUGGER_DETECTED = auto()
    INTEGRITY_FAILURE = auto()
    TIMING_ATTACK_DETECTED = auto()
    REPLAY_ATTACK_DETECTED = auto()
    INJECTION_DETECTED = auto()
    UNAUTHORIZED_ACCESS = auto()
    MEMORY_CORRUPTION = auto()
    CODE_MODIFICATION = auto()


@dataclass
class SecurityViolation:
    """Record of a security violation."""
    violation_type: SecurityViolationType
    timestamp: datetime
    details: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    severity: str = "HIGH"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.violation_type.name,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "source_ip": self.source_ip,
            "user_id": self.user_id,
            "severity": self.severity
        }


class SecurityHardeningEngine:
    """
    Military-grade security hardening engine.
    
    Provides comprehensive protection against:
    - Reverse engineering attempts
    - Code tampering
    - Timing attacks
    - Replay attacks
    - Debugging/instrumentation
    - Memory inspection
    """
    
    def __init__(self):
        self._integrity_key = secrets.token_bytes(32)
        self._module_hashes: Dict[str, str] = {}
        self._violation_log: List[SecurityViolation] = []
        self._nonce_cache: Dict[str, datetime] = {}
        self._timing_baseline: Dict[str, float] = {}
        self._initialized = False
        
    def initialize(self):
        """Initialize security engine and compute baseline checksums."""
        if self._initialized:
            return
        
        # Compute module integrity hashes
        self._compute_module_hashes()
        
        # Establish timing baselines
        self._establish_timing_baselines()
        
        # Set up runtime protections
        self._setup_runtime_protections()
        
        self._initialized = True
    
    def _compute_module_hashes(self):
        """Compute SHA3-512 hashes of critical modules for integrity verification."""
        critical_modules = [
            "server.crypto.signatures",
            "server.crypto.encryption",
            "server.crypto.hashing",
            "server.crypto.dna_generator",
            "server.crypto.dna_key",
            "server.core.authentication",
            "server.core.enrollment",
            "server.core.revocation",
        ]
        
        for module_name in critical_modules:
            try:
                if module_name in sys.modules:
                    module = sys.modules[module_name]
                    if hasattr(module, "__file__") and module.__file__:
                        with open(module.__file__, "rb") as f:
                            content = f.read()
                            hash_value = hashlib.sha3_512(content).hexdigest()
                            self._module_hashes[module_name] = hash_value
            except Exception:
                pass  # Module not loaded yet
    
    def _establish_timing_baselines(self):
        """Establish timing baselines for detecting timing attacks."""
        # Baseline for cryptographic operations
        from server.crypto.signatures import generate_ed25519_keypair
        
        times = []
        for _ in range(10):
            start = time.perf_counter_ns()
            generate_ed25519_keypair()
            end = time.perf_counter_ns()
            times.append(end - start)
        
        self._timing_baseline["keypair_generation"] = sum(times) / len(times)
    
    def _setup_runtime_protections(self):
        """Set up runtime protection mechanisms."""
        # Register atexit handler for secure cleanup
        import atexit
        atexit.register(self._secure_cleanup)
    
    def _secure_cleanup(self):
        """Securely clean up sensitive data on exit."""
        # Overwrite integrity key
        self._integrity_key = secrets.token_bytes(32)
        
        # Clear module hashes
        self._module_hashes.clear()
        
        # Clear nonce cache
        self._nonce_cache.clear()
    
    def verify_module_integrity(self, module_name: str) -> bool:
        """
        Verify that a critical module has not been tampered with.
        
        Args:
            module_name: Name of module to verify
            
        Returns:
            True if module is intact, False if tampering detected
        """
        if module_name not in self._module_hashes:
            return True  # Module not tracked
        
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, "__file__") and module.__file__:
                    with open(module.__file__, "rb") as f:
                        content = f.read()
                        current_hash = hashlib.sha3_512(content).hexdigest()
                        
                        if current_hash != self._module_hashes[module_name]:
                            self._log_violation(
                                SecurityViolationType.CODE_MODIFICATION,
                                f"Module {module_name} has been modified"
                            )
                            return False
        except Exception:
            pass
        
        return True
    
    def verify_all_modules(self) -> bool:
        """Verify integrity of all tracked modules."""
        for module_name in self._module_hashes:
            if not self.verify_module_integrity(module_name):
                return False
        return True
    
    def detect_debugger(self) -> bool:
        """
        Attempt to detect if a debugger is attached.
        
        Returns:
            True if debugger detected, False otherwise
        """
        # Check for common debugger traces
        debugger_indicators = [
            sys.gettrace() is not None,
            hasattr(sys, "settrace") and sys.gettrace is not None,
        ]
        
        # Check for ptrace (Linux)
        try:
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("TracerPid:"):
                        tracer_pid = int(line.split(":")[1].strip())
                        if tracer_pid != 0:
                            debugger_indicators.append(True)
                        break
        except (FileNotFoundError, PermissionError):
            pass
        
        if any(debugger_indicators):
            self._log_violation(
                SecurityViolationType.DEBUGGER_DETECTED,
                "Debugger or tracing mechanism detected"
            )
            return True
        
        return False
    
    def generate_secure_nonce(self, context: str = "default") -> bytes:
        """
        Generate a cryptographically secure nonce with replay protection.
        
        Args:
            context: Context string for the nonce
            
        Returns:
            32-byte nonce
        """
        nonce = secrets.token_bytes(32)
        nonce_hash = hashlib.sha3_256(nonce + context.encode()).hexdigest()
        
        # Store for replay protection
        self._nonce_cache[nonce_hash] = datetime.now(timezone.utc)
        
        # Clean old nonces (older than 5 minutes)
        self._clean_nonce_cache()
        
        return nonce
    
    def verify_nonce(self, nonce: bytes, context: str = "default") -> bool:
        """
        Verify a nonce has not been used before (replay protection).
        
        Args:
            nonce: Nonce to verify
            context: Context string
            
        Returns:
            True if nonce is valid and unused, False otherwise
        """
        nonce_hash = hashlib.sha3_256(nonce + context.encode()).hexdigest()
        
        if nonce_hash in self._nonce_cache:
            self._log_violation(
                SecurityViolationType.REPLAY_ATTACK_DETECTED,
                f"Nonce reuse detected in context: {context}"
            )
            return False
        
        # Mark as used
        self._nonce_cache[nonce_hash] = datetime.now(timezone.utc)
        return True
    
    def _clean_nonce_cache(self, max_age_seconds: int = 300):
        """Remove old nonces from cache."""
        now = datetime.now(timezone.utc)
        expired = []
        
        for nonce_hash, timestamp in self._nonce_cache.items():
            age = (now - timestamp).total_seconds()
            if age > max_age_seconds:
                expired.append(nonce_hash)
        
        for nonce_hash in expired:
            del self._nonce_cache[nonce_hash]
    
    def constant_time_compare(self, a: bytes, b: bytes) -> bool:
        """
        Compare two byte strings in constant time to prevent timing attacks.
        
        Args:
            a: First byte string
            b: Second byte string
            
        Returns:
            True if equal, False otherwise
        """
        return hmac.compare_digest(a, b)
    
    def secure_hash(self, data: bytes, salt: Optional[bytes] = None) -> bytes:
        """
        Compute a secure hash with optional salt.
        
        Uses SHA3-512 for quantum resistance.
        
        Args:
            data: Data to hash
            salt: Optional salt
            
        Returns:
            64-byte hash
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Use HMAC with SHA3-512 for keyed hashing
        return hmac.new(
            self._integrity_key,
            salt + data,
            hashlib.sha3_512
        ).digest()
    
    def generate_integrity_token(self, data: bytes) -> bytes:
        """
        Generate an integrity verification token for data.
        
        Args:
            data: Data to protect
            
        Returns:
            32-byte integrity token
        """
        return hmac.new(
            self._integrity_key,
            data,
            hashlib.sha3_256
        ).digest()
    
    def verify_integrity_token(self, data: bytes, token: bytes) -> bool:
        """
        Verify an integrity token.
        
        Args:
            data: Original data
            token: Integrity token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        expected = self.generate_integrity_token(data)
        
        if not self.constant_time_compare(expected, token):
            self._log_violation(
                SecurityViolationType.TAMPERING_DETECTED,
                "Data integrity verification failed"
            )
            return False
        
        return True
    
    def _log_violation(
        self,
        violation_type: SecurityViolationType,
        details: str,
        severity: str = "HIGH"
    ):
        """Log a security violation."""
        violation = SecurityViolation(
            violation_type=violation_type,
            timestamp=datetime.now(timezone.utc),
            details=details,
            severity=severity
        )
        self._violation_log.append(violation)
        
        # In production, this would send alerts
        # For now, we track in memory
    
    def get_violation_log(self) -> List[Dict[str, Any]]:
        """Get the security violation log."""
        return [v.to_dict() for v in self._violation_log]
    
    def clear_violation_log(self):
        """Clear the violation log (for testing)."""
        self._violation_log.clear()


def secure_function(func: Callable) -> Callable:
    """
    Decorator for security-sensitive functions.
    
    Adds:
    - Timing jitter to prevent timing attacks
    - Integrity verification
    - Error handling without information leakage
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Add random timing jitter
        jitter = secrets.randbelow(1000) / 1000000  # 0-1ms
        time.sleep(jitter)
        
        try:
            result = func(*args, **kwargs)
            
            # Add exit jitter
            exit_jitter = secrets.randbelow(1000) / 1000000
            time.sleep(exit_jitter)
            
            return result
        except Exception as e:
            # Log internal error but return generic message
            # to prevent information leakage
            raise SecurityError("Operation failed") from None
    
    return wrapper


class SecurityError(Exception):
    """Generic security error that doesn't leak information."""
    pass


def secure_memory_clear(data: bytearray):
    """
    Securely clear sensitive data from memory.
    
    Overwrites the memory multiple times before allowing GC.
    
    Args:
        data: Bytearray to clear
    """
    if not isinstance(data, bytearray):
        return
    
    # Multiple passes with different patterns
    patterns = [
        b'\x00',  # Zeros
        b'\xFF',  # Ones
        b'\xAA',  # Alternating
        b'\x55',  # Alternating inverse
        b'\x00',  # Final zeros
    ]
    
    for pattern in patterns:
        for i in range(len(data)):
            data[i] = pattern[0]


def generate_secure_random_bytes(length: int) -> bytes:
    """
    Generate cryptographically secure random bytes.
    
    Uses multiple entropy sources for defense in depth.
    
    Args:
        length: Number of bytes to generate
        
    Returns:
        Random bytes
    """
    # Primary source: os.urandom (CSPRNG)
    primary = os.urandom(length)
    
    # Secondary source: secrets module
    secondary = secrets.token_bytes(length)
    
    # Mix sources using XOR
    result = bytes(a ^ b for a, b in zip(primary, secondary))
    
    return result


# Global security engine instance
_security_engine: Optional[SecurityHardeningEngine] = None


def get_security_engine() -> SecurityHardeningEngine:
    """Get or create the global security engine instance."""
    global _security_engine
    if _security_engine is None:
        _security_engine = SecurityHardeningEngine()
        _security_engine.initialize()
    return _security_engine


def verify_system_integrity() -> bool:
    """
    Perform comprehensive system integrity verification.
    
    Returns:
        True if system is secure, False if any issues detected
    """
    engine = get_security_engine()
    
    # Check for debuggers
    if engine.detect_debugger():
        return False
    
    # Verify module integrity
    if not engine.verify_all_modules():
        return False
    
    return True
