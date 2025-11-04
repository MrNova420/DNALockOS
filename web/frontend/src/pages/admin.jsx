// Admin Dashboard - DNA-Key Protected
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AdminDashboard() {
  const [adminKey, setAdminKey] = useState('');
  const [sessionToken, setSessionToken] = useState(null);
  const [stats, setStats] = useState(null);
  const [keys, setKeys] = useState([]);
  const [revocations, setRevocations] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');

  // Admin authentication with DNA-Key
  const handleAdminAuth = async () => {
    try {
      // Step 1: Get challenge
      const challengeResp = await axios.post(`${API_URL}/api/v1/challenge`, {
        key_id: adminKey
      });

      if (!challengeResp.data.success) {
        alert('Authentication failed: ' + challengeResp.data.error_message);
        return;
      }

      // Step 2: In production, sign challenge with DNA key
      // For demo, we'll simulate authentication
      alert('Admin DNA-Key authentication required. In production, this would sign the challenge with your DNA key.');
      
      // Simulate successful auth
      setSessionToken('dna-session-admin-demo-token');
      loadAdminData('dna-session-admin-demo-token');
    } catch (error) {
      console.error('Admin auth failed:', error);
      alert('Authentication failed');
    }
  };

  const loadAdminData = async (token) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      
      // Load stats
      const statsResp = await axios.get(`${API_URL}/api/v1/admin/stats`, { headers });
      setStats(statsResp.data);

      // Load keys
      const keysResp = await axios.get(`${API_URL}/api/v1/admin/keys`, { headers });
      setKeys(keysResp.data.keys);

      // Load revocations
      const revokeResp = await axios.get(`${API_URL}/api/v1/admin/revocations`, { headers });
      setRevocations(revokeResp.data.revocations);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    }
  };

  const handleRevoke = async (keyId) => {
    if (!confirm(`Revoke key ${keyId}?`)) return;

    try {
      await axios.post(
        `${API_URL}/api/v1/admin/revoke`,
        {
          key_id: keyId,
          reason: 'privilege_withdrawn',
          revoked_by: 'admin',
          notes: 'Revoked from admin dashboard'
        },
        { headers: { Authorization: `Bearer ${sessionToken}` } }
      );

      alert('Key revoked successfully');
      loadAdminData(sessionToken);
    } catch (error) {
      alert('Revocation failed: ' + error.message);
    }
  };

  if (!sessionToken) {
    return (
      <div style={styles.container}>
        <div style={styles.authPanel}>
          <h1 style={styles.title}>🔒 ADMIN AUTHENTICATION 🔒</h1>
          <p style={styles.subtitle}>DNA-Key Master Key Required</p>
          
          <div style={styles.authForm}>
            <input
              style={styles.input}
              type="text"
              placeholder="Enter Admin DNA-Key ID"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
            />
            <button 
              style={styles.button}
              onClick={handleAdminAuth}
              disabled={!adminKey}
            >
              AUTHENTICATE WITH DNA-KEY →
            </button>
          </div>

          <div style={styles.infoBox}>
            <h3>🔷 Admin Access Security</h3>
            <p>• Admin dashboard uses DNA-Key authentication</p>
            <p>• Master key with admin privileges required</p>
            <p>• Challenge-response protocol for verification</p>
            <p>• Session tokens expire after 1 hour</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>⚡ ADMIN CONTROL CENTER ⚡</h1>
        <button style={styles.logoutBtn} onClick={() => setSessionToken(null)}>
          LOGOUT
        </button>
      </div>

      <div style={styles.tabs}>
        <button 
          style={{...styles.tab, ...(activeTab === 'overview' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('overview')}
        >
          OVERVIEW
        </button>
        <button 
          style={{...styles.tab, ...(activeTab === 'keys' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('keys')}
        >
          ENROLLED KEYS
        </button>
        <button 
          style={{...styles.tab, ...(activeTab === 'revocations' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('revocations')}
        >
          REVOCATIONS
        </button>
      </div>

      <div style={styles.content}>
        {activeTab === 'overview' && stats && (
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <h3>ENROLLED KEYS</h3>
              <p style={styles.statNumber}>{stats.enrolled_keys}</p>
            </div>
            <div style={styles.statCard}>
              <h3>ACTIVE CHALLENGES</h3>
              <p style={styles.statNumber}>{stats.active_challenges}</p>
            </div>
            <div style={styles.statCard}>
              <h3>REVOKED KEYS</h3>
              <p style={styles.statNumber}>{stats.revoked_keys}</p>
            </div>
            <div style={styles.statCard}>
              <h3>CRL VERSION</h3>
              <p style={styles.statNumber}>{stats.crl_version}</p>
            </div>
          </div>
        )}

        {activeTab === 'keys' && (
          <div style={styles.table}>
            <h2>Enrolled DNA Keys</h2>
            <table style={styles.dataTable}>
              <thead>
                <tr>
                  <th>Key ID</th>
                  <th>Type</th>
                  <th>Created</th>
                  <th>Expires</th>
                  <th>Segments</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {keys.map(key => (
                  <tr key={key.key_id}>
                    <td>{key.key_id.substring(0, 20)}...</td>
                    <td>{key.subject_type}</td>
                    <td>{new Date(key.created).toLocaleDateString()}</td>
                    <td>{new Date(key.expires).toLocaleDateString()}</td>
                    <td>{key.segment_count}</td>
                    <td style={{color: key.is_revoked ? '#ff0000' : '#00ff00'}}>
                      {key.is_revoked ? '❌ REVOKED' : '✓ ACTIVE'}
                    </td>
                    <td>
                      {!key.is_revoked && (
                        <button 
                          style={styles.revokeBtn}
                          onClick={() => handleRevoke(key.key_id)}
                        >
                          REVOKE
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'revocations' && (
          <div style={styles.table}>
            <h2>Revocation History</h2>
            <table style={styles.dataTable}>
              <thead>
                <tr>
                  <th>Key ID</th>
                  <th>Revoked At</th>
                  <th>Reason</th>
                  <th>Revoked By</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {revocations.map(rev => (
                  <tr key={rev.key_id}>
                    <td>{rev.key_id.substring(0, 20)}...</td>
                    <td>{new Date(rev.revoked_at).toLocaleString()}</td>
                    <td>{rev.reason}</td>
                    <td>{rev.revoked_by}</td>
                    <td>{rev.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(180deg, #000000 0%, #1a001a 100%)',
    color: '#00ffff',
    fontFamily: '"Orbitron", monospace',
    padding: '20px'
  },
  authPanel: {
    maxWidth: '600px',
    margin: '100px auto',
    background: 'rgba(0, 255, 255, 0.05)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '40px',
    boxShadow: '0 0 50px rgba(0, 255, 255, 0.3)'
  },
  title: {
    fontSize: '36px',
    textAlign: 'center',
    marginBottom: '10px',
    textShadow: '0 0 20px #00ffff'
  },
  subtitle: {
    textAlign: 'center',
    color: '#ff00ff',
    marginBottom: '30px'
  },
  authForm: {
    marginBottom: '30px'
  },
  input: {
    width: '100%',
    padding: '15px',
    background: 'rgba(0, 0, 0, 0.5)',
    border: '2px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    fontSize: '16px',
    marginBottom: '20px',
    fontFamily: 'inherit'
  },
  button: {
    width: '100%',
    padding: '15px',
    background: 'linear-gradient(90deg, #00ffff 0%, #00cccc 100%)',
    border: 'none',
    borderRadius: '5px',
    color: '#000',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    textTransform: 'uppercase'
  },
  infoBox: {
    background: 'rgba(255, 0, 255, 0.1)',
    border: '1px solid #ff00ff',
    borderRadius: '5px',
    padding: '20px',
    fontSize: '14px'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px',
    borderBottom: '2px solid #00ffff',
    marginBottom: '20px'
  },
  logoutBtn: {
    padding: '10px 20px',
    background: '#ff0000',
    border: 'none',
    borderRadius: '5px',
    color: '#fff',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  tabs: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px'
  },
  tab: {
    padding: '15px 30px',
    background: 'rgba(0, 255, 255, 0.1)',
    border: '2px solid #00ffff',
    borderRadius: '5px',
    color: '#00ffff',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold'
  },
  activeTab: {
    background: '#00ffff',
    color: '#000'
  },
  content: {
    padding: '20px'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px'
  },
  statCard: {
    background: 'rgba(0, 255, 255, 0.05)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '30px',
    textAlign: 'center'
  },
  statNumber: {
    fontSize: '48px',
    fontWeight: 'bold',
    color: '#00ffff',
    textShadow: '0 0 20px #00ffff'
  },
  table: {
    width: '100%'
  },
  dataTable: {
    width: '100%',
    borderCollapse: 'collapse',
    marginTop: '20px',
    fontSize: '14px'
  },
  revokeBtn: {
    padding: '5px 15px',
    background: '#ff0000',
    border: 'none',
    borderRadius: '3px',
    color: '#fff',
    cursor: 'pointer',
    fontSize: '12px'
  }
};
