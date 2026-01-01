"""Management command to setup initial data"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserConfig


class Command(BaseCommand):
    help = 'Initialize the ReportForMe application'

    def add_arguments(self, parser):
        parser.add_argument('--create-admin', action='store_true', help='Create admin user')

    def handle(self, *args, **options):
        if options['create_admin']:
            self.create_admin_user()

        self.stdout.write(self.style.SUCCESS('✓ ReportForMe initialized successfully'))
        self.print_setup_instructions()

    def create_admin_user(self):
        """Create a superuser for the admin panel"""
        username = input('Admin username: ').strip()
        email = input('Admin email: ').strip()

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            return

        password = input('Admin password: ').strip()
        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f'✓ Admin user {username} created'))

    def print_setup_instructions(self):
        """Print setup instructions"""
        self.stdout.write(self.style.SUCCESS('''
╔═══════════════════════════════════════════════════════════════╗
║               ReportForMe Setup Instructions                  ║
╚═══════════════════════════════════════════════════════════════╝

1. Environment Configuration:
   - Copy .env.example to .env
   - Fill in your GitHub token and email credentials

2. Database Migration:
   python manage.py migrate

3. Create Superuser:
   python manage.py createsuperuser

4. Start Development Server:
   python manage.py runserver

5. Open Admin Panel:
   http://localhost:8000/admin

6. Configure Your Account:
   - Add your GitHub token
   - Set your email address
   - Configure report time and timezone
   - Sync your repositories

7. Start Celery (in a separate terminal):
   celery -A reportforme worker -l info

8. Start Celery Beat (in another terminal):
   celery -A reportforme beat -l info

API Endpoints:
   GET    /api/users/                    - List users
   POST   /api/users/1/verify_token/     - Verify GitHub token
   POST   /api/users/1/sync_repositories/ - Sync repos
   POST   /api/users/1/fetch_daily_commits/ - Fetch commits
   POST   /api/users/1/send_test_email/  - Send test email
   GET    /api/reports/today/            - Get today's report
   GET    /api/reports/recent/           - Get recent reports
   GET    /api/commits/today/            - Get today's commits
'''))
