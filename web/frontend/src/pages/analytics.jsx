// DNA-Key Authentication System - Analytics Page
// Comprehensive analytics and statistics visualization

import React, { useState, useEffect } from 'react';

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7d');
  const [analyticsData, setAnalyticsData] = useState({
    totalAuthentications: 1247892,
    successRate: 99.7,
    averageResponseTime: 45,
    peakLoad: 12847,
    uniqueUsers: 45892,
    newEnrollments: 3847,
    dnaKeysGenerated: 52847,
    threatsBlocked: 1892
  });

  const [chartData, setChartData] = useState({
    hourly: [
      { hour: '00:00', auth: 1200, threats: 12 },
      { hour: '04:00', auth: 800, threats: 8 },
      { hour: '08:00', auth: 4500, threats: 45 },
      { hour: '12:00', auth: 6200, threats: 62 },
      { hour: '16:00', auth: 5800, threats: 58 },
      { hour: '20:00', auth: 3200, threats: 32 }
    ],
    securityLevels: [
      { level: 'STANDARD', count: 12847, percent: 15 },
      { level: 'ENHANCED', count: 25847, percent: 30 },
      { level: 'HIGH', count: 28947, percent: 34 },
      { level: 'MAXIMUM', count: 12847, percent: 15 },
      { level: 'ULTIMATE', count: 5128, percent: 6 }
    ],
    segmentTypes: [
      { type: 'HASH', count: 2500000 },
      { type: 'SIGNATURE', count: 1800000 },
      { type: 'ENCRYPTION', count: 1500000 },
      { type: 'QUANTUM', count: 800000 },
      { type: 'BIOMETRIC', count: 600000 },
      { type: 'OTHER', count: 1200000 }
    ],
    geoDistribution: [
      { region: 'North America', percent: 45 },
      { region: 'Europe', percent: 28 },
      { region: 'Asia Pacific', percent: 18 },
      { region: 'Latin America', percent: 6 },
      { region: 'Other', percent: 3 }
    ]
  });

  const StatCard = ({ title, value, icon, color, change, changeType }) => (
    <div style={{...styles.statCard, borderColor: color}}>
      <div style={styles.statIcon}>{icon}</div>
      <div style={styles.statContent}>
        <div style={{...styles.statValue, color}}>{value}</div>
        <div style={styles.statTitle}>{title}</div>
        {change && (
          <div style={{
            ...styles.statChange, 
            color: changeType === 'positive' ? '#00ff00' : 
                   changeType === 'negative' ? '#ff0000' : '#ffaa00'
          }}>
            {changeType === 'positive' ? '↑' : changeType === 'negative' ? '↓' : '→'} {change}
          </div>
        )}
      </div>
    </div>
  );

  const BarChart = ({ data, maxValue, label }) => (
    <div style={styles.barChart}>
      {data.map((item, i) => (
        <div key={i} style={styles.barContainer}>
          <div style={styles.barLabel}>{item.hour || item.level || item.type}</div>
          <div style={styles.barWrapper}>
            <div 
              style={{
                ...styles.bar,
                width: `${(item.auth || item.count || item.percent) / maxValue * 100}%`
              }}
            />
          </div>
          <div style={styles.barValue}>
            {(item.auth || item.count || item.percent)?.toLocaleString()}
            {item.percent !== undefined && '%'}
          </div>
        </div>
      ))}
    </div>
  );

  const DonutChart = ({ data }) => {
    let cumulativePercent = 0;
    const colors = ['#00ffff', '#ff00ff', '#00ff00', '#ffff00', '#ff8800', '#8888ff'];
    
    return (
      <div style={styles.donutContainer}>
        <svg viewBox="0 0 100 100" style={styles.donutSvg}>
          {data.map((item, i) => {
            const startAngle = cumulativePercent * 3.6;
            cumulativePercent += item.percent;
            const endAngle = cumulativePercent * 3.6;
            
            const startRad = (startAngle - 90) * Math.PI / 180;
            const endRad = (endAngle - 90) * Math.PI / 180;
            
            const x1 = 50 + 40 * Math.cos(startRad);
            const y1 = 50 + 40 * Math.sin(startRad);
            const x2 = 50 + 40 * Math.cos(endRad);
            const y2 = 50 + 40 * Math.sin(endRad);
            
            const largeArc = item.percent > 50 ? 1 : 0;
            
            return (
              <path
                key={i}
                d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`}
                fill={colors[i % colors.length]}
                opacity="0.8"
              />
            );
          })}
          <circle cx="50" cy="50" r="25" fill="#000" />
          <text x="50" y="50" textAnchor="middle" dy="0.3em" fill="#00ffff" fontSize="8" fontFamily="Orbitron">
            {data.length} TYPES
          </text>
        </svg>
        <div style={styles.donutLegend}>
          {data.map((item, i) => (
            <div key={i} style={styles.legendItem}>
              <div style={{...styles.legendColor, background: colors[i % colors.length]}}></div>
              <span style={styles.legendLabel}>{item.level || item.region}</span>
              <span style={styles.legendValue}>{item.percent}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      <div style={styles.bgGrid}></div>
      
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logoIcon}>📊</span>
          <div>
            <h1 style={styles.title}>SYSTEM ANALYTICS</h1>
            <p style={styles.subtitle}>Real-Time Performance Metrics</p>
          </div>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.timeSelector}>
            {['24h', '7d', '30d', '90d'].map(range => (
              <button
                key={range}
                style={{
                  ...styles.timeBtn,
                  background: timeRange === range ? 'rgba(0, 255, 255, 0.3)' : 'transparent',
                  borderColor: timeRange === range ? '#00ffff' : '#333'
                }}
                onClick={() => setTimeRange(range)}
              >
                {range}
              </button>
            ))}
          </div>
          <a href="/dashboard" style={styles.navLink}>← Back to Dashboard</a>
        </div>
      </header>

      {/* Main Stats */}
      <div style={styles.statsGrid}>
        <StatCard
          title="Total Authentications"
          value={analyticsData.totalAuthentications.toLocaleString()}
          icon="🔐"
          color="#00ffff"
          change="+12.5%"
          changeType="positive"
        />
        <StatCard
          title="Success Rate"
          value={`${analyticsData.successRate}%`}
          icon="✓"
          color="#00ff00"
          change="+0.3%"
          changeType="positive"
        />
        <StatCard
          title="Avg Response Time"
          value={`${analyticsData.averageResponseTime}ms`}
          icon="⚡"
          color="#ffff00"
          change="-5ms"
          changeType="positive"
        />
        <StatCard
          title="Peak Load"
          value={`${analyticsData.peakLoad.toLocaleString()}/min`}
          icon="📈"
          color="#ff00ff"
          change="+8%"
          changeType="neutral"
        />
        <StatCard
          title="Unique Users"
          value={analyticsData.uniqueUsers.toLocaleString()}
          icon="👥"
          color="#00ffff"
          change="+2,847"
          changeType="positive"
        />
        <StatCard
          title="New Enrollments"
          value={analyticsData.newEnrollments.toLocaleString()}
          icon="🆕"
          color="#00ff00"
          change="+847"
          changeType="positive"
        />
        <StatCard
          title="DNA Keys Generated"
          value={analyticsData.dnaKeysGenerated.toLocaleString()}
          icon="🧬"
          color="#ff00ff"
          change="+5,847"
          changeType="positive"
        />
        <StatCard
          title="Threats Blocked"
          value={analyticsData.threatsBlocked.toLocaleString()}
          icon="🛡️"
          color="#ff0000"
          change="+247"
          changeType="negative"
        />
      </div>

      {/* Charts Section */}
      <div style={styles.chartsGrid}>
        {/* Hourly Activity */}
        <div style={styles.chartPanel}>
          <h2 style={styles.chartTitle}>📉 AUTHENTICATION ACTIVITY</h2>
          <BarChart 
            data={chartData.hourly} 
            maxValue={7000}
            label="Authentications"
          />
        </div>

        {/* Security Levels Distribution */}
        <div style={styles.chartPanel}>
          <h2 style={styles.chartTitle}>🏰 SECURITY LEVEL DISTRIBUTION</h2>
          <DonutChart data={chartData.securityLevels} />
        </div>

        {/* Segment Types */}
        <div style={styles.chartPanel}>
          <h2 style={styles.chartTitle}>🧬 DNA SEGMENT TYPES</h2>
          <BarChart 
            data={chartData.segmentTypes}
            maxValue={3000000}
            label="Segments"
          />
          <div style={styles.totalSegments}>
            <span style={styles.totalLabel}>Total Segments Generated:</span>
            <span style={styles.totalValue}>8,400,000</span>
          </div>
        </div>

        {/* Geographic Distribution */}
        <div style={styles.chartPanel}>
          <h2 style={styles.chartTitle}>🌍 GEOGRAPHIC DISTRIBUTION</h2>
          <DonutChart data={chartData.geoDistribution} />
        </div>
      </div>

      {/* Performance Metrics */}
      <div style={styles.performanceSection}>
        <h2 style={styles.sectionTitle}>⚡ PERFORMANCE METRICS</h2>
        <div style={styles.performanceGrid}>
          {/* Latency bars use 200ms as max scale for meaningful visualization */}
          <div style={styles.performanceCard}>
            <div style={styles.perfLabel}>API Latency (p50)</div>
            <div style={styles.perfValue}>23ms</div>
            <div style={styles.perfBar}>
              <div style={{...styles.perfFill, width: `${(23/200)*100}%`, background: '#00ff00'}}></div>
            </div>
          </div>
          <div style={styles.performanceCard}>
            <div style={styles.perfLabel}>API Latency (p95)</div>
            <div style={styles.perfValue}>67ms</div>
            <div style={styles.perfBar}>
              <div style={{...styles.perfFill, width: `${(67/200)*100}%`, background: '#ffff00'}}></div>
            </div>
          </div>
          <div style={styles.performanceCard}>
            <div style={styles.perfLabel}>API Latency (p99)</div>
            <div style={styles.perfValue}>124ms</div>
            <div style={styles.perfBar}>
              <div style={{...styles.perfFill, width: `${(124/200)*100}%`, background: '#ffaa00'}}></div>
            </div>
          </div>
          <div style={styles.performanceCard}>
            <div style={styles.perfLabel}>Throughput</div>
            <div style={styles.perfValue}>12,847 req/s</div>
            <div style={styles.perfBar}>
              {/* 15,000 req/s as max capacity */}
              <div style={{...styles.perfFill, width: `${(12847/15000)*100}%`, background: '#00ffff'}}></div>
            </div>
          </div>
          <div style={styles.performanceCard}>
            <div style={styles.perfLabel}>Error Rate</div>
            <div style={styles.perfValue}>0.03%</div>
            <div style={styles.perfBar}>
              {/* Error rate: lower is better, 1% max scale */}
              <div style={{...styles.perfFill, width: `${(0.03/1)*100}%`, background: '#00ff00'}}></div>
            </div>
          </div>
          <div style={styles.performanceCard}>
            <div style={styles.perfLabel}>CPU Utilization</div>
            <div style={styles.perfValue}>42%</div>
            <div style={styles.perfBar}>
              <div style={{...styles.perfFill, width: '42%', background: '#00ffff'}}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>📊 DNALockOS Analytics Dashboard | Real-Time Metrics 📊</p>
        <p style={styles.footerMeta}>
          Data refreshed every 30 seconds | Last update: {new Date().toLocaleString()}
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
    position: 'relative'
  },
  bgGrid: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `
      linear-gradient(rgba(0, 255, 255, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 255, 255, 0.02) 1px, transparent 1px)
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
  timeSelector: {
    display: 'flex',
    gap: '10px'
  },
  timeBtn: {
    padding: '8px 15px',
    border: '1px solid',
    borderRadius: '5px',
    background: 'transparent',
    color: '#00ffff',
    fontSize: '12px',
    cursor: 'pointer',
    fontFamily: 'Orbitron, monospace'
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
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '15px',
    padding: '30px 40px'
  },
  statCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    padding: '20px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid',
    borderRadius: '10px'
  },
  statIcon: {
    fontSize: '30px'
  },
  statContent: {},
  statValue: {
    fontSize: '20px',
    fontWeight: 'bold'
  },
  statTitle: {
    fontSize: '10px',
    color: '#888',
    textTransform: 'uppercase'
  },
  statChange: {
    fontSize: '11px',
    marginTop: '5px'
  },
  chartsGrid: {
    position: 'relative',
    zIndex: 1,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '20px',
    padding: '0 40px'
  },
  chartPanel: {
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid #00ffff',
    borderRadius: '10px',
    padding: '25px'
  },
  chartTitle: {
    fontSize: '14px',
    marginBottom: '20px',
    paddingBottom: '10px',
    borderBottom: '1px solid #00ffff33',
    letterSpacing: '2px'
  },
  barChart: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  barContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  },
  barLabel: {
    width: '80px',
    fontSize: '11px',
    color: '#888',
    textAlign: 'right'
  },
  barWrapper: {
    flex: 1,
    height: '20px',
    background: 'rgba(0, 255, 255, 0.1)',
    borderRadius: '3px',
    overflow: 'hidden'
  },
  bar: {
    height: '100%',
    background: 'linear-gradient(90deg, #00ffff, #ff00ff)',
    borderRadius: '3px',
    transition: 'width 0.5s'
  },
  barValue: {
    width: '80px',
    fontSize: '11px',
    color: '#00ffff',
    fontWeight: 'bold'
  },
  donutContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '30px'
  },
  donutSvg: {
    width: '150px',
    height: '150px'
  },
  donutLegend: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '11px'
  },
  legendColor: {
    width: '12px',
    height: '12px',
    borderRadius: '3px'
  },
  legendLabel: {
    flex: 1,
    color: '#888'
  },
  legendValue: {
    color: '#00ffff',
    fontWeight: 'bold'
  },
  totalSegments: {
    marginTop: '20px',
    padding: '15px',
    background: 'rgba(0, 255, 0, 0.1)',
    border: '1px solid #00ff00',
    borderRadius: '5px',
    textAlign: 'center'
  },
  totalLabel: {
    fontSize: '11px',
    color: '#888',
    marginRight: '10px'
  },
  totalValue: {
    fontSize: '18px',
    color: '#00ff00',
    fontWeight: 'bold'
  },
  performanceSection: {
    position: 'relative',
    zIndex: 1,
    padding: '30px 40px'
  },
  sectionTitle: {
    fontSize: '16px',
    marginBottom: '20px',
    letterSpacing: '2px'
  },
  performanceGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '15px'
  },
  performanceCard: {
    padding: '20px',
    background: 'rgba(0, 0, 0, 0.8)',
    border: '2px solid #00ffff',
    borderRadius: '10px'
  },
  perfLabel: {
    fontSize: '11px',
    color: '#888',
    marginBottom: '5px'
  },
  perfValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#00ffff',
    marginBottom: '10px'
  },
  perfBar: {
    height: '6px',
    background: 'rgba(0, 255, 255, 0.1)',
    borderRadius: '3px',
    overflow: 'hidden'
  },
  perfFill: {
    height: '100%',
    borderRadius: '3px'
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
