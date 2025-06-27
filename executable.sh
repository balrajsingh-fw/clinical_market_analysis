#!/bin/bash
set -e

echo "🔹 Apply migrations..."
python manage.py makemigrations
python manage.py migrate

python import_script.py

echo "🔹 Start Django server..."
python manage.py runserver 0.0.0.0:8042
