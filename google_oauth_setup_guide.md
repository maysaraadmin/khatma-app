# Setting Up Google OAuth for Khatma App

This guide will walk you through the process of setting up Google OAuth for the Khatma App.

## Step 1: Create a Google OAuth Client ID and Secret

1. Go to the Google Developer Console: https://console.developers.google.com/
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"

### Configure the OAuth consent screen:
- User Type: External
- App name: Khatma App
- User support email: Your email
- Developer contact information: Your email
- Authorized domains: localhost (for development)

### Create OAuth client ID:
- Application type: Web application
- Name: Khatma App
- Authorized JavaScript origins: 
  - http://localhost:8000
  - http://127.0.0.1:8000
- Authorized redirect URIs: 
  - http://localhost:8000/accounts/google/login/callback/
  - http://127.0.0.1:8000/accounts/google/login/callback/

5. Click "Create" and note down the Client ID and Client Secret

## Step 2: Add the Google OAuth Credentials to the Khatma App

### Option 1: Using the Admin Interface
1. Go to http://localhost:8000/admin/
2. Navigate to "Social Accounts" > "Social applications"
3. Click "Add social application"
4. Fill in the form:
   - Provider: Google
   - Name: Google
   - Client ID: [Your Google Client ID]
   - Secret key: [Your Google Client Secret]
   - Sites: Add localhost:8000 (or your domain)
5. Click "Save"

### Option 2: Using the Script
Run the provided script with your Google OAuth credentials:

```bash
python add_google_oauth.py <client_id> <client_secret>
```

## Step 3: Test the Google Authentication

1. Go to http://127.0.0.1:8000/users/register/
2. Click on "التسجيل باستخدام Google"
3. You should be redirected to Google's login page
4. After logging in with your Google account, you should be redirected back to the Khatma App

## Troubleshooting

### Redirect URI Mismatch
If you see an error about the redirect URI not matching, make sure you've added the correct redirect URIs to your Google OAuth client:
- http://localhost:8000/accounts/google/login/callback/
- http://127.0.0.1:8000/accounts/google/login/callback/

### Invalid Client ID or Secret
If you see an error about an invalid client ID or secret, make sure you've copied them correctly from the Google Developer Console.

### Site Configuration
Make sure your site is configured correctly in the Django admin:
1. Go to http://localhost:8000/admin/sites/site/
2. Edit the default site to match your domain (e.g., localhost:8000)
