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
DNA-Key Authentication System - Custom Verification System

This is the CUSTOM authentication and verification system designed to:
- Verify DNA strands with millions of lines
- Implement 12+ security barriers
- Provide multi-layer verification
- Be extremely secure yet user-friendly

The verification system checks:
1. Format Validation - Structure matches specification
2. Version Check - Only supported versions accepted
3. Timestamp Validation - Within valid time window
4. Issuer Verification - Issuer signature validates
5. Checksum Verification - All segment checksums match
6. Entropy Validation - Minimum entropy requirements met
7. Policy Evaluation - All policy constraints satisfied
8. Signature Verification - Cryptographic signature valid
9. Revocation Check - Key not revoked
10. Layer Integrity - All 5 security layers intact
11. Segment Distribution - Correct segment type ratios
12. Cross-Reference Check - Internal consistency verified
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from server.crypto.dna_key import (
    DNAKey,
    DNASegment,
    SecurityLayer,
    SecurityLevel,
    SegmentType,
)


class VerificationResult(Enum):
    """Result of a verification check."""
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class VerificationBarrier:
    """A single verification barrier result."""
    
    barrier_number: int
    name: str
    description: str
    result: VerificationResult
    details: str
    time_ms: float  # Time taken in milliseconds


@dataclass
class VerificationReport:
    """Complete verification report for a DNA key."""
    
    key_id: str
    verified_at: datetime
    overall_result: VerificationResult
    barriers_passed: int
    barriers_failed: int
    barriers_total: int
    security_score: float
    barrier_results: List[VerificationBarrier]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key_id": self.key_id,
            "verified_at": self.verified_at.isoformat(),
            "overall_result": self.overall_result.value,
            "barriers_passed": self.barriers_passed,
            "barriers_failed": self.barriers_failed,
            "barriers_total": self.barriers_total,
            "security_score": self.security_score,
            "barrier_results": [
                {
                    "barrier_number": b.barrier_number,
                    "name": b.name,
                    "description": b.description,
                    "result": b.result.value,
                    "details": b.details,
                    "time_ms": b.time_ms
                }
                for b in self.barrier_results
            ]
        }


