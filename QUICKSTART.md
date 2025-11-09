# 🚀 QUICK START - AI Captain Backend

## Vue d'ensemble rapide

Ceci est le **Backend IA complet** du système AI Captain (sans frontend). Il comprend:

✅ **Moteur d'Optimisation Multi-Objectifs** (Weighted A\*)  
✅ **Pipeline ETL pour données AIS**  
✅ **Agent de Monitoring** (Détection de déviation + Re-routing)  
✅ **Agent de Prédiction** (Congestion portuaire)  
✅ **API REST** (FastAPI)  
✅ **Notebook de démonstration** (Interactive)

---

## 📋 Prérequis

- **Python 3.9+**
- **pip** (gestionnaire de packages)
- ~500 MB espace disque
- Les données AIS JSON (`ais_data.json`) dans `c:\Users\dell\Downloads\`

---

## ⚡ Lancement rapide (5 min)

### Sur Windows:

```bash
cd c:\Users\dell\AICapitain_MITChallenge\backend

# Option 1: Cliquer sur run.bat
run.bat

# Option 2: Cmd/PowerShell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Sur Linux/Mac:

```bash
cd /path/to/AICapitain_MITChallenge/backend

# Rendre le script exécutable
chmod +x run.sh

# Lancer
./run.sh
```

### Une fois que le serveur est lancé:

```
✓ L'API sera disponible à: http://localhost:8000/api/v1

📍 Documentation interactive:
   http://localhost:8000/api/v1/docs  (Swagger UI)
   http://localhost:8000/api/v1/redoc (ReDoc)

📍 Health check:
   http://localhost:8000/health
```

---

## 🎮 Test basique (dans Swagger UI)

1. Ouvrir http://localhost:8000/api/v1/docs
2. Cliquer sur **POST** `/route/optimize`
3. Cliquer **"Try it out"**
4. Remplacer le JSON par:

```json
{
  "vessel": {
    "mmsi": "257465900",
    "imo": "123456789",
    "name": "Test Vessel",
    "call_sign": "TEST",
    "dimensions": {
      "length_m": 120,
      "beam_m": 25,
      "draught_m": 8.5,
      "depth_m": 12
    },
    "type_code": 60,
    "latitude": 1.3521,
    "longitude": 103.8198,
    "sog_knots": 15,
    "cog_degrees": 90,
    "heading_degrees": 90,
    "nav_status": 0
  },
  "start_port_id": "PORT_SG",
  "end_port_id": "PORT_HH",
  "weight_time": 1.0,
  "weight_cost": 1.0,
  "weight_risk": 1.0
}
```

5. Cliquer **"Execute"**

Résultat attendu:

```json
{
  "waypoints": [...],
  "metrics": {
    "distance_nm": 6850,
    "time_hours": 340,
    "fuel_tons": 102.75,
    "cost_usd": 51375,
    "risk_score": 2.3
  }
}
```

---

## 📊 Exécuter la démonstration interactive

### Avec Jupyter Notebook:

```bash
cd c:\Users\dell\AICapitain_MITChallenge

# Installer Jupyter (si nécessaire)
pip install jupyter

# Lancer Jupyter
jupyter notebook

# Ouvrir demo_aicaptain.ipynb
```

La démonstration exécute:

- ✅ Chargement données AIS
- ✅ Construction graphe géospatial
- ✅ Optimisation multi-objectifs (3 stratégies)
- ✅ Détection de déviation en temps réel
- ✅ Prédiction de congestion portuaire
- ✅ Parsing NLP de requêtes naturelles
- ✅ Benchmarking performance

**Durée**: ~2-3 minutes d'exécution

---

## 🧪 Tests unitaires

```bash
# Installer pytest (si nécessaire)
pip install pytest pytest-cov

# Lancer tous les tests
pytest backend/tests/ -v

# Avec couverture de code
pytest backend/tests/ -v --cov=backend --cov-report=html
```

Expected output:

```
test_ai_captain.py::TestAISProcessor::test_haversine_distance_calculation PASSED
test_ai_captain.py::TestGeospatialGraph::test_add_waypoint PASSED
test_ai_captain.py::TestOptimizer::test_find_route_exists PASSED
...
======================== X passed in Y.XXs =========================
```

---

## 📁 Structure du projet

```
AICapitain_MITChallenge/
├── backend/                          # ← VOUS ÊTES ICI
│   ├── data_engineering/
│   │   └── ais_processor.py          # Ingestion + Graphe
│   ├── optimization_engine/
│   │   └── optimizer.py              # A* pondéré
│   ├── agents/
│   │   ├── monitoring_agent.py       # Monitoring + Re-routing
│   │   └── forecasting_agent.py      # Prédiction
│   ├── api/
│   │   └── main.py                   # FastAPI REST
│   ├── models/
│   │   └── data_models.py            # Pydantic models
│   ├── config/
│   │   └── settings.py               # Configuration
│   ├── tests/
│   │   └── test_ai_captain.py        # Tests unitaires
│   ├── api.py                        # Launcher
│   ├── run.bat / run.sh              # Scripts d'exécution
│   ├── requirements.txt              # Dépendances
│   ├── README.md
│   ├── TECHNICAL_DOC.md              # Doc technique détaillée
│   └── .env.example
│
├── demo_aicaptain.ipynb              # ← Démonstration interactive
└── frontend/                         # (À faire: Frontend optional)
```

