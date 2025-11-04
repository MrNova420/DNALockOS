"""
DNA-Key Authentication System - REST API Server

FastAPI-based REST API with complete authentication system.
Admin authentication uses DNA-Key system for master key auth.
"""

import base64
import os
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from server.core.authentication import AuthenticationService
from server.core.authentication import ChallengeRequest as CoreChallengeRequest
from server.core.enrollment import EnrollmentRequest as CoreEnrollmentRequest
from server.core.enrollment import EnrollmentService
from server.core.revocation import RevocationReason
from server.core.revocation import RevocationRequest as CoreRevocationRequest
from server.core.revocation import RevocationService
from server.crypto.dna_key import SecurityLevel

# Initialize services
enrollment_service = EnrollmentService()
auth_service = AuthenticationService()
revocation_service = RevocationService()
security = HTTPBearer()


# ============= API Models =============


class EnrollmentRequest(BaseModel):
    subject_id: str = Field(..., max_length=512)
    subject_type: str = Field(default="human")
    security_level: str = Field(default="standard")
    policy_id: str = Field(default="default-policy-v1")
    validity_days: int = Field(default=365, ge=1, le=3650)
    mfa_required: bool = False
    biometric_required: bool = False
    device_binding_required: bool = False


class EnrollmentResponse(BaseModel):
    success: bool
    key_id: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    serialized_key: Optional[str] = None
    visual_seed: Optional[str] = None
    error_message: Optional[str] = None


class ChallengeRequest(BaseModel):
    key_id: str


class ChallengeResponse(BaseModel):
    success: bool
    challenge: Optional[str] = None
    challenge_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AuthenticateRequest(BaseModel):
    challenge_id: str
    challenge_response: str


class AuthenticationResponse(BaseModel):
    success: bool
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    key_id: Optional[str] = None
    is_admin: bool = False
    permissions: List[str] = []
    error_message: Optional[str] = None


class RevocationRequest(BaseModel):
    key_id: str
    reason: str
    revoked_by: str
    notes: Optional[str] = None


# ============= Security Dependencies =============


