"""
DNALockOS Stress Tests

Load and concurrency tests for the authentication system.
Military-grade stress testing with full authentication flows.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pytest

from server.core.enrollment import EnrollmentService, EnrollmentRequest, enroll_user
from server.core.authentication import AuthenticationService, ChallengeRequest
from server.crypto.dna_key import SecurityLevel
from server.crypto.dna_generator import DNAKeyGenerator
from server.crypto.signatures import Ed25519SigningKey, generate_ed25519_keypair


@dataclass
class EnrolledKeyWithSigner:
    """Container for enrolled key with corresponding signing key for testing."""
    enrollment_response: any
    signing_key: Ed25519SigningKey
    verify_key: any
    key_id: str


def create_test_enrollment_with_signer(
    auth_service: AuthenticationService,
    subject_id: str
) -> EnrolledKeyWithSigner:
    """
    Create an enrollment with a signing key we control.
    
    This is the proper way to test authentication - we generate our own
    keypair, update the DNA key to use our public key, then we can sign
    challenges with our private key.
    """
    # Enroll the user
    enrollment = enroll_user(subject_id)
    assert enrollment.success, f"Enrollment failed: {enrollment.error_message}"
    
    # Generate a test keypair we control
    generator = DNAKeyGenerator()
    signing_key, verify_key = generator._generate_test_keypair()
    
    # Update the DNA key's public key to match our test keypair
    enrollment.dna_key.cryptographic_material.public_key = verify_key.to_bytes()
    
    # Register with auth service
    auth_service.enroll_key(enrollment.dna_key)
    
    return EnrolledKeyWithSigner(
        enrollment_response=enrollment,
        signing_key=signing_key,
        verify_key=verify_key,
        key_id=enrollment.key_id
    )


@dataclass
class StressTestMetrics:
    """Metrics from a stress test run."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    avg_latency: float = 0.0
    requests_per_second: float = 0.0
    
    def add_request(self, duration: float, success: bool):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.min_latency = min(self.min_latency, duration)
        self.max_latency = max(self.max_latency, duration)
        
        # Update running average
        prev_avg = self.avg_latency * (self.total_requests - 1)
        self.avg_latency = (prev_avg + duration) / self.total_requests
    
    def finalize(self, total_duration: float):
        self.total_duration = total_duration
        if total_duration > 0:
            self.requests_per_second = self.total_requests / total_duration


class TestEnrollmentStress:
    """Stress tests for the enrollment service."""
    
    def test_sequential_enrollments(self):
        """Test sequential enrollment performance."""
        service = EnrollmentService()
        num_enrollments = 50
        
        metrics = StressTestMetrics()
        start_time = time.time()
        
        for i in range(num_enrollments):
            request = EnrollmentRequest(
                subject_id=f"stress-user-{i}",
                subject_type="human",
                security_level=SecurityLevel.STANDARD,
                policy_id="default-policy-v1",
                validity_days=365
            )
            
            req_start = time.time()
            response = service.enroll(request)
            req_duration = time.time() - req_start
            
            metrics.add_request(req_duration, response.success)
        
        metrics.finalize(time.time() - start_time)
        
        # Assertions
        assert metrics.successful_requests >= num_enrollments * 0.95, \
            f"At least 95% should succeed, got {metrics.successful_requests}/{num_enrollments}"
        
        # Performance assertions (relaxed for CI)
        assert metrics.avg_latency < 1.0, \
            f"Average latency should be < 1s, got {metrics.avg_latency:.3f}s"
        
        print(f"\n📊 Enrollment Stress Test Results:")
        print(f"   Total: {metrics.total_requests}")
        print(f"   Success: {metrics.successful_requests}")
        print(f"   Failed: {metrics.failed_requests}")
        print(f"   Avg Latency: {metrics.avg_latency*1000:.2f}ms")
        print(f"   Min Latency: {metrics.min_latency*1000:.2f}ms")
        print(f"   Max Latency: {metrics.max_latency*1000:.2f}ms")
        print(f"   RPS: {metrics.requests_per_second:.2f}")
    
    def test_concurrent_enrollments(self):
        """Test concurrent enrollment with thread pool."""
        num_workers = 5
        enrollments_per_worker = 10
        total_enrollments = num_workers * enrollments_per_worker
        
        metrics = StressTestMetrics()
        results = []
        
        def enroll_worker(worker_id: int) -> List[tuple]:
            """Worker function for enrollment."""
            service = EnrollmentService()
            worker_results = []
            
            for i in range(enrollments_per_worker):
                request = EnrollmentRequest(
                    subject_id=f"concurrent-user-{worker_id}-{i}",
                    subject_type="human",
                    security_level=SecurityLevel.STANDARD,
                    policy_id="default-policy-v1",
                    validity_days=365
                )
                
                req_start = time.time()
                response = service.enroll(request)
                req_duration = time.time() - req_start
                
                worker_results.append((req_duration, response.success))
            
            return worker_results
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(enroll_worker, i) for i in range(num_workers)]
            
            for future in as_completed(futures):
                worker_results = future.result()
                for duration, success in worker_results:
                    metrics.add_request(duration, success)
        
        metrics.finalize(time.time() - start_time)
        
        # Assertions
        assert metrics.successful_requests >= total_enrollments * 0.90, \
            f"At least 90% should succeed under concurrency"
        
        print(f"\n📊 Concurrent Enrollment Stress Test Results:")
        print(f"   Workers: {num_workers}")
        print(f"   Total: {metrics.total_requests}")
        print(f"   Success: {metrics.successful_requests}")
        print(f"   Failed: {metrics.failed_requests}")
        print(f"   Avg Latency: {metrics.avg_latency*1000:.2f}ms")
        print(f"   RPS: {metrics.requests_per_second:.2f}")


