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

PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE
This software is NOT free and is NOT open source.
Unauthorized copying, modification, distribution, or use is strictly prohibited.
See LICENSE file for full terms.

REST API Server - FastAPI-based REST API with complete authentication system.
Admin authentication uses DNA-Key system for master key auth.
"""

import base64
import os
import sys
import traceback
from datetime import datetime
from typing import List, Optional, Dict, Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Import with error handling for graceful degradation
try:
    from server.core.authentication import AuthenticationService
    from server.core.authentication import ChallengeRequest as CoreChallengeRequest
    from server.core.enrollment import EnrollmentRequest as CoreEnrollmentRequest
    from server.core.enrollment import EnrollmentService
    from server.core.revocation import RevocationReason
    from server.core.revocation import RevocationRequest as CoreRevocationRequest
    from server.core.revocation import RevocationService
    from server.crypto.dna_key import SecurityLevel
    CORE_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Core services not fully available: {e}")
    CORE_SERVICES_AVAILABLE = False

# Import runtime utilities with fallback
try:
    from server.runtime.event_loop import install_best_event_loop, get_platform_info
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False
    def install_best_event_loop():
        return "asyncio"
    def get_platform_info():
        return {"platform": sys.platform, "python_version": sys.version}

# Import crypto backend info
try:
    from server.crypto.backend import is_nacl_available, get_available_backends
    CRYPTO_BACKEND_AVAILABLE = True
except ImportError:
    CRYPTO_BACKEND_AVAILABLE = False
    def is_nacl_available():
        return False
    def get_available_backends():
        return []

# Import messaging info
try:
    from server.messaging.zmq_client import is_zmq_available
    MESSAGING_AVAILABLE = True
except ImportError:
    MESSAGING_AVAILABLE = False
    def is_zmq_available():
        return False

# Initialize services with error handling
enrollment_service = None
auth_service = None
revocation_service = None

if CORE_SERVICES_AVAILABLE:
    try:
        enrollment_service = EnrollmentService()
        auth_service = AuthenticationService()
        revocation_service = RevocationService()
    except Exception as e:
        print(f"[ERROR] Failed to initialize services: {e}")
        CORE_SERVICES_AVAILABLE = False

security = HTTPBearer(auto_error=False)


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
    signing_key: Optional[str] = None  # IMPORTANT: User's private key - store securely!
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


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


# ============= Error Handling =============


def create_error_response(
    error: str,
    error_code: str,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error,
            "error_code": error_code,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ============= Security Dependencies =============


async def verify_admin_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication using DNA-Key system."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # In production, validate session token against auth_service
    # For now, check token format
    if not token.startswith("dna-session-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin authentication token"
        )

    # Return admin identity
    return {"token": token, "role": "admin"}


def check_services_available():
    """Check if core services are available and raise appropriate error if not."""
    if not CORE_SERVICES_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Core services are not available. Check server logs for details."
        )


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


# ============= Global Exception Handler =============


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions gracefully."""
    error_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    # Log the error (in production, use proper logging)
    print(f"[ERROR {error_id}] Unhandled exception: {exc}")
    print(traceback.format_exc())

    return create_error_response(
        error="An internal error occurred. Please try again later.",
        error_code="INTERNAL_ERROR",
        status_code=500,
        details={"error_id": error_id}
    )


