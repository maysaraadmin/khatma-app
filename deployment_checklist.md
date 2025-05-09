# Deployment Checklist

This document provides a checklist for deploying the Khatma app to staging and production environments.

## Pre-Deployment Checklist

- [ ] Run all tests and ensure they pass
- [ ] Check for any pending migrations
- [ ] Update the requirements.txt file with any new dependencies
- [ ] Update the .env file with the appropriate settings
- [ ] Collect static files
- [ ] Check for any security vulnerabilities
- [ ] Backup the database

## Staging Deployment Checklist

1. **Prepare for Deployment**
   - [ ] Run `python prepare_deployment.py staging`
   - [ ] Verify that all static files are collected
   - [ ] Verify that all migrations are applied
   - [ ] Check that the Procfile is set to use the staging settings

2. **Deploy to Staging Server**
   - [ ] Push changes to the staging branch
   - [ ] Run `./deploy_staging.sh` on the staging server
   - [ ] Verify that the app is running correctly
   - [ ] Check logs for any errors

3. **Post-Deployment Testing**
   - [ ] Test all major features
   - [ ] Test user authentication
   - [ ] Test Khatma creation and management
   - [ ] Test Quran reading features
   - [ ] Test group features
   - [ ] Test notification system
   - [ ] Test chat functionality
   - [ ] Test on different devices and browsers

## Production Deployment Checklist

1. **Prepare for Deployment**
   - [ ] Run `python prepare_deployment.py production`
   - [ ] Verify that all static files are collected
   - [ ] Verify that all migrations are applied
   - [ ] Check that the Procfile is set to use the production settings

2. **Deploy to Production Server**
   - [ ] Push changes to the main branch
   - [ ] Run `./deploy_production.sh` on the production server
   - [ ] Verify that the app is running correctly
   - [ ] Check logs for any errors

3. **Post-Deployment Testing**
   - [ ] Test all major features
   - [ ] Test user authentication
   - [ ] Test Khatma creation and management
   - [ ] Test Quran reading features
   - [ ] Test group features
   - [ ] Test notification system
   - [ ] Test chat functionality
   - [ ] Test on different devices and browsers

4. **Post-Deployment Monitoring**
   - [ ] Monitor server performance
   - [ ] Monitor database performance
   - [ ] Monitor error logs
   - [ ] Monitor user activity
   - [ ] Set up alerts for critical errors

## Rollback Procedure

If deployment fails or critical issues are found after deployment, follow these steps to rollback:

1. **Identify the Issue**
   - [ ] Check error logs
   - [ ] Identify the cause of the issue

2. **Rollback to Previous Version**
   - [ ] Restore the database from backup
   - [ ] Deploy the previous version of the code
   - [ ] Verify that the app is running correctly

3. **Post-Rollback Actions**
   - [ ] Notify users of the rollback
   - [ ] Fix the issue in a development environment
   - [ ] Test the fix thoroughly before redeploying
