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
DNA-Key Authentication System - Crypto Backend with Fallbacks

Provides cryptographic signing and verification with optional PyNaCl support.
Falls back to Python's cryptography library when PyNaCl is not available.

Security Note:
    Production deployments should always use PyNaCl for optimal security.
    The fallback mode uses the cryptography library which is also secure
    but PyNaCl (libsodium) is preferred for its constant-time implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import warnings


# Track which backend is available
_NACL_AVAILABLE: Optional[bool] = None
_CRYPTOGRAPHY_AVAILABLE: Optional[bool] = None


def _check_nacl() -> bool:
    """Check if PyNaCl is available."""
    global _NACL_AVAILABLE
    if _NACL_AVAILABLE is None:
        try:
            import nacl.signing  # noqa: F401
            import nacl.exceptions  # noqa: F401
            _NACL_AVAILABLE = True
        except ImportError:
            _NACL_AVAILABLE = False
    return _NACL_AVAILABLE


def _check_cryptography() -> bool:
    """Check if cryptography library is available."""
    global _CRYPTOGRAPHY_AVAILABLE
    if _CRYPTOGRAPHY_AVAILABLE is None:
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519  # noqa: F401
            _CRYPTOGRAPHY_AVAILABLE = True
        except ImportError:
            _CRYPTOGRAPHY_AVAILABLE = False
    return _CRYPTOGRAPHY_AVAILABLE


class SignerBackend(ABC):
    """Abstract base class for cryptographic signing backends."""

    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        """
        Sign data with the private key.

        Args:
            data: The data to sign.

        Returns:
            The signature bytes.
        """
        pass

    @abstractmethod
    def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify a signature on data.

        Args:
            data: The original data.
            signature: The signature to verify.

        Returns:
            True if signature is valid, False otherwise.
        """
        pass

    @abstractmethod
    def get_public_key(self) -> bytes:
        """
        Get the public key bytes.

        Returns:
            The public key as bytes.
        """
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        """
        Export the private key as raw bytes.

        Returns:
            The private key as bytes (32 bytes for Ed25519).
        """
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Return the name of the backend being used."""
        pass


class PyNaClSigner(SignerBackend):
    """
    Ed25519 signer using PyNaCl (libsodium).

    This is the preferred backend for production use due to libsodium's
    constant-time implementations and extensive security auditing.
    """

    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize PyNaCl signer.

        Args:
            private_key: Optional 32-byte seed for the signing key.
                        If None, generates a random key.

        Raises:
            ImportError: If PyNaCl is not installed.
            ValueError: If private_key is provided but not 32 bytes.
        """
        try:
            from nacl.signing import SigningKey
        except ImportError as e:
            raise ImportError(
                "PyNaCl is not installed. Install it with: pip install PyNaCl"
            ) from e

        if private_key is not None:
            if len(private_key) != 32:
                raise ValueError("Private key must be exactly 32 bytes")
            self._signing_key = SigningKey(private_key)
        else:
            self._signing_key = SigningKey.generate()

        self._verify_key = self._signing_key.verify_key

    def sign(self, data: bytes) -> bytes:
        """Sign data and return the signature."""
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")

        signed = self._signing_key.sign(data)
        return signed.signature

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify a signature on data."""
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        if len(signature) != 64:
            raise ValueError("Signature must be exactly 64 bytes")

        try:
            from nacl.exceptions import BadSignatureError
            self._verify_key.verify(data, signature)
            return True
        except BadSignatureError:
            return False

    def get_public_key(self) -> bytes:
        """Get the public key bytes."""
        return bytes(self._verify_key)

    def to_bytes(self) -> bytes:
        """Export the private key as raw bytes."""
        return bytes(self._signing_key)

    @property
    def backend_name(self) -> str:
        return "PyNaCl (libsodium)"


