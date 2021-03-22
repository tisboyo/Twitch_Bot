#!/usr/bin/env bash
echo "Updating database..."
python alembic_update.py

#Added in #151
echo "Updating Trivia..."
python import_trivia.py

echo "Starting Bot..."
python main.py
