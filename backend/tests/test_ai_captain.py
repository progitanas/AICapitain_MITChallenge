import pytest
import json
import networkx as nx
from datetime import datetime, timedelta
from pathlib import Path

# Import backend components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    VesselSpec, VesselDimensions, WayPoint, EdgeAttributes,
    OptimizationParams, OptimizedRoute, NavigationStatus, RiskLevel,
)
from data_engineering.ais_processor import AISDataProcessor, GeospatialGraphBuilder
from optimization_engine.optimizer import WeightedAStarOptimizer
from agents.monitoring_agent import DeviationMonitoringAgent
from agents.forecasting_agent import CongestionForecastingAgent


class TestAISProcessor:
    """Tests pour le pipeline ETL AIS"""
    
    def test_haversine_distance_calculation(self):
        """Test calcul de distance haversine"""
        # Singapore to Hamburg (direct distance is ~5475 NM, not ~7000)
        distance_nm = AISDataProcessor.haversine_distance(
            1.3521, 103.8198,  # Singapore
            53.3495, 9.9878    # Hamburg
        )
        assert 5000 < distance_nm < 6000, f"Expected ~5475 NM, got {distance_nm}"
    
    def test_haversine_same_point(self):
        """Distance entre deux points identiques doit être 0"""
        distance = AISDataProcessor.haversine_distance(0, 0, 0, 0)
        assert distance == 0


class TestGeospatialGraph:
    """Tests pour la construction du graphe géospatial"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.builder = GeospatialGraphBuilder()
    
    def test_add_waypoint(self):
        """Test ajout de waypoint"""
        wp = WayPoint("P1", "Singapore", 1.35, 103.82, "port")
        self.builder.add_waypoint(wp)
        
        assert "P1" in self.builder.waypoints
        assert self.builder.waypoints["P1"].name == "Singapore"
    
    def test_graph_nodes(self):
        """Test que les nodes sont bien dans le graphe"""
        wp1 = WayPoint("P1", "Singapore", 1.35, 103.82, "port")
        wp2 = WayPoint("P2", "Hamburg", 53.35, 9.99, "port")
        
        self.builder.add_waypoint(wp1)
        self.builder.add_waypoint(wp2)
        
        graph = self.builder.get_graph()
        assert graph.number_of_nodes() == 2
        assert "P1" in graph.nodes()
        assert "P2" in graph.nodes()
    
    def test_add_edge(self):
        """Test ajout d'arête entre ports"""
        wp1 = WayPoint("P1", "Singapore", 1.35, 103.82, "port")
        wp2 = WayPoint("P2", "Hamburg", 53.35, 9.99, "port")
        
        self.builder.add_waypoint(wp1)
        self.builder.add_waypoint(wp2)
        
        attrs = EdgeAttributes(
            distance_nm=7000,
            time_hours_avg=350,
            fuel_consumption_tons=105
        )
        
        self.builder.add_edge_from_ais(wp1, wp2, attrs)
        
        graph = self.builder.get_graph()
        assert graph.has_edge("P1", "P2")


