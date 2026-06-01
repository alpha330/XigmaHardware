#!/bin/bash
set -e

echo "========================================="
echo "🔴 Marketplace Backend - Production Mode"
echo "========================================="

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 2
done
echo "✅ PostgreSQL is available!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
    sleep 2
done
echo "✅ Redis is available!"

# Run database migrations with safety check
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Verify migrations
echo "🔍 Checking for unapplied migrations..."
python manage.py showmigrations --plan | grep -q "\[ \]" && {
    echo "❌ There are unapplied migrations!"
    exit 1
} || echo "✅ All migrations applied!"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Compress static files (if using django-compressor)
echo "🗜️ Compressing static files..."
python manage.py compress --force 2>/dev/null || true

# Clear cache
echo "🧹 Clearing cache..."
python manage.py clear_cache 2>/dev/null || true

# Start Gunicorn with production config
echo "🔴 Starting Gunicorn (Production)..."
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 4 \
    --worker-class gthread \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level warning \
    --preload