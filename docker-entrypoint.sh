#!/bin/sh
set -e

# Target database path (from environment or default)
TARGET_DB="${DB_PATH:-/app/data/gpat_knowledge.db}"
SEED_DB="/app/seed/gpat_knowledge.db"
TARGET_DIR=$(dirname "$TARGET_DB")
BACKUP_PATH="${BACKUP_DIR:-/app/data/backups}"

mkdir -p "$TARGET_DIR"
mkdir -p "$BACKUP_PATH"

# Ensure database exists in persistent volume without ever overwriting existing learner data
if [ ! -f "$TARGET_DB" ]; then
    if [ -f "$SEED_DB" ]; then
        echo "[Entrypoint] Initializing persistent database volume from packaged seed database..."
        cp "$SEED_DB" "$TARGET_DB"
    else
        echo "[Entrypoint] ERROR: Target database not found and no seed database available at $SEED_DB."
        exit 1
    fi
else
    echo "[Entrypoint] Found existing persistent database at $TARGET_DB. Preserving all learner history."
fi

# Set proper permissions
chmod 644 "$TARGET_DB" || true

# Execute uvicorn server
echo "[Entrypoint] Starting GPAT 2027 Learning OS backend on port ${PORT:-8000}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
