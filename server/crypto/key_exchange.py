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
DNA-Key Authentication System - X25519 Key Exchange

Implements X25519 Elliptic Curve Diffie-Hellman (ECDH) key exchange using PyNaCl
with fallback to cryptography library when PyNaCl is unavailable.

X25519 provides:
- 128-bit security level (256-bit keys)
- Fast key exchange operations
- Ephemeral key generation for forward secrecy
- Shared secret derivation

Reference: RFC 7748 - Elliptic Curves for Security
"""

import warnings
from typing import Optional, Tuple

# Check for available backends
_NACL_AVAILABLE = None
_CRYPTOGRAPHY_AVAILABLE = None


def _check_nacl() -> bool:
    """Check if PyNaCl is available."""
    global _NACL_AVAILABLE
    if _NACL_AVAILABLE is None:
        try:
            import nacl.public  # noqa: F401
            _NACL_AVAILABLE = True
        except ImportError:
            _NACL_AVAILABLE = False
    return _NACL_AVAILABLE


def _check_cryptography() -> bool:
    """Check if cryptography library is available."""
    global _CRYPTOGRAPHY_AVAILABLE
    if _CRYPTOGRAPHY_AVAILABLE is None:
        try:
            from cryptography.hazmat.primitives.asymmetric import x25519  # noqa: F401
            _CRYPTOGRAPHY_AVAILABLE = True
        except ImportError:
            _CRYPTOGRAPHY_AVAILABLE = False
    return _CRYPTOGRAPHY_AVAILABLE


class X25519PrivateKey:
    """
    X25519 private key for key exchange operations.

    Supports both PyNaCl and cryptography library backends.
    """

    def __init__(self, seed: Optional[bytes] = None):
        """
        Initialize an X25519 private key.

        Args:
            seed: Optional 32-byte seed for deterministic key generation.
                  If None, generates a random key using CSPRNG.

        Raises:
            ValueError: If seed is provided but not exactly 32 bytes.
            RuntimeError: If no backend is available.
        """
        if seed is not None and len(seed) != 32:
            raise ValueError("Seed must be exactly 32 bytes")
        
        self._use_nacl = _check_nacl()
        
        if self._use_nacl:
            import nacl.public
            if seed is not None:
                self._private_key = nacl.public.PrivateKey(seed)
            else:
                self._private_key = nacl.public.PrivateKey.generate()
        elif _check_cryptography():
            from cryptography.hazmat.primitives.asymmetric import x25519
            if seed is not None:
                self._private_key = x25519.X25519PrivateKey.from_private_bytes(seed)
            else:
                self._private_key = x25519.X25519PrivateKey.generate()
            warnings.warn(
                "PyNaCl not available, using cryptography library for X25519. "
                "For optimal performance, install PyNaCl: pip install PyNaCl",
                UserWarning,
                stacklevel=2,
            )
        else:
            raise RuntimeError(
                "No key exchange backend available. "
                "Install PyNaCl (pip install PyNaCl) or "
                "cryptography (pip install cryptography)."
            )

    def exchange(self, peer_public_key: "X25519PublicKey") -> bytes:
        """
        Perform key exchange with a peer's public key.

        Computes a shared secret using ECDH. The shared secret can be used
        to derive encryption keys using HKDF or similar KDF.

        Args:
            peer_public_key: The peer's X25519 public key

        Returns:
            32-byte shared secret

        Raises:
            TypeError: If peer_public_key is not X25519PublicKey

        Security:
            The shared secret should be passed through a KDF before use.
            Never use the raw shared secret directly as an encryption key.
        """
        if not isinstance(peer_public_key, X25519PublicKey):
            raise TypeError("peer_public_key must be X25519PublicKey")

        if self._use_nacl:
            import nacl.public
            box = nacl.public.Box(self._private_key, peer_public_key._public_key)
            return bytes(box.shared_key())
        else:
            # Using cryptography library
            return self._private_key.exchange(peer_public_key._public_key)

    def to_bytes(self) -> bytes:
        """
        Export the private key as raw bytes.

        Returns:
            32-byte private key

        Security:
            Handle with care - this is the secret key material.
            Should be encrypted before storage.
        """
        if self._use_nacl:
            return bytes(self._private_key)
        else:
            from cryptography.hazmat.primitives.serialization import (
                Encoding,
                PrivateFormat,
                NoEncryption,
            )
            return self._private_key.private_bytes(
                Encoding.Raw, PrivateFormat.Raw, NoEncryption()
            )

    def public_key(self) -> "X25519PublicKey":
        """
        Get the corresponding public key.

        Returns:
            X25519PublicKey object
        """
        if self._use_nacl:
            return X25519PublicKey(public_key=self._private_key.public_key, use_nacl=True)
        else:
            return X25519PublicKey(public_key=self._private_key.public_key(), use_nacl=False)

    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "X25519PrivateKey":
        """
        Load a private key from raw bytes.

        Args:
            key_bytes: 32-byte private key

        Returns:
            X25519PrivateKey object

        Raises:
            ValueError: If key_bytes is not exactly 32 bytes
        """
        if len(key_bytes) != 32:
            raise ValueError("Private key must be exactly 32 bytes")
        return cls(seed=key_bytes)


class X25519PublicKey:
    """
    X25519 public key for key exchange operations.

    Supports both PyNaCl and cryptography library backends.
    """

    def __init__(self, public_key=None, key_bytes: Optional[bytes] = None, use_nacl: Optional[bool] = None):
        """
        Initialize an X25519 public key.

        Args:
            public_key: Backend-specific PublicKey object
            key_bytes: Optional 32-byte public key
            use_nacl: Optional flag indicating which backend to use

        Raises:
            ValueError: If neither or both public_key and key_bytes are provided
            ValueError: If key_bytes is not exactly 32 bytes
            RuntimeError: If no backend is available
        """
        if (public_key is None) == (key_bytes is None):
            raise ValueError("Must provide either public_key or key_bytes, not both or neither")

        if use_nacl is None:
            use_nacl = _check_nacl()
        
        self._use_nacl = use_nacl

        if key_bytes is not None:
            if len(key_bytes) != 32:
                raise ValueError("Public key must be exactly 32 bytes")
            
            if self._use_nacl:
                import nacl.public
                self._public_key = nacl.public.PublicKey(key_bytes)
            elif _check_cryptography():
                from cryptography.hazmat.primitives.asymmetric import x25519
                self._public_key = x25519.X25519PublicKey.from_public_bytes(key_bytes)
            else:
                raise RuntimeError(
                    "No key exchange backend available. "
                    "Install PyNaCl (pip install PyNaCl) or "
                    "cryptography (pip install cryptography)."
                )
        else:
            self._public_key = public_key

    def to_bytes(self) -> bytes:
        """
        Export the public key as raw bytes.

        Returns:
            32-byte public key
        """
        if self._use_nacl:
            return bytes(self._public_key)
        else:
            from cryptography.hazmat.primitives.serialization import (
                Encoding,
                PublicFormat,
            )
            return self._public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

    @classmethod
    def from_bytes(cls, key_bytes: bytes) -> "X25519PublicKey":
        """
        Load a public key from raw bytes.

        Args:
            key_bytes: 32-byte public key

        Returns:
            X25519PublicKey object

        Raises:
            ValueError: If key_bytes is not exactly 32 bytes
        """
        if len(key_bytes) != 32:
            raise ValueError("Public key must be exactly 32 bytes")
        return cls(key_bytes=key_bytes)


def generate_x25519_keypair() -> Tuple[X25519PrivateKey, X25519PublicKey]:
    """
    Generate a new X25519 key pair.

    Uses CSPRNG for secure random key generation.

    Returns:
        Tuple of (private_key, public_key)

    Example:
        >>> private_key, public_key = generate_x25519_keypair()
        >>> # Share public_key with peer
        >>> # Receive peer_public_key from peer
        >>> shared_secret = private_key.exchange(peer_public_key)
    """
    private_key = X25519PrivateKey()
    public_key = private_key.public_key()
    return private_key, public_key


def perform_key_exchange(our_private_key: X25519PrivateKey, peer_public_key: X25519PublicKey) -> bytes:
    """
    Perform X25519 key exchange.

    This is a convenience function that wraps the exchange method.

    Args:
        our_private_key: Our X25519 private key
        peer_public_key: Peer's X25519 public key

    Returns:
        32-byte shared secret

    Security:
        The shared secret should be passed through a KDF (like HKDF)
        before use as an encryption key.

    Example:
        >>> alice_priv, alice_pub = generate_x25519_keypair()
        >>> bob_priv, bob_pub = generate_x25519_keypair()
        >>>
        >>> # Alice computes shared secret
        >>> alice_shared = perform_key_exchange(alice_priv, bob_pub)
        >>>
        >>> # Bob computes shared secret
        >>> bob_shared = perform_key_exchange(bob_priv, alice_pub)
        >>>
        >>> # Both compute the same shared secret
        >>> assert alice_shared == bob_shared
    """
    return our_private_key.exchange(peer_public_key)
