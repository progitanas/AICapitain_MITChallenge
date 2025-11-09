"""
API REST pour AI Captain
Endpoints pour requêtes d'optimisation, monitoring, et prédictions
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from models import (
    VesselSpec,
    VesselDimensions,
    WayPoint,
    OptimizationParams,
    NavigationStatus,
    serialize_route,
)
from data_engineering.ais_processor import AISDataProcessor, GeospatialGraphBuilder
from data_engineering.maritime_graph_builder import create_maritime_network
from optimization_engine.optimizer import WeightedAStarOptimizer
from agents.monitoring_agent import DeviationMonitoringAgent, CongestionBlockageDetector
from agents.forecasting_agent import CongestionForecastingAgent

logger = logging.getLogger(__name__)

# Initialisation FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, use ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Composants globaux
optimizer: Optional[WeightedAStarOptimizer] = None
waypoints_dict: Optional[Dict[str, WayPoint]] = None
monitoring_agent: Optional[DeviationMonitoringAgent] = None
forecasting_agent: Optional[CongestionForecastingAgent] = None
blockage_detector: Optional[CongestionBlockageDetector] = None


# ==================== REQUEST/RESPONSE MODELS ====================

class VesselDimensionsRequest(BaseModel):
    length_m: float
    beam_m: float
    draught_m: float
    depth_m: float


class VesselSpecRequest(BaseModel):
    mmsi: str
    imo: str
    name: str
    call_sign: str
    dimensions: VesselDimensionsRequest
    type_code: int
    latitude: float
    longitude: float
    sog_knots: float
    cog_degrees: float
    heading_degrees: float
    nav_status: int
    destination_port: Optional[str] = None


class OptimizationRequest(BaseModel):
    """Requête d'optimisation de route"""
    vessel: VesselSpecRequest
    start_port_id: str
    end_port_id: str
    weight_time: float = 1.0
    weight_cost: float = 1.0
    weight_risk: float = 1.0
    fuel_price_per_ton: float = 500.0
    avoid_piracy_zones: bool = True
    avoid_weather_risks: bool = True


class PortCongestionForecastRequest(BaseModel):
    """Requête de prédiction de congestion"""
    port_id: str
    arrival_date: datetime
    vessel_type: Optional[str] = None


class VesselPositionUpdate(BaseModel):
    """Mise à jour de position d'un navire"""
    mmsi: str
    latitude: float
    longitude: float
    timestamp: datetime


# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialise les composants au démarrage"""
    global optimizer, waypoints_dict, monitoring_agent, forecasting_agent, blockage_detector
    
    logger.info(f"🚀 Démarrage de {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Créer le réseau maritime réaliste avec tous les waypoints et routes
        logger.info("🌍 Construction du réseau maritime réaliste...")
        graph, wp_dict = create_maritime_network()
        waypoints_dict = wp_dict
        
        logger.info(f"✅ Réseau créé: {graph.number_of_nodes()} nœuds, {graph.number_of_edges()} arêtes")
        
        # Initialiser l'optimiseur avec le graphe réaliste
        optimizer = WeightedAStarOptimizer(graph, waypoints_dict)
        logger.info("✅ Optimiseur A* pondéré initialisé")
        
        # Initialiser les agents
        monitoring_agent = DeviationMonitoringAgent(optimizer, max_deviation_km=50.0)
        forecasting_agent = CongestionForecastingAgent()
        blockage_detector = CongestionBlockageDetector()
        logger.info("✅ Agents initialisés")
        
        logger.info("✅ Tous les composants démarrés avec succès!\n")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Arrête les composants"""
    if monitoring_agent:
        monitoring_agent.stop_monitoring()
    logger.info("Arrêt de l'application")


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Vérification de l'état du système"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
    }


@app.get(f"{settings.API_PREFIX}/waypoints")
async def get_waypoints():
    """Retourne la liste des waypoints/ports disponibles"""
    if not waypoints_dict:
        raise HTTPException(status_code=503, detail="Waypoints not initialized")
    
    waypoints = [
        {
            "id": wp.id,
            "name": wp.name,
            "latitude": wp.latitude,
            "longitude": wp.longitude,
            "port_type": wp.port_type,
        }
        for wp in waypoints_dict.values()
    ]
    
    return {"waypoints": waypoints}


# ==================== ROUTE OPTIMIZATION ENDPOINTS ====================

@app.post(f"{settings.API_PREFIX}/route/optimize")
async def optimize_route(request: OptimizationRequest):
    """
    Principale endpoint: demande d'optimisation de route
    Input: Navire, ports de départ/arrivée, paramètres d'optimisation
    Output: Route optimisée
    """
    if not optimizer or not waypoints_dict:
        raise HTTPException(status_code=503, detail="Optimizer not initialized")
    
    try:
        logger.info(f"Route optimization request: {request.start_port_id} -> {request.end_port_id}")
        
        # Créer les paramètres
        params = OptimizationParams(
            weight_time=request.weight_time,
            weight_cost=request.weight_cost,
            weight_risk=request.weight_risk,
            fuel_price_per_ton=request.fuel_price_per_ton,
        )
        
        # Trouver le chemin optimal
        path = optimizer.find_optimal_route(
            request.start_port_id,
            request.end_port_id,
            params,
        )
        
        if not path:
            raise HTTPException(status_code=404, detail="No route found")
        
        # Construire l'objet route
        route = optimizer.construct_optimized_route(path, params)
        
        # Vérifier les blocages de canaux
        blockages = blockage_detector.check_chokepoint_blockage(route)
        
        # Convertir en JSON
        route_data = {
            "waypoints": [
                {"id": wp.id, "name": wp.name, "lat": wp.latitude, "lon": wp.longitude}
                for wp in route.waypoints
            ],
            "metrics": {
                "distance_nm": route.total_distance_nm,
                "time_hours": route.estimated_time_hours,
                "fuel_tons": route.estimated_fuel_tons,
                "cost_usd": route.estimated_cost_usd,
                "risk_score": route.overall_risk_score,
            },
            "blockages": blockages,
            "generated_at": route.generated_at.isoformat(),
        }
        
        return JSONResponse(content=route_data)
    
    except Exception as e:
        logger.error(f"Error in optimize_route: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{settings.API_PREFIX}/route/alternatives")
async def get_alternative_routes(start: str, end: str, num_alternatives: int = 3):
    """Retourne plusieurs routes alternatives"""
    if not optimizer:
        raise HTTPException(status_code=503, detail="Optimizer not initialized")
    
    try:
        alternatives = []
        
        # Générer plusieurs routes avec des pondérations différentes
        weight_configs = [
            {"time": 1.0, "cost": 1.0, "risk": 1.0},  # Équilibré
            {"time": 2.0, "cost": 1.0, "risk": 1.0},  # Priorité temps
            {"time": 1.0, "cost": 1.0, "risk": 2.0},  # Priorité sécurité
        ]
        
        for i, weights in enumerate(weight_configs[:num_alternatives]):
            params = OptimizationParams(
                weight_time=weights["time"],
                weight_cost=weights["cost"],
                weight_risk=weights["risk"],
            )
            
            path = optimizer.find_optimal_route(start, end, params)
            if path:
                route = optimizer.construct_optimized_route(path, params)
                alternatives.append({
                    "id": i,
                    "strategy": list(weights.keys())[i],
                    "metrics": {
                        "distance": route.total_distance_nm,
                        "time": route.estimated_time_hours,
                        "cost": route.estimated_cost_usd,
                        "risk": route.overall_risk_score,
                    }
                })
        
        return {"alternatives": alternatives}
    
    except Exception as e:
        logger.error(f"Error in get_alternative_routes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MONITORING ENDPOINTS ====================

@app.post(f"{settings.API_PREFIX}/voyage/register")
async def register_voyage(vessel_request: VesselSpecRequest, start_port: str, end_port: str):
    """Enregistre un nouveau voyage pour monitoring"""
    if not optimizer or not monitoring_agent:
        raise HTTPException(status_code=503, detail="Monitoring not initialized")
    
    try:
        # Créer la route optimale
        params = OptimizationParams()
        path = optimizer.find_optimal_route(start_port, end_port, params)
        
        if not path:
            raise HTTPException(status_code=404, detail="No route found")
        
        route = optimizer.construct_optimized_route(path, params)
        
        # Construire le VesselSpec
        vessel_dims = VesselDimensions(
            length_m=vessel_request.dimensions.length_m,
            beam_m=vessel_request.dimensions.beam_m,
            draught_m=vessel_request.dimensions.draught_m,
            depth_m=vessel_request.dimensions.depth_m,
        )
        
        vessel = VesselSpec(
            mmsi=vessel_request.mmsi,
            imo=vessel_request.imo,
            name=vessel_request.name,
            call_sign=vessel_request.call_sign,
            dimensions=vessel_dims,
            type_code=vessel_request.type_code,
            current_position=(vessel_request.latitude, vessel_request.longitude),
            sog_knots=vessel_request.sog_knots,
            cog_degrees=vessel_request.cog_degrees,
            heading_degrees=vessel_request.heading_degrees,
            nav_status=NavigationStatus(vessel_request.nav_status),
        )
        
        # Enregistrer le voyage
        monitoring_agent.register_voyage(vessel, route)
        
        return {
            "message": "Voyage registered",
            "mmsi": vessel_request.mmsi,
            "route_waypoints": len(route.waypoints),
        }
    
    except Exception as e:
        logger.error(f"Error in register_voyage: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put(f"{settings.API_PREFIX}/vessel/position")
async def update_vessel_position(update: VesselPositionUpdate):
    """Met à jour la position d'un navire en navigation"""
    if not monitoring_agent:
        raise HTTPException(status_code=503, detail="Monitoring not initialized")
    
    try:
        monitoring_agent.update_vessel_position(
            update.mmsi,
            update.latitude,
            update.longitude,
            update.timestamp
        )
        
        # Vérifier déviation
        deviation_event = monitoring_agent.detect_deviation(update.mmsi)
        
        return {
            "status": "position_updated",
            "mmsi": update.mmsi,
            "deviation_detected": deviation_event is not None,
            "rerouting_required": deviation_event is not None,
        }
    
    except Exception as e:
        logger.error(f"Error in update_vessel_position: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FORECASTING ENDPOINTS ====================

@app.post(f"{settings.API_PREFIX}/forecast/congestion")
async def forecast_port_congestion(request: PortCongestionForecastRequest):
    """Prédit la congestion à un port"""
    if not forecasting_agent:
        raise HTTPException(status_code=503, detail="Forecasting agent not initialized")
    
    try:
        forecast = forecasting_agent.forecast_port_congestion(
            request.port_id,
            request.arrival_date,
            request.vessel_type
        )
        
        return {
            "port_id": forecast.port_id,
            "predicted_queue_length": forecast.predicted_queue_length,
            "predicted_wait_hours": forecast.predicted_wait_hours,
            "confidence_score": forecast.confidence_score,
            "factors": forecast.factors,
        }
    
    except Exception as e:
        logger.error(f"Error in forecast_port_congestion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(f"{settings.API_PREFIX}/forecast/best-port")
async def select_best_port(primary_port: str, alternatives: List[str], arrival_date: datetime):
    """Sélectionne le meilleur port alternatif"""
    if not forecasting_agent:
        raise HTTPException(status_code=503, detail="Forecasting agent not initialized")
    
    try:
        best_port = forecasting_agent.select_best_alternate_port(
            primary_port,
            alternatives,
            arrival_date
        )
        
        return {
            "best_port": best_port,
            "reason": "Lowest predicted congestion",
        }
    
    except Exception as e:
        logger.error(f"Error in select_best_port: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATISTICS ENDPOINTS ====================

@app.get(f"{settings.API_PREFIX}/system/status")
async def system_status():
    """Status du système"""
    graph_stats = {
        "nodes": len(waypoints_dict) if waypoints_dict else 0,
        "waypoints": list(waypoints_dict.keys()) if waypoints_dict else []
    }
    
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "graph": graph_stats,
        "active_voyages": len(monitoring_agent.active_voyages) if monitoring_agent else 0,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
