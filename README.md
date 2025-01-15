# a-real-django-app
A real django app. Can't be more real.

## Project Overview

This project is a Django-based web application designed to provide a robust and scalable platform for web services. It includes features such as API endpoints, user authentication, and background task scheduling.

### Current Version/Status
- Version: 1.0.0
- Status: Active Development

### System Requirements
- Docker and Docker Compose (for Docker setup)
- Python 3.8+
- PostgreSQL

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

## Additional Notes

- The project now includes a `package.json` file indicating the use of Node.js packages for scheduling and email notifications.
- The `requirements.txt` has been updated to reflect the current Python dependencies, including APScheduler and SQLAlchemy.
