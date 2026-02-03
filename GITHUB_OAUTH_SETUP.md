# GitHub OAuth Integration Guide

## Overview
ReportForMe now uses GitHub OAuth for seamless registration and login. Users no longer need to manually create and manage GitHub personal access tokens.

## How It Works

### Architecture
- **OAuth Provider**: GitHub
- **OAuth Library**: `django-allauth`
- **Token Storage**: GitHub SocialAccount (automatic token refresh)
- **Scopes Requested**: `user`, `repo`, `read:org`

### User Flow

#### 1. Registration
```
User clicks "Sign Up with GitHub"
        ↓
Redirected to GitHub OAuth consent screen
        ↓
User authorizes ReportForMe
        ↓
GitHub redirects back to app with code
        ↓
App exchanges code for access token
        ↓
User created in Django + Social Account created
        ↓
User prompted to complete registration
        (email, report time, timezone)
        ↓
UserConfig created with OAuth token stored
```

#### 2. Login
```
User clicks "Login with GitHub"
        ↓
Redirected to GitHub OAuth consent screen
        ↓
User authorizes (if needed)
        ↓
GitHub redirects with code
        ↓
App exchanges code for new token
        ↓
User authenticated + logged in
        ↓
Token synced automatically
```

## Setup Instructions

### 1. Install django-allauth
```bash
pip install django-allauth
```

### 2. Create GitHub OAuth App
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: ReportForMe
   - **Homepage URL**: http://localhost:3000 (or your frontend URL)
   - **Authorization callback URL**: http://localhost:8000/accounts/github/login/callback/
4. Copy the **Client ID** and **Client Secret**

### 3. Configure Django Settings
Add to your `settings.py`:

```python
# GitHub OAuth Credentials (use environment variables in production)
GITHUB_OAUTH_CLIENT_ID = os.environ.get('GITHUB_OAUTH_CLIENT_ID', '')
GITHUB_OAUTH_CLIENT_SECRET = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET', '')
```

### 4. Create Site in Django Admin
1. Go to Django admin: http://localhost:8000/admin/
2. Navigate to Sites
3. Edit the existing site (or create new):
   - **Domain name**: localhost:8000 (or your actual domain)
   - **Display name**: ReportForMe

### 5. Create GitHub Social App
1. Go to Django admin: http://localhost:8000/admin/socialaccount/socialapp/
2. Click "Add Social Application"
3. Fill in:
   - **Provider**: GitHub
   - **Name**: GitHub OAuth
   - **Client id**: [Your GitHub Client ID]
   - **Secret key**: [Your GitHub Client Secret]
   - **Sites**: Select your site
4. Click Save

### 6. Run Migrations
```bash
python manage.py migrate
```

## API Endpoints

### 1. Get GitHub Login URL
```http
GET /api/auth/github/login/
```

**Response:**
```json
{
    "auth_url": "https://github.com/login/oauth/authorize?client_id=...&redirect_uri=...&scope=..."
}
```

**Frontend Usage:**
```javascript
// When user clicks "Sign up with GitHub"
const response = await fetch('/api/auth/github/login/');
const data = await response.json();
window.location.href = data.auth_url;
```

### 2. OAuth Callback Status
```http
GET /api/auth/github/callback/
```

**After GitHub redirects, check authentication status:**

**Response (Authenticated, has config):**
```json
{
    "authenticated": true,
    "has_config": true,
    "username": "john_doe",
    "email": "john@example.com"
}
```

**Response (Authenticated, needs to complete registration):**
```json
{
    "authenticated": true,
    "has_config": false,
    "username": "john_doe",
    "email": "john@example.com",
    "message": "Please complete registration"
}
```

### 3. Complete Registration
```http
POST /api/auth/complete-registration/
Content-Type: application/json
Authorization: Bearer <token>

{
    "email": "john@example.com",
    "report_time": "18:00",
    "timezone": "America/New_York"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Registration completed successfully",
    "user_config": {
        "id": 1,
        "github_username": "john_doe",
        "email": "john@example.com",
        "report_time": "18:00",
        "timezone": "America/New_York",
        "is_active": true,
        "repositories": [],
        "github_token": "ghp_abc...789",
        "created_at": "2026-02-03T10:00:00Z",
        "updated_at": "2026-02-03T10:00:00Z"
    }
}
```

