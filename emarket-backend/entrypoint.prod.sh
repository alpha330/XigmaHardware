#!/bin/sh
set -eu

wait_for_service() {
    host="$1"
    port="$2"
    service="$3"
    attempts=0

    echo "Waiting for ${service} at ${host}:${port}..."
    until nc -z "$host" "$port"; do
        attempts=$((attempts + 1))
        if [ "$attempts" -ge 30 ]; then
            echo "${service} is unavailable after 30 attempts."
            exit 1
        fi
        sleep 2
    done
}

wait_for_service "${DB_HOST:-postgres}" "${DB_PORT:-5432}" "PostgreSQL"
wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput --clear
fi

exec "$@"
