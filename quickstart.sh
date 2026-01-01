#!/bin/bash
# Quick Start Script for ReportForMe

echo "🚀 ReportForMe Quick Start"
echo "=========================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser if needed
if ! python manage.py shell -c "from django.contrib.auth.models import User; exit(0 if User.objects.exists() else 1)" 2>/dev/null; then
    echo ""
    echo "No admin user found. Creating superuser..."
    python manage.py createsuperuser
fi

# Show instructions
echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
echo ""
echo "In separate terminals, run:"
echo "  celery -A reportforme worker -l info"
echo "  celery -A reportforme beat -l info"
echo ""
echo "Then visit: http://localhost:8000/admin"
