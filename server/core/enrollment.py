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
DNA-Key Authentication System - Enrollment Service

Implements the enrollment service for registering new DNA keys.
Handles key generation, validation, and storage preparation.

Enrollment Flow:
1. Receive enrollment request
2. Validate user data
3. Generate DNA key
4. Sign key with issuer
5. Return enrollment response
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from server.crypto.dna_generator import DNAKeyGenerator, SecurityLevel
from server.crypto.dna_key import DNAKey
from server.crypto.serialization import serialize_dna_key


@dataclass
class EnrollmentRequest:
    """Request to enroll a new DNA key."""

    subject_id: str
    subject_type: str = "human"  # human, device, service
    security_level: SecurityLevel = SecurityLevel.STANDARD
    policy_id: str = "default-policy-v1"
    validity_days: int = 365
    mfa_required: bool = False
    biometric_required: bool = False
    device_binding_required: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EnrollmentResponse:
    """Response from enrollment."""

    success: bool
    dna_key: Optional[DNAKey] = None
    key_id: Optional[str] = None
    serialized_key: Optional[bytes] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None


class EnrollmentError(Exception):
    """Exception raised during enrollment."""

    pass


class EnrollmentService:
    """
    Service for enrolling new DNA keys.

    Handles the complete enrollment workflow including
    validation, generation, and key preparation.
    """

    def __init__(self, issuer_org: str = "DNAKeyAuthSystem"):
        """
        Initialize enrollment service.

        Args:
            issuer_org: Organization ID for issuing keys
        """
        self.issuer_org = issuer_org

    def enroll(self, request: EnrollmentRequest) -> EnrollmentResponse:
        """
        Enroll a new DNA key.

        Args:
            request: Enrollment request with user details

        Returns:
            EnrollmentResponse with generated key or error

        Example:
            >>> service = EnrollmentService()
            >>> request = EnrollmentRequest(
            ...     subject_id="user@example.com",
            ...     security_level=SecurityLevel.ENHANCED,
            ...     mfa_required=True
            ... )
            >>> response = service.enroll(request)
            >>> if response.success:
            ...     print(f"Enrolled key: {response.key_id}")
        """
        try:
            # Validate request
            self._validate_request(request)

            # Generate DNA key
            generator = DNAKeyGenerator(request.security_level)
            dna_key = generator.generate(
                subject_id=request.subject_id,
                subject_type=request.subject_type,
                policy_id=request.policy_id,
                validity_days=request.validity_days,
                issuer_org=self.issuer_org,
                mfa_required=request.mfa_required,
                biometric_required=request.biometric_required,
                device_binding_required=request.device_binding_required,
            )

            # Validate generated key
            if not dna_key.is_valid():
                raise EnrollmentError("Generated key failed validation")

            # Serialize key
            serialized = serialize_dna_key(dna_key)

            # Create successful response
            return EnrollmentResponse(
                success=True,
                dna_key=dna_key,
                key_id=dna_key.key_id,
                serialized_key=serialized,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            # Create error response
            return EnrollmentResponse(success=False, error_message=str(e), timestamp=datetime.now(timezone.utc))

    def _validate_request(self, request: EnrollmentRequest) -> None:
        """
        Validate enrollment request.

        Args:
            request: Request to validate

        Raises:
            EnrollmentError: If validation fails
        """
        # Validate subject ID
        if not request.subject_id or len(request.subject_id) == 0:
            raise EnrollmentError("Subject ID cannot be empty")

        if len(request.subject_id) > 512:
            raise EnrollmentError("Subject ID too long (max 512 characters)")

        # Validate subject type
        valid_types = ["human", "device", "service"]
        if request.subject_type not in valid_types:
            raise EnrollmentError(f"Invalid subject type: {request.subject_type}")

        # Validate validity period
        if request.validity_days < 1:
            raise EnrollmentError("Validity days must be at least 1")

        if request.validity_days > 3650:  # Max 10 years
            raise EnrollmentError("Validity days cannot exceed 3650 (10 years)")

        # Validate policy ID
        if not request.policy_id or len(request.policy_id) == 0:
            raise EnrollmentError("Policy ID cannot be empty")

    def verify_enrollment(self, dna_key: DNAKey) -> bool:
        """
        Verify an enrolled DNA key.

        Args:
            dna_key: DNA key to verify

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check basic validity
            if not dna_key.is_valid():
                return False

            # Verify checksum
            if not dna_key.dna_helix.verify_checksum():
                return False

            # Check expiration
            if dna_key.is_expired():
                return False

            # Verify issuer organization
            if dna_key.issuer and dna_key.issuer.organization_id != self.issuer_org:
                return False

            return True

        except Exception:
            return False

    def get_enrollment_stats(self, dna_key: DNAKey) -> Dict[str, Any]:
        """
        Get statistics about an enrolled key.

        Args:
            dna_key: DNA key to analyze

        Returns:
            Dictionary with key statistics
        """
        from server.crypto.serialization import DNAKeySerializer

        return {
            "key_id": dna_key.key_id,
            "security_level": self._get_security_level(dna_key),
            "segment_count": dna_key.dna_helix.segment_count,
            "strand_length": dna_key.dna_helix.strand_length,
            "serialized_size_kb": DNAKeySerializer.get_serialized_size(dna_key) / 1024,
            "created": dna_key.created_timestamp.isoformat() if dna_key.created_timestamp else None,
            "expires": dna_key.expires_timestamp.isoformat() if dna_key.expires_timestamp else None,
            "subject_type": dna_key.subject.subject_type if dna_key.subject else None,
            "policy_id": dna_key.policy_binding.policy_id if dna_key.policy_binding else None,
            "mfa_required": dna_key.policy_binding.mfa_required if dna_key.policy_binding else False,
            "is_valid": dna_key.is_valid(),
            "is_expired": dna_key.is_expired(),
        }

    def _get_security_level(self, dna_key: DNAKey) -> str:
        """Determine security level from segment count."""
        count = dna_key.dna_helix.segment_count

        if count <= 1024:
            return "STANDARD"
        elif count <= 16384:
            return "ENHANCED"
        elif count <= 65536:
            return "MAXIMUM"
        else:
            return "GOVERNMENT"


def enroll_user(
    subject_id: str, security_level: SecurityLevel = SecurityLevel.STANDARD, **kwargs
) -> EnrollmentResponse:
    """
    Convenience function to enroll a user.

    Args:
        subject_id: User identifier
        security_level: Security level for the key
        **kwargs: Additional enrollment parameters

    Returns:
        EnrollmentResponse

    Example:
        >>> response = enroll_user("user@example.com", SecurityLevel.ENHANCED)
        >>> if response.success:
        ...     print(f"Enrolled: {response.key_id}")
    """
    service = EnrollmentService()
    request = EnrollmentRequest(subject_id=subject_id, security_level=security_level, **kwargs)
    return service.enroll(request)
