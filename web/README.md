# DNA-Key Authentication System - Web Application

## 🔷 Tron-Inspired Futuristic Interface 🔷

Complete web application with 3D visual DNA rendering, admin dashboard, and authentication flows.

## Features

### Frontend (Next.js + React + Three.js)
- **Main Page**: DNA key enrollment with real-time 3D visualization
- **Admin Dashboard**: DNA-Key protected admin interface
- **3D DNA Visualizer**: Three.js rendering of unique DNA helices
- **Tron-Inspired UI**: Futuristic cyan/magenta color scheme with glow effects

### Backend (FastAPI)
- **REST API**: Complete OpenAPI documented endpoints
- **DNA-Key Auth**: Admin endpoints protected by DNA-Key authentication
- **Visual DNA Generator**: Creates unique 3D helix data for each key

## Quick Start

### Backend
```bash
cd /home/runner/work/DNALockOS/DNALockOS
pip install fastapi uvicorn pydantic
python -m server.api.main
```

Server runs on: http://localhost:8000
API docs: http://localhost:8000/api/docs

### Frontend
```bash
cd web/frontend
npm install
npm run dev
```

Web app runs on: http://localhost:3000

## API Endpoints

### Public Endpoints
- `POST /api/v1/enroll` - Enroll new DNA key
- `POST /api/v1/challenge` - Get authentication challenge
- `POST /api/v1/authenticate` - Authenticate with signed challenge
- `GET /api/v1/visual/{key_id}` - Get 3D visual DNA config

### Admin Endpoints (DNA-Key Protected)
- `POST /api/v1/admin/revoke` - Revoke DNA key
- `GET /api/v1/admin/stats` - System statistics
- `GET /api/v1/admin/keys` - List all enrolled keys
- `GET /api/v1/admin/revocations` - Revocation history
- `DELETE /api/v1/admin/challenges/cleanup` - Cleanup expired challenges

## Admin Authentication

The admin dashboard uses DNA-Key authentication:
1. Admin enters their DNA-Key ID
2. System generates challenge
3. Admin signs challenge with their DNA key
4. System verifies signature and issues session token
5. Admin can access all admin endpoints with token

## 3D DNA Visualization

Each DNA key gets a unique 3D visualization:
- **Geometry**: Double helix with thousands of points
- **Colors**: Each segment type has unique color (10 types)
- **Animation**: Rotating helix with pulse effect
- **Particles**: Flowing particle effects
- **Glow**: Each point glows based on segment data

Colors:
- Cyan (#00FFFF) - Entropy
- Magenta (#FF00FF) - Policy
- Yellow (#FFFF00) - Hash
- Green (#00FF00) - Temporal
- Red (#FF0000) - Capability
- Blue (#0000FF) - Signature
- Orange (#FFA500) - Metadata
- Purple (#800080) - Biometric
- Turquoise (#00CED1) - Geolocation
- Pink (#FF1493) - Revocation

## Technology Stack

- **Backend**: FastAPI, Python 3.12+
- **Frontend**: Next.js 14, React 18
- **3D Rendering**: Three.js, React Three Fiber
- **Styling**: Tron-inspired CSS-in-JS
- **API**: REST with OpenAPI 3.0
- **Auth**: DNA-Key challenge-response

## Security

- All admin endpoints require DNA-Key authentication
- Session tokens expire after 1 hour
- Challenges expire after 5 minutes
- One-time use challenges
- CORS configured for production
