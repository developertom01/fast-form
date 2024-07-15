#! /bin/sh

set -e

echo "Running production server ..."

export APP_ENV="production"

echo "Running table migrations ..."

#Run migrations
python3 scripts/migrate_db_tables.py

echo "Starting server ..."
fastapi run server.py #Start production instance