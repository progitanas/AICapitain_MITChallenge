# AI Captain - Maritime Route Optimization Engine

Backend IA pour l'optimisation des routes maritimes. Système complet d'optimisation multi-objectifs sans interface frontend.

## 📋 Architecture

```
backend/
├── data_engineering/        # Pipeline ETL & Graphe Géospatial
│   └── ais_processor.py     # Ingestion AIS + construction graphe
├── optimization_engine/     # Moteur d'optimisation
│   └── optimizer.py         # A* pondéré + solveur multi-objectifs
├── agents/                  # Agents IA
│   ├── monitoring_agent.py  # Détection de déviation + re-routing
│   └── forecasting_agent.py # Prédiction de congestion
├── api/                     # API REST
│   └── main.py             # FastAPI endpoints
├── models/                  # Data models
│   └── data_models.py      # Pydantic models
├── config/                  # Configuration
│   ├── settings.py         # Paramètres
│   └── logging_config.py   # Logging
└── requirements.txt         # Dépendances Python
```

## 🚀 Installation & Lancement

### 1. Créer un environnement virtuel

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 4. Lancer l'API

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur: **http://localhost:8000/api/v1**

Documentation interactive: **http://localhost:8000/api/v1/docs**

## 📡 API Endpoints Principaux

### Optimisation de Route

**POST** `/api/v1/route/optimize`

```json
{
  "vessel": {
    "mmsi": "257465900",
    "name": "D/S HANSTEEN",
    "dimensions": {
      "length_m": 120,
      "beam_m": 25,
      "draught_m": 8.5,
      "depth_m": 12
    },
    "latitude": 63.4,
    "longitude": 10.4,
    "sog_knots": 15,
    "cog_degrees": 90,
    "heading_degrees": 89
  },
  "start_port_id": "PORT_SG",
  "end_port_id": "PORT_HH",
  "weight_time": 1.0,
  "weight_cost": 1.0,
  "weight_risk": 1.0
}
```

**Response:**

```json
{
  "waypoints": [{"id": "PORT_SG", "name": "Singapore", "lat": 1.35, "lon": 103.82}, ...],
  "metrics": {
    "distance_nm": 7000,
    "time_hours": 350,
    "fuel_tons": 105,
    "cost_usd": 52500,
    "risk_score": 2.5
  },
  "blockages": [],
  "generated_at": "2025-11-08T10:30:00"
}
```

### Enregistrement Voyage (pour Monitoring)

**POST** `/api/v1/voyage/register`

```json
{
  "vessel_request": {...},
  "start_port": "PORT_SG",
  "end_port": "PORT_HH"
}
```

### Mise à jour Position (Real-time)

**PUT** `/api/v1/vessel/position`

```json
{
  "mmsi": "257465900",
  "latitude": 63.45,
  "longitude": 10.4,
  "timestamp": "2025-11-08T10:35:00"
}
```

### Prévision Congestion

**POST** `/api/v1/forecast/congestion`

```json
{
  "port_id": "PORT_HH",
  "arrival_date": "2025-11-15T14:00:00",
  "vessel_type": "container_ship"
}
```

**Response:**

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

### Sélectionner Meilleur Port Alternatif

**GET** `/api/v1/forecast/best-port?primary_port=PORT_HH&alternatives=PORT_RO,PORT_LA&arrival_date=2025-11-15T14:00:00`

### Status Système

**GET** `/api/v1/system/status`

## 🧠 Composants Clés

### 1. **Data Engineering (AIS Processor)**

- Ingère données AIS brutes (JSON)
- Crée des segments de voyage continus
- Construit un **Graphe Géospatial Dynamique** (NetworkX)
- Agrège les statistiques par arête (temps moyen, consommation)

### 2. **Moteur d'Optimisation (Weighted A\*)**

- Implémente **A\* pondéré** pour multi-objectifs
- Minimise: `W_time × time + W_cost × cost + W_risk × risk`
- Paramètres dynamiques (météo, congestion, chokepoints)
- Latence < 5 secondes pour routes transocéaniques

### 3. **Agent de Monitoring (Deviation Detection)**

- Surveille en temps réel les navires en voyage
- Détecte les déviances de trajectoire > seuil
- Déclenche **re-routing automatique** en cas de:
  - Tempête imprévue
  - Blocage de canal
  - Déviation significative de la route prévue

### 4. **Agent de Prédiction (Forecasting)**

- Prédit **temps d'attente aux ports** (Queue_Time)
- Modèles: Moyenne Mobile + Ajustement Saisonnier + Type de Navire
- Sélectionne le meilleur port alternatif
- Révise l'ETA en ajoutant la congestion prévue

## 📊 Data Models

### Vessel

```python
VesselSpec(
    mmsi: str,
    name: str,
    dimensions: VesselDimensions,
    current_position: Tuple[float, float],
    sog_knots: float,
    ...
)
```

### Optimized Route

```python
OptimizedRoute(
    waypoints: List[WayPoint],
    segments: List[RouteSegment],
    total_distance_nm: float,
    estimated_time_hours: float,
    estimated_fuel_tons: float,
    estimated_cost_usd: float,
    overall_risk_score: float,
)
```

### Rerouting Event

```python
ReroutingEvent(
    vessel_mmsi: str,
    trigger_type: str,  # 'storm', 'blockage', 'deviation'
    old_route: OptimizedRoute,
    new_route: OptimizedRoute,
    deviation_km: float,
)
```

## 🧪 Tests

```bash
pytest tests/ -v
pytest tests/ --cov=.
```

## 🔧 Configuration Avancée

Éditer `.env`:

```bash
# Paramètres d'optimisation
DEFAULT_WEIGHT_TIME=1.0
DEFAULT_WEIGHT_COST=1.0
DEFAULT_WEIGHT_RISK=1.5  # Priorité sécurité

# Monitoring
MONITORING_CHECK_INTERVAL_MINUTES=5
REROUTING_THRESHOLD_DEVIATION_KM=50.0  # Déclencher si > 50km

# APIs externes
WEATHER_API_KEY=your_key
```

## 📦 Déploiement Docker (Optionnel)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t ai-captain:latest .
docker run -p 8000:8000 ai-captain:latest
```

## 📈 Prochaines Étapes

1. **Intégration BigQuery** pour data lake
2. **APIs Météo** (WeatherAPI, NOAA)
3. **Vertex AI** pour ML avancé (time series forecasting)
4. **Authentification** (OAuth2)
5. **Message Queue** (RabbitMQ, Kafka) pour événements temps réel
6. **Monitoring** (Prometheus, Grafana)
7. **Tests unitaires & E2E** complets

## 📝 Licence

MIT

## 👤 Auteur

AI Captain - Maritime Logistics AI System
