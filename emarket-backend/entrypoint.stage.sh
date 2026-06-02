#!/bin/bash
set -e

echo "========================================="
echo "🔶 Marketplace Backend - STAGING"
echo "========================================="
echo ""

wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    
    echo "⏳ Waiting for $service..."
    while ! nc -z $host $port; do
        sleep 1
    done
    echo "✅ $service is ready!"
}

wait_for_service ${DB_HOST} ${DB_PORT:-5432} "PostgreSQL"
wait_for_service ${REDIS_HOST} ${REDIS_PORT:-6379} "Redis"

echo ""
echo "📦 Running database migrations..."
python manage.py migrate --noinput

echo "🔍 Checking for unapplied migrations..."
python manage.py showmigrations --plan | grep -q "\[ \]" && {
    echo "❌ ERROR: Unapplied migrations found!"
    exit 1
} || echo "✅ All migrations applied!"

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🌍 Compiling translations..."
python manage.py compilemessages 2>/dev/null || true

echo ""
echo "🔶 Starting Gunicorn (Staging Mode)..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --worker-class gthread \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance