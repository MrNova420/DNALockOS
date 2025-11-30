<!--
DNALockOS - DNA-Key Authentication System
Copyright (c) 2025 WeNova Interactive
Legal Owner: Kayden Shawn Massengill (Operating as WeNova Interactive)

PROPRIETARY AND CONFIDENTIAL - COMMERCIAL SOFTWARE
This is NOT free software. This is NOT open source. Commercial license required.
Unauthorized use is strictly prohibited.
-->

# DNALockOS Production Deployment Guide

## Overview

This guide covers deploying DNALockOS in production environments with:
- High availability configuration
- Security hardening
- Performance optimization
- Monitoring and alerting
- Backup and disaster recovery

---

## Pre-Deployment Checklist

### Security Requirements

- [ ] Generate strong `DNA_SECRET_KEY` (minimum 64 characters)
- [ ] Configure TLS/HTTPS with valid certificates
- [ ] Set up Web Application Firewall (WAF)
- [ ] Enable rate limiting
- [ ] Configure IP allowlisting for admin endpoints
- [ ] Set up intrusion detection system (IDS)
- [ ] Enable audit logging to external SIEM
- [ ] Configure HSM for key storage (recommended)

### Infrastructure Requirements

- [ ] Minimum 4 vCPU, 8GB RAM per API server
- [ ] PostgreSQL 14+ with replication
- [ ] Redis 7+ for caching/sessions
- [ ] Load balancer with health checks
- [ ] CDN for static assets
- [ ] Secure network segmentation

---

## Environment Variables

```bash
# =============================================================================
# CORE CONFIGURATION
# =============================================================================

# Server Settings
DNA_SERVER_HOST=0.0.0.0
DNA_SERVER_PORT=8000
DNA_WORKERS=4
DNA_DEBUG=false
DNA_LOG_LEVEL=INFO

# Security (REQUIRED - Generate strong values)
DNA_SECRET_KEY=<64-character-secure-random-string>
DNA_API_KEY_SALT=<32-character-secure-random-string>

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Primary Database
DNA_DATABASE_URL=postgresql://dnalock:password@db-primary:5432/dnalock
DNA_DATABASE_POOL_SIZE=20
DNA_DATABASE_MAX_OVERFLOW=10

# Read Replicas (comma-separated)
DNA_DATABASE_READ_REPLICAS=postgresql://dnalock:password@db-replica1:5432/dnalock,postgresql://dnalock:password@db-replica2:5432/dnalock

# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

DNA_REDIS_URL=redis://:password@redis-cluster:6379/0
DNA_REDIS_CLUSTER_ENABLED=true
DNA_CACHE_TTL=3600

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Session Management
DNA_SESSION_LIFETIME=28800
DNA_SESSION_IDLE_TIMEOUT=1800
DNA_MAX_CONCURRENT_SESSIONS=5
DNA_TOKEN_LIFETIME=3600

# Rate Limiting
DNA_RATE_LIMIT_ENABLED=true
DNA_RATE_LIMIT_REQUESTS_PER_MINUTE=60
DNA_RATE_LIMIT_BURST=100

# Neural Authentication
DNA_NEURAL_AUTH_ENABLED=true
DNA_NEURAL_MFA_THRESHOLD=0.3
DNA_NEURAL_BIOMETRIC_THRESHOLD=0.5
DNA_NEURAL_BLOCK_THRESHOLD=0.8

# Threat Intelligence
DNA_THREAT_INTEL_ENABLED=true
DNA_THREAT_INTEL_UPDATE_INTERVAL=300
DNA_MAX_FAILED_ATTEMPTS=5
DNA_LOCKOUT_DURATION=900

# =============================================================================
# BLOCKCHAIN CONFIGURATION
# =============================================================================

DNA_BLOCKCHAIN_ENABLED=true
DNA_BLOCKCHAIN_NETWORK=mainnet
DNA_BLOCKCHAIN_RPC_URL=https://rpc.dnalock.network
DNA_BLOCKCHAIN_CONFIRMATION_BLOCKS=6

# =============================================================================
# MONITORING CONFIGURATION
# =============================================================================

DNA_METRICS_ENABLED=true
DNA_METRICS_PORT=9090
DNA_HEALTH_CHECK_ENABLED=true

# External Services
DNA_SENTRY_DSN=https://xxx@sentry.io/xxx
DNA_DATADOG_API_KEY=xxx

# =============================================================================
# TLS/HTTPS CONFIGURATION
# =============================================================================

DNA_TLS_ENABLED=true
DNA_TLS_CERT_PATH=/etc/ssl/certs/dnalock.crt
DNA_TLS_KEY_PATH=/etc/ssl/private/dnalock.key
DNA_TLS_MIN_VERSION=TLSv1.3
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server/ ./server/
COPY docs/ ./docs/

# Create non-root user
RUN useradd -m -u 1000 dnalock && chown -R dnalock:dnalock /app
USER dnalock

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "server.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose (Production)

```yaml
version: '3.8'

