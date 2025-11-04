"""
DNA-Key Authentication System - Key Derivation Functions

Implements HKDF (HMAC-based Key Derivation Function) and Argon2id password hashing.

HKDF:
- RFC 5869 compliant
- Derives cryptographic keys from shared secrets
- Used for key expansion and domain separation

Argon2id:
- Winner of Password Hashing Competition
- Memory-hard algorithm (resistant to ASICs)
- Combines Argon2i and Argon2d for side-channel and GPU resistance
"""

from typing import Optional

import argon2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class KeyDerivation:
    """HKDF-based key derivation functions."""

    @staticmethod
    def derive_key(
        input_key_material: bytes,
        length: int = 32,
        salt: Optional[bytes] = None,
        info: Optional[bytes] = None,
        algorithm: str = "SHA256",
    ) -> bytes:
        """
        Derive a cryptographic key using HKDF.

        Args:
            input_key_material: Source key material (e.g., shared secret from ECDH)
            length: Length of output key in bytes (default: 32)
            salt: Optional salt value (recommended for uniqueness)
            info: Optional context/application-specific info
            algorithm: Hash algorithm to use (SHA256, SHA384, SHA512)

        Returns:
            Derived key of specified length

        Raises:
            ValueError: If length is invalid or algorithm is unsupported
            TypeError: If input_key_material is not bytes

        Security:
            - Use salt for additional randomness
            - Use info for domain separation (e.g., "dna-key-encryption-v1")
            - Never reuse the same (IKM, salt, info) combination for different purposes

        Example:
            >>> shared_secret = b"..." # from ECDH
            >>> encryption_key = KeyDerivation.derive_key(
            ...     shared_secret,
            ...     length=32,
            ...     info=b"encryption"
            ... )
        """
        if not isinstance(input_key_material, bytes):
            raise TypeError("input_key_material must be bytes")

        if length <= 0:
            raise ValueError("length must be positive")

        # Map algorithm name to cryptography hash algorithm
        hash_algorithms = {
            "SHA256": hashes.SHA256(),
            "SHA384": hashes.SHA384(),
            "SHA512": hashes.SHA512(),
            "SHA3-256": hashes.SHA3_256(),
            "SHA3-512": hashes.SHA3_512(),
        }

        if algorithm not in hash_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        hkdf = HKDF(
            algorithm=hash_algorithms[algorithm], length=length, salt=salt, info=info, backend=default_backend()
        )

        return hkdf.derive(input_key_material)

    @staticmethod
    def derive_multiple_keys(
        input_key_material: bytes,
        key_lengths: list,
        salt: Optional[bytes] = None,
        info_prefix: bytes = b"",
        algorithm: str = "SHA256",
    ) -> list:
        """
        Derive multiple keys from the same input material.

        Uses info parameter for domain separation to ensure different keys.

        Args:
            input_key_material: Source key material
            key_lengths: List of key lengths to derive
            salt: Optional salt value
            info_prefix: Prefix for info parameter
            algorithm: Hash algorithm to use

        Returns:
            List of derived keys

        Example:
            >>> shared_secret = b"..."
            >>> enc_key, mac_key = KeyDerivation.derive_multiple_keys(
            ...     shared_secret,
            ...     [32, 32],
            ...     info_prefix=b"dna-key-v1"
            ... )
        """
        keys = []
        for i, length in enumerate(key_lengths):
            info = info_prefix + f"-key-{i}".encode()
            key = KeyDerivation.derive_key(input_key_material, length=length, salt=salt, info=info, algorithm=algorithm)
            keys.append(key)
        return keys


class PasswordHashing:
    """Argon2id password hashing functions."""

    # Argon2id parameters (OWASP recommended minimums for 2023)
    TIME_COST = 2  # Number of iterations
    MEMORY_COST = 19456  # Memory in KiB (19 MiB)
    PARALLELISM = 1  # Degree of parallelism
    HASH_LENGTH = 32  # Output hash length in bytes
    SALT_LENGTH = 16  # Salt length in bytes

    def __init__(
        self,
        time_cost: int = TIME_COST,
        memory_cost: int = MEMORY_COST,
        parallelism: int = PARALLELISM,
        hash_length: int = HASH_LENGTH,
        salt_length: int = SALT_LENGTH,
    ):
        """
        Initialize Argon2id password hasher.

        Args:
            time_cost: Number of iterations
            memory_cost: Memory usage in KiB
            parallelism: Number of parallel threads
            hash_length: Length of hash output
            salt_length: Length of random salt

        Note:
            Default values follow OWASP recommendations for 2023.
            Increase time_cost and memory_cost for higher security.
        """
        self._hasher = argon2.PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_length,
            salt_len=salt_length,
            type=argon2.Type.ID,  # Argon2id
        )

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id.

        Args:
            password: Password to hash (will be encoded to UTF-8)

        Returns:
            Encoded hash string containing salt and all parameters

        Security:
            The returned hash includes all parameters and the salt,
            so it can be verified later without storing them separately.

        Example:
            >>> hasher = PasswordHashing()
            >>> password_hash = hasher.hash_password("user_password")
            >>> # Store password_hash in database
        """
        return self._hasher.hash(password)

    def verify_password(self, password_hash: str, password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password_hash: Previously hashed password
            password: Password to verify

        Returns:
            True if password matches, False otherwise

        Security:
            Uses constant-time comparison to prevent timing attacks.

        Example:
            >>> hasher = PasswordHashing()
            >>> is_valid = hasher.verify_password(stored_hash, user_input)
        """
        try:
            self._hasher.verify(password_hash, password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
        except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHashError):
            # Invalid hash format or other verification error
            return False

    def needs_rehash(self, password_hash: str) -> bool:
        """
        Check if a password hash needs to be rehashed.

        This is useful when updating security parameters.
        If this returns True, verify the password and generate a new hash.

        Args:
            password_hash: Previously hashed password

        Returns:
            True if hash should be updated with current parameters

        Example:
            >>> if hasher.needs_rehash(stored_hash):
            ...     if hasher.verify_password(stored_hash, password):
            ...         new_hash = hasher.hash_password(password)
            ...         # Update database with new_hash
        """
        try:
            return self._hasher.check_needs_rehash(password_hash)
        except (argon2.exceptions.InvalidHashError, ValueError):
            # If we can't parse the hash, it definitely needs rehashing
            return True


def hash_password(password: str) -> str:
    """
    Convenience function to hash a password with default parameters.

    Args:
        password: Password to hash

    Returns:
        Argon2id hash string

    Example:
        >>> from server.crypto.hashing import hash_password, verify_password
        >>> password_hash = hash_password("user_password")
        >>> assert verify_password(password_hash, "user_password")
    """
    hasher = PasswordHashing()
    return hasher.hash_password(password)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Convenience function to verify a password.

    Args:
        password_hash: Previously hashed password
        password: Password to verify

    Returns:
        True if password matches, False otherwise
    """
    hasher = PasswordHashing()
    return hasher.verify_password(password_hash, password)
