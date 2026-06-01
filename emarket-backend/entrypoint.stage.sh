#!/bin/bash
set -e

echo "========================================="
echo "🔶 Marketplace Backend - Staging Mode"
echo "========================================="

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
done
echo "✅ PostgreSQL is available!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
    sleep 1
done
echo "✅ Redis is available!"

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Compile messages (if using translations)
echo "🌍 Compiling translation messages..."
python manage.py compilemessages 2>/dev/null || true

# Start Gunicorn with staging config
echo "🔶 Starting Gunicorn (Staging)..."
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info