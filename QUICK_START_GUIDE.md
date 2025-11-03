# DNA-KEY AUTHENTICATION SYSTEM
## QUICK START GUIDE FOR DEVELOPERS

**Version:** 1.0  
**Audience:** Developers building the system autonomously

---

## 🚀 GETTING STARTED

This guide will help you begin implementing the DNA-Key Authentication System based on the comprehensive blueprint.

---

## STEP 1: UNDERSTAND THE ARCHITECTURE

### Core Concept
The DNA-Key is a **biologically-inspired digital authentication key** where:
- Each key is a structured "DNA strand" with thousands of segments
- Each segment contains specific authentication data (entropy, policies, identity)
- The key is both cryptographically secure AND visually stunning
- Works universally across any platform

### Key Innovation
Instead of traditional username/password or even typical public-key auth, users have a **unique digital DNA** that:
1. Cannot be guessed or brute-forced
2. Is beautiful and engaging (Tron-like visualization)
3. Can authenticate anywhere (web, mobile, IoT, government systems)
4. Contains all policy and permission data within itself

---

## STEP 2: SET UP YOUR DEVELOPMENT ENVIRONMENT

### Prerequisites
```bash
# Required Software
- Node.js 18+ (for JavaScript SDK and web interface)
- Python 3.10+ (for server-side implementation)
- Docker & Docker Compose (for local services)
- PostgreSQL 14+ (for data storage)
- Redis 7+ (for caching and revocation)
- Git (for version control)

# Recommended Tools
- VS Code or JetBrains IDE
- Postman or Insomnia (API testing)
- pgAdmin or DBeaver (database management)
```

### Initial Setup
```bash
# 1. Clone the repository
git clone https://github.com/your-org/dnalock-auth.git
cd dnalock-auth

# 2. Install dependencies
npm install          # For JavaScript/TypeScript
pip install -r requirements.txt  # For Python

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 4. Start local services
docker-compose up -d

# 5. Run database migrations
npm run migrate
# or
python manage.py migrate

# 6. Seed initial data
npm run seed
# or
python manage.py seed
```

---

## STEP 3: UNDERSTAND THE DNA KEY FORMAT

### JSON Structure (Simplified)
```json
{
  "key_id": "dna-550e8400-e29b-41d4-a716-446655440000",
  "created": "2025-11-03T22:37:51.631Z",
  "expires": "2030-11-03T22:37:51.631Z",
  
  "dna_helix": {
    "segments": [
      {
        "position": 0,
        "type": "E",  // Entropy
        "data": "base64url_random_32bytes"
      },
      {
        "position": 1,
        "type": "P",  // Policy
        "data": "base64url_policy_data"
      }
      // ... thousands more segments
    ]
  },
  
  "public_key": "base64url_ed25519_public_key",
  "issuer_signature": "base64url_signature"
}
```

### Segment Types
- **E (Entropy):** Random cryptographic data
- **P (Policy):** Access control rules
- **H (Hash):** Identity commitments
- **T (Temporal):** Timestamps and validity
- **C (Capability):** Permissions and scopes
- **S (Signature):** Cryptographic proofs
- **M (Metadata):** Non-sensitive context
- **B (Biometric):** Biometric anchors
- **G (Geo):** Location policies
- **R (Revocation):** Revocation tokens

---

## STEP 4: IMPLEMENT CORE CRYPTOGRAPHY

### 1. Key Generation

```python
# Python example
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder
import os

def generate_dna_key():
    # Generate Ed25519 key pair
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    
    # Build DNA segments
    segments = []
    
    # Add entropy segments (40% of total)
    for i in range(400):
        segments.append({
            'position': i,
            'type': 'E',
            'data': base64url_encode(os.urandom(32))
        })
    
    # Add policy segments (10%)
    policy_data = encode_policy(load_policy('standard'))
    segments.append({
        'position': 400,
        'type': 'P',
        'data': base64url_encode(policy_data)
    })
    
    # ... add other segment types
    
    # Create DNA key structure
    dna_key = {
        'key_id': str(uuid.uuid4()),
        'created': datetime.now().isoformat(),
        'dna_helix': {'segments': segments},
        'public_key': verify_key.encode(encoder=Base64Encoder).decode(),
    }
    
    # Sign with issuer key
    dna_key['issuer_signature'] = sign_dna_key(dna_key, issuer_private_key)
    
    return {
        'dna_key': dna_key,
        'private_key': signing_key.encode(encoder=Base64Encoder).decode()
    }
```

