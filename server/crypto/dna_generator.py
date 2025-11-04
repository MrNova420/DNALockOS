"""
DNA-Key Authentication System - DNA Key Generation

Implements the DNA key generation algorithm that creates thousands
of segments forming a unique authentication credential.

Generation follows the algorithm specified in the blueprint:
- 40% Entropy segments
- 10% Policy segments  
- 5% Hash segments
- 5% Temporal segments
- 20% Capability segments
- 10% Signature segments
- 10% Metadata segments
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import secrets
import hashlib

from server.crypto.dna_key import (
    DNAKey,
    DNAHelix,
    DNASegment,
    SegmentType,
    SecurityLevel,
    IssuerInfo,
    SubjectInfo,
    CryptographicMaterial,
    PolicyBinding,
    VisualDNA
)
from server.crypto.signatures import generate_ed25519_keypair


class DNAKeyGenerator:
    """
    Generator for DNA authentication keys.
    
    Creates DNA keys with specified security levels, containing
    thousands of cryptographically secure segments.
    """
    
    # Segment counts per security level
    SEGMENT_COUNTS = {
        SecurityLevel.STANDARD: 1024,      # ~100KB
        SecurityLevel.ENHANCED: 16384,     # ~1.5MB
        SecurityLevel.MAXIMUM: 65536,      # ~6MB
        SecurityLevel.GOVERNMENT: 262144   # ~25MB
    }
    
    # Distribution of segment types (percentages)
    SEGMENT_DISTRIBUTION = {
        SegmentType.ENTROPY: 0.40,      # 40%
        SegmentType.POLICY: 0.10,       # 10%
        SegmentType.HASH: 0.05,         # 5%
        SegmentType.TEMPORAL: 0.05,     # 5%
        SegmentType.CAPABILITY: 0.20,   # 20%
        SegmentType.SIGNATURE: 0.10,    # 10%
        SegmentType.METADATA: 0.10      # 10%
    }
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.STANDARD):
        """
        Initialize DNA key generator.
        
        Args:
            security_level: Security level determining segment count
        """
        self.security_level = security_level
        self.segment_count = self.SEGMENT_COUNTS[security_level]
    
    def generate(
        self,
        subject_id: str,
        subject_type: str = "human",
        policy_id: str = "default-policy-v1",
        validity_days: int = 365,
        issuer_org: str = "DNAKeyAuthSystem",
        **kwargs
    ) -> DNAKey:
        """
        Generate a complete DNA authentication key.
        
        Args:
            subject_id: Unique identifier for the subject
            subject_type: Type of subject (human, device, service)
            policy_id: Policy ID to bind
            validity_days: Number of days until expiration
            issuer_org: Issuing organization ID
            **kwargs: Additional parameters
            
        Returns:
            Complete DNAKey object
            
        Example:
            >>> generator = DNAKeyGenerator(SecurityLevel.STANDARD)
            >>> key = generator.generate(
            ...     subject_id="user@example.com",
            ...     subject_type="human",
            ...     policy_id="standard-access-v1"
            ... )
        """
        # Generate Ed25519 key pair
        signing_key, verify_key = generate_ed25519_keypair()
        
        # Create timestamps
        created = datetime.now(timezone.utc)
        expires = created + timedelta(days=validity_days)
        
        # Generate DNA segments
        segments = self._generate_segments(
            subject_id=subject_id,
            signing_key=signing_key
        )
        
        # Create helix and compute checksum
        helix = DNAHelix(segments=segments)
        helix.compute_checksum()
        
        # Create issuer info
        issuer_key, issuer_verify_key = generate_ed25519_keypair()
        issuer = IssuerInfo(
            organization_id=issuer_org,
            issuer_public_key=issuer_verify_key.to_bytes()
        )
        
        # Create subject info
        attributes_hash = hashlib.sha3_512(
            f"{subject_id}:{subject_type}".encode()
        ).hexdigest()
        
        subject = SubjectInfo(
            subject_id=hashlib.sha3_512(subject_id.encode()).hexdigest(),
            subject_type=subject_type,
            attributes_hash=attributes_hash
        )
        
        # Create cryptographic material
        crypto_material = CryptographicMaterial(
            algorithm="Ed25519",
            public_key=verify_key.to_bytes(),
            salt=secrets.token_bytes(32)
        )
        
        # Create policy binding
        policy = PolicyBinding(
            policy_id=policy_id,
            policy_version="1.0",
            policy_hash=hashlib.sha3_512(policy_id.encode()).hexdigest(),
            mfa_required=kwargs.get("mfa_required", False),
            biometric_required=kwargs.get("biometric_required", False),
            device_binding_required=kwargs.get("device_binding_required", False)
        )
        
        # Create visual DNA
        visual = VisualDNA()
        
        # Assemble DNA key
        dna_key = DNAKey(
            created_timestamp=created,
            expires_timestamp=expires,
            issuer=issuer,
            subject=subject,
            dna_helix=helix,
            cryptographic_material=crypto_material,
            policy_binding=policy,
            visual_dna=visual
        )
        
        # Sign the DNA key with issuer key
        key_data = self._serialize_for_signing(dna_key)
        issuer.issuer_signature = issuer_key.sign(key_data)
        
        return dna_key
    
    def _generate_segments(
        self,
        subject_id: str,
        signing_key: Any
    ) -> List[DNASegment]:
        """
        Generate all DNA segments according to distribution.
        
        Args:
            subject_id: Subject identifier
            signing_key: Signing key for signature segments
            
        Returns:
            List of DNASegment objects
        """
        segments = []
        position = 0
        
        # Calculate segment counts per type
        # Use explicit calculation to ensure we hit exact count
        counts = {}
        total_assigned = 0
        distributions = list(self.SEGMENT_DISTRIBUTION.items())
        
        # Calculate all but last
        for seg_type, percentage in distributions[:-1]:
            count = int(self.segment_count * percentage)
            counts[seg_type] = count
            total_assigned += count
        
        # Last one gets remainder to ensure exact total
        last_type, _ = distributions[-1]
        counts[last_type] = self.segment_count - total_assigned
        
        # Generate entropy segments (40%)
        for _ in range(counts[SegmentType.ENTROPY]):
            data = secrets.token_bytes(32)
            segments.append(DNASegment(
                position=position,
                type=SegmentType.ENTROPY,
                data=data
            ))
            position += 1
        
        # Generate policy segments (10%)
        for i in range(counts[SegmentType.POLICY]):
            data = self._generate_policy_data(i)
            segments.append(DNASegment(
                position=position,
                type=SegmentType.POLICY,
                data=data
            ))
            position += 1
        
        # Generate hash segments (5%)
        identity_hash = hashlib.sha3_512(subject_id.encode()).digest()
        for i in range(counts[SegmentType.HASH]):
            # Split hash across segments
            start = (i * len(identity_hash)) // counts[SegmentType.HASH]
            end = ((i + 1) * len(identity_hash)) // counts[SegmentType.HASH]
            data = identity_hash[start:end]
            
            segments.append(DNASegment(
                position=position,
                type=SegmentType.HASH,
                data=data
            ))
            position += 1
        
        # Generate temporal segments (5%)
        for i in range(counts[SegmentType.TEMPORAL]):
            data = self._generate_temporal_data(i)
            segments.append(DNASegment(
                position=position,
                type=SegmentType.TEMPORAL,
                data=data
            ))
            position += 1
        
        # Generate capability segments (20%)
        for i in range(counts[SegmentType.CAPABILITY]):
            data = self._generate_capability_data(i)
            segments.append(DNASegment(
                position=position,
                type=SegmentType.CAPABILITY,
                data=data
            ))
            position += 1
        
        # Generate signature segments (10%)
        for i in range(counts[SegmentType.SIGNATURE]):
            data = self._generate_signature_data(i, signing_key)
            segments.append(DNASegment(
                position=position,
                type=SegmentType.SIGNATURE,
                data=data
            ))
            position += 1
        
        # Generate metadata segments (10%)
        for i in range(counts[SegmentType.METADATA]):
            data = self._generate_metadata(i)
            segments.append(DNASegment(
                position=position,
                type=SegmentType.METADATA,
                data=data
            ))
            position += 1
        
        # Cryptographically shuffle segments for security
        segments = self._cryptographic_shuffle(segments)
        
        return segments
    
    def _generate_policy_data(self, index: int) -> bytes:
        """Generate policy segment data."""
        # For now, generate random policy data
        # In production, this would encode actual policy rules
        return secrets.token_bytes(64) + index.to_bytes(4, 'big')
    
    def _generate_temporal_data(self, index: int) -> bytes:
        """Generate temporal segment data."""
        timestamp = datetime.now(timezone.utc).timestamp()
        data = int(timestamp).to_bytes(8, 'big')
        data += index.to_bytes(4, 'big')
        data += secrets.token_bytes(4)
        return data
    
    def _generate_capability_data(self, index: int) -> bytes:
        """Generate capability segment data."""
        # Capability flags + random data
        capabilities = secrets.randbits(32).to_bytes(4, 'big')
        return capabilities + secrets.token_bytes(28) + index.to_bytes(4, 'big')
    
    def _generate_signature_data(self, index: int, signing_key: Any) -> bytes:
        """Generate signature segment data."""
        # Sign the index to create verifiable segment
        message = f"segment-{index}".encode()
        signature = signing_key.sign(message)
        # Use part of signature as segment data
        return signature[:32] + index.to_bytes(4, 'big')
    
    def _generate_metadata(self, index: int) -> bytes:
        """Generate metadata segment data."""
        return secrets.token_bytes(28) + index.to_bytes(4, 'big')
    
    def _cryptographic_shuffle(self, segments: List[DNASegment]) -> List[DNASegment]:
        """
        Cryptographically shuffle segments.
        
        Uses Fisher-Yates shuffle with CSPRNG for security.
        Position markers are preserved.
        
        Args:
            segments: List of segments to shuffle
            
        Returns:
            Shuffled list of segments
        """
        shuffled = segments.copy()
        n = len(shuffled)
        
        for i in range(n - 1, 0, -1):
            # Use secrets.randbelow for cryptographically secure random
            j = secrets.randbelow(i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        
        return shuffled
    
    def _serialize_for_signing(self, dna_key: DNAKey) -> bytes:
        """
        Serialize DNA key for signing.
        
        Args:
            dna_key: DNA key to serialize
            
        Returns:
            Bytes to sign
        """
        # Create deterministic representation
        data = f"{dna_key.key_id}:{dna_key.created_timestamp.isoformat()}"
        data += f":{dna_key.subject.subject_id}"
        data += f":{dna_key.dna_helix.checksum}"
        
        return data.encode()


def generate_dna_key(
    subject_id: str,
    security_level: SecurityLevel = SecurityLevel.STANDARD,
    **kwargs
) -> DNAKey:
    """
    Convenience function to generate a DNA key.
    
    Args:
        subject_id: Unique identifier for the subject
        security_level: Security level for the key
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated DNAKey
        
    Example:
        >>> from server.crypto.dna_generator import generate_dna_key, SecurityLevel
        >>> key = generate_dna_key("user@example.com", SecurityLevel.ENHANCED)
        >>> print(f"Generated key with {key.dna_helix.segment_count} segments")
    """
    generator = DNAKeyGenerator(security_level)
    return generator.generate(subject_id, **kwargs)
