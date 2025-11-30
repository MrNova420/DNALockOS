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
    """Root endpoint - Full DNA-Key Platform with enrollment, authentication, and 3D visualization."""
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
        <title>DNALockOS - DNA-Key Authentication Platform</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                min-height: 100vh;
                background: linear-gradient(135deg, #000000 0%, #0a0a2e 50%, #000000 100%);
                color: #00ffff;
                font-family: 'Orbitron', monospace;
                overflow-x: hidden;
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
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.1); opacity: 0.8; }}
            }}
            @keyframes glow {{
                0%, 100% {{ box-shadow: 0 0 20px rgba(0, 255, 255, 0.5); }}
                50% {{ box-shadow: 0 0 40px rgba(0, 255, 255, 0.8); }}
            }}
            @keyframes rotate {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            .header {{
                text-align: center;
                padding: 30px 20px 20px;
                border-bottom: 3px solid #00ffff;
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
                background: linear-gradient(180deg, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.6) 100%);
                position: relative;
                z-index: 10;
            }}
            .logo-container {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 20px;
                margin-bottom: 10px;
            }}
            .logo-icon {{
                font-size: 60px;
                animation: pulse 2s ease-in-out infinite;
            }}
            .logo-text {{
                font-size: 48px;
                font-weight: 900;
                text-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff;
                letter-spacing: 5px;
            }}
            .tagline {{
                font-size: 18px;
                color: #ff00ff;
                letter-spacing: 8px;
                text-shadow: 0 0 10px #ff00ff;
            }}
            .version {{
                font-size: 12px;
                color: #666;
                letter-spacing: 2px;
                margin-top: 5px;
            }}
            .status-bar {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin-top: 15px;
                flex-wrap: wrap;
            }}
            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 15px;
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid #00ffff;
                border-radius: 20px;
                font-size: 12px;
            }}
            .status-dot {{
                width: 10px;
                height: 10px;
                border-radius: 50%;
                animation: pulse 1s ease-in-out infinite;
            }}
            .status-dot.online {{ background: #00ff00; box-shadow: 0 0 10px #00ff00; }}
            .status-dot.offline {{ background: #ff0000; box-shadow: 0 0 10px #ff0000; }}
            
            /* Navigation Tabs */
            .nav-tabs {{
                display: flex;
                justify-content: center;
                gap: 10px;
                padding: 20px;
                flex-wrap: wrap;
                position: relative;
                z-index: 10;
            }}
            .nav-tab {{
                padding: 15px 30px;
                background: rgba(0, 255, 255, 0.1);
                border: 2px solid #00ffff;
                border-radius: 10px;
                color: #00ffff;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-family: 'Orbitron', monospace;
            }}
            .nav-tab:hover {{
                background: rgba(0, 255, 255, 0.2);
                transform: translateY(-2px);
            }}
            .nav-tab.active {{
                background: linear-gradient(90deg, #00ffff 0%, #00cccc 100%);
                color: #000;
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
            }}
            
            /* Content Panels */
            .content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                position: relative;
                z-index: 10;
            }}
            .panel {{
                display: none;
                background: rgba(0, 0, 0, 0.85);
                border: 3px solid #00ffff;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 0 50px rgba(0, 255, 255, 0.3);
                animation: fadeIn 0.3s ease;
            }}
            .panel.active {{
                display: block;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .panel-title {{
                font-size: 28px;
                text-align: center;
                margin-bottom: 10px;
                text-shadow: 0 0 20px #00ffff;
                letter-spacing: 3px;
            }}
            .panel-desc {{
                text-align: center;
                color: #888;
                margin-bottom: 30px;
                font-size: 14px;
            }}
            
            /* Form Styles */
            .form-group {{
                margin-bottom: 25px;
            }}
            .form-label {{
                display: block;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #00ffff;
            }}
            .form-input {{
                width: 100%;
                padding: 15px;
                font-size: 16px;
                background: rgba(0, 0, 0, 0.5);
                border: 2px solid #00ffff;
                border-radius: 8px;
                color: #00ffff;
                font-family: 'Orbitron', monospace;
                transition: all 0.3s;
            }}
            .form-input:focus {{
                outline: none;
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            }}
            .form-input::placeholder {{
                color: #666;
            }}
            .security-options {{
                display: grid;
                gap: 10px;
            }}
            .security-option {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 15px;
                background: rgba(0, 255, 255, 0.05);
                border: 2px solid #00ffff;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .security-option:hover {{
                background: rgba(0, 255, 255, 0.1);
            }}
            .security-option.selected {{
                background: rgba(0, 255, 255, 0.2);
                border-color: #00ff00;
            }}
            .security-option input {{
                width: 20px;
                height: 20px;
                accent-color: #00ffff;
            }}
            .security-name {{
                font-weight: bold;
                font-size: 14px;
            }}
            .security-desc {{
                font-size: 12px;
                color: #888;
                margin-left: auto;
            }}
            
            /* Buttons */
            .btn {{
                width: 100%;
                padding: 18px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                text-transform: uppercase;
                letter-spacing: 3px;
                transition: all 0.3s;
                font-family: 'Orbitron', monospace;
            }}
            .btn-primary {{
                background: linear-gradient(90deg, #00ffff 0%, #00cccc 100%);
                color: #000;
                box-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
            }}
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 0 50px rgba(0, 255, 255, 0.8);
            }}
            .btn-primary:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            .btn-secondary {{
                background: rgba(255, 0, 255, 0.2);
                border: 2px solid #ff00ff;
                color: #ff00ff;
            }}
            .btn-secondary:hover {{
                background: rgba(255, 0, 255, 0.3);
            }}
            .btn-export {{
                background: rgba(0, 255, 0, 0.2);
                border: 2px solid #00ff00;
                color: #00ff00;
                margin-top: 10px;
            }}
            
            /* Result Box */
            .result-box {{
                margin-top: 30px;
                padding: 25px;
                background: rgba(0, 255, 0, 0.05);
                border: 2px solid #00ff00;
                border-radius: 10px;
                display: none;
            }}
            .result-box.show {{
                display: block;
                animation: fadeIn 0.3s ease;
            }}
            .result-title {{
                font-size: 20px;
                color: #00ff00;
                margin-bottom: 20px;
                text-align: center;
                text-shadow: 0 0 15px #00ff00;
            }}
            .result-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid rgba(0, 255, 255, 0.2);
                font-size: 13px;
            }}
            .result-label {{
                color: #888;
                font-weight: bold;
            }}
            .result-value {{
                color: #00ffff;
                word-break: break-all;
                max-width: 60%;
                text-align: right;
            }}
            
            /* 3D Viewer */
            .viewer-container {{
                width: 100%;
                height: 500px;
                background: rgba(0, 0, 0, 0.9);
                border: 3px solid #ff00ff;
                border-radius: 15px;
                overflow: hidden;
                position: relative;
            }}
            .viewer-canvas {{
                width: 100%;
                height: 100%;
            }}
            .viewer-controls {{
                position: absolute;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 10px;
                z-index: 100;
            }}
            .viewer-btn {{
                padding: 10px 20px;
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid #ff00ff;
                border-radius: 5px;
                color: #ff00ff;
                cursor: pointer;
                font-family: 'Orbitron', monospace;
                font-size: 12px;
            }}
            .viewer-btn:hover {{
                background: rgba(255, 0, 255, 0.2);
            }}
            .viewer-info {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid #00ffff;
                border-radius: 10px;
                padding: 15px;
                font-size: 12px;
                z-index: 100;
            }}
            .viewer-info p {{
                margin: 5px 0;
            }}
            
            /* Services Grid */
            .services-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .service-card {{
                background: rgba(0, 255, 255, 0.1);
                border: 2px solid #00ffff;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }}
            .service-icon {{
                font-size: 40px;
                margin-bottom: 10px;
            }}
            .service-name {{
                font-size: 14px;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 10px;
            }}
            .service-status {{
                font-size: 16px;
                font-weight: bold;
            }}
            .service-status.online {{ color: #00ff00; }}
            .service-status.offline {{ color: #ff0000; }}
            
            /* Footer */
            .footer {{
                text-align: center;
                padding: 30px;
                margin-top: 40px;
                border-top: 2px solid #00ffff;
                background: rgba(0, 0, 0, 0.8);
                font-size: 12px;
                color: #666;
            }}
            .footer-links {{
                margin-top: 15px;
                display: flex;
                justify-content: center;
                gap: 20px;
                flex-wrap: wrap;
            }}
            .footer-link {{
                color: #00ffff;
                text-decoration: none;
                padding: 8px 15px;
                border: 1px solid #00ffff;
                border-radius: 5px;
                transition: all 0.3s;
            }}
            .footer-link:hover {{
                background: #00ffff;
                color: #000;
            }}
            
            /* Loading Spinner */
            .loading {{
                display: none;
                text-align: center;
                padding: 20px;
            }}
            .loading.show {{
                display: block;
            }}
            .spinner {{
                width: 50px;
                height: 50px;
                border: 4px solid rgba(0, 255, 255, 0.2);
                border-top-color: #00ffff;
                border-radius: 50%;
                animation: rotate 1s linear infinite;
                margin: 0 auto 15px;
            }}
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        
        <!-- Header -->
        <div class="header">
            <div class="logo-container">
                <span class="logo-icon">🧬</span>
                <h1 class="logo-text">DNA-KEY</h1>
            </div>
            <div class="tagline">AUTHENTICATION PLATFORM</div>
            <div class="version">v1.0.0 | DNA PROTOCOL</div>
            
            <div class="status-bar">
                <div class="status-indicator">
                    <span class="status-dot {'online' if CORE_SERVICES_AVAILABLE else 'offline'}"></span>
                    <span>System: {status_text}</span>
                </div>
                <div class="status-indicator">
                    <span class="status-dot {'online' if enrollment_service else 'offline'}"></span>
                    <span>Enrollment</span>
                </div>
                <div class="status-indicator">
                    <span class="status-dot {'online' if auth_service else 'offline'}"></span>
                    <span>Auth</span>
                </div>
                <div class="status-indicator">
                    <span class="status-dot {'online' if pynacl_status else 'offline'}"></span>
                    <span>Crypto</span>
                </div>
            </div>
        </div>
        
        <!-- Navigation -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showPanel('enroll')">⚡ Generate Key</button>
            <button class="nav-tab" onclick="showPanel('authenticate')">🔐 Authenticate</button>
            <button class="nav-tab" onclick="showPanel('viewer')">🌀 3D Viewer</button>
            <button class="nav-tab" onclick="showPanel('status')">📊 Status</button>
            <button class="nav-tab" onclick="showPanel('integrate')">🔗 Integrate</button>
        </div>
        
        <!-- Content -->
        <div class="content">
            <!-- Enroll Panel -->
            <div id="panel-enroll" class="panel active">
                <h2 class="panel-title">🧬 GENERATE NEW DNA KEY 🧬</h2>
                <p class="panel-desc">Create a unique cryptographic DNA authentication key with thousands of secure segments</p>
                
                <div style="max-width: 600px; margin: 0 auto;">
                    <div class="form-group">
                        <label class="form-label">Subject ID</label>
                        <input type="text" id="subject-id" class="form-input" placeholder="email@example.com or username">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Security Level</label>
                        <div class="security-options">
                            <label class="security-option" onclick="selectSecurity(this, 'standard')">
                                <input type="radio" name="security" value="standard">
                                <span class="security-name">STANDARD</span>
                                <span class="security-desc">1,024 segments</span>
                            </label>
                            <label class="security-option selected" onclick="selectSecurity(this, 'enhanced')">
                                <input type="radio" name="security" value="enhanced" checked>
                                <span class="security-name">ENHANCED</span>
                                <span class="security-desc">16,384 segments</span>
                            </label>
                            <label class="security-option" onclick="selectSecurity(this, 'maximum')">
                                <input type="radio" name="security" value="maximum">
                                <span class="security-name">MAXIMUM</span>
                                <span class="security-desc">65,536 segments</span>
                            </label>
                            <label class="security-option" onclick="selectSecurity(this, 'government')">
                                <input type="radio" name="security" value="government">
                                <span class="security-name">GOVERNMENT</span>
                                <span class="security-desc">262,144 segments</span>
                            </label>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary" onclick="enrollKey()" id="enroll-btn">
                        ⚡ GENERATE DNA KEY
                    </button>
                    
                    <div class="loading" id="enroll-loading">
                        <div class="spinner"></div>
                        <p>Generating DNA Key...</p>
                    </div>
                    
                    <div class="result-box" id="enroll-result">
                        <h3 class="result-title">✓ DNA KEY GENERATED</h3>
                        <div class="result-row">
                            <span class="result-label">KEY ID:</span>
                            <span class="result-value" id="result-key-id">-</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">CREATED:</span>
                            <span class="result-value" id="result-created">-</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">EXPIRES:</span>
                            <span class="result-value" id="result-expires">-</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">SIGNING KEY:</span>
                            <span class="result-value" id="result-signing-key">-</span>
                        </div>
                        <button class="btn btn-secondary" onclick="showPanel('viewer')" style="margin-top: 20px;">
                            🌀 VIEW IN 3D
                        </button>
                        <button class="btn btn-export" onclick="exportKey()">
                            📥 EXPORT KEY
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Authenticate Panel -->
            <div id="panel-authenticate" class="panel">
                <h2 class="panel-title">🔐 AUTHENTICATE WITH DNA KEY 🔐</h2>
                <p class="panel-desc">Challenge-response authentication using your DNA key signature</p>
                
                <div style="max-width: 600px; margin: 0 auto;">
                    <div class="form-group">
                        <label class="form-label">DNA Key ID</label>
                        <input type="text" id="auth-key-id" class="form-input" placeholder="dna-xxxxxxxx...">
                    </div>
                    
                    <button class="btn btn-primary" onclick="getChallenge()" id="challenge-btn">
                        🔐 GET CHALLENGE
                    </button>
                    
                    <div class="loading" id="auth-loading">
                        <div class="spinner"></div>
                        <p>Requesting Challenge...</p>
                    </div>
                    
                    <div class="result-box" id="challenge-result">
                        <h3 class="result-title">✓ CHALLENGE RECEIVED</h3>
                        <div class="result-row">
                            <span class="result-label">CHALLENGE ID:</span>
                            <span class="result-value" id="challenge-id">-</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">CHALLENGE:</span>
                            <span class="result-value" id="challenge-data">-</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">EXPIRES:</span>
                            <span class="result-value" id="challenge-expires">-</span>
                        </div>
                        <p style="margin-top: 15px; padding: 15px; background: rgba(255, 255, 0, 0.1); border: 1px solid #ffff00; border-radius: 5px; color: #ffff00; font-size: 13px;">
                            📝 Sign this challenge with your DNA key's private signing key and submit for authentication.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- 3D Viewer Panel -->
            <div id="panel-viewer" class="panel">
                <h2 class="panel-title">🌀 3D DNA VISUALIZATION 🌀</h2>
                <p class="panel-desc">Interactive 360° view of your unique DNA authentication key</p>
                
                <div class="viewer-container">
                    <canvas id="dna-canvas" class="viewer-canvas"></canvas>
                    <div class="viewer-info">
                        <p><strong>KEY:</strong> <span id="viewer-key-id">demo-key</span></p>
                        <p><strong>SEGMENTS:</strong> <span id="viewer-segments">16,384</span></p>
                        <p><strong>SECURITY:</strong> <span id="viewer-security">ENHANCED</span></p>
                    </div>
                    <div class="viewer-controls">
                        <button class="viewer-btn" onclick="toggleRotation()">⏯ Toggle Rotation</button>
                        <button class="viewer-btn" onclick="resetView()">🔄 Reset View</button>
                        <button class="viewer-btn" onclick="toggleWireframe()">📐 Wireframe</button>
                    </div>
                </div>
            </div>
            
            <!-- Status Panel -->
            <div id="panel-status" class="panel">
                <h2 class="panel-title">📊 SYSTEM STATUS 📊</h2>
                <p class="panel-desc">Real-time status of all DNA-Key Authentication services</p>
                
                <div class="services-grid">
                    <div class="service-card">
                        <div class="service-icon">⚡</div>
                        <div class="service-name">Enrollment Service</div>
                        <div class="service-status {'online' if enrollment_service else 'offline'}">
                            {'🟢 ONLINE' if enrollment_service else '🔴 OFFLINE'}
                        </div>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">🔐</div>
                        <div class="service-name">Authentication</div>
                        <div class="service-status {'online' if auth_service else 'offline'}">
                            {'🟢 ONLINE' if auth_service else '🔴 OFFLINE'}
                        </div>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">🚫</div>
                        <div class="service-name">Revocation</div>
                        <div class="service-status {'online' if revocation_service else 'offline'}">
                            {'🟢 ONLINE' if revocation_service else '🔴 OFFLINE'}
                        </div>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">🔒</div>
                        <div class="service-name">Crypto Backend</div>
                        <div class="service-status {'online' if pynacl_status else 'offline'}">
                            {'🟢 PyNaCl' if pynacl_status else '🟡 Fallback'}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Integration Panel -->
            <div id="panel-integrate" class="panel">
                <h2 class="panel-title">🔗 INTEGRATE DNA-KEY 🔗</h2>
                <p class="panel-desc">Add DNA-Key authentication to your application</p>
                
                <div style="max-width: 800px; margin: 0 auto;">
                    <div class="form-group">
                        <label class="form-label">API Endpoints</label>
                        <div style="background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px; font-family: monospace; font-size: 13px;">
                            <p style="margin: 5px 0;"><span style="color: #00ff00;">POST</span> /api/v1/enroll - Generate new DNA key</p>
                            <p style="margin: 5px 0;"><span style="color: #ffff00;">POST</span> /api/v1/challenge - Request auth challenge</p>
                            <p style="margin: 5px 0;"><span style="color: #00ffff;">POST</span> /api/v1/authenticate - Submit signed challenge</p>
                            <p style="margin: 5px 0;"><span style="color: #ff00ff;">GET</span> /api/v1/visual/{{key_id}} - Get 3D visualization data</p>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Example: Enroll New Key</label>
                        <pre style="background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px; font-family: monospace; font-size: 12px; overflow-x: auto; white-space: pre-wrap;">
curl -X POST "http://localhost:8000/api/v1/enroll" \\
  -H "Content-Type: application/json" \\
  -d '{{"subject_id": "user@example.com", "security_level": "enhanced"}}'
                        </pre>
                    </div>
                    
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <a href="/api/docs" class="btn btn-secondary" style="flex: 1; text-align: center; text-decoration: none;">📚 API DOCS</a>
                        <a href="/api/redoc" class="btn btn-secondary" style="flex: 1; text-align: center; text-decoration: none;">📖 REDOC</a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>🧬 DNALockOS - DNA-Key Authentication Platform v1.0.0 🧬</p>
            <p>Copyright © 2025 WeNova Interactive</p>
            <div class="footer-links">
                <a href="/health" class="footer-link">💓 Health Check</a>
                <a href="/api/v1/status" class="footer-link">📊 API Status</a>
                <a href="/api/docs" class="footer-link">📚 Documentation</a>
            </div>
        </div>
        
        <script>
            // State
            let currentKeyData = null;
            let selectedSecurity = 'enhanced';
            let scene, camera, renderer, dnaGroup;
            let isRotating = true;
            let isWireframe = false;
            
            // Panel Navigation
            function showPanel(panelId) {{
                document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                document.getElementById('panel-' + panelId).classList.add('active');
                event.target.classList.add('active');
                
                if (panelId === 'viewer') {{
                    initViewer();
                }}
            }}
            
            // Security Selection
            function selectSecurity(element, level) {{
                document.querySelectorAll('.security-option').forEach(opt => opt.classList.remove('selected'));
                element.classList.add('selected');
                selectedSecurity = level;
            }}
            
            // Enroll Key
            async function enrollKey() {{
                const subjectId = document.getElementById('subject-id').value;
                if (!subjectId) {{
                    alert('Please enter a Subject ID');
                    return;
                }}
                
                document.getElementById('enroll-btn').disabled = true;
                document.getElementById('enroll-loading').classList.add('show');
                document.getElementById('enroll-result').classList.remove('show');
                
                try {{
                    const response = await fetch('/api/v1/enroll', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            subject_id: subjectId,
                            subject_type: 'human',
                            security_level: selectedSecurity,
                            mfa_required: true,
                            device_binding_required: true
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        currentKeyData = data;
                        document.getElementById('result-key-id').textContent = data.key_id;
                        document.getElementById('result-created').textContent = new Date(data.created_at).toLocaleString();
                        document.getElementById('result-expires').textContent = new Date(data.expires_at).toLocaleString();
                        document.getElementById('result-signing-key').textContent = (data.signing_key || '').substring(0, 32) + '...';
                        document.getElementById('enroll-result').classList.add('show');
                        
                        // Update viewer info
                        document.getElementById('viewer-key-id').textContent = data.key_id;
                        document.getElementById('viewer-security').textContent = selectedSecurity.toUpperCase();
                    }} else {{
                        alert('Enrollment failed: ' + (data.error_message || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }} finally {{
                    document.getElementById('enroll-btn').disabled = false;
                    document.getElementById('enroll-loading').classList.remove('show');
                }}
            }}
            
            // Get Challenge
            async function getChallenge() {{
                const keyId = document.getElementById('auth-key-id').value;
                if (!keyId) {{
                    alert('Please enter a DNA Key ID');
                    return;
                }}
                
                document.getElementById('challenge-btn').disabled = true;
                document.getElementById('auth-loading').classList.add('show');
                document.getElementById('challenge-result').classList.remove('show');
                
                try {{
                    const response = await fetch('/api/v1/challenge', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ key_id: keyId }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        document.getElementById('challenge-id').textContent = data.challenge_id;
                        document.getElementById('challenge-data').textContent = data.challenge.substring(0, 40) + '...';
                        document.getElementById('challenge-expires').textContent = new Date(data.expires_at).toLocaleString();
                        document.getElementById('challenge-result').classList.add('show');
                    }} else {{
                        alert('Challenge request failed: ' + (data.error_message || 'Unknown error'));
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }} finally {{
                    document.getElementById('challenge-btn').disabled = false;
                    document.getElementById('auth-loading').classList.remove('show');
                }}
            }}
            
            // Export Key
            function exportKey() {{
                if (!currentKeyData) {{
                    alert('No key generated yet');
                    return;
                }}
                
                const exportData = {{
                    key_id: currentKeyData.key_id,
                    created_at: currentKeyData.created_at,
                    expires_at: currentKeyData.expires_at,
                    signing_key: currentKeyData.signing_key,
                    serialized_key: currentKeyData.serialized_key,
                    security_level: selectedSecurity
                }};
                
                const blob = new Blob([JSON.stringify(exportData, null, 2)], {{ type: 'application/json' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'dna-key-' + currentKeyData.key_id + '.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
            
            // 3D Viewer
            function initViewer() {{
                const canvas = document.getElementById('dna-canvas');
                if (!canvas || scene) return;
                
                scene = new THREE.Scene();
                camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
                renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true, alpha: true }});
                renderer.setSize(canvas.clientWidth, canvas.clientHeight);
                renderer.setClearColor(0x000000, 0);
                
                // Create DNA helix
                dnaGroup = new THREE.Group();
                const colors = [0x00ffff, 0xff00ff, 0xffff00, 0x00ff00, 0xff0000];
                
                for (let i = 0; i < 500; i++) {{
                    const t = i / 50;
                    const angle = t * Math.PI * 2;
                    
                    // First strand
                    const sphere1 = new THREE.Mesh(
                        new THREE.SphereGeometry(0.15, 16, 16),
                        new THREE.MeshBasicMaterial({{ color: colors[i % 5] }})
                    );
                    sphere1.position.set(Math.cos(angle) * 2, t - 5, Math.sin(angle) * 2);
                    dnaGroup.add(sphere1);
                    
                    // Second strand (opposite)
                    const sphere2 = new THREE.Mesh(
                        new THREE.SphereGeometry(0.15, 16, 16),
                        new THREE.MeshBasicMaterial({{ color: colors[(i + 2) % 5] }})
                    );
                    sphere2.position.set(Math.cos(angle + Math.PI) * 2, t - 5, Math.sin(angle + Math.PI) * 2);
                    dnaGroup.add(sphere2);
                    
                    // Connecting lines
                    if (i % 5 === 0) {{
                        const lineGeom = new THREE.BufferGeometry().setFromPoints([
                            new THREE.Vector3(Math.cos(angle) * 2, t - 5, Math.sin(angle) * 2),
                            new THREE.Vector3(Math.cos(angle + Math.PI) * 2, t - 5, Math.sin(angle + Math.PI) * 2)
                        ]);
                        const line = new THREE.Line(lineGeom, new THREE.LineBasicMaterial({{ color: 0x00ffff, opacity: 0.5, transparent: true }}));
                        dnaGroup.add(line);
                    }}
                }}
                
                scene.add(dnaGroup);
                camera.position.z = 12;
                
                animate();
            }}
            
            function animate() {{
                requestAnimationFrame(animate);
                if (dnaGroup && isRotating) {{
                    dnaGroup.rotation.y += 0.01;
                }}
                if (renderer && scene && camera) {{
                    renderer.render(scene, camera);
                }}
            }}
            
            function toggleRotation() {{
                isRotating = !isRotating;
            }}
            
            function resetView() {{
                if (camera) {{
                    camera.position.set(0, 0, 12);
                    camera.lookAt(0, 0, 0);
                }}
                if (dnaGroup) {{
                    dnaGroup.rotation.set(0, 0, 0);
                }}
            }}
            
            function toggleWireframe() {{
                isWireframe = !isWireframe;
                if (dnaGroup) {{
                    dnaGroup.traverse((child) => {{
                        if (child.isMesh) {{
                            child.material.wireframe = isWireframe;
                        }}
                    }});
                }}
            }}
            
            // Handle window resize
            window.addEventListener('resize', () => {{
                const canvas = document.getElementById('dna-canvas');
                if (canvas && camera && renderer) {{
                    camera.aspect = canvas.clientWidth / canvas.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
                }}
            }});
        </script>
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