class CryptographySigner(SignerBackend):
    """
    Ed25519 signer using the cryptography library.

    This is a fallback backend when PyNaCl is not available.
    It provides equivalent security but PyNaCl is preferred.
    """

    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize cryptography-based signer.

        Args:
            private_key: Optional 32-byte seed for the signing key.
                        If None, generates a random key.

        Raises:
            ImportError: If cryptography is not installed.
            ValueError: If private_key is provided but not 32 bytes.
        """
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519
        except ImportError as e:
            raise ImportError(
                "cryptography is not installed. Install it with: pip install cryptography"
            ) from e

        if private_key is not None:
            if len(private_key) != 32:
                raise ValueError("Private key must be exactly 32 bytes")
            self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        else:
            self._private_key = ed25519.Ed25519PrivateKey.generate()

        self._public_key = self._private_key.public_key()

    def sign(self, data: bytes) -> bytes:
        """Sign data and return the signature."""
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")

        return self._private_key.sign(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify a signature on data."""
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes")
        if not isinstance(signature, bytes):
            raise TypeError("Signature must be bytes")
        if len(signature) != 64:
            raise ValueError("Signature must be exactly 64 bytes")

        try:
            from cryptography.exceptions import InvalidSignature
            self._public_key.verify(signature, data)
            return True
        except InvalidSignature:
            return False

    def get_public_key(self) -> bytes:
        """Get the public key bytes."""
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            PublicFormat,
        )
        return self._public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

    def to_bytes(self) -> bytes:
        """Export the private key as raw bytes."""
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            PrivateFormat,
            NoEncryption,
        )
        return self._private_key.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption()
        )

    @property
    def backend_name(self) -> str:
        return "cryptography"


class DisabledSigner(SignerBackend):
    """
    Fallback signer that refuses to operate.

    Used when no secure signing backend is available. Raises clear errors
    rather than silently failing or providing insecure operations.
    """

    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize disabled signer.

        Note: Does not raise on init, but all operations will raise RuntimeError.
        """
        self._error_message = (
            "No secure signing backend available. "
            "Please install PyNaCl (pip install PyNaCl) or "
            "cryptography (pip install cryptography) to enable signing."
        )

    def sign(self, data: bytes) -> bytes:
        raise RuntimeError(self._error_message)

    def verify(self, data: bytes, signature: bytes) -> bool:
        raise RuntimeError(self._error_message)

    def get_public_key(self) -> bytes:
        raise RuntimeError(self._error_message)

    def to_bytes(self) -> bytes:
        """Export the private key - not available for disabled signer."""
        raise RuntimeError(self._error_message)

    @property
    def backend_name(self) -> str:
        return "disabled"


def get_signer_backend(private_key: Optional[bytes] = None) -> SignerBackend:
    """
    Get the best available signing backend.

    Attempts to use PyNaCl first, falls back to cryptography library,
    and returns a disabled signer if neither is available.

    Args:
        private_key: Optional 32-byte private key seed.

    Returns:
        A SignerBackend instance. If no backend is available, returns
        a DisabledSigner that will raise RuntimeError when used.

    Example:
        >>> signer = get_signer_backend()
        >>> signature = signer.sign(b"Hello, World!")
        >>> assert signer.verify(b"Hello, World!", signature)
    """
    # Try PyNaCl first (preferred)
    if _check_nacl():
        return PyNaClSigner(private_key)

    # Fall back to cryptography
    if _check_cryptography():
        warnings.warn(
            "PyNaCl not available, using cryptography library as fallback. "
            "For optimal security, install PyNaCl: pip install PyNaCl",
            UserWarning,
            stacklevel=2,
        )
        return CryptographySigner(private_key)

    # No backend available - return disabled signer that will error on use
    warnings.warn(
        "No crypto backend available. Signing operations will fail. "
        "Install PyNaCl or cryptography to enable signing.",
        UserWarning,
        stacklevel=2,
    )
    return DisabledSigner(private_key)


def generate_keypair() -> Tuple[bytes, bytes]:
    """
    Generate a new Ed25519 keypair using the best available backend.

    Returns:
        Tuple of (private_key_bytes, public_key_bytes).

    Raises:
        RuntimeError: If no signing backend is available.

    Example:
        >>> private_key, public_key = generate_keypair()
        >>> len(private_key) == 32
        True
        >>> len(public_key) == 32
        True
    """
    signer = get_signer_backend()
    return signer.to_bytes(), signer.get_public_key()


def is_nacl_available() -> bool:
    """
    Check if PyNaCl is available.

    Returns:
        True if PyNaCl is installed and importable.
    """
    return _check_nacl()


def is_cryptography_available() -> bool:
    """
    Check if the cryptography library is available.

    Returns:
        True if cryptography is installed and importable.
    """
    return _check_cryptography()


def get_available_backends() -> list:
    """
    Get list of available signing backends.

    Returns:
        List of available backend names.
    """
    backends = []
    if _check_nacl():
        backends.append("PyNaCl")
    if _check_cryptography():
        backends.append("cryptography")
    return backends
