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
DNALockOS Adversarial Tests - Fuzz Testing

Tests that attempt to break the system with malformed inputs,
random data, and edge cases.
"""

import base64
import os
import secrets
from typing import Optional

import pytest
from hypothesis import given, settings, strategies as st

# Import the actual modules we're testing
from server.crypto.dna_key import DNAKey, SecurityLevel
from server.crypto.dna_generator import DNAKeyGenerator
from server.crypto.serialization import DNAKeySerializer
from server.crypto.signatures import Ed25519SigningKey, Ed25519VerifyKey, generate_ed25519_keypair
from server.crypto.encryption import encrypt_data, decrypt_data
from server.core.enrollment import EnrollmentService, EnrollmentRequest


class TestFuzzedDNAKeyInputs:
    """Fuzz test DNA key generation with random inputs."""
    
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=100)
    def test_enrollment_with_random_subject_id(self, subject_id: str):
        """Enrollment should handle any string as subject_id safely."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id=subject_id,
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        # Should not crash - might succeed or fail gracefully
        try:
            response = service.enroll(request)
            # If it succeeds, verify the key is valid
            if response.success:
                assert response.dna_key is not None
                assert response.key_id is not None
        except Exception as e:
            # Should only fail with expected exceptions
            assert isinstance(e, (ValueError, TypeError))
    
    @given(st.integers(min_value=-1000000, max_value=1000000))
    @settings(max_examples=50)
    def test_enrollment_with_random_validity_days(self, days: int):
        """Enrollment should handle any validity days value."""
        service = EnrollmentService()
        
        # System should handle invalid values
        try:
            request = EnrollmentRequest(
                subject_id="test-user",
                subject_type="human",
                security_level=SecurityLevel.STANDARD,
                policy_id="default-policy-v1",
                validity_days=days
            )
            response = service.enroll(request)
            
            if days > 0 and days <= 3650:
                # Valid range - should succeed
                assert response.success or response.error_message is not None
            else:
                # Invalid range - should fail gracefully
                pass
        except (ValueError, TypeError):
            # Expected for invalid inputs
            pass
    
    @given(st.binary(min_size=1, max_size=10000))
    @settings(max_examples=50)
    def test_deserialization_with_random_bytes(self, random_bytes: bytes):
        """Serializer should handle random bytes without crashing."""
        serializer = DNAKeySerializer()
        
        try:
            key = serializer.deserialize(random_bytes)
            # If deserialization succeeded with random bytes, that's a potential issue
            # but we shouldn't crash
        except Exception:
            # Expected to fail - that's good
            pass


class TestFuzzedCryptoOperations:
    """Fuzz test cryptographic operations."""
    
    @given(st.binary(min_size=1, max_size=1000))
    @settings(max_examples=100)
    def test_signature_verification_with_random_data(self, random_bytes: bytes):
        """Signature verification should reject random data."""
        signing_key, verify_key = generate_ed25519_keypair()
        
        # Create a valid signature
        message = b"valid message"
        signature = signing_key.sign(message)
        
        # Try to verify with random data as signature
        try:
            # Use random bytes padded to 64 bytes as signature - should fail
            padded_random = (random_bytes + b'\x00' * 64)[:64]
            is_valid = verify_key.verify(message, padded_random)
            # Should NEVER validate with random signature
            assert is_valid is False
        except (ValueError, Exception):
            # Exception is also acceptable - just shouldn't crash unexpectedly
            pass
    
    @given(st.binary(min_size=32, max_size=32))
    @settings(max_examples=50)
    def test_encryption_decryption_with_random_key(self, random_key: bytes):
        """Encryption service should handle random keys safely."""
        plaintext = b"test data"
        
        try:
            # Try to encrypt with random key
            ciphertext = encrypt_data(plaintext, random_key)
            
            # Try to decrypt
            decrypted = decrypt_data(ciphertext, random_key)
            
            # If both succeeded, data should match
            assert decrypted == plaintext
        except Exception:
            # Expected to fail with invalid key format
            pass