class TestAuthenticationStress:
    """Stress tests for the authentication service with full authentication flows."""
    
    def setup_method(self):
        """Set up test fixtures with proper signing capability."""
        self.auth_service = AuthenticationService()
        
        # Create enrollment with signing key we control
        self.test_key = create_test_enrollment_with_signer(
            self.auth_service,
            "auth-stress-user"
        )
    
    def test_sequential_challenge_generation(self):
        """Test sequential challenge generation performance."""
        num_challenges = 100
        metrics = StressTestMetrics()
        start_time = time.time()
        
        for i in range(num_challenges):
            request = ChallengeRequest(key_id=self.test_key.key_id)
            
            req_start = time.time()
            response = self.auth_service.generate_challenge(request)
            req_duration = time.time() - req_start
            
            metrics.add_request(req_duration, response.success)
        
        metrics.finalize(time.time() - start_time)
        
        # Assertions
        assert metrics.successful_requests >= num_challenges * 0.99, \
            "Challenge generation should be highly reliable"
        
        assert metrics.avg_latency < 0.1, \
            f"Challenge generation should be fast, got {metrics.avg_latency*1000:.2f}ms avg"
        
        print(f"\n📊 Challenge Generation Stress Test Results:")
        print(f"   Total: {metrics.total_requests}")
        print(f"   Success: {metrics.successful_requests}")
        print(f"   Avg Latency: {metrics.avg_latency*1000:.2f}ms")
        print(f"   RPS: {metrics.requests_per_second:.2f}")
    
    def test_full_authentication_flow_stress(self):
        """Stress test complete authentication flow with proper signing."""
        num_authentications = 20
        metrics = StressTestMetrics()
        start_time = time.time()
        
        for i in range(num_authentications):
            req_start = time.time()
            
            # Generate challenge
            challenge_request = ChallengeRequest(key_id=self.test_key.key_id)
            challenge_response = self.auth_service.generate_challenge(challenge_request)
            
            if not challenge_response.success:
                metrics.add_request(time.time() - req_start, False)
                continue
            
            # Sign challenge with our test signing key
            signature = self.test_key.signing_key.sign(challenge_response.challenge)
            
            # Authenticate
            auth_response = self.auth_service.authenticate(
                challenge_response.challenge_id,
                signature
            )
            
            req_duration = time.time() - req_start
            metrics.add_request(req_duration, auth_response.success)
        
        metrics.finalize(time.time() - start_time)
        
        # Assertions
        assert metrics.successful_requests >= num_authentications * 0.95, \
            f"Full auth flow should be reliable, got {metrics.successful_requests}/{num_authentications}"
        
        print(f"\n📊 Full Authentication Flow Stress Test Results:")
        print(f"   Total: {metrics.total_requests}")
        print(f"   Success: {metrics.successful_requests}")
        print(f"   Avg Latency: {metrics.avg_latency*1000:.2f}ms")
        print(f"   RPS: {metrics.requests_per_second:.2f}")


