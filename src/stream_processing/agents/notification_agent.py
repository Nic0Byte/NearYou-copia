"""
Agent Faust per processare eventi di prossimità e generare notifiche.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator

from ..app import app
from ..topics.topics import shop_proximity_topic, notification_events_topic, analytics_events_topic
from ..tables.state_tables import user_states_table, shop_stats_table
from ..models.events import ShopProximityEvent, NotificationEvent, AnalyticsEvent
from ..services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Inizializza il servizio di notifiche
notification_service = NotificationService()

@app.agent(shop_proximity_topic)
async def process_proximity_events(stream) -> AsyncGenerator[None, None]:
    """
    Processa eventi di prossimità ai negozi e genera notifiche personalizzate.
    
    - Verifica se l'utente ha già ricevuto notifiche recenti per il negozio
    - Genera messaggio personalizzato
    - Pubblica evento di notifica
    - Aggiorna statistiche
    """
    async for event in stream:
        try:
            logger.debug(f"Processing proximity event: User {event.user_id} "
                        f"near {event.shop_name} ({event.distance:.1f}m)")
            
            # Ottieni stato utente corrente
            user_state = user_states_table.get(event.user_id)
            if not user_state:
                logger.warning(f"No state found for user {event.user_id}")
                continue
            
            # Controlla se abbiamo già inviato una notifica recente per questo negozio
            cooldown_period = timedelta(minutes=30)  # 30 minuti tra notifiche dello stesso negozio
            last_notification_time = user_state.recent_notifications.get(event.shop_id)
            
            if (last_notification_time and 
                event.timestamp - last_notification_time < cooldown_period):
                logger.debug(f"Skipping notification for user {event.user_id}, "
                           f"shop {event.shop_id} due to cooldown")
                continue
            
            # Genera messaggio personalizzato
            message, from_cache, generation_time = await notification_service.generate_personalized_message(
                user_data={
                    'age': event.user_age,
                    'profession': event.user_profession,
                    'interests': event.user_interests
                },
                poi_data={
                    'name': event.shop_name,
                    'category': event.shop_category,
                    'description': f"Negozio a {event.distance:.0f}m di distanza"
                }
            )
            
            if message:
                # Crea evento di notifica
                notification_event = NotificationEvent(
                    event_id=f"{event.user_id}_{event.shop_id}_{int(event.timestamp.timestamp())}",
                    user_id=event.user_id,
                    shop_id=event.shop_id,
                    shop_name=event.shop_name,
                    shop_category=event.shop_category,
                    message=message,
                    distance=event.distance,
                    latitude=event.latitude,
                    longitude=event.longitude,
                    timestamp=event.timestamp,
                    from_cache=from_cache,
                    generation_time_ms=generation_time
                )
                
                # Pubblica evento di notifica
                await notification_events_topic.send(value=notification_event)
                
                # Aggiorna stato utente con nuova notifica
                user_state.recent_notifications[event.shop_id] = event.timestamp
                user_state.notifications_received += 1
                user_states_table[event.user_id] = user_state
                
                # Aggiorna statistiche negozio
                shop_stats = shop_stats_table.get(event.shop_id)
                if shop_stats:
                    shop_stats.notifications_sent += 1
                    shop_stats.last_updated = event.timestamp
                    shop_stats_table[event.shop_id] = shop_stats
                
                # Pubblica evento analytics
                analytics_event = AnalyticsEvent(
                    event_type='notification',
                    user_id=event.user_id,
                    shop_id=event.shop_id,
                    shop_category=event.shop_category,
                    distance=event.distance,
                    timestamp=event.timestamp,
                    metadata={
                        'from_cache': from_cache,
                        'generation_time_ms': generation_time,
                        'message_length': len(message)
                    }
                )
                await analytics_events_topic.send(value=analytics_event)
                
                logger.info(f"Notification sent to user {event.user_id} "
                          f"for shop {event.shop_name}: {message[:50]}...")
                
        except Exception as e:
            logger.error(f"Error processing proximity event: {e}")
            continue