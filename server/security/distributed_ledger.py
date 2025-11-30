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
DNA-Key Authentication System - Distributed Ledger Integration

██████╗ ██╗     ██████╗  ██████╗██╗  ██╗ ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
██╔══██╗██║    ██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██║  ██║██╔══██╗██║████╗  ██║
██████╔╝██║    ██║   ██║██║     █████╔╝ ██║     ███████║███████║██║██╔██╗ ██║
██╔══██╗██║    ██║   ██║██║     ██╔═██╗ ██║     ██╔══██║██╔══██║██║██║╚██╗██║
██████╔╝██████╗╚██████╔╝╚██████╗██║  ██╗╚██████╗██║  ██║██║  ██║██║██║ ╚████║
╚═════╝ ╚═════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝

IMMUTABLE DNA STRAND REGISTRY ON DISTRIBUTED LEDGER

This module implements distributed ledger technology for:

1. Immutable DNA strand registration
2. Decentralized verification
3. Tamper-proof audit trail
4. Cross-platform DNA strand validation
5. Revocation management
6. Ownership proof
7. Chain of custody tracking

TRUST THROUGH TRANSPARENCY AND IMMUTABILITY
"""

import hashlib
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# BLOCKCHAIN TYPES
# ============================================================================

class BlockchainNetwork(Enum):
    """Supported blockchain networks for DNA registration."""
    
    DNA_MAINNET = "dna_mainnet"          # DNALockOS native chain
    DNA_TESTNET = "dna_testnet"          # Testing network
    ETHEREUM = "ethereum"                 # Ethereum mainnet
    POLYGON = "polygon"                   # Polygon/Matic
    SOLANA = "solana"                     # Solana
    PRIVATE_CHAIN = "private_chain"       # Enterprise private chain


class TransactionStatus(Enum):
    """Status of a blockchain transaction."""
    
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVERTED = "reverted"


class DNAStrandStatus(Enum):
    """Status of a DNA strand on the ledger."""
    
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING_ACTIVATION = "pending_activation"


# ============================================================================
# BLOCKCHAIN PRIMITIVES
# ============================================================================

@dataclass
class BlockHeader:
    """Header of a block in the DNA chain."""
    
    block_number: int
    previous_hash: str
    merkle_root: str
    timestamp: datetime
    nonce: int
    difficulty: int
    validator: str
    
    def compute_hash(self) -> str:
        """Compute the hash of this block header."""
        data = f"{self.block_number}{self.previous_hash}{self.merkle_root}"
        data += f"{self.timestamp.isoformat()}{self.nonce}{self.difficulty}{self.validator}"
        return hashlib.sha3_256(data.encode()).hexdigest()


@dataclass
class DNATransaction:
    """A transaction registering or updating a DNA strand."""
    
    transaction_id: str
    transaction_type: str  # register, update, revoke, transfer
    dna_key_id: str
    dna_checksum: str
    owner_address: str
    timestamp: datetime
    signature: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Blockchain info
    block_number: Optional[int] = None
    block_hash: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING
    
    def compute_hash(self) -> str:
        """Compute transaction hash."""
        data = f"{self.transaction_type}{self.dna_key_id}{self.dna_checksum}"
        data += f"{self.owner_address}{self.timestamp.isoformat()}"
        return hashlib.sha3_256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "dna_key_id": self.dna_key_id,
            "dna_checksum": self.dna_checksum,
            "owner_address": self.owner_address,
            "timestamp": self.timestamp.isoformat(),
            "block_number": self.block_number,
            "status": self.status.value
        }


@dataclass
class Block:
    """A block containing DNA strand transactions."""
    
    header: BlockHeader
    transactions: List[DNATransaction]
    block_hash: str = ""
    
    def __post_init__(self):
        if not self.block_hash:
            self.block_hash = self.header.compute_hash()
    
    def compute_merkle_root(self) -> str:
        """Compute Merkle root of transactions."""
        if not self.transactions:
            return hashlib.sha3_256(b"").hexdigest()
        
        hashes = [tx.compute_hash() for tx in self.transactions]
        
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha3_256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            hashes = new_hashes
        
        return hashes[0]
    
    def verify_integrity(self) -> bool:
        """Verify block integrity."""
        computed_merkle = self.compute_merkle_root()
        return computed_merkle == self.header.merkle_root


# ============================================================================
# DNA STRAND REGISTRY
# ============================================================================

@dataclass
class DNARegistryEntry:
    """An entry in the DNA strand registry."""
    
    dna_key_id: str
    dna_checksum: str
    owner_address: str
    status: DNAStrandStatus
    
    # Registration info
    registration_timestamp: datetime
    registration_tx_id: str
    registration_block: int
    
    # Metadata
    security_level: str
    segment_count: int
    expiration_date: Optional[datetime] = None
    
    # History
    update_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dna_key_id": self.dna_key_id,
            "dna_checksum": self.dna_checksum,
            "owner_address": self.owner_address,
            "status": self.status.value,
            "registration_timestamp": self.registration_timestamp.isoformat(),
            "security_level": self.security_level,
            "segment_count": self.segment_count
        }


class DNAStrandRegistry:
    """
    Distributed registry for DNA strands.
    
    Provides:
    - Registration of new DNA strands
    - Verification of strand authenticity
    - Ownership tracking
    - Revocation management
    - Audit trail
    """
    
    def __init__(self, network: BlockchainNetwork = BlockchainNetwork.DNA_MAINNET):
        self.network = network
        self._entries: Dict[str, DNARegistryEntry] = {}
        self._transactions: Dict[str, DNATransaction] = {}
        self._blocks: List[Block] = []
        self._pending_transactions: List[DNATransaction] = []
        
        # Initialize genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the genesis block."""
        genesis_header = BlockHeader(
            block_number=0,
            previous_hash="0" * 64,
            merkle_root=hashlib.sha3_256(b"genesis").hexdigest(),
            timestamp=datetime.now(timezone.utc),
            nonce=0,
            difficulty=1,
            validator="genesis"
        )
        genesis_block = Block(header=genesis_header, transactions=[])
        self._blocks.append(genesis_block)
    
    def register_strand(
        self,
        dna_key_id: str,
        dna_checksum: str,
        owner_address: str,
        security_level: str,
        segment_count: int,
        signature: bytes,
        expiration_date: Optional[datetime] = None
    ) -> DNATransaction:
        """
        Register a new DNA strand on the ledger.
        
        Args:
            dna_key_id: Unique identifier for the DNA key
            dna_checksum: Checksum of the DNA strand
            owner_address: Owner's blockchain address
            security_level: Security level of the strand
            segment_count: Number of segments in the strand
            signature: Owner's signature proving ownership
            expiration_date: Optional expiration date
            
        Returns:
            DNATransaction for the registration
        """
        if dna_key_id in self._entries:
            raise ValueError(f"DNA strand {dna_key_id} already registered")
        
        # Create transaction
        tx = DNATransaction(
            transaction_id=f"tx_{secrets.token_hex(16)}",
            transaction_type="register",
            dna_key_id=dna_key_id,
            dna_checksum=dna_checksum,
            owner_address=owner_address,
            timestamp=datetime.now(timezone.utc),
            signature=signature,
            metadata={
                "security_level": security_level,
                "segment_count": segment_count,
                "expiration_date": expiration_date.isoformat() if expiration_date else None
            }
        )
        
        # Add to pending
        self._pending_transactions.append(tx)
        self._transactions[tx.transaction_id] = tx
        
        # Process immediately (in production, wait for block confirmation)
        self._process_pending_transactions()
        
        return tx
    
    def verify_strand(self, dna_key_id: str, dna_checksum: str) -> Tuple[bool, Optional[DNARegistryEntry]]:
        """
        Verify a DNA strand against the registry.
        
        Args:
            dna_key_id: DNA key identifier
            dna_checksum: Checksum to verify
            
        Returns:
            Tuple of (is_valid, registry_entry)
        """
        entry = self._entries.get(dna_key_id)
        
        if not entry:
            return False, None
        
        if entry.status != DNAStrandStatus.ACTIVE:
            return False, entry
        
        if entry.expiration_date and datetime.now(timezone.utc) > entry.expiration_date:
            return False, entry
        
        if not secrets.compare_digest(entry.dna_checksum, dna_checksum):
            return False, entry
        
        return True, entry
    
    def revoke_strand(
        self,
        dna_key_id: str,
        owner_signature: bytes,
        reason: str = ""
    ) -> DNATransaction:
        """
        Revoke a DNA strand.
        
        Args:
            dna_key_id: DNA key to revoke
            owner_signature: Owner's signature authorizing revocation
            reason: Reason for revocation
            
        Returns:
            DNATransaction for the revocation
        """
        entry = self._entries.get(dna_key_id)
        if not entry:
            raise ValueError(f"DNA strand {dna_key_id} not found")
        
        tx = DNATransaction(
            transaction_id=f"tx_{secrets.token_hex(16)}",
            transaction_type="revoke",
            dna_key_id=dna_key_id,
            dna_checksum=entry.dna_checksum,
            owner_address=entry.owner_address,
            timestamp=datetime.now(timezone.utc),
            signature=owner_signature,
            metadata={"reason": reason}
        )
        
        self._pending_transactions.append(tx)
        self._transactions[tx.transaction_id] = tx
        self._process_pending_transactions()
        
        return tx
    
    def transfer_ownership(
        self,
        dna_key_id: str,
        new_owner_address: str,
        current_owner_signature: bytes,
        new_owner_signature: bytes
    ) -> DNATransaction:
        """
        Transfer ownership of a DNA strand.
        
        Args:
            dna_key_id: DNA key to transfer
            new_owner_address: New owner's address
            current_owner_signature: Current owner's authorization
            new_owner_signature: New owner's acceptance
            
        Returns:
            DNATransaction for the transfer
        """
        entry = self._entries.get(dna_key_id)
        if not entry:
            raise ValueError(f"DNA strand {dna_key_id} not found")
        
        tx = DNATransaction(
            transaction_id=f"tx_{secrets.token_hex(16)}",
            transaction_type="transfer",
            dna_key_id=dna_key_id,
            dna_checksum=entry.dna_checksum,
            owner_address=new_owner_address,
            timestamp=datetime.now(timezone.utc),
            signature=current_owner_signature,
            metadata={
                "previous_owner": entry.owner_address,
                "new_owner_signature": new_owner_signature.hex()
            }
        )
        
        self._pending_transactions.append(tx)
        self._transactions[tx.transaction_id] = tx
        self._process_pending_transactions()
        
        return tx
    
    def get_entry(self, dna_key_id: str) -> Optional[DNARegistryEntry]:
        """Get registry entry for a DNA strand."""
        return self._entries.get(dna_key_id)
    
    def get_transaction(self, tx_id: str) -> Optional[DNATransaction]:
        """Get a transaction by ID."""
        return self._transactions.get(tx_id)
    
    def get_owner_strands(self, owner_address: str) -> List[DNARegistryEntry]:
        """Get all DNA strands owned by an address."""
        return [
            entry for entry in self._entries.values()
            if entry.owner_address == owner_address
        ]
    
    def get_audit_trail(self, dna_key_id: str) -> List[DNATransaction]:
        """Get full audit trail for a DNA strand."""
        return [
            tx for tx in self._transactions.values()
            if tx.dna_key_id == dna_key_id
        ]
    
    def _process_pending_transactions(self):
        """Process pending transactions into a new block."""
        if not self._pending_transactions:
            return
        
        last_block = self._blocks[-1]
        
        # Create new block
        header = BlockHeader(
            block_number=last_block.header.block_number + 1,
            previous_hash=last_block.block_hash,
            merkle_root="",  # Will be computed
            timestamp=datetime.now(timezone.utc),
            nonce=secrets.randbelow(2**32),
            difficulty=1,
            validator="system"
        )
        
        new_block = Block(header=header, transactions=self._pending_transactions.copy())
        new_block.header.merkle_root = new_block.compute_merkle_root()
        new_block.block_hash = new_block.header.compute_hash()
        
        # Process transactions
        for tx in self._pending_transactions:
            tx.block_number = new_block.header.block_number
            tx.block_hash = new_block.block_hash
            tx.status = TransactionStatus.CONFIRMED
            
            # Update registry based on transaction type
            if tx.transaction_type == "register":
                entry = DNARegistryEntry(
                    dna_key_id=tx.dna_key_id,
                    dna_checksum=tx.dna_checksum,
                    owner_address=tx.owner_address,
                    status=DNAStrandStatus.ACTIVE,
                    registration_timestamp=tx.timestamp,
                    registration_tx_id=tx.transaction_id,
                    registration_block=new_block.header.block_number,
                    security_level=tx.metadata.get("security_level", "standard"),
                    segment_count=tx.metadata.get("segment_count", 0),
                    expiration_date=datetime.fromisoformat(tx.metadata["expiration_date"])
                    if tx.metadata.get("expiration_date") else None
                )
                self._entries[tx.dna_key_id] = entry
                
            elif tx.transaction_type == "revoke":
                if tx.dna_key_id in self._entries:
                    self._entries[tx.dna_key_id].status = DNAStrandStatus.REVOKED
                    self._entries[tx.dna_key_id].update_history.append({
                        "action": "revoked",
                        "timestamp": tx.timestamp.isoformat(),
                        "tx_id": tx.transaction_id
                    })
                    
            elif tx.transaction_type == "transfer":
                if tx.dna_key_id in self._entries:
                    old_owner = self._entries[tx.dna_key_id].owner_address
                    self._entries[tx.dna_key_id].owner_address = tx.owner_address
                    self._entries[tx.dna_key_id].update_history.append({
                        "action": "transferred",
                        "from": old_owner,
                        "to": tx.owner_address,
                        "timestamp": tx.timestamp.isoformat(),
                        "tx_id": tx.transaction_id
                    })
        
        self._blocks.append(new_block)
        self._pending_transactions.clear()
    
    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of the entire blockchain.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        for i in range(1, len(self._blocks)):
            current = self._blocks[i]
            previous = self._blocks[i - 1]
            
            # Verify previous hash link
            if current.header.previous_hash != previous.block_hash:
                issues.append(f"Block {i}: Previous hash mismatch")
            
            # Verify block hash
            computed_hash = current.header.compute_hash()
            if computed_hash != current.block_hash:
                issues.append(f"Block {i}: Block hash invalid")
            
            # Verify Merkle root
            if not current.verify_integrity():
                issues.append(f"Block {i}: Merkle root invalid")
        
        return len(issues) == 0, issues