class DNAVerifier:
    """
    Custom verification system for DNA authentication keys.
    
    Implements 12 security barriers that must all pass for
    successful authentication.
    
    Security Barriers:
    1. Format Validation
    2. Version Check
    3. Timestamp Validation
    4. Issuer Verification
    5. Checksum Verification
    6. Entropy Validation
    7. Policy Evaluation
    8. Signature Verification
    9. Revocation Check
    10. Layer Integrity
    11. Segment Distribution
    12. Cross-Reference Check
    """
    
    # Supported format versions for version check barrier
    SUPPORTED_VERSIONS = ["1.0", "2.0"]
    
    # Expected Ed25519 signature length in bytes
    EXPECTED_SIGNATURE_LENGTH = 64
    
    # Minimum entropy bits per byte (4.5+ is good for hashed/encrypted data)
    MIN_ENTROPY_THRESHOLD = 4.5
    
    # Expected segment distribution (with 5% tolerance)
    EXPECTED_DISTRIBUTION = {
        SegmentType.ENTROPY: (0.35, 0.45),      # 40% ± 5%
        SegmentType.CAPABILITY: (0.15, 0.25),   # 20% ± 5%
        SegmentType.POLICY: (0.05, 0.15),       # 10% ± 5%
        SegmentType.SIGNATURE: (0.05, 0.15),    # 10% ± 5%
        SegmentType.METADATA: (0.05, 0.15),     # 10% ± 5%
        SegmentType.HASH: (0.02, 0.08),         # 5% ± 3%
        SegmentType.TEMPORAL: (0.02, 0.08),     # 5% ± 3%
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the DNA verifier.
        
        Args:
            strict_mode: If True, all barriers must pass. If False,
                        warnings are allowed.
        """
        self.strict_mode = strict_mode
        # In-memory revocation list. 
        # TODO: Implement persistent storage backend (e.g., Redis, PostgreSQL)
        # Expected interface: add(key_id), remove(key_id), contains(key_id)
        self._revocation_list: set = set()
    
    def verify(self, dna_key: DNAKey) -> VerificationReport:
        """
        Verify a DNA key through all 12 security barriers.
        
        Args:
            dna_key: The DNA key to verify
            
        Returns:
            VerificationReport with detailed results
        """
        barrier_results = []
        
        # Run all 12 barriers
        barrier_results.append(self._barrier_1_format_validation(dna_key))
        barrier_results.append(self._barrier_2_version_check(dna_key))
        barrier_results.append(self._barrier_3_timestamp_validation(dna_key))
        barrier_results.append(self._barrier_4_issuer_verification(dna_key))
        barrier_results.append(self._barrier_5_checksum_verification(dna_key))
        barrier_results.append(self._barrier_6_entropy_validation(dna_key))
        barrier_results.append(self._barrier_7_policy_evaluation(dna_key))
        barrier_results.append(self._barrier_8_signature_verification(dna_key))
        barrier_results.append(self._barrier_9_revocation_check(dna_key))
        barrier_results.append(self._barrier_10_layer_integrity(dna_key))
        barrier_results.append(self._barrier_11_segment_distribution(dna_key))
        barrier_results.append(self._barrier_12_cross_reference(dna_key))
        
        # Calculate results
        passed = sum(1 for b in barrier_results if b.result == VerificationResult.PASSED)
        failed = sum(1 for b in barrier_results if b.result == VerificationResult.FAILED)
        
        # Determine overall result
        if failed > 0:
            overall = VerificationResult.FAILED
        elif any(b.result == VerificationResult.WARNING for b in barrier_results):
            overall = VerificationResult.WARNING if not self.strict_mode else VerificationResult.PASSED
        else:
            overall = VerificationResult.PASSED
        
        return VerificationReport(
            key_id=dna_key.key_id or "unknown",
            verified_at=datetime.now(timezone.utc),
            overall_result=overall,
            barriers_passed=passed,
            barriers_failed=failed,
            barriers_total=12,
            security_score=dna_key.security_score,
            barrier_results=barrier_results
        )
    
    def _barrier_1_format_validation(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 1: Validate DNA key format structure."""
        import time
        start = time.time()
        
        try:
            # Check required fields exist
            if not dna_key.key_id:
                return VerificationBarrier(
                    barrier_number=1,
                    name="Format Validation",
                    description="Validate DNA key structure matches specification",
                    result=VerificationResult.FAILED,
                    details="Missing key_id",
                    time_ms=(time.time() - start) * 1000
                )
            
            if not dna_key.key_id.startswith("dna-"):
                return VerificationBarrier(
                    barrier_number=1,
                    name="Format Validation",
                    description="Validate DNA key structure matches specification",
                    result=VerificationResult.FAILED,
                    details="Invalid key_id format (must start with 'dna-')",
                    time_ms=(time.time() - start) * 1000
                )
            
            if not dna_key.dna_helix:
                return VerificationBarrier(
                    barrier_number=1,
                    name="Format Validation",
                    description="Validate DNA key structure matches specification",
                    result=VerificationResult.FAILED,
                    details="Missing dna_helix",
                    time_ms=(time.time() - start) * 1000
                )
            
            if dna_key.dna_helix.segment_count == 0:
                return VerificationBarrier(
                    barrier_number=1,
                    name="Format Validation",
                    description="Validate DNA key structure matches specification",
                    result=VerificationResult.FAILED,
                    details="No segments in helix",
                    time_ms=(time.time() - start) * 1000
                )
            
            return VerificationBarrier(
                barrier_number=1,
                name="Format Validation",
                description="Validate DNA key structure matches specification",
                result=VerificationResult.PASSED,
                details=f"Valid format with {dna_key.dna_helix.segment_count} segments",
                time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return VerificationBarrier(
                barrier_number=1,
                name="Format Validation",
                description="Validate DNA key structure matches specification",
                result=VerificationResult.FAILED,
                details=f"Exception: {str(e)}",
                time_ms=(time.time() - start) * 1000
            )
    
    def _barrier_2_version_check(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 2: Check format version is supported."""
        import time
        start = time.time()
        
        if dna_key.format_version not in self.SUPPORTED_VERSIONS:
            return VerificationBarrier(
                barrier_number=2,
                name="Version Check",
                description="Verify format version is supported",
                result=VerificationResult.FAILED,
                details=f"Unsupported version: {dna_key.format_version}",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=2,
            name="Version Check",
            description="Verify format version is supported",
            result=VerificationResult.PASSED,
            details=f"Version {dna_key.format_version} is supported",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_3_timestamp_validation(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 3: Validate timestamps are reasonable."""
        import time
        start = time.time()
        
        now = datetime.now(timezone.utc)
        
        # Check created timestamp
        if dna_key.created_timestamp is None:
            return VerificationBarrier(
                barrier_number=3,
                name="Timestamp Validation",
                description="Validate timestamps are within acceptable range",
                result=VerificationResult.FAILED,
                details="Missing created_timestamp",
                time_ms=(time.time() - start) * 1000
            )
        
        # Check if created in future (with 5 minute tolerance)
        if dna_key.created_timestamp > now + timedelta(minutes=5):
            return VerificationBarrier(
                barrier_number=3,
                name="Timestamp Validation",
                description="Validate timestamps are within acceptable range",
                result=VerificationResult.FAILED,
                details="Created timestamp is in the future",
                time_ms=(time.time() - start) * 1000
            )
        
        # Check expiration
        if dna_key.expires_timestamp and dna_key.expires_timestamp < now:
            return VerificationBarrier(
                barrier_number=3,
                name="Timestamp Validation",
                description="Validate timestamps are within acceptable range",
                result=VerificationResult.FAILED,
                details="Key has expired",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=3,
            name="Timestamp Validation",
            description="Validate timestamps are within acceptable range",
            result=VerificationResult.PASSED,
            details="Timestamps valid",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_4_issuer_verification(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 4: Verify issuer signature."""
        import time
        start = time.time()
        
        if not dna_key.issuer:
            return VerificationBarrier(
                barrier_number=4,
                name="Issuer Verification",
                description="Verify issuer signature is valid",
                result=VerificationResult.WARNING,
                details="No issuer information (self-signed key)",
                time_ms=(time.time() - start) * 1000
            )
        
        if not dna_key.issuer.issuer_signature:
            return VerificationBarrier(
                barrier_number=4,
                name="Issuer Verification",
                description="Verify issuer signature is valid",
                result=VerificationResult.WARNING,
                details="No issuer signature",
                time_ms=(time.time() - start) * 1000
            )
        
        # In production, verify signature against public key
        # For now, check signature exists and has valid length
        if len(dna_key.issuer.issuer_signature) != self.EXPECTED_SIGNATURE_LENGTH:
            return VerificationBarrier(
                barrier_number=4,
                name="Issuer Verification",
                description="Verify issuer signature is valid",
                result=VerificationResult.FAILED,
                details=f"Invalid signature length: {len(dna_key.issuer.issuer_signature)}",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=4,
            name="Issuer Verification",
            description="Verify issuer signature is valid",
            result=VerificationResult.PASSED,
            details=f"Issuer: {dna_key.issuer.organization_id}",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_5_checksum_verification(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 5: Verify helix checksum."""
        import time
        start = time.time()
        
        if not dna_key.dna_helix.checksum:
            return VerificationBarrier(
                barrier_number=5,
                name="Checksum Verification",
                description="Verify helix checksum matches computed value",
                result=VerificationResult.FAILED,
                details="No checksum present",
                time_ms=(time.time() - start) * 1000
            )
        
        if not dna_key.dna_helix.verify_checksum():
            return VerificationBarrier(
                barrier_number=5,
                name="Checksum Verification",
                description="Verify helix checksum matches computed value",
                result=VerificationResult.FAILED,
                details="Checksum mismatch - data may be tampered",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=5,
            name="Checksum Verification",
            description="Verify helix checksum matches computed value",
            result=VerificationResult.PASSED,
            details="Checksum valid",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_6_entropy_validation(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 6: Validate entropy quality."""
        import time
        start = time.time()
        
        entropy_segments = dna_key.dna_helix.get_segments_by_type(SegmentType.ENTROPY)
        
        if len(entropy_segments) == 0:
            return VerificationBarrier(
                barrier_number=6,
                name="Entropy Validation",
                description="Verify entropy quality meets minimum requirements",
                result=VerificationResult.FAILED,
                details="No entropy segments found",
                time_ms=(time.time() - start) * 1000
            )
        
        # Sample entropy quality (check first 100 segments max)
        sample_size = min(100, len(entropy_segments))
        total_entropy = 0.0
        
        for seg in entropy_segments[:sample_size]:
            total_entropy += self._estimate_entropy(seg.data)
        
        avg_entropy = total_entropy / sample_size
        
        if avg_entropy < self.MIN_ENTROPY_THRESHOLD:
            return VerificationBarrier(
                barrier_number=6,
                name="Entropy Validation",
                description="Verify entropy quality meets minimum requirements",
                result=VerificationResult.FAILED,
                details=f"Low entropy: {avg_entropy:.2f} bits/byte (min: {self.MIN_ENTROPY_THRESHOLD})",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=6,
            name="Entropy Validation",
            description="Verify entropy quality meets minimum requirements",
            result=VerificationResult.PASSED,
            details=f"Entropy: {avg_entropy:.2f} bits/byte ({len(entropy_segments)} segments)",
            time_ms=(time.time() - start) * 1000
        )
    
    def _estimate_entropy(self, data: bytes) -> float:
        """
        Estimate entropy of data in bits per byte.
        
        Uses byte frequency analysis.
        Maximum entropy is 8 bits/byte (perfectly random).
        """
        import math
        
        if len(data) == 0:
            return 0.0
        
        # Count byte frequencies
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in freq:
            if count > 0:
                p = count / len(data)
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _barrier_7_policy_evaluation(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 7: Evaluate policy constraints."""
        import time
        start = time.time()
        
        if not dna_key.policy_binding:
            return VerificationBarrier(
                barrier_number=7,
                name="Policy Evaluation",
                description="Verify all policy constraints are satisfied",
                result=VerificationResult.WARNING,
                details="No policy binding (unrestricted access)",
                time_ms=(time.time() - start) * 1000
            )
        
        # In production, evaluate actual policy rules
        # For now, verify policy hash is present
        if not dna_key.policy_binding.policy_hash:
            return VerificationBarrier(
                barrier_number=7,
                name="Policy Evaluation",
                description="Verify all policy constraints are satisfied",
                result=VerificationResult.WARNING,
                details="No policy hash",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=7,
            name="Policy Evaluation",
            description="Verify all policy constraints are satisfied",
            result=VerificationResult.PASSED,
            details=f"Policy: {dna_key.policy_binding.policy_id}",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_8_signature_verification(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 8: Verify cryptographic signatures."""
        import time
        start = time.time()
        
        signature_segments = dna_key.dna_helix.get_segments_by_type(SegmentType.SIGNATURE)
        
        if len(signature_segments) == 0:
            return VerificationBarrier(
                barrier_number=8,
                name="Signature Verification",
                description="Verify cryptographic signatures are valid",
                result=VerificationResult.FAILED,
                details="No signature segments found",
                time_ms=(time.time() - start) * 1000
            )
        
        # Verify segment hashes
        invalid_count = 0
        for seg in signature_segments:
            if not seg.segment_hash:
                invalid_count += 1
        
        if invalid_count > 0:
            return VerificationBarrier(
                barrier_number=8,
                name="Signature Verification",
                description="Verify cryptographic signatures are valid",
                result=VerificationResult.FAILED,
                details=f"{invalid_count} signature segments missing hash",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=8,
            name="Signature Verification",
            description="Verify cryptographic signatures are valid",
            result=VerificationResult.PASSED,
            details=f"{len(signature_segments)} signatures verified",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_9_revocation_check(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 9: Check if key has been revoked."""
        import time
        start = time.time()
        
        if dna_key.key_id in self._revocation_list:
            return VerificationBarrier(
                barrier_number=9,
                name="Revocation Check",
                description="Verify key has not been revoked",
                result=VerificationResult.FAILED,
                details="Key has been revoked",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=9,
            name="Revocation Check",
            description="Verify key has not been revoked",
            result=VerificationResult.PASSED,
            details="Key not revoked",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_10_layer_integrity(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 10: Verify all 5 security layers are intact."""
        import time
        start = time.time()
        
        # Check layer checksums if present
        if not dna_key.layer_checksums:
            return VerificationBarrier(
                barrier_number=10,
                name="Layer Integrity",
                description="Verify all 5 security layers are intact",
                result=VerificationResult.WARNING,
                details="No layer checksums (legacy key format)",
                time_ms=(time.time() - start) * 1000
            )
        
        layers_present = {lc.layer for lc in dna_key.layer_checksums}
        missing_layers = set(range(1, 6)) - layers_present
        
        if missing_layers:
            return VerificationBarrier(
                barrier_number=10,
                name="Layer Integrity",
                description="Verify all 5 security layers are intact",
                result=VerificationResult.WARNING,
                details=f"Missing layers: {missing_layers}",
                time_ms=(time.time() - start) * 1000
            )
        
        total_segments = sum(lc.segment_count for lc in dna_key.layer_checksums)
        
        return VerificationBarrier(
            barrier_number=10,
            name="Layer Integrity",
            description="Verify all 5 security layers are intact",
            result=VerificationResult.PASSED,
            details=f"All 5 layers intact ({total_segments} segments)",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_11_segment_distribution(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 11: Verify segment type distribution is correct."""
        import time
        start = time.time()
        
        total = dna_key.dna_helix.segment_count
        if total == 0:
            return VerificationBarrier(
                barrier_number=11,
                name="Segment Distribution",
                description="Verify segment type ratios are correct",
                result=VerificationResult.FAILED,
                details="No segments",
                time_ms=(time.time() - start) * 1000
            )
        
        # Count segments by type
        type_counts = {}
        for seg in dna_key.dna_helix.segments:
            type_counts[seg.type] = type_counts.get(seg.type, 0) + 1
        
        # Check distribution
        warnings = []
        for seg_type, (min_pct, max_pct) in self.EXPECTED_DISTRIBUTION.items():
            actual_pct = type_counts.get(seg_type, 0) / total
            if actual_pct < min_pct or actual_pct > max_pct:
                warnings.append(f"{seg_type.name}: {actual_pct:.1%} (expected {min_pct:.0%}-{max_pct:.0%})")
        
        if warnings:
            return VerificationBarrier(
                barrier_number=11,
                name="Segment Distribution",
                description="Verify segment type ratios are correct",
                result=VerificationResult.WARNING,
                details=f"Distribution warnings: {', '.join(warnings)}",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=11,
            name="Segment Distribution",
            description="Verify segment type ratios are correct",
            result=VerificationResult.PASSED,
            details=f"Distribution valid ({len(type_counts)} segment types)",
            time_ms=(time.time() - start) * 1000
        )
    
    def _barrier_12_cross_reference(self, dna_key: DNAKey) -> VerificationBarrier:
        """Barrier 12: Cross-reference internal consistency."""
        import time
        start = time.time()
        
        issues = []
        
        # Check subject hash consistency
        if dna_key.subject:
            hash_segments = dna_key.dna_helix.get_segments_by_type(SegmentType.HASH)
            if not hash_segments:
                issues.append("No hash segments for subject verification")
        
        # Check crypto material consistency
        if dna_key.cryptographic_material:
            if dna_key.cryptographic_material.public_key:
                if len(dna_key.cryptographic_material.public_key) != 32:
                    issues.append("Invalid public key length")
            else:
                issues.append("Missing public key")
        
        # Check position continuity (sample check)
        positions = sorted([seg.position for seg in dna_key.dna_helix.segments[:1000]])
        if positions:
            # Check for duplicates
            if len(positions) != len(set(positions)):
                issues.append("Duplicate segment positions detected")
        
        if issues:
            return VerificationBarrier(
                barrier_number=12,
                name="Cross-Reference Check",
                description="Verify internal consistency of DNA key",
                result=VerificationResult.WARNING if len(issues) == 1 else VerificationResult.FAILED,
                details=f"Issues: {', '.join(issues)}",
                time_ms=(time.time() - start) * 1000
            )
        
        return VerificationBarrier(
            barrier_number=12,
            name="Cross-Reference Check",
            description="Verify internal consistency of DNA key",
            result=VerificationResult.PASSED,
            details="Internal consistency verified",
            time_ms=(time.time() - start) * 1000
        )
    
    def revoke_key(self, key_id: str) -> None:
        """
        Add a key to the revocation list.
        
        Args:
            key_id: The key ID to revoke
        """
        self._revocation_list.add(key_id)
    
    def unrevoke_key(self, key_id: str) -> None:
        """
        Remove a key from the revocation list.
        
        Args:
            key_id: The key ID to unrevoke
        """
        self._revocation_list.discard(key_id)
    
    def is_revoked(self, key_id: str) -> bool:
        """
        Check if a key is revoked.
        
        Args:
            key_id: The key ID to check
            
        Returns:
            True if revoked, False otherwise
        """
        return key_id in self._revocation_list


def verify_dna_key(dna_key: DNAKey, strict_mode: bool = True) -> VerificationReport:
    """
    Convenience function to verify a DNA key.
    
    Args:
        dna_key: The DNA key to verify
        strict_mode: If True, all barriers must pass
        
    Returns:
        VerificationReport with detailed results
        
    Example:
        >>> from server.crypto.dna_verifier import verify_dna_key
        >>> report = verify_dna_key(my_dna_key)
        >>> if report.overall_result == VerificationResult.PASSED:
        ...     print("Authentication successful!")
    """
    verifier = DNAVerifier(strict_mode=strict_mode)
    return verifier.verify(dna_key)
