import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CongestionForecast:
    """Prévision de congestion d'un port"""
    port_id: str
    port_name: str
    timestamp: datetime
    predicted_queue_length: int
    predicted_wait_hours: float
    confidence_score: float
    factors: Dict[str, float]  # Facteurs influençant la prédiction


class CongestionForecastingAgent:
    """
    Prédit les temps d'attente aux ports
    Utilise les modèles de séries temporelles
    """
    
    def __init__(self):
        # Données historiques simulées (en production: BigQuery)
        self.port_history: Dict[str, List[Dict]] = {}
        self.forecasts: Dict[str, CongestionForecast] = {}
        
    def register_port_history(self, port_id: str, historical_data: List[Dict]):
        """
        Enregistre l'historique d'un port
        historical_data: [{timestamp, queue_length, wait_hours, vessel_type, ...}]
        """
        self.port_history[port_id] = historical_data
        logger.info(f"Historique enregistré pour {port_id}: {len(historical_data)} entrées")
    
    def simple_moving_average_forecast(self, port_id: str, days_ahead: int = 3) -> Optional[float]:
        """
        Prévision simple par moyenne mobile
        Pour 3 jours à l'avance: moyenne des 7 derniers jours
        """
        if port_id not in self.port_history:
            return None
        
        history = self.port_history[port_id]
        
        if not history:
            return None
        
        # Conversion en DataFrame pour facilité
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Moyenne mobile sur les 7 derniers jours
        recent_data = df.tail(7)
        avg_wait = recent_data['wait_hours'].mean()
        
        return avg_wait
    
    def seasonal_adjustment_forecast(self, port_id: str, forecast_date: datetime) -> float:
        """
        Ajuste la prévision en fonction de la saisonnalité
        Exemple: ports nord = plus congestion en été
        """
        if port_id not in self.port_history:
            return 0.0
        
        history = self.port_history[port_id]
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['month'] = df['timestamp'].dt.month
        
        # Groupe par mois
        monthly_avg = df.groupby('month')['wait_hours'].mean()
        
        month_of_forecast = forecast_date.month
        
        if month_of_forecast in monthly_avg.index:
            return monthly_avg[month_of_forecast]
        
        return df['wait_hours'].mean()
    
    def vessel_type_adjustment(self, port_id: str, vessel_type: str) -> float:
        """
        Ajuste en fonction du type de navire
        Les navires cargo de gros tonnage attendent généralement plus
        """
        if port_id not in self.port_history:
            return 0.0
        
        history = self.port_history[port_id]
        df = pd.DataFrame(history)
        
        # Moyenne par type de navire
        if 'vessel_type' in df.columns:
            type_avg = df.groupby('vessel_type')['wait_hours'].mean()
            
            if vessel_type in type_avg.index:
                return type_avg[vessel_type]
        
        return df['wait_hours'].mean()
    
    def forecast_port_congestion(self, port_id: str, arrival_date: datetime,
                                 vessel_type: Optional[str] = None) -> CongestionForecast:
        """
        Prévision complète de la congestion d'un port
        Combine plusieurs modèles
        """
        logger.info(f"Prévision de congestion pour {port_id} (arrivée: {arrival_date})")
        
        # 1. Moyenne mobile
        ma_forecast = self.simple_moving_average_forecast(port_id, days_ahead=3)
        
        # 2. Ajustement saisonnier
        seasonal_factor = self.seasonal_adjustment_forecast(port_id, arrival_date)
        
        # 3. Ajustement par type de navire
        vessel_factor = self.vessel_type_adjustment(port_id, vessel_type) if vessel_type else 0
        
        # Combinaison des modèles (poids égaux)
        predicted_wait = (ma_forecast + seasonal_factor + vessel_factor) / 3 \
                        if all([ma_forecast, seasonal_factor]) else ma_forecast or 0
        
        # Estimation de la queue
        predicted_queue = max(1, int(predicted_wait / 2))  # Environ 1 navire tous les 2 heures
        
        # Score de confiance basé sur la quantité de données
        confidence = min(1.0, len(self.port_history.get(port_id, [])) / 100)
        
        forecast = CongestionForecast(
            port_id=port_id,
            port_name=port_id.upper(),
            timestamp=datetime.now(),
            predicted_queue_length=predicted_queue,
            predicted_wait_hours=predicted_wait,
            confidence_score=confidence,
            factors={
                'moving_average': ma_forecast or 0,
                'seasonal_adjustment': seasonal_factor,
                'vessel_type_factor': vessel_factor,
            }
        )
        
        self.forecasts[port_id] = forecast
        return forecast
    
    def select_best_alternate_port(self, primary_port_id: str, 
                                   alternate_ports: List[str],
                                   arrival_date: datetime) -> Optional[str]:
        """
        Sélectionne le port alternatif avec la plus basse prédiction d'attente
        """
        forecasts_dict = {}
        
        for port_id in alternate_ports:
            forecast = self.forecast_port_congestion(port_id, arrival_date)
            forecasts_dict[port_id] = forecast.predicted_wait_hours
        
        if not forecasts_dict:
            return None
        
        best_port = min(forecasts_dict, key=forecasts_dict.get)
        
        logger.info(
            f"Port alternatif sélectionné: {best_port} "
            f"({forecasts_dict[best_port]:.1f}h d'attente prévue)"
        )
        
        return best_port
    
    def add_queue_time_to_eta(self, current_eta: datetime, port_id: str) -> datetime:
        """
        Ajoute le temps d'attente prévu à l'ETA
        Retourne l'ETA révisée (Estimated Time of Arrival + Queue)
        """
        forecast = self.forecast_port_congestion(port_id, current_eta)
        queue_time = timedelta(hours=forecast.predicted_wait_hours)
        
        revised_eta = current_eta + queue_time
        
        logger.info(
            f"ETA pour {port_id}: {current_eta} + {forecast.predicted_wait_hours:.1f}h "
            f"= {revised_eta}"
        )
        
        return revised_eta
    
    def generate_congestion_report(self, ports: List[str]) -> str:
        """Génère un rapport de prévision pour plusieurs ports"""
        report = "=== RAPPORT DE PRÉVISION DE CONGESTION ===\n\n"
        
        for port_id in ports:
            if port_id in self.forecasts:
                forecast = self.forecasts[port_id]
                report += f"Port: {forecast.port_name}\n"
                report += f"  Queue prévue: {forecast.predicted_queue_length} navires\n"
                report += f"  Attente prévue: {forecast.predicted_wait_hours:.1f} heures\n"
                report += f"  Confiance: {forecast.confidence_score * 100:.0f}%\n\n"
        
        return report
