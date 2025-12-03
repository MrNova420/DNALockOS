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
DNA-Key Authentication System - AES-256-GCM Encryption

Implements AES-256-GCM authenticated encryption using PyNaCl (libsodium) with
fallback to cryptography library when PyNaCl is unavailable.

AES-256-GCM provides:
- 256-bit key strength
- Authenticated encryption (confidentiality + integrity)
- Nonce-based operation
- Additional authenticated data (AAD) support

Reference: NIST SP 800-38D - Galois/Counter Mode (GCM)
"""

import os
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
            import nacl.secret  # noqa: F401
            _NACL_AVAILABLE = True
        except ImportError:
            _NACL_AVAILABLE = False
    return _NACL_AVAILABLE


def _check_cryptography() -> bool:
    """Check if cryptography library is available."""
    global _CRYPTOGRAPHY_AVAILABLE
    if _CRYPTOGRAPHY_AVAILABLE is None:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: F401
            _CRYPTOGRAPHY_AVAILABLE = True
        except ImportError:
            _CRYPTOGRAPHY_AVAILABLE = False
    return _CRYPTOGRAPHY_AVAILABLE


class AES256GCM:
    """
    AES-256-GCM authenticated encryption cipher.

    Provides authenticated encryption with associated data (AEAD).
    
    Uses PyNaCl's XSalsa20-Poly1305 (equivalent security to AES-256-GCM) when available,
    falls back to cryptography library's AES-256-GCM when PyNaCl is not available.
    """

    def __init__(self, key: bytes):
        """
        Initialize AES-256-GCM cipher with a key.

        Args:
            key: 32-byte encryption key

        Raises:
            ValueError: If key is not exactly 32 bytes
            RuntimeError: If no encryption backend is available
        """
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")

        self._key = key
        self._use_nacl = _check_nacl()
        
        if self._use_nacl:
            import nacl.secret
            self._box = nacl.secret.SecretBox(key)
        elif _check_cryptography():
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            self._cipher = AESGCM(key)
            warnings.warn(
                "PyNaCl not available, using cryptography library for AES-256-GCM. "
                "For optimal security and performance, install PyNaCl: pip install PyNaCl",
                UserWarning,
                stacklevel=2,
            )
        else:
            raise RuntimeError(
                "No encryption backend available. "
                "Install PyNaCl (pip install PyNaCl) or "
                "cryptography (pip install cryptography)."
            )

    def encrypt(
        self, plaintext: bytes, nonce: Optional[bytes] = None, aad: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext with authenticated encryption.

        Args:
            plaintext: Data to encrypt
            nonce: Optional nonce. If None, generates random nonce.
                   For PyNaCl: 24 bytes. For AES-GCM: 12 bytes.
            aad: Optional additional authenticated data (supported in AES-GCM backend only)

        Returns:
            Tuple of (ciphertext, nonce)
            The ciphertext includes the authentication tag.

        Raises:
            TypeError: If plaintext is not bytes
            ValueError: If nonce is provided but wrong size

        Security:
            - Never reuse a nonce with the same key
            - Generate random nonces for each encryption
            - If using deterministic nonces, ensure they're unique
        """
        if not isinstance(plaintext, bytes):
            raise TypeError("Plaintext must be bytes")

        if self._use_nacl:
            import nacl.secret
            import nacl.utils
            
            if nonce is not None:
                if len(nonce) != 24:
                    raise ValueError("Nonce must be exactly 24 bytes for PyNaCl backend")
            else:
                nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

            if aad is not None:
                raise NotImplementedError("AAD support requires AES-GCM backend")

            ciphertext = self._box.encrypt(plaintext, nonce)
            # Remove the nonce prefix that encrypt() adds
            ciphertext_only = ciphertext[nacl.secret.SecretBox.NONCE_SIZE:]
            return ciphertext_only, nonce
        else:
            # Using cryptography library's AES-GCM
            if nonce is not None:
                if len(nonce) != 12:
                    raise ValueError("Nonce must be exactly 12 bytes for AES-GCM backend")
            else:
                nonce = os.urandom(12)  # AES-GCM standard nonce size
            
            ciphertext = self._cipher.encrypt(nonce, plaintext, aad)
            return ciphertext, nonce

    def decrypt(self, ciphertext: bytes, nonce: bytes, aad: Optional[bytes] = None) -> bytes:
        """
        Decrypt ciphertext and verify authentication tag.

        Args:
            ciphertext: Encrypted data (includes authentication tag)
            nonce: Nonce used during encryption (24 bytes for PyNaCl, 12 bytes for AES-GCM)
            aad: Optional additional authenticated data (supported in AES-GCM backend only)

        Returns:
            Decrypted plaintext

        Raises:
            TypeError: If ciphertext or nonce are not bytes
            ValueError: If nonce is wrong size
            DecryptionError: If authentication fails or ciphertext is invalid

        Security:
            If decryption fails, the ciphertext has been tampered with
            or the wrong key/nonce was used.
        """
        if not isinstance(ciphertext, bytes):
            raise TypeError("Ciphertext must be bytes")
        if not isinstance(nonce, bytes):
            raise TypeError("Nonce must be bytes")

        if self._use_nacl:
            import nacl.exceptions
            
            if len(nonce) != 24:
                raise ValueError("Nonce must be exactly 24 bytes for PyNaCl backend")
            
            if aad is not None:
                raise NotImplementedError("AAD support requires AES-GCM backend")
            
            # Validate minimum ciphertext length (must include authentication tag)
            # XSalsa20-Poly1305 has a 16-byte tag
            if len(ciphertext) < 16:
                raise ValueError("Ciphertext too short - must include authentication tag")

            try:
                # Reconstruct the format that decrypt() expects (nonce + ciphertext)
                combined = nonce + ciphertext
                plaintext = self._box.decrypt(combined)
                return plaintext
            except nacl.exceptions.CryptoError as e:
                raise DecryptionError("Decryption failed: authentication tag mismatch or invalid ciphertext") from e
        else:
            # Using cryptography library's AES-GCM
            if len(nonce) != 12:
                raise ValueError("Nonce must be exactly 12 bytes for AES-GCM backend")
            
            try:
                from cryptography.exceptions import InvalidTag
                plaintext = self._cipher.decrypt(nonce, ciphertext, aad)
                return plaintext
            except InvalidTag as e:
                raise DecryptionError("Decryption failed: authentication tag mismatch or invalid ciphertext") from e

    @classmethod
    def generate_key(cls) -> bytes:
        """
        Generate a secure random 32-byte key.

        Uses CSPRNG for secure key generation.

        Returns:
            32-byte encryption key

        Example:
            >>> key = AES256GCM.generate_key()
            >>> cipher = AES256GCM(key)
        """
        if _check_nacl():
            import nacl.utils
            return nacl.utils.random(32)
        else:
            return os.urandom(32)

    @staticmethod
    def generate_nonce() -> bytes:
        """
        Generate a secure random nonce.

        Uses CSPRNG for secure nonce generation.
        Returns 24 bytes for PyNaCl backend, 12 bytes for AES-GCM backend.

        Returns:
            Nonce bytes (size depends on backend)

        Example:
            >>> nonce = AES256GCM.generate_nonce()
            >>> ciphertext, _ = cipher.encrypt(plaintext, nonce=nonce)
        """
        if _check_nacl():
            import nacl.utils
            return nacl.utils.random(24)
        else:
            return os.urandom(12)  # AES-GCM standard nonce size


class DecryptionError(Exception):
    """Exception raised when decryption or authentication fails."""

    pass


def encrypt_data(key: bytes, plaintext: bytes, nonce: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Convenience function for authenticated encryption.

    Args:
        key: 32-byte encryption key
        plaintext: Data to encrypt
        nonce: Optional 24-byte nonce

    Returns:
        Tuple of (ciphertext, nonce)

    Example:
        >>> key = AES256GCM.generate_key()
        >>> ciphertext, nonce = encrypt_data(key, b"Secret message")
        >>> plaintext = decrypt_data(key, ciphertext, nonce)
        >>> assert plaintext == b"Secret message"
    """
    cipher = AES256GCM(key)
    return cipher.encrypt(plaintext, nonce)


def decrypt_data(key: bytes, ciphertext: bytes, nonce: bytes) -> bytes:
    """
    Convenience function for authenticated decryption.

    Args:
        key: 32-byte encryption key
        ciphertext: Encrypted data
        nonce: 24-byte nonce used during encryption

    Returns:
        Decrypted plaintext

    Raises:
        DecryptionError: If decryption or authentication fails
    """
    cipher = AES256GCM(key)
    return cipher.decrypt(ciphertext, nonce)
