#!/usr/bin/env bash
echo "Updating database..."
python alembic_update.py

echo "Starting Bot..."
python main.py