class TestOptimizer:
    """Tests pour le moteur d'optimisation"""
    
    def setup_method(self):
        """Setup test graph"""
        self.graph = nx.DiGraph()
        
        # Ajouter 3 ports
        ports = {
            'A': {'name': 'Port A', 'latitude': 0, 'longitude': 0},
            'B': {'name': 'Port B', 'latitude': 1, 'longitude': 1},
            'C': {'name': 'Port C', 'latitude': 2, 'longitude': 2},
        }
        
        for port_id, info in ports.items():
            self.graph.add_node(port_id, **info)
        
        # Ajouter arêtes avec poids
        self.graph.add_edge('A', 'B', distance_nm=100, time_hours=10, fuel_tons=1.5,
                           weather_risk=0, piracy_risk=0)
        self.graph.add_edge('B', 'C', distance_nm=150, time_hours=15, fuel_tons=2.0,
                           weather_risk=1, piracy_risk=0)
        self.graph.add_edge('A', 'C', distance_nm=300, time_hours=30, fuel_tons=4.5,
                           weather_risk=2, piracy_risk=1)
        
        # Créer waypoints dict
        self.waypoints = {
            port_id: WayPoint(port_id, info['name'], info['latitude'], info['longitude'], 'port')
            for port_id, info in ports.items()
        }
        
        self.optimizer = WeightedAStarOptimizer(self.graph, self.waypoints)
    
    def test_find_route_exists(self):
        """Test que l'algorithme trouve un chemin quand il existe"""
        params = OptimizationParams(weight_time=1, weight_cost=1, weight_risk=1)
        path = self.optimizer.find_optimal_route('A', 'C', params)
        
        assert path is not None
        assert path[0] == 'A'
        assert path[-1] == 'C'
    
    def test_find_route_no_path(self):
        """Test quand pas de chemin disponible"""
        params = OptimizationParams()
        path = self.optimizer.find_optimal_route('C', 'A', params)  # Path doesn't exist (directed)
        
        # C ne peut pas atteindre A (graphe orienté)
        assert path is None
    
    def test_compute_edge_cost_weighted(self):
        """Test calcul pondéré du coût d'arête"""
        params = OptimizationParams(
            weight_time=2.0,
            weight_cost=1.0,
            weight_risk=0.5,
            fuel_price_per_ton=500
        )
        
        cost, edge_data = self.optimizer.compute_edge_cost('A', 'B', params, datetime.now())
        
        # Cost = 2*10 + 1*(1.5*500) + 0.5*0 = 20 + 750 = 770
        assert cost > 0
        assert edge_data is not None


class TestDeviationMonitoring:
    """Tests pour l'agent de monitoring de déviation"""
    
    def setup_method(self):
        """Setup"""
        self.graph = nx.DiGraph()
        self.graph.add_node('PORT1', latitude=0, longitude=0, name='Port 1')
        self.graph.add_node('PORT2', latitude=1, longitude=1, name='Port 2')
        self.waypoints = {
            'PORT1': WayPoint('PORT1', 'Port 1', 0, 0, 'port'),
            'PORT2': WayPoint('PORT2', 'Port 2', 1, 1, 'port'),
        }
        
        self.optimizer = WeightedAStarOptimizer(self.graph, self.waypoints)
        self.agent = DeviationMonitoringAgent(self.graph, self.optimizer)
    
    def test_register_voyage(self):
        """Test enregistrement d'un voyage"""
        # Create a mock vessel and route
        vessel = VesselSpec(
            mmsi="MMSI123",
            imo="IMO123",
            name="Test Vessel",
            call_sign="TEST",
            dimensions=VesselDimensions(120, 25, 8.5, 12),
            type_code=70,
            current_position=(0, 0),
            sog_knots=15.0,
            cog_degrees=180.0,
            heading_degrees=180,
            nav_status=NavigationStatus.UNDER_WAY
        )
        
        route = OptimizedRoute(
            waypoints=[
                WayPoint('PORT1', 'Port 1', 0, 0, 'port'),
                WayPoint('PORT2', 'Port 2', 1, 1, 'port'),
            ],
            segments=[],
            total_distance_nm=100,
            estimated_time_hours=10,
            estimated_fuel_tons=5,
            estimated_cost_usd=2500,
            overall_risk_score=1.5
        )
        
        # Register the voyage
        self.agent.register_voyage(vessel, route)
        
        # Verify it was registered
        assert vessel.mmsi in self.agent.active_voyages
    
    def test_update_position(self):
        """Test mise à jour de position"""
        # Create mock vessel and route
        vessel = VesselSpec(
            mmsi="MMSI123",
            imo="IMO123",
            name="Test Vessel",
            call_sign="TEST",
            dimensions=VesselDimensions(120, 25, 8.5, 12),
            type_code=70,
            current_position=(0, 0),
            sog_knots=15.0,
            cog_degrees=180.0,
            heading_degrees=180,
            nav_status=NavigationStatus.UNDER_WAY
        )
        
        route = OptimizedRoute(
            waypoints=[
                WayPoint('PORT1', 'Port 1', 0, 0, 'port'),
                WayPoint('PORT2', 'Port 2', 1, 1, 'port'),
            ],
            segments=[],
            total_distance_nm=100,
            estimated_time_hours=10,
            estimated_fuel_tons=5,
            estimated_cost_usd=2500,
            overall_risk_score=1.5
        )
        
        # Register voyage first
        self.agent.register_voyage(vessel, route)
        
        # Update position
        self.agent.update_vessel_position('MMSI123', 0.5, 0.5, datetime.now())
        
        # Verify position was recorded
        assert len(self.agent.active_voyages['MMSI123'].actual_positions) == 1


