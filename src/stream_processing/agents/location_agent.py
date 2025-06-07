"""
Agent Faust per processare eventi di posizione.
"""
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator

from ..app import app
from ..topics.topics import location_events_topic, shop_proximity_topic
from ..tables.state_tables import user_states_table
from ..models.events import LocationEvent, ShopProximityEvent
from ..models.state import UserState
from ..services.location_service import LocationService

logger = logging.getLogger(__name__)

# Inizializza il servizio di localizzazione
location_service = LocationService()

@app.agent(location_events_topic)
async def process_location_events(stream) -> AsyncGenerator[None, None]:
    """
    Processa eventi di posizione degli utenti.
    
    - Aggiorna stato utente
    - Calcola distanza percorsa
    - Trova negozi nelle vicinanze
    - Pubblica eventi di prossimità
    """
    async for event in stream:
        try:
            logger.debug(f"Processing location event for user {event.user_id}")
            
            # Ottieni stato utente corrente
            current_state = user_states_table.get(event.user_id, UserState(
                user_id=event.user_id,
                last_latitude=event.latitude,
                last_longitude=event.longitude,
                last_seen=event.timestamp
            ))
            
            # Calcola distanza percorsa se abbiamo posizione precedente
            distance_traveled = 0.0
            if hasattr(current_state, 'last_latitude'):
                distance_traveled = location_service.calculate_distance(
                    current_state.last_latitude, current_state.last_longitude,
                    event.latitude, event.longitude
                )
            
            # Aggiorna stato utente
            updated_state = UserState(
                user_id=event.user_id,
                last_latitude=event.latitude,
                last_longitude=event.longitude,
                last_seen=event.timestamp,
                total_distance=current_state.total_distance + distance_traveled,
                shops_visited=current_state.shops_visited,
                notifications_received=current_state.notifications_received,
                recent_positions=current_state.recent_positions[-9:] + [{
                    'lat': event.latitude,
                    'lon': event.longitude,
                    'timestamp': event.timestamp.isoformat()
                }],
                recent_notifications=current_state.recent_notifications
            )
            
            # Salva stato aggiornato
            user_states_table[event.user_id] = updated_state
            
            # Trova negozi nelle vicinanze
            nearby_shops = await location_service.find_nearby_shops(
                event.latitude, event.longitude, max_distance=200
            )
            
            # Pubblica eventi di prossimità per ogni negozio vicino
            for shop in nearby_shops:
                proximity_event = ShopProximityEvent(
                    user_id=event.user_id,
                    shop_id=shop['shop_id'],
                    shop_name=shop['shop_name'],
                    shop_category=shop['category'],
                    distance=shop['distance'],
                    latitude=event.latitude,
                    longitude=event.longitude,
                    timestamp=event.timestamp,
                    user_age=event.age,
                    user_profession=event.profession,
                    user_interests=event.interests
                )
                
                # Pubblica su topic prossimità
                await shop_proximity_topic.send(value=proximity_event)
                
                logger.info(f"User {event.user_id} near shop {shop['shop_name']} "
                           f"(distance: {shop['distance']:.1f}m)")
                
        except Exception as e:
            logger.error(f"Error processing location event: {e}")
            # In un sistema di produzione, qui potresti voler inviare a un DLQ
            continue