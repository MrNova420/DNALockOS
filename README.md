<!--
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill (Operating as WeNova Interactive)

PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE
This is NOT free software. This is NOT open source. Commercial license required.
Unauthorized use is strictly prohibited.
-->

# 🔷 DNALockOS - DNA-Key Authentication System

A military-grade, passwordless authentication system using unique DNA-Key cryptographic identities.

---

## 📋 Requirements

### Python Version

| Version | Status | Notes |
|---------|--------|-------|
| **Python 3.11.x** | ✅ Recommended | Full support, all features |
| Python 3.10.x | ✅ Supported | Full support |
| Python 3.12.x | ⚠️ Experimental | May have issues with pydantic-core on some platforms |

**Recommended:** Use Python 3.11 for production deployments.

### System Requirements

- **CPU:** 1+ cores
- **RAM:** 512MB minimum, 2GB recommended
- **Storage:** 500MB for installation

---

## 🚀 Quick Start

### Standard Installation (Desktop/Server)

```bash
# Clone repository
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: .\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Start the server
./start_all.sh
# or: python -m server.api.main
```

### Mobile/Termux Installation

For Android/Termux environments where native compilation is limited:

```bash
# Install Termux build tools (recommended)
pkg update -y
pkg upgrade -y
pkg install -y python clang make pkg-config binutils

# Optional: Install libsodium for PyNaCl support
pkg install -y libsodium

# Clone and setup
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install mobile dependencies (excludes heavy native deps)
pip install --no-cache-dir -r requirements-mobile.txt

# Start the server
./start_all.sh
```

**Mobile Mode Features:**
- Uses `cryptography` library instead of PyNaCl (if not available)
- Uses default asyncio instead of uvloop
- ZMQ messaging disabled
- All core authentication features work

---

## 📦 Dependency Profiles

### Production (`requirements.txt`)

Full feature set for servers and CI:
- PyNaCl (libsodium)
- uvloop (fast event loop)
- Full testing suite
- Monitoring tools

```bash
pip install -r requirements.txt
```

### Mobile/Lite (`requirements-mobile.txt`)

Lightweight profile for Termux/Android:
- No native compilation required
- Automatic fallbacks for missing deps
- Core features preserved

```bash
pip install -r requirements-mobile.txt
```

---

## 🔐 Features

- **Passwordless Authentication** - DNA-Key based identity
- **Military-Grade Cryptography** - Ed25519, X25519, AES-256-GCM
- **Visual DNA Verification** - 3D helix visualization
- **Challenge-Response Protocol** - Secure authentication flow
- **Key Revocation** - Instant key invalidation
- **Platform Fallbacks** - Graceful degradation on constrained platforms

---

## 🌍 Universal Usages

The DNA-Key Authentication System can be used in **any authentication scenario**. See our [Complete Universal Usage Guide](README-UNIVERSAL-USAGES.md) for 30+ detailed scenarios including:

### Enterprise & Business
- Employee authentication
- Customer portals
- Multi-tenant SaaS
- SSO integration

### Security Applications
- Two-factor authentication
- Privileged access management
- Zero trust architecture

### Mobile & IoT
- Mobile app authentication
- IoT device authentication
- API authentication

### Web Applications
- Single sign-on (SSO)
- CMS integration (WordPress, Drupal)
- E-commerce checkout

### Healthcare & Government
- HIPAA-compliant records access
- Government services
- Military & defense systems

### Financial Services
- Banking transactions
- Cryptocurrency wallets
- Stock trading platforms

### Gaming & Entertainment
- Gaming platform authentication
- Streaming services
- Content protection

### Education
- Student authentication
- Online exam proctoring
- Campus access control

### Industrial & Manufacturing
- Equipment access control
- Supply chain verification
- Safety-critical systems

### Transportation
- Vehicle access and start
- Fleet management
- Public transport

### And Many More!
See the [full guide](README-UNIVERSAL-USAGES.md) for complete implementation examples, code samples, and integration patterns for each use case.

### Universal Integration

```python
# Works with ANY application
from server.core.enrollment import enroll_user
from server.crypto.dna_key import SecurityLevel

# 1. Enroll
response = enroll_user("user@anywhere.com", SecurityLevel.ENHANCED)

# 2. Authenticate
challenge = get_challenge(response.key_id)
signature = sign_challenge(challenge)
session = authenticate(challenge.id, signature)

# 3. Use in your application
if session.success:
    grant_access(user)
```

**Universal Benefits:**
- ✅ Passwordless
- ✅ Visual verification
- ✅ Military-grade security
- ✅ Instant revocation
- ✅ Complete audit trail
- ✅ Works anywhere

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/api/v1/status` | GET | Detailed API status |
| `/api/v1/enroll` | POST | Enroll new DNA key |
| `/api/v1/challenge` | POST | Get auth challenge |
| `/api/v1/authenticate` | POST | Authenticate with response |
| `/api/docs` | GET | Swagger API documentation |

---

## 📖 Documentation

- [Platform Start Guide](PLATFORM_START_GUIDE.md) - Detailed platform instructions
- [Quick Start Guide](QUICK_START_GUIDE.md) - Getting started quickly
- [DNA Architecture](DNA_ARCHITECTURE.md) - Technical architecture
- [Implementation Status](IMPLEMENTATION_STATUS.md) - Feature status

---

## ⚠️ Troubleshooting

### Common Issues

**PyNaCl installation fails on Termux:**
```bash
pkg install libsodium
pip install PyNaCl
```
Or use `requirements-mobile.txt` which doesn't require PyNaCl.

**pydantic-core build errors on Python 3.12:**
Use Python 3.11 for best compatibility, or the system will use available fallbacks.

**Port already in use:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
# Or use different port
DNAKEY_API_PORT=8080 ./start_all.sh
```

---

## 📜 License

**PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE**

Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill

This is NOT free software. This is NOT open source.
Commercial license required for any use.

