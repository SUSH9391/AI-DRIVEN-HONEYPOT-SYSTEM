# File Index for AI-Driven Honeypot System

This index catalogs all files in the codebase (generated recursively from root). Files are grouped by location/type for easy navigation. Empty directories are noted. Project appears to be a FastAPI-based honeypot with database (Alembic/SQLAlchemy), Redis, ML/rule detectors, fake data generators, honeypot services, and fake web templates/static assets.

## Root Files (./)
- `.gitignore` - Git ignore rules
- `alembic.ini` - Alembic migration config
- `pyproject.toml` - Python project config (likely for uv/packaging)
- `README.md` - Project documentation
- `requirements.txt` - Python dependencies
- `tmp.txt` - Temporary file
- `uv.lock` - UV package lockfile

## Docker Files (docker/)
- `docker-compose.yml` - Docker Compose orchestration
- `Dockerfile` - Docker build instructions

## Source Code (src/)
### Core Modules (src/core/)
- `config.py` - Configuration settings
- `database.py` - Database connection/setup (SQLAlchemy)
- `redis.py` - Redis client setup
- `security.py` - Security utilities (e.g., hashing, JWT)

### App Main (src/app/)
- `__init__.py` - Package init
- `main.py` - FastAPI app entrypoint

### Models (src/app/models/)
- `attack_log.py` - Pydantic/SQLAlchemy models for attack logs

### Schemas (src/app/schemas/)
- `__init__.py`
- `attack.py` - Pydantic schemas for attacks
- `session.py` - Pydantic schemas for sessions

### Services (src/app/services/)
- `__init__.py`
- `geo_service.py` - Geolocation service
- `honeypot_service.py` - Core honeypot logic
- `logging_service.py` - Logging service
- `session_service.py` - Session management

### Detectors (src/app/detectors/)
- `__init__.py`
- `ml_detector.py` - ML-based attack detection
- `rule_detector.py` - Rule-based detection

### Generators (src/app/generators/)
- `__init__.py`
- `fake_data.py` - Fake data generation for honeypot

### Middleware (src/app/middleware/)
- `__init__.py`
- `auth.py` - Authentication middleware
- `fingerprint.py` - Client fingerprinting
- `logging_mw.py` - Logging middleware
- `rate_limit.py` - Rate limiting

### Routers (src/app/routers/)
- `__init__.py`
- `admin.py` - Admin API endpoints
- `health.py` - Health checks
- `honeypot.py` - Honeypot API endpoints

### Alembic Migrations (src/alembic/)
- `env.py` - Migration environment
- `script.py.mako` - Migration script template
### Alembic Versions (src/alembic/versions/)
- `__init__.py`
- `001_create_sessions.py` - Create sessions table
- `002_create_attack_logs.py` - Create attack logs table

### Data/Logs
- `attack_logs.json` - Sample or logged attacks (JSON)

### Static Assets (src/static/)
- `main.css` (src/static/css/) - Main stylesheet
- **Empty:** src/static/images/products/

### Templates (src/templates/)
- `admin_login.html` - Admin login page
- `checkout.html` - Fake checkout (honeypot lure)
- `dashboard.html` - Dashboard
- `login.html` - Login page
- `product.html` - Product page
- `signup.html` - Signup page

### Other (src/)
- `3.1.1` - Directory (possibly version tag or data)

## Empty Directories
- `static/`
- `src/static/css/` (except main.css listed)
- `src/static/images/`
- Various `__init__.py` only dirs are packages

## Notes
- Total files: ~60 (exact count from recursive list).
- Primary tech: Python/FastAPI, SQLAlchemy, Alembic, Redis, Pydantic.
- Honeypot simulates e-commerce (templates/static) to log attacks via detectors/services.
- Duplicates noted in VSCode tabs (e.g., Backend/ paths may be legacy).
- To search contents: Use `grep` or IDE search.

Generated automatically.
