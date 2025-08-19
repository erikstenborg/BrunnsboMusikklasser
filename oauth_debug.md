# Google OAuth 403 Debug Guide - ISSUE FOUND!

## PROBLEM IDENTIFIED
The first URL in Google Console is TRUNCATED!

**Current (WRONG) in Google Console:**
- URL 1: `https://cc4f1f99-b283-44db-b27f-f4de7d33dcc2-00-1c1tcbympt7hl.rik` ❌ TRUNCATED!
- URL 2: `https://brunnsbomusikklasser.replit.app/auth/google_callback` ✅ Correct

**Should be (CORRECT):**
- URL 1: `https://cc4f1f99-b283-44db-b27f-f4de7d33dcc2-00-1c1tcbympt7hl.riker.replit.dev/auth/google_callback`
- URL 2: `https://brunnsbomusikklasser.replit.app/auth/google_callback`

## Debug Steps
1. **Check Google Cloud Console**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Find your OAuth 2.0 Client ID
   - Verify "Authorized redirect URIs" contains EXACTLY:
     ```
     https://cc4f1f99-b283-44db-b27f-f4de7d33dcc2-00-1c1tcbympt7hl.riker.replit.dev/auth/google_callback
     https://brunnsbomusikklasser.replit.app/auth/google_callback
     ```

2. **Test the OAuth Flow**:
   - Click "Continue with Google" in your app
   - Check the console logs for debug information
   - Compare the logged redirect_uri with Google Console settings

3. **Common Issues**:
   - Trailing slash differences (`/callback` vs `/callback/`)
   - HTTP vs HTTPS mismatch
   - Wrong domain (make sure it's the current Replit domain)
   - Typos in the URL
   - Using old/cached OAuth credentials

## If Still Getting 403:
- Double-check both Client ID and Secret are from the SAME OAuth application
- Make sure you saved changes in Google Console
- Wait 1-2 minutes after saving changes
- Try clearing browser cache/cookies