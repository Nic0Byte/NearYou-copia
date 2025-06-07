#!/bin/bash
set -e

echo "=== Avvio Faust Stream Processor ==="

# Attendi che le dipendenze siano pronte
echo "Attendo Kafka..."
while ! nc -z kafka 9093; do
  echo "Kafka non ancora pronto..."
  sleep 2
done
echo "✓ Kafka pronto"

echo "Attendo ClickHouse..."
while ! nc -z clickhouse-server 9000; do
  echo "ClickHouse non ancora pronto..."
  sleep 2
done
echo "✓ ClickHouse pronto"

echo "Attendo PostgreSQL..."
while ! nc -z postgres-postgis 5432; do
  echo "PostgreSQL non ancora pronto..."
  sleep 2
done
echo "✓ PostgreSQL pronto"

echo "Attendo Message Generator..."
while ! nc -z message-generator 8001; do
  echo "Message Generator non ancora pronto..."
  sleep 2
done
echo "✓ Message Generator pronto"

echo "Tutte le dipendenze sono pronte. Avvio Faust worker..."

# Avvia Faust worker
exec faust -A src.stream_processing.app worker --loglevel=info --web-host=0.0.0.0 --web-port=8002