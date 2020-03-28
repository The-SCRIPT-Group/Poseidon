#!/usr/bin/env bash

# shellcheck disable=SC1091

[[ -d "venv" ]] || python3.8 -m venv ./venv
source venv/bin/activate
source .env
export TELEGRAM_API_KEY TELEGRAM_CHAT_ID
pip install -r requirements.txt
gunicorn api:app -b :5501 --workers=$(nproc)
