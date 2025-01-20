# a-real-django-app
A real django app. Can't be more real.

## Docker Setup (Recommended)

1. Install Docker and Docker Compose on your system
2. Clone the repository
3. Start the application:
   ```bash
   docker-compose up --build
   ```
4. Run migrations (first time only):
   ```bash
   docker-compose exec web python manage.py migrate
   ```

The application will be available at http://localhost:8001

### Running Tests with Docker
```bash
docker-compose exec web python manage.py test
```

### Accessing Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Viewing Logs
```bash
docker-compose logs -f
```

## Local Setup (Alternative)

If you prefer to run without Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update the values
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Required environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable debug mode (True/False)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `REDIS_URL`: Redis connection URL
- `SENTRY_DSN`: Sentry Data Source Name for error tracking (optional)
- `JWT_SECRET`: Secret key for JWT authentication
- `SMTP_HOST`: SMTP server host for email notifications
- `SMTP_PORT`: SMTP server port
- `SMTP_USER`: SMTP server user
- `SMTP_PASS`: SMTP server password
- `ALERT_FROM`: Email address for sending alerts
- `ALERT_TO`: Email address to receive alerts

## API Documentation

API documentation is available at:
- OpenAPI Schema: `/api/schema/`
- Swagger UI: `/api/docs/`

## Development

### Common Commands

With Docker:
```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web python manage.py test

# Shell access
docker-compose exec web python manage.py shell
```

### Rebuilding

If you make changes to requirements.txt:
```bash
docker-compose down
docker-compose up --build
```

## New Features and Changes

- **Authentication Service**: Added JWT-based authentication service in `auth/auth.js` and `auth/auth_service.py`.
- **Scheduler Enhancements**: Introduced new scheduler functionalities in `scheduler.js` and `scheduler.py` for automated tasks and health checks.
- **Disk Space Monitoring**: Implemented disk space monitoring and emergency cleanup in `scheduler.js` and `scheduler.py`.
- **Logging and Notifications**: Enhanced logging with Winston and added email notifications for job failures and alerts.

## Additional Dependencies

- **Node.js**: Added dependencies in `package.json` for `express`, `jsonwebtoken`, `bcrypt`, `cors`, and `disk-space`.
- **Python**: Updated `requirements.txt` with `psutil`, `PyJWT`, `bcrypt`, `fastapi`, and `uvicorn`.
