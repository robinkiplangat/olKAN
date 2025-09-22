# olKAN Change Log

## v0.0.1 - Saturday, September 20, 2025
- Initialized project structure.
- Added basic FastAPI app.
- Created initial models and flat-file storage.
- Milestone: Basic dataset creation endpoint working.

## v0.0.2 - Saturday, September 20, 2025
- Added PostgreSQL via docker-compose.
- Created SQLAlchemy models and integrated with hybrid storage.
- Set up Alembic for migrations (initial schema).
- Updated storage to use database.
- Milestone: Persistent dataset storage with DB.

## v0.0.3 - Saturday, September 20, 2025
- Fixed Pydantic 'regex' to 'pattern' in schemas.py.
- Resolved app startup issues.
- Milestone: FastAPI app running successfully with endpoints testable.
