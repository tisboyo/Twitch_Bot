#!/bin/bash
pip install -r /workspace/requirements-dev.txt
pip install -r /workspace/web/requirements.txt
pre-commit
