"""
DNA-Key Authentication System - Key Derivation and Hashing Tests

Comprehensive test suite for HKDF and Argon2id implementations.
Tests cover:
- HKDF key derivation
- Multiple key derivation
- Argon2id password hashing
- Password verification
- Edge cases and error handling
- Security properties
"""

import pytest
from server.crypto.hashing import (
    KeyDerivation,
    PasswordHashing,
    hash_password,
    verify_password
)


class TestHKDFKeyDerivation:
    """Test HKDF key derivation functions."""
    
    def test_derive_key_basic(self):
        """Test basic key derivation."""
        ikm = b"input key material"
        derived = KeyDerivation.derive_key(ikm)
        
        assert isinstance(derived, bytes)
        assert len(derived) == 32  # Default length
    
    def test_derive_key_custom_length(self):
        """Test key derivation with custom length."""
        ikm = b"input key material"
        
        for length in [16, 32, 48, 64]:
            derived = KeyDerivation.derive_key(ikm, length=length)
            assert len(derived) == length
    
    def test_derive_key_with_salt(self):
        """Test key derivation with salt."""
        ikm = b"input key material"
        salt = b"unique salt"
        
        derived1 = KeyDerivation.derive_key(ikm, salt=salt)
        derived2 = KeyDerivation.derive_key(ikm, salt=salt)
        
        assert derived1 == derived2
    
    def test_derive_key_different_salts(self):
        """Test that different salts produce different keys."""
        ikm = b"input key material"
        
        derived1 = KeyDerivation.derive_key(ikm, salt=b"salt1")
        derived2 = KeyDerivation.derive_key(ikm, salt=b"salt2")
        
        assert derived1 != derived2
    
    def test_derive_key_with_info(self):
        """Test key derivation with context info."""
        ikm = b"input key material"
        
        derived1 = KeyDerivation.derive_key(ikm, info=b"encryption")
        derived2 = KeyDerivation.derive_key(ikm, info=b"authentication")
        
        assert derived1 != derived2
    
    def test_derive_key_different_algorithms(self):
        """Test key derivation with different hash algorithms."""
        ikm = b"input key material"
        
        sha256 = KeyDerivation.derive_key(ikm, algorithm="SHA256")
        sha384 = KeyDerivation.derive_key(ikm, algorithm="SHA384")
        sha512 = KeyDerivation.derive_key(ikm, algorithm="SHA512")
        
        # Different algorithms should produce different keys
        assert sha256 != sha384
        assert sha384 != sha512
        assert sha256 != sha512
    
    def test_derive_key_sha3(self):
        """Test key derivation with SHA3 algorithms."""
        ikm = b"input key material"
        
        sha3_256 = KeyDerivation.derive_key(ikm, algorithm="SHA3-256")
        sha3_512 = KeyDerivation.derive_key(ikm, algorithm="SHA3-512")
        
        assert isinstance(sha3_256, bytes)
        assert isinstance(sha3_512, bytes)
        assert sha3_256 != sha3_512
    
    def test_derive_key_deterministic(self):
        """Test that key derivation is deterministic."""
        ikm = b"input key material"
        salt = b"salt"
        info = b"context"
        
        derived1 = KeyDerivation.derive_key(ikm, salt=salt, info=info)
        derived2 = KeyDerivation.derive_key(ikm, salt=salt, info=info)
        
        assert derived1 == derived2
    
    def test_derive_key_non_bytes_raises_error(self):
        """Test that non-bytes input raises TypeError."""
        with pytest.raises(TypeError, match="input_key_material must be bytes"):
            KeyDerivation.derive_key("not bytes")
    
    def test_derive_key_invalid_length_raises_error(self):
        """Test that invalid length raises ValueError."""
        ikm = b"input key material"
        
        with pytest.raises(ValueError, match="length must be positive"):
            KeyDerivation.derive_key(ikm, length=0)
        
        with pytest.raises(ValueError, match="length must be positive"):
            KeyDerivation.derive_key(ikm, length=-1)
    
    def test_derive_key_unsupported_algorithm_raises_error(self):
        """Test that unsupported algorithm raises ValueError."""
        ikm = b"input key material"
        
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            KeyDerivation.derive_key(ikm, algorithm="MD5")


