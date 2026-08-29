#!/bin/bash

# Script to switch between development, staging, and production environments

# Exit on error
set -e

# Check if environment argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [development|staging|production]"
    exit 1
fi

# Get environment from argument
ENV=$1

# Switch environment
case $ENV in
    development)
        echo "Switching to development environment..."
        cp Procfile.development Procfile
        sed -i 's/^DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=khatma.settings/' .env
        sed -i 's/^DJANGO_DEBUG=.*/DJANGO_DEBUG=True/' .env
        sed -i 's/^DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1/' .env
        sed -i 's/^SITE_DOMAIN=.*/SITE_DOMAIN=localhost:8000/' .env
        echo "Switched to development environment."
        ;;
    staging)
        echo "Switching to staging environment..."
        cp Procfile.staging Procfile
        sed -i 's/^DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=khatma.settings_staging/' .env
        sed -i 's/^DJANGO_DEBUG=.*/DJANGO_DEBUG=False/' .env
        sed -i 's/^DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=staging.khatma-app.com,staging-khatma-app.herokuapp.com/' .env
        sed -i 's/^SITE_DOMAIN=.*/SITE_DOMAIN=staging.khatma-app.com/' .env
        echo "Switched to staging environment."
        ;;
    production)
        echo "Switching to production environment..."
        cp Procfile.production Procfile
        sed -i 's/^DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=khatma.settings_production/' .env
        sed -i 's/^DJANGO_DEBUG=.*/DJANGO_DEBUG=False/' .env
        sed -i 's/^DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=khatma-app.com,www.khatma-app.com,khatma-app.herokuapp.com/' .env
        sed -i 's/^SITE_DOMAIN=.*/SITE_DOMAIN=khatma-app.com/' .env
        echo "Switched to production environment."
        ;;
    *)
        echo "Invalid environment: $ENV"
        echo "Usage: $0 [development|staging|production]"
        exit 1
        ;;
esac

echo "Environment switched to $ENV."
