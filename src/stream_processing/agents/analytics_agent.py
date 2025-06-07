"""
Agent Faust per processare eventi analytics e aggiornare ClickHouse.
"""
import logging
from datetime import datetime
from typing import AsyncGenerator

from ..app import app
from ..topics.topics import notification_events_topic, analytics_events_topic
from ..tables.state_tables import system_stats_table
from ..models.events import NotificationEvent, AnalyticsEvent
from ..services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

# Inizializza il servizio analytics
analytics_service = AnalyticsService()

@app.agent(notification_events_topic)
async def store_notifications(stream) -> AsyncGenerator[None, None]:
    """
    Salva gli eventi di notifica in ClickHouse per la dashboard.
    """
    async for event in stream:
        try:
            await analytics_service.store_notification_event(event)
            logger.debug(f"Stored notification event {event.event_id} in ClickHouse")
            
        except Exception as e:
            logger.error(f"Error storing notification event: {e}")
            continue

@app.agent(analytics_events_topic)
async def process_analytics(stream) -> AsyncGenerator[None, None]:
    """
    Processa eventi analytics per statistiche e reporting.
    """
    async for event in stream:
        try:
            # Aggiorna statistiche di sistema
            system_stats = system_stats_table.get('global', {
                'total_events_processed': 0,
                'total_notifications_sent': 0,
                'active_users_count': 0,
                'last_updated': datetime.now(timezone.utc)
            })
            
            system_stats['total_events_processed'] += 1
            
            if event.event_type == 'notification':
                system_stats['total_notifications_sent'] += 1
            
            system_stats['last_updated'] = event.timestamp
            system_stats_table['global'] = system_stats
            
            # Invia a servizio analytics per elaborazioni più complesse
            await analytics_service.process_analytics_event(event)
            
            logger.debug(f"Processed analytics event: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Error processing analytics event: {e}")
            continue