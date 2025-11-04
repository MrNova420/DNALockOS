"""
DNA-Key Authentication System - AES-256-GCM Encryption Tests

Comprehensive test suite for AES-256-GCM authenticated encryption.
Tests cover:
- Key generation
- Encryption and decryption
- Authentication tag verification
- Nonce handling
- Edge cases and error handling
- Security properties
"""

import pytest
from server.crypto.encryption import (
    AES256GCM,
    DecryptionError,
    encrypt_data,
    decrypt_data
)


class TestAES256GCMKeyGeneration:
    """Test AES-256-GCM key generation."""
    
    def test_generate_key(self):
        """Test generating an encryption key."""
        key = AES256GCM.generate_key()
        
        assert isinstance(key, bytes)
        assert len(key) == 32
    
    def test_generate_multiple_unique_keys(self):
        """Test that multiple key generations produce unique keys."""
        key1 = AES256GCM.generate_key()
        key2 = AES256GCM.generate_key()
        
        assert key1 != key2
    
    def test_generate_nonce(self):
        """Test generating a nonce."""
        nonce = AES256GCM.generate_nonce()
        
        assert isinstance(nonce, bytes)
        assert len(nonce) == 24
    
    def test_generate_multiple_unique_nonces(self):
        """Test that multiple nonce generations produce unique nonces."""
        nonce1 = AES256GCM.generate_nonce()
        nonce2 = AES256GCM.generate_nonce()
        
        assert nonce1 != nonce2
    
    def test_init_with_valid_key(self):
        """Test initializing cipher with valid key."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        assert isinstance(cipher, AES256GCM)
    
    def test_init_with_wrong_key_length_raises_error(self):
        """Test that wrong key length raises ValueError."""
        with pytest.raises(ValueError, match="Key must be exactly 32 bytes"):
            AES256GCM(b"too short")
        
        with pytest.raises(ValueError, match="Key must be exactly 32 bytes"):
            AES256GCM(b"a" * 31)
        
        with pytest.raises(ValueError, match="Key must be exactly 32 bytes"):
            AES256GCM(b"a" * 33)


class TestAES256GCMEncryption:
    """Test AES-256-GCM encryption operations."""
    
    def test_encrypt_message(self):
        """Test encrypting a message."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"Secret message"
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        
        assert isinstance(ciphertext, bytes)
        assert isinstance(nonce, bytes)
        assert len(nonce) == 24
        assert ciphertext != plaintext
    
    def test_encrypt_empty_message(self):
        """Test encrypting an empty message."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b""
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        
        assert isinstance(ciphertext, bytes)
        assert len(nonce) == 24
    
    def test_encrypt_large_message(self):
        """Test encrypting a large message."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"x" * 1000000  # 1 MB
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        
        assert isinstance(ciphertext, bytes)
        assert len(nonce) == 24
    
    def test_encrypt_with_custom_nonce(self):
        """Test encrypting with a custom nonce."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"Test message"
        custom_nonce = AES256GCM.generate_nonce()
        
        ciphertext, nonce = cipher.encrypt(plaintext, nonce=custom_nonce)
        
        assert nonce == custom_nonce
    
    def test_encrypt_with_wrong_nonce_length_raises_error(self):
        """Test that wrong nonce length raises ValueError."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        with pytest.raises(ValueError, match="Nonce must be exactly 24 bytes"):
            cipher.encrypt(b"test", nonce=b"too short")
    
    def test_encrypt_non_bytes_raises_error(self):
        """Test that encrypting non-bytes raises TypeError."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        with pytest.raises(TypeError, match="Plaintext must be bytes"):
            cipher.encrypt("not bytes")
    
    def test_encrypt_same_plaintext_different_ciphertexts(self):
        """Test that encrypting same plaintext produces different ciphertexts (random nonces)."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"Same plaintext"
        
        ciphertext1, nonce1 = cipher.encrypt(plaintext)
        ciphertext2, nonce2 = cipher.encrypt(plaintext)
        
        assert nonce1 != nonce2
        assert ciphertext1 != ciphertext2


class TestAES256GCMDecryption:
    """Test AES-256-GCM decryption operations."""
    
    def test_decrypt_message(self):
        """Test decrypting a message."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"Secret message"
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(ciphertext, nonce)
        
        assert decrypted == plaintext
    
    def test_decrypt_empty_message(self):
        """Test decrypting an empty message."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b""
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(ciphertext, nonce)
        
        assert decrypted == plaintext
    
    def test_decrypt_large_message(self):
        """Test decrypting a large message."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"y" * 1000000
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(ciphertext, nonce)
        
        assert decrypted == plaintext
    
    def test_decrypt_with_wrong_key_fails(self):
        """Test that decryption with wrong key fails."""
        key1 = AES256GCM.generate_key()
        key2 = AES256GCM.generate_key()
        
        cipher1 = AES256GCM(key1)
        cipher2 = AES256GCM(key2)
        
        ciphertext, nonce = cipher1.encrypt(b"Secret")
        
        with pytest.raises(DecryptionError):
            cipher2.decrypt(ciphertext, nonce)
    
    def test_decrypt_with_wrong_nonce_fails(self):
        """Test that decryption with wrong nonce fails."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        ciphertext, _ = cipher.encrypt(b"Secret")
        wrong_nonce = AES256GCM.generate_nonce()
        
        with pytest.raises(DecryptionError):
            cipher.decrypt(ciphertext, wrong_nonce)
    
    def test_decrypt_tampered_ciphertext_fails(self):
        """Test that decryption of tampered ciphertext fails."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        ciphertext, nonce = cipher.encrypt(b"Secret message")
        
        # Tamper with ciphertext
        tampered = bytes([b ^ 0xFF for b in ciphertext])
        
        with pytest.raises(DecryptionError):
            cipher.decrypt(tampered, nonce)
    
    def test_decrypt_non_bytes_ciphertext_raises_error(self):
        """Test that decrypting non-bytes ciphertext raises TypeError."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        nonce = AES256GCM.generate_nonce()
        
        with pytest.raises(TypeError, match="Ciphertext must be bytes"):
            cipher.decrypt("not bytes", nonce)
    
    def test_decrypt_non_bytes_nonce_raises_error(self):
        """Test that decrypting with non-bytes nonce raises TypeError."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        with pytest.raises(TypeError, match="Nonce must be bytes"):
            cipher.decrypt(b"ciphertext", "not bytes")
    
    def test_decrypt_wrong_nonce_length_raises_error(self):
        """Test that wrong nonce length raises ValueError."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        with pytest.raises(ValueError, match="Nonce must be exactly 24 bytes"):
            cipher.decrypt(b"ciphertext", b"short")


