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
DNALockOS SDK - Main Client

The primary interface for integrating DNALockOS authentication
into your application.
"""

import base64
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from urllib.parse import urljoin

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import Base64Encoder
    HAS_NACL = True
except ImportError:
    HAS_NACL = False

from .models import (
    AuthenticationResult,
    ChallengeResult,
    EnrollmentResult,
    HealthStatus,
    KeyInfo,
    RevocationResult,
    SecurityLevel
)
from .exceptions import (
    AuthenticationError,
    DNALockError,
    EnrollmentError,
    NetworkError,
    ValidationError
)


@dataclass
class DNALockConfig:
    """Configuration for DNALockOS client."""
    
    # Server configuration
    api_url: str = "http://localhost:8000"
    api_version: str = "v1"
    
    # Authentication
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    
    # Timeouts (in seconds)
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Security
    verify_ssl: bool = True
    
    # Callbacks
    on_error: Optional[Callable[[Exception], None]] = None
    
    @property
    def base_url(self) -> str:
        """Get the base API URL."""
        return urljoin(self.api_url, f"/api/{self.api_version}/")
    
    @classmethod
    def from_env(cls) -> "DNALockConfig":
        """Create config from environment variables."""
        return cls(
            api_url=os.getenv("DNALOCK_API_URL", "http://localhost:8000"),
            api_key=os.getenv("DNALOCK_API_KEY"),
            client_id=os.getenv("DNALOCK_CLIENT_ID"),
            verify_ssl=os.getenv("DNALOCK_VERIFY_SSL", "true").lower() == "true"
        )


class DNALockClient:
    """
    DNALockOS Authentication Client
    
    A comprehensive client for integrating DNA-Key authentication
    into your application.
    
    Example usage:
    
        # Initialize client
        client = DNALockClient(DNALockConfig(api_url="https://api.dnalock.example.com"))
        
        # Enroll a new user
        enrollment = client.enroll(
            subject_id="user@example.com",
            security_level=SecurityLevel.ENHANCED
        )
        
        # Store the serialized key securely
        user_key = enrollment.serialized_key
        
        # Later, authenticate
        result = client.authenticate(user_key)
        
        if result.success:
            print(f"Session token: {result.session_token}")
    """
    
    def __init__(self, config: Optional[DNALockConfig] = None):
        """Initialize the DNALock client."""
        self.config = config or DNALockConfig()
        self._session = None
        
        if not HAS_REQUESTS:
            raise ImportError(
                "The 'requests' library is required. "
                "Install it with: pip install requests"
            )
    
    @property
    def session(self):
        """Get or create the requests session."""
        if self._session is None:
            self._session = requests.Session()
            
            # Set default headers
            self._session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "DNALockOS-SDK/1.0.0"
            })
            
            # Add API key if configured
            if self.config.api_key:
                self._session.headers["X-API-Key"] = self.config.api_key
            
            if self.config.client_id:
                self._session.headers["X-Client-ID"] = self.config.client_id
        
        return self._session
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = urljoin(self.config.base_url, endpoint)
        headers = {}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=(self.config.connect_timeout, self.config.read_timeout),
                verify=self.config.verify_ssl
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {e}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.HTTPError as e:
            # Try to parse error response
            try:
                error_data = e.response.json()
                raise DNALockError(
                    message=error_data.get("error_message", str(e)),
                    code=error_data.get("error_code", "HTTP_ERROR"),
                    details=error_data
                )
            except (ValueError, KeyError):
                raise DNALockError(f"HTTP error: {e}")
        except Exception as e:
            if self.config.on_error:
                self.config.on_error(e)
            raise
    
    # ==================== Health & Status ====================
    
    def health_check(self) -> HealthStatus:
        """Check the health status of the DNALockOS server."""
        # Health endpoint is at root, not under /api/v1/
        url = urljoin(self.config.api_url, "/health")
        
        try:
            response = self.session.get(
                url,
                timeout=(self.config.connect_timeout, self.config.read_timeout),
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return HealthStatus.from_dict(response.json())
        except Exception as e:
            raise NetworkError(f"Health check failed: {e}")
    
    # ==================== Enrollment ====================
    
    def enroll(
        self,
        subject_id: str,
        security_level: SecurityLevel = SecurityLevel.STANDARD,
        subject_type: str = "human",
        policy_id: str = "default-policy-v1",
        validity_days: int = 365,
        mfa_required: bool = False,
        biometric_required: bool = False,
        device_binding_required: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EnrollmentResult:
        """
        Enroll a new DNA key for a subject.
        
        Args:
            subject_id: Unique identifier for the subject (e.g., email, user ID)
            security_level: Security level for the key
            subject_type: Type of subject ("human", "device", "service")
            policy_id: Policy ID to apply
            validity_days: Number of days the key is valid
            mfa_required: Whether MFA is required for this key
            biometric_required: Whether biometric verification is required
            device_binding_required: Whether device binding is required
            metadata: Optional metadata to associate with the key
        
        Returns:
            EnrollmentResult containing the new key information
        
        Example:
            result = client.enroll(
                subject_id="user@example.com",
                security_level=SecurityLevel.ENHANCED,
                validity_days=180
            )
            
            if result.success:
                # Store result.serialized_key securely for later authentication
                save_key(user_id, result.serialized_key)
        """
        if not subject_id:
            raise ValidationError("subject_id is required")
        
        data = {
            "subject_id": subject_id,
            "subject_type": subject_type,
            "security_level": security_level.value if isinstance(security_level, SecurityLevel) else security_level,
            "policy_id": policy_id,
            "validity_days": validity_days,
            "mfa_required": mfa_required,
            "biometric_required": biometric_required,
            "device_binding_required": device_binding_required
        }
        
        if metadata:
            data["metadata"] = metadata
        
        try:
            response = self._request("POST", "enroll", data=data)
            return EnrollmentResult.from_dict(response)
        except DNALockError as e:
            raise EnrollmentError(e.message, details=e.details)
    
    # ==================== Authentication ====================
    
    def get_challenge(self, key_id: str) -> ChallengeResult:
        """
        Request an authentication challenge for a key.
        
        Args:
            key_id: The ID of the DNA key
        
        Returns:
            ChallengeResult containing the challenge to sign
        """
        if not key_id:
            raise ValidationError("key_id is required")
        
        data = {"key_id": key_id}
        response = self._request("POST", "challenge", data=data)
        return ChallengeResult.from_dict(response)
    
    def submit_response(
        self,
        challenge_id: str,
        challenge_response: str
    ) -> AuthenticationResult:
        """
        Submit a signed challenge response.
        
        Args:
            challenge_id: The ID of the challenge
            challenge_response: Hex-encoded signed response
        
        Returns:
            AuthenticationResult with session token if successful
        """
        if not challenge_id or not challenge_response:
            raise ValidationError("challenge_id and challenge_response are required")
        
        data = {
            "challenge_id": challenge_id,
            "challenge_response": challenge_response
        }
        
        try:
            response = self._request("POST", "authenticate", data=data)
            return AuthenticationResult.from_dict(response)
        except DNALockError as e:
            raise AuthenticationError(e.message, details=e.details)
    
    def authenticate(
        self,
        serialized_key: str,
        auto_sign: bool = True
    ) -> AuthenticationResult:
        """
        Complete authentication flow with a stored key.
        
        This method handles the full challenge-response flow:
        1. Deserialize the stored key
        2. Request a challenge
        3. Sign the challenge
        4. Submit the response
        
        Args:
            serialized_key: Base64-encoded serialized DNA key
            auto_sign: Whether to automatically sign the challenge (requires PyNaCl)
        
        Returns:
            AuthenticationResult with session token if successful
        
        Example:
            # Retrieve stored key
            stored_key = get_user_key(user_id)
            
            # Authenticate
            result = client.authenticate(stored_key)
            
            if result.success:
                # Use session token for subsequent requests
                session_token = result.session_token
        """
        if not HAS_NACL and auto_sign:
            raise ImportError(
                "PyNaCl is required for automatic signing. "
                "Install it with: pip install pynacl"
            )
        
        # Decode and parse the key
        try:
            key_data = self._decode_key(serialized_key)
            key_id = key_data.get("key_id")
            private_key = key_data.get("private_key")
        except Exception as e:
            raise ValidationError(f"Invalid serialized key: {e}")
        
        if not key_id:
            raise ValidationError("Key ID not found in serialized key")
        
        # Get challenge
        challenge_result = self.get_challenge(key_id)
        
        if not challenge_result.success:
            raise AuthenticationError(
                challenge_result.error_message or "Failed to get challenge"
            )
        
        # Sign challenge
        if auto_sign:
            if not private_key:
                raise ValidationError("Private key not found in serialized key")
            
            challenge_bytes = bytes.fromhex(challenge_result.challenge)
            signature = self._sign_challenge(challenge_bytes, private_key)
            challenge_response = signature.hex()
        else:
            raise ValidationError(
                "Manual signing not implemented. Use auto_sign=True"
            )
        
        # Submit response
        return self.submit_response(
            challenge_result.challenge_id,
            challenge_response
        )
    
    def _decode_key(self, serialized_key: str) -> Dict[str, Any]:
        """Decode a serialized key."""
        try:
            # Try base64 decode
            key_bytes = base64.b64decode(serialized_key)
            
            # Try CBOR decode first
            try:
                import cbor2
                return cbor2.loads(key_bytes)
            except ImportError:
                pass
            
            # Fallback to JSON
            return json.loads(key_bytes.decode('utf-8'))
        except Exception as e:
            raise ValidationError(f"Failed to decode key: {e}")
    
    def _sign_challenge(self, challenge: bytes, private_key: bytes) -> bytes:
        """Sign a challenge with the private key."""
        if not HAS_NACL:
            raise ImportError("PyNaCl is required for signing")
        
        if isinstance(private_key, str):
            private_key = base64.b64decode(private_key)
        
        signing_key = SigningKey(private_key)
        signed = signing_key.sign(challenge)
        return signed.signature
    
    # ==================== Key Management ====================
    
    def get_key_info(self, key_id: str, auth_token: str) -> KeyInfo:
        """
        Get information about a DNA key.
        
        Args:
            key_id: The ID of the key
            auth_token: Admin authentication token
        
        Returns:
            KeyInfo with key details
        """
        response = self._request(
            "GET",
            f"admin/keys/{key_id}",
            auth_token=auth_token
        )
        return KeyInfo.from_dict(response)
    
    def revoke_key(
        self,
        key_id: str,
        reason: str,
        revoked_by: str,
        auth_token: str,
        notes: Optional[str] = None
    ) -> RevocationResult:
        """
        Revoke a DNA key.
        
        Args:
            key_id: The ID of the key to revoke
            reason: Reason for revocation
            revoked_by: Identity of the revoker
            auth_token: Admin authentication token
            notes: Optional notes about the revocation
        
        Returns:
            RevocationResult with revocation details
        """
        data = {
            "key_id": key_id,
            "reason": reason,
            "revoked_by": revoked_by
        }
        
        if notes:
            data["notes"] = notes
        
        response = self._request(
            "POST",
            "admin/revoke",
            data=data,
            auth_token=auth_token
        )
        return RevocationResult.from_dict(response)
    
    # ==================== Visual DNA ====================
    
    def get_visual_config(self, key_id: str) -> Dict[str, Any]:
        """
        Get the visual DNA configuration for rendering.
        
        Args:
            key_id: The ID of the key
        
        Returns:
            Dictionary with visual configuration for 3D rendering
        """
        return self._request("GET", f"visual/{key_id}")
    
    # ==================== Context Manager ====================
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the client and release resources."""
        if self._session:
            self._session.close()
            self._session = None


# ==================== Helper Functions ====================


def create_client(
    api_url: str = "http://localhost:8000",
    api_key: Optional[str] = None
) -> DNALockClient:
    """
    Create a DNALockOS client with simple configuration.
    
    Args:
        api_url: The API server URL
        api_key: Optional API key for authentication
    
    Returns:
        Configured DNALockClient instance
    
    Example:
        client = create_client("https://api.dnalock.example.com", "your-api-key")
    """
    config = DNALockConfig(api_url=api_url, api_key=api_key)
    return DNALockClient(config)


def create_client_from_env() -> DNALockClient:
    """
    Create a DNALockOS client from environment variables.
    
    Environment variables:
        DNALOCK_API_URL: API server URL
        DNALOCK_API_KEY: API key
        DNALOCK_CLIENT_ID: Client ID
        DNALOCK_VERIFY_SSL: Whether to verify SSL (true/false)
    
    Returns:
        Configured DNALockClient instance
    """
    return DNALockClient(DNALockConfig.from_env())
