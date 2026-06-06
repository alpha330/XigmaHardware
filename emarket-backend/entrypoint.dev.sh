#!/bin/bash
set -e

echo "========================================="
echo "🚀 Marketplace Backend - DEVELOPMENT"
echo "========================================="
echo ""

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do sleep 0.5; done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do sleep 0.5; done
echo "✅ Redis is ready!"

# Wait for MailHog
echo "⏳ Waiting for MailHog..."
while ! nc -z ${EMAIL_HOST:-mailhog} ${EMAIL_SMTP_PORT:-1025}; do sleep 0.5; done
echo "✅ MailHog is ready!"

echo ""
echo "📦 Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "🔥 Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000