class TestAES256GCMConvenienceFunctions:
    """Test convenience encryption/decryption functions."""
    
    def test_encrypt_decrypt_data(self):
        """Test encrypt_data and decrypt_data convenience functions."""
        key = AES256GCM.generate_key()
        plaintext = b"Convenience test"
        
        ciphertext, nonce = encrypt_data(key, plaintext)
        decrypted = decrypt_data(key, ciphertext, nonce)
        
        assert decrypted == plaintext
    
    def test_encrypt_data_with_custom_nonce(self):
        """Test encrypt_data with custom nonce."""
        key = AES256GCM.generate_key()
        plaintext = b"Test"
        custom_nonce = AES256GCM.generate_nonce()
        
        ciphertext, nonce = encrypt_data(key, plaintext, nonce=custom_nonce)
        
        assert nonce == custom_nonce
        
        decrypted = decrypt_data(key, ciphertext, nonce)
        assert decrypted == plaintext


class TestAES256GCMSecurityProperties:
    """Test security properties of AES-256-GCM implementation."""
    
    def test_ciphertext_differs_from_plaintext(self):
        """Test that ciphertext is different from plaintext."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"x" * 100
        
        ciphertext, _ = cipher.encrypt(plaintext)
        
        assert ciphertext != plaintext
    
    def test_different_keys_different_ciphertexts(self):
        """Test that different keys produce different ciphertexts."""
        key1 = AES256GCM.generate_key()
        key2 = AES256GCM.generate_key()
        
        cipher1 = AES256GCM(key1)
        cipher2 = AES256GCM(key2)
        
        plaintext = b"Same plaintext"
        nonce = AES256GCM.generate_nonce()
        
        ciphertext1, _ = cipher1.encrypt(plaintext, nonce=nonce)
        ciphertext2, _ = cipher2.encrypt(plaintext, nonce=nonce)
        
        assert ciphertext1 != ciphertext2
    
    def test_encryption_is_deterministic_with_same_nonce(self):
        """Test that encryption is deterministic with the same nonce."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"Deterministic test"
        nonce = AES256GCM.generate_nonce()
        
        ciphertext1, _ = cipher.encrypt(plaintext, nonce=nonce)
        ciphertext2, _ = cipher.encrypt(plaintext, nonce=nonce)
        
        assert ciphertext1 == ciphertext2
    
    def test_small_plaintext_change_changes_ciphertext(self):
        """Test that even small plaintext changes produce different ciphertexts."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        nonce = AES256GCM.generate_nonce()
        
        ciphertext1, _ = cipher.encrypt(b"test message", nonce=nonce)
        nonce2 = AES256GCM.generate_nonce()
        ciphertext2, _ = cipher.encrypt(b"test messaga", nonce=nonce2)
        
        assert ciphertext1 != ciphertext2
    
    def test_authentication_prevents_tampering(self):
        """Test that authentication tag prevents ciphertext tampering."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        ciphertext, nonce = cipher.encrypt(b"Important message")
        
        # Try various tampering attacks
        for i in range(min(10, len(ciphertext))):
            tampered = bytearray(ciphertext)
            tampered[i] ^= 0x01  # Flip one bit
            
            with pytest.raises(DecryptionError):
                cipher.decrypt(bytes(tampered), nonce)
    
    def test_decryption_is_consistent(self):
        """Test that decryption is consistent across multiple calls."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        plaintext = b"Consistency test"
        
        ciphertext, nonce = cipher.encrypt(plaintext)
        
        # Decrypt multiple times
        results = [cipher.decrypt(ciphertext, nonce) for _ in range(10)]
        
        assert all(r == plaintext for r in results)
    
    def test_aad_not_implemented(self):
        """Test that AAD is not yet implemented."""
        key = AES256GCM.generate_key()
        cipher = AES256GCM(key)
        
        with pytest.raises(NotImplementedError):
            cipher.encrypt(b"test", aad=b"additional data")
        
        with pytest.raises(NotImplementedError):
            cipher.decrypt(b"test", AES256GCM.generate_nonce(), aad=b"additional data")