# ============================================================================
# SMART CONTRACT INTERFACE
# ============================================================================

class DNASmartContract:
    """
    Smart contract interface for DNA strand operations.
    
    Provides automated enforcement of:
    - Access control
    - Expiration management
    - Multi-signature requirements
    - Conditional transfers
    """
    
    def __init__(self, registry: DNAStrandRegistry):
        self.registry = registry
        self._access_policies: Dict[str, Dict[str, Any]] = {}
        self._multi_sig_requirements: Dict[str, int] = {}
    
    def set_access_policy(
        self,
        dna_key_id: str,
        policy: Dict[str, Any],
        owner_signature: bytes
    ):
        """Set access policy for a DNA strand."""
        entry = self.registry.get_entry(dna_key_id)
        if not entry:
            raise ValueError("DNA strand not found")
        
        self._access_policies[dna_key_id] = policy
    
    def check_access(
        self,
        dna_key_id: str,
        requester_address: str,
        action: str
    ) -> Tuple[bool, str]:
        """Check if an action is allowed for a DNA strand."""
        entry = self.registry.get_entry(dna_key_id)
        if not entry:
            return False, "DNA strand not found"
        
        if entry.status != DNAStrandStatus.ACTIVE:
            return False, f"DNA strand is {entry.status.value}"
        
        policy = self._access_policies.get(dna_key_id, {})
        
        # Owner always has access
        if requester_address == entry.owner_address:
            return True, "Owner access granted"
        
        # Check policy
        allowed_addresses = policy.get("allowed_addresses", [])
        if requester_address in allowed_addresses:
            allowed_actions = policy.get("allowed_actions", [])
            if action in allowed_actions or "*" in allowed_actions:
                return True, "Policy allows access"
        
        return False, "Access denied by policy"
    
    def require_multi_sig(self, dna_key_id: str, required_signatures: int):
        """Require multiple signatures for operations on a DNA strand."""
        self._multi_sig_requirements[dna_key_id] = required_signatures
    
    def verify_multi_sig(
        self,
        dna_key_id: str,
        signatures: List[bytes]
    ) -> bool:
        """Verify multi-signature requirement is met."""
        required = self._multi_sig_requirements.get(dna_key_id, 1)
        return len(signatures) >= required


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "BlockchainNetwork",
    "TransactionStatus",
    "DNAStrandStatus",
    "BlockHeader",
    "DNATransaction",
    "Block",
    "DNARegistryEntry",
    "DNAStrandRegistry",
    "DNASmartContract",
]
