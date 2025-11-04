"""
DNA-Key Authentication System - X25519 Key Exchange

Implements X25519 Elliptic Curve Diffie-Hellman (ECDH) key exchange using PyNaCl.
X25519 provides:
- 128-bit security level (256-bit keys)
- Fast key exchange operations
- Ephemeral key generation for forward secrecy
- Shared secret derivation

Reference: RFC 7748 - Elliptic Curves for Security
"""

from typing import Optional, Tuple

import nacl.encoding
import nacl.exceptions
import nacl.public


class X25519PrivateKey:
    """
    X25519 private key for key exchange operations.

    Wraps PyNaCl's PrivateKey with additional validation and helpers.
    """

    def __init__(self, seed: Optional[bytes] = None):
        """
        Initialize an X25519 private key.

        Args:
            seed: Optional 32-byte seed for deterministic key generation.
                  If None, generates a random key using CSPRNG.

        Raises:
            ValueError: If seed is provided but not exactly 32 bytes.
        """
        if seed is not None:
            if len(seed) != 32:
                raise ValueError("Seed must be exactly 32 bytes")
            self._private_key = nacl.public.PrivateKey(seed)
        else:
            self._private_key = nacl.public.PrivateKey.generate()

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

        box = nacl.public.Box(self._private_key, peer_public_key._public_key)
        # Use the shared key from the box (32 bytes)
        return bytes(box.shared_key())

    def to_bytes(self) -> bytes:
        """
        Export the private key as raw bytes.

        Returns:
            32-byte private key

        Security:
            Handle with care - this is the secret key material.
            Should be encrypted before storage.
        """
        return bytes(self._private_key)

    def public_key(self) -> "X25519PublicKey":
        """
        Get the corresponding public key.

        Returns:
            X25519PublicKey object
        """
        return X25519PublicKey(public_key=self._private_key.public_key)

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

    Wraps PyNaCl's PublicKey with additional validation and helpers.
    """

    def __init__(self, public_key: Optional[nacl.public.PublicKey] = None, key_bytes: Optional[bytes] = None):
        """
        Initialize an X25519 public key.

        Args:
            public_key: PyNaCl PublicKey object
            key_bytes: Optional 32-byte public key

        Raises:
            ValueError: If neither or both parameters are provided
            ValueError: If key_bytes is not exactly 32 bytes
        """
        if (public_key is None) == (key_bytes is None):
            raise ValueError("Must provide either public_key or key_bytes, not both or neither")

        if key_bytes is not None:
            if len(key_bytes) != 32:
                raise ValueError("Public key must be exactly 32 bytes")
            self._public_key = nacl.public.PublicKey(key_bytes)
        else:
            self._public_key = public_key

    def to_bytes(self) -> bytes:
        """
        Export the public key as raw bytes.

        Returns:
            32-byte public key
        """
        return bytes(self._public_key)

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
