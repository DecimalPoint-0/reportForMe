# ReportForMe — Automated Daily Work Report Generator

A Django-based application that automatically aggregates GitHub commits and generates human-readable daily work reports, delivered via email.

## Features

- **GitHub Integration**: Automatically fetch commits from your GitHub repositories
- **Smart Aggregation**: Group commits by repository and filter out noise (merge commits, version bumps)
- **Human-Readable Reports**: Transform raw commits into well-formatted daily work summaries
- **Email Delivery**: Automated email sending at your configured time
- **REST API**: Full API for programmatic access and automation
- **Admin Dashboard**: Django admin for easy management
- **Celery Scheduling**: Robust background job scheduling
- **Solo Developer Friendly**: Perfect for individual developers

## Architecture

### Core Components

1. **GitHub Integration Layer** (`github_service.py`)
   - Fetch commits via GitHub REST API
   - Filter noise commits automatically
   - Normalize commit data

2. **Commit Aggregation Engine** (`commit_aggregator.py`)
   - Daily commit collection
   - Repository synchronization
   - Database storage

3. **Report Generation Engine** (`report_generator.py`)
   - Commit categorization (Bugs, Features, Refactoring, etc.)
   - HTML and text report formatting
   - Message enhancement for readability

4. **Scheduler** (`tasks.py` + `celery.py`)
   - Daily report generation (11:45 PM)
   - Hourly report delivery checks
   - Automatic cleanup of old commits

5. **Email Delivery** (`email_service.py`)
   - SMTP-based email sending
   - HTML formatting
   - Delivery logging

## System Requirements

- Python 3.8+
- Django 4.2+
- PostgreSQL or SQLite
- Redis (for Celery)
- GitHub personal access token

## Installation & Setup

### 1. Clone and Setup Environment

```bash
cd ReportForMe
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

Required variables:
- `GITHUB_API_BASE`: GitHub API endpoint
- `EMAIL_HOST`: SMTP server (Mailgun, Gmail, etc.)
- `EMAIL_HOST_USER`: Email account
- `EMAIL_HOST_PASSWORD`: Email password/API key
- `REDIS_URL`: Redis connection string (for local: `redis://localhost:6379/0`)

### 3. Database Migration

```bash
python manage.py migrate
```

### 4. Create Admin User

```bash
python manage.py createsuperuser
# Or use the init command:
python manage.py init_reportforme --create-admin
```

### 5. Start Services

**Terminal 1 - Django Development Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A reportforme worker -l info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
celery -A reportforme beat -l info
```

## Configuration

### 1. Access Admin Panel

Navigate to `http://localhost:8000/admin` and log in with your superuser credentials.

### 2. Create Your User Configuration

Create a `UserConfig` entry with:
- **GitHub Token**: Personal access token from GitHub Settings → Developer settings → Personal access tokens
- **GitHub Username**: Your GitHub username
- **Email**: Email address to receive reports
- **Report Time**: Time to send daily report (e.g., `18:00`)
- **Timezone**: Your timezone (e.g., `US/Eastern`)

### 3. Sync Your Repositories

Use the API or admin to sync your GitHub repositories:

```bash
curl -X POST http://localhost:8000/api/users/1/sync_repositories/
```

## API Endpoints

### User Management
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user config
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user config

### User Actions
- `POST /api/users/{id}/verify_token/` - Verify GitHub token
- `POST /api/users/{id}/sync_repositories/` - Sync all repositories
- `POST /api/users/{id}/fetch_daily_commits/` - Manually fetch today's commits
- `POST /api/users/{id}/send_test_email/` - Send test email

### Reports
- `GET /api/reports/` - List all reports
- `GET /api/reports/today/` - Get today's report
- `GET /api/reports/recent/` - Get last 7 days of reports

### Commits
- `GET /api/commits/` - List all commits
- `GET /api/commits/today/` - Get today's commits

### Repositories
- `GET /api/repositories/` - List monitored repositories
- `POST /api/repositories/{id}/toggle_monitoring/` - Toggle monitoring

## Scheduling

Reports are automatically generated and sent according to these schedules:

| Task | Schedule | Details |
|------|----------|---------|
| Generate Reports | 11:45 PM Daily | Fetches commits and generates reports |
| Send Reports | Every hour | Sends reports at user's configured time |
| Cleanup Old Commits | 2:00 AM Daily | Removes commits older than 30 days |

## Report Generation

### Report Categories

Reports automatically categorize commits:
- 🐛 **Bug Fixes** - Fixed, fix, resolve, patch
- ✨ **Features** - Add, implement, create, feature
- ♻️ **Refactoring** - Refactor, restructure, reorganize
- ⚡ **Improvements** - Improve, enhance, update
- 🧪 **Tests** - Test, tests, add test
- 📚 **Documentation** - Doc, docs, readme
- 📝 **Other Updates** - Everything else

### Message Enhancement

Raw commit messages are processed to:
- Remove conventional commit prefixes (feat:, fix:, etc.)
- Filter noise commits (merge, version bumps)
- Capitalize properly
- Extract first line only

## Testing

### Verify GitHub Token
```bash
curl -X POST http://localhost:8000/api/users/1/verify_token/
```

### Send Test Email
```bash
curl -X POST http://localhost:8000/api/users/1/send_test_email/
```

### Manually Fetch Commits
```bash
curl -X POST http://localhost:8000/api/users/1/fetch_daily_commits/
```

### Check Celery Tasks
```bash
celery -A reportforme inspect active
```

## Email Configuration

### Using Mailgun (Recommended)
1. Sign up at [mailgun.com](https://mailgun.com)
2. Add your domain
3. Get SMTP credentials
4. Set in `.env`:
```
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-api-key
```

### Using Gmail
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Troubleshooting

### Redis Connection Error
- Make sure Redis is running: `redis-server`
- Check `REDIS_URL` in `.env`

### GitHub Token Invalid
- Generate new token at GitHub Settings → Developer settings → Personal access tokens
- Verify in admin or via `/api/users/{id}/verify_token/`

### Reports Not Sending
1. Check Celery worker logs
2. Verify email credentials in `.env`
3. Check admin → Delivery Log for errors
4. Test with `/api/users/{id}/send_test_email/`

### No Commits Fetched
- Verify GitHub token is valid
- Check that repositories are monitored
- Ensure commits are within today's date
- Check Celery Beat logs for scheduling

## Database Schema

### UserConfig
Stores user configuration and credentials

### GithubRepository
Tracks monitored repositories per user

### Commit
Stores fetched commits with metadata

### Report
Generated daily reports with HTML and text versions

### DeliveryLog
Tracks email delivery attempts and status

## Future Enhancements (Phase 2)

- ✅ WhatsApp Business API integration
- ✅ AI-powered commit summarization
- ✅ Team dashboards and manager views
- ✅ Weekly and monthly summaries
- ✅ Export to PDF/Excel
- ✅ Webhook-based real-time updates
- ✅ Slack integration
- ✅ Analytics and productivity insights

## Monetization Strategy

### Free Tier
- 1 GitHub repository
- Email delivery only
- 7 days of report history

### Pro Tier ($5/month)
- Unlimited repositories
- Multiple delivery channels
- 90 days of report history
- Advanced features

### Team Tier ($25/month)
- Team management
- Weekly summaries
- Manager dashboard
- Advanced analytics

## Contributing

Contributions are welcome! Areas for contribution:
- Additional delivery channels (Slack, Discord)
- AI summarization improvements
- UI/Dashboard development
- Tests and documentation

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- GitHub Issues
- Email: support@reportforme.com

---

**Built with ❤️ for developers who forget their daily reports**
