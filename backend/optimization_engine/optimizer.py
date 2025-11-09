import heapq
import math
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
import networkx as nx
from dataclasses import dataclass
import logging

from models import (
    WayPoint,
    EdgeAttributes,
    OptimizationParams,
    OptimizedRoute,
    RouteSegment,
    RiskLevel,
)

logger = logging.getLogger(__name__)


@dataclass
class PathNode:
    """Nœud pour l'algorithme de recherche"""
    node_id: str
    g_cost: float  # Coût réel depuis le début
    h_cost: float  # Coût estimé vers la fin (heuristique)
    timestamp: datetime  # Heure d'arrivée estimée au nœud
    
    @property
    def f_cost(self) -> float:
        """Coût total (g + h)"""
        return self.g_cost + self.h_cost
    
    def __lt__(self, other):
        """Comparaison pour la file de priorité"""
        return self.f_cost < other.f_cost


class WeightedAStarOptimizer:
    """
    Optimisation A* pondérée pour le routage maritime
    Minimise: W_time * time + W_cost * cost + W_risk * risk
    """
    
    def __init__(self, graph: nx.DiGraph, waypoints: Dict[str, WayPoint]):
        self.graph = graph
        self.waypoints = waypoints
        
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distance en nautical miles"""
        from math import radians, cos, sin, asin, sqrt
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return c * 3440.065
    
    def heuristic_cost(self, from_node_id: str, to_node_id: str, 
                      params: OptimizationParams) -> float:
        """
        Heuristique: distance restante * vitesse moyenne
        Pondérée par les poids d'optimisation
        """
        from_wp = self.waypoints[from_node_id]
        to_wp = self.waypoints[to_node_id]
        
        distance_nm = self.haversine_distance(
            from_wp.latitude, from_wp.longitude,
            to_wp.latitude, to_wp.longitude
        )
        
        # Vitesse moyenne supposée: 15 knots (navires cargo)
        time_hours = distance_nm / 15
        cost_usd = distance_nm * 20  # Estimation: $20 par NM
        
        # Score de risque estimé (0-10)
        risk_score = 2.0
        
        return (
            params.weight_time * time_hours +
            params.weight_cost * cost_usd +
            params.weight_risk * risk_score
        )
    
    def compute_edge_cost(self, from_node_id: str, to_node_id: str,
                         params: OptimizationParams,
                         current_time: datetime) -> Tuple[float, EdgeAttributes]:
        """
        Calcule le coût d'une arête avec conditions dynamiques
        Intègre météo, carburant, congestion
        """
        edge_data = self.graph.get_edge_data(from_node_id, to_node_id)
        
        if not edge_data:
            return float('inf'), None
        
        # Coûts de base
        time_hours = edge_data.get('time_hours', 0)
        fuel_tons = edge_data.get('fuel_tons', 0)
        distance_nm = edge_data.get('weight', 0)
        
        # Coût du carburant
        fuel_cost = fuel_tons * params.fuel_price_per_ton
        
        # Risques
        weather_risk_value = edge_data.get('weather_risk', 0)
        piracy_risk_value = edge_data.get('piracy_risk', 0)
        risk_score = (weather_risk_value + piracy_risk_value) / 2.0
        
        # Score de pénalité pour risque (augmente le temps estimé)
        risk_penalty_hours = risk_score * 2.0
        
        # Coût final pondéré
        total_cost = (
            params.weight_time * (time_hours + risk_penalty_hours) +
            params.weight_cost * fuel_cost +
            params.weight_risk * risk_score
        )
        
        return total_cost, edge_data
    
    def find_optimal_route(self, start_node_id: str, end_node_id: str,
                          params: OptimizationParams,
                          max_iterations: int = 10000) -> Optional[List[str]]:
        """
        Trouve la route optimale en utilisant A* pondéré
        Retourne la liste des node_ids
        """
        logger.info(f"Recherche route optimale: {start_node_id} -> {end_node_id}")
        
        current_time = datetime.now()
        
        # Initialisation
        open_set = []
        closed_set: Set[str] = set()
        came_from: Dict[str, str] = {}
        g_costs: Dict[str, float] = {start_node_id: 0}
        
        start_h = self.heuristic_cost(start_node_id, end_node_id, params)
        start_node = PathNode(start_node_id, 0, start_h, current_time)
        heapq.heappush(open_set, (start_node.f_cost, id(start_node), start_node))
        
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            
            _, _, current = heapq.heappop(open_set)
            
            if current.node_id in closed_set:
                continue
            
            closed_set.add(current.node_id)
            
            # Arrivée trouvée
            if current.node_id == end_node_id:
                path = []
                node = end_node_id
                while node in came_from:
                    path.insert(0, node)
                    node = came_from[node]
                path.insert(0, start_node_id)
                
                logger.info(f"Route trouvée en {iterations} itérations: {len(path)} waypoints")
                return path
            
            # Exploration des voisins
            for neighbor in self.graph.successors(current.node_id):
                if neighbor in closed_set:
                    continue
                
                edge_cost, _ = self.compute_edge_cost(
                    current.node_id, neighbor, params, current.timestamp
                )
                
                if edge_cost == float('inf'):
                    continue
                
                tentative_g = g_costs[current.node_id] + edge_cost
                
                if neighbor not in g_costs or tentative_g < g_costs[neighbor]:
                    came_from[neighbor] = current.node_id
                    g_costs[neighbor] = tentative_g
                    
                    h = self.heuristic_cost(neighbor, end_node_id, params)
                    neighbor_node = PathNode(
                        neighbor,
                        tentative_g,
                        h,
                        current.timestamp + timedelta(hours=edge_cost / 10)
                    )
                    heapq.heappush(
                        open_set,
                        (neighbor_node.f_cost, id(neighbor_node), neighbor_node)
                    )
        
        logger.warning(f"Pas de route trouvée après {iterations} itérations")
        return None
    
    def construct_optimized_route(self, path: List[str], 
                                  params: OptimizationParams) -> OptimizedRoute:
        """Construit un objet OptimizedRoute à partir d'un chemin"""
        
        waypoints = [self.waypoints[node_id] for node_id in path]
        segments = []
        
        total_distance_nm = 0
        total_time_hours = 0
        total_fuel_tons = 0
        total_cost_usd = 0
        total_risk_score = 0
        
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]
            
            edge_cost, edge_data = self.compute_edge_cost(
                from_node, to_node, params, datetime.now()
            )
            
            if edge_data:
                distance = edge_data.get('weight', 0)
                time = edge_data.get('time_hours', 0)
                fuel = edge_data.get('fuel_tons', 0)
                
                total_distance_nm += distance
                total_time_hours += time
                total_fuel_tons += fuel
                total_cost_usd += fuel * params.fuel_price_per_ton
                
                risk_val = (edge_data.get('weather_risk', 0) + 
                           edge_data.get('piracy_risk', 0)) / 2
                total_risk_score += risk_val
                
                # Création du segment
                segment = RouteSegment(
                    from_node_id=from_node,
                    to_node_id=to_node,
                    from_waypoint=self.waypoints[from_node],
                    to_waypoint=self.waypoints[to_node],
                    attributes=EdgeAttributes(
                        distance_nm=distance,
                        time_hours_avg=time,
                        fuel_consumption_tons=fuel,
                        weather_risk=RiskLevel(int(edge_data.get('weather_risk', 0))),
                    )
                )
                segments.append(segment)
        
        return OptimizedRoute(
            waypoints=waypoints,
            segments=segments,
            total_distance_nm=total_distance_nm,
            estimated_time_hours=total_time_hours,
            estimated_fuel_tons=total_fuel_tons,
            estimated_cost_usd=total_cost_usd,
            overall_risk_score=total_risk_score / max(len(segments), 1),
        )
