# Supabase Tables Creation - Alembic Migration Plan
Status: In Progress

**Completed:**
- [x] Analyzed models (sessions, attack_logs, users)
- [x] Confirmed Supabase config (host=db.hciwrwoakivuzjukqjyy.supabase.co, port=5432)

**Pending Steps:**
1. [ ] Update core/config.py to construct DATABASE_URL from .env (user, password, host, port, dbname) using asyncpg+sslmode=require
2. [ ] Update alembic/env.py to use settings.DATABASE_URL (remove local fallback)
3. [x] Ensure deps installed (alembic, asyncpg, sqlalchemy, pydantic-settings)
4. [ ] Run `cd src && alembic upgrade head`
5. [ ] Verify: `cd src && alembic current` and check Supabase dashboard/app health

**Tables to be created:**
- sessions
- attack_logs 
- users

