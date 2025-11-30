"""
Tests for Distributed Ledger Module.

Tests the blockchain-based DNA strand registry including:
- Block creation and verification
- Transaction processing
- DNA strand registration
- Ownership verification
- Revocation management
- Chain integrity verification
"""

import secrets
from datetime import datetime, timedelta, timezone

import pytest

from server.security.distributed_ledger import (
    Block,
    BlockchainNetwork,
    BlockHeader,
    DNARegistryEntry,
    DNASmartContract,
    DNAStrandRegistry,
    DNAStrandStatus,
    DNATransaction,
    TransactionStatus,
)


class TestBlockchainNetwork:
    """Test blockchain network enumeration."""
    
    def test_network_types_exist(self):
        """Test that all network types exist."""
        assert BlockchainNetwork.DNA_MAINNET.value == "dna_mainnet"
        assert BlockchainNetwork.DNA_TESTNET.value == "dna_testnet"
        assert BlockchainNetwork.ETHEREUM.value == "ethereum"
        assert BlockchainNetwork.POLYGON.value == "polygon"
        assert BlockchainNetwork.PRIVATE_CHAIN.value == "private_chain"


class TestTransactionStatus:
    """Test transaction status enumeration."""
    
    def test_status_values(self):
        """Test transaction status values."""
        assert TransactionStatus.PENDING.value == "pending"
        assert TransactionStatus.CONFIRMED.value == "confirmed"
        assert TransactionStatus.FAILED.value == "failed"
        assert TransactionStatus.REVERTED.value == "reverted"


class TestDNAStrandStatus:
    """Test DNA strand status enumeration."""
    
    def test_strand_status_values(self):
        """Test strand status values."""
        assert DNAStrandStatus.ACTIVE.value == "active"
        assert DNAStrandStatus.SUSPENDED.value == "suspended"
        assert DNAStrandStatus.REVOKED.value == "revoked"
        assert DNAStrandStatus.EXPIRED.value == "expired"


class TestBlockHeader:
    """Test block header functionality."""
    
    def test_create_block_header(self):
        """Test creating a block header."""
        header = BlockHeader(
            block_number=1,
            previous_hash="0" * 64,
            merkle_root="abc123",
            timestamp=datetime.now(timezone.utc),
            nonce=12345,
            difficulty=1,
            validator="validator1"
        )
        
        assert header.block_number == 1
        assert header.nonce == 12345
    
    def test_compute_hash(self):
        """Test hash computation."""
        header = BlockHeader(
            block_number=1,
            previous_hash="0" * 64,
            merkle_root="abc123",
            timestamp=datetime.now(timezone.utc),
            nonce=12345,
            difficulty=1,
            validator="validator1"
        )
        
        hash1 = header.compute_hash()
        hash2 = header.compute_hash()
        
        assert len(hash1) == 64  # SHA3-256 hex output
        assert hash1 == hash2  # Deterministic
    
    def test_different_headers_different_hashes(self):
        """Test that different headers have different hashes."""
        timestamp = datetime.now(timezone.utc)
        
        header1 = BlockHeader(
            block_number=1,
            previous_hash="0" * 64,
            merkle_root="abc123",
            timestamp=timestamp,
            nonce=12345,
            difficulty=1,
            validator="validator1"
        )
        
        header2 = BlockHeader(
            block_number=2,
            previous_hash="0" * 64,
            merkle_root="abc123",
            timestamp=timestamp,
            nonce=12345,
            difficulty=1,
            validator="validator1"
        )
        
        assert header1.compute_hash() != header2.compute_hash()


