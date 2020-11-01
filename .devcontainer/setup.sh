#!/bin/bash
cd /workspace/bot/
pipenv install --dev --system --deploy
pre-commit
cd /workspace/web/
pipenv install --dev --system --deploy
