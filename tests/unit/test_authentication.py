"""
DNA-Key Authentication System - Authentication Service Tests

Comprehensive test suite for authentication service.
Tests cover:
- Challenge generation
- Challenge-response authentication
- Session token creation
- Challenge expiry
"""

import pytest
from datetime import datetime, timezone, timedelta
import time

from server.core.authentication import (
    AuthenticationService,
    ChallengeRequest,
    AuthenticationResponse
)
from server.core.enrollment import enroll_user
from server.crypto.dna_key import SecurityLevel
from server.crypto.signatures import Ed25519SigningKey


class TestChallengeGeneration:
    """Test challenge generation."""
    
    def test_generate_challenge_for_enrolled_key(self):
        """Test generating challenge for enrolled key."""
        service = AuthenticationService()
        
        # Enroll a key
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        # Request challenge
        request = ChallengeRequest(key_id=enrollment.key_id)
        response = service.generate_challenge(request)
        
        assert response.success is True
        assert response.challenge is not None
        assert len(response.challenge) == 32
        assert response.challenge_id is not None
    
    def test_generate_challenge_for_unknown_key(self):
        """Test generating challenge for unknown key fails."""
        service = AuthenticationService()
        
        request = ChallengeRequest(key_id="unknown-key")
        response = service.generate_challenge(request)
        
        assert response.success is False
        assert "not found" in response.error_message
    
    def test_challenge_has_expiry(self):
        """Test that challenge has expiry time."""
        service = AuthenticationService()
        
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        request = ChallengeRequest(key_id=enrollment.key_id)
        response = service.generate_challenge(request)
        
        assert response.expires_at is not None
        assert response.expires_at > datetime.now(timezone.utc)
    
    def test_multiple_challenges_unique(self):
        """Test that multiple challenges are unique."""
        service = AuthenticationService()
        
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        request = ChallengeRequest(key_id=enrollment.key_id)
        response1 = service.generate_challenge(request)
        response2 = service.generate_challenge(request)
        
        assert response1.challenge != response2.challenge
        assert response1.challenge_id != response2.challenge_id


class TestAuthentication:
    """Test authentication with challenge-response."""
    
    def test_successful_authentication(self):
        """Test successful authentication flow."""
        service = AuthenticationService()
        
        # Enroll key
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        # Get challenge
        challenge_req = ChallengeRequest(key_id=enrollment.key_id)
        challenge_resp = service.generate_challenge(challenge_req)
        
        # Sign challenge with private key
        # Recreate signing key from the DNA key's crypto material
        from server.crypto.dna_generator import DNAKeyGenerator
        generator = DNAKeyGenerator()
        # For testing, we'll generate and sign with a key pair
        signing_key, verify_key = generator._generate_test_keypair()
        
        # Update the DNA key's public key to match our test key
        enrollment.dna_key.cryptographic_material.public_key = verify_key.to_bytes()
        service.enroll_key(enrollment.dna_key)
        
        # Get new challenge
        challenge_resp = service.generate_challenge(challenge_req)
        
        # Sign challenge
        signature = signing_key.sign(challenge_resp.challenge)
        
        # Authenticate
        auth_resp = service.authenticate(challenge_resp.challenge_id, signature)
        
        assert auth_resp.success is True
        assert auth_resp.session_token is not None
        assert auth_resp.key_id == enrollment.key_id
    
    def test_authentication_with_invalid_signature(self):
        """Test that invalid signature fails authentication."""
        service = AuthenticationService()
        
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        challenge_req = ChallengeRequest(key_id=enrollment.key_id)
        challenge_resp = service.generate_challenge(challenge_req)
        
        # Use wrong signature
        bad_signature = b"x" * 64
        
        auth_resp = service.authenticate(challenge_resp.challenge_id, bad_signature)
        
        assert auth_resp.success is False
        assert "Invalid signature" in auth_resp.error_message
    
    def test_authentication_with_invalid_challenge_id(self):
        """Test that invalid challenge ID fails."""
        service = AuthenticationService()
        
        auth_resp = service.authenticate("invalid-challenge-id", b"signature")
        
        assert auth_resp.success is False
        assert "Invalid challenge ID" in auth_resp.error_message
    
    def test_challenge_cannot_be_reused(self):
        """Test that challenge can only be used once."""
        service = AuthenticationService()
        
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        challenge_req = ChallengeRequest(key_id=enrollment.key_id)
        challenge_resp = service.generate_challenge(challenge_req)
        
        signature = b"x" * 64
        
        # First attempt
        auth_resp1 = service.authenticate(challenge_resp.challenge_id, signature)
        
        # Second attempt with same challenge
        auth_resp2 = service.authenticate(challenge_resp.challenge_id, signature)
        
        assert auth_resp2.success is False
        assert "already used" in auth_resp2.error_message or "Invalid challenge" in auth_resp2.error_message


