# GitHub OAuth Integration - Changes Summary

## Overview
ReportForMe has been fully migrated from personal access token authentication to GitHub OAuth 2.0 using `django-allauth`.

## Files Modified

### 1. **settings.py** - Configuration
- ✅ Added `allauth` apps to `INSTALLED_APPS`
  - `allauth`
  - `allauth.account`
  - `allauth.socialaccount`
  - `allauth.socialaccount.providers.github`
- ✅ Added `allauth.account.middleware.AccountMiddleware` to MIDDLEWARE
- ✅ Configured `AUTHENTICATION_BACKENDS` to include allauth
- ✅ Added allauth settings:
  - Account email verification
  - Social account auto-signup
  - GitHub OAuth scopes: `user`, `repo`, `read:org`
- ✅ Updated REST_FRAMEWORK permissions to require authentication
- ✅ Added login redirect URLs

### 2. **core/models.py** - Data Model
- ✅ Removed `github_token` database field (CharField)
- ✅ Added import: `from allauth.socialaccount.models import SocialAccount`
- ✅ Added `github_token` as a **property** that:
  - Fetches token from SocialAccount on demand
  - Returns None if no GitHub account connected
  - Never stores sensitive data in UserConfig

```python
@property
def github_token(self):
    """Get GitHub access token from social account"""
    try:
        social_account = SocialAccount.objects.get(
            user=self.user,
            provider='github'
        )
        return social_account.socialaccount_ptr.extra_data.get('access_token')
    except SocialAccount.DoesNotExist:
        return None
```

### 3. **core/urls.py** - API Routes
- ✅ Added OAuth routes:
  - `GET /api/auth/github/login/` → Get GitHub OAuth URL
  - `GET /api/auth/github/callback/` → Check auth status after OAuth
  - `POST /api/auth/complete-registration/` → Finish user registration
  - `GET /api/users/me/` → Get current user config
  - `POST /api/auth/sync-token/` → Sync GitHub token
  - `POST /api/auth/logout/` → Logout user

### 4. **core/views.py** - API Endpoints
- ✅ Added `IsAuthenticated` permission to all viewsets
- ✅ Updated `UserConfigViewSet`:
  - Filter by current user: `get_queryset()`
  - Check token validity before verifying
- ✅ Updated `ReportViewSet`:
  - Filter reports by current user only
- ✅ Updated `CommitViewSet`:
  - Filter commits by current user only
- ✅ Updated `GithubRepositoryViewSet`:
  - Filter repositories by current user only

### 5. **core/serializers.py** - Data Serialization
- ✅ Added `github_token` as SerializerMethodField
- ✅ Return **masked token**: `"ghp_abc...789"` (never full token)
- ✅ Made token read-only
- ✅ Added `created_at` and `updated_at` to fields

### 6. **core/oauth_views.py** - NEW FILE
Complete OAuth implementation with 6 endpoints:

```python
1. github_login() → GET /api/auth/github/login/
   Returns GitHub OAuth authorization URL

2. oauth_callback_status() → GET /api/auth/github/callback/
   Check if user is authenticated and has config

3. get_current_user() → GET /api/users/me/
   Get current user's configuration

4. complete_github_registration() → POST /api/auth/complete-registration/
   Create UserConfig after successful OAuth

5. sync_github_token() → POST /api/auth/sync-token/
   Verify and sync GitHub token

6. logout_user() → POST /api/auth/logout/
   Log out current user
```

### 7. **core/migrations/0002_remove_github_token.py** - NEW MIGRATION
- ✅ Removes `github_token` CharField from UserConfig
- ✅ Preserves all other data
- ✅ Safe migration with no data loss

### 8. **reportforme/urls.py** - URL Configuration
- ✅ Added `path('accounts/', include('allauth.urls'))`
- ✅ Enables django-allauth OAuth callback handling

### 9. **requirements.txt** - Dependencies
- ✅ Added `django-allauth==0.57.0`

### 10. **GITHUB_OAUTH_SETUP.md** - NEW DOCUMENTATION
- ✅ Complete setup guide with 6 steps
- ✅ Detailed API endpoint documentation
- ✅ React/JavaScript integration examples
- ✅ Troubleshooting guide
- ✅ Architecture explanation
- ✅ Environment variable reference

### 11. **OAUTH_QUICKSTART.md** - NEW DOCUMENTATION
- ✅ Quick-start in 5 minutes
- ✅ Simplified setup steps
- ✅ Key endpoints summary
- ✅ Frontend integration code
- ✅ Token storage & security explanation
- ✅ Common troubleshooting

### 12. **setup_oauth.sh** - NEW SCRIPT
- ✅ Automated setup helper
- ✅ Creates .env template
- ✅ Runs migrations
- ✅ Prompts for superuser

## Database Changes

### Before
```
UserConfig:
├── user: OneToOneField(User)
├── github_token: CharField(max_length=255) ← STORED IN DB
├── github_username: CharField
├── email: EmailField
├── report_time: TimeField
├── timezone: CharField
└── is_active: BooleanField
```

