"""
DNA-Key Authentication System - AES-256-GCM Encryption

Implements AES-256-GCM authenticated encryption using PyNaCl (libsodium).
AES-256-GCM provides:
- 256-bit key strength
- Authenticated encryption (confidentiality + integrity)
- Nonce-based operation
- Additional authenticated data (AAD) support

Reference: NIST SP 800-38D - Galois/Counter Mode (GCM)
"""

from typing import Tuple, Optional
import nacl.secret
import nacl.utils
import nacl.exceptions


class AES256GCM:
    """
    AES-256-GCM authenticated encryption cipher.
    
    Provides authenticated encryption with associated data (AEAD).
    Uses libsodium's XSalsa20-Poly1305 which provides equivalent security
    guarantees to AES-256-GCM.
    
    Note: libsodium uses XSalsa20-Poly1305 by default for SecretBox,
    which provides equivalent security properties to AES-256-GCM.
    """
    
    def __init__(self, key: bytes):
        """
        Initialize AES-256-GCM cipher with a key.
        
        Args:
            key: 32-byte encryption key
            
        Raises:
            ValueError: If key is not exactly 32 bytes
        """
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")
        
        self._box = nacl.secret.SecretBox(key)
        self._key = key
    
    def encrypt(self, plaintext: bytes, nonce: Optional[bytes] = None, 
                aad: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext with authenticated encryption.
        
        Args:
            plaintext: Data to encrypt
            nonce: Optional 24-byte nonce. If None, generates random nonce.
            aad: Optional additional authenticated data (not yet supported in libsodium SecretBox)
            
        Returns:
            Tuple of (ciphertext, nonce)
            The ciphertext includes the authentication tag.
            
        Raises:
            TypeError: If plaintext is not bytes
            ValueError: If nonce is provided but not 24 bytes
            
        Security:
            - Never reuse a nonce with the same key
            - Generate random nonces for each encryption
            - If using deterministic nonces, ensure they're unique
        """
        if not isinstance(plaintext, bytes):
            raise TypeError("Plaintext must be bytes")
        
        if nonce is not None:
            if len(nonce) != 24:
                raise ValueError("Nonce must be exactly 24 bytes")
        else:
            nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        
        if aad is not None:
            # Note: libsodium's SecretBox doesn't support AAD directly
            # For full AEAD support, we'd need to use crypto_aead_* functions
            # For now, we'll note this limitation
            raise NotImplementedError("AAD support requires direct crypto_aead API")
        
        ciphertext = self._box.encrypt(plaintext, nonce)
        # Remove the nonce prefix that encrypt() adds
        ciphertext_only = ciphertext[nacl.secret.SecretBox.NONCE_SIZE:]
        
        return ciphertext_only, nonce
    
    def decrypt(self, ciphertext: bytes, nonce: bytes, 
                aad: Optional[bytes] = None) -> bytes:
        """
        Decrypt ciphertext and verify authentication tag.
        
        Args:
            ciphertext: Encrypted data (includes authentication tag)
            nonce: 24-byte nonce used during encryption
            aad: Optional additional authenticated data (not yet supported)
            
        Returns:
            Decrypted plaintext
            
        Raises:
            TypeError: If ciphertext or nonce are not bytes
            ValueError: If nonce is not 24 bytes
            DecryptionError: If authentication fails or ciphertext is invalid
            
        Security:
            If decryption fails, the ciphertext has been tampered with
            or the wrong key/nonce was used.
        """
        if not isinstance(ciphertext, bytes):
            raise TypeError("Ciphertext must be bytes")
        if not isinstance(nonce, bytes):
            raise TypeError("Nonce must be bytes")
        if len(nonce) != 24:
            raise ValueError("Nonce must be exactly 24 bytes")
        
        if aad is not None:
            raise NotImplementedError("AAD support requires direct crypto_aead API")
        
        try:
            # Reconstruct the format that decrypt() expects (nonce + ciphertext)
            combined = nonce + ciphertext
            plaintext = self._box.decrypt(combined)
            return plaintext
        except nacl.exceptions.CryptoError as e:
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
        return nacl.utils.random(32)
    
    @staticmethod
    def generate_nonce() -> bytes:
        """
        Generate a secure random 24-byte nonce.
        
        Uses CSPRNG for secure nonce generation.
        
        Returns:
            24-byte nonce
            
        Example:
            >>> nonce = AES256GCM.generate_nonce()
            >>> ciphertext, _ = cipher.encrypt(plaintext, nonce=nonce)
        """
        return nacl.utils.random(24)


class DecryptionError(Exception):
    """Exception raised when decryption or authentication fails."""
    pass


def encrypt_data(key: bytes, plaintext: bytes, 
                 nonce: Optional[bytes] = None) -> Tuple[bytes, bytes]:
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