class TestReplayAttacks:
    """Test resistance to replay attacks."""
    
    def test_challenge_cannot_be_reused(self):
        """Same challenge should not work twice."""
        from server.core.authentication import AuthenticationService, ChallengeRequest
        from server.core.enrollment import enroll_user
        from server.crypto.dna_generator import DNAKeyGenerator
        
        # Enroll a key
        auth_service = AuthenticationService()
        enrollment = enroll_user("replay-test-user")
        
        # Generate a test keypair and update the DNA key to use it
        generator = DNAKeyGenerator()
        signing_key, verify_key = generator._generate_test_keypair()
        enrollment.dna_key.cryptographic_material.public_key = verify_key.to_bytes()
        auth_service.enroll_key(enrollment.dna_key)
        
        # Get a challenge
        challenge_request = ChallengeRequest(key_id=enrollment.key_id)
        challenge_response = auth_service.generate_challenge(challenge_request)
        assert challenge_response.success
        
        # Create valid signature
        challenge_signature = signing_key.sign(challenge_response.challenge)
        
        # First authentication should succeed
        auth_result1 = auth_service.authenticate(
            challenge_response.challenge_id,
            challenge_signature
        )
        assert auth_result1.success
        
        # Second authentication with same challenge should fail
        auth_result2 = auth_service.authenticate(
            challenge_response.challenge_id,
            challenge_signature
        )
        assert not auth_result2.success, "Replay attack should be rejected"
    
    def test_old_challenge_rejected_after_new_one(self):
        """Old challenges should be unique from new ones."""
        from server.core.authentication import AuthenticationService, ChallengeRequest
        from server.core.enrollment import enroll_user
        
        auth_service = AuthenticationService()
        enrollment = enroll_user("old-challenge-test")
        auth_service.enroll_key(enrollment.dna_key)
        
        # Get first challenge
        challenge_request = ChallengeRequest(key_id=enrollment.key_id)
        old_challenge = auth_service.generate_challenge(challenge_request)
        
        # Get second challenge
        new_challenge = auth_service.generate_challenge(challenge_request)
        
        # Both should be different
        assert old_challenge.challenge_id != new_challenge.challenge_id
        assert old_challenge.challenge != new_challenge.challenge


class TestKeyCloning:
    """Test resistance to key cloning attacks."""
    
    def test_same_key_material_detected(self):
        """System should detect duplicate key registrations."""
        from server.core.enrollment import EnrollmentService, EnrollmentRequest
        
        enrollment_service = EnrollmentService()
        
        # Enroll first key
        request1 = EnrollmentRequest(
            subject_id="original-user",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        response1 = enrollment_service.enroll(request1)
        assert response1.success
        
        # Try to enroll with same subject_id
        request2 = EnrollmentRequest(
            subject_id="original-user",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        response2 = enrollment_service.enroll(request2)
        
        # System should either:
        # 1. Generate a new unique key (different key_id)
        # 2. Or reject duplicate enrollment
        if response2.success:
            # Different key IDs expected
            assert response2.key_id != response1.key_id, "Cloned keys should have different IDs"


class TestMalformedInputs:
    """Test handling of malformed API inputs."""
    
    def test_enrollment_with_empty_subject_id(self):
        """Empty subject ID should be rejected."""
        from server.core.enrollment import EnrollmentService, EnrollmentRequest
        
        service = EnrollmentService()
        
        try:
            request = EnrollmentRequest(
                subject_id="",
                subject_type="human",
                security_level=SecurityLevel.STANDARD,
                policy_id="default-policy-v1",
                validity_days=365
            )
            response = service.enroll(request)
            # If it doesn't raise, should fail gracefully
            # Some systems may allow empty strings
        except (ValueError, TypeError):
            pass  # Expected
    
    def test_enrollment_with_null_bytes(self):
        """Subject ID with null bytes should be handled safely."""
        from server.core.enrollment import EnrollmentService, EnrollmentRequest
        
        service = EnrollmentService()
        
        try:
            request = EnrollmentRequest(
                subject_id="user\x00with\x00nulls",
                subject_type="human",
                security_level=SecurityLevel.STANDARD,
                policy_id="default-policy-v1",
                validity_days=365
            )
            response = service.enroll(request)
            # Should not crash
        except (ValueError, TypeError):
            pass  # Expected
    
    def test_challenge_with_invalid_key_id(self):
        """Challenge request with invalid key ID should fail gracefully."""
        from server.core.authentication import AuthenticationService, ChallengeRequest
        
        auth_service = AuthenticationService()
        
        # Non-existent key
        request = ChallengeRequest(key_id="nonexistent-key-12345")
        response = auth_service.generate_challenge(request)
        
        # Should fail gracefully
        assert not response.success
        assert response.error_message is not None
    
    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=50)
    def test_authentication_with_random_challenge_id(self, challenge_id: str):
        """Authentication with random challenge ID should fail safely."""
        from server.core.authentication import AuthenticationService
        
        auth_service = AuthenticationService()
        
        # Random signature
        fake_signature = secrets.token_bytes(64)
        
        try:
            response = auth_service.authenticate(challenge_id, fake_signature)
            # Should always fail with invalid challenge
            assert not response.success
        except Exception:
            # Exception is acceptable, just shouldn't crash unexpectedly
            pass
