// DNA-Key Authentication System - Security Settings Page
// Futuristic security configuration and monitoring interface

import React, { useState, useEffect } from 'react';

export default function SecuritySettings() {
  const [securityConfig, setSecurityConfig] = useState({
    securityLevel: 'ULTIMATE',
    verificationBarriers: 24,
    quantumProtection: true,
    neuralAuth: true,
    biometricRequired: true,
    hardwareBinding: true,
    threatIntelligence: true,
    autoRevocation: true,
    sessionTimeout: 3600,
    maxConcurrentSessions: 3,
    ipWhitelist: [],
    complianceFrameworks: ['FIPS_140_3', 'NIST_SP_800_53', 'DOD_IL6']
  });

  const [securityMetrics, setSecurityMetrics] = useState({
    blockedAttempts: 1247,
    threatsDetected: 89,
    quarantinedKeys: 12,
    pendingReviews: 5,
    lastSecurityAudit: '2024-01-15T10:30:00Z',
    nextScheduledAudit: '2024-02-15T10:30:00Z'
  });

  const [algorithms, setAlgorithms] = useState({
    keyEncapsulation: 'ML-KEM-1024 (Kyber)',
    digitalSignature: 'ML-DSA-87 (Dilithium)',
    hashFunction: 'SHA3-512',
    keyDerivation: 'Argon2id',
    symmetricEncryption: 'AES-256-GCM',
    postQuantum: 'SPHINCS+-256f'
  });

  const SecurityToggle = ({ label, value, onChange, description }) => (
    <div style={styles.toggleRow}>
      <div style={styles.toggleInfo}>
        <span style={styles.toggleLabel}>{label}</span>
        <span style={styles.toggleDescription}>{description}</span>
      </div>
      <button 
        style={{...styles.toggleBtn, 
          background: value ? 'rgba(0, 255, 0, 0.2)' : 'rgba(255, 0, 0, 0.2)',
          borderColor: value ? '#00ff00' : '#ff0000'
        }}
        onClick={() => onChange(!value)}
      >
        {value ? '● ENABLED' : '○ DISABLED'}
      </button>
    </div>
  );

  const MetricCard = ({ title, value, icon, color, trend }) => (
    <div style={{...styles.metricCard, borderColor: color}}>
      <div style={styles.metricIcon}>{icon}</div>
      <div style={styles.metricContent}>
        <div style={{...styles.metricValue, color}}>{value}</div>
        <div style={styles.metricTitle}>{title}</div>
        {trend && (
          <div style={{...styles.metricTrend, color: trend > 0 ? '#ff0000' : '#00ff00'}}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% from last week
          </div>
        )}
      </div>
    </div>
  );

  const AlgorithmDisplay = ({ name, value }) => (
    <div style={styles.algorithmRow}>
      <span style={styles.algorithmName}>{name}</span>
      <span style={styles.algorithmValue}>{value}</span>
    </div>
  );

  return (
    <div style={styles.container}>
      <div style={styles.bgGrid}></div>
      
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logoIcon}>🛡️</span>
          <div>
            <h1 style={styles.title}>SECURITY CONFIGURATION</h1>
            <p style={styles.subtitle}>Military-Grade Protection Settings</p>
          </div>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.classificationBadge}>
            <span style={styles.classificationLabel}>CLASSIFICATION:</span>
            <span style={styles.classificationValue}>ULTIMATE</span>
          </div>
          <a href="/dashboard" style={styles.navLink}>← Back to Dashboard</a>
        </div>
      </header>

      {/* Security Metrics */}
      <div style={styles.metricsGrid}>
        <MetricCard
          title="Blocked Attempts"
          value={securityMetrics.blockedAttempts.toLocaleString()}
          icon="🚫"
          color="#ff0000"
          trend={12}
        />
        <MetricCard
          title="Threats Detected"
          value={securityMetrics.threatsDetected}
          icon="⚠️"
          color="#ffaa00"
          trend={-8}
        />
        <MetricCard
          title="Quarantined Keys"
          value={securityMetrics.quarantinedKeys}
          icon="🔒"
          color="#ff00ff"
          trend={2}
        />
        <MetricCard
          title="Pending Reviews"
          value={securityMetrics.pendingReviews}
          icon="📋"
          color="#00ffff"
        />
      </div>

      <div style={styles.mainContent}>
        {/* Security Controls */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>⚙️ SECURITY CONTROLS</h2>
          
          <SecurityToggle
            label="Quantum Protection"
            value={securityConfig.quantumProtection}
            onChange={(v) => setSecurityConfig({...securityConfig, quantumProtection: v})}
            description="Post-quantum cryptographic algorithms (Kyber, Dilithium, SPHINCS+)"
          />
          
          <SecurityToggle
            label="Neural Authentication"
            value={securityConfig.neuralAuth}
            onChange={(v) => setSecurityConfig({...securityConfig, neuralAuth: v})}
            description="AI-powered behavioral biometrics and anomaly detection"
          />
          
          <SecurityToggle
            label="Biometric Required"
            value={securityConfig.biometricRequired}
            onChange={(v) => setSecurityConfig({...securityConfig, biometricRequired: v})}
            description="Require biometric verification for authentication"
          />
          
          <SecurityToggle
            label="Hardware Binding"
            value={securityConfig.hardwareBinding}
            onChange={(v) => setSecurityConfig({...securityConfig, hardwareBinding: v})}
            description="TPM/Secure Enclave device attestation"
          />
          
          <SecurityToggle
            label="Threat Intelligence"
            value={securityConfig.threatIntelligence}
            onChange={(v) => setSecurityConfig({...securityConfig, threatIntelligence: v})}
            description="Real-time threat detection and IP reputation"
          />
          
          <SecurityToggle
            label="Auto Revocation"
            value={securityConfig.autoRevocation}
            onChange={(v) => setSecurityConfig({...securityConfig, autoRevocation: v})}
            description="Automatically revoke compromised DNA keys"
          />
        </div>

        {/* Cryptographic Algorithms */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>🔐 CRYPTOGRAPHIC SUITE</h2>
          <div style={styles.algorithmList}>
            <AlgorithmDisplay name="Key Encapsulation" value={algorithms.keyEncapsulation} />
            <AlgorithmDisplay name="Digital Signature" value={algorithms.digitalSignature} />
            <AlgorithmDisplay name="Hash Function" value={algorithms.hashFunction} />
            <AlgorithmDisplay name="Key Derivation" value={algorithms.keyDerivation} />
            <AlgorithmDisplay name="Symmetric Encryption" value={algorithms.symmetricEncryption} />
            <AlgorithmDisplay name="Post-Quantum Signature" value={algorithms.postQuantum} />
          </div>
          
          <div style={styles.suiteIndicator}>
            <span style={styles.suiteLabel}>ALGORITHM SUITE:</span>
            <span style={styles.suiteValue}>CNSA 2.0 COMPLIANT</span>
          </div>
        </div>

        {/* Verification Barriers */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>🏰 VERIFICATION BARRIERS</h2>
          <div style={styles.barriersGrid}>
            {[...Array(24)].map((_, i) => (
              <div 
                key={i}
                style={{
                  ...styles.barrierBlock,
                  background: i < securityConfig.verificationBarriers 
                    ? 'rgba(0, 255, 0, 0.3)' 
                    : 'rgba(255, 0, 0, 0.1)',
                  borderColor: i < securityConfig.verificationBarriers 
                    ? '#00ff00' 
                    : '#ff000055'
                }}
              >
                <span style={styles.barrierNumber}>{i + 1}</span>
              </div>
            ))}
          </div>
          <div style={styles.barrierInfo}>
            <span style={styles.barrierLabel}>ACTIVE BARRIERS:</span>
            <span style={styles.barrierCount}>{securityConfig.verificationBarriers}/24</span>
          </div>
          <div style={styles.barrierList}>
            <div style={styles.barrierItem}>✓ Format Validation</div>
            <div style={styles.barrierItem}>✓ Version Check</div>
            <div style={styles.barrierItem}>✓ Timestamp Validation</div>
            <div style={styles.barrierItem}>✓ Issuer Verification</div>
            <div style={styles.barrierItem}>✓ Checksum Verification</div>
            <div style={styles.barrierItem}>✓ Entropy Validation</div>
            <div style={styles.barrierItem}>✓ Policy Evaluation</div>
            <div style={styles.barrierItem}>✓ Signature Verification</div>
            <div style={styles.barrierItem}>✓ Revocation Check</div>
            <div style={styles.barrierItem}>✓ Layer Integrity</div>
            <div style={styles.barrierItem}>✓ Segment Distribution</div>
            <div style={styles.barrierItem}>✓ Cross-Reference Check</div>
            <div style={styles.barrierItem}>✓ Quantum Signature</div>
            <div style={styles.barrierItem}>✓ Hardware Attestation</div>
            <div style={styles.barrierItem}>✓ Biometric Match</div>
            <div style={styles.barrierItem}>✓ Behavioral Analysis</div>
            <div style={styles.barrierItem}>✓ Device Fingerprint</div>
            <div style={styles.barrierItem}>✓ Geolocation Check</div>
            <div style={styles.barrierItem}>✓ Time-Based Token</div>
            <div style={styles.barrierItem}>✓ Risk Score Eval</div>
            <div style={styles.barrierItem}>✓ Blockchain Verify</div>
            <div style={styles.barrierItem}>✓ Zero-Knowledge Proof</div>
            <div style={styles.barrierItem}>✓ Multi-Party Compute</div>
            <div style={styles.barrierItem}>✓ Final Consensus</div>
          </div>
        </div>

        {/* Compliance Frameworks */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>📜 COMPLIANCE FRAMEWORKS</h2>
          <div style={styles.complianceGrid}>
            {[
              { id: 'FIPS_140_3', name: 'FIPS 140-3 Level 3', active: true },
              { id: 'NIST_SP_800_53', name: 'NIST SP 800-53 Rev 5', active: true },
              { id: 'DOD_IL6', name: 'DoD Impact Level 6', active: true },
              { id: 'FEDRAMP_HIGH', name: 'FedRAMP High', active: true },
              { id: 'SOC2_TYPE2', name: 'SOC 2 Type II', active: true },
              { id: 'ISO_27001', name: 'ISO 27001:2022', active: true },
              { id: 'PCI_DSS', name: 'PCI DSS 4.0', active: false },
              { id: 'HIPAA', name: 'HIPAA', active: false }
            ].map(fw => (
              <div 
                key={fw.id}
                style={{
                  ...styles.complianceItem,
                  background: fw.active ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  borderColor: fw.active ? '#00ff00' : '#333'
                }}
              >
                <span style={{color: fw.active ? '#00ff00' : '#666'}}>
                  {fw.active ? '✓' : '○'}
                </span>
                <span style={{color: fw.active ? '#00ffff' : '#666'}}>{fw.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Schedule */}
      <div style={styles.auditSection}>
        <h3 style={styles.auditTitle}>🔍 SECURITY AUDIT SCHEDULE</h3>
        <div style={styles.auditGrid}>
          <div style={styles.auditCard}>
            <div style={styles.auditLabel}>Last Audit</div>
            <div style={styles.auditDate}>
              {new Date(securityMetrics.lastSecurityAudit).toLocaleDateString()}
            </div>
            <div style={styles.auditStatus}>✓ PASSED</div>
          </div>
          <div style={styles.auditCard}>
            <div style={styles.auditLabel}>Next Scheduled</div>
            <div style={styles.auditDate}>
              {new Date(securityMetrics.nextScheduledAudit).toLocaleDateString()}
            </div>
            <div style={styles.auditDays}>
              {Math.ceil((new Date(securityMetrics.nextScheduledAudit) - new Date()) / (1000 * 60 * 60 * 24))} days
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>🛡️ DNALockOS Security Configuration | Classification: ULTIMATE 🛡️</p>
        <p style={styles.footerMeta}>
          Security Policy Version: 2.0.0 | Last Updated: {new Date().toLocaleString()}
        </p>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: '#000',
    color: '#00ffff',
    fontFamily: 'Orbitron, monospace',
    position: 'relative',
    overflow: 'auto'
  },
  bgGrid: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      linear-gradient(rgba(255, 0, 0, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 0, 0, 0.02) 1px, transparent 1px)
    `,
    backgroundSize: '50px 50px',
    zIndex: 0
  },
  header: {
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 40px',
    borderBottom: '2px solid #ff0000',
    background: 'rgba(0, 0, 0, 0.95)'
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px'
  },
  logoIcon: {
    fontSize: '40px'
  },
  title: {
    fontSize: '24px',
    margin: 0,
    color: '#ff0000',
    textShadow: '0 0 10px #ff0000'
  },
  subtitle: {
    fontSize: '12px',
    color: '#888',
    margin: 0,
    letterSpacing: '2px'
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '30px'
  },
  classificationBadge: {
    padding: '10px 20px',
    background: 'rgba(255, 0, 0, 0.2)',
    border: '2px solid #ff0000',
    borderRadius: '5px'
  },
  classificationLabel: {
    fontSize: '10px',
    color: '#888',
    marginRight: '10px'
  },
  classificationValue: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#ff0000'
  },
  navLink: {
    color: '#00ffff',
    textDecoration: 'none',
    fontSize: '14px'
  },
  metricsGrid: {
    position: 'relative',
    zIndex: 1,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    padding: '30px 40px'
  },
  metricCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '20px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid',
    borderRadius: '10px'
  },
  metricIcon: {
    fontSize: '30px'
  },
  metricContent: {},
  metricValue: {
    fontSize: '24px',
    fontWeight: 'bold'
  },
  metricTitle: {
    fontSize: '11px',
    color: '#888',
    textTransform: 'uppercase'
  },
  metricTrend: {
    fontSize: '10px',
    marginTop: '5px'
  },
  mainContent: {
    position: 'relative',
    zIndex: 1,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
    gap: '20px',
    padding: '0 40px'
  },
  panel: {
    background: 'rgba(0, 0, 0, 0.9)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '25px'
  },
  panelTitle: {
    fontSize: '16px',
    marginBottom: '20px',
    paddingBottom: '10px',
    borderBottom: '1px solid #00ffff33',
    letterSpacing: '2px'
  },
  toggleRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px',
    background: 'rgba(0, 255, 255, 0.05)',
    borderRadius: '5px',
    marginBottom: '10px'
  },
  toggleInfo: {
    flex: 1
  },
  toggleLabel: {
    display: 'block',
    fontSize: '14px',
    fontWeight: 'bold'
  },
  toggleDescription: {
    display: 'block',
    fontSize: '11px',
    color: '#666',
    marginTop: '5px'
  },
  toggleBtn: {
    padding: '8px 15px',
    border: '2px solid',
    borderRadius: '5px',
    background: 'transparent',
    color: '#fff',
    fontSize: '12px',
    cursor: 'pointer',
    fontFamily: 'Orbitron, monospace'
  },
  algorithmList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  algorithmRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px 15px',
    background: 'rgba(0, 255, 255, 0.05)',
    borderRadius: '5px',
    borderLeft: '3px solid #00ffff'
  },
  algorithmName: {
    fontSize: '12px',
    color: '#888'
  },
  algorithmValue: {
    fontSize: '12px',
    color: '#00ff00',
    fontWeight: 'bold'
  },
  suiteIndicator: {
    marginTop: '20px',
    padding: '15px',
    background: 'rgba(0, 255, 0, 0.1)',
    border: '1px solid #00ff00',
    borderRadius: '5px',
    textAlign: 'center'
  },
  suiteLabel: {
    fontSize: '10px',
    color: '#888',
    marginRight: '10px'
  },
  suiteValue: {
    fontSize: '14px',
    color: '#00ff00',
    fontWeight: 'bold'
  },
  barriersGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(8, 1fr)',
    gap: '8px',
    marginBottom: '15px'
  },
  barrierBlock: {
    aspectRatio: '1',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '2px solid',
    borderRadius: '5px'
  },
  barrierNumber: {
    fontSize: '12px',
    fontWeight: 'bold'
  },
  barrierInfo: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '10px',
    padding: '10px',
    background: 'rgba(0, 255, 0, 0.1)',
    borderRadius: '5px',
    marginBottom: '15px'
  },
  barrierLabel: {
    fontSize: '12px',
    color: '#888'
  },
  barrierCount: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#00ff00'
  },
  barrierList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '5px',
    fontSize: '11px',
    color: '#00ff00'
  },
  barrierItem: {
    padding: '5px 10px',
    background: 'rgba(0, 255, 0, 0.05)',
    borderRadius: '3px'
  },
  complianceGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '10px'
  },
  complianceItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '12px 15px',
    border: '1px solid',
    borderRadius: '5px',
    fontSize: '12px'
  },
  auditSection: {
    position: 'relative',
    zIndex: 1,
    padding: '30px 40px'
  },
  auditTitle: {
    fontSize: '16px',
    marginBottom: '20px',
    letterSpacing: '2px'
  },
  auditGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px'
  },
  auditCard: {
    padding: '25px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    textAlign: 'center'
  },
  auditLabel: {
    fontSize: '12px',
    color: '#888',
    marginBottom: '10px'
  },
  auditDate: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#00ffff'
  },
  auditStatus: {
    marginTop: '10px',
    fontSize: '14px',
    color: '#00ff00',
    fontWeight: 'bold'
  },
  auditDays: {
    marginTop: '10px',
    fontSize: '14px',
    color: '#ffaa00'
  },
  footer: {
    position: 'relative',
    zIndex: 1,
    textAlign: 'center',
    padding: '30px',
    marginTop: '20px',
    borderTop: '1px solid #ff000033',
    fontSize: '12px',
    color: '#666'
  },
  footerMeta: {
    marginTop: '5px',
    fontSize: '11px',
    color: '#444'
  }
};
