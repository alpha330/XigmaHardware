#!/bin/bash
set -e

echo "========================================="
echo "🚀 Marketplace Backend - Development Mode"
echo "========================================="

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.5
done
echo "✅ PostgreSQL is available!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
    sleep 0.5
done
echo "✅ Redis is available!"

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if needed (for development)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput || true
fi

# Start development server with auto-reload
echo "🔥 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000