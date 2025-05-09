#!/bin/bash

# Deployment script for production environment

# Exit on error
set -e

echo "Deploying to production environment..."

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --settings=khatma.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=khatma.settings_production

# Restart the application
touch khatma/wsgi_production.py

echo "Deployment to production environment completed successfully!"
