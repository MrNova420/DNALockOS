/**
 * =============================================================================
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * =============================================================================
 *
 * OWNERSHIP AND LEGAL NOTICE:
 *
 * This software and all associated intellectual property is the exclusive
 * property of WeNova Interactive, legally owned and operated by:
 *
 *     Kayden Shawn Massengill
 *
 * COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
 *
 * This is proprietary commercial software. It is NOT free software. It is NOT
 * open source software. This software is developed for commercial sale and
 * requires a valid commercial license for ANY use.
 *
 * STRICT PROHIBITION NOTICE:
 *
 * Without a valid commercial license agreement, you are PROHIBITED from:
 *   - Using this software for any purpose
 *   - Copying, reproducing, or duplicating this software
 *   - Modifying, adapting, or creating derivative works
 *   - Distributing, publishing, or transferring this software
 *   - Reverse engineering, decompiling, or disassembling this software
 *   - Sublicensing or permitting any third-party access
 *
 * LEGAL ENFORCEMENT:
 *
 * Unauthorized use will be prosecuted to the maximum extent of applicable law.
 *
 * For licensing inquiries: WeNova Interactive
 * =============================================================================
 */

/**
 * DNALockOS JavaScript/TypeScript SDK
 * 
 * A comprehensive SDK for integrating DNALockOS authentication
 * into web applications and Node.js services.
 * 
 * @version 1.0.0
 */

// ==================== Configuration ====================

/**
 * Configuration options for DNALockClient
 */
class DNALockConfig {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || 'http://localhost:8000';
        this.apiVersion = options.apiVersion || 'v1';
        this.apiKey = options.apiKey || null;
        this.clientId = options.clientId || null;
        this.timeout = options.timeout || 30000;
        this.retries = options.retries || 3;
        this.onError = options.onError || null;
    }

    get baseUrl() {
        return `${this.apiUrl}/api/${this.apiVersion}`;
    }

    /**
     * Create config from environment variables (Node.js only)
     */
    static fromEnv() {
        if (typeof process !== 'undefined' && process.env) {
            return new DNALockConfig({
                apiUrl: process.env.DNALOCK_API_URL || 'http://localhost:8000',
                apiKey: process.env.DNALOCK_API_KEY,
                clientId: process.env.DNALOCK_CLIENT_ID
            });
        }
        return new DNALockConfig();
    }
}

// ==================== Error Classes ====================

class DNALockError extends Error {
    constructor(message, code = 'UNKNOWN_ERROR', details = {}) {
        super(message);
        this.name = 'DNALockError';
        this.code = code;
        this.details = details;
    }

    toJSON() {
        return {
            error: this.code,
            message: this.message,
            details: this.details
        };
    }
}

class AuthenticationError extends DNALockError {
    constructor(message = 'Authentication failed', details = {}) {
        super(message, 'AUTH_FAILED', details);
        this.name = 'AuthenticationError';
    }
}

class EnrollmentError extends DNALockError {
    constructor(message = 'Enrollment failed', details = {}) {
        super(message, 'ENROLLMENT_FAILED', details);
        this.name = 'EnrollmentError';
    }
}

class NetworkError extends DNALockError {
    constructor(message = 'Network error', details = {}) {
        super(message, 'NETWORK_ERROR', details);
        this.name = 'NetworkError';
    }
}

class ValidationError extends DNALockError {
    constructor(message = 'Validation error', details = {}) {
        super(message, 'VALIDATION_ERROR', details);
        this.name = 'ValidationError';
    }
}

// ==================== Security Levels ====================

const SecurityLevel = {
    STANDARD: 'standard',
    ENHANCED: 'enhanced',
    MAXIMUM: 'maximum',
    GOVERNMENT: 'government'
};

// ==================== Main Client ====================

/**
 * DNALockOS Authentication Client
 * 
 * @example
 * // Initialize client
 * const client = new DNALockClient({ apiUrl: 'https://api.dnalock.example.com' });
 * 
 * // Enroll a new user
 * const enrollment = await client.enroll({
 *     subjectId: 'user@example.com',
 *     securityLevel: SecurityLevel.ENHANCED
 * });
 * 
 * // Store the serialized key securely
 * localStorage.setItem('dna_key', enrollment.serializedKey);
 * 
 * // Later, authenticate
 * const storedKey = localStorage.getItem('dna_key');
 * const result = await client.authenticate(storedKey);
 * 
 * if (result.success) {
 *     console.log('Session token:', result.sessionToken);
 * }
 */
class DNALockClient {
    constructor(config = {}) {
        this.config = config instanceof DNALockConfig ? config : new DNALockConfig(config);
    }

