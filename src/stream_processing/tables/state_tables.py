"""
Tabelle di stato per Faust stream processing.
"""
from ..app import app
from ..models.state import UserState, ShopStats, SystemStats

# Tabella stato utenti
user_states_table = app.Table(
    'user_states',
    default=UserState,
    partitions=4,
    help='Stato corrente di ogni utente'
)

# Tabella statistiche negozi
shop_stats_table = app.Table(
    'shop_stats',
    default=ShopStats,
    partitions=2,
    help='Statistiche per ogni negozio'
)

# Tabella statistiche sistema
system_stats_table = app.Table(
    'system_stats',
    default=SystemStats,
    help='Statistiche aggregate di sistema'
)