#!/bin/bash
# Install dependencies using uv or pip with --break-system-packages (for Vercel build container)
uv pip install -r requirements.txt --system 2>/dev/null || python3 -m pip install -r requirements.txt --break-system-packages

python3 manage.py migrate --noinput
python3 seed_data.py
python3 manage.py collectstatic --noinput --clear
