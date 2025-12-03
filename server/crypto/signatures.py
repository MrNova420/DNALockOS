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

PROPRIETARY AND CONFIDENTIAL
This is commercial software. Unauthorized copying, modification,
distribution, or use is strictly prohibited.
"""

"""
DNA-Key Authentication System - Ed25519 Digital Signatures

Implements Ed25519 signing and verification using PyNaCl (libsodium) with
fallback to cryptography library when PyNaCl is unavailable.

Ed25519 provides:
- 256-bit security level
- Fast signing and verification
- Small signature size (64 bytes)
- Deterministic signatures

Reference: RFC 8032 - Edwards-Curve Digital Signature Algorithm (EdDSA)
"""

from typing import Optional, Tuple

# Import backend abstraction
try:
    from .backend import get_signer_backend
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False


class Ed25519SigningKey:
    """
    Ed25519 private key for signing operations.

    Uses backend abstraction to support both PyNaCl and cryptography library.
    """

    def __init__(self, seed: Optional[bytes] = None):
        """
        Initialize an Ed25519 signing key.

        Args:
            seed: Optional 32-byte seed for deterministic key generation.
                  If None, generates a random key using CSPRNG.

        Raises:
            ValueError: If seed is provided but not exactly 32 bytes.
            RuntimeError: If no signing backend is available.
        """
        if seed is not None:
            if len(seed) != 32:
                raise ValueError("Seed must be exactly 32 bytes")
        
        if BACKEND_AVAILABLE:
            self._backend = get_signer_backend(seed)
        else:
            raise RuntimeError(
                "No signing backend available. "
                "Install PyNaCl (pip install PyNaCl) or "
                "cryptography (pip install cryptography)."
            )

    def sign(self, message: bytes) -> bytes:
        """
        Sign a message with this private key.

        Args:
            message: The message bytes to sign

        Returns:
            64-byte Ed25519 signature

        Raises:
            TypeError: If message is not bytes
        """
        if not isinstance(message, bytes):
            raise TypeError("Message must be bytes")

        return self._backend.sign(message)

    def to_bytes(self) -> bytes:
        """
        Export the private key as raw bytes.

        Returns:
            32-byte private key

        Security:
            Handle with care - this is the secret key material.
            Should be encrypted before storage.
        """
        return self._backend.to_bytes()

    def verify_key(self) -> "Ed25519VerifyKey":
        """
        Get the corresponding public verification key.

        Returns:
            Ed25519VerifyKey object for signature verification
        """
        public_key_bytes = self._backend.get_public_key()
        return Ed25519VerifyKey(key_bytes=public_key_bytes)

    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "Ed25519SigningKey":
        """
        Load a private key from raw bytes.

        Args:
            key_bytes: 32-byte private key

        Returns:
            Ed25519SigningKey object

        Raises:
            ValueError: If key_bytes is not exactly 32 bytes
        """
        if len(key_bytes) != 32:
            raise ValueError("Private key must be exactly 32 bytes")
        return cls(seed=key_bytes)


class Ed25519VerifyKey:
    """
    Ed25519 public key for signature verification.

    Uses backend abstraction to support both PyNaCl and cryptography library.
    """

    def __init__(self, key_bytes: bytes):
        """
        Initialize an Ed25519 verification key.

        Args:
            key_bytes: 32-byte public key

        Raises:
            ValueError: If key_bytes is not exactly 32 bytes
            RuntimeError: If no signing backend is available
        """
        if len(key_bytes) != 32:
            raise ValueError("Public key must be exactly 32 bytes")
        
        self._key_bytes = key_bytes
        
        # We need backend-specific public key objects for verification.
        # The backend abstraction in backend.py is designed for private keys,
        # so we instantiate public key objects directly here for verification.
        # Future improvement: Could create a VerifierBackend abstraction similar to SignerBackend.
        if BACKEND_AVAILABLE:
            # Store the backend type for verification
            try:
                import nacl.signing
                self._verify_key = nacl.signing.VerifyKey(key_bytes)
                self._use_nacl = True
            except ImportError:
                from cryptography.hazmat.primitives.asymmetric import ed25519
                self._verify_key = ed25519.Ed25519PublicKey.from_public_bytes(key_bytes)
                self._use_nacl = False
        else:
            raise RuntimeError(
                "No signing backend available. "
                "Install PyNaCl (pip install PyNaCl) or "
                "cryptography (pip install cryptography)."
            )

    def verify(self, message: bytes, signature: bytes) -> bool:
        """
        Verify a signature on a message.

        Args:
            message: The original message bytes
            signature: The 64-byte Ed25519 signature

        Returns:
            True if signature is valid, False otherwise

        Raises:
            TypeError: If message or signature are not bytes
            ValueError: If signature is not exactly 64 bytes
        """
        if not isinstance(message, bytes):
            raise TypeError("Message must be bytes")
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        if len(signature) != 64:
            raise ValueError("Signature must be exactly 64 bytes")

        try:
            if self._use_nacl:
                self._verify_key.verify(message, signature)
                return True
            else:
                from cryptography.exceptions import InvalidSignature
                self._verify_key.verify(signature, message)
                return True
        except Exception:
            return False

    def to_bytes(self) -> bytes:
        """
        Export the public key as raw bytes.

        Returns:
            32-byte public key
        """
        return self._key_bytes

    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "Ed25519VerifyKey":
        """
        Load a public key from raw bytes.

        Args:
            key_bytes: 32-byte public key

        Returns:
            Ed25519VerifyKey object

        Raises:
            ValueError: If key_bytes is not exactly 32 bytes
        """
        if len(key_bytes) != 32:
            raise ValueError("Public key must be exactly 32 bytes")
        return cls(key_bytes=key_bytes)


def generate_ed25519_keypair() -> Tuple[Ed25519SigningKey, Ed25519VerifyKey]:
    """
    Generate a new Ed25519 key pair.

    Uses CSPRNG for secure random key generation.

    Returns:
        Tuple of (signing_key, verify_key)

    Example:
        >>> signing_key, verify_key = generate_ed25519_keypair()
        >>> message = b"Hello, DNA-Key!"
        >>> signature = signing_key.sign(message)
        >>> assert verify_key.verify(message, signature)
    """
    signing_key = Ed25519SigningKey()
    verify_key = signing_key.verify_key()
    return signing_key, verify_key
