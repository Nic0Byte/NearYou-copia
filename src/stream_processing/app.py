"""
Main Faust application per stream processing NearYou.
"""
import os
import logging
import ssl
from faust import App

from src.configg import (
    KAFKA_BROKER, SSL_CAFILE, SSL_CERTFILE, SSL_KEYFILE
)

logger = logging.getLogger(__name__)

# Configurazione SSL per Kafka
ssl_context = ssl.create_default_context(cafile=SSL_CAFILE)
ssl_context.load_cert_chain(certfile=SSL_CERTFILE, keyfile=SSL_KEYFILE)

# Configurazione Faust app (usa memory store)
app = App(
    'nearyou-stream-processor',
    broker=f'kafka+ssl://{KAFKA_BROKER}',
    broker_credentials=ssl_context,
    value_type='json',
    web_host='0.0.0.0',
    web_port=8002,
    
    # Usa memory store (nessuna persistenza ma molto più semplice)
    store='memory://',
    
    # Configurazioni per produzione
    stream_buffer_maxsize=1000,
    stream_wait_empty=False,
    
    # Configurazioni per consumer
    consumer_max_fetch_size=1048576,  # 1MB
    consumer_auto_offset_reset='latest',
    
    # Logging
    logging_config={
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'default': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'nearyou-stream-processor': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'handlers': ['default'],
            },
        }
    }
)

# Import agents dopo la creazione dell'app per evitare circular imports
from .agents import location_agent, notification_agent, analytics_agent

logger.info("Faust app configurata per NearYou stream processing (memory store)")