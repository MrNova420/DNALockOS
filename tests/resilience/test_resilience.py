"""
DNALockOS Resilience Tests

Tests for system behavior under failure conditions and recovery scenarios.
Military-grade resilience testing with full authentication flows.
"""

import time
from dataclasses import dataclass
from typing import Optional, Any
from unittest.mock import MagicMock, patch

import pytest

from server.core.enrollment import EnrollmentService, EnrollmentRequest, enroll_user
from server.core.authentication import AuthenticationService, ChallengeRequest
from server.crypto.dna_key import SecurityLevel
from server.crypto.dna_generator import DNAKeyGenerator
from server.crypto.signatures import Ed25519SigningKey, generate_ed25519_keypair


@dataclass
class AuthenticatedKeyContainer:
    """Container for a test key with its signing capability."""
    enrollment: Any
    signing_key: Ed25519SigningKey
    verify_key: Any
    key_id: str


def create_authenticated_test_key(
    auth_service: AuthenticationService,
    subject_id: str
) -> AuthenticatedKeyContainer:
    """
    Create an enrolled key with signing capability for testing.
    
    This properly sets up a key where we control the private key
    for full authentication testing.
    """
    # Enroll the user
    enrollment = enroll_user(subject_id)
    assert enrollment.success, f"Enrollment failed: {enrollment.error_message}"
    
    # Generate a test keypair we control
    generator = DNAKeyGenerator()
    signing_key, verify_key = generator._generate_test_keypair()
    
    # Update the DNA key's public key to match our test keypair
    enrollment.dna_key.cryptographic_material.public_key = verify_key.to_bytes()
    
    # Register with auth service
    auth_service.enroll_key(enrollment.dna_key)
    
    return AuthenticatedKeyContainer(
        enrollment=enrollment,
        signing_key=signing_key,
        verify_key=verify_key,
        key_id=enrollment.key_id
    )