### 4. Get Current User Config
```http
GET /api/users/me/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "id": 1,
    "github_username": "john_doe",
    "email": "john@example.com",
    "report_time": "18:00",
    "timezone": "America/New_York",
    "is_active": true,
    "repositories": [],
    "github_token": "ghp_abc...789"
}
```

### 5. Sync GitHub Token
```http
POST /api/auth/sync-token/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "success",
    "message": "GitHub token is synchronized",
    "token_exists": true
}
```

### 6. Logout
```http
POST /api/auth/logout/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "success",
    "message": "Logged out successfully"
}
```

## Frontend Integration Example

### React Implementation

```javascript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function GitHubLogin() {
  const navigate = useNavigate();

  const handleGitHubLogin = async () => {
    try {
      const response = await fetch('/api/auth/github/login/');
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <button onClick={handleGitHubLogin}>
      Sign in with GitHub
    </button>
  );
}

function OAuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await fetch('/api/auth/github/callback/');
        const data = await response.json();
        
        if (data.authenticated) {
          if (data.has_config) {
            // User is fully registered
            navigate('/dashboard');
          } else {
            // User needs to complete registration
            navigate('/complete-registration');
          }
        } else {
          navigate('/login');
        }
      } catch (error) {
        console.error('Auth check error:', error);
        navigate('/login');
      }
    };

    checkAuthStatus();
  }, [navigate]);

  return <div>Loading...</div>;
}

function CompleteRegistration() {
  const [formData, setFormData] = useState({
    email: '',
    report_time: '18:00',
    timezone: 'UTC'
  });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/auth/complete-registration/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        navigate('/dashboard');
      } else {
        const error = await response.json();
        console.error('Registration error:', error);
      }
    } catch (error) {
      console.error('Submit error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <input
        type="time"
        value={formData.report_time}
        onChange={(e) => setFormData({...formData, report_time: e.target.value})}
      />
      <select
        value={formData.timezone}
        onChange={(e) => setFormData({...formData, timezone: e.target.value})}
      >
        <option value="UTC">UTC</option>
        <option value="America/New_York">Eastern Time</option>
        <option value="America/Chicago">Central Time</option>
        {/* Add more timezones */}
      </select>
      <button type="submit">Complete Registration</button>
    </form>
  );
}

export { GitHubLogin, OAuthCallback, CompleteRegistration };
```

## Important Notes

### Token Management
- GitHub tokens are stored securely in the `SocialAccount` model
- Tokens are **never** stored in the `UserConfig` model
- The `github_token` property fetches it from the social account on demand
- Django-allauth handles token refresh automatically

### Permissions Requested
- `user` - Access to user profile data
- `repo` - Access to private repositories
- `read:org` - Read access to organization data

### Security Considerations
1. **Client Secret**: Keep in environment variables, never commit to git
2. **Redirect URI**: Must match exactly what's registered on GitHub
3. **HTTPS**: Use HTTPS in production for OAuth callbacks
4. **Token Expiration**: Tokens are automatically refreshed by django-allauth

### Troubleshooting

#### "Invalid client_id" error
- Check if Client ID matches GitHub OAuth App settings
- Ensure the OAuth App still exists and is active

#### "Redirect URI mismatch" error
- The callback URL must exactly match GitHub OAuth App settings
- Format: `https://yourdomain.com/accounts/github/login/callback/`

#### User not authenticated after callback
- Check if database migrations were run: `python manage.py migrate`
- Verify Site settings in Django admin matches your domain
- Clear browser cookies and try again

#### Token validation fails
- Check if GitHub OAuth App Client Secret is correct
- Ensure the Social App is properly configured in Django admin
- Verify the Site is correctly set in the Social App

## Environment Variables (Production)

Create a `.env` file:
```env
GITHUB_OAUTH_CLIENT_ID=your_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_client_secret
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEBUG=False
```

Load in settings.py:
```python
from decouple import config

GITHUB_OAUTH_CLIENT_ID = config('GITHUB_OAUTH_CLIENT_ID')
GITHUB_OAUTH_CLIENT_SECRET = config('GITHUB_OAUTH_CLIENT_SECRET')
```

## Next Steps

1. Create GitHub OAuth App (see Setup Instructions above)
2. Configure Django settings with OAuth credentials
3. Run migrations: `python manage.py migrate`
4. Create Social App in Django admin
5. Test the flow on `/api/docs/` Swagger UI
6. Integrate frontend OAuth callback handling
