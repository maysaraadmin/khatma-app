# Setting Up Google OAuth for Khatma App

This guide will walk you through the process of setting up Google OAuth for your Khatma App to enable Google login functionality.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click on "New Project"
4. Enter "Khatma App" as the project name
5. Click "Create"

## Step 2: Enable the Google OAuth API

1. Select your newly created project
2. In the left sidebar, navigate to "APIs & Services" > "Library"
3. Search for "Google OAuth2 API" or "Google+ API"
4. Click on the API and then click "Enable"

## Step 3: Configure the OAuth Consent Screen

1. In the left sidebar, navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" as the user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required information:
   - App name: "Khatma App"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. Under "Scopes", click "Add or Remove Scopes"
7. Add the following scopes:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
8. Click "Save and Continue"
9. Add any test users if you're in testing mode
10. Click "Save and Continue"
11. Review your settings and click "Back to Dashboard"

## Step 4: Create OAuth Client ID

1. In the left sidebar, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "OAuth client ID"
3. Select "Web application" as the application type
4. Name: "Khatma Web App"
5. Authorized JavaScript origins: Add `http://localhost:8000`
6. Authorized redirect URIs: Add `http://localhost:8000/accounts/google/login/callback/`
7. Click "Create"
8. A popup will appear with your client ID and client secret. Save these values.

## Step 5: Configure Django-allauth with Google OAuth Credentials

1. In the Django admin interface, go to http://localhost:8000/admin/
2. Log in with your superuser credentials
3. Navigate to "Sites" and click on the existing site (usually "example.com")
4. Change the domain name to `localhost:8000` and the display name to "Khatma App"
5. Click "Save"
6. Navigate to "Social applications" under the "Social Accounts" section
7. Click "Add social application"
8. Fill in the following details:
   - Provider: Select "Google"
   - Name: "Google OAuth"
   - Client ID: Paste your Google client ID
   - Secret key: Paste your Google client secret
   - Sites: Move "Khatma App (localhost:8000)" from "Available sites" to "Chosen sites"
9. Click "Save"

## Step 6: Test Google Login

1. Go to http://localhost:8000/accounts/login/
2. Click on the "Google" button
3. You should be redirected to Google's login page
4. After logging in with your Google account, you should be redirected back to your app and logged in

## Troubleshooting

If you encounter any issues:

1. **Redirect URI mismatch**: Make sure the redirect URI in your Google Cloud Console matches exactly with the callback URL in your Django app.
2. **Domain verification**: For production use, you may need to verify your domain ownership.
3. **Scope issues**: Ensure you've enabled the correct scopes in the OAuth consent screen.
4. **Site configuration**: Make sure your Site model in Django has the correct domain name.

## Production Deployment

For production deployment:

1. Add your production domain to the authorized JavaScript origins and redirect URIs in the Google Cloud Console
2. Update the Site model in your Django admin to use your production domain
3. If you're using HTTPS (which you should), make sure all URLs use https://
