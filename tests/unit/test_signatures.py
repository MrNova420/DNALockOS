"""
DNA-Key Authentication System - Ed25519 Signature Tests

Comprehensive test suite for Ed25519 digital signature implementation.
Tests cover:
- Key generation
- Signing and verification
- Edge cases and error handling
- Key serialization/deserialization
- Security properties
"""

import pytest
from server.crypto.signatures import (
    Ed25519SigningKey,
    Ed25519VerifyKey,
    generate_ed25519_keypair
)


class TestEd25519KeyGeneration:
    """Test Ed25519 key generation functions."""
    
    def test_generate_random_keypair(self):
        """Test generating a random Ed25519 key pair."""
        signing_key, verify_key = generate_ed25519_keypair()
        
        assert isinstance(signing_key, Ed25519SigningKey)
        assert isinstance(verify_key, Ed25519VerifyKey)
        assert len(signing_key.to_bytes()) == 32
        assert len(verify_key.to_bytes()) == 32
    
    def test_generate_multiple_unique_keys(self):
        """Test that multiple key generations produce unique keys."""
        key1, _ = generate_ed25519_keypair()
        key2, _ = generate_ed25519_keypair()
        
        assert key1.to_bytes() != key2.to_bytes()
    
    def test_generate_from_seed(self):
        """Test deterministic key generation from seed."""
        seed = b"a" * 32
        key1 = Ed25519SigningKey(seed=seed)
        key2 = Ed25519SigningKey(seed=seed)
        
        assert key1.to_bytes() == key2.to_bytes()
    
    def test_seed_wrong_length_raises_error(self):
        """Test that invalid seed length raises ValueError."""
        with pytest.raises(ValueError, match="Seed must be exactly 32 bytes"):
            Ed25519SigningKey(seed=b"too short")
        
        with pytest.raises(ValueError, match="Seed must be exactly 32 bytes"):
            Ed25519SigningKey(seed=b"a" * 33)


class TestEd25519Signing:
    """Test Ed25519 signing operations."""
    
    def test_sign_message(self):
        """Test signing a message."""
        signing_key, _ = generate_ed25519_keypair()
        message = b"Hello, DNA-Key Authentication!"
        
        signature = signing_key.sign(message)
        
        assert isinstance(signature, bytes)
        assert len(signature) == 64
    
    def test_sign_empty_message(self):
        """Test signing an empty message."""
        signing_key, _ = generate_ed25519_keypair()
        message = b""
        
        signature = signing_key.sign(message)
        
        assert isinstance(signature, bytes)
        assert len(signature) == 64
    
    def test_sign_large_message(self):
        """Test signing a large message."""
        signing_key, _ = generate_ed25519_keypair()
        message = b"x" * 1000000  # 1 MB
        
        signature = signing_key.sign(message)
        
        assert isinstance(signature, bytes)
        assert len(signature) == 64
    
    def test_sign_non_bytes_raises_error(self):
        """Test that signing non-bytes raises TypeError."""
        signing_key, _ = generate_ed25519_keypair()
        
        with pytest.raises(TypeError, match="Message must be bytes"):
            signing_key.sign("not bytes")
    
    def test_deterministic_signatures(self):
        """Test that Ed25519 produces deterministic signatures."""
        seed = b"b" * 32
        signing_key = Ed25519SigningKey(seed=seed)
        message = b"Deterministic test"
        
        sig1 = signing_key.sign(message)
        sig2 = signing_key.sign(message)
        
        assert sig1 == sig2


class TestEd25519Verification:
    """Test Ed25519 signature verification."""
    
    def test_verify_valid_signature(self):
        """Test verifying a valid signature."""
        signing_key, verify_key = generate_ed25519_keypair()
        message = b"Test message"
        signature = signing_key.sign(message)
        
        result = verify_key.verify(message, signature)
        
        assert result is True
    
    def test_verify_invalid_signature(self):
        """Test that invalid signature is rejected."""
        signing_key, verify_key = generate_ed25519_keypair()
        message = b"Test message"
        signature = signing_key.sign(message)
        
        # Modify the signature
        bad_signature = bytes([b ^ 0xFF for b in signature])
        
        result = verify_key.verify(message, bad_signature)
        
        assert result is False
    
    def test_verify_wrong_message(self):
        """Test that signature fails for different message."""
        signing_key, verify_key = generate_ed25519_keypair()
        message1 = b"Original message"
        message2 = b"Different message"
        signature = signing_key.sign(message1)
        
        result = verify_key.verify(message2, signature)
        
        assert result is False
    
    def test_verify_wrong_key(self):
        """Test that signature fails with wrong public key."""
        signing_key1, _ = generate_ed25519_keypair()
        _, verify_key2 = generate_ed25519_keypair()
        
        message = b"Test message"
        signature = signing_key1.sign(message)
        
        result = verify_key2.verify(message, signature)
        
        assert result is False
    
    def test_verify_non_bytes_message_raises_error(self):
        """Test that verifying non-bytes message raises TypeError."""
        _, verify_key = generate_ed25519_keypair()
        signature = b"a" * 64
        
        with pytest.raises(TypeError, match="Message must be bytes"):
            verify_key.verify("not bytes", signature)
    
    def test_verify_non_bytes_signature_raises_error(self):
        """Test that verifying non-bytes signature raises TypeError."""
        _, verify_key = generate_ed25519_keypair()
        message = b"Test"
        
        with pytest.raises(TypeError, match="Signature must be bytes"):
            verify_key.verify(message, "not bytes")
    
    def test_verify_wrong_signature_length_raises_error(self):
        """Test that wrong signature length raises ValueError."""
        _, verify_key = generate_ed25519_keypair()
        message = b"Test"
        
        with pytest.raises(ValueError, match="Signature must be exactly 64 bytes"):
            verify_key.verify(message, b"too short")


