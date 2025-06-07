"""
Definizione dei topic Kafka per Faust.
"""
from ..app import app
from ..models.events import (
    LocationEvent, ShopProximityEvent, 
    NotificationEvent, AnalyticsEvent
)

# Topic input dal producer esistente
location_events_topic = app.topic(
    'gps_stream',
    value_type=LocationEvent,
    partitions=4,
    replicas=1,
)

# Topic interni per processing
shop_proximity_topic = app.topic(
    'shop_proximity_events',
    value_type=ShopProximityEvent,
    partitions=4,
    replicas=1,
)

notification_events_topic = app.topic(
    'notification_events',
    value_type=NotificationEvent,
    partitions=4,
    replicas=1,
)

analytics_events_topic = app.topic(
    'analytics_events',
    value_type=AnalyticsEvent,
    partitions=2,
    replicas=1,
)