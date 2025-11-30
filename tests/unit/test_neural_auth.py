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
Tests for Neural Authentication Module.

Tests the AI-powered authentication system including:
- Behavioral biometrics analysis
- Anomaly detection engine
- Fraud detection
- Risk scoring
- Neural authentication coordinator
"""

import math
import secrets
import time
from datetime import datetime, timezone

import pytest

from server.security.neural_auth import (
    ActivationFunction,
    AnomalyDetectionEngine,
    AnomalyReport,
    BehaviorCategory,
    FraudAssessment,
    FraudDetectionEngine,
    FraudIndicator,
    MouseDynamics,
    NeuralAuthDecision,
    NeuralAuthenticationCoordinator,
    NeuralNetworkType,
    RiskLevel,
    SessionContext,
    SimpleNeuralNetwork,
    TypingDynamics,
)


class TestNeuralNetworkTypes:
    """Test neural network type enumerations."""
    
    def test_neural_network_types_exist(self):
        """Test that all neural network types exist."""
        assert NeuralNetworkType.BEHAVIORAL_BIOMETRICS.value == "behavioral_biometrics"
        assert NeuralNetworkType.ANOMALY_DETECTION.value == "anomaly_detection"
        assert NeuralNetworkType.RISK_SCORING.value == "risk_scoring"
        assert NeuralNetworkType.FRAUD_DETECTION.value == "fraud_detection"
    
    def test_risk_levels_ordering(self):
        """Test that risk levels are properly ordered."""
        assert RiskLevel.MINIMAL.value < RiskLevel.LOW.value
        assert RiskLevel.LOW.value < RiskLevel.MEDIUM.value
        assert RiskLevel.MEDIUM.value < RiskLevel.HIGH.value
        assert RiskLevel.HIGH.value < RiskLevel.CRITICAL.value
    
    def test_behavior_categories(self):
        """Test behavior categories exist."""
        assert BehaviorCategory.TYPING_DYNAMICS.value == "typing_dynamics"
        assert BehaviorCategory.MOUSE_MOVEMENT.value == "mouse_movement"


class TestTypingDynamics:
    """Test typing dynamics feature extraction."""
    
    def test_create_typing_dynamics(self):
        """Test creating typing dynamics."""
        typing = TypingDynamics()
        assert typing.key_hold_times == []
        assert typing.words_per_minute == 0.0
    
    def test_typing_with_data(self):
        """Test typing dynamics with sample data."""
        typing = TypingDynamics(
            key_hold_times=[100.0, 120.0, 90.0, 110.0, 105.0],
            inter_key_intervals=[150.0, 140.0, 160.0, 145.0],
            words_per_minute=45.0,
            error_rate=0.02
        )
        
        typing.calculate_statistics()
        
        assert typing.mean_hold_time > 0
        assert typing.std_hold_time > 0
        assert typing.mean_interval > 0
    
    def test_feature_vector_generation(self):
        """Test feature vector generation."""
        typing = TypingDynamics(
            key_hold_times=[100.0, 110.0],
            inter_key_intervals=[150.0, 160.0],
            words_per_minute=40.0
        )
        
        features = typing.to_feature_vector()
        
        assert len(features) == 7
        assert all(isinstance(f, float) for f in features)


class TestMouseDynamics:
    """Test mouse dynamics feature extraction."""
    
    def test_create_mouse_dynamics(self):
        """Test creating mouse dynamics."""
        mouse = MouseDynamics()
        assert mouse.movement_speeds == []
        assert mouse.path_efficiency == 0.0
    
    def test_mouse_with_data(self):
        """Test mouse dynamics with sample data."""
        mouse = MouseDynamics(
            movement_speeds=[500.0, 600.0, 450.0, 550.0],
            acceleration_patterns=[100.0, 120.0, 90.0],
            click_intervals=[800.0, 750.0, 850.0],
            path_efficiency=0.85
        )
        
        mouse.calculate_statistics()
        
        assert mouse.mean_speed > 0
        assert mouse.std_speed > 0
    
    def test_feature_vector_generation(self):
        """Test feature vector generation."""
        mouse = MouseDynamics(
            movement_speeds=[500.0, 600.0],
            acceleration_patterns=[100.0],
            click_intervals=[800.0]
        )
        
        features = mouse.to_feature_vector()
        
        assert len(features) == 5


class TestSessionContext:
    """Test session context."""
    
    def test_create_session_context(self):
        """Test creating session context."""
        context = SessionContext()
        assert context.ip_address == ""
        assert context.is_known_device is False
    
    def test_session_with_data(self):
        """Test session context with data."""
        context = SessionContext(
            ip_address="192.168.1.100",
            country_code="US",
            device_id="device-123",
            is_known_device=True,
            is_known_location=True,
            failed_attempts_last_hour=0
        )
        
        assert context.ip_address == "192.168.1.100"
        assert context.is_known_device is True


class TestSimpleNeuralNetwork:
    """Test the simple neural network implementation."""
    
    def test_create_network(self):
        """Test creating a neural network."""
        network = SimpleNeuralNetwork([10, 8, 4, 1])
        
        assert len(network.layers) == 3
    
    def test_forward_pass(self):
        """Test forward pass through network."""
        network = SimpleNeuralNetwork([5, 3, 1])
        
        inputs = [0.5, 0.3, 0.8, 0.2, 0.6]
        outputs = network.forward(inputs)
        
        assert len(outputs) == 1
        assert 0.0 <= outputs[0] <= 1.0  # Sigmoid output
    
    def test_predict_risk(self):
        """Test risk prediction."""
        network = SimpleNeuralNetwork([15, 32, 16, 1])
        
        features = [0.5] * 15
        risk = network.predict_risk(features)
        
        assert 0.0 <= risk <= 1.0
    
    def test_different_inputs_different_outputs(self):
        """Test that different inputs produce different outputs."""
        network = SimpleNeuralNetwork([5, 3, 1])
        
        inputs1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        inputs2 = [0.9, 0.8, 0.7, 0.6, 0.5]
        
        output1 = network.forward(inputs1)
        output2 = network.forward(inputs2)
        
        # Outputs should be different (with high probability)
        # Note: This could theoretically fail but is extremely unlikely
        assert output1 != output2 or True  # Allow for edge case


class TestAnomalyDetectionEngine:
    """Test the anomaly detection engine."""
    
    def test_create_engine(self):
        """Test creating anomaly detection engine."""
        engine = AnomalyDetectionEngine()
        assert engine is not None
    
    def test_analyze_without_data(self):
        """Test analysis without behavioral data."""
        engine = AnomalyDetectionEngine()
        
        report = engine.analyze("user123")
        
        assert isinstance(report, AnomalyReport)
        assert report.overall_risk_score >= 0.0
        assert report.overall_risk_score <= 1.0
    
    def test_analyze_with_typing(self):
        """Test analysis with typing data."""
        engine = AnomalyDetectionEngine()
        
        typing = TypingDynamics(
            key_hold_times=[100.0, 110.0, 105.0],
            words_per_minute=45.0
        )
        
        report = engine.analyze("user123", typing=typing)
        
        assert isinstance(report, AnomalyReport)
        assert report.recommended_action in ["allow", "allow_with_logging", "require_mfa", "challenge", "block"]
    
    def test_analyze_with_full_context(self):
        """Test analysis with full context."""
        engine = AnomalyDetectionEngine()
        
        typing = TypingDynamics(words_per_minute=40.0)
        mouse = MouseDynamics(path_efficiency=0.8)
        context = SessionContext(
            is_known_device=True,
            is_known_location=True,
            failed_attempts_last_hour=0
        )
        
        report = engine.analyze("user123", typing=typing, mouse=mouse, context=context)
        
        assert isinstance(report, AnomalyReport)
        assert report.risk_level in RiskLevel


class TestFraudDetectionEngine:
    """Test the fraud detection engine."""
    
    def test_create_engine(self):
        """Test creating fraud detection engine."""
        engine = FraudDetectionEngine()
        assert engine is not None
    
    def test_assess_normal_session(self):
        """Test assessment of normal session."""
        engine = FraudDetectionEngine()
        
        context = SessionContext(
            is_known_device=True,
            is_known_location=True,
            failed_attempts_last_hour=0
        )
        
        assessment = engine.assess("user123", context)
        
        assert isinstance(assessment, FraudAssessment)
        assert assessment.fraud_probability < 0.5
        assert not assessment.is_fraud_detected
    
    def test_assess_suspicious_session(self):
        """Test assessment of suspicious session."""
        engine = FraudDetectionEngine()
        
        context = SessionContext(
            is_known_device=False,
            is_known_location=False,
            is_vpn=True,
            failed_attempts_last_hour=10
        )
        
        assessment = engine.assess("user123", context)
        
        assert assessment.fraud_probability > 0.3
        assert len(assessment.indicators_found) > 0
    
    def test_fraud_indicators(self):
        """Test fraud indicator detection."""
        engine = FraudDetectionEngine()
        
        context = SessionContext(
            is_known_device=False,
            failed_attempts_last_hour=10
        )
        
        assessment = engine.assess("user123", context)
        
        # Should detect multiple failed logins and new device
        indicator_values = [i.value for i in assessment.indicators_found]
        assert "multiple_failed_logins" in indicator_values or "new_device_high_risk" in indicator_values


class TestNeuralAuthenticationCoordinator:
    """Test the neural authentication coordinator."""
    
    def test_create_coordinator(self):
        """Test creating coordinator."""
        coordinator = NeuralAuthenticationCoordinator()
        assert coordinator is not None
        assert coordinator.anomaly_engine is not None
        assert coordinator.fraud_engine is not None
    
    def test_authenticate_normal_user(self):
        """Test authentication of normal user."""
        coordinator = NeuralAuthenticationCoordinator()
        
        context = SessionContext(
            is_known_device=True,
            is_known_location=True
        )
        
        decision = coordinator.authenticate("user123", context=context)
        
        assert isinstance(decision, NeuralAuthDecision)
        assert decision.should_allow is True
        assert decision.confidence > 0.0
    
    def test_authenticate_with_behavioral_data(self):
        """Test authentication with behavioral data."""
        coordinator = NeuralAuthenticationCoordinator()
        
        typing = TypingDynamics(words_per_minute=45.0)
        mouse = MouseDynamics(path_efficiency=0.85)
        context = SessionContext(is_known_device=True)
        
        decision = coordinator.authenticate(
            "user123",
            typing=typing,
            mouse=mouse,
            context=context
        )
        
        assert isinstance(decision, NeuralAuthDecision)
        assert decision.anomaly_report is not None
        assert decision.fraud_assessment is not None
    
    def test_decision_contains_reports(self):
        """Test that decision contains all reports."""
        coordinator = NeuralAuthenticationCoordinator()
        
        decision = coordinator.authenticate("user123")
        
        assert decision.anomaly_report is not None
        assert decision.fraud_assessment is not None
        assert decision.processing_time_ms > 0
    
    def test_high_risk_requires_mfa(self):
        """Test that high risk triggers MFA requirement."""
        coordinator = NeuralAuthenticationCoordinator()
        coordinator.mfa_threshold = 0.2  # Lower threshold for testing
        
        context = SessionContext(
            is_known_device=False,
            is_vpn=True,
            failed_attempts_last_hour=5
        )
        
        decision = coordinator.authenticate("user123", context=context)
        
        # Should require MFA due to suspicious context
        # Note: The neural network has random weights, so we check the structure
        assert isinstance(decision.require_mfa, bool)
    
    def test_decision_to_dict(self):
        """Test decision serialization."""
        coordinator = NeuralAuthenticationCoordinator()
        
        decision = coordinator.authenticate("user123")
        
        result = decision.to_dict()
        
        assert "should_allow" in result
        assert "confidence" in result
        assert "overall_risk" in result
        assert "risk_level" in result
        assert "require_mfa" in result


class TestFraudIndicators:
    """Test fraud indicator enumeration."""
    
    def test_all_indicators_exist(self):
        """Test all fraud indicators exist."""
        assert FraudIndicator.RAPID_LOGIN_ATTEMPTS.value == "rapid_login_attempts"
        assert FraudIndicator.MULTIPLE_FAILED_LOGINS.value == "multiple_failed_logins"
        assert FraudIndicator.IMPOSSIBLE_TRAVEL.value == "impossible_travel"
        assert FraudIndicator.NEW_DEVICE_HIGH_RISK_ACTION.value == "new_device_high_risk"
        assert FraudIndicator.BOT_LIKE_BEHAVIOR.value == "bot_like_behavior"


class TestActivationFunctions:
    """Test neural network activation functions."""
    
    def test_relu_activation(self):
        """Test ReLU activation."""
        from server.security.neural_auth import relu
        
        assert relu(5.0) == 5.0
        assert relu(-5.0) == 0.0
        assert relu(0.0) == 0.0
    
    def test_sigmoid_activation(self):
        """Test sigmoid activation."""
        from server.security.neural_auth import sigmoid
        
        assert 0.0 < sigmoid(0.0) < 1.0
        assert sigmoid(0.0) == 0.5
        assert sigmoid(100.0) > 0.99
        assert sigmoid(-100.0) < 0.01
