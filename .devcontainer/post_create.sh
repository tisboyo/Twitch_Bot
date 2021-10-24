#!/bin/bash
pip install -r /workspace/requirements-dev.txt -r /workspace/bot/requirements.txt -r /workspace/web/requirements.txt
pre-commit
sudo ln /home/twitch_bot/.local/bin/black /usr/local/bin/black
