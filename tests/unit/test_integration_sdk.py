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
DNA-Key Authentication System - Integration SDK Tests

Tests for the platform integration SDK.
"""

import pytest
from datetime import datetime, timezone, timedelta

from server.crypto.dna_key import SecurityLevel
from server.crypto.dna_generator import generate_dna_key
from server.integration.dna_integration_sdk import (
    DNAIntegrationService,
    IntegrationScope,
    AuthenticationFlow,
    IntegrationClient,
    AccessToken,
    DNAChallenge,
    DNAChallengeResponse,
    create_integration_service,
)


class TestDNAIntegrationService:
    """Test DNA Integration Service."""
    
    def test_create_service(self):
        """Test creating an integration service."""
        service = create_integration_service()
        assert service is not None
    
    def test_register_client(self):
        """Test registering a client."""
        service = create_integration_service()
        
        client_id, client_secret = service.register_client(
            client_name="Test App",
            description="A test application",
            redirect_uris=["https://example.com/callback"]
        )
        
        assert client_id.startswith("dna_client_")
        assert len(client_secret) > 20
    
    def test_verify_client(self):
        """Test verifying client credentials."""
        service = create_integration_service()
        
        client_id, client_secret = service.register_client(
            client_name="Test App",
            description="A test application",
            redirect_uris=["https://example.com/callback"]
        )
        
        # Valid credentials
        assert service.verify_client(client_id, client_secret) is True
        
        # Invalid credentials
        assert service.verify_client(client_id, "wrong_secret") is False
        assert service.verify_client("wrong_id", client_secret) is False
    
    def test_get_client(self):
        """Test getting a client by ID."""
        service = create_integration_service()
        
        client_id, _ = service.register_client(
            client_name="Test App",
            description="A test application",
            redirect_uris=["https://example.com/callback"]
        )
        
        client = service.get_client(client_id)
        
        assert client is not None
        assert client.client_name == "Test App"
    
    def test_register_dna_key(self):
        """Test registering a DNA key."""
        service = create_integration_service()
        
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        key_id = service.register_dna_key(dna_key, "user123")
        
        assert key_id is not None
        
        # 3D model should be generated
        model = service.get_3d_model(key_id)
        assert model is not None
        assert len(model.points) > 0


class TestDNAChallengeResponse:
    """Test DNA challenge-response authentication."""
    
    def test_create_challenge(self):
        """Test creating a DNA challenge."""
        service = create_integration_service()
        
        # Register client
        client_id, _ = service.register_client(
            client_name="Test App",
            description="Test",
            redirect_uris=["https://example.com/callback"]
        )
        
        # Register DNA key
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        key_id = service.register_dna_key(dna_key, "user123")
        
        # Create challenge
        challenge = service.create_dna_challenge(client_id, key_id)
        
        assert challenge.challenge_id is not None
        assert len(challenge.requested_point_indices) > 0
        assert challenge.nonce is not None
    
    def test_verify_challenge_response(self):
        """Test verifying a challenge response."""
        service = create_integration_service()
        
        # Register client
        client_id, _ = service.register_client(
            client_name="Test App",
            description="Test",
            redirect_uris=["https://example.com/callback"]
        )
        
        # Register DNA key
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        key_id = service.register_dna_key(dna_key, "user123")
        
        # Get the model
        model = service.get_3d_model(key_id)
        
        # Create challenge
        challenge = service.create_dna_challenge(client_id, key_id)
        
        # Build valid response
        point_responses = []
        for idx in challenge.requested_point_indices:
            if idx < len(model.points):
                point = model.points[idx]
                point_responses.append({
                    "position_hash": point.position_hash,
                    "x": point.x,
                    "y": point.y,
                    "z": point.z
                })
        
        bond_responses = []
        for idx in challenge.requested_bond_indices:
            if idx < len(model.bonds):
                bond = model.bonds[idx]
                bond_responses.append({
                    "bond_hash": bond.bond_hash
                })
        
        response = DNAChallengeResponse(
            challenge_id=challenge.challenge_id,
            point_responses=point_responses,
            bond_responses=bond_responses,
            model_checksum=model.model_checksum,
            response_signature=""
        )
        
        # Verify
        success, message = service.verify_dna_challenge_response(response)
        
        assert success is True
        assert message == "Authentication successful"
    
    def test_invalid_challenge_response(self):
        """Test that invalid responses are rejected."""
        service = create_integration_service()
        
        # Register client
        client_id, _ = service.register_client(
            client_name="Test App",
            description="Test",
            redirect_uris=["https://example.com/callback"]
        )
        
        # Register DNA key
        dna_key = generate_dna_key("user@example.com", SecurityLevel.STANDARD)
        key_id = service.register_dna_key(dna_key, "user123")
        
        # Create challenge
        challenge = service.create_dna_challenge(client_id, key_id)
        
        # Build invalid response (wrong checksum)
        response = DNAChallengeResponse(
            challenge_id=challenge.challenge_id,
            point_responses=[],
            bond_responses=[],
            model_checksum="wrong_checksum",
            response_signature=""
        )
        
        # Verify - should fail
        success, message = service.verify_dna_challenge_response(response)
        
        assert success is False
        assert "mismatch" in message.lower()


class TestAccessTokens:
    """Test access token management."""
    
    def test_validate_token(self):
        """Test token validation."""
        service = create_integration_service()
        
        # Create a token
        token = AccessToken(
            token="test_token_123",
            client_id="client123",
            user_id="user123",
            dna_key_id="dna123",
            scopes=[IntegrationScope.DNA_VERIFY]
        )
        
        service._access_tokens[token.token] = token
        
        # Validate
        validated = service.validate_token("test_token_123")
        
        assert validated is not None
        assert validated.client_id == "client123"
    
    def test_expired_token_invalid(self):
        """Test that expired tokens are invalid."""
        service = create_integration_service()
        
        # Create expired token
        token = AccessToken(
            token="expired_token",
            client_id="client123",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        service._access_tokens[token.token] = token
        
        # Should be invalid
        validated = service.validate_token("expired_token")
        
        assert validated is None
    
    def test_token_introspection(self):
        """Test token introspection."""
        service = create_integration_service()
        
        # Create token
        token = AccessToken(
            token="introspect_token",
            client_id="client123",
            user_id="user123",
            dna_key_id="dna123",
            scopes=[IntegrationScope.DNA_VERIFY, IntegrationScope.DNA_READ],
            dna_model_hash="abc123",
            security_level="30",
            verification_status="verified"
        )
        
        service._access_tokens[token.token] = token
        
        # Introspect
        info = service.introspect_token("introspect_token")
        
        assert info["active"] is True
        assert info["client_id"] == "client123"
        assert info["dna_key_id"] == "dna123"
        assert info["verification_status"] == "verified"


class TestRateLimiting:
    """Test rate limiting."""
    
    def test_rate_limit_allows_requests(self):
        """Test that rate limiting allows normal requests."""
        service = create_integration_service()
        
        client_id, _ = service.register_client(
            client_name="Test App",
            description="Test",
            redirect_uris=["https://example.com/callback"]
        )
        
        # First request should be allowed
        assert service.check_rate_limit(client_id) is True
    
    def test_rate_limit_per_minute(self):
        """Test per-minute rate limiting."""
        service = create_integration_service()
        
        client_id, _ = service.register_client(
            client_name="Test App",
            description="Test",
            redirect_uris=["https://example.com/callback"]
        )
        
        # Get the client and set a low limit for testing
        client = service.get_client(client_id)
        client.rate_limit_per_minute = 5
        
        # Make 5 requests (should all succeed)
        for _ in range(5):
            assert service.check_rate_limit(client_id) is True
        
        # 6th request should fail
        assert service.check_rate_limit(client_id) is False


class TestIntegrationScopes:
    """Test integration scopes."""
    
    def test_scope_values(self):
        """Test scope enum values."""
        assert IntegrationScope.DNA_READ.value == "dna:read"
        assert IntegrationScope.DNA_VERIFY.value == "dna:verify"
        assert IntegrationScope.DNA_GENERATE.value == "dna:generate"
        assert IntegrationScope.DNA_3D_MODEL.value == "dna:3d_model"
    
    def test_token_has_scope(self):
        """Test checking token scopes."""
        token = AccessToken(
            token="test",
            scopes=[IntegrationScope.DNA_VERIFY, IntegrationScope.DNA_READ]
        )
        
        assert token.has_scope(IntegrationScope.DNA_VERIFY) is True
        assert token.has_scope(IntegrationScope.DNA_READ) is True
        assert token.has_scope(IntegrationScope.DNA_ADMIN) is False


class TestAuthenticationFlows:
    """Test authentication flow support."""
    
    def test_flow_values(self):
        """Test authentication flow enum values."""
        assert AuthenticationFlow.AUTHORIZATION_CODE.value == "authorization_code"
        assert AuthenticationFlow.CLIENT_CREDENTIALS.value == "client_credentials"
        assert AuthenticationFlow.DNA_CHALLENGE_RESPONSE.value == "dna_challenge_response"
    
    def test_client_allowed_flows(self):
        """Test client allowed flows."""
        service = create_integration_service()
        
        client_id, _ = service.register_client(
            client_name="Test App",
            description="Test",
            redirect_uris=["https://example.com/callback"],
            allowed_flows=[
                AuthenticationFlow.AUTHORIZATION_CODE,
                AuthenticationFlow.DNA_CHALLENGE_RESPONSE
            ]
        )
        
        client = service.get_client(client_id)
        
        assert AuthenticationFlow.AUTHORIZATION_CODE in client.allowed_flows
        assert AuthenticationFlow.DNA_CHALLENGE_RESPONSE in client.allowed_flows