class TestMultipleKeyDerivation:
    """Test deriving multiple keys from single input."""
    
    def test_derive_multiple_keys(self):
        """Test deriving multiple keys."""
        ikm = b"shared secret"
        lengths = [32, 32, 16]
        
        keys = KeyDerivation.derive_multiple_keys(ikm, lengths)
        
        assert len(keys) == 3
        assert len(keys[0]) == 32
        assert len(keys[1]) == 32
        assert len(keys[2]) == 16
    
    def test_derived_keys_are_different(self):
        """Test that derived keys are all different."""
        ikm = b"shared secret"
        lengths = [32, 32, 32]
        
        keys = KeyDerivation.derive_multiple_keys(ikm, lengths)
        
        # All keys should be different
        assert keys[0] != keys[1]
        assert keys[1] != keys[2]
        assert keys[0] != keys[2]
    
    def test_derive_multiple_keys_with_prefix(self):
        """Test deriving multiple keys with info prefix."""
        ikm = b"shared secret"
        lengths = [32, 32]
        
        keys1 = KeyDerivation.derive_multiple_keys(ikm, lengths, info_prefix=b"app1")
        keys2 = KeyDerivation.derive_multiple_keys(ikm, lengths, info_prefix=b"app2")
        
        # Different prefixes should produce different keys
        assert keys1[0] != keys2[0]
        assert keys1[1] != keys2[1]
    
    def test_derive_multiple_keys_deterministic(self):
        """Test that multiple key derivation is deterministic."""
        ikm = b"shared secret"
        lengths = [32, 16, 24]
        
        keys1 = KeyDerivation.derive_multiple_keys(ikm, lengths)
        keys2 = KeyDerivation.derive_multiple_keys(ikm, lengths)
        
        assert keys1 == keys2


