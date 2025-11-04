"""
DNA-Key Authentication System - Enrollment Service Tests

Comprehensive test suite for enrollment service.
Tests cover:
- Enrollment request validation
- DNA key generation during enrollment
- Enrollment response handling
- Error cases
"""

import pytest
from datetime import datetime, timedelta, timezone
from server.core.enrollment import (
    EnrollmentService,
    EnrollmentRequest,
    EnrollmentResponse,
    EnrollmentError,
    enroll_user
)
from server.crypto.dna_key import SecurityLevel


class TestEnrollmentRequest:
    """Test enrollment request validation."""
    
    def test_create_basic_request(self):
        """Test creating a basic enrollment request."""
        request = EnrollmentRequest(subject_id="user@example.com")
        
        assert request.subject_id == "user@example.com"
        assert request.subject_type == "human"
        assert request.security_level == SecurityLevel.STANDARD
    
    def test_create_custom_request(self):
        """Test creating a custom enrollment request."""
        request = EnrollmentRequest(
            subject_id="device-12345",
            subject_type="device",
            security_level=SecurityLevel.ENHANCED,
            mfa_required=True,
            validity_days=90
        )
        
        assert request.subject_id == "device-12345"
        assert request.subject_type == "device"
        assert request.security_level == SecurityLevel.ENHANCED
        assert request.mfa_required is True
        assert request.validity_days == 90


class TestEnrollmentService:
    """Test enrollment service functionality."""
    
    def test_create_service(self):
        """Test creating enrollment service."""
        service = EnrollmentService()
        
        assert isinstance(service, EnrollmentService)
        assert service.issuer_org == "DNAKeyAuthSystem"
    
    def test_enroll_basic_user(self):
        """Test enrolling a basic user."""
        service = EnrollmentService()
        request = EnrollmentRequest(subject_id="user@example.com")
        
        response = service.enroll(request)
        
        assert response.success is True
        assert response.dna_key is not None
        assert response.key_id is not None
        assert response.serialized_key is not None
        assert response.error_message is None
    
    def test_enroll_device(self):
        """Test enrolling a device."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="device-12345",
            subject_type="device"
        )
        
        response = service.enroll(request)
        
        assert response.success is True
        assert response.dna_key.subject.subject_type == "device"
    
    def test_enroll_with_mfa(self):
        """Test enrolling with MFA requirement."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            mfa_required=True
        )
        
        response = service.enroll(request)
        
        assert response.success is True
        assert response.dna_key.policy_binding.mfa_required is True
    
    def test_enroll_enhanced_security(self):
        """Test enrolling with enhanced security."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            security_level=SecurityLevel.ENHANCED
        )
        
        response = service.enroll(request)
        
        assert response.success is True
        assert response.dna_key.dna_helix.segment_count == 16384
    
    def test_enrolled_key_is_valid(self):
        """Test that enrolled key is valid."""
        service = EnrollmentService()
        request = EnrollmentRequest(subject_id="user@example.com")
        
        response = service.enroll(request)
        
        assert response.dna_key.is_valid() is True
        assert response.dna_key.dna_helix.verify_checksum() is True
    
    def test_serialized_key_provided(self):
        """Test that serialized key is provided."""
        service = EnrollmentService()
        request = EnrollmentRequest(subject_id="user@example.com")
        
        response = service.enroll(request)
        
        assert isinstance(response.serialized_key, bytes)
        assert len(response.serialized_key) > 0


class TestEnrollmentValidation:
    """Test enrollment request validation."""
    
    def test_empty_subject_id_fails(self):
        """Test that empty subject ID fails."""
        service = EnrollmentService()
        request = EnrollmentRequest(subject_id="")
        
        response = service.enroll(request)
        
        assert response.success is False
        assert "Subject ID cannot be empty" in response.error_message
    
    def test_subject_id_too_long_fails(self):
        """Test that subject ID that's too long fails."""
        service = EnrollmentService()
        request = EnrollmentRequest(subject_id="x" * 513)
        
        response = service.enroll(request)
        
        assert response.success is False
        assert "too long" in response.error_message
    
    def test_invalid_subject_type_fails(self):
        """Test that invalid subject type fails."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            subject_type="invalid"
        )
        
        response = service.enroll(request)
        
        assert response.success is False
        assert "Invalid subject type" in response.error_message
    
    def test_invalid_validity_period_fails(self):
        """Test that invalid validity period fails."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            validity_days=0
        )
        
        response = service.enroll(request)
        
        assert response.success is False
        assert "at least 1" in response.error_message
    
    def test_excessive_validity_period_fails(self):
        """Test that excessive validity period fails."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            validity_days=5000
        )
        
        response = service.enroll(request)
        
        assert response.success is False
        assert "cannot exceed" in response.error_message
    
    def test_empty_policy_id_fails(self):
        """Test that empty policy ID fails."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            policy_id=""
        )
        
        response = service.enroll(request)
        
        assert response.success is False
        assert "Policy ID cannot be empty" in response.error_message


