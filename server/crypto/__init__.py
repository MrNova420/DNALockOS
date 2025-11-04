"""
DNA-Key Authentication System - Cryptographic Module

This module implements the core cryptographic primitives for the DNA-Key
authentication system following FIPS 140-3 and industry best practices.

Implements:
- Ed25519 digital signatures
- X25519 key exchange
- AES-256-GCM encryption
- HKDF key derivation
- Argon2id password hashing
- CSPRNG with entropy monitoring

All implementations use approved libraries (PyNaCl/libsodium, cryptography).
"""

__version__ = "0.1.0"
