# DNALockOS Integration SDK

This directory contains SDKs for integrating DNALockOS authentication into third-party applications.

## Available SDKs

### Python SDK (`python/`)

Full-featured SDK for Python applications with support for both synchronous and asynchronous operations.

```python
from sdk.python import DNALockClient, DNALockConfig, SecurityLevel

# Initialize client
config = DNALockConfig(api_url="https://api.dnalock.example.com")
client = DNALockClient(config)

# Enroll a new user
enrollment = client.enroll(
    subject_id="user@example.com",
    security_level=SecurityLevel.ENHANCED,
    validity_days=180
)

if enrollment.success:
    # Store the key securely (e.g., in encrypted storage)
    save_to_secure_storage(user_id, enrollment.serialized_key)
    print(f"Enrolled key: {enrollment.key_id}")

# Later, authenticate
stored_key = get_from_secure_storage(user_id)
result = client.authenticate(stored_key)

if result.success:
    print(f"Session token: {result.session_token}")
    # Use session_token for authenticated requests
```

#### Installation

```bash
# Required dependencies
pip install requests pynacl

# Optional: for CBOR key encoding
pip install cbor2
```

### JavaScript SDK (`javascript/`)

Browser and Node.js compatible SDK for web applications.

```javascript
import { DNALockClient, SecurityLevel } from './sdk/javascript/dnalock-sdk.js';

// Initialize client
const client = new DNALockClient({
    apiUrl: 'https://api.dnalock.example.com'
});

// Enroll a new user
const enrollment = await client.enroll({
    subjectId: 'user@example.com',
    securityLevel: SecurityLevel.ENHANCED,
    validityDays: 180
});

if (enrollment.success) {
    // Store the key securely
    localStorage.setItem('dna_key', enrollment.serializedKey);
    console.log('Enrolled key:', enrollment.keyId);
}

// Later, authenticate
const storedKey = localStorage.getItem('dna_key');
const result = await client.authenticate(storedKey, {
    signChallenge: async (challenge, privateKey) => {
        // Use your preferred crypto library
        return signWithNacl(challenge, privateKey);
    }
});

if (result.success) {
    console.log('Session token:', result.sessionToken);
}
```

#### Browser Usage

```html
<script src="https://cdn.jsdelivr.net/npm/tweetnacl/nacl-fast.min.js"></script>
<script src="./sdk/javascript/dnalock-sdk.js"></script>
<script>
    const client = DNALock.createClient('https://api.dnalock.example.com');
    
    async function login() {
        const storedKey = localStorage.getItem('dna_key');
        const result = await client.authenticate(storedKey);
        // ...
    }
</script>
```

## Integration Patterns

### 1. Basic Integration

For simple authentication needs:

```python
# Python
client = DNALockClient()

# Enrollment (one-time)
enrollment = client.enroll("user@example.com")
store_key(user_id, enrollment.serialized_key)

# Authentication (each login)
result = client.authenticate(get_key(user_id))
if result.success:
    create_session(result.session_token)
```

### 2. Two-Factor Authentication

Use DNALockOS as a second factor:

```python
# After password verification
if verify_password(username, password):
    stored_key = get_dna_key(username)
    result = client.authenticate(stored_key)
    
    if result.success:
        grant_access(username)
```

### 3. Enterprise SSO Integration

```python
# SAML/OIDC integration
class DNALockSSOProvider:
    def __init__(self, client):
        self.client = client
    
    def authenticate_user(self, user_id, dna_key):
        result = self.client.authenticate(dna_key)
        if result.success:
            return generate_sso_token(user_id, result.session_token)
        return None
```

### 4. API Gateway Integration

```python
# Middleware for API authentication
def dna_auth_middleware(request):
    auth_header = request.headers.get('X-DNA-Auth')
    if not auth_header:
        return unauthorized()
    
    result = client.authenticate(auth_header)
    if not result.success:
        return unauthorized()
    
    request.user = get_user(result.key_id)
    return continue_request()
```

## Security Recommendations

1. **Store keys securely**: Use encrypted storage (Keychain on iOS, Keystore on Android, encrypted file storage on servers)

2. **Use HTTPS**: Always use TLS for API communication

3. **Implement rate limiting**: Protect against brute force attempts

4. **Monitor for anomalies**: Log and alert on suspicious authentication patterns

5. **Rotate keys periodically**: Set appropriate validity periods

6. **Handle revocation**: Check revocation status before critical operations

## Error Handling

Both SDKs provide specific exception types:

```python
# Python
try:
    result = client.authenticate(key)
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except NetworkError as e:
    print(f"Network issue: {e.message}")
except DNALockError as e:
    print(f"General error: {e.code} - {e.message}")
```

```javascript
// JavaScript
try {
    const result = await client.authenticate(key);
} catch (error) {
    if (error instanceof AuthenticationError) {
        console.error('Auth failed:', error.message);
    } else if (error instanceof NetworkError) {
        console.error('Network issue:', error.message);
    } else {
        console.error('Error:', error.code, error.message);
    }
}
```

## Support

For issues and questions:
- GitHub Issues: Report bugs and feature requests
- Documentation: See main README and API docs
- Security: Report vulnerabilities to security@dnalock.example.com