class TestMixedWorkloadStress:
    """Stress tests with mixed workloads including full authentication flows."""
    
    def test_mixed_enrollment_and_full_auth(self):
        """Test mixed enrollment and full authentication workload."""
        auth_service = AuthenticationService()
        
        num_operations = 30
        enrolled_keys: List[EnrolledKeyWithSigner] = []
        
        enroll_metrics = StressTestMetrics()
        auth_metrics = StressTestMetrics()
        
        start_time = time.time()
        
        for i in range(num_operations):
            # Alternate between enrollment and full authentication
            if i % 2 == 0 or len(enrolled_keys) == 0:
                # Enrollment with signing key
                req_start = time.time()
                try:
                    test_key = create_test_enrollment_with_signer(
                        auth_service,
                        f"mixed-user-{i}"
                    )
                    enrolled_keys.append(test_key)
                    enroll_metrics.add_request(time.time() - req_start, True)
                except Exception as e:
                    enroll_metrics.add_request(time.time() - req_start, False)
            else:
                # Full authentication with random enrolled key
                import random
                test_key = random.choice(enrolled_keys)
                
                req_start = time.time()
                
                # Generate challenge
                challenge_request = ChallengeRequest(key_id=test_key.key_id)
                challenge_response = auth_service.generate_challenge(challenge_request)
                
                if challenge_response.success:
                    # Sign with our controlled signing key
                    signature = test_key.signing_key.sign(challenge_response.challenge)
                    
                    # Authenticate
                    auth_response = auth_service.authenticate(
                        challenge_response.challenge_id,
                        signature
                    )
                    success = auth_response.success
                else:
                    success = False
                
                req_duration = time.time() - req_start
                auth_metrics.add_request(req_duration, success)
        
        total_duration = time.time() - start_time
        enroll_metrics.finalize(total_duration)
        auth_metrics.finalize(total_duration)
        
        print(f"\n📊 Mixed Workload Stress Test Results:")
        print(f"   Enrollments: {enroll_metrics.total_requests} ({enroll_metrics.successful_requests} success)")
        print(f"   Authentications: {auth_metrics.total_requests} ({auth_metrics.successful_requests} success)")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        # Overall success rate
        total = enroll_metrics.total_requests + auth_metrics.total_requests
        success = enroll_metrics.successful_requests + auth_metrics.successful_requests
        
        assert success >= total * 0.85, \
            f"Mixed workload should have 85%+ success rate, got {success}/{total}"


class TestMobileSafeStress:
    """Lightweight stress tests safe for mobile/Termux."""
    
    def test_light_enrollment_stress(self):
        """Light stress test suitable for mobile devices."""
        service = EnrollmentService()
        num_enrollments = 10  # Reduced for mobile
        
        metrics = StressTestMetrics()
        start_time = time.time()
        
        for i in range(num_enrollments):
            request = EnrollmentRequest(
                subject_id=f"mobile-user-{i}",
                subject_type="human",
                security_level=SecurityLevel.STANDARD,
                policy_id="default-policy-v1",
                validity_days=365
            )
            
            req_start = time.time()
            response = service.enroll(request)
            req_duration = time.time() - req_start
            
            metrics.add_request(req_duration, response.success)
        
        metrics.finalize(time.time() - start_time)
        
        # More relaxed assertions for mobile
        assert metrics.successful_requests >= num_enrollments * 0.80, \
            "At least 80% should succeed on mobile"
        
        print(f"\n📱 Mobile-Safe Stress Test Results:")
        print(f"   Total: {metrics.total_requests}")
        print(f"   Success: {metrics.successful_requests}")
        print(f"   Duration: {metrics.total_duration:.2f}s")
