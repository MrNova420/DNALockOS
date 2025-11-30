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
Tests for Quantum-Safe Cryptography Module.

Tests the post-quantum cryptographic implementations including:
- Kyber Key Encapsulation
- Dilithium Digital Signatures
- SPHINCS+ Signatures
- Hybrid Cryptography
- Quantum-Safe Key Derivation
"""

import secrets
from datetime import datetime, timezone

import pytest

from server.crypto.quantum_safe import (
    DilithiumSignature,
    HybridCrypto,
    HybridKeyPair,
    HybridSignature,
    KEMCiphertext,
    KEMKeyPair,
    KyberKEM,
    QuantumDNAProtector,
    QuantumProtectedDNAStrand,
    QuantumSafeKDF,
    QuantumSecurityLevel,
    QuantumSignature,
    QuantumThreatLevel,
    SignatureKeyPair,
    SPHINCSSignature,
)


class TestQuantumThreatLevel:
    """Test quantum threat level enumeration."""
    
    def test_threat_levels_exist(self):
        """Test all threat levels exist."""
        assert QuantumThreatLevel.NONE.value == "none"
        assert QuantumThreatLevel.THEORETICAL.value == "theoretical"
        assert QuantumThreatLevel.EMERGING.value == "emerging"
        assert QuantumThreatLevel.ADVANCING.value == "advancing"
        assert QuantumThreatLevel.IMMINENT.value == "imminent"
        assert QuantumThreatLevel.ACTIVE.value == "active"


class TestQuantumSecurityLevel:
    """Test quantum security level enumeration."""
    
    def test_security_levels_ordering(self):
        """Test security levels are properly ordered."""
        assert QuantumSecurityLevel.LEVEL_1.value < QuantumSecurityLevel.LEVEL_3.value
        assert QuantumSecurityLevel.LEVEL_3.value < QuantumSecurityLevel.LEVEL_5.value
    
    def test_security_level_values(self):
        """Test security level values."""
        assert QuantumSecurityLevel.LEVEL_1.value == 1
        assert QuantumSecurityLevel.LEVEL_5.value == 5


class TestKyberKEM:
    """Test Kyber Key Encapsulation Mechanism."""
    
    def test_create_kyber_default(self):
        """Test creating Kyber with default parameters."""
        kem = KyberKEM()
        assert kem.variant == "kyber768"
    
    def test_create_kyber_variants(self):
        """Test creating different Kyber variants."""
        for variant in ["kyber512", "kyber768", "kyber1024"]:
            kem = KyberKEM(variant)
            assert kem.variant == variant
    
    def test_invalid_variant_raises_error(self):
        """Test that invalid variant raises error."""
        with pytest.raises(ValueError, match="Unknown Kyber variant"):
            KyberKEM("invalid_variant")
    
    def test_generate_keypair(self):
        """Test key pair generation."""
        kem = KyberKEM("kyber768")
        keypair = kem.generate_keypair()
        
        assert isinstance(keypair, KEMKeyPair)
        assert len(keypair.public_key) > 0
        assert len(keypair.private_key) > 0
        assert keypair.algorithm == "ML-KEM-kyber768"
    
    def test_encapsulate(self):
        """Test key encapsulation."""
        kem = KyberKEM()
        keypair = kem.generate_keypair()
        
        ciphertext = kem.encapsulate(keypair.public_key)
        
        assert isinstance(ciphertext, KEMCiphertext)
        assert len(ciphertext.ciphertext) > 0
        assert len(ciphertext.shared_secret) == 32
    
    def test_decapsulate(self):
        """Test key decapsulation."""
        kem = KyberKEM()
        keypair = kem.generate_keypair()
        
        ciphertext = kem.encapsulate(keypair.public_key)
        shared_secret = kem.decapsulate(ciphertext.ciphertext, keypair.private_key)
        
        assert len(shared_secret) == 32
    
    def test_security_level_kyber512(self):
        """Test Kyber512 security level."""
        kem = KyberKEM("kyber512")
        keypair = kem.generate_keypair()
        
        assert keypair.security_level == QuantumSecurityLevel.LEVEL_1
    
    def test_security_level_kyber1024(self):
        """Test Kyber1024 security level."""
        kem = KyberKEM("kyber1024")
        keypair = kem.generate_keypair()
        
        assert keypair.security_level == QuantumSecurityLevel.LEVEL_5


class TestDilithiumSignature:
    """Test Dilithium Digital Signature."""
    
    def test_create_dilithium_default(self):
        """Test creating Dilithium with default parameters."""
        sig = DilithiumSignature()
        assert sig.variant == "dilithium3"
    
    def test_create_dilithium_variants(self):
        """Test creating different Dilithium variants."""
        for variant in ["dilithium2", "dilithium3", "dilithium5"]:
            sig = DilithiumSignature(variant)
            assert sig.variant == variant
    
    def test_invalid_variant_raises_error(self):
        """Test that invalid variant raises error."""
        with pytest.raises(ValueError, match="Unknown Dilithium variant"):
            DilithiumSignature("invalid")
    
    def test_generate_keypair(self):
        """Test key pair generation."""
        sig = DilithiumSignature()
        keypair = sig.generate_keypair()
        
        assert isinstance(keypair, SignatureKeyPair)
        assert len(keypair.public_key) > 0
        assert len(keypair.private_key) > 0
    
    def test_sign_message(self):
        """Test signing a message."""
        sig = DilithiumSignature()
        keypair = sig.generate_keypair()
        
        message = b"test message to sign"
        signature = sig.sign(message, keypair.private_key)
        
        assert isinstance(signature, QuantumSignature)
        assert len(signature.signature) == sig.params["sig_size"]
    
    def test_verify_signature(self):
        """Test signature verification."""
        sig = DilithiumSignature()
        keypair = sig.generate_keypair()
        
        message = b"test message"
        signature = sig.sign(message, keypair.private_key)
        
        is_valid = sig.verify(message, signature, keypair.public_key)
        assert is_valid is True
    
    def test_signature_sizes(self):
        """Test signature sizes for different variants."""
        sizes = {
            "dilithium2": 2420,
            "dilithium3": 3293,
            "dilithium5": 4595,
        }
        
        for variant, expected_size in sizes.items():
            sig = DilithiumSignature(variant)
            keypair = sig.generate_keypair()
            signature = sig.sign(b"test", keypair.private_key)
            
            assert len(signature.signature) == expected_size


class TestSPHINCSSignature:
    """Test SPHINCS+ Signature."""
    
    def test_create_sphincs_default(self):
        """Test creating SPHINCS+ with default parameters."""
        sig = SPHINCSSignature()
        assert sig.variant == "sphincs-256s"
    
    def test_create_sphincs_variants(self):
        """Test creating different SPHINCS+ variants."""
        variants = ["sphincs-128s", "sphincs-128f", "sphincs-192s", "sphincs-256s"]
        for variant in variants:
            sig = SPHINCSSignature(variant)
            assert sig.variant == variant
    
    def test_generate_keypair(self):
        """Test key pair generation."""
        sig = SPHINCSSignature()
        keypair = sig.generate_keypair()
        
        assert isinstance(keypair, SignatureKeyPair)
        assert len(keypair.public_key) == 64
        assert len(keypair.private_key) == 128
    
    def test_sign_and_verify(self):
        """Test signing and verification."""
        sig = SPHINCSSignature()
        keypair = sig.generate_keypair()
        
        message = b"test message for SPHINCS+"
        signature = sig.sign(message, keypair.private_key)
        
        assert isinstance(signature, QuantumSignature)
        
        is_valid = sig.verify(message, signature, keypair.public_key)
        assert is_valid is True


class TestHybridCrypto:
    """Test Hybrid Cryptography."""
    
    def test_create_hybrid(self):
        """Test creating hybrid crypto instance."""
        hybrid = HybridCrypto()
        assert hybrid is not None
    
    def test_generate_hybrid_keypair(self):
        """Test hybrid key pair generation."""
        hybrid = HybridCrypto()
        keypair = hybrid.generate_hybrid_keypair()
        
        assert isinstance(keypair, HybridKeyPair)
        assert len(keypair.classical_public_key) > 0
        assert len(keypair.pq_public_key) > 0
        assert len(keypair.combined_public_key_hash) == 64
    
    def test_hybrid_sign(self):
        """Test hybrid signing."""
        hybrid = HybridCrypto()
        keypair = hybrid.generate_hybrid_keypair()
        
        message = b"hybrid test message"
        signature = hybrid.hybrid_sign(message, keypair)
        
        assert isinstance(signature, HybridSignature)
        assert signature.is_hybrid is True
        assert len(signature.classical_signature) > 0
        assert len(signature.pq_signature) > 0
    
    def test_hybrid_verify(self):
        """Test hybrid signature verification."""
        hybrid = HybridCrypto()
        keypair = hybrid.generate_hybrid_keypair()
        
        message = b"verify this hybrid signature"
        signature = hybrid.hybrid_sign(message, keypair)
        
        overall, classical, pq = hybrid.hybrid_verify(message, signature, keypair)
        
        assert classical is True
        assert pq is True
        assert overall is True


class TestQuantumDNAProtector:
    """Test Quantum DNA Protector."""
    
    def test_create_protector_default(self):
        """Test creating protector with default settings."""
        protector = QuantumDNAProtector()
        assert protector.security_level == QuantumSecurityLevel.LEVEL_3
    
    def test_create_protector_level5(self):
        """Test creating protector with maximum security."""
        protector = QuantumDNAProtector(QuantumSecurityLevel.LEVEL_5)
        assert protector.security_level == QuantumSecurityLevel.LEVEL_5
    
    def test_protect_strand(self):
        """Test protecting a DNA strand."""
        protector = QuantumDNAProtector()
        
        strand_id = "dna-test-001"
        strand_data = secrets.token_bytes(1024)
        
        protected, keypair = protector.protect_strand(strand_id, strand_data)
        
        assert isinstance(protected, QuantumProtectedDNAStrand)
        assert protected.strand_id == strand_id
        assert len(protected.strand_checksum) == 128  # SHA3-512 hex
        assert len(protected.kem_public_key) > 0
        assert len(protected.pq_signature) > 0
    
    def test_protect_strand_with_hybrid(self):
        """Test protecting with hybrid signature."""
        protector = QuantumDNAProtector()
        
        strand_data = secrets.token_bytes(512)
        protected, _ = protector.protect_strand(
            "hybrid-strand",
            strand_data,
            use_hybrid=True
        )
        
        assert protected.hybrid_signature is not None
    
    def test_verify_protection(self):
        """Test verifying strand protection."""
        protector = QuantumDNAProtector()
        
        strand_data = secrets.token_bytes(1024)
        protected, keypair = protector.protect_strand("verify-test", strand_data)
        
        is_valid, details = protector.verify_protection(
            protected,
            strand_data,
            keypair.public_key
        )
        
        assert is_valid is True
        assert details["checksum_valid"] is True
        assert details["signature_valid"] is True
    
    def test_verify_wrong_data_fails(self):
        """Test that wrong data fails verification."""
        protector = QuantumDNAProtector()
        
        strand_data = secrets.token_bytes(1024)
        protected, keypair = protector.protect_strand("wrong-data", strand_data)
        
        wrong_data = secrets.token_bytes(1024)  # Different data
        is_valid, details = protector.verify_protection(
            protected,
            wrong_data,
            keypair.public_key
        )
        
        assert details["checksum_valid"] is False
    
    def test_protected_strand_to_dict(self):
        """Test protected strand serialization."""
        protector = QuantumDNAProtector()
        
        protected, _ = protector.protect_strand(
            "dict-test",
            b"test data"
        )
        
        result = protected.to_dict()
        
        assert result["strand_id"] == "dict-test"
        assert "quantum_security_level" in result
        assert "protection_timestamp" in result


class TestQuantumSafeKDF:
    """Test Quantum-Safe Key Derivation."""
    
    def test_derive_basic(self):
        """Test basic key derivation."""
        master_key = secrets.token_bytes(32)
        
        derived = QuantumSafeKDF.derive(master_key, "test_context")
        
        assert len(derived) == 32
    
    def test_derive_custom_length(self):
        """Test derivation with custom length."""
        master_key = secrets.token_bytes(32)
        
        for length in [16, 32, 64, 128]:
            derived = QuantumSafeKDF.derive(master_key, "context", length)
            assert len(derived) == length
    
    def test_derive_is_deterministic(self):
        """Test that derivation is deterministic."""
        master_key = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        
        derived1 = QuantumSafeKDF.derive(master_key, "context", salt=salt)
        derived2 = QuantumSafeKDF.derive(master_key, "context", salt=salt)
        
        assert derived1 == derived2
    
    def test_different_contexts_different_keys(self):
        """Test that different contexts produce different keys."""
        master_key = secrets.token_bytes(32)
        
        derived1 = QuantumSafeKDF.derive(master_key, "context1")
        derived2 = QuantumSafeKDF.derive(master_key, "context2")
        
        assert derived1 != derived2
    
    def test_derive_dna_segment_key(self):
        """Test DNA segment key derivation."""
        master_key = secrets.token_bytes(32)
        
        key1 = QuantumSafeKDF.derive_dna_segment_key(master_key, 0, "ENTROPY")
        key2 = QuantumSafeKDF.derive_dna_segment_key(master_key, 1, "ENTROPY")
        key3 = QuantumSafeKDF.derive_dna_segment_key(master_key, 0, "HASH")
        
        # All should be different
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3
        
        # All should be 32 bytes
        assert len(key1) == 32
        assert len(key2) == 32
        assert len(key3) == 32


class TestKEMKeyPair:
    """Test KEM KeyPair dataclass."""
    
    def test_create_keypair(self):
        """Test creating a KEM key pair."""
        keypair = KEMKeyPair(
            public_key=b"public_key_bytes",
            private_key=b"private_key_bytes",
            algorithm="ML-KEM-768",
            security_level=QuantumSecurityLevel.LEVEL_3
        )
        
        assert keypair.algorithm == "ML-KEM-768"
        assert keypair.security_level == QuantumSecurityLevel.LEVEL_3


class TestSignatureKeyPair:
    """Test Signature KeyPair dataclass."""
    
    def test_create_signature_keypair(self):
        """Test creating a signature key pair."""
        keypair = SignatureKeyPair(
            public_key=b"pk",
            private_key=b"sk",
            algorithm="ML-DSA-65",
            security_level=QuantumSecurityLevel.LEVEL_3
        )
        
        assert keypair.algorithm == "ML-DSA-65"