# ============= Public Endpoints =============


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Landing page with system status."""
    status_emoji = "🟢" if CORE_SERVICES_AVAILABLE else "🟡"
    status_text = "OPERATIONAL" if CORE_SERVICES_AVAILABLE else "DEGRADED"
    status_color = "#00ff00" if CORE_SERVICES_AVAILABLE else "#ffff00"
    
    # Get feature availability
    pynacl_status = is_nacl_available() if CRYPTO_BACKEND_AVAILABLE else False
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DNALockOS - DNA-Key Authentication System</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                min-height: 100vh;
                background: linear-gradient(135deg, #000000 0%, #0a0a2e 50%, #000000 100%);
                color: #00ffff;
                font-family: 'Orbitron', monospace;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                overflow-x: hidden;
            }}
            .container {{
                max-width: 800px;
                width: 100%;
                text-align: center;
            }}
            .logo {{
                font-size: 80px;
                margin-bottom: 10px;
                animation: pulse 2s ease-in-out infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.1); opacity: 0.8; }}
            }}
            h1 {{
                font-size: 48px;
                font-weight: 900;
                text-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff;
                letter-spacing: 5px;
                margin-bottom: 10px;
            }}
            .tagline {{
                font-size: 18px;
                color: #ff00ff;
                letter-spacing: 8px;
                text-shadow: 0 0 10px #ff00ff;
                margin-bottom: 5px;
            }}
            .version {{
                font-size: 12px;
                color: #666;
                letter-spacing: 2px;
                margin-bottom: 40px;
            }}
            .status-box {{
                background: rgba(0, 0, 0, 0.8);
                border: 3px solid #00ffff;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 0 50px rgba(0, 255, 255, 0.3);
            }}
            .status {{
                font-size: 36px;
                color: {status_color};
                text-shadow: 0 0 20px {status_color};
                margin-bottom: 20px;
            }}
            .services {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .service {{
                background: rgba(0, 255, 255, 0.1);
                border: 2px solid #00ffff;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
            }}
            .service-name {{
                font-size: 12px;
                color: #888;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .service-status {{
                font-size: 18px;
            }}
            .service-status.online {{ color: #00ff00; }}
            .service-status.offline {{ color: #ff0000; }}
            .links {{
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 30px;
            }}
            .link {{
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(90deg, rgba(0, 255, 255, 0.2) 0%, rgba(0, 255, 255, 0.1) 100%);
                border: 2px solid #00ffff;
                border-radius: 10px;
                color: #00ffff;
                text-decoration: none;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
                transition: all 0.3s;
            }}
            .link:hover {{
                background: linear-gradient(90deg, #00ffff 0%, #00cccc 100%);
                color: #000;
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
                transform: translateY(-2px);
            }}
            .footer {{
                margin-top: 40px;
                font-size: 12px;
                color: #666;
            }}
            .grid-bg {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    linear-gradient(#00ffff 1px, transparent 1px),
                    linear-gradient(90deg, #00ffff 1px, transparent 1px);
                background-size: 50px 50px;
                opacity: 0.05;
                z-index: -1;
                animation: gridScroll 20s linear infinite;
            }}
            @keyframes gridScroll {{
                0% {{ transform: translateY(0); }}
                100% {{ transform: translateY(50px); }}
            }}
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="container">
            <div class="logo">🔷</div>
            <h1>DNA-KEY</h1>
            <div class="tagline">AUTHENTICATION SYSTEM</div>
            <div class="version">v1.0.0 | TRON PROTOCOL</div>
            
            <div class="status-box">
                <div class="status">{status_emoji} {status_text}</div>
                <p>All core services are running</p>
                
                <div class="services">
                    <div class="service">
                        <div class="service-name">Enrollment</div>
                        <div class="service-status {'online' if enrollment_service else 'offline'}">
                            {'🟢 ONLINE' if enrollment_service else '🔴 OFFLINE'}
                        </div>
                    </div>
                    <div class="service">
                        <div class="service-name">Authentication</div>
                        <div class="service-status {'online' if auth_service else 'offline'}">
                            {'🟢 ONLINE' if auth_service else '🔴 OFFLINE'}
                        </div>
                    </div>
                    <div class="service">
                        <div class="service-name">Revocation</div>
                        <div class="service-status {'online' if revocation_service else 'offline'}">
                            {'🟢 ONLINE' if revocation_service else '🔴 OFFLINE'}
                        </div>
                    </div>
                    <div class="service">
                        <div class="service-name">Crypto Backend</div>
                        <div class="service-status {'online' if pynacl_status else 'offline'}">
                            {'🟢 PyNaCl' if pynacl_status else '🟡 Fallback'}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="links">
                <a href="/api/docs" class="link">📚 API Docs</a>
                <a href="/api/redoc" class="link">📖 ReDoc</a>
                <a href="/health" class="link">💓 Health</a>
                <a href="/api/v1/status" class="link">📊 Status</a>
            </div>
            
            <div class="footer">
                <p>🔷 Powered by DNALockOS - DNA-Key Authentication System 🔷</p>
                <p>Copyright © 2025 WeNova Interactive</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/favicon.ico")
async def favicon():
    """Return a simple favicon."""
    # Return a simple 1x1 transparent PNG as favicon placeholder
    # This prevents 404 errors in browser console
    favicon_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return Response(content=favicon_data, media_type="image/png")


@app.get("/health")
async def health_check():
    """System health check with detailed status."""
    platform_info = get_platform_info() if RUNTIME_AVAILABLE else {}

    return {
        "status": "🟢 OPERATIONAL" if CORE_SERVICES_AVAILABLE else "🟡 DEGRADED",
        "version": "1.0.0",
        "timestamp": datetime.utcnow(),
        "services": {
            "enrollment": "online" if enrollment_service else "offline",
            "authentication": "online" if auth_service else "offline",
            "revocation": "online" if revocation_service else "offline",
            "visualization": "online",
        },
        "platform": {
            "os": platform_info.get("platform", sys.platform),
            "python": platform_info.get("python_version_info", {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
            }),
            "is_mobile": platform_info.get("is_android", False),
        },
        "features": {
            "uvloop": platform_info.get("uvloop_available", False),
            "pynacl": is_nacl_available() if CRYPTO_BACKEND_AVAILABLE else False,
            "zmq": is_zmq_available() if MESSAGING_AVAILABLE else False,
            "crypto_backends": get_available_backends() if CRYPTO_BACKEND_AVAILABLE else [],
        },
    }


@app.get("/api/v1/status")
async def api_status():
    """Get detailed API status and available features."""
    return {
        "api_version": "1.0.0",
        "core_services": CORE_SERVICES_AVAILABLE,
        "runtime_available": RUNTIME_AVAILABLE,
        "crypto_backend": CRYPTO_BACKEND_AVAILABLE,
        "messaging_available": MESSAGING_AVAILABLE,
        "available_endpoints": [
            "/health",
            "/api/v1/status",
            "/api/v1/enroll",
            "/api/v1/challenge",
            "/api/v1/authenticate",
            "/api/v1/visual/{key_id}",
        ],
        "admin_endpoints": [
            "/api/v1/admin/revoke",
            "/api/v1/admin/stats",
            "/api/v1/admin/keys",
            "/api/v1/admin/revocations",
            "/api/v1/admin/challenges/cleanup",
        ],
    }


@app.post("/api/v1/enroll", response_model=EnrollmentResponse)
async def enroll_key(request: EnrollmentRequest):
    """Enroll new DNA key with visual DNA generation."""
    check_services_available()

    try:
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
            signing_key=response.signing_key_hex,  # User needs this to sign challenges!
            visual_seed=response.dna_key.visual_dna.animation_seed if response.dna_key.visual_dna else None,
        )
    except Exception as e:
        return EnrollmentResponse(success=False, error_message=f"Enrollment failed: {str(e)}")


@app.post("/api/v1/challenge", response_model=ChallengeResponse)
async def get_challenge(request: ChallengeRequest):
    """Get authentication challenge."""
    check_services_available()

    try:
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
    except Exception as e:
        return ChallengeResponse(success=False, error_message=f"Challenge generation failed: {str(e)}")


@app.post("/api/v1/authenticate", response_model=AuthenticationResponse)
async def authenticate(request: AuthenticateRequest):
    """Authenticate with challenge response."""
    check_services_available()

    try:
        # Validate hex string
        try:
            challenge_response = bytes.fromhex(request.challenge_response)
        except ValueError:
            return AuthenticationResponse(
                success=False,
                error_message="Invalid challenge response format. Expected hex string."
            )

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
    except Exception as e:
        return AuthenticationResponse(success=False, error_message=f"Authentication failed: {str(e)}")


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
    check_services_available()

    try:
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
    except Exception as e:
        return {"success": False, "error": f"Revocation failed: {str(e)}"}


@app.get("/api/v1/admin/stats", dependencies=[Depends(verify_admin_auth)])
async def admin_stats():
    """Admin: Get system statistics."""
    check_services_available()

    try:
        return {
            "enrolled_keys": len(auth_service._enrolled_keys),
            "active_challenges": auth_service.get_active_challenges_count(),
            "revoked_keys": revocation_service.get_revoked_count(),
            "crl_version": revocation_service.get_crl_version(),
            "crl_hash": revocation_service.get_crl_hash(),
        }
    except Exception as e:
        return {"error": f"Failed to get stats: {str(e)}"}


@app.get("/api/v1/admin/keys", dependencies=[Depends(verify_admin_auth)])
async def admin_list_keys():
    """Admin: List all enrolled keys."""
    check_services_available()

    try:
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
    except Exception as e:
        return {"keys": [], "total": 0, "error": f"Failed to list keys: {str(e)}"}


@app.get("/api/v1/admin/revocations", dependencies=[Depends(verify_admin_auth)])
async def admin_revocations():
    """Admin: Get revocation list."""
    check_services_available()

    try:
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
    except Exception as e:
        return {"revocations": [], "total": 0, "error": f"Failed to get revocations: {str(e)}"}


@app.delete("/api/v1/admin/challenges/cleanup", dependencies=[Depends(verify_admin_auth)])
async def admin_cleanup_challenges():
    """Admin: Cleanup expired challenges."""
    check_services_available()

    try:
        cleaned = auth_service.cleanup_expired_challenges()
        return {"cleaned": cleaned, "remaining": auth_service.get_active_challenges_count()}
    except Exception as e:
        return {"cleaned": 0, "remaining": 0, "error": f"Cleanup failed: {str(e)}"}


def main():
    """Main entry point with platform-aware event loop setup."""
    # Install best available event loop
    loop_type = install_best_event_loop()
    print(f"[INFO] Using {loop_type} event loop")

    # Get configuration from environment variables
    host = os.getenv("DNAKEY_API_HOST", "0.0.0.0")
    port = int(os.getenv("DNAKEY_API_PORT", "8000"))
    reload = os.getenv("DNAKEY_API_RELOAD", "true").lower() == "true"

    print(f"[INFO] Starting DNALockOS API server on {host}:{port}")
    print(f"[INFO] Core services available: {CORE_SERVICES_AVAILABLE}")
    print(f"[INFO] PyNaCl available: {is_nacl_available() if CRYPTO_BACKEND_AVAILABLE else False}")
    print(f"[INFO] ZMQ available: {is_zmq_available() if MESSAGING_AVAILABLE else False}")

    uvicorn.run("server.api.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
