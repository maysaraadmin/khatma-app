# Fixing the "redirect_uri_mismatch" Error in Google OAuth

The "redirect_uri_mismatch" error occurs when the redirect URI in your Google OAuth configuration doesn't match the one expected by django-allauth. Here's how to fix it:

## Step 1: Check the Exact Callback URL Used by Django-allauth

The callback URL used by django-allauth for Google authentication is:

```
http://127.0.0.1:8000/accounts/google/login/callback/
```

Note that this URL uses `127.0.0.1` instead of `localhost`. Both are technically the same, but Google OAuth treats them as different domains.

## Step 2: Update Your Google OAuth Configuration

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Credentials"
4. Find your OAuth 2.0 Client ID and click on it to edit
5. Under "Authorized redirect URIs", make sure you have the following URL:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
6. If you only have `http://localhost:8000/accounts/google/login/callback/`, add the 127.0.0.1 version as well
7. Click "Save"

## Step 3: Add Both Versions of the Domain

For maximum compatibility, add both versions of the redirect URI:

1. `http://127.0.0.1:8000/accounts/google/login/callback/`
2. `http://localhost:8000/accounts/google/login/callback/`

This ensures that regardless of which domain you use to access your application, the Google OAuth flow will work.

## Step 4: Update the JavaScript Origins

Similarly, update the "Authorized JavaScript origins" to include both:

1. `http://127.0.0.1:8000`
2. `http://localhost:8000`

## Step 5: Wait for Changes to Propagate

After making these changes, it may take a few minutes for them to propagate through Google's systems. Wait a few minutes before trying again.

## Step 6: Clear Your Browser Cache

Sometimes, your browser may cache OAuth-related information. Clear your browser cache and cookies before trying again.

## Step 7: Try the Google Login Again

Now try logging in with Google again. The error should be resolved.

## Additional Troubleshooting

If you're still experiencing issues:

1. **Double-check the URL format**: Make sure there are no extra spaces or characters in the redirect URI.
2. **Check the protocol**: Ensure you're using `http://` and not `https://` for local development.
3. **Verify the client ID and secret**: Make sure the client ID and secret in your Django application match the ones in the Google Cloud Console.
4. **Check the consent screen configuration**: Make sure your OAuth consent screen is properly configured.

## For Production Deployment

When deploying to production:

1. Add your production domain to the authorized redirect URIs (e.g., `https://yourdomain.com/accounts/google/login/callback/`)
2. Add your production domain to the authorized JavaScript origins (e.g., `https://yourdomain.com`)
3. Update the Site model in your Django admin to use your production domain
