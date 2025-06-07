"""
Servizio per operazioni relative alla localizzazione.
"""
import asyncio
import logging
import math
import asyncpg
from typing import List, Dict, Any

from src.configg import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, 
    POSTGRES_PASSWORD, POSTGRES_DB
)

logger = logging.getLogger(__name__)

class LocationService:
    """Servizio per gestire operazioni di localizzazione."""
    
    def __init__(self):
        """Inizializza il servizio."""
        self.pool = None
    
    async def _get_pool(self):
        """Ottiene il pool di connessioni PostgreSQL."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database=POSTGRES_DB,
                min_size=1,
                max_size=5
            )
        return self.pool
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcola la distanza haversine tra due punti in metri.
        
        Args:
            lat1, lon1: Coordinate del primo punto
            lat2, lon2: Coordinate del secondo punto
            
        Returns:
            float: Distanza in metri
        """
        R = 6371000  # Raggio della Terra in metri
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    async def find_nearby_shops(
        self, 
        latitude: float, 
        longitude: float, 
        max_distance: float = 200
    ) -> List[Dict[str, Any]]:
        """
        Trova negozi nelle vicinanze di una posizione.
        
        Args:
            latitude: Latitudine della posizione
            longitude: Longitudine della posizione
            max_distance: Distanza massima in metri
            
        Returns:
            List[Dict]: Lista dei negozi nelle vicinanze
        """
        try:
            pool = await self._get_pool()
            
            async with pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        shop_id,
                        shop_name,
                        category,
                        ST_Distance(
                            geom::geography,
                            ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                        ) AS distance
                    FROM shops
                    WHERE ST_Distance(
                        geom::geography,
                        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
                    ) <= $3
                    ORDER BY distance
                    LIMIT 10
                """, longitude, latitude, max_distance)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error finding nearby shops: {e}")
            return []