class TestEd25519KeySerialization:
    """Test Ed25519 key serialization and deserialization."""
    
    def test_signing_key_to_from_bytes(self):
        """Test signing key serialization round-trip."""
        signing_key1, _ = generate_ed25519_keypair()
        key_bytes = signing_key1.to_bytes()
        signing_key2 = Ed25519SigningKey.from_bytes(key_bytes)
        
        assert signing_key1.to_bytes() == signing_key2.to_bytes()
        
        # Verify they produce same signatures
        message = b"Test"
        sig1 = signing_key1.sign(message)
        sig2 = signing_key2.sign(message)
        assert sig1 == sig2
    
    def test_verify_key_to_from_bytes(self):
        """Test verify key serialization round-trip."""
        _, verify_key1 = generate_ed25519_keypair()
        key_bytes = verify_key1.to_bytes()
        verify_key2 = Ed25519VerifyKey.from_bytes(key_bytes)
        
        assert verify_key1.to_bytes() == verify_key2.to_bytes()
    
    def test_signing_key_from_bytes_wrong_length(self):
        """Test that wrong key length raises ValueError."""
        with pytest.raises(ValueError, match="Private key must be exactly 32 bytes"):
            Ed25519SigningKey.from_bytes(b"too short")
    
    def test_verify_key_from_bytes_wrong_length(self):
        """Test that wrong key length raises ValueError."""
        with pytest.raises(ValueError, match="Public key must be exactly 32 bytes"):
            Ed25519VerifyKey.from_bytes(b"too short")
    
    def test_verify_key_derived_from_signing_key(self):
        """Test that verify key can be derived from signing key."""
        signing_key, original_verify_key = generate_ed25519_keypair()
        derived_verify_key = signing_key.verify_key()
        
        assert original_verify_key.to_bytes() == derived_verify_key.to_bytes()
        
        # Verify both work the same
        message = b"Test message"
        signature = signing_key.sign(message)
        assert original_verify_key.verify(message, signature)
        assert derived_verify_key.verify(message, signature)


class TestEd25519EdgeCases:
    """Test Ed25519 edge cases and special scenarios."""
    
    def test_sign_and_verify_empty_message(self):
        """Test signing and verifying an empty message."""
        signing_key, verify_key = generate_ed25519_keypair()
        message = b""
        
        signature = signing_key.sign(message)
        result = verify_key.verify(message, signature)
        
        assert result is True
    
    def test_verify_key_init_requires_one_param(self):
        """Test that VerifyKey init requires exactly one parameter."""
        with pytest.raises(ValueError, match="Must provide either verify_key or key_bytes"):
            Ed25519VerifyKey()
        
        with pytest.raises(ValueError, match="Must provide either verify_key or key_bytes"):
            _, verify_key = generate_ed25519_keypair()
            Ed25519VerifyKey(verify_key._verify_key, key_bytes=b"a" * 32)


class TestEd25519SecurityProperties:
    """Test security properties of Ed25519 implementation."""
    
    def test_different_messages_different_signatures(self):
        """Test that different messages produce different signatures."""
        signing_key, _ = generate_ed25519_keypair()
        
        sig1 = signing_key.sign(b"message1")
        sig2 = signing_key.sign(b"message2")
        
        assert sig1 != sig2
    
    def test_small_message_change_changes_signature(self):
        """Test that even small message changes produce different signatures."""
        signing_key, _ = generate_ed25519_keypair()
        
        sig1 = signing_key.sign(b"test message")
        sig2 = signing_key.sign(b"test messaga")  # Changed one letter
        
        assert sig1 != sig2
    
    def test_signature_verification_is_consistent(self):
        """Test that verification is consistent across multiple calls."""
        signing_key, verify_key = generate_ed25519_keypair()
        message = b"Consistency test"
        signature = signing_key.sign(message)
        
        # Verify multiple times
        results = [verify_key.verify(message, signature) for _ in range(100)]
        
        assert all(results)
        assert len(set(results)) == 1  # All results are the same