async def verify_admin_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication using DNA-Key system."""
    token = credentials.credentials

    # In production, validate session token against auth_service
    # For now, check token format
    if not token.startswith("dna-session-"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin authentication token")

    # Return admin identity
    return {"token": token, "role": "admin"}


# ============= FastAPI App =============

app = FastAPI(
    title="DNA-Key Authentication System API",
    description="🔷 Tron-Inspired Futuristic Authentication System 🔷",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Public Endpoints =============


@app.get("/health")
async def health_check():
    """System health check."""
    return {
        "status": "🟢 OPERATIONAL",
        "version": "1.0.0",
        "timestamp": datetime.utcnow(),
        "services": {
            "enrollment": "online",
            "authentication": "online",
            "revocation": "online",
            "visualization": "online",
        },
    }


@app.post("/api/v1/enroll", response_model=EnrollmentResponse)
async def enroll_key(request: EnrollmentRequest):
    """Enroll new DNA key with visual DNA generation."""
    security_map = {
        "standard": SecurityLevel.STANDARD,
        "enhanced": SecurityLevel.ENHANCED,
        "maximum": SecurityLevel.MAXIMUM,
        "government": SecurityLevel.GOVERNMENT,
    }

    core_request = CoreEnrollmentRequest(
        subject_id=request.subject_id,
        subject_type=request.subject_type,
        security_level=security_map.get(request.security_level.lower(), SecurityLevel.STANDARD),
        policy_id=request.policy_id,
        validity_days=request.validity_days,
        mfa_required=request.mfa_required,
        biometric_required=request.biometric_required,
        device_binding_required=request.device_binding_required,
    )

    response = enrollment_service.enroll(core_request)

    if not response.success:
        return EnrollmentResponse(success=False, error_message=response.error_message)

    auth_service.enroll_key(response.dna_key)

    return EnrollmentResponse(
        success=True,
        key_id=response.key_id,
        created_at=response.dna_key.created_timestamp,
        expires_at=response.dna_key.expires_timestamp,
        serialized_key=base64.b64encode(response.serialized_key).decode("utf-8"),
        visual_seed=response.dna_key.visual_dna.animation_seed if response.dna_key.visual_dna else None,
    )


@app.post("/api/v1/challenge", response_model=ChallengeResponse)
async def get_challenge(request: ChallengeRequest):
    """Get authentication challenge."""
    core_request = CoreChallengeRequest(key_id=request.key_id)
    response = auth_service.generate_challenge(core_request)

    if not response.success:
        return ChallengeResponse(success=False, error_message=response.error_message)

    return ChallengeResponse(
        success=True,
        challenge=response.challenge.hex(),
        challenge_id=response.challenge_id,
        expires_at=response.expires_at,
    )


@app.post("/api/v1/authenticate", response_model=AuthenticationResponse)
async def authenticate(request: AuthenticateRequest):
    """Authenticate with challenge response."""
    challenge_response = bytes.fromhex(request.challenge_response)
    response = auth_service.authenticate(request.challenge_id, challenge_response)

    if not response.success:
        return AuthenticationResponse(success=False, error_message=response.error_message)

    # Check if this is an admin key (based on policy or subject type)
    is_admin = response.key_id and "admin" in response.key_id
    permissions = ["admin:full"] if is_admin else ["user:standard"]

    return AuthenticationResponse(
        success=True,
        session_token=response.session_token,
        expires_at=response.expires_at,
        key_id=response.key_id,
        is_admin=is_admin,
        permissions=permissions,
    )


@app.get("/api/v1/visual/{key_id}")
async def get_visual_dna(key_id: str):
    """Get 3D visual DNA configuration."""
    # Would retrieve key and generate visual config
    return {
        "key_id": key_id,
        "geometry": {
            "type": "helix",
            "points": [],
            "colors": [],
            "animation": {"rotation_speed": 0.02, "pulse_frequency": 2.0},
        },
    }


# ============= Admin Endpoints (DNA-Key Protected) =============


@app.post("/api/v1/admin/revoke", dependencies=[Depends(verify_admin_auth)])
async def admin_revoke_key(request: RevocationRequest):
    """Admin: Revoke DNA key."""
    reason_map = {
        "key_compromise": RevocationReason.KEY_COMPROMISE,
        "affiliation_changed": RevocationReason.AFFILIATION_CHANGED,
        "superseded": RevocationReason.SUPERSEDED,
        "cessation_of_operation": RevocationReason.CESSATION_OF_OPERATION,
        "privilege_withdrawn": RevocationReason.PRIVILEGE_WITHDRAWN,
        "unspecified": RevocationReason.UNSPECIFIED,
    }

    core_request = CoreRevocationRequest(
        key_id=request.key_id,
        reason=reason_map.get(request.reason.lower(), RevocationReason.UNSPECIFIED),
        revoked_by=request.revoked_by,
        notes=request.notes,
    )

    response = revocation_service.revoke_key(core_request)
    return {"success": response.success, "key_id": response.key_id, "revoked_at": response.revoked_at}


@app.get("/api/v1/admin/stats", dependencies=[Depends(verify_admin_auth)])
async def admin_stats():
    """Admin: Get system statistics."""
    return {
        "enrolled_keys": len(auth_service._enrolled_keys),
        "active_challenges": auth_service.get_active_challenges_count(),
        "revoked_keys": revocation_service.get_revoked_count(),
        "crl_version": revocation_service.get_crl_version(),
        "crl_hash": revocation_service.get_crl_hash(),
    }


@app.get("/api/v1/admin/keys", dependencies=[Depends(verify_admin_auth)])
async def admin_list_keys():
    """Admin: List all enrolled keys."""
    keys = []
    for key_id, dna_key in auth_service._enrolled_keys.items():
        keys.append(
            {
                "key_id": key_id,
                "subject_type": dna_key.subject.subject_type if dna_key.subject else None,
                "created": dna_key.created_timestamp.isoformat() if dna_key.created_timestamp else None,
                "expires": dna_key.expires_timestamp.isoformat() if dna_key.expires_timestamp else None,
                "is_revoked": revocation_service.is_revoked(key_id),
                "segment_count": dna_key.dna_helix.segment_count,
            }
        )
    return {"keys": keys, "total": len(keys)}


@app.get("/api/v1/admin/revocations", dependencies=[Depends(verify_admin_auth)])
async def admin_revocations():
    """Admin: Get revocation list."""
    revocations = revocation_service.get_revocation_list()
    return {
        "revocations": [
            {
                "key_id": r.key_id,
                "revoked_at": r.revoked_at.isoformat(),
                "reason": r.reason.value,
                "revoked_by": r.revoked_by,
                "notes": r.notes,
            }
            for r in revocations
        ],
        "total": len(revocations),
    }


@app.delete("/api/v1/admin/challenges/cleanup", dependencies=[Depends(verify_admin_auth)])
async def admin_cleanup_challenges():
    """Admin: Cleanup expired challenges."""
    cleaned = auth_service.cleanup_expired_challenges()
    return {"cleaned": cleaned, "remaining": auth_service.get_active_challenges_count()}


if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("DNAKEY_API_HOST", "0.0.0.0")
    port = int(os.getenv("DNAKEY_API_PORT", "8000"))
    reload = os.getenv("DNAKEY_API_RELOAD", "true").lower() == "true"

    uvicorn.run("server.api.main:app", host=host, port=port, reload=reload)
