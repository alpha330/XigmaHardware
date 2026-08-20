#!/bin/sh
set -eu

wait_for_service() {
    host="$1"
    port="$2"
    service="$3"

    echo "Waiting for ${service} at ${host}:${port}..."
    until nc -z "$host" "$port"; do
        sleep 1
    done
}

wait_for_service "${DB_HOST:-postgres}" "${DB_PORT:-5432}" "PostgreSQL"
wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    python manage.py migrate --noinput
fi

exec "$@"
