<!--
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill (Operating as WeNova Interactive)

PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE
This is NOT free software. This is NOT open source. Commercial license required.
Unauthorized use is strictly prohibited.
-->

# DNALockOS - Getting Started Guide

## Quick Start in 5 Minutes

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/MrNova420/DNALockOS.git
cd DNALockOS

# Install Python dependencies
pip install -r requirements.txt

# Verify installation by running tests
python -m pytest tests/ -v --tb=no | tail -5
```

You should see: `556 passed`

### Step 2: Generate Your First DNA Key

```python
# Start Python
python

# Import the generator
from server.crypto.dna_generator import generate_dna_key
from server.crypto.dna_key import SecurityLevel

# Generate a DNA key
key = generate_dna_key("your@email.com", SecurityLevel.ENHANCED)

# View key details
print(f"Key ID: {key.key_id}")
print(f"Segments: {key.dna_helix.segment_count:,}")
print(f"Created: {key.metadata.created_at}")
```

### Step 3: Verify the Key

```python
from server.crypto.dna_verifier import verify_dna_key

# Verify the key through all security barriers
report = verify_dna_key(key)

print(f"Valid: {report.is_valid}")
print(f"Barriers Passed: {report.barriers_passed}/12")
```

### Step 4: Generate 3D Model

```python
from server.visual.dna_strand_3d_model import DNAStrand3DGenerator

generator = DNAStrand3DGenerator()
model = generator.generate(key)

print(f"3D Points: {len(model.points)}")
print(f"Model Hash: {model.model_checksum[:32]}...")
```

### Step 5: Start the Web Interface

```bash
# Terminal 1: Start backend
uvicorn server.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd web/frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser!

---

## Security Levels Guide

| Level | Segments | Best For |
|-------|----------|----------|
| **STANDARD** | 1,024 | Personal projects, testing |
| **ENHANCED** | 16,384 | Small businesses, apps |
| **MAXIMUM** | 65,536 | Enterprise applications |
| **GOVERNMENT** | 262,144 | Government, healthcare |
| **ULTIMATE** | 1,048,576 | Military, critical infrastructure |

---

## Core Modules

### DNA Key Generation

```python
from server.crypto.dna_generator import generate_dna_key
from server.crypto.dna_key import SecurityLevel

# Standard key (1,024 segments)
key = generate_dna_key("user", SecurityLevel.STANDARD)

# Ultimate key (1,048,576 segments)
key = generate_dna_key("user", SecurityLevel.ULTIMATE)
```

### DNA Verification

```python
from server.crypto.dna_verifier import verify_dna_key

report = verify_dna_key(key)
if report.is_valid:
    print("✓ Key verified successfully")
```

### Neural Authentication

```python
from server.security.neural_auth import NeuralAuthenticationCoordinator

coordinator = NeuralAuthenticationCoordinator()
decision = coordinator.authenticate("user_id")

if decision.should_allow:
    print(f"Allowed with {decision.confidence:.0%} confidence")
```

### Threat Intelligence

```python
from server.security.threat_intelligence import ThreatIntelligenceService

service = ThreatIntelligenceService()
ip_rep = service.check_ip("192.168.1.100")

print(f"IP Score: {ip_rep.reputation_score}")
```

### Quantum-Safe Cryptography

```python
from server.crypto.quantum_safe import KyberKEM, DilithiumSignature

# Post-quantum key exchange
kem = KyberKEM("kyber768")
keypair = kem.generate_keypair()

# Post-quantum signatures
sig = DilithiumSignature("dilithium3")
keypair = sig.generate_keypair()
signature = sig.sign(b"message", keypair.private_key)
```

### Distributed Ledger

```python
from server.security.distributed_ledger import DNAStrandRegistry

registry = DNAStrandRegistry()
tx = registry.register_strand(
    dna_key_id="key-001",
    dna_checksum="checksum",
    owner_address="owner",
    security_level="ultimate",
    segment_count=1000000,
    signature=b"sig"
)
```

---

## Testing

```bash
# Run all tests (556 tests)
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/unit/test_dna_key.py -v
python -m pytest tests/unit/test_neural_auth.py -v
python -m pytest tests/unit/test_quantum_safe.py -v

# Run with coverage
python -m pytest tests/ --cov=server --cov-report=html
```

---

## Project Structure

```
DNALockOS/
├── server/
│   ├── crypto/              # Cryptographic modules
│   │   ├── dna_key.py       # DNA key data models
│   │   ├── dna_generator.py # Key generation
│   │   ├── dna_verifier.py  # Verification
│   │   ├── quantum_safe.py  # Post-quantum crypto
│   │   └── ...
│   ├── security/            # Security modules
│   │   ├── neural_auth.py   # AI authentication
│   │   ├── threat_intelligence.py
│   │   ├── distributed_ledger.py
│   │   └── session_management.py
│   ├── visual/              # 3D visualization
│   └── integration/         # Platform SDK
├── web/frontend/            # React/Next.js UI
├── tests/                   # 556+ tests
├── docs/                    # Documentation
└── requirements.txt
```

---

## Need Help?

- **Documentation**: `/docs/` directory
- **API Reference**: `/docs/API_REFERENCE.md`
- **Issues**: GitHub Issues

---

*Happy authenticating with DNA strands! 🧬*
