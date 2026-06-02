#!/bin/bash
set -e

echo "========================================="
echo "🚀 Marketplace Backend - DEVELOPMENT"
echo "========================================="
echo "Environment: ${RUN_AS:-dev}"
echo "Settings: ${DJANGO_SETTINGS_MODULE:-config.settings.dev}"
echo ""

# Function to check service availability
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3

    echo "⏳ Waiting for $service ($host:$port)..."
    while ! nc -z $host $port; do
        sleep 0.5
    done
    echo "✅ $service is ready!"
}

# Wait for services
wait_for_service ${DB_HOST:-postgres} ${DB_PORT:-5432} "PostgreSQL"
wait_for_service ${REDIS_HOST:-redis} ${REDIS_PORT:-6379} "Redis"
wait_for_service ${EMAIL_HOST:-mailhog} ${EMAIL_SMTP_PORT:-1025} "MailHog"

echo ""
echo "📦 Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser for development
if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        mobile='09123456789',
        password='Admin123!@#',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created!')
" || true
fi

echo ""
echo "🔥 Starting Django development server..."
echo "📚 API Documentation: http://localhost:${BACKEND_PORT:-8000}/swagger/"
echo "📧 MailHog Interface: http://localhost:${MAILHOG_UI_PORT:-8025}/"
echo "🌸 Flower: http://localhost:${FLOWER_PORT:-5555}/"
echo ""

exec python manage.py runserver 0.0.0.0:${BACKEND_PORT:-8000}