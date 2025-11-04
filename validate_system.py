#!/usr/bin/env python3
"""
DNA-Key Authentication System - Complete System Validation
Validates all components are present and functional.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class SystemValidator:
    """Validates all system components"""
    
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.root = Path(__file__).parent
        
    def check_file(self, path: str, description: str) -> bool:
        """Check if a file exists"""
        full_path = self.root / path
        exists = full_path.exists()
        self.results.append((description, exists, str(full_path)))
        return exists
    
    def check_import(self, module: str, description: str) -> bool:
        """Check if a module can be imported"""
        try:
            __import__(module)
            self.results.append((description, True, module))
            return True
        except ImportError as e:
            self.results.append((description, False, f"{module} - {e}"))
            return False
    
    def validate_backend(self) -> Dict[str, int]:
        """Validate backend components"""
        print("\n🔷 VALIDATING BACKEND COMPONENTS...")
        
        checks = {
            "passed": 0,
            "failed": 0
        }
        
        # Crypto modules
        backend_checks = [
            ("server/crypto/signatures.py", "Ed25519 Signatures"),
            ("server/crypto/key_exchange.py", "X25519 Key Exchange"),
            ("server/crypto/encryption.py", "AES-256-GCM Encryption"),
            ("server/crypto/hashing.py", "HKDF & Argon2id"),
            ("server/crypto/dna_key.py", "DNA Key Data Model"),
            ("server/crypto/dna_generator.py", "DNA Key Generator"),
            ("server/crypto/serialization.py", "CBOR Serialization"),
            
            # Core services
            ("server/core/enrollment.py", "Enrollment Service"),
            ("server/core/authentication.py", "Authentication Service"),
            ("server/core/revocation.py", "Revocation Service"),
            
            # API
            ("server/api/main.py", "FastAPI REST API Server"),
            ("server/visual/dna_visualizer.py", "3D DNA Visualizer"),
        ]
        
        for path, desc in backend_checks:
            if self.check_file(path, desc):
                checks["passed"] += 1
            else:
                checks["failed"] += 1
        
        return checks
    
    def validate_frontend(self) -> Dict[str, int]:
        """Validate frontend components"""
        print("\n🌐 VALIDATING FRONTEND COMPONENTS...")
        
        checks = {
            "passed": 0,
            "failed": 0
        }
        
        frontend_checks = [
            ("web/frontend/package.json", "Package Configuration"),
            ("web/frontend/next.config.js", "Next.js Configuration"),
            ("web/frontend/src/pages/index.jsx", "Main Enrollment Page"),
            ("web/frontend/src/pages/admin.jsx", "Admin Dashboard"),
            ("web/frontend/src/pages/_document.jsx", "Document Setup"),
            ("web/frontend/src/components/DNAVisualizer.jsx", "Basic DNA Viewer"),
            ("web/frontend/src/components/FullDNAViewer.jsx", "Full 360° DNA Viewer"),
            ("web/frontend/src/components/UniversalDNAViewer.jsx", "Universal Device Viewer"),
            ("web/frontend/src/components/DNAViewer2D.jsx", "2D Fallback Viewer"),
            ("web/frontend/src/styles/GlobalStyles.jsx", "Tron-Inspired Styles"),
        ]
        
        for path, desc in frontend_checks:
            if self.check_file(path, desc):
                checks["passed"] += 1
            else:
                checks["failed"] += 1
        
        return checks
    
    def validate_cli(self) -> Dict[str, int]:
        """Validate CLI tool"""
        print("\n💻 VALIDATING CLI TOOL...")
        
        checks = {
            "passed": 0,
            "failed": 0
        }
        
        if self.check_file("dnakey_cli.py", "User-Friendly CLI Tool"):
            checks["passed"] += 1
        else:
            checks["failed"] += 1
        
        return checks
    
    def validate_docs(self) -> Dict[str, int]:
        """Validate documentation"""
        print("\n📚 VALIDATING DOCUMENTATION...")
        
        checks = {
            "passed": 0,
            "failed": 0
        }
        
        doc_checks = [
            ("README.md", "Main README"),
            ("PLATFORM_START_GUIDE.md", "Platform Start Guide"),
            ("README-UNIVERSAL-USAGES.md", "Universal Usages"),
            ("QUICK_START_FRIENDLY.md", "Quick Start Guide"),
            ("DEVICE_COMPATIBILITY.md", "Device Compatibility"),
            ("IMPLEMENTATION_STATUS.md", "Implementation Status"),
            ("PROJECT_COMPLETE.md", "Project Completion Summary"),
            ("DEVELOPMENT_LOG.md", "Development Log"),
        ]
        
        for path, desc in doc_checks:
            if self.check_file(path, desc):
                checks["passed"] += 1
            else:
                checks["failed"] += 1
        
        return checks
    
    def validate_tests(self) -> Dict[str, int]:
        """Validate test files"""
        print("\n🧪 VALIDATING TESTS...")
        
        checks = {
            "passed": 0,
            "failed": 0
        }
        
        test_checks = [
            ("tests/unit/test_signatures.py", "Signature Tests"),
            ("tests/unit/test_key_exchange.py", "Key Exchange Tests"),
            ("tests/unit/test_encryption.py", "Encryption Tests"),
            ("tests/unit/test_hashing.py", "Hashing Tests"),
            ("tests/unit/test_dna_key.py", "DNA Key Tests"),
            ("tests/unit/test_serialization.py", "Serialization Tests"),
            ("tests/unit/test_enrollment.py", "Enrollment Tests"),
            ("tests/unit/test_authentication.py", "Authentication Tests"),
            ("tests/unit/test_revocation.py", "Revocation Tests"),
        ]
        
        for path, desc in test_checks:
            if self.check_file(path, desc):
                checks["passed"] += 1
            else:
                checks["failed"] += 1
        
        return checks
    
    def validate_dependencies(self) -> Dict[str, int]:
        """Validate Python dependencies"""
        print("\n📦 VALIDATING DEPENDENCIES...")
        
        checks = {
            "passed": 0,
            "failed": 0
        }
        
        deps = [
            ("nacl", "PyNaCl (libsodium)"),
            ("cryptography", "Cryptography Library"),
            ("argon2", "Argon2"),
            ("cbor2", "CBOR2"),
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("pydantic", "Pydantic"),
        ]
        
        for module, desc in deps:
            if self.check_import(module, desc):
                checks["passed"] += 1
            else:
                checks["failed"] += 1
        
        return checks
    
    def print_results(self, section: str, checks: Dict[str, int]):
        """Print results for a section"""
        total = checks["passed"] + checks["failed"]
        if checks["failed"] == 0:
            status = "✅ ALL PASS"
        else:
            status = f"⚠️ {checks['failed']} FAILED"
        
        print(f"  {section}: {checks['passed']}/{total} {status}")
    
    def run(self):
        """Run all validations"""
        print("🔷 DNA-KEY AUTHENTICATION SYSTEM VALIDATION")
        print("=" * 60)
        
        backend = self.validate_backend()
        frontend = self.validate_frontend()
        cli = self.validate_cli()
        docs = self.validate_docs()
        tests = self.validate_tests()
        deps = self.validate_dependencies()
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY:")
        print("=" * 60)
        
        self.print_results("Backend", backend)
        self.print_results("Frontend", frontend)
        self.print_results("CLI Tool", cli)
        self.print_results("Documentation", docs)
        self.print_results("Tests", tests)
        self.print_results("Dependencies", deps)
        
        # Calculate totals
        total_passed = sum(c["passed"] for c in [backend, frontend, cli, docs, tests, deps])
        total_failed = sum(c["failed"] for c in [backend, frontend, cli, docs, tests, deps])
        total = total_passed + total_failed
        
        print("\n" + "=" * 60)
        if total_failed == 0:
            print(f"✅ VALIDATION COMPLETE: {total_passed}/{total} CHECKS PASSED!")
            print("🎉 All components are present and functional!")
        else:
            print(f"⚠️ VALIDATION COMPLETE: {total_passed}/{total} PASSED, {total_failed} FAILED")
            print("\nFailed checks:")
            for desc, passed, detail in self.results:
                if not passed:
                    print(f"  ❌ {desc}: {detail}")
        
        print("=" * 60)
        
        return total_failed == 0


if __name__ == "__main__":
    validator = SystemValidator()
    success = validator.run()
    sys.exit(0 if success else 1)
