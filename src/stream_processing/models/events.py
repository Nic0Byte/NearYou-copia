"""
Modelli Faust per gli eventi del sistema NearYou.
"""
import faust
from datetime import datetime
from typing import Optional


class LocationEvent(faust.Record, serializer='json'):
    """Evento di posizione utente."""
    user_id: int
    latitude: float
    longitude: float
    timestamp: datetime
    age: int
    profession: str
    interests: str


class ShopProximityEvent(faust.Record, serializer='json'):
    """Evento di prossimità a un negozio."""
    user_id: int
    shop_id: int
    shop_name: str
    shop_category: str
    distance: float
    latitude: float
    longitude: float
    timestamp: datetime
    
    # Dati utente per personalizzazione
    user_age: int
    user_profession: str
    user_interests: str


class NotificationEvent(faust.Record, serializer='json'):
    """Evento di notifica generata."""
    event_id: str
    user_id: int
    shop_id: int
    shop_name: str
    shop_category: str
    message: str
    distance: float
    latitude: float
    longitude: float
    timestamp: datetime
    
    # Metadati
    from_cache: bool = False
    generation_time_ms: Optional[float] = None


class AnalyticsEvent(faust.Record, serializer='json'):
    """Evento per analytics."""
    event_type: str  # 'location', 'notification', 'shop_visit'
    user_id: int
    shop_id: Optional[int] = None
    shop_category: Optional[str] = None
    distance: Optional[float] = None
    timestamp: datetime
    
    # Metadati aggiuntivi
    metadata: dict = {}


class UserStateUpdate(faust.Record, serializer='json'):
    """Aggiornamento dello stato utente."""
    user_id: int
    last_latitude: float
    last_longitude: float
    last_seen: datetime
    total_distance: float
    shops_visited: int
    notifications_received: int