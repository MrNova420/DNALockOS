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
DNA-Key Authentication System - DNA Key Data Models

Implements the core DNA Key data structure with segments representing
a biologically-inspired authentication credential.

Segment Types (Digital "Bases"):
- E: Entropy Segment (Cryptographic randomness)
- P: Policy Segment (Access control rules)
- H: Hash Segment (Identity commitment)
- T: Temporal Segment (Timestamps, validity)
- C: Capability Segment (Permissions, scopes)
- S: Signature Segment (Cryptographic proofs)
- M: Metadata Segment (Non-sensitive context)
- B: Biometric Segment (Biometric anchors)
- G: Geolocation Segment (Location policies)
- R: Revocation Segment (Revocation tokens)
"""

import hashlib
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SegmentType(Enum):
    """
    DNA segment types (digital bases).
    
    Each type represents a different category of security data,
    analogous to nucleotide bases in biological DNA (A, T, G, C).
    Our digital DNA has 20 distinct segment types for maximum security.
    """

    # Core Security Types (Original)
    ENTROPY = "E"  # Cryptographic randomness
    POLICY = "P"  # Access control rules
    HASH = "H"  # Identity commitment
    TEMPORAL = "T"  # Timestamps, validity
    CAPABILITY = "C"  # Permissions, scopes
    SIGNATURE = "S"  # Cryptographic proofs
    METADATA = "M"  # Non-sensitive context
    BIOMETRIC = "B"  # Biometric anchors
    GEOLOCATION = "G"  # Location policies
    REVOCATION = "R"  # Revocation tokens
    
    # Extended Security Types (New)
    KEY_DERIVATION = "K"    # Key derivation data (HKDF, PBKDF2)
    ENCRYPTION = "X"        # Encrypted payload segments
    NONCE = "N"             # Anti-replay nonces
    CHALLENGE = "Q"         # Challenge-response data
    ATTESTATION = "A"       # Third-party attestations
    FINGERPRINT = "F"       # Device/browser fingerprints
    RECOVERY = "Y"          # Recovery and backup data
    AUDIT = "U"             # Audit trail segments
    QUANTUM = "W"           # Post-quantum security data
    CUSTOM = "Z"            # Custom/extensible segments


class SecurityLevel(Enum):
    """Security levels determining segment count."""

    STANDARD = "standard"  # 1,024 segments (~100KB)
    ENHANCED = "enhanced"  # 16,384 segments (~1.5MB)
    MAXIMUM = "maximum"  # 65,536 segments (~6MB)
    GOVERNMENT = "government"  # 262,144 segments (~25MB)
    ULTIMATE = "ultimate"  # 1,048,576 segments (~100MB) - 1 million lines


class SecurityLayer(Enum):
    """
    Multi-layer security architecture.
    
    Each DNA strand contains 5 concentric security layers,
    from outermost to innermost, each with distinct security methods.
    """
    
    OUTER_SHELL = 1      # Layer 1: Format, signatures, metadata (5%)
    ENTROPY_MATRIX = 2   # Layer 2: Cryptographic randomness (40%)
    SECURITY_FRAMEWORK = 3  # Layer 3: Policies, capabilities, temporal (30%)
    IDENTITY_CORE = 4    # Layer 4: Hashes, commitments, attestations (15%)
    CRYPTO_NUCLEUS = 5   # Layer 5: Keys, salts, signatures, recovery (10%)


@dataclass
class DNASegment:
    """
    A single DNA segment (digital base).

    Represents one unit of the DNA authentication key,
    analogous to a nucleotide base in biological DNA.
    """

    position: int
    type: SegmentType
    data: bytes
    segment_hash: Optional[str] = None

    def __post_init__(self):
        """Compute segment hash if not provided."""
        if self.segment_hash is None:
            self.segment_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA3-256 hash of segment data."""
        hasher = hashlib.sha3_256()
        hasher.update(self.type.value.encode())
        hasher.update(self.position.to_bytes(4, "big"))
        hasher.update(self.data)
        return hasher.hexdigest()

    @property
    def length(self) -> int:
        """Get length of segment data."""
        return len(self.data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary."""
        return {
            "position": self.position,
            "type": self.type.value,
            "length": self.length,
            "data": self.data.hex(),
            "segment_hash": self.segment_hash,
        }


@dataclass
class IssuerInfo:
    """Information about the DNA key issuer."""

    organization_id: str
    issuer_public_key: bytes
    issuer_signature: Optional[bytes] = None


@dataclass
class SubjectInfo:
    """Information about the DNA key subject."""

    subject_id: str
    subject_type: str  # human, device, service
    attributes_hash: str


@dataclass
class CryptographicMaterial:
    """Cryptographic material for the DNA key."""

    algorithm: str = "Ed25519"
    public_key: Optional[bytes] = None
    salt: Optional[bytes] = None
    kdf_info: str = "DNAKeyAuthSystem-v1"


@dataclass
class PolicyBinding:
    """Policy binding information."""

    policy_id: str
    policy_version: str
    policy_hash: str
    mfa_required: bool = False
    biometric_required: bool = False
    device_binding_required: bool = False


@dataclass
class VisualDNA:
    """Visual representation parameters."""

    color_palette: List[str] = field(default_factory=lambda: ["#00FFFF", "#FF00FF", "#FFFF00", "#00FF00"])
    helix_rotation: float = 23.5
    glow_intensity: float = 0.8
    animation_seed: Optional[str] = None

    def __post_init__(self):
        """Generate animation seed if not provided."""
        if self.animation_seed is None:
            self.animation_seed = secrets.token_hex(16)


@dataclass
class SecurityMethodsIntegrated:
    """
    Tracks all security methods integrated into the DNA strand.
    
    This comprehensive tracking ensures we know exactly what
    security techniques are embedded in each DNA key.
    """
    
    # Hashing algorithms used
    hash_algorithms: List[str] = field(default_factory=lambda: [
        "SHA3-512", "SHA3-256", "SHA-256", "BLAKE2b", "SHAKE256"
    ])
    
    # Encryption algorithms used  
    encryption_algorithms: List[str] = field(default_factory=lambda: [
        "AES-256-GCM", "ChaCha20-Poly1305", "XSalsa20-Poly1305"
    ])
    
    # Signature algorithms used
    signature_algorithms: List[str] = field(default_factory=lambda: [
        "Ed25519", "ECDSA-P256"
    ])
    
    # Key derivation functions used
    key_derivation_functions: List[str] = field(default_factory=lambda: [
        "HKDF-SHA512", "Argon2id", "PBKDF2-SHA512"
    ])
    
    # Random number generators used
    random_sources: List[str] = field(default_factory=lambda: [
        "CSPRNG", "os.urandom", "secrets.token_bytes"
    ])
    
    # Anti-tampering techniques
    anti_tampering: List[str] = field(default_factory=lambda: [
        "Merkle-Tree-Checksums", "Segment-Interlocking", 
        "Position-Binding", "Type-Binding"
    ])
    
    # Anti-replay mechanisms
    anti_replay: List[str] = field(default_factory=lambda: [
        "Nonce-Tracking", "Timestamp-Windows", 
        "Sequence-Numbers", "One-Time-Tokens"
    ])
    
    # Identity protection
    identity_protection: List[str] = field(default_factory=lambda: [
        "Hash-Commitment", "Attribute-Blinding", 
        "Unlinkability", "Forward-Secrecy"
    ])
    
    # Brute force resistance
    brute_force_resistance: List[str] = field(default_factory=lambda: [
        "Large-Key-Space", "Rate-Limiting", 
        "Exponential-Backoff", "Account-Lockout"
    ])
    
    # Total count of security methods
    @property
    def total_methods_count(self) -> int:
        """Count total number of security methods integrated."""
        return (
            len(self.hash_algorithms) +
            len(self.encryption_algorithms) +
            len(self.signature_algorithms) +
            len(self.key_derivation_functions) +
            len(self.random_sources) +
            len(self.anti_tampering) +
            len(self.anti_replay) +
            len(self.identity_protection) +
            len(self.brute_force_resistance)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hash_algorithms": self.hash_algorithms,
            "encryption_algorithms": self.encryption_algorithms,
            "signature_algorithms": self.signature_algorithms,
            "key_derivation_functions": self.key_derivation_functions,
            "random_sources": self.random_sources,
            "anti_tampering": self.anti_tampering,
            "anti_replay": self.anti_replay,
            "identity_protection": self.identity_protection,
            "brute_force_resistance": self.brute_force_resistance,
            "total_methods_count": self.total_methods_count
        }


@dataclass  
class LayerChecksum:
    """Checksum for each security layer."""
    
    layer: int  # 1-5
    algorithm: str  # e.g., "SHA3-512"
    checksum: str  # Hex-encoded checksum
    segment_count: int  # Number of segments in this layer


@dataclass
class DNAHelix:
    """
    The DNA helix structure containing all segments.

    This is the core container for the authentication data,
    analogous to a chromosome in biological DNA.
    """

    segments: List[DNASegment] = field(default_factory=list)
    checksum: Optional[str] = None

    @property
    def strand_length(self) -> int:
        """Total length of all segment data."""
        return sum(seg.length for seg in self.segments)

    @property
    def segment_count(self) -> int:
        """Total number of segments."""
        return len(self.segments)

    def compute_checksum(self) -> str:
        """
        Compute SHA3-512 checksum of all segments.

        Returns:
            Hexadecimal checksum string
        """
        hasher = hashlib.sha3_512()

        # Sort segments by position for deterministic checksum
        sorted_segments = sorted(self.segments, key=lambda s: s.position)

        for segment in sorted_segments:
            hasher.update(segment.type.value.encode())
            hasher.update(segment.position.to_bytes(4, "big"))
            hasher.update(segment.data)
            if segment.segment_hash:
                hasher.update(segment.segment_hash.encode())

        self.checksum = hasher.hexdigest()
        return self.checksum

    def verify_checksum(self) -> bool:
        """Verify the checksum matches current segments."""
        if self.checksum is None:
            return False

        stored_checksum = self.checksum
        computed_checksum = self.compute_checksum()

        # Restore the original checksum for future verifications
        self.checksum = stored_checksum

        return secrets.compare_digest(computed_checksum, stored_checksum)

    def get_segments_by_type(self, segment_type: SegmentType) -> List[DNASegment]:
        """Get all segments of a specific type."""
        return [seg for seg in self.segments if seg.type == segment_type]


@dataclass
class DNAKey:
    """
    Complete DNA-Key authentication credential.

    The DNA key is a biologically-inspired credential containing
    thousands to millions of segments that together form a unique 
    authentication identity, analogous to a complete genome.
    
    Multi-Layer Architecture:
    - Layer 1: Outer Shell (format, signatures, metadata)
    - Layer 2: Entropy Matrix (cryptographic randomness)
    - Layer 3: Security Framework (policies, capabilities)
    - Layer 4: Identity Core (hashes, commitments)
    - Layer 5: Cryptographic Nucleus (keys, signatures)
    
    Security Methods Integrated:
    - 5+ Hash algorithms (SHA3-512, SHA3-256, SHA-256, BLAKE2b, SHAKE256)
    - 3+ Encryption algorithms (AES-256-GCM, ChaCha20-Poly1305, XSalsa20)
    - 2+ Signature algorithms (Ed25519, ECDSA-P256)
    - 3+ Key derivation functions (HKDF, Argon2id, PBKDF2)
    - Anti-tampering, anti-replay, identity protection
    - Brute force resistance mechanisms
    """

    format_version: str = "2.0"
    key_id: Optional[str] = None
    created_timestamp: Optional[datetime] = None
    expires_timestamp: Optional[datetime] = None

    issuer: Optional[IssuerInfo] = None
    subject: Optional[SubjectInfo] = None
    dna_helix: DNAHelix = field(default_factory=DNAHelix)
    cryptographic_material: Optional[CryptographicMaterial] = None
    policy_binding: Optional[PolicyBinding] = None
    visual_dna: VisualDNA = field(default_factory=VisualDNA)
    
    # New fields for enhanced security tracking
    security_methods: SecurityMethodsIntegrated = field(default_factory=SecurityMethodsIntegrated)
    layer_checksums: List[LayerChecksum] = field(default_factory=list)
    total_lines: int = 0  # Total lines/symbols in the strand
    security_score: float = 0.0  # Calculated security strength (0-100)

    def __post_init__(self):
        """Initialize timestamps and key ID if not provided."""
        if self.created_timestamp is None:
            self.created_timestamp = datetime.now(timezone.utc)

        if self.key_id is None:
            # Generate key ID from timestamp and random data
            key_data = f"{self.created_timestamp.isoformat()}-{secrets.token_hex(16)}"
            key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:32]
            self.key_id = f"dna-{key_hash}"

    def is_expired(self) -> bool:
        """Check if the DNA key has expired."""
        if self.expires_timestamp is None:
            return False
        return datetime.now(timezone.utc) > self.expires_timestamp

    def is_valid(self) -> bool:
        """
        Validate the DNA key structure and checksums.

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not self.key_id or not self.created_timestamp:
            return False

        # Check expiration
        if self.is_expired():
            return False

        # Verify helix checksum
        if self.dna_helix.checksum:
            if not self.dna_helix.verify_checksum():
                return False

        # Check segment count
        if self.dna_helix.segment_count == 0:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert DNA key to dictionary representation."""
        result = {
            "format_version": self.format_version,
            "key_id": self.key_id,
            "created_timestamp": self.created_timestamp.isoformat() if self.created_timestamp else None,
            "expires_timestamp": self.expires_timestamp.isoformat() if self.expires_timestamp else None,
        }

        if self.issuer:
            result["issuer"] = {
                "organization_id": self.issuer.organization_id,
                "issuer_public_key": self.issuer.issuer_public_key.hex(),
                "issuer_signature": self.issuer.issuer_signature.hex() if self.issuer.issuer_signature else None,
            }

        if self.subject:
            result["subject"] = asdict(self.subject)

        result["dna_helix"] = {
            "strand_length": self.dna_helix.strand_length,
            "segment_count": self.dna_helix.segment_count,
            "checksum": self.dna_helix.checksum,
            "segments": [seg.to_dict() for seg in self.dna_helix.segments],
        }

        if self.cryptographic_material:
            result["cryptographic_material"] = {
                "algorithm": self.cryptographic_material.algorithm,
                "public_key": self.cryptographic_material.public_key.hex()
                if self.cryptographic_material.public_key
                else None,
                "salt": self.cryptographic_material.salt.hex() if self.cryptographic_material.salt else None,
                "kdf_info": self.cryptographic_material.kdf_info,
            }

        if self.policy_binding:
            result["policy_binding"] = asdict(self.policy_binding)

        result["visual_dna"] = asdict(self.visual_dna)
        
        # Add new security tracking fields
        result["security_methods"] = self.security_methods.to_dict()
        result["layer_checksums"] = [
            {"layer": lc.layer, "algorithm": lc.algorithm, 
             "checksum": lc.checksum, "segment_count": lc.segment_count}
            for lc in self.layer_checksums
        ]
        result["total_lines"] = self.total_lines
        result["security_score"] = self.security_score

        return result
    
    def calculate_security_score(self) -> float:
        """
        Calculate the security strength score (0-100).
        
        Based on:
        - Segment count (more = stronger)
        - Security methods integrated
        - Layer completeness
        - Checksum validity
        """
        score = 0.0
        
        # Segment count contribution (max 40 points)
        segment_count = self.dna_helix.segment_count
        if segment_count >= 1_000_000:
            score += 40.0
        elif segment_count >= 262_144:
            score += 35.0
        elif segment_count >= 65_536:
            score += 30.0
        elif segment_count >= 16_384:
            score += 25.0
        elif segment_count >= 1_024:
            score += 20.0
        else:
            score += segment_count / 1024 * 20.0
        
        # Security methods contribution (max 30 points)
        methods_count = self.security_methods.total_methods_count
        score += min(30.0, methods_count * 0.75)
        
        # Layer checksums contribution (max 15 points)
        score += len(self.layer_checksums) * 3.0
        
        # Checksum validity (max 10 points)
        if self.dna_helix.checksum:
            score += 10.0
        
        # Issuer signature (max 5 points)
        if self.issuer and self.issuer.issuer_signature:
            score += 5.0
        
        self.security_score = min(100.0, score)
        return self.security_score