class TestDNATransaction:
    """Test DNA transaction functionality."""
    
    def test_create_transaction(self):
        """Test creating a transaction."""
        tx = DNATransaction(
            transaction_id="tx_123",
            transaction_type="register",
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner_address_1",
            timestamp=datetime.now(timezone.utc),
            signature=b"signature_bytes"
        )
        
        assert tx.transaction_id == "tx_123"
        assert tx.transaction_type == "register"
        assert tx.status == TransactionStatus.PENDING
    
    def test_transaction_hash(self):
        """Test transaction hash computation."""
        tx = DNATransaction(
            transaction_id="tx_123",
            transaction_type="register",
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner_address_1",
            timestamp=datetime.now(timezone.utc),
            signature=b"signature_bytes"
        )
        
        tx_hash = tx.compute_hash()
        
        assert len(tx_hash) == 64
    
    def test_transaction_to_dict(self):
        """Test transaction serialization."""
        tx = DNATransaction(
            transaction_id="tx_123",
            transaction_type="register",
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner_address_1",
            timestamp=datetime.now(timezone.utc),
            signature=b"signature_bytes"
        )
        
        result = tx.to_dict()
        
        assert result["transaction_id"] == "tx_123"
        assert result["transaction_type"] == "register"
        assert result["dna_key_id"] == "dna-key-001"


class TestBlock:
    """Test block functionality."""
    
    def test_create_block(self):
        """Test creating a block."""
        header = BlockHeader(
            block_number=1,
            previous_hash="0" * 64,
            merkle_root="",
            timestamp=datetime.now(timezone.utc),
            nonce=0,
            difficulty=1,
            validator="validator1"
        )
        
        block = Block(header=header, transactions=[])
        
        assert block.header.block_number == 1
        assert block.block_hash != ""
    
    def test_merkle_root_computation(self):
        """Test Merkle root computation."""
        header = BlockHeader(
            block_number=1,
            previous_hash="0" * 64,
            merkle_root="",
            timestamp=datetime.now(timezone.utc),
            nonce=0,
            difficulty=1,
            validator="validator1"
        )
        
        tx1 = DNATransaction(
            transaction_id="tx_1",
            transaction_type="register",
            dna_key_id="key1",
            dna_checksum="checksum1",
            owner_address="owner1",
            timestamp=datetime.now(timezone.utc),
            signature=b"sig1"
        )
        
        tx2 = DNATransaction(
            transaction_id="tx_2",
            transaction_type="register",
            dna_key_id="key2",
            dna_checksum="checksum2",
            owner_address="owner2",
            timestamp=datetime.now(timezone.utc),
            signature=b"sig2"
        )
        
        block = Block(header=header, transactions=[tx1, tx2])
        merkle_root = block.compute_merkle_root()
        
        assert len(merkle_root) == 64
    
    def test_block_integrity_verification(self):
        """Test block integrity verification."""
        header = BlockHeader(
            block_number=1,
            previous_hash="0" * 64,
            merkle_root="",
            timestamp=datetime.now(timezone.utc),
            nonce=0,
            difficulty=1,
            validator="validator1"
        )
        
        block = Block(header=header, transactions=[])
        block.header.merkle_root = block.compute_merkle_root()
        
        assert block.verify_integrity() is True


