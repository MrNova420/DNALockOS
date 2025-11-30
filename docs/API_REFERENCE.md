# DNALockOS API Reference

## Overview

The DNALockOS API provides a complete interface for DNA strand authentication. This document covers all endpoints, request/response formats, and usage examples.

**Base URL**: `http://localhost:8000/api/v1`

---

## Authentication

### Enrollment

Create a new DNA authentication key for a user.

```http
POST /api/v1/enroll
Content-Type: application/json
```

**Request Body:**

```json
{
  "subject_id": "user@example.com",
  "subject_type": "human",
  "security_level": "ultimate",
  "mfa_required": true,
  "biometric_required": false,
  "device_binding_required": true
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| subject_id | string | Yes | Unique identifier (email, username, etc.) |
| subject_type | string | No | Type: "human", "machine", "service" |
| security_level | string | No | "standard", "enhanced", "maximum", "government", "ultimate" |
| mfa_required | boolean | No | Require multi-factor authentication |
| biometric_required | boolean | No | Require biometric verification |
| device_binding_required | boolean | No | Bind key to specific device |

**Response:**

```json
{
  "key_id": "dna-abc123xyz",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2025-01-01T00:00:00Z",
  "visual_seed": "9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c",
  "segment_count": 1048576,
  "security_level": "ultimate",
  "checksum": "sha3_256_checksum_value"
}
```

---

### Challenge Request

Request an authentication challenge.

```http
POST /api/v1/challenge
Content-Type: application/json
```

**Request Body:**

```json
{
  "key_id": "dna-abc123xyz"
}
```

**Response:**

```json
{
  "success": true,
  "challenge_id": "chal-xyz789",
  "challenge": "hex_encoded_random_challenge_64_bytes",
  "expires_at": "2024-01-01T00:01:00Z",
  "algorithm": "Ed25519"
}
```

---

### Authentication

Submit a signed challenge for authentication.

```http
POST /api/v1/authenticate
Content-Type: application/json
```

**Request Body:**

```json
{
  "challenge_id": "chal-xyz789",
  "key_id": "dna-abc123xyz",
  "signature": "hex_encoded_signature"
}
```

**Response:**

```json
{
  "success": true,
  "session_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_value",
  "user_id": "user@example.com"
}
```

---

### Token Refresh

Refresh an access token.

```http
POST /api/v1/refresh
Content-Type: application/json
```

**Request Body:**

```json
{
  "refresh_token": "refresh_token_value"
}
```

**Response:**

```json
{
  "success": true,
  "access_token": "new_access_token",
  "expires_in": 3600
}
```

---

## Key Management

### Get Key Info

Retrieve information about a DNA key.

```http
GET /api/v1/keys/{key_id}
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "key_id": "dna-abc123xyz",
  "subject_id": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "expires_at": "2025-01-01T00:00:00Z",
  "status": "active",
  "security_level": "ultimate",
  "segment_count": 1048576,
  "last_used": "2024-01-15T10:30:00Z"
}
```

---

### Revoke Key

Revoke a DNA key.

```http
POST /api/v1/keys/{key_id}/revoke
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

```json
{
  "reason": "compromised"
}
```

**Response:**

```json
{
  "success": true,
  "revoked_at": "2024-01-15T12:00:00Z"
}
```

---

### List User Keys

List all keys for the authenticated user.

```http
GET /api/v1/keys
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "keys": [
    {
      "key_id": "dna-abc123xyz",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

---

## 3D Visualization

### Get Visual Config

Get 3D visualization configuration for a key.

```http
GET /api/v1/keys/{key_id}/visual
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "geometry": {
    "points": [...],
    "radius": 100,
    "height": 800,
    "turns": 8
  },
  "animation": {
    "rotation_speed": 0.01,
    "pulse_frequency": 2.0,
    "glow_intensity": 0.8
  },
  "style": "tron"
}
```

---

## Verification

### Verify Key

Verify a DNA key through all security barriers.

```http
POST /api/v1/verify
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

```json
{
  "key_id": "dna-abc123xyz",
  "checksum": "provided_checksum"
}
```

**Response:**

```json
{
  "is_valid": true,
  "barriers_passed": 12,
  "barriers_total": 12,
  "verification_time_ms": 45,
  "details": {
    "structural_integrity": true,
    "segment_count": true,
    "checksum_valid": true,
    "signature_valid": true,
    "timestamp_valid": true,
    "entropy_sufficient": true
  }
}
```

---

## Threat Intelligence

### Check IP Reputation

Check reputation of an IP address.

```http
GET /api/v1/threat/ip/{ip_address}
Authorization: Bearer {access_token}
```

**Response:**

```json
{
  "ip_address": "192.168.1.100",
  "reputation_score": 85.5,
  "risk_level": "LOW",
  "is_proxy": false,
  "is_vpn": false,
  "is_tor_exit": false,
  "country_code": "US",
  "threat_count_24h": 0
}
```

---

## Error Responses

All errors return a consistent format:

```json
{
  "error": true,
  "error_code": "INVALID_KEY",
  "error_message": "The provided DNA key is invalid or expired",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_KEY | 400 | Invalid or malformed key |
| KEY_EXPIRED | 401 | Key has expired |
| KEY_REVOKED | 401 | Key has been revoked |
| UNAUTHORIZED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

---

## Rate Limiting

API endpoints are rate limited:

| Endpoint Type | Limit |
|---------------|-------|
| Authentication | 10/minute |
| Key Operations | 60/minute |
| Verification | 100/minute |
| Read Operations | 200/minute |

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704067200
```

---

## SDK Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Enroll
response = requests.post(f"{API_URL}/enroll", json={
    "subject_id": "user@example.com",
    "security_level": "ultimate"
})
key_data = response.json()

# Get challenge
response = requests.post(f"{API_URL}/challenge", json={
    "key_id": key_data["key_id"]
})
challenge = response.json()

# Authenticate (sign challenge with your key)
signature = sign_challenge(challenge["challenge"], private_key)
response = requests.post(f"{API_URL}/authenticate", json={
    "challenge_id": challenge["challenge_id"],
    "key_id": key_data["key_id"],
    "signature": signature
})
session = response.json()
```

### JavaScript

```javascript
const API_URL = 'http://localhost:8000/api/v1';

// Enroll
const enrollResponse = await fetch(`${API_URL}/enroll`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    subject_id: 'user@example.com',
    security_level: 'ultimate'
  })
});
const keyData = await enrollResponse.json();

// Get challenge
const challengeResponse = await fetch(`${API_URL}/challenge`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key_id: keyData.key_id })
});
const challenge = await challengeResponse.json();
```

---

## Webhooks

Configure webhooks to receive real-time notifications:

### Events

| Event | Description |
|-------|-------------|
| key.created | New DNA key enrolled |
| key.authenticated | Successful authentication |
| key.revoked | Key was revoked |
| threat.detected | Security threat detected |
| session.terminated | Session was terminated |

### Webhook Payload

```json
{
  "event": "key.authenticated",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "key_id": "dna-abc123xyz",
    "user_id": "user@example.com",
    "ip_address": "192.168.1.100"
  },
  "signature": "hmac_sha256_signature"
}
```

---

*API Version: 1.0.0*