    /**
     * Make an HTTP request to the API
     * @private
     */
    async _request(method, endpoint, options = {}) {
        const url = `${this.config.baseUrl}/${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        if (this.config.apiKey) {
            headers['X-API-Key'] = this.config.apiKey;
        }

        if (this.config.clientId) {
            headers['X-Client-ID'] = this.config.clientId;
        }

        if (options.authToken) {
            headers['Authorization'] = `Bearer ${options.authToken}`;
        }

        const fetchOptions = {
            method,
            headers,
            ...options
        };

        if (options.body && typeof options.body === 'object') {
            fetchOptions.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, fetchOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new DNALockError(
                    errorData.error_message || `HTTP ${response.status}`,
                    errorData.error_code || 'HTTP_ERROR',
                    errorData
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof DNALockError) {
                throw error;
            }
            
            if (this.config.onError) {
                this.config.onError(error);
            }
            
            throw new NetworkError(error.message);
        }
    }

    // ==================== Health & Status ====================

    /**
     * Check the health status of the DNALockOS server
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.config.apiUrl}/health`);
            return await response.json();
        } catch (error) {
            throw new NetworkError(`Health check failed: ${error.message}`);
        }
    }

    // ==================== Enrollment ====================

    /**
     * Enroll a new DNA key
     * 
     * @param {Object} options Enrollment options
     * @param {string} options.subjectId Unique identifier for the subject
     * @param {string} [options.securityLevel='standard'] Security level
     * @param {string} [options.subjectType='human'] Type of subject
     * @param {string} [options.policyId='default-policy-v1'] Policy ID
     * @param {number} [options.validityDays=365] Validity period in days
     * @param {boolean} [options.mfaRequired=false] Whether MFA is required
     * @param {boolean} [options.biometricRequired=false] Whether biometric is required
     * @param {boolean} [options.deviceBindingRequired=false] Whether device binding is required
     * @returns {Promise<Object>} Enrollment result
     * 
     * @example
     * const result = await client.enroll({
     *     subjectId: 'user@example.com',
     *     securityLevel: SecurityLevel.ENHANCED,
     *     validityDays: 180
     * });
     * 
     * if (result.success) {
     *     // Store result.serializedKey securely
     *     await secureStorage.save('dna_key', result.serializedKey);
     * }
     */
    async enroll(options) {
        if (!options.subjectId) {
            throw new ValidationError('subjectId is required');
        }

        const data = {
            subject_id: options.subjectId,
            subject_type: options.subjectType || 'human',
            security_level: options.securityLevel || SecurityLevel.STANDARD,
            policy_id: options.policyId || 'default-policy-v1',
            validity_days: options.validityDays || 365,
            mfa_required: options.mfaRequired || false,
            biometric_required: options.biometricRequired || false,
            device_binding_required: options.deviceBindingRequired || false
        };

        try {
            const response = await this._request('POST', 'enroll', { body: data });
            
            return {
                success: response.success,
                keyId: response.key_id,
                serializedKey: response.serialized_key,
                visualSeed: response.visual_seed,
                createdAt: response.created_at ? new Date(response.created_at) : null,
                expiresAt: response.expires_at ? new Date(response.expires_at) : null,
                errorMessage: response.error_message
            };
        } catch (error) {
            throw new EnrollmentError(error.message, error.details);
        }
    }

    // ==================== Authentication ====================

    /**
     * Request an authentication challenge
     * 
     * @param {string} keyId The DNA key ID
     * @returns {Promise<Object>} Challenge result
     */
    async getChallenge(keyId) {
        if (!keyId) {
            throw new ValidationError('keyId is required');
        }

        const response = await this._request('POST', 'challenge', { 
            body: { key_id: keyId } 
        });

        return {
            success: response.success,
            challenge: response.challenge,
            challengeId: response.challenge_id,
            expiresAt: response.expires_at ? new Date(response.expires_at) : null,
            errorMessage: response.error_message
        };
    }

    /**
     * Submit a signed challenge response
     * 
     * @param {string} challengeId Challenge ID
     * @param {string} challengeResponse Hex-encoded signed response
     * @returns {Promise<Object>} Authentication result
     */
    async submitResponse(challengeId, challengeResponse) {
        if (!challengeId || !challengeResponse) {
            throw new ValidationError('challengeId and challengeResponse are required');
        }

        const response = await this._request('POST', 'authenticate', {
            body: {
                challenge_id: challengeId,
                challenge_response: challengeResponse
            }
        });

        return {
            success: response.success,
            sessionToken: response.session_token,
            expiresAt: response.expires_at ? new Date(response.expires_at) : null,
            keyId: response.key_id,
            isAdmin: response.is_admin || false,
            permissions: response.permissions || [],
            errorMessage: response.error_message
        };
    }

    /**
     * Complete authentication flow with a stored key
     * 
     * @param {string} serializedKey Base64-encoded serialized DNA key
     * @param {Object} [options] Authentication options
     * @param {Function} [options.signChallenge] Custom signing function
     * @returns {Promise<Object>} Authentication result
     * 
     * @example
     * // Retrieve stored key
     * const storedKey = await secureStorage.get('dna_key');
     * 
     * // Authenticate
     * const result = await client.authenticate(storedKey);
     * 
     * if (result.success) {
     *     // Use session token for subsequent requests
     *     setAuthHeader(result.sessionToken);
     * }
     */
    async authenticate(serializedKey, options = {}) {
        // Decode the key
        let keyData;
        try {
            const decoded = atob(serializedKey);
            keyData = JSON.parse(decoded);
        } catch (error) {
            throw new ValidationError('Invalid serialized key format');
        }

        const keyId = keyData.key_id;
        const privateKey = keyData.private_key;

        if (!keyId) {
            throw new ValidationError('Key ID not found in serialized key');
        }

        // Get challenge
        const challengeResult = await this.getChallenge(keyId);

        if (!challengeResult.success) {
            throw new AuthenticationError(
                challengeResult.errorMessage || 'Failed to get challenge'
            );
        }

        // Sign challenge
        let challengeResponse;
        if (options.signChallenge) {
            // Use custom signing function
            challengeResponse = await options.signChallenge(
                challengeResult.challenge,
                privateKey
            );
        } else {
            // Use built-in signing (requires tweetnacl or similar)
            challengeResponse = await this._signChallenge(
                challengeResult.challenge,
                privateKey
            );
        }

        // Submit response
        return this.submitResponse(challengeResult.challengeId, challengeResponse);
    }

    /**
     * Sign a challenge with the private key
     * @private
     */
    async _signChallenge(challengeHex, privateKeyBase64) {
        // Try to use Web Crypto API or tweetnacl
        if (typeof window !== 'undefined' && window.crypto && window.crypto.subtle) {
            // Web Crypto API available - but doesn't support Ed25519 in all browsers
            // Fall back to error for now, user should provide signChallenge function
        }

        // Try tweetnacl if available
        if (typeof nacl !== 'undefined') {
            const privateKey = this._base64ToBytes(privateKeyBase64);
            const challenge = this._hexToBytes(challengeHex);
            const signature = nacl.sign.detached(challenge, privateKey);
            return this._bytesToHex(signature);
        }

        throw new Error(
            'No signing library available. Please provide a signChallenge function ' +
            'or include tweetnacl library.'
        );
    }

    // ==================== Key Management ====================

    /**
     * Get the visual DNA configuration for rendering
     * 
     * @param {string} keyId The DNA key ID
     * @returns {Promise<Object>} Visual configuration
     */
    async getVisualConfig(keyId) {
        return this._request('GET', `visual/${keyId}`);
    }

    /**
     * Revoke a DNA key (requires admin authentication)
     * 
     * @param {Object} options Revocation options
     * @param {string} options.keyId Key ID to revoke
     * @param {string} options.reason Revocation reason
     * @param {string} options.revokedBy Identity of revoker
     * @param {string} options.authToken Admin authentication token
     * @param {string} [options.notes] Optional notes
     * @returns {Promise<Object>} Revocation result
     */
    async revokeKey(options) {
        const { keyId, reason, revokedBy, authToken, notes } = options;

        if (!keyId || !reason || !revokedBy || !authToken) {
            throw new ValidationError('keyId, reason, revokedBy, and authToken are required');
        }

        const data = {
            key_id: keyId,
            reason: reason,
            revoked_by: revokedBy
        };

        if (notes) {
            data.notes = notes;
        }

        return this._request('POST', 'admin/revoke', {
            body: data,
            authToken
        });
    }

    // ==================== Utility Methods ====================

    /**
     * Convert base64 string to Uint8Array
     * @private
     */
    _base64ToBytes(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
    }

    /**
     * Convert hex string to Uint8Array
     * @private
     */
    _hexToBytes(hex) {
        const bytes = new Uint8Array(hex.length / 2);
        for (let i = 0; i < bytes.length; i++) {
            bytes[i] = parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return bytes;
    }

    /**
     * Convert Uint8Array to hex string
     * @private
     */
    _bytesToHex(bytes) {
        return Array.from(bytes)
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }
}

// ==================== Factory Functions ====================

/**
 * Create a DNALockOS client with simple configuration
 * 
 * @param {string} apiUrl API server URL
 * @param {string} [apiKey] Optional API key
 * @returns {DNALockClient} Configured client
 * 
 * @example
 * const client = createClient('https://api.dnalock.example.com', 'your-api-key');
 */
function createClient(apiUrl, apiKey = null) {
    return new DNALockClient({ apiUrl, apiKey });
}

// ==================== Exports ====================

// ES Module exports
export {
    DNALockClient,
    DNALockConfig,
    DNALockError,
    AuthenticationError,
    EnrollmentError,
    NetworkError,
    ValidationError,
    SecurityLevel,
    createClient
};

// CommonJS compatibility
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DNALockClient,
        DNALockConfig,
        DNALockError,
        AuthenticationError,
        EnrollmentError,
        NetworkError,
        ValidationError,
        SecurityLevel,
        createClient
    };
}

// Browser global
if (typeof window !== 'undefined') {
    window.DNALock = {
        DNALockClient,
        DNALockConfig,
        DNALockError,
        AuthenticationError,
        EnrollmentError,
        NetworkError,
        ValidationError,
        SecurityLevel,
        createClient
    };
}