class TestDNAStrandRegistry:
    """Test DNA strand registry functionality."""
    
    def test_create_registry(self):
        """Test creating a registry."""
        registry = DNAStrandRegistry()
        
        assert registry is not None
        assert registry.network == BlockchainNetwork.DNA_MAINNET
    
    def test_create_registry_with_network(self):
        """Test creating registry with specific network."""
        registry = DNAStrandRegistry(network=BlockchainNetwork.DNA_TESTNET)
        
        assert registry.network == BlockchainNetwork.DNA_TESTNET
    
    def test_register_strand(self):
        """Test registering a DNA strand."""
        registry = DNAStrandRegistry()
        
        tx = registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="checksum123abc",
            owner_address="owner_0x123",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"owner_signature"
        )
        
        assert tx.transaction_type == "register"
        assert tx.status == TransactionStatus.CONFIRMED
        assert tx.block_number is not None
    
    def test_verify_strand_success(self):
        """Test verifying a registered strand."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="checksum123abc",
            owner_address="owner_0x123",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"owner_signature"
        )
        
        is_valid, entry = registry.verify_strand("dna-key-001", "checksum123abc")
        
        assert is_valid is True
        assert entry is not None
        assert entry.status == DNAStrandStatus.ACTIVE
    
    def test_verify_strand_wrong_checksum(self):
        """Test verifying strand with wrong checksum."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="correct_checksum",
            owner_address="owner_0x123",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"owner_signature"
        )
        
        is_valid, entry = registry.verify_strand("dna-key-001", "wrong_checksum")
        
        assert is_valid is False
    
    def test_verify_unregistered_strand(self):
        """Test verifying unregistered strand."""
        registry = DNAStrandRegistry()
        
        is_valid, entry = registry.verify_strand("nonexistent-key", "checksum")
        
        assert is_valid is False
        assert entry is None
    
    def test_revoke_strand(self):
        """Test revoking a DNA strand."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner_0x123",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"owner_signature"
        )
        
        revoke_tx = registry.revoke_strand(
            dna_key_id="dna-key-001",
            owner_signature=b"revoke_signature",
            reason="Key compromised"
        )
        
        assert revoke_tx.transaction_type == "revoke"
        
        # Verify strand is now revoked
        is_valid, entry = registry.verify_strand("dna-key-001", "checksum123")
        assert is_valid is False
        assert entry.status == DNAStrandStatus.REVOKED
    
    def test_transfer_ownership(self):
        """Test transferring ownership."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner_0x123",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"owner_signature"
        )
        
        transfer_tx = registry.transfer_ownership(
            dna_key_id="dna-key-001",
            new_owner_address="new_owner_0x456",
            current_owner_signature=b"current_sig",
            new_owner_signature=b"new_sig"
        )
        
        assert transfer_tx.transaction_type == "transfer"
        
        # Verify new owner
        entry = registry.get_entry("dna-key-001")
        assert entry.owner_address == "new_owner_0x456"
    
    def test_get_owner_strands(self):
        """Test getting all strands owned by an address."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="key-1",
            dna_checksum="checksum1",
            owner_address="owner_A",
            security_level="standard",
            segment_count=1000,
            signature=b"sig1"
        )
        
        registry.register_strand(
            dna_key_id="key-2",
            dna_checksum="checksum2",
            owner_address="owner_A",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"sig2"
        )
        
        registry.register_strand(
            dna_key_id="key-3",
            dna_checksum="checksum3",
            owner_address="owner_B",
            security_level="standard",
            segment_count=1000,
            signature=b"sig3"
        )
        
        owner_a_strands = registry.get_owner_strands("owner_A")
        
        assert len(owner_a_strands) == 2
    
    def test_get_audit_trail(self):
        """Test getting audit trail for a strand."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner_0x123",
            security_level="ultimate",
            segment_count=1000000,
            signature=b"owner_signature"
        )
        
        registry.transfer_ownership(
            dna_key_id="dna-key-001",
            new_owner_address="new_owner",
            current_owner_signature=b"sig1",
            new_owner_signature=b"sig2"
        )
        
        audit_trail = registry.get_audit_trail("dna-key-001")
        
        assert len(audit_trail) == 2  # register + transfer
    
    def test_chain_integrity(self):
        """Test blockchain integrity verification."""
        registry = DNAStrandRegistry()
        
        for i in range(5):
            registry.register_strand(
                dna_key_id=f"key-{i}",
                dna_checksum=f"checksum-{i}",
                owner_address="owner",
                security_level="standard",
                segment_count=1000,
                signature=b"sig"
            )
        
        is_valid, issues = registry.verify_chain_integrity()
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_duplicate_registration_fails(self):
        """Test that duplicate registration fails."""
        registry = DNAStrandRegistry()
        
        registry.register_strand(
            dna_key_id="dna-key-001",
            dna_checksum="checksum123",
            owner_address="owner",
            security_level="standard",
            segment_count=1000,
            signature=b"sig"
        )
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register_strand(
                dna_key_id="dna-key-001",
                dna_checksum="checksum456",
                owner_address="owner2",
                security_level="standard",
                segment_count=1000,
                signature=b"sig2"
            )


