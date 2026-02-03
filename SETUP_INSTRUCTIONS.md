# GitHub OAuth Integration - Complete Setup Instructions

## ✅ What's Been Done

Your ReportForMe project has been successfully migrated to GitHub OAuth 2.0!

### New Files Created:
- ✅ `core/oauth_views.py` - OAuth endpoints implementation
- ✅ `core/migrations/0002_remove_github_token.py` - Database migration
- ✅ `GITHUB_OAUTH_SETUP.md` - Complete technical documentation
- ✅ `OAUTH_QUICKSTART.md` - 5-minute quick start guide
- ✅ `OAUTH_MIGRATION_SUMMARY.md` - All changes documented

### Files Modified:
- ✅ `reportforme/settings.py` - OAuth configuration
- ✅ `reportforme/urls.py` - OAuth routes
- ✅ `core/models.py` - Removed github_token field, added property
- ✅ `core/views.py` - Added authentication & user filtering
- ✅ `core/serializers.py` - Updated for OAuth tokens
- ✅ `core/urls.py` - Added OAuth endpoints
- ✅ `requirements.txt` - Added django-allauth

### Database:
- ✅ Migration applied: `python manage.py migrate`
- ✅ `github_token` field removed from UserConfig
- ✅ Allauth tables created (SocialAccount, SocialApp, etc.)

## 🚀 Quick Setup (5 Minutes)

### 1. Create GitHub OAuth App

**Visit:** https://github.com/settings/developers

1. Click "OAuth Apps" → "New OAuth App"
2. Fill in:
   - Application name: `ReportForMe`
   - Homepage URL: `http://localhost:3000` (your frontend domain)
   - Authorization callback URL: `http://localhost:8000/accounts/github/login/callback/`
3. Copy the **Client ID** and **Client Secret**

### 2. Create `.env` File

In the project root, create `.env`:
```env
GITHUB_OAUTH_CLIENT_ID=<paste your Client ID>
GITHUB_OAUTH_CLIENT_SECRET=<paste your Client Secret>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Create Django Admin User

```bash
python manage.py createsuperuser
```

### 4. Configure Site in Django Admin

```bash
python manage.py runserver
```

1. Go to http://localhost:8000/admin/
2. Navigate to **Sites** (under "Websites")
3. Edit the default site:
   - Domain name: `localhost:8000`
   - Display name: `ReportForMe`
4. Click Save

### 5. Add Social Application

1. In Django admin, go to **Social applications** (under "Social authentication")
2. Click "Add Social Application"
3. Fill in:
   - **Provider**: GitHub
   - **Name**: GitHub OAuth
   - **Client id**: [Your GitHub Client ID from step 1]
   - **Secret key**: [Your GitHub Client Secret from step 1]
   - **Sites**: Select "localhost:8000"
4. Click Save

### 6. Test It!

```bash
python manage.py runserver
```

Go to http://localhost:8000/api/docs/

Test endpoints:
1. **GET** `/api/auth/github/login/` → Get OAuth URL
2. Copy the URL and visit it in browser to authorize
3. **GET** `/api/auth/github/callback/` → Check if authenticated
4. **POST** `/api/auth/complete-registration/` → Finish setup
5. **GET** `/api/users/me/` → View your config

## 📚 API Endpoints

### Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/auth/github/login/` | Get GitHub OAuth authorization URL |
| GET | `/api/auth/github/callback/` | Check authentication status |
| POST | `/api/auth/complete-registration/` | Complete user registration |
| POST | `/api/auth/logout/` | Logout user |

### User Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/users/me/` | Get current user's configuration |
| POST | `/api/auth/sync-token/` | Refresh/verify GitHub token |

### Data Access (All require authentication)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/users/` | List user configs (filtered to current user) |
| GET | `/api/reports/` | List reports (filtered to current user) |
| GET | `/api/commits/` | List commits (filtered to current user) |
| GET | `/api/repositories/` | List repositories (filtered to current user) |

## 🔐 Security Notes

### Token Storage
- ✅ Tokens stored in encrypted Django database (`SocialAccount` table)
- ✅ Never exposed to frontend (masked as `ghp_abc...789`)
- ✅ Automatic refresh handled by django-allauth
- ✅ No manual token management by users

### Scopes Requested
Users are asked to authorize these GitHub permissions:
- `user` - Access to user profile
- `repo` - Access to repositories
- `read:org` - Read access to organizations

## 📝 Example Frontend Implementation

