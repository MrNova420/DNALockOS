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
DNA-Key Authentication System - Futuristic Algorithms Tests

Comprehensive tests for the futuristic cryptographic algorithms.
"""

import pytest
import secrets

from server.crypto.futuristic_algorithms import (
    SignatureScheme,
    MultiLayerSignature,
    ThresholdShare,
    ThresholdScheme,
    ZKProof,
    SchnorrZKP,
    VRFOutput,
    VerifiableRandomFunction,
    TimeLockPuzzle,
    TimeLockPuzzleGenerator,
    AdvancedKeyDerivation,
    QuantumResistantUtilities,
    AggregateSignature,
    SignatureAggregator,
)


class TestMultiLayerSignature:
    """Tests for multi-layer signature scheme."""
    
    def test_create_signature(self):
        """Test creating a multi-layer signature."""
        sig = MultiLayerSignature(
            classical_signature=secrets.token_bytes(64),
            lattice_signature=secrets.token_bytes(2420),
            hash_signature=secrets.token_bytes(17088)
        )
        
        assert len(sig.classical_signature) == 64
        assert len(sig.lattice_signature) == 2420
        assert len(sig.hash_signature) == 17088
    
    def test_compute_binding_hash(self):
        """Test computing binding hash."""
        sig = MultiLayerSignature(
            classical_signature=secrets.token_bytes(64),
            lattice_signature=secrets.token_bytes(128),
            hash_signature=secrets.token_bytes(128)
        )
        
        binding = sig.compute_binding_hash()
        
        assert len(binding) == 64  # SHA3-512
        assert sig.binding_hash == binding
    
    def test_verify_binding(self):
        """Test verifying binding hash."""
        sig = MultiLayerSignature(
            classical_signature=secrets.token_bytes(64),
            lattice_signature=secrets.token_bytes(128),
            hash_signature=secrets.token_bytes(128)
        )
        
        sig.compute_binding_hash()
        
        assert sig.verify_binding() is True
    
    def test_tampered_binding_fails(self):
        """Test that tampered signature fails binding verification."""
        sig = MultiLayerSignature(
            classical_signature=secrets.token_bytes(64),
            lattice_signature=secrets.token_bytes(128),
            hash_signature=secrets.token_bytes(128)
        )
        
        sig.compute_binding_hash()
        
        # Tamper with classical signature
        sig.classical_signature = secrets.token_bytes(64)
        
        assert sig.verify_binding() is False
    
    def test_serialization_round_trip(self):
        """Test serialization and deserialization."""
        original = MultiLayerSignature(
            classical_signature=secrets.token_bytes(64),
            lattice_signature=secrets.token_bytes(128),
            hash_signature=secrets.token_bytes(128)
        )
        original.compute_binding_hash()
        
        serialized = original.to_bytes()
        restored = MultiLayerSignature.from_bytes(serialized)
        
        assert restored.classical_signature == original.classical_signature
        assert restored.lattice_signature == original.lattice_signature
        assert restored.hash_signature == original.hash_signature


class TestThresholdScheme:
    """Tests for threshold cryptography."""
    
    def test_split_and_reconstruct(self):
        """Test splitting and reconstructing a secret."""
        scheme = ThresholdScheme(threshold=3, total_shares=5)
        
        secret = secrets.token_bytes(32)
        shares = scheme.split_secret(secret)
        
        assert len(shares) == 5
        
        # Reconstruct with exactly threshold shares
        reconstructed = scheme.reconstruct_secret(shares[:3])
        
        assert reconstructed == secret
    
    def test_any_k_shares_work(self):
        """Test that any K shares can reconstruct."""
        scheme = ThresholdScheme(threshold=3, total_shares=5)
        
        secret = secrets.token_bytes(32)
        shares = scheme.split_secret(secret)
        
        # Try different combinations
        combinations = [
            [shares[0], shares[1], shares[2]],
            [shares[0], shares[2], shares[4]],
            [shares[1], shares[3], shares[4]],
        ]
        
        for combo in combinations:
            reconstructed = scheme.reconstruct_secret(combo)
            assert reconstructed == secret
    
    def test_fewer_than_threshold_fails(self):
        """Test that fewer than K shares cannot reconstruct."""
        scheme = ThresholdScheme(threshold=3, total_shares=5)
        
        secret = secrets.token_bytes(32)
        shares = scheme.split_secret(secret)
        
        with pytest.raises(ValueError, match="Need at least"):
            scheme.reconstruct_secret(shares[:2])
    
    def test_share_commitment_verification(self):
        """Test that share commitments are verifiable."""
        scheme = ThresholdScheme(threshold=2, total_shares=3)
        
        secret = secrets.token_bytes(32)
        shares = scheme.split_secret(secret)
        
        for share in shares:
            assert share.verify_commitment() is True
    
    def test_tampered_share_detected(self):
        """Test that tampered shares are detected."""
        scheme = ThresholdScheme(threshold=2, total_shares=3)
        
        secret = secrets.token_bytes(32)
        shares = scheme.split_secret(secret)
        
        # Tamper with a share
        shares[0].share_value = secrets.token_bytes(32)
        
        assert shares[0].verify_commitment() is False


class TestSchnorrZKP:
    """Tests for Schnorr zero-knowledge proofs."""
    
    def test_generate_and_verify_proof(self):
        """Test generating and verifying a ZK proof."""
        zkp = SchnorrZKP()
        
        secret = secrets.token_bytes(32)
        message = b"test message"
        
        proof = zkp.generate_proof(secret, message)
        
        assert isinstance(proof, ZKProof)
        assert len(proof.commitment) > 0
        assert len(proof.challenge) == 32
        assert len(proof.response) == 64  # 32 bytes response + 32 bytes nonce
    
    def test_proof_verification_succeeds(self):
        """Test that valid proofs verify."""
        zkp = SchnorrZKP()
        
        secret = secrets.token_bytes(32)
        message = b"authenticate this"
        
        proof = zkp.generate_proof(secret, message)
        
        assert zkp.verify_proof(proof, message) is True
    
    def test_wrong_message_fails(self):
        """Test that wrong message fails verification."""
        zkp = SchnorrZKP()
        
        secret = secrets.token_bytes(32)
        message = b"original message"
        
        proof = zkp.generate_proof(secret, message)
        
        assert zkp.verify_proof(proof, b"different message") is False
    
    def test_proof_to_dict(self):
        """Test proof serialization."""
        zkp = SchnorrZKP()
        
        secret = secrets.token_bytes(32)
        proof = zkp.generate_proof(secret, b"test")
        
        proof_dict = proof.to_dict()
        
        assert "commitment" in proof_dict
        assert "challenge" in proof_dict
        assert "response" in proof_dict
        assert "public_input" in proof_dict


class TestVerifiableRandomFunction:
    """Tests for Verifiable Random Functions."""
    
    def test_evaluate_vrf(self):
        """Test VRF evaluation."""
        vrf = VerifiableRandomFunction()
        
        input_data = b"test input"
        output = vrf.evaluate(input_data)
        
        assert isinstance(output, VRFOutput)
        assert len(output.value) == 32
        assert len(output.proof) == 32
    
    def test_vrf_is_deterministic(self):
        """Test that VRF is deterministic."""
        secret_key = secrets.token_bytes(32)
        vrf = VerifiableRandomFunction(secret_key)
        
        input_data = b"same input"
        
        output1 = vrf.evaluate(input_data)
        output2 = vrf.evaluate(input_data)
        
        assert output1.value == output2.value
    
    def test_vrf_verification(self):
        """Test VRF verification."""
        vrf = VerifiableRandomFunction()
        
        input_data = b"verify me"
        output = vrf.evaluate(input_data)
        
        assert vrf.verify(input_data, output) is True
    
    def test_different_inputs_different_outputs(self):
        """Test that different inputs produce different outputs."""
        vrf = VerifiableRandomFunction()
        
        output1 = vrf.evaluate(b"input1")
        output2 = vrf.evaluate(b"input2")
        
        assert output1.value != output2.value
    
    def test_vrf_output_to_hex(self):
        """Test VRF output serialization."""
        vrf = VerifiableRandomFunction()
        
        output = vrf.evaluate(b"test")
        hex_output = output.to_hex()
        
        assert "value" in hex_output
        assert "proof" in hex_output
        assert "public_key" in hex_output


class TestAdvancedKeyDerivation:
    """Tests for advanced key derivation."""
    
    def test_derive_key(self):
        """Test key derivation."""
        master = secrets.token_bytes(32)
        context = b"test context"
        
        key = AdvancedKeyDerivation.derive_key(master, context)
        
        assert len(key) == 32
    
    def test_derivation_is_deterministic(self):
        """Test that derivation is deterministic."""
        master = secrets.token_bytes(32)
        context = b"same context"
        
        key1 = AdvancedKeyDerivation.derive_key(master, context)
        key2 = AdvancedKeyDerivation.derive_key(master, context)
        
        assert key1 == key2
    
    def test_different_contexts_different_keys(self):
        """Test that different contexts produce different keys."""
        master = secrets.token_bytes(32)
        
        key1 = AdvancedKeyDerivation.derive_key(master, b"context1")
        key2 = AdvancedKeyDerivation.derive_key(master, b"context2")
        
        assert key1 != key2
    
    def test_derive_segment_key(self):
        """Test segment key derivation."""
        master = secrets.token_bytes(32)
        
        key = AdvancedKeyDerivation.derive_segment_key(
            master, segment_index=42, segment_type="ENTROPY"
        )
        
        assert len(key) == 32
    
    def test_segment_keys_unique(self):
        """Test that each segment gets a unique key."""
        master = secrets.token_bytes(32)
        
        keys = [
            AdvancedKeyDerivation.derive_segment_key(master, i, "ENTROPY")
            for i in range(10)
        ]
        
        # All keys should be unique
        assert len(set(keys)) == 10


class TestQuantumResistantUtilities:
    """Tests for quantum-resistant utilities."""
    
    def test_quantum_safe_hash(self):
        """Test quantum-safe hash."""
        data = b"test data"
        
        hash_output = QuantumResistantUtilities.quantum_safe_hash(data)
        
        assert len(hash_output) == 64  # Default output length
    
    def test_quantum_safe_hash_variable_length(self):
        """Test quantum-safe hash with variable output length."""
        data = b"test data"
        
        for length in [32, 64, 128]:
            output = QuantumResistantUtilities.quantum_safe_hash(data, length)
            assert len(output) == length
    
    def test_quantum_safe_random(self):
        """Test quantum-safe random generation."""
        random_bytes = QuantumResistantUtilities.quantum_safe_random(32)
        
        assert len(random_bytes) == 32
    
    def test_quantum_safe_random_is_random(self):
        """Test that random bytes are actually random."""
        bytes1 = QuantumResistantUtilities.quantum_safe_random(32)
        bytes2 = QuantumResistantUtilities.quantum_safe_random(32)
        
        assert bytes1 != bytes2
    
    def test_post_quantum_kem(self):
        """Test post-quantum key encapsulation."""
        public_key = secrets.token_bytes(32)
        
        shared_secret, ciphertext = QuantumResistantUtilities.post_quantum_key_encapsulation(
            public_key
        )
        
        assert len(shared_secret) == 32
        assert len(ciphertext) == 64


class TestSignatureAggregator:
    """Tests for signature aggregation."""
    
    def test_aggregate_signatures(self):
        """Test aggregating multiple signatures."""
        signatures = [secrets.token_bytes(64) for _ in range(100)]
        public_keys = [secrets.token_bytes(32) for _ in range(100)]
        messages = [f"message {i}".encode() for i in range(100)]
        
        aggregate = SignatureAggregator.aggregate(signatures, public_keys, messages)
        
        assert isinstance(aggregate, AggregateSignature)
        assert aggregate.signature_count == 100
    
    def test_verify_aggregate(self):
        """Test verifying aggregate signature."""
        signatures = [secrets.token_bytes(64) for _ in range(10)]
        public_keys = [secrets.token_bytes(32) for _ in range(10)]
        messages = [f"message {i}".encode() for i in range(10)]
        
        aggregate = SignatureAggregator.aggregate(signatures, public_keys, messages)
        
        assert SignatureAggregator.verify_aggregate(aggregate) is True
    
    def test_aggregate_to_dict(self):
        """Test aggregate serialization."""
        signatures = [secrets.token_bytes(64) for _ in range(5)]
        public_keys = [secrets.token_bytes(32) for _ in range(5)]
        messages = [b"msg"] * 5
        
        aggregate = SignatureAggregator.aggregate(signatures, public_keys, messages)
        aggregate_dict = aggregate.to_dict()
        
        assert "aggregated_signature" in aggregate_dict
        assert "signature_count" in aggregate_dict
        assert aggregate_dict["signature_count"] == 5


class TestSignatureScheme:
    """Tests for signature scheme enum."""
    
    def test_classical_schemes(self):
        """Test classical signature schemes exist."""
        assert SignatureScheme.ED25519.value == "ed25519"
        assert SignatureScheme.ECDSA_P384.value == "ecdsa_p384"
    
    def test_post_quantum_schemes(self):
        """Test post-quantum signature schemes exist."""
        assert SignatureScheme.ML_DSA_65.value == "ml_dsa_65"
        assert SignatureScheme.SLH_DSA_128S.value == "slh_dsa_128s"
        assert SignatureScheme.FALCON_1024.value == "falcon_1024"
