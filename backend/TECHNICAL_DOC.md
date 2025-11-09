"""
Documentation technique complète du système AI Captain
Maritime Route Optimization Engine
"""

# ============================================================================

# AI CAPTAIN - SYSTÈME D'OPTIMISATION D'ITINÉRAIRE MARITIME AGENTIQUE

# ============================================================================

## 📋 TABLE DES MATIÈRES

1. [Architecture Générale](#architecture)
2. [Composants Clés](#composants)
3. [Algorithmes & Mathématiques](#algos)
4. [APIs & Endpoints](#apis)
5. [Déploiement & Configuration](#deploy)
6. [Prochaines Phases](#prochaines)

---

## ARCHITECTURE GÉNÉRALE

### 1.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                         AI Captain Backend                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  API REST (FastAPI)                                     │    │
│  │  POST /api/v1/route/optimize                           │    │
│  │  GET  /api/v1/route/alternatives                       │    │
│  │  POST /api/v1/voyage/register                          │    │
│  │  PUT  /api/v1/vessel/position                          │    │
│  │  POST /api/v1/forecast/congestion                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         AGENTS INTELLIGENTS (IA/ML)                      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                            │   │
│  │  ┌──────────────────┐    ┌───────────────────────┐      │   │
│  │  │ Monitoring Agent │    │ Forecasting Agent     │      │   │
│  │  │                  │    │                       │      │   │
│  │  │ • Deviation      │    │ • Time Series Model   │      │   │
│  │  │   Detection      │    │ • Port Congestion     │      │   │
│  │  │ • Re-routing     │    │   Forecast            │      │   │
│  │  │   Trigger        │    │ • Queue Prediction    │      │   │
│  │  │ • Storm Impact   │    │ • Port Selection      │      │   │
│  │  └──────────────────┘    └───────────────────────┘      │   │
│  │                                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │    MOTEUR D'OPTIMISATION (Weighted A*)                  │   │
│  │                                                            │   │
│  │  Minimise: W_t×T + W_c×C + W_r×R                         │   │
│  │  • Multi-objectifs (Temps, Coût, Risque)               │   │
│  │  • Contraintes dynamiques (météo, draft)               │   │
│  │  • Latence < 5 secondes                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   GRAPHE GÉOSPATIAL DYNAMIQUE (NetworkX)               │   │
│  │                                                            │   │
│  │  • Nodes: Ports internationaux (WPI)                    │   │
│  │  • Edges: Lanes de navigation avec:                     │   │
│  │    - Distance (NM)                                      │   │
│  │    - Temps de transit historique                        │   │
│  │    - Consommation de carburant                          │   │
│  │    - Risques météo/piraterie                            │   │
│  │  • Mise à jour dynamique                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │   PIPELINE ETL (Data Engineering)                       │   │
│  │                                                            │   │
│  │  • Ingestion AIS brutes (JSON/Parquet)                  │   │
│  │  • Construction segments de voyage                      │   │
│  │  • Agrégation statistiques par arête                    │   │
│  │  • Intégration contraintes géospatiales                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Architecture des dossiers

```
backend/
├── data_engineering/          # ETL & Graphe
│   ├── ais_processor.py       # Ingestion AIS + segments
│   └── __init__.py
│
├── optimization_engine/       # Moteur d'optimisation
│   ├── optimizer.py           # A* pondéré
│   └── __init__.py
│
├── agents/                    # Agents IA
│   ├── monitoring_agent.py    # Détection déviation
│   ├── forecasting_agent.py   # Prédiction congestion
│   └── __init__.py
│
├── api/                       # API REST
│   ├── main.py               # FastAPI app
│   └── __init__.py
│
├── models/                    # Data Models
│   ├── data_models.py        # Pydantic schemas
│   └── __init__.py
│
├── config/                    # Configuration
│   ├── settings.py           # Paramètres
│   ├── logging_config.py     # Logging
│   └── __init__.py
│
├── tests/                     # Tests unitaires
│   ├── test_ai_captain.py
│   └── __init__.py
│
├── requirements.txt           # Dépendances
├── README.md
├── .env.example
└── .gitignore
```

---

## COMPOSANTS CLÉS

### 2.1 Data Engineering Pipeline

#### AIS Data Processor

```
Entrée: AIS JSON brut (MMSI, TSTAMP, LAT, LON, SOG, COG, DRAUGHT, ...)
  ↓
1. Chargement & conversion types
2. Nettoyage (remove NaN, duplicates)
3. Tri par (MMSI, TSTAMP)
4. Création segments continus
   - Filtrer gaps > 1h (perte signal)
   - Calculer distance Haversine
   - Enregistrer temps, vitesse
5. Agrégation statistiques par arête
   - Temps moyen (hours)
   - Consommation moyenne (tons)
   - Observations (count)
  ↓
Sortie: DataFrame segments avec stats + Edges pour graphe
```

Exemple segment:

```python
{
    'mmsi': '257465900',
    'from_lat': 1.35, 'from_lon': 103.82,  # Singapore
    'to_lat': 5.12, 'to_lon': 100.34,      # Malaysia
    'distance_nm': 250,
    'time_hours': 20,
    'fuel_tons': 3.75,
    'sog_knots': 12.5
}
```

#### Geospatial Graph Builder

- Utilise NetworkX (DiGraph)
- Nodes: Ports internationaux (6+ majors)
- Edges: Shipping lanes avec attributes (distance, time, fuel, risk)
- Supports bidirectional routes
- Méthodes de query:
  - get_waypoint_by_proximity(lat, lon, radius)
  - get_graph_statistics()

### 2.2 Optimization Engine

#### Weighted A\* Algorithm

**Problème**: Shortest Path Multi-Objective

```
Minimize: C = W_time × T + W_cost × Cost + W_risk × R

Subject to:
- Navigability constraint (not in no-go zones)
- Draft constraint (vessel.draft ≤ route.min_depth)
- Canal/chokepoint restrictions
- Port availability
```

**Algorithme**:

```
1. Initialisation
   open_set = [Start node]
   g_cost[Start] = 0
   f_cost[Start] = heuristic(Start → End)

2. Boucle principale
   while open_set not empty and iterations < MAX:
       current = pop node with min f_cost from open_set

       if current == End:
           reconstruct_path(current)
           return path, iterations

       for neighbor in successors(current):
           edge_cost = compute_weighted_cost(current → neighbor)
           tentative_g = g_cost[current] + edge_cost

           if tentative_g < g_cost[neighbor]:
               came_from[neighbor] = current
               g_cost[neighbor] = tentative_g
               h = heuristic(neighbor → End)
               f = tentative_g + h
               push neighbor to open_set

3. Return None if no path found
```

**Heuristique admissible**:

```
h(n) = distance_to_goal_nm / 18_knots_avg_speed

Propriétés:
- Never overestimates (admissible)
- Consistent (monotonic)
- Efficient search (A* optimality)
```

**Fonction de coût d'arête**:

```python
def compute_edge_cost(from_node, to_node, params, current_time):
    # Récupérer données historiques
    time_hours = edge_data['time_hours_avg']
    fuel_tons = edge_data['fuel_consumption_tons']

    # Pénalité météo dynamique
    if params.weather_avoidance:
        weather_risk = interpolate_forecast(
            from_node, to_node, current_time
        )
        time_hours *= (1 + weather_risk * 0.2)

    # Coût du carburant
    fuel_cost = fuel_tons * params.fuel_price_per_ton

    # Score de risque (0-10)
    risk_score = weather_risk + piracy_risk

    # Coût pondéré
    total_cost = (
        params.weight_time * time_hours +
        params.weight_cost * fuel_cost +
        params.weight_risk * risk_score
    )

    return total_cost
```

### 2.3 Monitoring Agent

**Rôle**: Surveillance temps réel + re-routing automatique

**Entrées**:

- active_voyages: Dict[mmsi] → {planned_path, actual_positions}
- vessel_position_updates: Stream(mmsi, lat, lon, timestamp)
- alert_stream: Events (storm, blockage, anomaly)

**Détection de déviation**:

```python
def detect_deviation(vessel_mmsi):
    voyage = active_voyages[mmsi]
    current_pos = voyage.actual_positions[-1]

    # Trouver point le plus proche sur route prévue
    min_distance = inf
    for waypoint in voyage.planned_path:
        dist = haversine_distance(
            current_pos, waypoint
        )
        min_distance = min(min_distance, dist)

    if min_distance > THRESHOLD_KM:
        return ReroutingEvent(
            trigger='deviation',
            current_pos=current_pos,
            old_route=voyage.planned_route
        )
```

**Détection d'impact tempête**:

```python
def detect_storm_impact(vessel_mmsi, storm_location, radius_km):
    for waypoint in route.waypoints:
        dist_to_storm = haversine_distance(
            waypoint, storm_location
        )

        if dist_to_storm < radius_km:
            return ReroutingEvent(
                trigger='storm',
                affected_waypoint=waypoint,
                storm_location=storm_location
            )
```

**Actions de re-routing**:

```
1. Détecter événement critique
2. Récupérer position actuelle du navire
3. Re-calculer route optimale avec:
   - Poids priorité sécurité (W_risk 2.0×)
   - Contraintes actualisées
4. Comparer:
   - Temps supplémentaire
   - Déviation en km
   - Réduction de risque
5. Émettre notification + nouvelle route
```

### 2.4 Forecasting Agent

**Modèles de prédiction**:

1. **Moyenne Mobile (MA)**:

   ```
   MA_7d = average(wait_hours last 7 days)
   ```

2. **Ajustement Saisonnier**:

   ```
   seasonal_factor = mean(wait_hours | month == arrival_month)
   forecast = MA × seasonal_factor
   ```

3. **Ajustement par Type Navire**:

   ```
   type_factor = mean(wait_hours | vessel_type == arrival_type)
   ```

4. **Combinaison (Moyenne Pondérée)**:
   ```
   predicted_wait = (MA + seasonal + type_factor) / 3
   queue_length ≈ predicted_wait / 2.5  # ~1 navire par 2.5h
   ```

**Sélection port alternatif**:

```python
def select_best_alternate_port(primary, alternates, eta):
    best_score = inf
    best_port = None

    for port in alternates:
        forecast = forecast_congestion(port, eta)
        distance_nm = haversine(primary, port)

        # Scoring: minimiser temps + distance
        score = forecast.wait_hours + (distance_nm / 1000) * 0.1

        if score < best_score:
            best_score = score
            best_port = port

    return best_port
```

---

## ALGORITHMES & MATHÉMATIQUES

### 3.1 Fonction de coût multi-objectifs

$$C_{\text{total}} = W_{\text{Temps}} \times T + W_{\text{Coût}} \times C + W_{\text{Risque}} \times R$$

Où:

- $T$ = Temps de transit (hours)
- $C$ = Coût carburant (USD) = fuel_tons × price_per_ton
- $R$ = Score de risque normalisé (0-10)
- $W_i$ = Poids d'optimisation (contrôlés par utilisateur)

### 3.2 Distance Haversine

Pour calculer distance entre deux points géodésiques:

$$a = \sin^2(\Delta \phi / 2) + \cos(\phi_1) \times \cos(\phi_2) \times \sin^2(\Delta \lambda / 2)$$

$$c = 2 \times \arcsin(\sqrt{a})$$

$$d = R \times c$$

Où:

- $\phi$ = latitude (rad), $\lambda$ = longitude (rad)
- $R$ = 3440.065 NM (rayon terrestre en miles nautiques)

### 3.3 Complexité & Performance

**Weighted A\***:

- **Time Complexity**: $O(E \log V)$ where $E$ = edges, $V$ = nodes
- **Space Complexity**: $O(V)$
- **Target Latency**: < 5 seconds for transoceanic routes
- **Optimization Gap**: ~2-5% vs global optimum

**Benchmark Typical** (demo_aicaptain.ipynb):

```
Singapore → Hamburg (7000 NM)
  Iterations: 50-150
  Latency: 50-200 ms
  Route nodes: 4-6 ports
```

---

## APIs & ENDPOINTS

### 4.1 API REST Documentation

**Base URL**: `http://localhost:8000/api/v1`

**Health Check**:

```
GET /health
Response: {
  "status": "healthy",
  "app": "AI Captain - Maritime Route Optimization",
  "version": "0.1.0",
  "timestamp": "2025-11-08T10:30:00"
}
```

### 4.2 Route Optimization Endpoint

**POST** `/route/optimize`

Request:

```json
{
  "vessel": {
    "mmsi": "257465900",
    "imo": "123456789",
    "name": "D/S HANSTEEN",
    "call_sign": "LDQF",
    "dimensions": {
      "length_m": 120,
      "beam_m": 25,
      "draught_m": 8.5,
      "depth_m": 12
    },
    "type_code": 60,
    "latitude": 63.35,
    "longitude": 10.4,
    "sog_knots": 15,
    "cog_degrees": 137.6,
    "heading_degrees": 137,
    "nav_status": 0
  },
  "start_port_id": "PORT_SG",
  "end_port_id": "PORT_HH",
  "weight_time": 1.0,
  "weight_cost": 1.0,
  "weight_risk": 1.0,
  "fuel_price_per_ton": 500.0,
  "avoid_piracy_zones": true,
  "avoid_weather_risks": true
}
```

Response:

```json
{
  "waypoints": [
    { "id": "PORT_SG", "name": "Singapore", "lat": 1.3521, "lon": 103.8198 },
    { "id": "PORT_DU", "name": "Dubai", "lat": 25.2048, "lon": 55.2708 },
    { "id": "PORT_HH", "name": "Hamburg", "lat": 53.3495, "lon": 9.9878 }
  ],
  "metrics": {
    "distance_nm": 6850,
    "time_hours": 340,
    "fuel_tons": 102.75,
    "cost_usd": 51375,
    "risk_score": 2.3
  },
  "blockages": [],
  "generated_at": "2025-11-08T10:35:00"
}
```

### 4.3 Alternative Routes Endpoint

**GET** `/route/alternatives?start=PORT_SG&end=PORT_HH&num_alternatives=3`

Response:

```json
{
  "alternatives": [
    {
      "id": 0,
      "strategy": "time",
      "metrics": {
        "distance": 6850,
        "time": 340,
        "cost": 51375,
        "risk": 2.3
      }
    },
    {
      "id": 1,
      "strategy": "cost",
      "metrics": {...}
    },
    {
      "id": 2,
      "strategy": "risk",
      "metrics": {...}
    }
  ]
}
```

### 4.4 Voyage Registration Endpoint

**POST** `/voyage/register`

Request:

```json
{
  "vessel_request": {...},
  "start_port": "PORT_SG",
  "end_port": "PORT_HH"
}
```

Response:

```json
{
  "message": "Voyage registered",
  "mmsi": "257465900",
  "route_waypoints": 3
}
```

### 4.5 Position Update Endpoint

**PUT** `/vessel/position`

Request:

```json
{
  "mmsi": "257465900",
  "latitude": 63.45,
  "longitude": 10.4,
  "timestamp": "2025-11-08T10:35:00"
}
```

Response:

```json
{
  "status": "position_updated",
  "mmsi": "257465900",
  "deviation_detected": false,
  "rerouting_required": false
}
```

### 4.6 Congestion Forecast Endpoint

**POST** `/forecast/congestion`

Request:

```json
{
  "port_id": "PORT_HH",
  "arrival_date": "2025-11-15T14:00:00",
  "vessel_type": "container_ship"
}
```

Response:

```json
{
  "port_id": "PORT_HH",
  "predicted_queue_length": 3,
  "predicted_wait_hours": 6.5,
  "confidence_score": 0.85,
  "factors": {
    "moving_average": 6.2,
    "seasonal_adjustment": 6.8,
    "vessel_type_factor": 6.5
  }
}
```

### 4.7 Best Alternate Port Endpoint

**GET** `/forecast/best-port?primary_port=PORT_HH&alternatives=PORT_RO,PORT_DU&arrival_date=2025-11-15T14:00:00`

Response:

```json
{
  "best_port": "PORT_RO",
  "reason": "Lowest predicted congestion"
}
```

### 4.8 System Status Endpoint

**GET** `/system/status`

Response:

```json
{
  "app": "AI Captain - Maritime Route Optimization",
  "version": "0.1.0",
  "status": "operational",
  "graph": {
    "num_nodes": 6,
    "num_edges": 12,
    "waypoints": 6,
    "is_directed": true
  },
  "active_voyages": 2,
  "timestamp": "2025-11-08T10:35:00"
}
```

---

## DÉPLOIEMENT & CONFIGURATION

### 5.1 Installation locale

```bash
# 1. Clone repo
cd backend

# 2. Créer venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env avec vos params

# 5. Lancer API
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 6. Accéder à:
# http://localhost:8000/api/v1/docs  (Swagger)
# http://localhost:8000/api/v1/redoc (ReDoc)
```

### 5.2 Configuration (.env)

```bash
# Application
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost/aicaptain
REDIS_URL=redis://localhost:6379/0

# Optimization
DEFAULT_WEIGHT_TIME=1.0
DEFAULT_WEIGHT_COST=1.0
DEFAULT_WEIGHT_RISK=1.0
MAX_ROUTE_COMPUTE_TIME_SECONDS=5.0

# Monitoring
MONITORING_CHECK_INTERVAL_MINUTES=5
REROUTING_THRESHOLD_DEVIATION_KM=50.0

# Weather API
WEATHER_API_KEY=your_api_key_here
WEATHER_API_URL=https://api.weatherapi.com/v1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 5.3 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# Run
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build & Run:

```bash
docker build -t ai-captain:latest .
docker run -p 8000:8000 -e DATABASE_URL="..." ai-captain:latest
```

---

## PROCHAINES PHASES

### 6.1 Phase 2: Data Lake & BigQuery Integration

- [ ] Ingestion streaming de données AIS (Kafka/Pub-Sub)
- [ ] Stockage BigQuery (tables partitionnées par jour)
- [ ] Query optimisée pour calculs d'agrégation
- [ ] Cache Redis pour edges populaires
- [ ] ML pipeline pour feature engineering (Vertex AI)

### 6.2 Phase 3: Advanced ML Models

- [ ] Time Series Forecasting (Prophet, ARIMA)
- [ ] Neural Network pour prédiction Queue_Time
- [ ] Anomaly Detection (Isolation Forest)
- [ ] Graph Neural Networks (GNN) pour optimisation
- [ ] Reinforcement Learning pour adaptation dynamique

### 6.3 Phase 4: Real-time Streaming

- [ ] WebSocket pour live vessel tracking
- [ ] RabbitMQ/Kafka pour event streaming
- [ ] Real-time weather integration (NOAA, WeatherAPI)
- [ ] Piracy alerts + dynamic risk map
- [ ] Notification system (Push, SMS, Email)

### 6.4 Phase 5: Advanced Features

- [ ] Multi-leg itineraries (waypoints intermédiaires)
- [ ] Time-window constraints (port opening hours)
- [ ] Fuel consumption optimization curves (speed vs consumption)
- [ ] Environmental impact tracking (CO₂, emissions)
- [ ] Compliance checks (SOLAS, MARPOL, regional regs)
- [ ] Insurance premium optimization

### 6.5 Phase 6: Scale & Performance

- [ ] Load testing (1000+ concurrent requests)
- [ ] Distributed optimization (multi-node A\*)
- [ ] GPU acceleration for large graphs
- [ ] Caching layer (Redis, Memcached)
- [ ] CDN for static data
- [ ] Monitoring & alerting (Prometheus, Grafana)

---

## CONTACTS & SUPPORT

- **Documentation**: [Backend README](./README.md)
- **Demo Notebook**: [demo_aicaptain.ipynb](../demo_aicaptain.ipynb)
- **Tests**: `pytest tests/ -v`
- **API Docs**: http://localhost:8000/api/v1/docs

## LICENCE

MIT License - Maritime Logistics AI System

---

**Document version**: 0.1.0
**Last updated**: November 8, 2025
