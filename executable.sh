#!/bin/bash
set -e

echo "🔹 Apply migrations..."
python manage.py makemigrations
python manage.py migrate

echo "🔹 Start Django server..."
python manage.py runserver 0.0.0.0:3004
