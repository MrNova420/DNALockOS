"""
DNA-Key Authentication System - Platform Integration SDK

THIS MODULE ENABLES OTHER PLATFORMS AND SYSTEMS TO AUTHENTICATE DNA STRANDS.

Since DNALockOS uses a completely unique, futuristic authentication system
(the 3D DNA strand model IS the authentication itself), we need to provide
a complete integration framework that allows:

1. Third-party platforms to integrate DNA authentication
2. Verification of DNA strands from any system
3. Challenge-response authentication flows
4. SDK for multiple programming languages (via REST API)
5. Webhooks for authentication events
6. OAuth 2.0 / OpenID Connect compatibility layer

This is the bridge between our futuristic DNA authentication
and the rest of the world's systems.
"""

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

from server.crypto.dna_key import DNAKey, SecurityLevel
from server.crypto.dna_verifier import DNAVerifier, VerificationReport, VerificationResult
from server.visual.dna_strand_3d_model import (
    DNAStrand3DModel,
    DNAStrand3DGenerator,
    DNAStrandShape,
    DNAStrandStyle,
    generate_dna_strand_3d,
)


class IntegrationScope(Enum):
    """OAuth-style scopes for DNA authentication."""
    
    # Basic scopes
    DNA_READ = "dna:read"              # Read DNA key metadata
    DNA_VERIFY = "dna:verify"          # Verify DNA authentication
    DNA_GENERATE = "dna:generate"       # Generate new DNA keys
    
    # Advanced scopes
    DNA_3D_MODEL = "dna:3d_model"       # Access 3D model data
    DNA_REVOKE = "dna:revoke"           # Revoke DNA keys
    DNA_ADMIN = "dna:admin"             # Administrative access
    
    # Identity scopes
    PROFILE = "profile"                 # User profile info
    EMAIL = "email"                     # Email address
    
    # OpenID Connect
    OPENID = "openid"                   # OpenID Connect


class AuthenticationFlow(Enum):
    """Supported authentication flows."""
    
    # Standard flows
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    
    # DNA-specific flows
    DNA_CHALLENGE_RESPONSE = "dna_challenge_response"
    DNA_3D_MODEL_VERIFY = "dna_3d_model_verify"
    DNA_VISUAL_MATCH = "dna_visual_match"


@dataclass
class IntegrationClient:
    """
    A registered client application that can use DNA authentication.
    
    Every platform/system that wants to authenticate DNA strands
    must register as a client first.
    """
    
    client_id: str
    client_secret_hash: str  # Stored as hash, not plaintext
    client_name: str
    description: str
    
    # Allowed authentication flows
    allowed_flows: List[AuthenticationFlow] = field(default_factory=list)
    
    # Allowed scopes
    allowed_scopes: List[IntegrationScope] = field(default_factory=list)
    
    # Redirect URIs for OAuth flows
    redirect_uris: List[str] = field(default_factory=list)
    
    # Webhook configuration
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_day: int = 10000
    
    # Security settings
    require_pkce: bool = True
    token_lifetime_seconds: int = 3600
    refresh_token_lifetime_seconds: int = 86400 * 30  # 30 days
    
    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def verify_secret(self, secret: str) -> bool:
        """Verify client secret."""
        secret_hash = hashlib.sha3_256(secret.encode()).hexdigest()
        return secrets.compare_digest(secret_hash, self.client_secret_hash)


@dataclass
class AuthorizationCode:
    """OAuth authorization code."""
    
    code: str
    client_id: str
    user_id: str
    dna_key_id: str
    scopes: List[IntegrationScope]
    redirect_uri: str
    code_challenge: Optional[str]  # PKCE
    code_challenge_method: str = "S256"
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    used: bool = False