class TestArgon2idPasswordHashing:
    """Test Argon2id password hashing."""
    
    def test_hash_password(self):
        """Test hashing a password."""
        hasher = PasswordHashing()
        password = "test_password_123"
        
        password_hash = hasher.hash_password(password)
        
        assert isinstance(password_hash, str)
        assert len(password_hash) > 0
        assert password_hash != password
    
    def test_hash_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hasher = PasswordHashing()
        
        hash1 = hasher.hash_password("password1")
        hash2 = hasher.hash_password("password2")
        
        assert hash1 != hash2
    
    def test_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (random salt)."""
        hasher = PasswordHashing()
        password = "same_password"
        
        hash1 = hasher.hash_password(password)
        hash2 = hasher.hash_password(password)
        
        # Different salts should produce different hashes
        assert hash1 != hash2
    
    def test_verify_correct_password(self):
        """Test verifying a correct password."""
        hasher = PasswordHashing()
        password = "correct_password"
        
        password_hash = hasher.hash_password(password)
        result = hasher.verify_password(password_hash, password)
        
        assert result is True
    
    def test_verify_incorrect_password(self):
        """Test verifying an incorrect password."""
        hasher = PasswordHashing()
        password = "correct_password"
        
        password_hash = hasher.hash_password(password)
        result = hasher.verify_password(password_hash, "wrong_password")
        
        assert result is False
    
    def test_verify_empty_password(self):
        """Test hashing and verifying empty password."""
        hasher = PasswordHashing()
        password = ""
        
        password_hash = hasher.hash_password(password)
        result = hasher.verify_password(password_hash, password)
        
        assert result is True
    
    def test_verify_long_password(self):
        """Test hashing and verifying long password."""
        hasher = PasswordHashing()
        password = "x" * 1000
        
        password_hash = hasher.hash_password(password)
        result = hasher.verify_password(password_hash, password)
        
        assert result is True
    
    def test_verify_unicode_password(self):
        """Test hashing and verifying Unicode password."""
        hasher = PasswordHashing()
        password = "пароль密码🔐"
        
        password_hash = hasher.hash_password(password)
        result = hasher.verify_password(password_hash, password)
        
        assert result is True
    
    def test_verify_invalid_hash(self):
        """Test verifying with invalid hash format."""
        hasher = PasswordHashing()
        
        result = hasher.verify_password("invalid_hash", "password")
        
        assert result is False
    
    def test_needs_rehash(self):
        """Test checking if hash needs rehashing."""
        hasher = PasswordHashing()
        password = "test_password"
        
        password_hash = hasher.hash_password(password)
        needs_rehash = hasher.needs_rehash(password_hash)
        
        # With same parameters, shouldn't need rehash
        assert needs_rehash is False
    
    def test_needs_rehash_different_parameters(self):
        """Test that different parameters trigger rehash."""
        hasher1 = PasswordHashing(time_cost=2, memory_cost=19456)
        hasher2 = PasswordHashing(time_cost=3, memory_cost=19456)
        
        password_hash = hasher1.hash_password("password")
        needs_rehash = hasher2.needs_rehash(password_hash)
        
        assert needs_rehash is True
    
    def test_needs_rehash_invalid_hash(self):
        """Test that invalid hash triggers rehash."""
        hasher = PasswordHashing()
        
        needs_rehash = hasher.needs_rehash("invalid_hash")
        
        assert needs_rehash is True
    
    def test_custom_parameters(self):
        """Test hashing with custom parameters."""
        hasher = PasswordHashing(
            time_cost=3,
            memory_cost=65536,
            parallelism=2,
            hash_length=64,
            salt_length=32
        )
        
        password_hash = hasher.hash_password("password")
        result = hasher.verify_password(password_hash, "password")
        
        assert result is True


class TestPasswordHashingConvenienceFunctions:
    """Test convenience functions for password hashing."""
    
    def test_hash_password_function(self):
        """Test hash_password convenience function."""
        password = "test_password"
        
        password_hash = hash_password(password)
        
        assert isinstance(password_hash, str)
        assert len(password_hash) > 0
    
    def test_verify_password_function(self):
        """Test verify_password convenience function."""
        password = "test_password"
        
        password_hash = hash_password(password)
        result = verify_password(password_hash, password)
        
        assert result is True
    
    def test_verify_wrong_password_function(self):
        """Test verify_password with wrong password."""
        password = "test_password"
        
        password_hash = hash_password(password)
        result = verify_password(password_hash, "wrong_password")
        
        assert result is False


class TestSecurityProperties:
    """Test security properties of hashing implementations."""
    
    def test_hkdf_different_ikm_different_output(self):
        """Test that different input material produces different output."""
        derived1 = KeyDerivation.derive_key(b"ikm1")
        derived2 = KeyDerivation.derive_key(b"ikm2")
        
        assert derived1 != derived2
    
    def test_password_hash_is_not_reversible(self):
        """Test that password hash doesn't reveal password."""
        password = "my_secret_password"
        password_hash = hash_password(password)
        
        # Hash shouldn't contain the password
        assert password not in password_hash
        assert password.encode() not in password_hash.encode()
    
    def test_timing_attack_resistance(self):
        """Test that verification is timing-attack resistant."""
        hasher = PasswordHashing()
        password = "test_password"
        password_hash = hasher.hash_password(password)
        
        # Both correct and incorrect passwords should take similar time
        # This is a simple test - real timing analysis would be more complex
        import time
        
        start = time.time()
        hasher.verify_password(password_hash, password)
        time_correct = time.time() - start
        
        start = time.time()
        hasher.verify_password(password_hash, "wrong_password")
        time_incorrect = time.time() - start
        
        # Times should be in the same order of magnitude
        assert abs(time_correct - time_incorrect) < 1.0  # Within 1 second
