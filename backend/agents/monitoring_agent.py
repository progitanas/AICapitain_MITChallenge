"""
Agent de Détection de Déviation (Monitoring Agent)
Surveille les trajets actifs et déclenche les re-routages
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from models import (
    VesselSpec,
    OptimizedRoute,
    ReroutingEvent,
)

logger = logging.getLogger(__name__)


@dataclass
class ActiveVoyage:
    """Représente un voyage actif en cours"""
    vessel: VesselSpec
    planned_route: OptimizedRoute
    actual_positions: List[tuple] = field(default_factory=list)  # [(lat, lon, timestamp)]
    last_check_time: datetime = field(default_factory=datetime.now)
    rerouting_history: List[ReroutingEvent] = field(default_factory=list)
    deviation_from_plan_km: float = 0.0


class DeviationMonitoringAgent:
    """
    Surveille les déviances de trajectoire
    Déclenche les re-routages automatiques
    """
    
    def __init__(self, optimizer, max_deviation_km: float = 50.0):
        self.optimizer = optimizer
        self.max_deviation_km = max_deviation_km
        self.active_voyages: Dict[str, ActiveVoyage] = {}
        self.is_running = False
        
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distance en km"""
        from math import radians, cos, sin, asin, sqrt
        lon1, lon2 = map(radians, [lon1, lon2])
        lat1, lat2 = map(radians, [lat1, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = c * 6371
        return km
    
    def register_voyage(self, vessel: VesselSpec, route: OptimizedRoute):
        """Enregistre un nouveau voyage actif"""
        voyage = ActiveVoyage(vessel=vessel, planned_route=route)
        self.active_voyages[vessel.mmsi] = voyage
        logger.info(f"Voyage enregistré: {vessel.name} ({vessel.mmsi})")
    
    def update_vessel_position(self, mmsi: str, latitude: float, longitude: float,
                              timestamp: datetime):
        """Met à jour la position actuelle d'un navire"""
        if mmsi not in self.active_voyages:
            logger.warning(f"Navire {mmsi} non trouvé dans les voyages actifs")
            return
        
        voyage = self.active_voyages[mmsi]
        voyage.actual_positions.append((latitude, longitude, timestamp))
    
    def _get_closest_waypoint_on_planned_route(self, vessel_lat: float, 
                                               vessel_lon: float,
                                               voyage: ActiveVoyage) -> Optional[int]:
        """Trouve le waypoint le plus proche sur la route prévue"""
        min_distance = float('inf')
        closest_index = None
        
        for i, wp in enumerate(voyage.planned_route.waypoints):
            distance = self.haversine_distance(vessel_lat, vessel_lon, 
                                             wp.latitude, wp.longitude)
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        return closest_index
    
    def detect_deviation(self, mmsi: str) -> Optional[ReroutingEvent]:
        """
        Détecte une déviation significative du plan
        Retourne l'événement de re-routage si nécessaire
        """
        voyage = self.active_voyages[mmsi]
        
        if not voyage.actual_positions:
            return None
        
        current_lat, current_lon, _ = voyage.actual_positions[-1]
        
        # Trouver le point le plus proche sur la route prévue
        closest_wp_idx = self._get_closest_waypoint_on_planned_route(
            current_lat, current_lon, voyage
        )
        
        if closest_wp_idx is None:
            return None
        
        waypoint = voyage.planned_route.waypoints[closest_wp_idx]
        distance_to_plan_km = self.haversine_distance(
            current_lat, current_lon,
            waypoint.latitude, waypoint.longitude
        )
        
        voyage.deviation_from_plan_km = distance_to_plan_km
        
        # Seuil de déviation atteint
        if distance_to_plan_km > self.max_deviation_km:
            logger.warning(
                f"Déviation détectée pour {voyage.vessel.name}: "
                f"{distance_to_plan_km:.1f} km > {self.max_deviation_km} km"
            )
            
            event = ReroutingEvent(
                vessel_mmsi=mmsi,
                trigger_type="deviation",
                trigger_location=(current_lat, current_lon),
                old_route=voyage.planned_route,
                deviation_km=distance_to_plan_km,
            )
            
            return event
        
        return None
    
    def detect_storm_impact(self, mmsi: str, storm_warning: Dict) -> Optional[ReroutingEvent]:
        """
        Détecte l'impact d'une tempête sur la route
        storm_warning: {location: (lat, lon), radius_km: float, severity: str}
        """
        voyage = self.active_voyages[mmsi]
        
        storm_lat, storm_lon = storm_warning.get('location')
        storm_radius = storm_warning.get('radius_km', 100)
        
        # Vérifier si la tempête coupe la route planifiée
        for segment in voyage.planned_route.segments:
            wp_to = segment.to_waypoint
            distance_to_storm = self.haversine_distance(
                wp_to.latitude, wp_to.longitude,
                storm_lat, storm_lon
            )
            
            if distance_to_storm < storm_radius:
                logger.warning(
                    f"Tempête affectant le passage de {voyage.vessel.name} "
                    f"à {wp_to.name} (distance: {distance_to_storm:.1f} km)"
                )
                
                event = ReroutingEvent(
                    vessel_mmsi=mmsi,
                    trigger_type="storm",
                    trigger_location=voyage.actual_positions[-1][:2],
                    old_route=voyage.planned_route,
                )
                
                return event
        
        return None
    
    async def monitor_active_voyages(self, check_interval_seconds: float = 60):
        """
        Boucle de surveillance des voyages actifs
        À exécuter en continu
        """
        logger.info("Démarrage de la surveillance des voyages actifs")
        self.is_running = True
        
        try:
            while self.is_running:
                for mmsi, voyage in list(self.active_voyages.items()):
                    # Détection de déviation
                    deviation_event = self.detect_deviation(mmsi)
                    
                    if deviation_event:
                        logger.info(f"Événement de déviation détecté: {mmsi}")
                        voyage.rerouting_history.append(deviation_event)
                        # Déclencher re-routage (émit un événement/message)
                
                await asyncio.sleep(check_interval_seconds)
        
        except asyncio.CancelledError:
            logger.info("Surveillance des voyages arrêtée")
            self.is_running = False
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.is_running = False


class CongestionBlockageDetector:
    """Détecte les blocages de canaux et passages étroits"""
    
    def __init__(self):
        # Définition des chokepoints critiques
        self.chokepoints = {
            'suez': {
                'center': (29.95, 32.58),
                'radius_km': 50,
                'typical_delay_hours': 12,
                'blocked_reason': 'Incidents au Canal de Suez',
            },
            'panama': {
                'center': (9.27, -79.52),
                'radius_km': 50,
                'typical_delay_hours': 8,
                'blocked_reason': 'Incidents au Canal de Panama',
            },
            'strait_of_malacca': {
                'center': (2.5, 101.5),
                'radius_km': 100,
                'typical_delay_hours': 6,
                'blocked_reason': 'Incidents au Détroit de Malacca',
            },
        }
    
    def check_chokepoint_blockage(self, route: OptimizedRoute) -> List[Dict]:
        """Vérifie si la route traverse des chokepoints bloqués"""
        blockages = []
        
        for segment in route.segments:
            wp = segment.to_waypoint
            
            for choke_name, choke_info in self.chokepoints.items():
                choke_lat, choke_lon = choke_info['center']
                
                from optimization_engine.optimizer import WeightedAStarOptimizer
                distance_km = WeightedAStarOptimizer.haversine_distance(
                    wp.latitude, wp.longitude,
                    choke_lat, choke_lon
                ) * 1.852  # Convert NM to km
                
                if distance_km < choke_info['radius_km']:
                    blockages.append({
                        'chokepoint': choke_name,
                        'reason': choke_info['blocked_reason'],
                        'estimated_delay_hours': choke_info['typical_delay_hours'],
                    })
        
        return blockages
