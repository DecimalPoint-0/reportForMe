@echo off
REM Quick Start Script for ReportForMe on Windows

echo.
echo 🚀 ReportForMe Quick Start
echo ==========================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Show instructions
echo.
echo ✅ Setup complete!
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo In separate terminals, run:
echo   celery -A reportforme worker -l info
echo   celery -A reportforme beat -l info
echo.
echo Then visit: http://localhost:8000/admin
echo.

pause