@dataclass
class AccessToken:
    """DNA authentication access token."""
    
    token: str
    token_type: str = "Bearer"
    client_id: str = ""
    user_id: str = ""
    dna_key_id: str = ""
    scopes: List[IntegrationScope] = field(default_factory=list)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    # DNA-specific claims
    dna_model_hash: str = ""  # Hash of the 3D model
    security_level: str = ""
    verification_status: str = ""
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def has_scope(self, scope: IntegrationScope) -> bool:
        """Check if token has a specific scope."""
        return scope in self.scopes
    
    def to_jwt_claims(self) -> Dict[str, Any]:
        """Convert to JWT claims format."""
        return {
            "sub": self.user_id,
            "client_id": self.client_id,
            "dna_key_id": self.dna_key_id,
            "scope": " ".join(s.value for s in self.scopes),
            "exp": int(self.expires_at.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "dna_model_hash": self.dna_model_hash,
            "security_level": self.security_level,
            "verification_status": self.verification_status
        }


@dataclass
class DNAChallenge:
    """
    Challenge for DNA 3D model authentication.
    
    The client must prove they have the actual 3D DNA strand
    by responding with specific point data from their model.
    """
    
    challenge_id: str
    client_id: str
    dna_key_id: str
    
    # Challenge parameters
    requested_point_indices: List[int]
    requested_bond_indices: List[int]
    nonce: str
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(seconds=60)
    )
    
    # State
    responded: bool = False
    verified: bool = False
    
    def is_expired(self) -> bool:
        """Check if challenge is expired."""
        return datetime.now(timezone.utc) > self.expires_at


@dataclass
class DNAChallengeResponse:
    """Response to a DNA challenge."""
    
    challenge_id: str
    
    # Point data from the user's 3D model
    point_responses: List[Dict[str, Any]]
    bond_responses: List[Dict[str, Any]]
    
    # Model checksum
    model_checksum: str
    
    # Signature of the response
    response_signature: str