services:
  api:
    build: .
    image: dnalock/api:latest
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    environment:
      - DNA_DATABASE_URL=postgresql://dnalock:${DB_PASSWORD}@db:5432/dnalock
      - DNA_REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - DNA_SECRET_KEY=${DNA_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=dnalock
      - POSTGRES_USER=dnalock
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dnalock"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--pass", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

---

## Kubernetes Deployment

### Namespace and Secrets

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dnalock
---
apiVersion: v1
kind: Secret
metadata:
  name: dnalock-secrets
  namespace: dnalock
type: Opaque
stringData:
  secret-key: "<your-64-character-secret-key>"
  db-password: "<database-password>"
  redis-password: "<redis-password>"
```

### API Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dnalock-api
  namespace: dnalock
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dnalock-api
  template:
    metadata:
      labels:
        app: dnalock-api
    spec:
      containers:
      - name: api
        image: dnalock/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DNA_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: dnalock-secrets
              key: secret-key
        - name: DNA_DATABASE_URL
          value: postgresql://dnalock:$(DB_PASSWORD)@dnalock-db:5432/dnalock
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: dnalock-secrets
              key: db-password
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: dnalock-api
  namespace: dnalock
spec:
  selector:
    app: dnalock-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dnalock-ingress
  namespace: dnalock
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.dnalock.example.com
    secretName: dnalock-tls
  rules:
  - host: api.dnalock.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dnalock-api
            port:
              number: 80
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dnalock-api-hpa
  namespace: dnalock
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dnalock-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Security Hardening

### 1. Network Security

```yaml
# Network Policy - Allow only necessary traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dnalock-api-policy
  namespace: dnalock
spec:
  podSelector:
    matchLabels:
      app: dnalock-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: dnalock-db
    ports:
    - port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: dnalock-redis
    ports:
    - port: 6379
```

### 2. Pod Security Standards

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dnalock-api
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: api
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

---

## Monitoring

### Prometheus Metrics

DNALockOS exposes metrics at `/metrics`:

```
# Authentication metrics
dnalock_auth_attempts_total{status="success|failure"}
dnalock_auth_latency_seconds{quantile="0.5|0.9|0.99"}

# Key management metrics
dnalock_keys_created_total
dnalock_keys_active_gauge
dnalock_key_verification_latency_seconds

# Security metrics
dnalock_threats_detected_total{type="brute_force|credential_stuffing|..."}
dnalock_blocked_requests_total

# System metrics
dnalock_request_duration_seconds
dnalock_active_sessions_gauge
```

### Grafana Dashboard

Import the provided dashboard JSON for visualization of:
- Authentication success/failure rates
- Key operations over time
- Threat detection alerts
- System health metrics

---

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR=/backups/postgres
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h db-primary -U dnalock -Fc dnalock > $BACKUP_DIR/dnalock_$DATE.dump

# Encrypt backup
gpg --symmetric --cipher-algo AES256 $BACKUP_DIR/dnalock_$DATE.dump

# Upload to S3
aws s3 cp $BACKUP_DIR/dnalock_$DATE.dump.gpg s3://dnalock-backups/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.dump*" -mtime +30 -delete
```

### Recovery Procedure

```bash
# Download backup
aws s3 cp s3://dnalock-backups/dnalock_20240115.dump.gpg .

# Decrypt
gpg --decrypt dnalock_20240115.dump.gpg > dnalock_20240115.dump

# Restore
pg_restore -h db-primary -U dnalock -d dnalock dnalock_20240115.dump
```

---

## Health Checks

### API Health Endpoint

```
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "blockchain": "healthy"
  },
  "uptime": 864000
}
```

### Readiness Check

```
GET /ready

Response:
{
  "ready": true,
  "checks": {
    "database_connection": true,
    "redis_connection": true,
    "config_loaded": true
  }
}
```

---

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check for memory leaks in long-running processes
   - Review cache configuration
   - Monitor DNA key generation for large security levels

2. **Slow Authentication**
   - Check database connection pool
   - Review neural auth thresholds
   - Monitor threat intelligence lookups

3. **Session Issues**
   - Verify Redis connectivity
   - Check session timeout configuration
   - Review concurrent session limits

### Log Analysis

```bash
# View API logs
kubectl logs -n dnalock -l app=dnalock-api --tail=100 -f

# Search for errors
kubectl logs -n dnalock -l app=dnalock-api | grep ERROR

# View audit logs
kubectl logs -n dnalock -l app=dnalock-api | grep "audit"
```

---

*Deployment Guide Version: 1.0.0*
