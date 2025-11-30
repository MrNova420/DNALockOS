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
DNALockOS SDK - Exception Classes
"""


class DNALockError(Exception):
    """Base exception for DNALockOS SDK."""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> dict:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(DNALockError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, code="AUTH_FAILED", **kwargs)


class EnrollmentError(DNALockError):
    """Raised when enrollment fails."""
    
    def __init__(self, message: str = "Enrollment failed", **kwargs):
        super().__init__(message, code="ENROLLMENT_FAILED", **kwargs)


class NetworkError(DNALockError):
    """Raised when network communication fails."""
    
    def __init__(self, message: str = "Network error", **kwargs):
        super().__init__(message, code="NETWORK_ERROR", **kwargs)


class ValidationError(DNALockError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation error", **kwargs):
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)


class RateLimitError(DNALockError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, code="RATE_LIMITED", **kwargs)
        self.retry_after = retry_after


class KeyNotFoundError(DNALockError):
    """Raised when a DNA key is not found."""
    
    def __init__(self, key_id: str, **kwargs):
        super().__init__(f"DNA key not found: {key_id}", code="KEY_NOT_FOUND", **kwargs)
        self.key_id = key_id


class KeyRevokedError(DNALockError):
    """Raised when trying to use a revoked key."""
    
    def __init__(self, key_id: str, **kwargs):
        super().__init__(f"DNA key is revoked: {key_id}", code="KEY_REVOKED", **kwargs)
        self.key_id = key_id


class ChallengeExpiredError(DNALockError):
    """Raised when a challenge has expired."""
    
    def __init__(self, challenge_id: str, **kwargs):
        super().__init__(f"Challenge expired: {challenge_id}", code="CHALLENGE_EXPIRED", **kwargs)
        self.challenge_id = challenge_id
