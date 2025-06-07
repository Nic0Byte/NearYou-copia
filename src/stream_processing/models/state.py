"""
Modelli di stato per le tabelle Faust.
"""
import faust
from datetime import datetime
from typing import Dict, List, Optional


class UserState(faust.Record, serializer='json'):
    """Stato corrente dell'utente."""
    user_id: int
    last_latitude: float
    last_longitude: float
    last_seen: datetime
    
    # Statistiche
    total_distance: float = 0.0
    shops_visited: int = 0
    notifications_received: int = 0
    
    # Storia recente (ultimi N punti)
    recent_positions: List[Dict] = []
    
    # Cache per evitare notifiche duplicate
    recent_notifications: Dict[int, datetime] = {}  # shop_id -> last_notification_time


class ShopStats(faust.Record, serializer='json'):
    """Statistiche per negozio."""
    shop_id: int
    shop_name: str
    category: str
    
    # Contatori
    total_visits: int = 0
    unique_visitors: int = 0
    notifications_sent: int = 0
    
    # Utenti che hanno visitato (per unicità)
    visitors: set = set()
    
    # Timestamp ultimo aggiornamento
    last_updated: datetime


class SystemStats(faust.Record, serializer='json'):
    """Statistiche di sistema aggregate."""
    total_events_processed: int = 0
    total_notifications_sent: int = 0
    active_users_count: int = 0
    last_updated: datetime