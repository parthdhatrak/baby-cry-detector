#!/usr/bin/env bash
# Build script for Render.com deployment
# This script runs during the build phase

set -o errexit  # Exit on error

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate --no-input