class TestEnrollmentVerification:
    """Test enrollment verification."""
    
    def test_verify_valid_enrollment(self):
        """Test verifying a valid enrollment."""
        service = EnrollmentService()
        request = EnrollmentRequest(subject_id="user@example.com")
        response = service.enroll(request)
        
        is_valid = service.verify_enrollment(response.dna_key)
        
        assert is_valid is True
    
    def test_verify_expired_key_fails(self):
        """Test that expired key fails verification."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            validity_days=1
        )
        response = service.enroll(request)
        
        # Manually expire the key
        response.dna_key.expires_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
        
        is_valid = service.verify_enrollment(response.dna_key)
        
        assert is_valid is False


class TestEnrollmentStats:
    """Test enrollment statistics."""
    
    def test_get_enrollment_stats(self):
        """Test getting enrollment statistics."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            security_level=SecurityLevel.ENHANCED
        )
        response = service.enroll(request)
        
        stats = service.get_enrollment_stats(response.dna_key)
        
        assert "key_id" in stats
        assert stats["security_level"] == "ENHANCED"
        assert stats["segment_count"] == 16384
        assert stats["is_valid"] is True
        assert stats["is_expired"] is False
    
    def test_stats_include_policy_info(self):
        """Test that stats include policy information."""
        service = EnrollmentService()
        request = EnrollmentRequest(
            subject_id="user@example.com",
            mfa_required=True
        )
        response = service.enroll(request)
        
        stats = service.get_enrollment_stats(response.dna_key)
        
        assert stats["mfa_required"] is True
        assert "policy_id" in stats


class TestConvenienceFunction:
    """Test convenience function for enrollment."""
    
    def test_enroll_user_function(self):
        """Test enroll_user convenience function."""
        response = enroll_user("user@example.com")
        
        assert response.success is True
        assert response.dna_key is not None
    
    def test_enroll_user_with_options(self):
        """Test enroll_user with custom options."""
        response = enroll_user(
            "user@example.com",
            SecurityLevel.ENHANCED,
            mfa_required=True,
            validity_days=90
        )
        
        assert response.success is True
        assert response.dna_key.policy_binding.mfa_required is True
        assert response.dna_key.dna_helix.segment_count == 16384


class TestMultipleEnrollments:
    """Test enrolling multiple users."""
    
    def test_enroll_multiple_users(self):
        """Test enrolling multiple different users."""
        service = EnrollmentService()
        
        response1 = service.enroll(EnrollmentRequest(subject_id="user1@example.com"))
        response2 = service.enroll(EnrollmentRequest(subject_id="user2@example.com"))
        
        assert response1.success is True
        assert response2.success is True
        assert response1.key_id != response2.key_id
    
    def test_enroll_same_user_generates_different_keys(self):
        """Test that enrolling same user twice generates different keys."""
        service = EnrollmentService()
        
        response1 = service.enroll(EnrollmentRequest(subject_id="user@example.com"))
        response2 = service.enroll(EnrollmentRequest(subject_id="user@example.com"))
        
        # Different enrollments should generate different keys
        assert response1.key_id != response2.key_id
        assert response1.dna_key.dna_helix.checksum != response2.dna_key.dna_helix.checksum
