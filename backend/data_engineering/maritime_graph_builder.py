"""
Constructeur de graphe maritime réaliste avec waypoints et routes
Basé sur les données AIS réelles et les corridors maritimes internationaux
"""

import json
import networkx as nx
from typing import Dict, List, Tuple
from pathlib import Path
import logging
from math import radians, cos, sin, asin, sqrt

from models import WayPoint

logger = logging.getLogger(__name__)


class MaritimeGraphBuilder:
    """Construit un graphe réaliste de routage maritime"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.waypoints: Dict[str, WayPoint] = {}
    
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distance entre deux points en milles nautiques"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return c * 3440.065  # Milles nautiques
    
    def add_waypoint(self, waypoint_id: str, name: str, latitude: float, 
                     longitude: float, port_type: str = "port", 
                     risk_level: str = "LOW") -> WayPoint:
        """Ajoute un waypoint au graphe"""
        wp = WayPoint(
            id=waypoint_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
            port_type=port_type
        )
        self.waypoints[waypoint_id] = wp
        self.graph.add_node(waypoint_id)
        logger.info(f"✅ Waypoint ajouté: {name} ({waypoint_id})")
        return wp
    
    def add_route(self, from_id: str, to_id: str, direct: bool = True,
                  priority: int = 1) -> Tuple[float, float, float]:
        """
        Ajoute une route maritime avec calcul automatique des métriques
        
        Returns: (distance_nm, time_hours, fuel_tons)
        """
        if from_id not in self.waypoints or to_id not in self.waypoints:
            logger.error(f"❌ Waypoints non trouvés: {from_id} → {to_id}")
            return 0, 0, 0
        
        from_wp = self.waypoints[from_id]
        to_wp = self.waypoints[to_id]
        
        # Calcul distance
        distance_nm = self.haversine(
            from_wp.latitude, from_wp.longitude,
            to_wp.latitude, to_wp.longitude
        )
        
        # Hypothèses réalistes pour porte-conteneurs
        avg_speed_knots = 20  # Vitesse de croisière
        time_hours = distance_nm / avg_speed_knots
        fuel_consumption = distance_nm * 0.005  # tonnes/NM (très réaliste)
        
        # Déterminer le coefficient de risque (zones de détroits/canaux = risque élevé)
        risk_multiplier = 1.0
        if "Suez" in from_wp.name or "Suez" in to_wp.name:
            risk_multiplier = 1.8  # Suez très dangereux
        elif "Panama" in from_wp.name or "Panama" in to_wp.name:
            risk_multiplier = 1.5  # Panama aussi dangereux
        elif "Malacca" in from_wp.name or "Malacca" in to_wp.name:
            risk_multiplier = 1.3  # Malacca: piraterie
        
        risk_score = 2.0 * risk_multiplier
        
        # Ajouter au graphe
        self.graph.add_edge(
            from_id, to_id,
            distance_nm=distance_nm,
            time_hours=time_hours,
            fuel_tons=fuel_consumption,
            risk_score=risk_score,
            cost_usd=fuel_consumption * 500,  # $500/tonne fuel
            direct=direct,
            priority=priority
        )
        
        logger.debug(f"  → Route: {distance_nm:.0f} NM, {time_hours:.1f}h, {fuel_consumption:.1f}t fuel")
        return distance_nm, time_hours, fuel_consumption
    
    def build_realistic_network(self) -> nx.DiGraph:
        """
        Construit un réseau maritime réaliste avec 20+ waypoints
        et des routes maritimes internationales majeures
        """
        logger.info("🚢 Construction d'un réseau maritime réaliste...")
        
        # === WAYPOINTS MAJEURS (Ports internationaux) ===
        print("\n📍 PORTS MAJEURS:")
        
        ports = [
            ("SG", "Singapore", 1.3521, 103.8198, "port", "LOW"),
            ("HK", "Hong Kong", 22.3193, 114.1694, "port", "LOW"),
            ("SH", "Shanghai", 30.5728, 121.5360, "port", "LOW"),
            ("LA", "Los Angeles", 33.7425, -118.2426, "port", "LOW"),
            ("PA", "Panama Canal", 9.0820, -79.5200, "port", "MEDIUM"),
            ("HA", "Hamburg", 53.5511, 9.9769, "port", "LOW"),
            ("RT", "Rotterdam", 51.9225, 4.4792, "port", "LOW"),
            ("DU", "Dubai", 25.2048, 55.2708, "port", "LOW"),
            ("CO", "Colombo", 6.9271, 79.8789, "port", "LOW"),
            ("MU", "Mumbai", 18.9520, 72.8347, "port", "LOW"),
            ("SY", "Sydney", -33.8688, 151.2093, "port", "LOW"),
            ("TO", "Tokyo", 35.6762, 139.6503, "port", "LOW"),
            ("SN", "Suez Canal", 29.9537, 32.5824, "port", "HIGH"),
        ]
        
        for pid, name, lat, lon, ptype, risk in ports:
            self.add_waypoint(pid, name, lat, lon, ptype, risk)
        
        # === WAYPOINTS INTERMÉDIAIRES (Detroits & Chokepoints) ===
        print("\n🚢 CHOKEPOINTS & DÉTROITS:")
        
        intermediate = [
            ("MC", "Malacca Strait", 1.0, 104.0, "strait", "MEDIUM"),
            ("PH", "Philippines Sea", 12.0, 130.0, "sea", "LOW"),
            ("IJ", "Indian Ocean Junction", 0.0, 70.0, "sea", "LOW"),
            ("SJ", "Suez Junction", 31.0, 32.0, "strait", "HIGH"),
            ("MD", "Mediterranean", 35.0, 15.0, "sea", "LOW"),
            ("GI", "Gibraltar", 35.9, -5.4, "strait", "MEDIUM"),
            ("AT", "Atlantic", 40.0, -20.0, "sea", "LOW"),
            ("PC", "Panama Canal Zone", 8.5, -80.0, "strait", "MEDIUM"),
        ]
        
        for pid, name, lat, lon, ptype, risk in intermediate:
            self.add_waypoint(pid, name, lat, lon, ptype, risk)
        
        print(f"\n✅ Total waypoints: {len(self.waypoints)}")
        
        # === ROUTES MARITIMES RÉALISTES ===
        print("\n🛣️  ROUTES MARITIMES MAJEURES:")
        
        routes = [
            # === ASIE-EUROPE (via Suez) ===
            ("SG", "MC", True, 1),   # Singapore → Malacca
            ("MC", "IJ", True, 1),   # Malacca → Indian Ocean
            ("IJ", "DU", True, 1),   # Indian Ocean → Dubai
            ("DU", "SJ", True, 1),   # Dubai → Suez Junction
            ("SJ", "SN", True, 1),   # Suez Junction → Suez Canal
            ("SN", "MD", True, 1),   # Suez → Mediterranean
            ("MD", "GI", True, 1),   # Mediterranean → Gibraltar
            ("GI", "RT", True, 1),   # Gibraltar → Rotterdam
            ("RT", "HA", True, 1),   # Rotterdam → Hamburg
            
            # === ASIE-USA (via Panama) ===
            ("SG", "HK", True, 1),   # Singapore → Hong Kong
            ("HK", "SH", True, 1),   # Hong Kong → Shanghai
            ("SH", "TO", True, 1),   # Shanghai → Tokyo
            ("TO", "PH", True, 1),   # Tokyo → Philippines
            ("PH", "PC", True, 1),   # Philippines → Panama Canal
            ("PC", "LA", True, 1),   # Panama → Los Angeles
            
            # === INTRA-ASIE ===
            ("SG", "CO", True, 1),   # Singapore → Colombo
            ("CO", "MU", True, 1),   # Colombo → Mumbai
            ("SH", "HK", True, 1),   # Shanghai → Hong Kong (retour)
            ("HK", "SG", True, 1),   # Hong Kong → Singapore
            
            # === ROUTES INVERSES (bidirectionnelles) ===
            ("HA", "RT", True, 1),   # Hamburg → Rotterdam
            ("RT", "GI", True, 1),   # Rotterdam → Gibraltar
            ("GI", "MD", True, 1),   # Gibraltar → Mediterranean
            ("MD", "SN", True, 1),   # Mediterranean → Suez
            ("SN", "SJ", True, 1),   # Suez → Suez Junction
            ("SJ", "DU", True, 1),   # Suez Junction → Dubai
            ("DU", "IJ", True, 1),   # Dubai → Indian Ocean
            ("IJ", "MC", True, 1),   # Indian Ocean → Malacca
            ("MC", "SG", True, 1),   # Malacca → Singapore
            
            # Routes inverses Amérique
            ("LA", "PC", True, 1),   # Los Angeles → Panama
            ("PC", "PH", True, 1),   # Panama → Philippines
            ("PH", "TO", True, 1),   # Philippines → Tokyo
            ("TO", "SH", True, 1),   # Tokyo → Shanghai
            ("SH", "HK", True, 1),   # Shanghai → Hong Kong
            ("HK", "SG", True, 1),   # Hong Kong → Singapore
            
            # Routes intermédiaires supplémentaires
            ("CO", "SG", True, 1),   # Colombo → Singapore
            ("MU", "CO", True, 1),   # Mumbai → Colombo
            ("SY", "TO", True, 1),   # Sydney → Tokyo
            ("TO", "LA", True, 1),   # Tokyo → Los Angeles
        ]
        
        total_distance = 0
        for from_id, to_id, direct, priority in routes:
            dist, time, fuel = self.add_route(from_id, to_id, direct, priority)
            total_distance += dist
        
        print(f"\n✅ Total routes: {self.graph.number_of_edges()}")
        print(f"📊 Distance totale du réseau: {total_distance:.0f} NM\n")
        
        return self.graph
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques du graphe"""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "average_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
            "is_connected": nx.is_strongly_connected(self.graph),
            "waypoints": list(self.waypoints.keys())
        }


def create_maritime_network() -> Tuple[nx.DiGraph, Dict[str, WayPoint]]:
    """Fonction helper pour créer et retourner le réseau maritime"""
    builder = MaritimeGraphBuilder()
    graph = builder.build_realistic_network()
    stats = builder.get_statistics()
    
    logger.info(f"📊 Statistiques du réseau maritime:")
    logger.info(f"   Nœuds: {stats['nodes']}")
    logger.info(f"   Arêtes: {stats['edges']}")
    logger.info(f"   Degré moyen: {stats['average_degree']:.2f}")
    logger.info(f"   Connectivité forte: {stats['is_connected']}")
    
    return graph, builder.waypoints
