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
DNA-Key Authentication System - X25519 Key Exchange Tests

Comprehensive test suite for X25519 ECDH key exchange implementation.
Tests cover:
- Key generation
- Key exchange operations
- Shared secret derivation
- Edge cases and error handling
- Key serialization/deserialization
- Security properties
"""

import pytest
from server.crypto.key_exchange import (
    X25519PrivateKey,
    X25519PublicKey,
    generate_x25519_keypair,
    perform_key_exchange
)


class TestX25519KeyGeneration:
    """Test X25519 key generation functions."""
    
    def test_generate_random_keypair(self):
        """Test generating a random X25519 key pair."""
        private_key, public_key = generate_x25519_keypair()
        
        assert isinstance(private_key, X25519PrivateKey)
        assert isinstance(public_key, X25519PublicKey)
        assert len(private_key.to_bytes()) == 32
        assert len(public_key.to_bytes()) == 32
    
    def test_generate_multiple_unique_keys(self):
        """Test that multiple key generations produce unique keys."""
        key1, _ = generate_x25519_keypair()
        key2, _ = generate_x25519_keypair()
        
        assert key1.to_bytes() != key2.to_bytes()
    
    def test_generate_from_seed(self):
        """Test deterministic key generation from seed."""
        seed = b"a" * 32
        key1 = X25519PrivateKey(seed=seed)
        key2 = X25519PrivateKey(seed=seed)
        
        assert key1.to_bytes() == key2.to_bytes()
    
    def test_seed_wrong_length_raises_error(self):
        """Test that invalid seed length raises ValueError."""
        with pytest.raises(ValueError, match="Seed must be exactly 32 bytes"):
            X25519PrivateKey(seed=b"too short")
        
        with pytest.raises(ValueError, match="Seed must be exactly 32 bytes"):
            X25519PrivateKey(seed=b"a" * 33)


class TestX25519KeyExchange:
    """Test X25519 key exchange operations."""
    
    def test_key_exchange_produces_shared_secret(self):
        """Test that key exchange produces a shared secret."""
        alice_priv, alice_pub = generate_x25519_keypair()
        bob_priv, bob_pub = generate_x25519_keypair()
        
        alice_shared = alice_priv.exchange(bob_pub)
        bob_shared = bob_priv.exchange(alice_pub)
        
        assert alice_shared == bob_shared
        assert len(alice_shared) == 32
    
    def test_key_exchange_with_perform_function(self):
        """Test key exchange using the convenience function."""
        alice_priv, alice_pub = generate_x25519_keypair()
        bob_priv, bob_pub = generate_x25519_keypair()
        
        alice_shared = perform_key_exchange(alice_priv, bob_pub)
        bob_shared = perform_key_exchange(bob_priv, alice_pub)
        
        assert alice_shared == bob_shared
        assert len(alice_shared) == 32
    
    def test_multiple_exchanges_same_result(self):
        """Test that multiple exchanges produce the same result."""
        alice_priv, alice_pub = generate_x25519_keypair()
        bob_priv, bob_pub = generate_x25519_keypair()
        
        shared1 = alice_priv.exchange(bob_pub)
        shared2 = alice_priv.exchange(bob_pub)
        shared3 = alice_priv.exchange(bob_pub)
        
        assert shared1 == shared2 == shared3
    
    def test_exchange_with_invalid_type_raises_error(self):
        """Test that exchange with invalid type raises TypeError."""
        private_key, _ = generate_x25519_keypair()
        
        with pytest.raises(TypeError, match="peer_public_key must be X25519PublicKey"):
            private_key.exchange("not a public key")
        
        with pytest.raises(TypeError, match="peer_public_key must be X25519PublicKey"):
            private_key.exchange(b"also not valid")
    
    def test_different_peers_different_secrets(self):
        """Test that exchanges with different peers produce different secrets."""
        alice_priv, _ = generate_x25519_keypair()
        _, bob_pub = generate_x25519_keypair()
        _, charlie_pub = generate_x25519_keypair()
        
        alice_bob_shared = alice_priv.exchange(bob_pub)
        alice_charlie_shared = alice_priv.exchange(charlie_pub)
        
        assert alice_bob_shared != alice_charlie_shared
    
    def test_three_party_key_exchange(self):
        """Test key exchange with three parties."""
        alice_priv, alice_pub = generate_x25519_keypair()
        bob_priv, bob_pub = generate_x25519_keypair()
        charlie_priv, charlie_pub = generate_x25519_keypair()
        
        # Alice-Bob
        alice_bob = alice_priv.exchange(bob_pub)
        bob_alice = bob_priv.exchange(alice_pub)
        assert alice_bob == bob_alice
        
        # Bob-Charlie
        bob_charlie = bob_priv.exchange(charlie_pub)
        charlie_bob = charlie_priv.exchange(bob_pub)
        assert bob_charlie == charlie_bob
        
        # Alice-Charlie
        alice_charlie = alice_priv.exchange(charlie_pub)
        charlie_alice = charlie_priv.exchange(alice_pub)
        assert alice_charlie == charlie_alice
        
        # All three should be different
        assert alice_bob != bob_charlie
        assert bob_charlie != alice_charlie
        assert alice_bob != alice_charlie


class TestX25519KeySerialization:
    """Test X25519 key serialization and deserialization."""
    
    def test_private_key_to_from_bytes(self):
        """Test private key serialization round-trip."""
        private_key1, _ = generate_x25519_keypair()
        key_bytes = private_key1.to_bytes()
        private_key2 = X25519PrivateKey.from_bytes(key_bytes)
        
        assert private_key1.to_bytes() == private_key2.to_bytes()
        
        # Verify they produce same shared secrets
        _, peer_pub = generate_x25519_keypair()
        shared1 = private_key1.exchange(peer_pub)
        shared2 = private_key2.exchange(peer_pub)
        assert shared1 == shared2
    
    def test_public_key_to_from_bytes(self):
        """Test public key serialization round-trip."""
        _, public_key1 = generate_x25519_keypair()
        key_bytes = public_key1.to_bytes()
        public_key2 = X25519PublicKey.from_bytes(key_bytes)
        
        assert public_key1.to_bytes() == public_key2.to_bytes()
    
    def test_private_key_from_bytes_wrong_length(self):
        """Test that wrong key length raises ValueError."""
        with pytest.raises(ValueError, match="Private key must be exactly 32 bytes"):
            X25519PrivateKey.from_bytes(b"too short")
        
        with pytest.raises(ValueError, match="Private key must be exactly 32 bytes"):
            X25519PrivateKey.from_bytes(b"a" * 33)
    
    def test_public_key_from_bytes_wrong_length(self):
        """Test that wrong key length raises ValueError."""
        with pytest.raises(ValueError, match="Public key must be exactly 32 bytes"):
            X25519PublicKey.from_bytes(b"too short")
        
        with pytest.raises(ValueError, match="Public key must be exactly 32 bytes"):
            X25519PublicKey.from_bytes(b"a" * 33)
    
    def test_public_key_derived_from_private_key(self):
        """Test that public key can be derived from private key."""
        private_key, original_public_key = generate_x25519_keypair()
        derived_public_key = private_key.public_key()
        
        assert original_public_key.to_bytes() == derived_public_key.to_bytes()
    
    def test_serialized_keys_work_in_exchange(self):
        """Test that serialized/deserialized keys work in key exchange."""
        # Generate original keys
        alice_priv1, alice_pub1 = generate_x25519_keypair()
        bob_priv1, bob_pub1 = generate_x25519_keypair()
        
        # Perform exchange with original keys
        shared1 = alice_priv1.exchange(bob_pub1)
        
        # Serialize and deserialize keys
        alice_priv2 = X25519PrivateKey.from_bytes(alice_priv1.to_bytes())
        bob_pub2 = X25519PublicKey.from_bytes(bob_pub1.to_bytes())
        
        # Perform exchange with deserialized keys
        shared2 = alice_priv2.exchange(bob_pub2)
        
        assert shared1 == shared2


class TestX25519EdgeCases:
    """Test X25519 edge cases and special scenarios."""
    
    def test_public_key_init_requires_one_param(self):
        """Test that PublicKey init requires exactly one parameter."""
        with pytest.raises(ValueError, match="Must provide either public_key or key_bytes"):
            X25519PublicKey()
        
        with pytest.raises(ValueError, match="Must provide either public_key or key_bytes"):
            _, public_key = generate_x25519_keypair()
            X25519PublicKey(public_key._public_key, key_bytes=b"a" * 32)
    
    def test_same_private_key_different_public_keys_different_secrets(self):
        """Test that same private key with different public keys produces different secrets."""
        private_key, _ = generate_x25519_keypair()
        _, public_key1 = generate_x25519_keypair()
        _, public_key2 = generate_x25519_keypair()
        
        shared1 = private_key.exchange(public_key1)
        shared2 = private_key.exchange(public_key2)
        
        assert shared1 != shared2


class TestX25519SecurityProperties:
    """Test security properties of X25519 implementation."""
    
    def test_shared_secret_is_symmetric(self):
        """Test that key exchange is symmetric (Alice->Bob == Bob->Alice)."""
        alice_priv, alice_pub = generate_x25519_keypair()
        bob_priv, bob_pub = generate_x25519_keypair()
        
        alice_perspective = alice_priv.exchange(bob_pub)
        bob_perspective = bob_priv.exchange(alice_pub)
        
        assert alice_perspective == bob_perspective
    
    def test_shared_secret_uniqueness(self):
        """Test that different key pairs produce different shared secrets."""
        # First pair
        alice1_priv, alice1_pub = generate_x25519_keypair()
        bob1_priv, bob1_pub = generate_x25519_keypair()
        shared1 = alice1_priv.exchange(bob1_pub)
        
        # Second pair
        alice2_priv, alice2_pub = generate_x25519_keypair()
        bob2_priv, bob2_pub = generate_x25519_keypair()
        shared2 = alice2_priv.exchange(bob2_pub)
        
        assert shared1 != shared2
    
    def test_public_key_reuse_is_safe(self):
        """Test that reusing public keys with different private keys is safe."""
        _, shared_public_key = generate_x25519_keypair()
        
        priv1, _ = generate_x25519_keypair()
        priv2, _ = generate_x25519_keypair()
        
        shared1 = priv1.exchange(shared_public_key)
        shared2 = priv2.exchange(shared_public_key)
        
        # Different private keys should produce different shared secrets
        assert shared1 != shared2
    
    def test_forward_secrecy_simulation(self):
        """Test that ephemeral keys provide forward secrecy."""
        # Session 1
        alice_eph1, alice_pub1 = generate_x25519_keypair()
        bob_eph1, bob_pub1 = generate_x25519_keypair()
        session1_secret = alice_eph1.exchange(bob_pub1)
        
        # Session 2 with new ephemeral keys
        alice_eph2, alice_pub2 = generate_x25519_keypair()
        bob_eph2, bob_pub2 = generate_x25519_keypair()
        session2_secret = alice_eph2.exchange(bob_pub2)
        
        # Different ephemeral keys should produce different secrets
        assert session1_secret != session2_secret
    
    def test_key_exchange_deterministic_with_same_keys(self):
        """Test that key exchange is deterministic with the same key pairs."""
        alice_priv, _ = generate_x25519_keypair()
        _, bob_pub = generate_x25519_keypair()
        
        results = [alice_priv.exchange(bob_pub) for _ in range(10)]
        
        # All results should be identical
        assert len(set(results)) == 1
    
    def test_shared_secret_length_is_constant(self):
        """Test that shared secrets are always 32 bytes."""
        secrets = []
        for _ in range(100):
            alice_priv, _ = generate_x25519_keypair()
            _, bob_pub = generate_x25519_keypair()
            shared = alice_priv.exchange(bob_pub)
            secrets.append(shared)
        
        # All secrets should be 32 bytes
        assert all(len(s) == 32 for s in secrets)
