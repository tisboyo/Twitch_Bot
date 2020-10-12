#!/bin/bash
cd /workspace/bot/
pipenv install --dev --system --deploy
pre-commit
