#!/bin/sh
set -eu

wait_for_service() {
    host="$1"
    port="$2"
    service="$3"

    echo "Waiting for ${service} at ${host}:${port}..."
    python - "$host" "$port" "$service" "${SERVICE_WAIT_TIMEOUT:-60}" <<'PY'
import socket
import sys
import time

host, port, service, timeout = sys.argv[1], int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
deadline = time.monotonic() + timeout
last_error = None

while time.monotonic() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"{service} is ready.")
            raise SystemExit(0)
    except OSError as exc:
        last_error = exc
        time.sleep(1)

print(f"{service} is unavailable after {timeout:g}s: {last_error}", file=sys.stderr)
raise SystemExit(1)
PY
}

cd "${APP_DIR:-/app}"
if [ ! -f manage.py ]; then
    echo "manage.py not found in $(pwd). Check the backend bind mount/build context." >&2
    exit 127
fi

wait_for_service "${DB_HOST:-postgres}" "${DB_PORT:-5432}" "PostgreSQL"
wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis"

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    python manage.py migrate --noinput
fi

exec "$@"
