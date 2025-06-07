"""
Servizio per analytics e salvataggio in ClickHouse.
"""
import logging
from datetime import datetime
from clickhouse_driver import Client as CHClient
from typing import Dict, Any

from src.configg import get_clickhouse_config
from ..models.events import NotificationEvent, AnalyticsEvent

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Servizio per gestire analytics e storage in ClickHouse."""
    
    def __init__(self):
        """Inizializza il servizio."""
        self.ch_client = CHClient(**get_clickhouse_config())
    
    async def store_notification_event(self, event: NotificationEvent) -> None:
        """
        Salva un evento di notifica in ClickHouse.
        
        Args:
            event: Evento di notifica da salvare
        """
        try:
            # Converte timestamp in formato ClickHouse
            timestamp = event.timestamp.replace(tzinfo=None) if event.timestamp.tzinfo else event.timestamp
            
            self.ch_client.execute(
                """
                INSERT INTO user_events
                (event_id, event_time, user_id, latitude, longitude, 
                 poi_range, poi_name, poi_info)
                VALUES
                """,
                [(
                    int(event.event_id.split('_')[-1]),  # Usa timestamp come event_id
                    timestamp,
                    event.user_id,
                    event.latitude,
                    event.longitude,
                    event.distance,
                    event.shop_name,
                    event.message
                )]
            )
            
            logger.debug(f"Stored notification event {event.event_id} in ClickHouse")
            
        except Exception as e:
            logger.error(f"Error storing notification event in ClickHouse: {e}")
            raise
    
    async def process_analytics_event(self, event: AnalyticsEvent) -> None:
        """
        Processa un evento analytics per statistiche avanzate.
        
        Args:
            event: Evento analytics da processare
        """
        try:
            # Qui puoi implementare logiche di analytics più complesse
            # Per ora, logghiamo l'evento
            logger.debug(f"Processing analytics event: {event.event_type} "
                        f"for user {event.user_id}")
            
            # Esempio: potresti aggregare dati per reporting
            # o triggerare altre azioni basate sul tipo di evento
            
        except Exception as e:
            logger.error(f"Error processing analytics event: {e}")