### 2. Challenge-Response Authentication

```python
# Server side: Generate challenge
def generate_challenge(key_id):
    nonce = os.urandom(32)
    challenge = {
        'challenge_id': str(uuid.uuid4()),
        'key_id': key_id,
        'nonce': base64url_encode(nonce),
        'timestamp': datetime.now().isoformat(),
        'ttl': 60
    }
    
    # Store in cache with TTL
    redis.setex(
        f"challenge:{challenge['challenge_id']}",
        60,
        json.dumps(challenge)
    )
    
    return challenge

# Client side: Sign challenge
def sign_challenge(challenge, private_key):
    signing_key = SigningKey(private_key, encoder=Base64Encoder)
    
    # Construct message
    message = canonical_encode({
        'challenge_id': challenge['challenge_id'],
        'nonce': challenge['nonce'],
        'timestamp': challenge['timestamp']
    })
    
    # Sign
    signature = signing_key.sign(message)
    
    return base64url_encode(signature.signature)

# Server side: Verify signature
def verify_authentication(challenge_id, signature, dna_key):
    # Load challenge
    challenge = json.loads(redis.get(f"challenge:{challenge_id}"))
    
    # Construct expected message
    message = canonical_encode({
        'challenge_id': challenge['challenge_id'],
        'nonce': challenge['nonce'],
        'timestamp': challenge['timestamp']
    })
    
    # Verify signature
    verify_key = VerifyKey(dna_key['public_key'], encoder=Base64Encoder)
    
    try:
        verify_key.verify(message, base64url_decode(signature))
        return True
    except:
        return False
```

---

## STEP 5: BUILD THE API

### API Endpoints to Implement

```
POST   /api/v1/enrollment/request       # Request enrollment token
POST   /api/v1/enrollment/create        # Create DNA key
GET    /api/v1/enrollment/:key_id       # Get key metadata

POST   /api/v1/auth/start                # Start authentication
POST   /api/v1/auth/complete             # Complete authentication
POST   /api/v1/auth/refresh              # Refresh token
POST   /api/v1/auth/logout               # Logout

POST   /api/v1/revocation/revoke         # Revoke key
GET    /api/v1/revocation/:key_id        # Check revocation status
GET    /api/v1/revocation/checkpoint     # Get revocation checkpoint

GET    /api/v1/policy/:policy_id         # Get policy
POST   /api/v1/policy                    # Create policy (admin)

GET    /api/v1/visual/:key_id            # Get visual DNA
POST   /api/v1/visual/:key_id/generate   # Generate visual
```

### Express.js API Example

```javascript
const express = require('express');
const app = express();

// Enrollment endpoint
app.post('/api/v1/enrollment/request', async (req, res) => {
  try {
    const { user_id, policy_id, device_info } = req.body;
    
    // Validate input
    if (!user_id || !policy_id) {
      return res.status(400).json({
        success: false,
        errors: [{ code: 'INVALID_INPUT', message: 'Missing required fields' }]
      });
    }
    
    // Generate enrollment token
    const enrollmentToken = await enrollmentService.requestEnrollment({
      user_id,
      policy_id,
      device_info
    });
    
    res.json({
      success: true,
      data: enrollmentToken
    });
  } catch (error) {
    console.error('Enrollment request failed:', error);
    res.status(500).json({
      success: false,
      errors: [{ code: 'INTERNAL_ERROR', message: error.message }]
    });
  }
});

// Authentication start endpoint
app.post('/api/v1/auth/start', async (req, res) => {
  try {
    const { key_id, context } = req.body;
    
    // Check rate limiting
    if (await rateLimiter.isLimited(key_id)) {
      return res.status(429).json({
        success: false,
        errors: [{ code: 'RATE_LIMIT_EXCEEDED', message: 'Too many attempts' }]
      });
    }
    
    // Generate challenge
    const challenge = await authService.startAuthentication({
      key_id,
      context
    });
    
    res.json({
      success: true,
      data: challenge
    });
  } catch (error) {
    console.error('Auth start failed:', error);
    res.status(500).json({
      success: false,
      errors: [{ code: 'INTERNAL_ERROR', message: error.message }]
    });
  }
});
```

---

## STEP 6: CREATE THE WEB INTERFACE

### Simple HTML/JavaScript Demo

