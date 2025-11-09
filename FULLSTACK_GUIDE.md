# Full Stack Development Guide

## Phase 2: Frontend Implementation

Vous êtes maintenant passé au **Full Stack**! Le backend AI Captain est prêt, maintenant on construit un frontend **professionnel et premium**.

### Vue d'ensemble

```
AI CAPTAIN - Full Stack Architecture
=====================================

                    Frontend (React)
                    Port 3000
                         │
                         ├─ Dashboard
                         ├─ Route Optimization
                         ├─ Vessel Monitoring
                         ├─ Analytics
                         └─ Settings
                         │
                    ↓ (API Calls)

                    Backend (FastAPI)
                    Port 8000
                         │
                         ├─ /health
                         ├─ /api/v1/route/optimize
                         ├─ /api/v1/route/alternatives
                         ├─ /api/v1/voyage/register
                         ├─ /api/v1/vessel/position
                         ├─ /api/v1/forecast/congestion
                         ├─ /api/v1/forecast/best-port
                         └─ /api/v1/system/status
```

### 1. Installation Initiale

```bash
# Backend: Vérifier que tout tourne
cd c:\Users\dell\AICapitain_MITChallenge
python -m uvicorn backend.api.main:app --port 8000

# Dans un nouveau terminal - Frontend
cd frontend
npm install

# Vérifier la version de Node
node --version  # Doit être >= 18
npm --version   # Doit être >= 9
```

### 2. Développement Local

#### Terminal 1: Backend

```bash
cd c:\Users\dell\AICapitain_MITChallenge
python -m uvicorn backend.api.main:app --port 8000 --reload
# Output: Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 2: Frontend

```bash
cd frontend
npm run dev
# Output: VITE v5.0.0  ready in XXX ms
#         ➜  Local:   http://localhost:3000/
#         ➜  press h to show help
```

Ouvrir navigateur: **http://localhost:3000**

### 3. Structure Complète

```
c:\Users\dell\AICapitain_MITChallenge\
├── backend/                          # Backend AI (Python/FastAPI)
│   ├── api/
│   ├── agents/
│   ├── config/
│   ├── data_engineering/
│   ├── models/
│   ├── optimization_engine/
│   ├── tests/
│   ├── ais_data.json
│   ├── requirements.txt
│   ├── Dockerfile
│   └── TECHNICAL_DOC.md
│
├── frontend/                         # Frontend Pro (React/TypeScript)
│   ├── src/
│   │   ├── components/              # UI Components réutilisables
│   │   ├── layouts/
│   │   ├── pages/                   # Pages principales
│   │   ├── services/                # API integration
│   │   ├── stores/                  # Zustand state management
│   │   ├── types/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── .eslintrc.json
│   ├── .prettierrc.json
│   ├── Dockerfile
│   └── README.md
│
└── docs/
    ├── README.md                    # Main overview
    ├── FINAL_STATUS_REPORT.md
    ├── QUICKSTART.md
    └── ...
```

### 4. Stack & Technologies

**Backend (Existant)**

- Python 3.14
- FastAPI
- NetworkX (graphes)
- Pandas (données)
- PyTest (tests)

**Frontend (Nouveau)**

- React 18 + TypeScript
- Vite (bundler)
- Tailwind CSS (design)
- React Router (navigation)
- Zustand (state)
- Axios (HTTP)
- Leaflet (cartes)
- Recharts (graphiques)

### 5. Prochaines Étapes

#### Phase 2.1: Composants UI (2-3 jours)

```bash
npm run dev  # Dev server

# Créer les composants de base:
src/components/
├── Button.tsx
├── Card.tsx
├── Input.tsx
├── Select.tsx
├── Modal.tsx
├── Spinner.tsx
├── Alert.tsx
└── Avatar.tsx
```

#### Phase 2.2: Pages (3-4 jours)

```bash
src/pages/
├── Dashboard.tsx              # KPIs + Overview
├── RouteOptimization.tsx      # Formulaire + Résultats
├── VesselMonitoring.tsx       # Carte + Tracking
├── Analytics.tsx              # Graphiques
└── Settings.tsx               # Préférences
```

#### Phase 2.3: Intégration API (2-3 jours)

```typescript
// src/services/api.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 10000,
});