class TestForecastingAgent:
    """Tests pour l'agent de prédiction de congestion"""
    
    def setup_method(self):
        """Setup"""
        self.agent = CongestionForecastingAgent()
    
    def test_forecast_wait_time(self):
        """Test prédiction de temps d'attente"""
        # Register some test data first
        self.agent.register_port_history('PORT_SG', [
            {'timestamp': datetime.now(), 'queue_length': 2, 'wait_hours': 3.5, 'vessel_type': 'CARGO'},
            {'timestamp': datetime.now() - timedelta(days=1), 'queue_length': 1, 'wait_hours': 2.0, 'vessel_type': 'CARGO'},
        ])
        
        # Forecast congestion
        forecast = self.agent.forecast_port_congestion('PORT_SG', datetime.now())
        
        assert forecast is not None
        assert forecast.predicted_wait_hours >= 0
        assert forecast.predicted_queue_length >= 1
    
    def test_predict_queue_length(self):
        """Test prédiction longueur queue"""
        # Register test data
        self.agent.register_port_history('PORT_HH', [
            {'timestamp': datetime.now(), 'queue_length': 2, 'wait_hours': 4.2, 'vessel_type': 'CARGO'},
            {'timestamp': datetime.now() - timedelta(days=1), 'queue_length': 1, 'wait_hours': 2.1, 'vessel_type': 'CARGO'},
        ])
        
        # Forecast for next day
        forecast = self.agent.forecast_port_congestion('PORT_HH', datetime.now() + timedelta(days=1))
        
        assert forecast is not None
        assert isinstance(forecast.predicted_queue_length, int)
        assert forecast.predicted_queue_length >= 1
    
    def test_select_best_alternate_port(self):
        """Test sélection meilleur port alternatif"""
        # Register test data for multiple ports
        for port in ['PORT_HH', 'PORT_RO', 'PORT_DU']:
            self.agent.register_port_history(port, [
                {'timestamp': datetime.now(), 'queue_length': 2, 'wait_hours': 4.0, 'vessel_type': 'CARGO'},
                {'timestamp': datetime.now() - timedelta(days=1), 'queue_length': 1, 'wait_hours': 2.0, 'vessel_type': 'CARGO'},
            ])
        
        # Select best alternate port
        best_port = self.agent.select_best_alternate_port(
            'PORT_HH',
            ['PORT_RO', 'PORT_DU'],
            datetime.now() + timedelta(days=5)
        )
        
        assert best_port is not None
        assert best_port in ['PORT_RO', 'PORT_DU']


class TestDataModels:
    """Tests pour les data models Pydantic"""
    
    def test_vessel_dimensions_creation(self):
        """Test création VesselDimensions"""
        dims = VesselDimensions(
            length_m=120,
            beam_m=25,
            draught_m=8.5,
            depth_m=12
        )
        
        assert dims.length_m == 120
        assert dims.draught_m == 8.5
    
    def test_optimization_params_defaults(self):
        """Test paramètres par défaut"""
        params = OptimizationParams()
        
        assert params.weight_time == 1.0
        assert params.weight_cost == 1.0
        assert params.weight_risk == 1.0
        assert params.fuel_price_per_ton == 500.0
    
    def test_risk_level_enum(self):
        """Test énumération RiskLevel"""
        assert RiskLevel.NONE.value == 0
        assert RiskLevel.CRITICAL.value == 4
    
    def test_navigation_status_enum(self):
        """Test énumération NavigationStatus"""
        assert NavigationStatus.UNDER_WAY.value == 0
        assert NavigationStatus.AT_ANCHOR.value == 1


# ==================== FIXTURES ====================

@pytest.fixture
def simple_graph():
    """Graph simple pour tests"""
    G = nx.DiGraph()
    G.add_node('A', latitude=0, longitude=0)
    G.add_node('B', latitude=1, longitude=1)
    G.add_edge('A', 'B', distance_nm=100, time_hours=10, fuel_tons=1, weather_risk=0, piracy_risk=0)
    return G


@pytest.fixture
def ais_processor():
    """Processeur AIS pour tests"""
    return AISDataProcessor('./test_data/ais_test.json')


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
