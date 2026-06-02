#!/bin/bash
set -e

echo "========================================="
echo "🔴 Marketplace Backend - PRODUCTION"
echo "========================================="
echo ""

wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service..."
    while ! nc -z $host $port; do
        if [ $attempt -ge $max_attempts ]; then
            echo "❌ $service not available after $max_attempts attempts"
            exit 1
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    echo "✅ $service is ready!"
}

# Wait for critical services
wait_for_service ${DB_HOST} ${DB_PORT:-5432} "PostgreSQL"
wait_for_service ${REDIS_HOST} ${REDIS_PORT:-6379} "Redis"

echo ""
echo "📦 Running database migrations..."
python manage.py migrate --noinput

echo "🔍 Verifying migrations..."
python manage.py showmigrations --plan | grep -q "\[ \]" && {
    echo "❌ CRITICAL: Unapplied migrations found!"
    exit 1
} || echo "✅ All migrations verified!"

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗜️ Compressing static assets..."
python manage.py compress --force 2>/dev/null || true

echo "🧹 Clearing old cache..."
python manage.py clear_cache 2>/dev/null || true

echo "🔄 Warming up application..."
curl -s http://localhost:8000/health/ > /dev/null 2>&1 || true

echo ""
echo "🔴 Starting Gunicorn (Production Mode)..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-4} \
    --worker-class gthread \
    --worker-connections 1000 \
    --max-requests 10000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level warning \
    --preload \
    --pid /tmp/gunicorn.pid