export const routeService = {
  optimize: (data) => apiClient.post("/api/v1/route/optimize", data),
  alternatives: (from, to) =>
    apiClient.get(`/api/v1/route/alternatives?from=${from}&to=${to}`),
};

export const vesselService = {
  register: (data) => apiClient.post("/api/v1/voyage/register", data),
  updatePosition: (data) => apiClient.put("/api/v1/vessel/position", data),
};

export const forecastService = {
  congestion: (data) => apiClient.post("/api/v1/forecast/congestion", data),
  bestPort: (port) =>
    apiClient.get(`/api/v1/forecast/best-port?destination=${port}`),
};
```

#### Phase 2.4: Testing & QA (2 jours)

```bash
npm run type-check   # TypeScript validation
npm run lint         # Code quality
npm run build        # Production build
npm run preview      # Test build
```

#### Phase 2.5: Docker & Deployment (1-2 jours)

```bash
# Build images
docker build -t aicaptain-backend:1.0.0 -f backend/Dockerfile .
docker build -t aicaptain-frontend:1.0.0 -f frontend/Dockerfile .

# Run with Docker Compose
docker-compose up -d
```

### 6. Configuration Locale (.env)

**Frontend**: `frontend/.env.local`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Captain
VITE_LOG_LEVEL=debug
```

**Backend**: `backend/.env`

```env
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
AIS_DATA_PATH=./backend/ais_data.json
```

### 7. Commandes Essentielles

```bash
# Frontend
npm run dev              # Démarrer dev server
npm run build            # Build production
npm run preview          # Prévisualiser build
npm run lint             # ESLint
npm run format           # Prettier
npm run type-check       # TypeScript check

# Backend
python -m pytest         # Tests
python -m pytest -v      # Tests verbose
pip install -r requirements.txt  # Dépendances
```

### 8. Vérification du Setup

```bash
# Terminal 1: Backend
curl http://localhost:8000/health
# Response: {"status":"healthy","version":"0.1.0"}

# Terminal 2: Frontend
curl http://localhost:3000
# Response: HTML + assets

# Browser
http://localhost:3000              # Frontend
http://localhost:8000/api/v1/docs  # Swagger API
```

### 9. Checklist Final

- [ ] Backend tourne sur :8000
- [ ] Frontend tourne sur :3000
- [ ] npm install sans erreurs
- [ ] npm run type-check passe
- [ ] npm run lint passe
- [ ] npm run dev marche
- [ ] API health check répond
- [ ] Pages chargent

### 10. Troubleshooting

**Port 3000/8000 déjà utilisé**

```bash
# Trouver le process
lsof -i :3000

# Tuer le process
kill -9 <PID>
```

**CORS issues**

```
Vérifier vite.config.ts proxy settings
Vérifier backend CORS configuration
```

**npm ERR!**

```bash
npm cache clean --force
rm -rf node_modules
npm install
```

**TypeScript errors**

```bash
npm run type-check
Fixer les erreurs avant de commit
```

### Documentation

- **Backend**: `backend/TECHNICAL_DOC.md` (70+ pages)
- **Frontend**: `frontend/README.md` (à compléter)
- **API**: `http://localhost:8000/api/v1/docs` (Swagger)
- **Concepts**: `INDEX.md`

### Support & Resources

- React: https://react.dev
- Vite: https://vitejs.dev
- Tailwind: https://tailwindcss.com
- TypeScript: https://www.typescriptlang.org
- React Router: https://reactrouter.com

---

**Status**: 🟢 Ready for Full Stack Development  
**Backend**: ✅ Production Ready  
**Frontend**: 🚀 Ready to Build  
**Timeline**: 2 weeks estimate

Vous êtes prêts à construire une plateforme **professionnelle et scalable**! 🚀
