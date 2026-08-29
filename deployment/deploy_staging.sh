#!/bin/bash

# Deployment script for staging environment

# Exit on error
set -e

echo "Deploying to staging environment..."

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --settings=khatma.settings_staging

# Collect static files
python manage.py collectstatic --noinput --settings=khatma.settings_staging

# Restart the application
touch khatma/wsgi_staging.py

echo "Deployment to staging environment completed successfully!"
