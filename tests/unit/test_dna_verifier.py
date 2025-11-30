"""
DNA-Key Authentication System - Verification System Tests

Tests for the custom DNA key verification system.
Tests cover:
- 12 security barrier verification
- Verification report generation
- Entropy validation
- Layer integrity checks
- Revocation checking
"""

import pytest
from datetime import datetime, timezone, timedelta

from server.crypto.dna_key import (
    DNAKey,
    DNAHelix,
    DNASegment,
    SegmentType,
    SecurityLevel,
)
from server.crypto.dna_generator import (
    DNAKeyGenerator,
    generate_dna_key
)
from server.crypto.dna_verifier import (
    DNAVerifier,
    VerificationResult,
    VerificationReport,
    VerificationBarrier,
    verify_dna_key
)


class TestDNAVerifier:
    """Test DNA verification system."""
    
    def test_verifier_creation(self):
        """Test creating a DNAVerifier."""
        verifier = DNAVerifier()
        assert verifier.strict_mode is True
        
        verifier_relaxed = DNAVerifier(strict_mode=False)
        assert verifier_relaxed.strict_mode is False
    
    def test_verify_valid_key(self):
        """Test verifying a valid DNA key."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        assert report.overall_result in [VerificationResult.PASSED, VerificationResult.WARNING]
        assert report.barriers_total == 12
        assert report.barriers_passed >= 10  # Most barriers should pass
    
    def test_verify_returns_report(self):
        """Test that verify returns a VerificationReport."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        assert isinstance(report, VerificationReport)
        assert report.key_id == key.key_id
        assert report.verified_at is not None
        assert len(report.barrier_results) == 12
    
    def test_all_12_barriers_checked(self):
        """Test that all 12 barriers are checked."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_numbers = [b.barrier_number for b in report.barrier_results]
        assert sorted(barrier_numbers) == list(range(1, 13))


class TestVerificationBarriers:
    """Test individual verification barriers."""
    
    def test_barrier_1_format_validation(self):
        """Test barrier 1: format validation."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_1 = next(b for b in report.barrier_results if b.barrier_number == 1)
        assert barrier_1.name == "Format Validation"
        assert barrier_1.result == VerificationResult.PASSED
    
    def test_barrier_2_version_check(self):
        """Test barrier 2: version check."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_2 = next(b for b in report.barrier_results if b.barrier_number == 2)
        assert barrier_2.name == "Version Check"
        assert barrier_2.result == VerificationResult.PASSED
    
    def test_barrier_3_timestamp_validation(self):
        """Test barrier 3: timestamp validation."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_3 = next(b for b in report.barrier_results if b.barrier_number == 3)
        assert barrier_3.name == "Timestamp Validation"
        assert barrier_3.result == VerificationResult.PASSED
    
    def test_barrier_3_expired_key_fails(self):
        """Test barrier 3 fails for expired keys."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        # Set expiration to past
        key.expires_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_3 = next(b for b in report.barrier_results if b.barrier_number == 3)
        assert barrier_3.result == VerificationResult.FAILED
        assert "expired" in barrier_3.details.lower()
    
    def test_barrier_5_checksum_verification(self):
        """Test barrier 5: checksum verification."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_5 = next(b for b in report.barrier_results if b.barrier_number == 5)
        assert barrier_5.name == "Checksum Verification"
        assert barrier_5.result == VerificationResult.PASSED
    
    def test_barrier_6_entropy_validation(self):
        """Test barrier 6: entropy validation."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_6 = next(b for b in report.barrier_results if b.barrier_number == 6)
        assert barrier_6.name == "Entropy Validation"
        assert barrier_6.result == VerificationResult.PASSED


class TestRevocation:
    """Test key revocation functionality."""
    
    def test_revoke_key(self):
        """Test revoking a key."""
        verifier = DNAVerifier()
        
        verifier.revoke_key("dna-test-key-123")
        assert verifier.is_revoked("dna-test-key-123")
    
    def test_unrevoke_key(self):
        """Test unrevoking a key."""
        verifier = DNAVerifier()
        
        verifier.revoke_key("dna-test-key-123")
        verifier.unrevoke_key("dna-test-key-123")
        assert not verifier.is_revoked("dna-test-key-123")
    
    def test_barrier_9_revocation_check(self):
        """Test barrier 9: revocation check."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        
        # First verify without revocation
        report = verifier.verify(key)
        barrier_9 = next(b for b in report.barrier_results if b.barrier_number == 9)
        assert barrier_9.result == VerificationResult.PASSED
        
        # Revoke the key
        verifier.revoke_key(key.key_id)
        
        # Verify again - should fail
        report = verifier.verify(key)
        barrier_9 = next(b for b in report.barrier_results if b.barrier_number == 9)
        assert barrier_9.result == VerificationResult.FAILED


class TestVerificationReport:
    """Test VerificationReport functionality."""
    
    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        report_dict = report.to_dict()
        
        assert "key_id" in report_dict
        assert "verified_at" in report_dict
        assert "overall_result" in report_dict
        assert "barriers_passed" in report_dict
        assert "barriers_failed" in report_dict
        assert "barriers_total" in report_dict
        assert "barrier_results" in report_dict
        assert len(report_dict["barrier_results"]) == 12


class TestConvenienceFunction:
    """Test verify_dna_key convenience function."""
    
    def test_verify_dna_key_function(self):
        """Test verify_dna_key convenience function."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        report = verify_dna_key(key)
        
        assert isinstance(report, VerificationReport)
        assert report.barriers_total == 12
    
    def test_verify_dna_key_with_strict_mode(self):
        """Test verify_dna_key with strict mode."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        report_strict = verify_dna_key(key, strict_mode=True)
        report_relaxed = verify_dna_key(key, strict_mode=False)
        
        assert isinstance(report_strict, VerificationReport)
        assert isinstance(report_relaxed, VerificationReport)


class TestVerificationResult:
    """Test VerificationResult enum."""
    
    def test_verification_result_values(self):
        """Test VerificationResult enum values."""
        assert VerificationResult.PASSED.value == "passed"
        assert VerificationResult.FAILED.value == "failed"
        assert VerificationResult.WARNING.value == "warning"
        assert VerificationResult.SKIPPED.value == "skipped"


class TestEntropyEstimation:
    """Test entropy estimation in verification."""
    
    def test_high_entropy_passes(self):
        """Test that high-entropy data passes validation."""
        generator = DNAKeyGenerator(SecurityLevel.STANDARD)
        key = generator.generate("user@example.com")
        
        verifier = DNAVerifier()
        report = verifier.verify(key)
        
        barrier_6 = next(b for b in report.barrier_results if b.barrier_number == 6)
        assert barrier_6.result == VerificationResult.PASSED
        assert "bits/byte" in barrier_6.details