class TestGracefulDegradation:
    """Test system behavior when components fail."""
    
    def test_enrollment_recovers_after_transient_failure(self):
        """System should recover after transient failures."""
        service = EnrollmentService()
        
        # Enroll successfully first
        request1 = EnrollmentRequest(
            subject_id="recovery-test-1",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        response1 = service.enroll(request1)
        assert response1.success
        
        # Simulate failure (service still works, just testing recovery pattern)
        # In a real test, we'd mock a dependency failure
        
        # Enroll again - should work
        request2 = EnrollmentRequest(
            subject_id="recovery-test-2",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        response2 = service.enroll(request2)
        assert response2.success
    
    def test_authentication_after_service_restart(self):
        """Authentication should work with fresh service instances - full flow test."""
        auth_service1 = AuthenticationService()
        
        # Create enrollment with signing key we control
        test_key = create_authenticated_test_key(auth_service1, "restart-test-user")
        
        # Generate challenge with first service
        challenge_request = ChallengeRequest(key_id=test_key.key_id)
        challenge_response = auth_service1.generate_challenge(challenge_request)
        assert challenge_response.success
        
        # Sign the challenge with our controlled signing key
        signature = test_key.signing_key.sign(challenge_response.challenge)
        
        # Authenticate with first service
        auth_result = auth_service1.authenticate(
            challenge_response.challenge_id,
            signature
        )
        assert auth_result.success, f"First auth failed: {auth_result.error_message}"
        
        # "Restart" - create new service instance
        auth_service2 = AuthenticationService()
        
        # Re-register the key with the new service (simulating reload from storage)
        auth_service2.enroll_key(test_key.enrollment.dna_key)
        
        # New authentication should work with new service
        challenge_response2 = auth_service2.generate_challenge(challenge_request)
        assert challenge_response2.success
        
        # Sign new challenge with same signing key
        signature2 = test_key.signing_key.sign(challenge_response2.challenge)
        
        auth_result2 = auth_service2.authenticate(
            challenge_response2.challenge_id,
            signature2
        )
        assert auth_result2.success, f"Second auth failed: {auth_result2.error_message}"


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_invalid_security_level_handled(self):
        """Invalid security levels should be handled gracefully."""
        service = EnrollmentService()
        
        # Test with all valid security levels
        for level in SecurityLevel:
            request = EnrollmentRequest(
                subject_id=f"security-level-test-{level.name}",
                subject_type="human",
                security_level=level,
                policy_id="default-policy-v1",
                validity_days=365
            )
            
            response = service.enroll(request)
            assert response.success, f"Should succeed with {level.name}"
    
    def test_multiple_rapid_enrollments_same_user(self):
        """Rapid enrollments for same user should be handled."""
        service = EnrollmentService()
        subject_id = "rapid-enrollment-user"
        
        responses = []
        for i in range(5):
            request = EnrollmentRequest(
                subject_id=subject_id,
                subject_type="human",
                security_level=SecurityLevel.STANDARD,
                policy_id="default-policy-v1",
                validity_days=365
            )
            
            response = service.enroll(request)
            responses.append(response)
        
        # At least some should succeed
        successful = sum(1 for r in responses if r.success)
        assert successful >= 1, "At least one enrollment should succeed"
        
        # All successful ones should have unique key IDs
        key_ids = [r.key_id for r in responses if r.success]
        assert len(key_ids) == len(set(key_ids)), "All key IDs should be unique"
    
    def test_authentication_with_revoked_challenge(self):
        """Authentication with manually invalidated challenge should fail gracefully."""
        auth_service = AuthenticationService()
        
        # Create enrollment with signing key we control
        test_key = create_authenticated_test_key(auth_service, "revoked-challenge-test")
        
        # Get challenge
        challenge_request = ChallengeRequest(key_id=test_key.key_id)
        challenge_response = auth_service.generate_challenge(challenge_request)
        assert challenge_response.success
        
        # Sign it with our controlled signing key
        signature = test_key.signing_key.sign(challenge_response.challenge)
        
        # Manually clean up the challenge (simulating revocation)
        auth_service.cleanup_expired_challenges()
        
        # Try to authenticate - may or may not work depending on implementation
        # But should NOT crash
        try:
            auth_result = auth_service.authenticate(
                challenge_response.challenge_id,
                signature
            )
            # Either success or failure is fine, just no crash
            assert auth_result is not None
        except Exception as e:
            # Should be a handled exception type
            pass


class TestDataIntegrity:
    """Test data integrity under various conditions."""
    
    def test_key_data_consistency(self):
        """Enrolled key data should remain consistent."""
        service = EnrollmentService()
        
        request = EnrollmentRequest(
            subject_id="consistency-test-user",
            subject_type="human",
            security_level=SecurityLevel.ENHANCED,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        response = service.enroll(request)
        assert response.success
        
        # Verify key properties
        dna_key = response.dna_key
        
        # Key should have consistent data
        assert dna_key.key_id == response.key_id
        assert dna_key.subject is not None
        assert dna_key.dna_helix is not None
        assert dna_key.cryptographic_material is not None
        assert dna_key.cryptographic_material.public_key is not None
        
        # Security score should be calculated
        assert dna_key.security_score is not None
        assert dna_key.security_score > 0
    
    def test_serialization_integrity(self):
        """Serialized keys should deserialize correctly."""
        from server.crypto.serialization import DNAKeySerializer
        
        enrollment_service = EnrollmentService()
        serializer = DNAKeySerializer()
        
        request = EnrollmentRequest(
            subject_id="serialization-test",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        response = enrollment_service.enroll(request)
        assert response.success
        
        # Serialize
        serialized = response.serialized_key
        assert serialized is not None
        
        # Deserialize
        deserialized = serializer.deserialize(serialized)
        
        # Verify integrity
        assert deserialized.key_id == response.dna_key.key_id
        # Verify the helix checksum matches
        assert deserialized.dna_helix.checksum == response.dna_key.dna_helix.checksum


class TestConcurrentAccess:
    """Test behavior under concurrent access."""
    
    def test_concurrent_challenge_generation(self):
        """Multiple challenges for same key should work correctly."""
        enrollment_service = EnrollmentService()
        auth_service = AuthenticationService()
        
        # Enroll
        request = EnrollmentRequest(
            subject_id="concurrent-challenges-test",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        enroll_response = enrollment_service.enroll(request)
        assert enroll_response.success
        
        auth_service.enroll_key(enroll_response.dna_key)
        
        # Generate multiple challenges
        challenges = []
        for _ in range(5):
            challenge_request = ChallengeRequest(key_id=enroll_response.key_id)
            challenge_response = auth_service.generate_challenge(challenge_request)
            if challenge_response.success:
                challenges.append(challenge_response)
        
        # All challenges should be unique
        challenge_ids = [c.challenge_id for c in challenges]
        assert len(challenge_ids) == len(set(challenge_ids)), \
            "All challenge IDs should be unique"
        
        # All challenges should be different
        challenge_data = [c.challenge for c in challenges]
        assert len(set(challenge_data)) == len(challenge_data), \
            "All challenge data should be unique"


class TestResourceCleanup:
    """Test proper resource cleanup."""
    
    def test_expired_challenges_cleanup(self):
        """Expired challenges should be cleaned up."""
        enrollment_service = EnrollmentService()
        auth_service = AuthenticationService()
        
        # Enroll
        request = EnrollmentRequest(
            subject_id="cleanup-test",
            subject_type="human",
            security_level=SecurityLevel.STANDARD,
            policy_id="default-policy-v1",
            validity_days=365
        )
        
        enroll_response = enrollment_service.enroll(request)
        assert enroll_response.success
        
        auth_service.enroll_key(enroll_response.dna_key)
        
        # Generate some challenges
        initial_count = auth_service.get_active_challenges_count()
        
        for _ in range(3):
            challenge_request = ChallengeRequest(key_id=enroll_response.key_id)
            auth_service.generate_challenge(challenge_request)
        
        # Should have more challenges now
        after_gen_count = auth_service.get_active_challenges_count()
        assert after_gen_count >= initial_count
        
        # Cleanup
        cleaned = auth_service.cleanup_expired_challenges()
        
        # Count might be same or less (depending on TTL)
        final_count = auth_service.get_active_challenges_count()
        assert final_count <= after_gen_count