class TestDNASmartContract:
    """Test DNA smart contract functionality."""
    
    def test_create_smart_contract(self):
        """Test creating a smart contract."""
        registry = DNAStrandRegistry()
        contract = DNASmartContract(registry)
        
        assert contract is not None
        assert contract.registry is registry
    
    def test_set_access_policy(self):
        """Test setting access policy."""
        registry = DNAStrandRegistry()
        contract = DNASmartContract(registry)
        
        registry.register_strand(
            dna_key_id="key-001",
            dna_checksum="checksum",
            owner_address="owner",
            security_level="standard",
            segment_count=1000,
            signature=b"sig"
        )
        
        policy = {
            "allowed_addresses": ["user1", "user2"],
            "allowed_actions": ["read", "verify"]
        }
        
        contract.set_access_policy("key-001", policy, b"owner_sig")
        
        # Check owner access
        allowed, reason = contract.check_access("key-001", "owner", "any_action")
        assert allowed is True
    
    def test_check_access_allowed(self):
        """Test access check for allowed user."""
        registry = DNAStrandRegistry()
        contract = DNASmartContract(registry)
        
        registry.register_strand(
            dna_key_id="key-001",
            dna_checksum="checksum",
            owner_address="owner",
            security_level="standard",
            segment_count=1000,
            signature=b"sig"
        )
        
        policy = {
            "allowed_addresses": ["user1"],
            "allowed_actions": ["read"]
        }
        
        contract.set_access_policy("key-001", policy, b"owner_sig")
        
        allowed, reason = contract.check_access("key-001", "user1", "read")
        assert allowed is True
    
    def test_check_access_denied(self):
        """Test access check for denied user."""
        registry = DNAStrandRegistry()
        contract = DNASmartContract(registry)
        
        registry.register_strand(
            dna_key_id="key-001",
            dna_checksum="checksum",
            owner_address="owner",
            security_level="standard",
            segment_count=1000,
            signature=b"sig"
        )
        
        allowed, reason = contract.check_access("key-001", "unauthorized_user", "read")
        assert allowed is False
    
    def test_multi_sig_requirement(self):
        """Test multi-signature requirement."""
        registry = DNAStrandRegistry()
        contract = DNASmartContract(registry)
        
        contract.require_multi_sig("key-001", 3)
        
        # 2 signatures should fail
        assert contract.verify_multi_sig("key-001", [b"sig1", b"sig2"]) is False
        
        # 3 signatures should pass
        assert contract.verify_multi_sig("key-001", [b"sig1", b"sig2", b"sig3"]) is True


class TestDNARegistryEntry:
    """Test DNA registry entry."""
    
    def test_create_entry(self):
        """Test creating a registry entry."""
        entry = DNARegistryEntry(
            dna_key_id="key-001",
            dna_checksum="checksum123",
            owner_address="owner",
            status=DNAStrandStatus.ACTIVE,
            registration_timestamp=datetime.now(timezone.utc),
            registration_tx_id="tx_001",
            registration_block=1,
            security_level="ultimate",
            segment_count=1000000
        )
        
        assert entry.dna_key_id == "key-001"
        assert entry.status == DNAStrandStatus.ACTIVE
    
    def test_entry_to_dict(self):
        """Test entry serialization."""
        entry = DNARegistryEntry(
            dna_key_id="key-001",
            dna_checksum="checksum123",
            owner_address="owner",
            status=DNAStrandStatus.ACTIVE,
            registration_timestamp=datetime.now(timezone.utc),
            registration_tx_id="tx_001",
            registration_block=1,
            security_level="ultimate",
            segment_count=1000000
        )
        
        result = entry.to_dict()
        
        assert result["dna_key_id"] == "key-001"
        assert result["status"] == "active"
        assert result["security_level"] == "ultimate"