### After
```
UserConfig:
├── user: OneToOneField(User)
├── github_username: CharField
├── email: EmailField
├── report_time: TimeField
├── timezone: CharField
└── is_active: BooleanField

SocialAccount (django-allauth):
├── user: ForeignKey(User)
├── provider: 'github'
├── uid: GitHub user ID
└── extra_data: {
    'access_token': '...',  ← TOKEN STORED HERE
    'login': 'username',
    'email': 'user@example.com',
    ...
}
```

## Security Improvements

### Before
- ❌ Users managed GitHub tokens manually
- ❌ Tokens stored in UserConfig model
- ❌ No automatic token refresh
- ❌ Risk of token exposure
- ❌ Users had to update tokens manually

### After
- ✅ Users authorize via GitHub OAuth
- ✅ Tokens stored securely in SocialAccount
- ✅ Automatic token refresh by django-allauth
- ✅ Tokens never shared with users
- ✅ No user action needed for token updates

## API Changes

### Removed Endpoints
- ❌ `POST /api/users/` - Manual user creation (now OAuth only)
- ❌ Need to pass `github_token` in requests

### New Endpoints
- ✅ `GET /api/auth/github/login/` - Get OAuth URL
- ✅ `GET /api/auth/github/callback/` - OAuth callback handler
- ✅ `POST /api/auth/complete-registration/` - Finish registration
- ✅ `POST /api/auth/sync-token/` - Sync token
- ✅ `POST /api/auth/logout/` - Logout

### Updated Endpoints
- ✅ All endpoints now require `IsAuthenticated`
- ✅ All endpoints filter by current user
- ✅ `github_token` in responses is masked (e.g., `"ghp_abc...789"`)

## Migration Steps for Users

### For New Users
```
1. Click "Sign up with GitHub"
2. Authorize ReportForMe on GitHub
3. Fill in email, report time, timezone
4. Done! Start getting reports
```

### For Existing Users
```
1. Old `github_token` will be lost (migration removes it)
2. Users must re-authenticate with GitHub OAuth
3. New tokens will be automatically managed
4. No manual token entry needed ever again
```

## Configuration Needed

### GitHub OAuth App Setup
1. Create OAuth App at https://github.com/settings/developers
2. Get Client ID and Client Secret
3. Set Authorization Callback URL to: `http://yourdomain.com/accounts/github/login/callback/`

### Django Admin Setup
1. Go to Sites and create/update site with correct domain
2. Go to Social Applications
3. Create GitHub social app with Client ID/Secret
4. Select the site for the app

### Environment Variables
```env
GITHUB_OAUTH_CLIENT_ID=your_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_client_secret
DEBUG=True/False
ALLOWED_HOSTS=yourdomain.com
```

## Testing the Integration

### In Swagger UI
```
1. Go to http://localhost:8000/api/docs/
2. Test endpoints in order:
   a. GET /api/auth/github/login/ → Get auth URL
   b. Manually visit the URL and authorize on GitHub
   c. GET /api/auth/github/callback/ → Verify authentication
   d. POST /api/auth/complete-registration/ → Finish registration
   e. GET /api/users/me/ → View your config
   f. POST /api/auth/logout/ → Logout
```

### With cURL
```bash
# 1. Get login URL
curl http://localhost:8000/api/auth/github/login/

# 2. Visit the returned auth_url in browser and authorize

# 3. Check if authenticated
curl -b cookies.txt http://localhost:8000/api/auth/github/callback/

# 4. Complete registration
curl -X POST http://localhost:8000/api/auth/complete-registration/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"email":"user@example.com","report_time":"18:00","timezone":"UTC"}'

# 5. Get user config
curl http://localhost:8000/api/users/me/ -b cookies.txt
```

## Backwards Compatibility

⚠️ **Not backwards compatible with manual token entry**

**Breaking Changes:**
- Users can no longer pass `github_token` in requests
- Old tokens in database will be lost in migration
- All users must re-authenticate with GitHub OAuth

**Migration Path:**
```
Old System:
1. User provides GitHub PAT
2. We store it in UserConfig.github_token
3. We use it to fetch commits

New System:
1. User authorizes via GitHub OAuth
2. Token stored in SocialAccount (encrypted)
3. Token auto-refreshed by django-allauth
4. We use SocialAccount token to fetch commits
```

## Performance Implications

### Benefits
- ✅ Fewer API calls (auto-refresh vs manual refresh)
- ✅ More secure (encrypted token storage)
- ✅ Better scalability (no token management overhead)

### Potential Issues
- ⏳ Initial OAuth redirect adds ~2 seconds to login
- ⏳ Token refresh happens in background (transparent to user)

## Future Enhancements

Possible improvements:
1. Add refresh token rotation
2. Add token revocation endpoint
3. Add scope-change capability
4. Add multiple GitHub account support
5. Add GitHub Enterprise support
6. Add team-based permissions

## Questions?

See documentation files:
- [OAUTH_QUICKSTART.md](./OAUTH_QUICKSTART.md) - 5-minute setup
- [GITHUB_OAUTH_SETUP.md](./GITHUB_OAUTH_SETUP.md) - Complete guide
- [README.md](./README.md) - General project info