class DNAIntegrationService:
    """
    Main service for DNA authentication integration.
    
    This service enables ANY platform or system to integrate
    DNA strand authentication. It provides:
    
    1. Client registration and management
    2. OAuth 2.0 / OIDC compatible flows
    3. DNA-specific challenge-response authentication
    4. 3D model verification
    5. Webhook notifications
    6. Rate limiting and security controls
    """
    
    def __init__(self):
        # Storage (in production, use database)
        self._clients: Dict[str, IntegrationClient] = {}
        self._auth_codes: Dict[str, AuthorizationCode] = {}
        self._access_tokens: Dict[str, AccessToken] = {}
        self._challenges: Dict[str, DNAChallenge] = {}
        self._dna_keys: Dict[str, DNAKey] = {}
        self._dna_3d_models: Dict[str, DNAStrand3DModel] = {}
        
        # Verifier
        self._verifier = DNAVerifier()
        
        # Rate limiting (in production, use Redis)
        self._rate_limits: Dict[str, List[float]] = {}
    
    # ==================== Client Management ====================
    
    def register_client(
        self,
        client_name: str,
        description: str,
        redirect_uris: List[str],
        allowed_flows: Optional[List[AuthenticationFlow]] = None,
        allowed_scopes: Optional[List[IntegrationScope]] = None,
        webhook_url: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Register a new integration client.
        
        Returns:
            Tuple of (client_id, client_secret)
            
        NOTE: client_secret is only returned once - store it securely!
        """
        # Generate credentials
        client_id = f"dna_client_{secrets.token_hex(16)}"
        client_secret = secrets.token_urlsafe(32)
        client_secret_hash = hashlib.sha3_256(client_secret.encode()).hexdigest()
        
        # Generate webhook secret if webhook URL provided
        webhook_secret = secrets.token_urlsafe(32) if webhook_url else None
        
        # Default flows and scopes
        if allowed_flows is None:
            allowed_flows = [
                AuthenticationFlow.AUTHORIZATION_CODE,
                AuthenticationFlow.DNA_CHALLENGE_RESPONSE
            ]
        
        if allowed_scopes is None:
            allowed_scopes = [
                IntegrationScope.DNA_VERIFY,
                IntegrationScope.DNA_READ,
                IntegrationScope.PROFILE
            ]
        
        # Create client
        client = IntegrationClient(
            client_id=client_id,
            client_secret_hash=client_secret_hash,
            client_name=client_name,
            description=description,
            allowed_flows=allowed_flows,
            allowed_scopes=allowed_scopes,
            redirect_uris=redirect_uris,
            webhook_url=webhook_url,
            webhook_secret=webhook_secret
        )
        
        self._clients[client_id] = client
        
        return client_id, client_secret
    
    def get_client(self, client_id: str) -> Optional[IntegrationClient]:
        """Get a client by ID."""
        return self._clients.get(client_id)
    
    def verify_client(self, client_id: str, client_secret: str) -> bool:
        """Verify client credentials."""
        client = self.get_client(client_id)
        if not client or not client.is_active:
            return False
        return client.verify_secret(client_secret)
    
    # ==================== DNA Key Management ====================
    
    def register_dna_key(self, dna_key: DNAKey, user_id: str) -> str:
        """
        Register a DNA key for authentication.
        
        This generates the 3D model that IS the authentication.
        """
        key_id = dna_key.key_id or f"dna-{secrets.token_hex(16)}"
        
        # Store the DNA key
        self._dna_keys[key_id] = dna_key
        
        # Generate the 3D model (THIS IS THE AUTHENTICATION)
        model = generate_dna_strand_3d(
            dna_key,
            shape=DNAStrandShape.DOUBLE_HELIX,
            style=DNAStrandStyle.TRON
        )
        self._dna_3d_models[key_id] = model
        
        return key_id
    
    def get_3d_model(self, dna_key_id: str) -> Optional[DNAStrand3DModel]:
        """Get the 3D model for a DNA key."""
        return self._dna_3d_models.get(dna_key_id)
    
    # ==================== OAuth 2.0 Flows ====================
    
    def create_authorization_url(
        self,
        client_id: str,
        redirect_uri: str,
        scopes: List[IntegrationScope],
        state: str,
        code_challenge: Optional[str] = None,
        code_challenge_method: str = "S256"
    ) -> str:
        """
        Create authorization URL for OAuth flow.
        
        This is how third-party platforms start DNA authentication.
        """
        client = self.get_client(client_id)
        if not client:
            raise ValueError("Invalid client_id")
        
        if redirect_uri not in client.redirect_uris:
            raise ValueError("Invalid redirect_uri")
        
        # Validate scopes
        for scope in scopes:
            if scope not in client.allowed_scopes:
                raise ValueError(f"Scope {scope.value} not allowed for this client")
        
        # PKCE required
        if client.require_pkce and not code_challenge:
            raise ValueError("PKCE code_challenge required")
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(s.value for s in scopes),
            "state": state,
            "response_type": "code"
        }
        
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = code_challenge_method
        
        # In production, this would be the actual auth server URL
        base_url = "https://auth.dnalockos.com/authorize"
        return f"{base_url}?{urlencode(params)}"
    
    def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        dna_key_id: str,
        scopes: List[IntegrationScope],
        redirect_uri: str,
        code_challenge: Optional[str] = None
    ) -> str:
        """
        Create an authorization code after user authenticates.
        
        This is called after the user proves they have their DNA strand.
        """
        code = secrets.token_urlsafe(32)
        
        auth_code = AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            dna_key_id=dna_key_id,
            scopes=scopes,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge
        )
        
        self._auth_codes[code] = auth_code
        
        return code
    
    def exchange_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Optional[AccessToken]:
        """
        Exchange authorization code for access token.
        
        This is the standard OAuth token exchange.
        """
        # Verify client
        if not self.verify_client(client_id, client_secret):
            return None
        
        # Get and validate auth code
        auth_code = self._auth_codes.get(code)
        if not auth_code:
            return None
        
        if auth_code.used:
            return None
        
        if auth_code.client_id != client_id:
            return None
        
        if auth_code.redirect_uri != redirect_uri:
            return None
        
        if datetime.now(timezone.utc) > auth_code.expires_at:
            return None
        
        # Verify PKCE if present
        if auth_code.code_challenge:
            if not code_verifier:
                return None
            
            # Verify S256 challenge
            verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
            import base64
            computed_challenge = base64.urlsafe_b64encode(verifier_hash).rstrip(b'=').decode()
            
            if not secrets.compare_digest(computed_challenge, auth_code.code_challenge):
                return None
        
        # Mark code as used
        auth_code.used = True
        
        # Get DNA key and model
        dna_key = self._dna_keys.get(auth_code.dna_key_id)
        model = self._dna_3d_models.get(auth_code.dna_key_id)
        
        # Create access token
        client = self.get_client(client_id)
        token = AccessToken(
            token=secrets.token_urlsafe(32),
            client_id=client_id,
            user_id=auth_code.user_id,
            dna_key_id=auth_code.dna_key_id,
            scopes=auth_code.scopes,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=client.token_lifetime_seconds),
            dna_model_hash=model.model_checksum if model else "",
            security_level=str(dna_key.security_methods.total_methods_count) if dna_key else "0",
            verification_status="verified"
        )
        
        self._access_tokens[token.token] = token
        
        return token
    
    # ==================== DNA Challenge-Response ====================
    
    def create_dna_challenge(
        self,
        client_id: str,
        dna_key_id: str
    ) -> DNAChallenge:
        """
        Create a challenge for DNA 3D model authentication.
        
        The user must prove they have the actual 3D DNA strand
        by responding with specific point/bond data.
        """
        client = self.get_client(client_id)
        if not client:
            raise ValueError("Invalid client_id")
        
        model = self._dna_3d_models.get(dna_key_id)
        if not model:
            raise ValueError("DNA key not found")
        
        # Select random points to challenge
        num_points = len(model.points)
        num_bonds = len(model.bonds)
        
        point_indices = sorted([
            secrets.randbelow(num_points) for _ in range(10)
        ])
        
        bond_indices = sorted([
            secrets.randbelow(num_bonds) for _ in range(5)
        ]) if num_bonds > 5 else []
        
        challenge = DNAChallenge(
            challenge_id=secrets.token_hex(32),
            client_id=client_id,
            dna_key_id=dna_key_id,
            requested_point_indices=point_indices,
            requested_bond_indices=bond_indices,
            nonce=secrets.token_hex(16)
        )
        
        self._challenges[challenge.challenge_id] = challenge
        
        return challenge
    
    def verify_dna_challenge_response(
        self,
        response: DNAChallengeResponse
    ) -> Tuple[bool, str]:
        """
        Verify a DNA challenge response.
        
        This is where we verify that the user actually has
        the correct 3D DNA strand model.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Get the challenge
        challenge = self._challenges.get(response.challenge_id)
        if not challenge:
            return False, "Challenge not found"
        
        if challenge.is_expired():
            return False, "Challenge expired"
        
        if challenge.responded:
            return False, "Challenge already used"
        
        # Get the expected 3D model
        model = self._dna_3d_models.get(challenge.dna_key_id)
        if not model:
            return False, "DNA model not found"
        
        # Verify model checksum
        if not secrets.compare_digest(response.model_checksum, model.model_checksum):
            return False, "Model checksum mismatch"
        
        # Verify point responses
        if len(response.point_responses) != len(challenge.requested_point_indices):
            return False, "Incorrect number of point responses"
        
        for i, point_idx in enumerate(challenge.requested_point_indices):
            if point_idx >= len(model.points):
                continue
            
            expected_point = model.points[point_idx]
            actual_response = response.point_responses[i]
            
            # Verify position hash
            if actual_response.get("position_hash") != expected_point.position_hash:
                return False, f"Point {point_idx} position hash mismatch"
            
            # Verify coordinates (with tolerance)
            if abs(actual_response.get("x", 0) - expected_point.x) > 0.001:
                return False, f"Point {point_idx} X coordinate mismatch"
            if abs(actual_response.get("y", 0) - expected_point.y) > 0.001:
                return False, f"Point {point_idx} Y coordinate mismatch"
            if abs(actual_response.get("z", 0) - expected_point.z) > 0.001:
                return False, f"Point {point_idx} Z coordinate mismatch"
        
        # Verify bond responses
        for i, bond_idx in enumerate(challenge.requested_bond_indices):
            if bond_idx >= len(model.bonds) or i >= len(response.bond_responses):
                continue
            
            expected_bond = model.bonds[bond_idx]
            actual_response = response.bond_responses[i]
            
            if actual_response.get("bond_hash") != expected_bond.bond_hash:
                return False, f"Bond {bond_idx} hash mismatch"
        
        # Mark challenge as used
        challenge.responded = True
        challenge.verified = True
        
        return True, "Authentication successful"
    
    # ==================== Token Validation ====================
    
    def validate_token(self, token: str) -> Optional[AccessToken]:
        """Validate an access token."""
        access_token = self._access_tokens.get(token)
        
        if not access_token:
            return None
        
        if access_token.is_expired():
            return None
        
        return access_token
    
    def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Introspect a token (RFC 7662).
        
        Returns token metadata for third-party verification.
        """
        access_token = self.validate_token(token)
        
        if not access_token:
            return {"active": False}
        
        return {
            "active": True,
            "client_id": access_token.client_id,
            "username": access_token.user_id,
            "scope": " ".join(s.value for s in access_token.scopes),
            "exp": int(access_token.expires_at.timestamp()),
            "iat": int((access_token.expires_at - timedelta(hours=1)).timestamp()),
            "sub": access_token.user_id,
            "token_type": access_token.token_type,
            
            # DNA-specific claims
            "dna_key_id": access_token.dna_key_id,
            "dna_model_hash": access_token.dna_model_hash,
            "security_level": access_token.security_level,
            "verification_status": access_token.verification_status
        }
    
    # ==================== Webhook Notifications ====================
    
    def send_webhook(
        self,
        client_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Send webhook notification to client.
        
        Event types:
        - dna.authenticated: User authenticated with DNA
        - dna.verification_failed: Authentication failed
        - dna.key_revoked: DNA key was revoked
        - dna.challenge_created: New challenge created
        """
        client = self.get_client(client_id)
        if not client or not client.webhook_url:
            return False
        
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload
        }
        
        # Sign the payload
        if client.webhook_secret:
            payload_json = json.dumps(webhook_payload, sort_keys=True)
            signature = hmac.new(
                client.webhook_secret.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            webhook_payload["signature"] = signature
        
        # In production, this would make an HTTP POST request
        # For now, we just return True
        return True
    
    # ==================== Rate Limiting ====================
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits."""
        client = self.get_client(client_id)
        if not client:
            return False
        
        now = time.time()
        minute_ago = now - 60
        day_ago = now - 86400
        
        # Get request timestamps
        timestamps = self._rate_limits.get(client_id, [])
        
        # Clean old timestamps
        timestamps = [t for t in timestamps if t > day_ago]
        self._rate_limits[client_id] = timestamps
        
        # Count recent requests
        requests_last_minute = sum(1 for t in timestamps if t > minute_ago)
        requests_last_day = len(timestamps)
        
        if requests_last_minute >= client.rate_limit_per_minute:
            return False
        
        if requests_last_day >= client.rate_limit_per_day:
            return False
        
        # Record this request
        timestamps.append(now)
        
        return True


# ==================== Convenience Functions ====================

def create_integration_service() -> DNAIntegrationService:
    """Create a new DNA integration service instance."""
    return DNAIntegrationService()


def quick_dna_authenticate(
    service: DNAIntegrationService,
    client_id: str,
    dna_key_id: str,
    model_data: Dict[str, Any]
) -> Tuple[bool, str, Optional[AccessToken]]:
    """
    Quick DNA authentication for simple integrations.
    
    Args:
        service: The integration service
        client_id: The client ID
        dna_key_id: The DNA key ID to authenticate
        model_data: The user's 3D model data
        
    Returns:
        Tuple of (success, message, access_token)
    """
    # Create challenge
    try:
        challenge = service.create_dna_challenge(client_id, dna_key_id)
    except ValueError as e:
        return False, str(e), None
    
    # Build response from model data
    point_responses = []
    for idx in challenge.requested_point_indices:
        points = model_data.get("points", [])
        if idx < len(points):
            point = points[idx]
            point_responses.append({
                "position_hash": point.get("auth", {}).get("position_hash", ""),
                "x": point.get("position", {}).get("x", 0),
                "y": point.get("position", {}).get("y", 0),
                "z": point.get("position", {}).get("z", 0)
            })
    
    bond_responses = []
    for idx in challenge.requested_bond_indices:
        bonds = model_data.get("bonds", [])
        if idx < len(bonds):
            bond = bonds[idx]
            bond_responses.append({
                "bond_hash": bond.get("auth_hash", "")
            })
    
    response = DNAChallengeResponse(
        challenge_id=challenge.challenge_id,
        point_responses=point_responses,
        bond_responses=bond_responses,
        model_checksum=model_data.get("authentication", {}).get("model_checksum", ""),
        response_signature=""
    )
    
    # Verify
    success, message = service.verify_dna_challenge_response(response)
    
    if not success:
        return False, message, None
    
    # Issue token
    token = AccessToken(
        token=secrets.token_urlsafe(32),
        client_id=client_id,
        dna_key_id=dna_key_id,
        scopes=[IntegrationScope.DNA_VERIFY],
        dna_model_hash=model_data.get("authentication", {}).get("model_checksum", ""),
        verification_status="verified"
    )
    
    service._access_tokens[token.token] = token
    
    return True, "Authentication successful", token
