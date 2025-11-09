import json
import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

from models import (
    WayPoint,
    EdgeAttributes,
    RiskLevel,
    NavigationStatus,
)

logger = logging.getLogger(__name__)


class AISDataProcessor:
    """Traitement des données AIS brutes"""
    
    def __init__(self, ais_data_path: str):
        self.ais_data_path = Path(ais_data_path)
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        
    def load_ais_data(self) -> pd.DataFrame:
        """Charge les données AIS JSON"""
        logger.info(f"Chargement des données AIS depuis {self.ais_data_path}")
        
        with open(self.ais_data_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # Conversion des types
        df['TSTAMP'] = pd.to_datetime(df['TSTAMP'], format='%Y-%m-%d %H:%M:%S GMT')
        df['LATITUDE'] = pd.to_numeric(df['LATITUDE'], errors='coerce')
        df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
        df['SOG'] = pd.to_numeric(df['SOG'], errors='coerce')
        df['COG'] = pd.to_numeric(df['COG'], errors='coerce')
        df['DRAUGHT'] = pd.to_numeric(df['DRAUGHT'], errors='coerce')
        
        # Nettoyage
        df = df.dropna(subset=['LATITUDE', 'LONGITUDE', 'MMSI'])
        
        self.raw_data = df
        logger.info(f"Données chargées: {len(df)} enregistrements")
        
        return df
    
    def create_voyage_segments(self, min_time_gap_hours: float = 1.0) -> pd.DataFrame:
        """
        Crée des segments de voyage continus
        Groupe les points AIS consécutifs d'un même navire
        """
        logger.info(f"Création des segments de voyage (gap minimum: {min_time_gap_hours}h)")
        
        df = self.raw_data.sort_values(['MMSI', 'TSTAMP'])
        segments = []
        
        for mmsi, group in df.groupby('MMSI'):
            group = group.sort_values('TSTAMP').reset_index(drop=True)
            
            for i in range(len(group) - 1):
                row1 = group.iloc[i]
                row2 = group.iloc[i + 1]
                
                time_gap = (row2['TSTAMP'] - row1['TSTAMP']).total_seconds() / 3600
                
                # Ignorer les gaps trop grands (changement de jour ou perte de signal)
                if time_gap > min_time_gap_hours:
                    continue
                
                segment = {
                    'mmsi': mmsi,
                    'vessel_name': row1['NAME'],
                    'from_lat': row1['LATITUDE'],
                    'from_lon': row1['LONGITUDE'],
                    'to_lat': row2['LATITUDE'],
                    'to_lon': row2['LONGITUDE'],
                    'time_hours': time_gap,
                    'sog_knots': row2['SOG'],
                    'timestamp': row1['TSTAMP'],
                    'draught': row1['DRAUGHT'],
                }
                
                segments.append(segment)
        
        self.processed_data = pd.DataFrame(segments)
        logger.info(f"Créé {len(segments)} segments de voyage")
        
        return self.processed_data
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcule la distance en nautical miles entre deux points
        """
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        nm = c * 3440.065  # Rayon terrestre en nautical miles
        return nm
    
    def compute_edge_statistics(self) -> Dict[Tuple[Tuple[float, float], Tuple[float, float]], Dict]:
        """
        Agrège les statistiques par arête (route)
        Retourne temps moyen, consommation moyenne, etc.
        """
        logger.info("Calcul des statistiques par arête")
        
        edge_stats = {}
        
        for _, row in self.processed_data.iterrows():
            from_point = (round(row['from_lat'], 2), round(row['from_lon'], 2))
            to_point = (round(row['to_lat'], 2), round(row['to_lon'], 2))
            
            edge_key = (from_point, to_point)
            
            distance_nm = self.haversine_distance(
                row['from_lat'], row['from_lon'],
                row['to_lat'], row['to_lon']
            )
            
            if edge_key not in edge_stats:
                edge_stats[edge_key] = {
                    'distances': [],
                    'times': [],
                    'speeds': [],
                    'count': 0,
                }
            
            edge_stats[edge_key]['distances'].append(distance_nm)
            edge_stats[edge_key]['times'].append(row['time_hours'])
            edge_stats[edge_key]['speeds'].append(row['sog_knots'])
            edge_stats[edge_key]['count'] += 1
        
        # Agrégation
        aggregated = {}
        for edge_key, stats in edge_stats.items():
            if stats['count'] >= 3:  # Au moins 3 observations
                aggregated[edge_key] = {
                    'distance_nm': np.mean(stats['distances']),
                    'time_hours_avg': np.mean(stats['times']),
                    'speed_avg_knots': np.mean(stats['speeds']),
                    'observations': stats['count'],
                    'fuel_consumption_tons': np.mean(stats['distances']) * 0.015,  # Estimation: 0.015t par NM
                }
        
        logger.info(f"Statistiques agrégées pour {len(aggregated)} arêtes")
        
        return aggregated


class GeospatialGraphBuilder:
    """Construction du Graphe Géospatial"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.waypoints: Dict[str, WayPoint] = {}
        
    def add_waypoint(self, waypoint: WayPoint):
        """Ajoute un point d'intérêt (port, waypoint)"""
        self.waypoints[waypoint.id] = waypoint
        self.graph.add_node(
            waypoint.id,
            latitude=waypoint.latitude,
            longitude=waypoint.longitude,
            name=waypoint.name,
            port_type=waypoint.port_type,
        )
    
    def add_edge_from_ais(self, from_wp: WayPoint, to_wp: WayPoint, 
                          attributes: EdgeAttributes):
        """Ajoute une arête basée sur les observations AIS"""
        edge_id = f"{from_wp.id}_{to_wp.id}"
        
        self.graph.add_edge(
            from_wp.id,
            to_wp.id,
            weight=attributes.distance_nm,
            time_hours=attributes.time_hours_avg,
            fuel_tons=attributes.fuel_consumption_tons,
            weather_risk=attributes.weather_risk.value,
            piracy_risk=attributes.piracy_risk.value,
            navigability=attributes.navigability,
            blocked=attributes.blocked,
        )
    
    def get_graph(self) -> nx.DiGraph:
        """Retourne le graphe NetworkX"""
        return self.graph
    
    def get_waypoint_by_proximity(self, latitude: float, longitude: float, 
                                   radius_nm: float = 50) -> Optional[WayPoint]:
        """Trouve le waypoint le plus proche"""
        from data_engineering.ais_processor import AISDataProcessor
        
        distances = {}
        for wp_id, wp in self.waypoints.items():
            dist = AISDataProcessor.haversine_distance(
                latitude, longitude,
                wp.latitude, wp.longitude
            )
            if dist <= radius_nm:
                distances[wp_id] = dist
        
        if distances:
            closest_id = min(distances, key=distances.get)
            return self.waypoints[closest_id]
        
        return None
    
    def get_graph_statistics(self) -> Dict:
        """Retourne les statistiques du graphe"""
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'waypoints': len(self.waypoints),
            'is_directed': self.graph.is_directed(),
        }
