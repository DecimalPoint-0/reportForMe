#!/bin/bash
# Setup GitHub OAuth for ReportForMe

echo "ReportForMe GitHub OAuth Setup"
echo "=============================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# GitHub OAuth Configuration
GITHUB_OAUTH_CLIENT_ID=your_client_id_here
GITHUB_OAUTH_CLIENT_SECRET=your_client_secret_here

# Django Settings
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST_USER=your_mailgun_email
EMAIL_HOST_PASSWORD=your_mailgun_password
EOF
    echo ".env file created. Please update it with your credentials."
else
    echo ".env file already exists."
fi

echo ""
echo "Running migrations..."
python manage.py migrate

echo ""
echo "Creating superuser for Django admin..."
python manage.py createsuperuser

echo ""
echo "Next steps:"
echo "1. Go to http://localhost:8000/admin/"
echo "2. Add a new Sites entry with your domain"
echo "3. Create a GitHub OAuth App at https://github.com/settings/developers"
echo "4. Add Social Application in admin with GitHub OAuth credentials"
echo ""
echo "Then start the server:"
echo "python manage.py runserver"
