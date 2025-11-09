"""
Data Models pour AI Captain
Définition des structures de données principales du système
"""
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict
from datetime import datetime
from enum import Enum
import json


class NavigationStatus(Enum):
    """États de navigation d'un navire (IFREMER standard)"""
    UNDER_WAY = 0
    AT_ANCHOR = 1
    NOT_UNDER_COMMAND = 2
    RESTRICTED_MANEUVERABILITY = 3
    CONSTRAINED_DRAFT = 4
    MOORED = 5
    AGROUND = 6
    ENGAGED_FISHING = 7
    UNDER_WAY_TOWING = 8


class RiskLevel(Enum):
    """Niveaux de risque"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class VesselDimensions:
    """Dimensions du navire"""
    length_m: float  # Longueur en mètres
    beam_m: float   # Largeur en mètres
    draught_m: float  # Tirant d'eau en mètres
    depth_m: float  # Profondeur du navire


@dataclass
class VesselSpec:
    """Spécifications d'un navire"""
    mmsi: str
    imo: str
    name: str
    call_sign: str
    dimensions: VesselDimensions
    type_code: int  # IMO type code
    current_position: Tuple[float, float]  # (lat, lon)
    sog_knots: float  # Speed over ground
    cog_degrees: float  # Course over ground
    heading_degrees: float
    nav_status: NavigationStatus
    destination_port: Optional[str] = None
    eta: Optional[datetime] = None


@dataclass
class WayPoint:
    """Point d'intérêt (port, waypoint)"""
    id: str
    name: str
    latitude: float
    longitude: float
    port_type: str  # 'port', 'waypoint', 'chokepoint'
    capacity: Optional[int] = None
    waiting_hours_avg: float = 0.0


@dataclass
class EdgeAttributes:
    """Attributs d'une arête du graphe (segment de route)"""
    distance_nm: float  # Nautical miles
    time_hours_avg: float  # Temps moyen historique
    fuel_consumption_tons: float  # Consommation historique moyenne
    weather_risk: RiskLevel = RiskLevel.NONE
    piracy_risk: RiskLevel = RiskLevel.NONE
    navigability: bool = True
    blocked: bool = False
    block_reason: Optional[str] = None


@dataclass
class RouteSegment:
    """Segment de route entre deux points"""
    from_node_id: str
    to_node_id: str
    from_waypoint: WayPoint
    to_waypoint: WayPoint
    attributes: EdgeAttributes


@dataclass
class OptimizationParams:
    """Paramètres d'optimisation"""
    weight_time: float = 1.0  # Poids du temps
    weight_cost: float = 1.0  # Poids du coût
    weight_risk: float = 1.0  # Poids du risque
    fuel_price_per_ton: float = 500.0  # USD/tonne
    max_draft_constraint: Optional[float] = None
    no_go_zones: List[Dict] = field(default_factory=list)  # Polygones interdits
    weather_avoidance: bool = True
    speed_profile: str = "normal"  # 'slow', 'normal', 'fast'


@dataclass
class OptimizedRoute:
    """Route optimisée résultante"""
    waypoints: List[WayPoint]
    segments: List[RouteSegment]
    total_distance_nm: float
    estimated_time_hours: float
    estimated_fuel_tons: float
    estimated_cost_usd: float
    overall_risk_score: float
    optimization_metrics: Dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0


@dataclass
class ReroutingEvent:
    """Événement de re-routage"""
    vessel_mmsi: str
    trigger_type: str  # 'storm', 'blockage', 'congestion', 'schedule'
    trigger_location: Tuple[float, float]  # (lat, lon)
    old_route: OptimizedRoute
    new_route: Optional[OptimizedRoute] = None
    timestamp: datetime = field(default_factory=datetime.now)
    deviation_km: float = 0.0
    eta_impact_hours: float = 0.0


@dataclass
class WeatherForecast:
    """Prévisions météorologiques"""
    location: Tuple[float, float]  # (lat, lon)
    timestamp: datetime
    wave_height_m: float
    wind_speed_knots: float
    wind_direction_degrees: float
    pressure_hpa: float
    visibility_km: float
    storm_risk: RiskLevel = RiskLevel.NONE


@dataclass
class PortCongestion:
    """État de congestion d'un port"""
    port_id: str
    timestamp: datetime
    queue_length: int  # Nombre de navires en attente
    avg_wait_hours: float
    estimated_wait_hours: float


def serialize_route(route: OptimizedRoute) -> str:
    """Sérialise une route optimisée en JSON"""
    return json.dumps({
        "waypoints": [
            {"id": wp.id, "name": wp.name, "lat": wp.latitude, "lon": wp.longitude}
            for wp in route.waypoints
        ],
        "metrics": {
            "total_distance_nm": route.total_distance_nm,
            "estimated_time_hours": route.estimated_time_hours,
            "estimated_fuel_tons": route.estimated_fuel_tons,
            "estimated_cost_usd": route.estimated_cost_usd,
            "overall_risk_score": route.overall_risk_score,
        },
        "generated_at": route.generated_at.isoformat(),
    }, indent=2)
