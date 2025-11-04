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
    """DNA segment types (digital bases)."""

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


class SecurityLevel(Enum):
    """Security levels determining segment count."""

    STANDARD = "standard"  # 1,024 segments (~100KB)
    ENHANCED = "enhanced"  # 16,384 segments (~1.5MB)
    MAXIMUM = "maximum"  # 65,536 segments (~6MB)
    GOVERNMENT = "government"  # 262,144 segments (~25MB)


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
    thousands of segments that together form a unique authentication
    identity, analogous to a complete genome.
    """

    format_version: str = "1.0"
    key_id: Optional[str] = None
    created_timestamp: Optional[datetime] = None
    expires_timestamp: Optional[datetime] = None

    issuer: Optional[IssuerInfo] = None
    subject: Optional[SubjectInfo] = None
    dna_helix: DNAHelix = field(default_factory=DNAHelix)
    cryptographic_material: Optional[CryptographicMaterial] = None
    policy_binding: Optional[PolicyBinding] = None
    visual_dna: VisualDNA = field(default_factory=VisualDNA)

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

        return result