class TestSessionTokens:
    """Test session token creation."""
    
    def test_session_token_format(self):
        """Test that session token has correct format."""
        service = AuthenticationService()
        
        token = service._create_session_token("test-key-id")
        
        assert token.startswith("dna-session-")
        assert len(token) > 20
    
    def test_session_tokens_unique(self):
        """Test that session tokens are unique."""
        service = AuthenticationService()
        
        token1 = service._create_session_token("key-1")
        token2 = service._create_session_token("key-1")
        
        assert token1 != token2


class TestChallengeExpiry:
    """Test challenge expiry handling."""
    
    def test_expired_challenge_rejected(self):
        """Test that expired challenge is rejected."""
        service = AuthenticationService()
        service.CHALLENGE_EXPIRY_SECONDS = 1  # 1 second for testing
        
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        challenge_req = ChallengeRequest(key_id=enrollment.key_id)
        challenge_resp = service.generate_challenge(challenge_req)
        
        # Wait for expiry
        time.sleep(2)
        
        # Try to authenticate
        auth_resp = service.authenticate(challenge_resp.challenge_id, b"signature")
        
        assert auth_resp.success is False
        assert "expired" in auth_resp.error_message.lower()
    
    def test_cleanup_expired_challenges(self):
        """Test cleanup of expired challenges."""
        service = AuthenticationService()
        service.CHALLENGE_EXPIRY_SECONDS = 1
        
        enrollment = enroll_user("user@example.com")
        service.enroll_key(enrollment.dna_key)
        
        # Generate some challenges
        challenge_req = ChallengeRequest(key_id=enrollment.key_id)
        service.generate_challenge(challenge_req)
        service.generate_challenge(challenge_req)
        
        assert service.get_active_challenges_count() == 2
        
        # Wait for expiry
        time.sleep(2)
        
        # Cleanup
        cleaned = service.cleanup_expired_challenges()
        
        assert cleaned == 2
        assert service.get_active_challenges_count() == 0


class TestMultipleUsers:
    """Test authentication with multiple users."""
    
    def test_authenticate_different_users(self):
        """Test authenticating different users."""
        service = AuthenticationService()
        
        # Enroll two users
        user1 = enroll_user("user1@example.com")
        user2 = enroll_user("user2@example.com")
        service.enroll_key(user1.dna_key)
        service.enroll_key(user2.dna_key)
        
        # Get challenges for both
        challenge1 = service.generate_challenge(ChallengeRequest(key_id=user1.key_id))
        challenge2 = service.generate_challenge(ChallengeRequest(key_id=user2.key_id))
        
        assert challenge1.success is True
        assert challenge2.success is True
        assert challenge1.challenge != challenge2.challenge


class TestKeyValidation:
    """Test key validation during authentication."""
    
    def test_expired_key_rejected(self):
        """Test that expired key is rejected."""
        service = AuthenticationService()
        
        # Enroll key with short validity
        enrollment = enroll_user("user@example.com", validity_days=1)
        
        # Manually expire it
        enrollment.dna_key.expires_timestamp = datetime.now(timezone.utc) - timedelta(days=1)
        service.enroll_key(enrollment.dna_key)
        
        # Try to get challenge
        challenge_req = ChallengeRequest(key_id=enrollment.key_id)
        response = service.generate_challenge(challenge_req)
        
        assert response.success is False
        assert "expired" in response.error_message.lower()