---

## 🔧 Configuration (.env)

Les paramètres par défaut fonctionnent bien. Pour personnaliser:

```bash
# Copier
cp backend/.env.example backend/.env

# Éditer backend/.env:
DEBUG=false
API_PORT=8000

# Poids d'optimisation par défaut
DEFAULT_WEIGHT_TIME=1.0      # Priorité temps
DEFAULT_WEIGHT_COST=1.0      # Priorité coût
DEFAULT_WEIGHT_RISK=1.0      # Priorité sécurité

# Monitoring
REROUTING_THRESHOLD_DEVIATION_KM=50.0

# Logging
LOG_LEVEL=INFO
```

---

## 📡 Principaux Endpoints API

| Méthode  | Endpoint                      | Description              |
| -------- | ----------------------------- | ------------------------ |
| **GET**  | `/health`                     | Health check             |
| **GET**  | `/api/v1/system/status`       | Status du système        |
| **POST** | `/api/v1/route/optimize`      | Optimiser une route      |
| **GET**  | `/api/v1/route/alternatives`  | Routes alternatives      |
| **POST** | `/api/v1/voyage/register`     | Enregistrer voyage       |
| **PUT**  | `/api/v1/vessel/position`     | Mettre à jour position   |
| **POST** | `/api/v1/forecast/congestion` | Prédire congestion       |
| **GET**  | `/api/v1/forecast/best-port`  | Meilleur port alternatif |

Documentation complète: [TECHNICAL_DOC.md](./TECHNICAL_DOC.md)

---

## 🎯 Cas d'usage typiques

### 1️⃣ Optimiser une route simple

```bash
curl -X POST http://localhost:8000/api/v1/route/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "vessel": {...},
    "start_port_id": "PORT_SG",
    "end_port_id": "PORT_HH",
    "weight_time": 1.0,
    "weight_cost": 1.0,
    "weight_risk": 1.0
  }'
```

### 2️⃣ Obtenir routes alternatives

```bash
curl http://localhost:8000/api/v1/route/alternatives\?start=PORT_SG\&end=PORT_HH\&num_alternatives=3
```

### 3️⃣ Prédire congestion à l'arrivée

```bash
curl -X POST http://localhost:8000/api/v1/forecast/congestion \
  -H "Content-Type: application/json" \
  -d '{
    "port_id": "PORT_HH",
    "arrival_date": "2025-11-15T14:00:00",
    "vessel_type": "container_ship"
  }'
```

### 4️⃣ Monitorer un navire actif

```bash
# Enregistrer voyage
curl -X POST http://localhost:8000/api/v1/voyage/register ...

# Mettre à jour position
curl -X PUT http://localhost:8000/api/v1/vessel/position \
  -H "Content-Type: application/json" \
  -d '{
    "mmsi": "257465900",
    "latitude": 1.35,
    "longitude": 103.82,
    "timestamp": "2025-11-08T10:30:00"
  }'

# Détection automatique de déviation + re-routing
```

---

## ⚙️ Troubleshooting

### Port 8000 déjà utilisé

```bash
# Utiliser un port différent
python -m uvicorn api.main:app --port 8001
```

### Erreur d'import

```bash
# Vérifier que le backend est dans le path Python
python -c "import sys; print(sys.path)"

# Ajouter au PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/backend
```

### Données AIS non trouvées

```bash
# Placer ais_data.json dans:
c:\Users\dell\Downloads\ais_data.json

# Ou modifier le chemin dans config/settings.py:
AIS_DATA_PATH = "votre/chemin/ais_data.json"
```

### Dépendances manquantes

```bash
pip install -r backend/requirements.txt --force-reinstall
```

---

## 📚 Documentation & Ressources

- **[TECHNICAL_DOC.md](./TECHNICAL_DOC.md)** - Documentation technique complète (algos, formules, APIs)
- **[README.md](./README.md)** - Guide d'installation détaillé
- **[demo_aicaptain.ipynb](../demo_aicaptain.ipynb)** - Démonstration interactive
- **API Swagger**: http://localhost:8000/api/v1/docs

---

## 🚀 Prochaines étapes après démarrage

1. ✅ Explorer les endpoints dans Swagger UI
2. ✅ Exécuter le notebook de démonstration
3. ✅ Tester l'API avec des requêtes personnalisées
4. ✅ Intégrer avec votre base de données (PostgreSQL, BigQuery)
5. ✅ Ajouter les APIs météo (WeatherAPI, NOAA)
6. ✅ Déployer avec Docker
7. ✅ Connecter à un système de monitoring (Prometheus, Grafana)

---

## 💡 Tips & Astuces

- **Développement rapide**: Utiliser `--reload` pour auto-reload
- **Déboguer**: Mettre `DEBUG=true` dans `.env`
- **Performance**: En production, utiliser plusieurs workers: `--workers 4`
- **Tests continus**: `pytest --watch backend/tests/`
- **API testing**: Exporter la collection Swagger pour Postman

---

## 📞 Support

- Erreur ? Vérifier les logs dans la console
- Question ? Consulter [TECHNICAL_DOC.md](./TECHNICAL_DOC.md)
- Rapport de bug ? Créer une issue sur GitHub

---

**Bon voyage ! 🚢⚓**

v0.1.0 | Nov 8, 2025