```html
<!DOCTYPE html>
<html>
<head>
  <title>DNA-Key Authentication</title>
  <style>
    body {
      background: #000;
      color: #0ff;
      font-family: 'Courier New', monospace;
    }
    
    #dna-visual {
      width: 800px;
      height: 600px;
      margin: 20px auto;
      border: 2px solid #0ff;
    }
    
    .button {
      background: #0ff;
      color: #000;
      padding: 10px 20px;
      border: none;
      cursor: pointer;
      font-size: 16px;
    }
  </style>
</head>
<body>
  <h1>DNA-Key Authentication Demo</h1>
  
  <div>
    <button class="button" onclick="enrollUser()">Enroll New User</button>
    <button class="button" onclick="authenticate()">Authenticate</button>
  </div>
  
  <div id="dna-visual"></div>
  
  <div id="status"></div>
  
  <script src="https://cdn.jsdelivr.net/npm/@dnalock/auth-sdk/dist/dna-auth.min.js"></script>
  <script>
    const dnaAuth = new DNAAuthClient({
      apiBaseUrl: 'http://localhost:3000/api/v1',
      clientId: 'demo-app'
    });
    
    async function enrollUser() {
      try {
        document.getElementById('status').innerText = 'Enrolling...';
        
        // Request enrollment
        const enrollment = await dnaAuth.enrollment.request({
          userId: 'demo-user-' + Date.now(),
          policyId: 'standard-policy',
          deviceInfo: await dnaAuth.device.getFingerprint()
        });
        
        // Create DNA key
        const dnaKey = await dnaAuth.enrollment.create({
          enrollmentToken: enrollment.enrollmentToken
        });
        
        // Store key ID
        localStorage.setItem('dna_key_id', dnaKey.keyId);
        localStorage.setItem('dna_private_key', dnaKey.privateKey);
        
        // Display visual DNA
        await dnaAuth.visual.display(dnaKey.keyId, {
          container: document.getElementById('dna-visual'),
          animated: true
        });
        
        document.getElementById('status').innerText = 'Enrollment successful! Key ID: ' + dnaKey.keyId;
      } catch (error) {
        document.getElementById('status').innerText = 'Enrollment failed: ' + error.message;
      }
    }
    
    async function authenticate() {
      try {
        const keyId = localStorage.getItem('dna_key_id');
        const privateKey = localStorage.getItem('dna_private_key');
        
        if (!keyId || !privateKey) {
          alert('Please enroll first!');
          return;
        }
        
        document.getElementById('status').innerText = 'Authenticating...';
        
        // Start authentication
        const challenge = await dnaAuth.auth.start({
          keyId: keyId,
          context: {
            appId: 'demo-app',
            deviceFingerprint: await dnaAuth.device.getFingerprint()
          }
        });
        
        // Sign challenge
        const signature = await dnaAuth.crypto.sign(
          challenge.challengeNonce,
          privateKey
        );
        
        // Complete authentication
        const tokens = await dnaAuth.auth.complete({
          keyId: keyId,
          challengeId: challenge.challengeId,
          signature: signature
        });
        
        document.getElementById('status').innerText = 'Authentication successful! Token: ' + tokens.accessToken.substring(0, 50) + '...';
      } catch (error) {
        document.getElementById('status').innerText = 'Authentication failed: ' + error.message;
      }
    }
  </script>
</body>
</html>
```

---

## STEP 7: TEST YOUR IMPLEMENTATION

### Unit Tests Example

```javascript
// test/crypto.test.js
const assert = require('assert');
const { generateKeyPair, sign, verify } = require('../src/crypto');

describe('Cryptography', () => {
  it('should generate valid key pair', () => {
    const { publicKey, privateKey } = generateKeyPair();
    assert(publicKey);
    assert(privateKey);
    assert(publicKey.length === 44); // Base64url encoded 32 bytes
  });
  
  it('should sign and verify message', () => {
    const { publicKey, privateKey } = generateKeyPair();
    const message = 'test message';
    
    const signature = sign(message, privateKey);
    const isValid = verify(message, signature, publicKey);
    
    assert(isValid === true);
  });
  
  it('should reject invalid signature', () => {
    const { publicKey } = generateKeyPair();
    const { privateKey: wrongPrivateKey } = generateKeyPair();
    const message = 'test message';
    
    const signature = sign(message, wrongPrivateKey);
    const isValid = verify(message, signature, publicKey);
    
    assert(isValid === false);
  });
});
```

