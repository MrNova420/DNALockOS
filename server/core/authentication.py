"""
DNA-Key Authentication System - Authentication Service

Implements challenge-response authentication protocol for DNA keys.

Authentication Flow:
1. Client initiates authentication with key ID
2. Server generates challenge
3. Client signs challenge with DNA key
4. Server verifies signature
5. Server creates session token
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from server.crypto.dna_key import DNAKey
from server.crypto.signatures import Ed25519VerifyKey


@dataclass
class AuthenticationRequest:
    """Request to authenticate with a DNA key."""

    key_id: str
    challenge_response: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChallengeRequest:
    """Request for authentication challenge."""

    key_id: str


@dataclass
class ChallengeResponse:
    """Response containing authentication challenge."""

    success: bool
    challenge: Optional[bytes] = None
    challenge_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class AuthenticationResponse:
    """Response from authentication attempt."""

    success: bool
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    key_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None


class AuthenticationError(Exception):
    """Exception raised during authentication."""

    pass


class AuthenticationService:
    """
    Service for DNA key authentication using challenge-response.

    Implements secure challenge-response protocol to verify
    possession of DNA key without transmitting private keys.
    """

    # Challenge expiry in seconds
    CHALLENGE_EXPIRY_SECONDS = 300  # 5 minutes

    # Session expiry in seconds
    SESSION_EXPIRY_SECONDS = 3600  # 1 hour

    def __init__(self):
        """Initialize authentication service."""
        # In-memory storage for active challenges
        # In production, this would be Redis or similar
        self._challenges: Dict[str, Dict[str, Any]] = {}

        # In-memory storage for enrolled keys
        # In production, this would be a database
        self._enrolled_keys: Dict[str, DNAKey] = {}

    def enroll_key(self, dna_key: DNAKey) -> None:
        """
        Enroll a DNA key for authentication.

        Args:
            dna_key: DNA key to enroll

        Note:
            In production, this would store in database.
        """
        self._enrolled_keys[dna_key.key_id] = dna_key

    def generate_challenge(self, request: ChallengeRequest) -> ChallengeResponse:
        """
        Generate an authentication challenge.

        Args:
            request: Challenge request with key ID

        Returns:
            ChallengeResponse with challenge data

        Example:
            >>> service = AuthenticationService()
            >>> request = ChallengeRequest(key_id="dna-abc123")
            >>> response = service.generate_challenge(request)
            >>> if response.success:
            ...     # Client signs response.challenge
        """
        try:
            # Validate key exists
            if request.key_id not in self._enrolled_keys:
                return ChallengeResponse(success=False, error_message="Key not found")

            dna_key = self._enrolled_keys[request.key_id]

            # Check if key is valid
            if not dna_key.is_valid() or dna_key.is_expired():
                return ChallengeResponse(success=False, error_message="Key is invalid or expired")

            # Generate random challenge (32 bytes)
            challenge = secrets.token_bytes(32)
            challenge_id = secrets.token_hex(16)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.CHALLENGE_EXPIRY_SECONDS)

            # Store challenge
            self._challenges[challenge_id] = {
                "challenge": challenge,
                "key_id": request.key_id,
                "expires_at": expires_at,
                "used": False,
            }

            return ChallengeResponse(
                success=True, challenge=challenge, challenge_id=challenge_id, expires_at=expires_at
            )

        except Exception as e:
            return ChallengeResponse(success=False, error_message=str(e))

    def authenticate(self, challenge_id: str, challenge_response: bytes) -> AuthenticationResponse:
        """
        Authenticate using challenge response.

        Args:
            challenge_id: ID of the challenge being responded to
            challenge_response: Signed challenge from client

        Returns:
            AuthenticationResponse with session token or error

        Example:
            >>> # After getting challenge
            >>> response = service.authenticate(challenge_id, signed_challenge)
            >>> if response.success:
            ...     print(f"Session token: {response.session_token}")
        """
        try:
            # Validate challenge exists
            if challenge_id not in self._challenges:
                return AuthenticationResponse(
                    success=False, error_message="Invalid challenge ID", timestamp=datetime.now(timezone.utc)
                )

            challenge_data = self._challenges[challenge_id]

            # Check if challenge is expired
            if datetime.now(timezone.utc) > challenge_data["expires_at"]:
                del self._challenges[challenge_id]
                return AuthenticationResponse(
                    success=False, error_message="Challenge expired", timestamp=datetime.now(timezone.utc)
                )

            # Check if challenge already used
            if challenge_data["used"]:
                return AuthenticationResponse(
                    success=False, error_message="Challenge already used", timestamp=datetime.now(timezone.utc)
                )

            # Mark challenge as used
            challenge_data["used"] = True

            # Get enrolled key
            key_id = challenge_data["key_id"]
            dna_key = self._enrolled_keys[key_id]

            # Verify signature
            if not self._verify_challenge_response(dna_key, challenge_data["challenge"], challenge_response):
                return AuthenticationResponse(
                    success=False, error_message="Invalid signature", timestamp=datetime.now(timezone.utc)
                )

            # Create session token
            session_token = self._create_session_token(key_id)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.SESSION_EXPIRY_SECONDS)

            # Clean up used challenge
            del self._challenges[challenge_id]

            return AuthenticationResponse(
                success=True,
                session_token=session_token,
                expires_at=expires_at,
                key_id=key_id,
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            return AuthenticationResponse(success=False, error_message=str(e), timestamp=datetime.now(timezone.utc))

    def _verify_challenge_response(self, dna_key: DNAKey, challenge: bytes, response: bytes) -> bool:
        """
        Verify challenge response signature.

        Args:
            dna_key: DNA key being authenticated
            challenge: Original challenge
            response: Signed challenge response

        Returns:
            True if signature valid, False otherwise
        """
        try:
            # Get public key from DNA key
            if not dna_key.cryptographic_material or not dna_key.cryptographic_material.public_key:
                return False

            # Create verify key
            verify_key = Ed25519VerifyKey.from_bytes(dna_key.cryptographic_material.public_key)

            # Verify signature
            return verify_key.verify(challenge, response)

        except Exception:
            return False

    def _create_session_token(self, key_id: str) -> str:
        """
        Create a session token.

        Args:
            key_id: Key ID for the session

        Returns:
            Session token string
        """
        # Create token with key ID and random data
        token_data = f"{key_id}:{secrets.token_hex(32)}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        return f"dna-session-{token_hash}"

    def get_active_challenges_count(self) -> int:
        """Get count of active challenges."""
        return len(self._challenges)

    def cleanup_expired_challenges(self) -> int:
        """
        Clean up expired challenges.

        Returns:
            Number of challenges cleaned up
        """
        now = datetime.now(timezone.utc)
        expired = [cid for cid, data in self._challenges.items() if now > data["expires_at"]]

        for cid in expired:
            del self._challenges[cid]

        return len(expired)
