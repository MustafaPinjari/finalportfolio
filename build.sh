#!/usr/bin/env bash
# exit on error
set -o errexit

# Use the deployment-specific requirements file
pip install -r requirements-render.txt

python manage.py collectstatic --no-input
python manage.py migrate