### Integration Tests

```javascript
// test/auth-flow.test.js
const request = require('supertest');
const app = require('../src/app');

describe('Authentication Flow', () => {
  let keyId, privateKey, challengeId;
  
  it('should enroll new user', async () => {
    // Request enrollment
    const enrollResp = await request(app)
      .post('/api/v1/enrollment/request')
      .send({
        user_id: 'test-user',
        policy_id: 'standard-policy'
      })
      .expect(200);
    
    assert(enrollResp.body.success);
    const enrollmentToken = enrollResp.body.data.enrollment_token;
    
    // Create DNA key
    const createResp = await request(app)
      .post('/api/v1/enrollment/create')
      .set('Authorization', `Bearer ${enrollmentToken}`)
      .send({
        device_info: { fingerprint: 'test-device' }
      })
      .expect(201);
    
    assert(createResp.body.success);
    keyId = createResp.body.data.key_id;
    privateKey = createResp.body.data.private_key;
  });
  
  it('should authenticate with DNA key', async () => {
    // Start authentication
    const startResp = await request(app)
      .post('/api/v1/auth/start')
      .send({
        key_id: keyId,
        context: { app_id: 'test-app' }
      })
      .expect(200);
    
    assert(startResp.body.success);
    const challenge = startResp.body.data;
    challengeId = challenge.challenge_id;
    
    // Sign challenge (mock)
    const signature = signChallenge(challenge, privateKey);
    
    // Complete authentication
    const completeResp = await request(app)
      .post('/api/v1/auth/complete')
      .send({
        key_id: keyId,
        challenge_id: challengeId,
        signature: signature
      })
      .expect(200);
    
    assert(completeResp.body.success);
    assert(completeResp.body.data.access_token);
  });
});
```

---

## STEP 8: DEPLOY LOCALLY

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: dnalock
      POSTGRES_USER: dnalock
      POSTGRES_PASSWORD: dnalock_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
  
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://dnalock:dnalock_dev_password@postgres:5432/dnalock
      REDIS_URL: redis://redis:6379
      NODE_ENV: development
    depends_on:
      - postgres
      - redis
    volumes:
      - ./src:/app/src

volumes:
  postgres-data:
  redis-data:
```

### Run Locally

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api npm run migrate

# Run tests
docker-compose exec api npm test

# Stop all services
docker-compose down
```

---

## NEXT STEPS

1. **Review the full blueprint** (`AUTONOMOUS_DEVELOPMENT_BLUEPRINT.md`)
2. **Follow the implementation roadmap** (`IMPLEMENTATION_ROADMAP.md`)
3. **Implement Phase 0-1** (Foundation & Core Crypto)
4. **Set up CI/CD pipeline**
5. **Begin security reviews early**
6. **Document as you build**
7. **Test continuously**

---

## HELPFUL RESOURCES

### Documentation
- Full Blueprint: `AUTONOMOUS_DEVELOPMENT_BLUEPRINT.md`
- Implementation Roadmap: `IMPLEMENTATION_ROADMAP.md`
- API Specification: Will be in `spec/api-spec.yaml`

### Libraries to Use
- **JavaScript/TypeScript:**
  - `tweetnacl` - Ed25519 crypto
  - `cbor` - Canonical encoding
  - `express` - API server
  - `three.js` - 3D visualization

- **Python:**
  - `pynacl` - Ed25519 crypto
  - `cbor2` - Canonical encoding
  - `fastapi` - API server
  - `sqlalchemy` - Database ORM

- **Mobile:**
  - iOS: Built-in CryptoKit
  - Android: Built-in AndroidKeyStore

### Support
- GitHub Issues: For bugs and feature requests
- Discussions: For questions and ideas
- Security: security@dnalock.system (for vulnerabilities)

---

## IMPORTANT REMINDERS

⚠️ **Security First:**
- Never log private keys
- Always use HTTPS in production
- Validate all inputs
- Use rate limiting
- Implement proper error handling

⚠️ **Testing:**
- Write tests before code
- Aim for >90% coverage
- Test error cases
- Performance test early

⚠️ **Documentation:**
- Document APIs with OpenAPI
- Comment complex code
- Update docs with code changes
- Create examples

---

**Ready to build? Start with Phase 0 of the Implementation Roadmap!**

Good luck! 🚀
