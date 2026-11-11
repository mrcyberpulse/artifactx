#!/usr/bin/env sh
set -e

echo "ArtifactX backend: running database migrations..."
alembic upgrade head

echo "ArtifactX backend: starting application..."
exec "$@"