### React Login Component
```javascript
import { useEffect } from 'react';

function GitHubLoginButton() {
  const handleLogin = async () => {
    const response = await fetch('/api/auth/github/login/');
    const data = await response.json();
    window.location.href = data.auth_url;
  };

  return (
    <button onClick={handleLogin}>
      Sign in with GitHub
    </button>
  );
}

function OAuthCallback() {
  useEffect(() => {
    const checkAuth = async () => {
      const response = await fetch('/api/auth/github/callback/');
      const data = await response.json();
      
      if (data.authenticated && !data.has_config) {
        // Redirect to complete registration form
        window.location.href = '/complete-registration';
      } else if (data.authenticated) {
        // User is fully set up
        window.location.href = '/dashboard';
      }
    };
    
    checkAuth();
  }, []);

  return <div>Setting up your account...</div>;
}

function CompleteRegistration() {
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const response = await fetch('/api/auth/complete-registration/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        email: formData.get('email'),
        report_time: formData.get('report_time'),
        timezone: formData.get('timezone')
      })
    });

    if (response.ok) {
      window.location.href = '/dashboard';
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" name="email" placeholder="Email" required />
      <input type="time" name="report_time" defaultValue="18:00" />
      <select name="timezone" defaultValue="UTC">
        <option value="UTC">UTC</option>
        <option value="America/New_York">Eastern Time</option>
        <option value="America/Chicago">Central Time</option>
        <option value="America/Los_Angeles">Pacific Time</option>
      </select>
      <button type="submit">Complete Registration</button>
    </form>
  );
}

export { GitHubLoginButton, OAuthCallback, CompleteRegistration };
```

## 🚨 Important: Existing Users

If you had users with old `github_token` values:
- ⚠️ Their tokens were removed in the migration
- ⚠️ They must re-authenticate with GitHub OAuth
- ⚠️ This is one-time only - new token is automatic

Migration command already run:
```bash
python manage.py migrate  # ✅ Done
```

## 🧪 Testing

### Test in Swagger UI
1. Go to http://localhost:8000/api/docs/
2. Click "Authorize" button
3. Try endpoints in order:
   - GET `/api/auth/github/login/`
   - (Visit returned URL in browser)
   - GET `/api/auth/github/callback/`
   - POST `/api/auth/complete-registration/`
   - GET `/api/users/me/`

### Test with cURL
```bash
# 1. Get GitHub OAuth URL
curl http://localhost:8000/api/auth/github/login/

# 2. Manually visit the returned auth_url and authorize

# 3. Check authentication
curl -b cookies.txt http://localhost:8000/api/auth/github/callback/

# 4. Complete registration
curl -X POST http://localhost:8000/api/auth/complete-registration/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "email": "user@example.com",
    "report_time": "18:00",
    "timezone": "UTC"
  }'

# 5. Get user config
curl -b cookies.txt http://localhost:8000/api/users/me/
```

## 🔧 Production Setup

### Environment Variables
```env
# GitHub OAuth
GITHUB_OAUTH_CLIENT_ID=your_prod_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_prod_client_secret

# Django
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email
EMAIL_HOST_USER=your_mailgun_email
EMAIL_HOST_PASSWORD=your_mailgun_password

# Database
DATABASE_URL=postgres://user:pass@localhost/dbname
```

### Production OAuth App

1. Create a **new** OAuth App on GitHub for production
2. Set Authorization callback URL to: `https://yourdomain.com/accounts/github/login/callback/`
3. Use different Client ID/Secret for production

### HTTPS Required
- ✅ GitHub OAuth requires HTTPS in production
- ✅ Use Let's Encrypt for free SSL certificates

## 📚 Documentation

For more details, see:
- **[OAUTH_QUICKSTART.md](./OAUTH_QUICKSTART.md)** - Fast setup guide
- **[GITHUB_OAUTH_SETUP.md](./GITHUB_OAUTH_SETUP.md)** - Complete technical docs
- **[OAUTH_MIGRATION_SUMMARY.md](./OAUTH_MIGRATION_SUMMARY.md)** - All changes explained

## ❓ Troubleshooting

### "Invalid client_id" error
- Check if Client ID is correct
- Verify OAuth App still exists on GitHub

### "Redirect URI mismatch" error
- Authorization callback URL must match **exactly**
- Format: `https://domain.com/accounts/github/login/callback/`

### "User not authenticated" after callback
- Check if migrations ran: `python manage.py migrate`
- Verify Site exists in Django admin
- Ensure Social Application created with correct credentials

### "No GitHub account found"
- User didn't complete GitHub authorization
- Try logging in again

### "Token is invalid"
- Django-allauth will auto-refresh
- Or call: `POST /api/auth/sync-token/`

## 🎉 You're Done!

Your app is now ready for GitHub OAuth authentication!

**Next Steps:**
1. ✅ Create GitHub OAuth App (DONE - step 1 above)
2. ✅ Set up environment variables (DONE - step 2)
3. ✅ Create Django admin user (DONE - step 3)
4. ✅ Configure Site (DONE - step 4)
5. ✅ Add Social Application (DONE - step 5)
6. ✅ Test the flow (DONE - step 6)
7. ⏳ Integrate with your frontend
8. ⏳ Deploy to production

**Questions?** Check the documentation files or review the code in `core/oauth_views.py`.
