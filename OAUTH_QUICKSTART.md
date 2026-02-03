# GitHub OAuth Integration - Quick Start

## What Changed?
- ✅ **No more personal access tokens!** Users authenticate via GitHub OAuth
- ✅ **Automatic token management** - Django-allauth handles token refresh
- ✅ **Seamless registration** - Users authorize once, we handle the rest
- ✅ **Better security** - No tokens in user's hands, stored securely

## Setup Steps (5 minutes)

### Step 1: Create GitHub OAuth App
1. Go to https://github.com/settings/developers
2. Click "OAuth Apps" → "New OAuth App"
3. Fill in:
   - **Application name**: ReportForMe
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:8000/accounts/github/login/callback/`
4. Copy **Client ID** and **Client Secret**

### Step 2: Create `.env` File
Create `.env` in project root:
```env
GITHUB_OAUTH_CLIENT_ID=your_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_client_secret
DEBUG=True
```

### Step 3: Run Django Setup
```bash
# Create superuser
python manage.py createsuperuser

# Go to admin
# http://localhost:8000/admin/

# Add Site (Sites section)
# - Domain: localhost:8000
# - Name: ReportForMe

# Add Social Application (Social applications section)
# - Provider: GitHub
# - Name: GitHub OAuth
# - Client id: [paste from step 1]
# - Secret key: [paste from step 1]
# - Sites: Select your site
```

### Step 4: Start Server
```bash
python manage.py runserver
```

## API Flow

### Registration (New User)
```
1. User clicks "Sign up with GitHub"
   GET /api/auth/github/login/
   
2. Frontend redirects to GitHub OAuth URL
   
3. User authorizes on GitHub
   
4. GitHub redirects to: /accounts/github/login/callback/
   (handled by django-allauth automatically)
   
5. User is now authenticated
   
6. Frontend calls:
   POST /api/auth/complete-registration/
   {
     "email": "user@example.com",
     "report_time": "18:00",
     "timezone": "America/New_York"
   }
   
7. UserConfig is created with OAuth token
```

### Login (Existing User)
```
1. User clicks "Login with GitHub"
   GET /api/auth/github/login/
   
2. Frontend redirects to GitHub OAuth URL
   
3. User authorizes on GitHub (may be automatic if already authorized)
   
4. GitHub redirects to: /accounts/github/login/callback/
   
5. User is logged in with new/refreshed token
```

## Key API Endpoints

### Get Login URL
```http
GET /api/auth/github/login/
```
Returns GitHub OAuth authorization URL

### Check Auth Status
```http
GET /api/auth/github/callback/
```
Returns: `{authenticated, has_config, username, email}`

### Complete Registration
```http
POST /api/auth/complete-registration/
Content-Type: application/json

{
  "email": "user@example.com",
  "report_time": "18:00",
  "timezone": "UTC"
}
```

### Get Current User
```http
GET /api/users/me/
```
Returns user's full config with masked token

### Sync Token
```http
POST /api/auth/sync-token/
```
Ensures GitHub token is fresh and valid

### Logout
```http
POST /api/auth/logout/
```

## Frontend Integration (React Example)

```javascript
// 1. Start Login
async function handleGitHubLogin() {
  const response = await fetch('/api/auth/github/login/');
  const data = await response.json();
  window.location.href = data.auth_url;
}

// 2. OAuth Callback Handler
function OAuthCallback() {
  useEffect(() => {
    const checkAuth = async () => {
      const response = await fetch('/api/auth/github/callback/');
      const data = await response.json();
      
      if (data.authenticated && !data.has_config) {
        // Need to complete registration
        navigate('/complete-registration');
      } else if (data.authenticated) {
        navigate('/dashboard');
      }
    };
    
    checkAuth();
  }, []);
  
  return <div>Loading...</div>;
}

// 3. Complete Registration
async function submitRegistration(formData) {
  const response = await fetch('/api/auth/complete-registration/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(formData)
  });
  
  if (response.ok) {
    navigate('/dashboard');
  }
}

// 4. Get User Config
async function loadUserConfig() {
  const response = await fetch('/api/users/me/', {
    credentials: 'include'
  });
  const config = await response.json();
  console.log(config);
}

// 5. Logout
async function logout() {
  await fetch('/api/auth/logout/', { 
    method: 'POST',
    credentials: 'include'
  });
  navigate('/login');
}
```

## Token Storage & Security

**Where tokens are stored:**
- GitHub access token → `SocialAccount.socialaccount_ptr.extra_data`
- Secure Django database storage
- Never stored in `UserConfig` model

**Token access:**
```python
# In code, tokens are accessed via:
user_config.github_token  # Returns the access token

# Internally it fetches from:
social_account = SocialAccount.objects.get(user=user, provider='github')
social_account.socialaccount_ptr.extra_data['access_token']
```

**Automatic refresh:**
- Django-allauth automatically refreshes expired tokens
- No manual refresh needed

## Troubleshooting

### "Django.contrib.admin auth password validation not working"
- This is normal. Users authenticate via GitHub, not passwords.
- Django superusers still use passwords for admin access.

### "User not authenticated after callback"
- Check if migrations ran: `python manage.py migrate`
- Verify Site settings in Django admin
- Ensure Social App is created with correct credentials
- Clear browser cookies and try again

### "Social account not found" error
- User likely didn't complete GitHub authorization
- Try logging in again from scratch

### "Token is invalid"
- Django-allauth will auto-refresh it
- Or call: `POST /api/auth/sync-token/`

## Database Schema

### UserConfig
```
- user: OneToOneField(User)
- github_username: CharField
- email: EmailField
- report_time: TimeField
- timezone: CharField
- is_active: BooleanField
- created_at, updated_at

Note: github_token removed from model!
      Access via: user_config.github_token property
```

### SocialAccount (django-allauth)
```
- user: ForeignKey(User)
- provider: 'github'
- uid: GitHub user ID
- extra_data: {
    'access_token': '...',
    'login': 'username',
    'email': 'user@example.com',
    ...
  }
```

## Next Steps

1. ✅ Install django-allauth
2. ✅ Configure OAuth in settings
3. ✅ Run migrations
4. ⏳ Create GitHub OAuth App
5. ⏳ Add Social App in Django admin
6. ⏳ Test the flow in Swagger UI: `/api/docs/`
7. ⏳ Integrate with your frontend

## Testing in Swagger UI

1. Go to `http://localhost:8000/api/docs/`
2. Click "Authorize" button
3. Check the OAuth endpoints:
   - `/api/auth/github/login/`
   - `/api/auth/github/callback/`
   - `/api/auth/complete-registration/`
   - `/api/users/me/`
   - `/api/auth/logout/`

## Environment Variables (Production)

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
GITHUB_OAUTH_CLIENT_ID=your_prod_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_prod_client_secret
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

## That's It! 🎉

Your app now uses GitHub OAuth instead of personal access tokens. Much better UX!

Questions? See [GITHUB_OAUTH_SETUP.md](./GITHUB_OAUTH_SETUP.md) for detailed docs.
