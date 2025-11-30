// DNA-Key Authentication System - Dashboard Page
// Modern, futuristic dashboard for system monitoring and management

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalKeys: 0,
    activeKeys: 0,
    authenticationsToday: 0,
    securityScore: 100,
    threatLevel: 'GREEN',
    uptime: '99.99%'
  });
  
  const [recentActivity, setRecentActivity] = useState([]);
  const [systemHealth, setSystemHealth] = useState({
    database: 'healthy',
    blockchain: 'synced',
    threatIntel: 'active',
    neuralAuth: 'online'
  });
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulated data loading
    setTimeout(() => {
      setStats({
        totalKeys: 12847,
        activeKeys: 11293,
        authenticationsToday: 45892,
        securityScore: 98.7,
        threatLevel: 'GREEN',
        uptime: '99.99%'
      });
      
      setRecentActivity([
        { id: 1, type: 'enrollment', user: 'user@example.com', time: '2 min ago', status: 'success' },
        { id: 2, type: 'authentication', user: 'admin@corp.com', time: '5 min ago', status: 'success' },
        { id: 3, type: 'challenge', user: 'dev@startup.io', time: '8 min ago', status: 'success' },
        { id: 4, type: 'authentication', user: 'test@demo.com', time: '12 min ago', status: 'failed' },
        { id: 5, type: 'revocation', user: 'old@legacy.net', time: '15 min ago', status: 'success' },
      ]);
      
      setLoading(false);
    }, 1000);
  }, []);

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <div style={{...styles.statCard, borderColor: color}}>
      <div style={styles.statIcon}>{icon}</div>
      <div style={styles.statContent}>
        <div style={{...styles.statValue, color}}>{value}</div>
        <div style={styles.statTitle}>{title}</div>
        {subtitle && <div style={styles.statSubtitle}>{subtitle}</div>}
      </div>
    </div>
  );

  const HealthIndicator = ({ name, status }) => {
    const colors = {
      healthy: '#00ff00',
      synced: '#00ffff',
      active: '#ff00ff',
      online: '#ffff00',
      degraded: '#ffaa00',
      offline: '#ff0000'
    };
    
    return (
      <div style={styles.healthItem}>
        <div style={{...styles.healthDot, background: colors[status] || '#888'}}></div>
        <span style={styles.healthName}>{name}</span>
        <span style={{...styles.healthStatus, color: colors[status] || '#888'}}>
          {status.toUpperCase()}
        </span>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      {/* Background Grid */}
      <div style={styles.bgGrid}></div>
      
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logoIcon}>🔷</span>
          <div>
            <h1 style={styles.title}>DNA-KEY DASHBOARD</h1>
            <p style={styles.subtitle}>System Control Center</p>
          </div>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.threatIndicator}>
            <span style={styles.threatLabel}>THREAT LEVEL:</span>
            <span style={{...styles.threatValue, 
              color: stats.threatLevel === 'GREEN' ? '#00ff00' : 
                     stats.threatLevel === 'YELLOW' ? '#ffff00' : '#ff0000'}}>
              {stats.threatLevel}
            </span>
          </div>
          <a href="/" style={styles.navLink}>← Back to Main</a>
        </div>
      </header>

      {/* Stats Grid */}
      <div style={styles.statsGrid}>
        <StatCard
          title="Total DNA Keys"
          value={stats.totalKeys.toLocaleString()}
          icon="🧬"
          color="#00ffff"
          subtitle="Registered in system"
        />
        <StatCard
          title="Active Keys"
          value={stats.activeKeys.toLocaleString()}
          icon="⚡"
          color="#00ff00"
          subtitle="Currently valid"
        />
        <StatCard
          title="Auth Today"
          value={stats.authenticationsToday.toLocaleString()}
          icon="🔐"
          color="#ff00ff"
          subtitle="Successful authentications"
        />
        <StatCard
          title="Security Score"
          value={`${stats.securityScore}%`}
          icon="🛡️"
          color="#ffff00"
          subtitle="System health rating"
        />
      </div>

      {/* Main Content */}
      <div style={styles.mainContent}>
        {/* System Health Panel */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>⚙️ SYSTEM HEALTH</h2>
          <div style={styles.healthGrid}>
            <HealthIndicator name="Database Cluster" status={systemHealth.database} />
            <HealthIndicator name="Blockchain Registry" status={systemHealth.blockchain} />
            <HealthIndicator name="Threat Intelligence" status={systemHealth.threatIntel} />
            <HealthIndicator name="Neural Auth Engine" status={systemHealth.neuralAuth} />
          </div>
          <div style={styles.uptimeBar}>
            <span style={styles.uptimeLabel}>UPTIME:</span>
            <div style={styles.uptimeProgress}>
              <div style={{...styles.uptimeFill, width: stats.uptime}}></div>
            </div>
            <span style={styles.uptimeValue}>{stats.uptime}</span>
          </div>
        </div>

        {/* Recent Activity Panel */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>📊 RECENT ACTIVITY</h2>
          <div style={styles.activityList}>
            {recentActivity.map(activity => (
              <div key={activity.id} style={styles.activityItem}>
                <div style={styles.activityIcon}>
                  {activity.type === 'enrollment' && '🆕'}
                  {activity.type === 'authentication' && '🔑'}
                  {activity.type === 'challenge' && '🎯'}
                  {activity.type === 'revocation' && '🚫'}
                </div>
                <div style={styles.activityDetails}>
                  <div style={styles.activityType}>{activity.type.toUpperCase()}</div>
                  <div style={styles.activityUser}>{activity.user}</div>
                </div>
                <div style={styles.activityMeta}>
                  <div style={styles.activityTime}>{activity.time}</div>
                  <div style={{...styles.activityStatus, 
                    color: activity.status === 'success' ? '#00ff00' : '#ff0000'}}>
                    {activity.status.toUpperCase()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={styles.quickActions}>
        <h3 style={styles.actionsTitle}>⚡ QUICK ACTIONS</h3>
        <div style={styles.actionsGrid}>
          <a href="/" style={styles.actionBtn}>
            <span>🧬</span>
            <span>New Enrollment</span>
          </a>
          <a href="/admin" style={styles.actionBtn}>
            <span>👤</span>
            <span>Manage Users</span>
          </a>
          <a href="#" style={styles.actionBtn}>
            <span>📈</span>
            <span>View Analytics</span>
          </a>
          <a href="#" style={styles.actionBtn}>
            <span>⚙️</span>
            <span>System Settings</span>
          </a>
        </div>
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>🔷 DNA-Key Authentication System v1.0 | Dashboard 🔷</p>
        <p style={styles.footerMeta}>
          Last Updated: {new Date().toLocaleString()} | Server: Production
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
    overflow: 'hidden'
  },
  bgGrid: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px)
    `,
    backgroundSize: '40px 40px',
    zIndex: 0
  },
  header: {
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 40px',
    borderBottom: '2px solid #00ffff',
    background: 'rgba(0, 0, 0, 0.9)',
    backdropFilter: 'blur(10px)'
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
    textShadow: '0 0 10px #00ffff'
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
  threatIndicator: {
    padding: '10px 20px',
    background: 'rgba(0, 255, 0, 0.1)',
    border: '1px solid #00ff00',
    borderRadius: '5px'
  },
  threatLabel: {
    fontSize: '12px',
    color: '#888',
    marginRight: '10px'
  },
  threatValue: {
    fontSize: '16px',
    fontWeight: 'bold'
  },
  navLink: {
    color: '#00ffff',
    textDecoration: 'none',
    fontSize: '14px'
  },
  statsGrid: {
    position: 'relative',
    zIndex: 1,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    padding: '30px 40px'
  },
  statCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
    padding: '25px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid',
    borderRadius: '10px',
    transition: 'all 0.3s',
    cursor: 'pointer'
  },
  statIcon: {
    fontSize: '40px'
  },
  statContent: {
    flex: 1
  },
  statValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    textShadow: '0 0 15px currentColor'
  },
  statTitle: {
    fontSize: '14px',
    color: '#888',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  },
  statSubtitle: {
    fontSize: '11px',
    color: '#555',
    marginTop: '5px'
  },
  mainContent: {
    position: 'relative',
    zIndex: 1,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '20px',
    padding: '0 40px'
  },
  panel: {
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '25px',
    boxShadow: '0 0 30px rgba(0, 255, 255, 0.1)'
  },
  panelTitle: {
    fontSize: '18px',
    marginBottom: '20px',
    paddingBottom: '10px',
    borderBottom: '1px solid #00ffff33',
    letterSpacing: '2px'
  },
  healthGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  healthItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '10px 15px',
    background: 'rgba(0, 255, 255, 0.05)',
    borderRadius: '5px'
  },
  healthDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    boxShadow: '0 0 10px currentColor'
  },
  healthName: {
    flex: 1,
    fontSize: '14px'
  },
  healthStatus: {
    fontSize: '12px',
    fontWeight: 'bold'
  },
  uptimeBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    marginTop: '20px',
    padding: '15px',
    background: 'rgba(0, 255, 255, 0.05)',
    borderRadius: '5px'
  },
  uptimeLabel: {
    fontSize: '12px',
    color: '#888'
  },
  uptimeProgress: {
    flex: 1,
    height: '8px',
    background: '#111',
    borderRadius: '4px',
    overflow: 'hidden'
  },
  uptimeFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #00ffff, #00ff00)',
    borderRadius: '4px'
  },
  uptimeValue: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#00ff00'
  },
  activityList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  activityItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '12px 15px',
    background: 'rgba(0, 255, 255, 0.05)',
    borderRadius: '5px',
    borderLeft: '3px solid #00ffff'
  },
  activityIcon: {
    fontSize: '24px'
  },
  activityDetails: {
    flex: 1
  },
  activityType: {
    fontSize: '12px',
    fontWeight: 'bold',
    color: '#00ffff'
  },
  activityUser: {
    fontSize: '14px',
    color: '#888'
  },
  activityMeta: {
    textAlign: 'right'
  },
  activityTime: {
    fontSize: '11px',
    color: '#555'
  },
  activityStatus: {
    fontSize: '11px',
    fontWeight: 'bold'
  },
  quickActions: {
    position: 'relative',
    zIndex: 1,
    padding: '30px 40px'
  },
  actionsTitle: {
    fontSize: '16px',
    marginBottom: '20px',
    letterSpacing: '2px'
  },
  actionsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '15px'
  },
  actionBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '20px',
    background: 'rgba(255, 0, 255, 0.1)',
    border: '2px solid #ff00ff',
    borderRadius: '10px',
    color: '#ff00ff',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: 'bold',
    transition: 'all 0.3s',
    cursor: 'pointer',
    fontFamily: 'Orbitron, monospace'
  },
  footer: {
    position: 'relative',
    zIndex: 1,
    textAlign: 'center',
    padding: '30px',
    marginTop: '20px',
    borderTop: '1px solid #00ffff33',
    fontSize: '12px',
    color: '#666'
  },
  footerMeta: {
    marginTop: '5px',
    fontSize: '11px',
    color: '#444'
  }
};
