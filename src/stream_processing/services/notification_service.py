"""
Servizio per gestire la generazione di notifiche.
"""
import logging
import time
import httpx
from typing import Dict, Any, Tuple

from src.configg import MESSAGE_GENERATOR_URL

logger = logging.getLogger(__name__)

class NotificationService:
    """Servizio per gestire notifiche personalizzate."""
    
    def __init__(self):
        """Inizializza il servizio."""
        self.http_client = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Ottiene il client HTTP."""
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=10.0)
        return self.http_client
    
    async def generate_personalized_message(
        self, 
        user_data: Dict[str, Any], 
        poi_data: Dict[str, Any]
    ) -> Tuple[str, bool, float]:
        """
        Genera un messaggio personalizzato per l'utente.
        
        Args:
            user_data: Dati dell'utente
            poi_data: Dati del punto di interesse
            
        Returns:
            Tuple[str, bool, float]: (messaggio, from_cache, tempo_generazione_ms)
        """
        start_time = time.time()
        
        try:
            client = await self._get_http_client()
            
            payload = {
                "user": {
                    "age": user_data["age"],
                    "profession": user_data["profession"],
                    "interests": user_data["interests"]
                },
                "poi": poi_data
            }
            
            response = await client.post(MESSAGE_GENERATOR_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                generation_time = (time.time() - start_time) * 1000
                
                return (
                    result.get("message", ""), 
                    result.get("cached", False),
                    generation_time
                )
            else:
                logger.error(f"Message generator error: {response.status_code}")
                return "", False, 0.0
                
        except Exception as e:
            logger.error(f"Error generating personalized message: {e}")
            # Fallback message
            fallback_msg = self._generate_fallback_message(poi_data.get("name", "negozio"))
            generation_time = (time.time() - start_time) * 1000
            return fallback_msg, False, generation_time
    
    def _generate_fallback_message(self, shop_name: str) -> str:
        """Genera un messaggio di fallback."""
        return f"Sei vicino a {shop_name}! Fermati a dare un'occhiata."
    
    async def close(self):
        """Chiude le risorse del servizio."""
        if self.http_client:
            await self.http_client.aclose()