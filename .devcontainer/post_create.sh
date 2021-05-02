#!/bin/bash
pip install -r /workspace/requirements-dev.txt -r /workspace/bot/requirements.txt -r /workspace/web/requirements.txt
pre-commit
