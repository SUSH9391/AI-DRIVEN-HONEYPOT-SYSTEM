# AI-Driven Honeypot System - Production Architecture

## Codebase Overview

**High-level structure:** 4-layer FastAPI (client → middleware → honeypot engine → async AI/log).

```
Backend/
├── app/                    # FastAPI core
│   ├── main.py             # App factory, middleware/routers mount
│   ├── routers/            # Trap + admin routes
│   │   ├── honeypot.py     # Bait: /api/login/signup/checkout/query /admin/*
│   │   ├── admin.py        # JWT admin: /api/admin/attacks/stats/sessions/block
│   │   └── health.py       # /health /metrics Prometheus
│   ├── middleware/         # Stack
│   │   ├── rate_limit.py   # SlowAPI Redis IP/hour
│   │   ├── auth.py         # Supabase JWT (anon honeypot OK)
│   │   ├── fingerprint.py  # UA/headers hash to request.state
│   │   └── logging_mw.py   # Structured JSON logs console
│   ├── services/           # Business logic
│   │   ├── honeypot_service.py # Orchestrate rule/ML/fake/log
│   │   ├── logging_service.py # Dual PG + NDJSON background
│   │   ├── session_service.py # Redis IP sessions/count/block
│   │   └── geo_service.py  # IP→country/ASN httpx background stub
│   ├── detectors/          # Attack ID
│   │   ├── rule_detector.py # Sync regex/SQLi/XSS/RCE/path-trav (legacy refactor)
│   │   └── ml_detector.py  # Async HF transformers threat score
│   ├── generators/         # Fake responses immediate
│   │   └── fake_data.py    # Schema-aware SQL fake rows/login (legacy refactor)
│   ├── models/             # SQLAlchemy async
│   │   └── attack_log.py   # AttackLog/Session/User (UUID/INET indexes)
│   └── schemas/            # Pydantic I/O
│       ├── attack.py       # AttackLogCreate/Read/Update
│       └── session.py      # SessionCreate/Read/Block
├── core/                   # Shared
│   ├── config.py           # PydanticSettings (.env)
│   ├── database.py         # asyncpg engine/session/Base
│   ├── redis.py            # aioredis pool
│   └── security.py         # Supabase JWT deps/RBAC
├── alembic/                # Migrations async
│   ├── ini/env/script.mako
│   └── versions/001_sessions.py 002_attack_logs.py
├── docker/                 # Deploy
│   ├── Dockerfile
│   └── docker-compose.yml  # postgres/redis/prometheus
├── templates/ static/      # Reused Flask honeypot UI
├── Backend/attack_logs.json # NDJSON fallback
├── .env.example            # Copy → .env (DB/Supabase/Redis/HF)
└── requirements.txt        # FastAPI/transformers/asyncpg/alembic/redis/arq/JWT/slowapi/prometheus

**Unwanted/Deprecated (delete safe):**
- honeypot.py honeypot_system_hf_merged.py products.py (refactored)
- e-commerce website/ frontend/ (old Flask/React, optional delete)
```

## Data Flow (Attacker POST /api/login)
1. **Middleware**: RateLimitRedis → AuthJWT(anon) → Fingerprint → LogReq
2. **HoneypotRouter** → HoneypotService.handle_request
3. **RuleDetector** sync regex → high conf? MLDetector async queue
4. **FakeDataGenerator** immediate realistic resp (no block)
5. **BackgroundTasks**: SessionService Redis inc count, LoggingService dual PG/NDJSON, Geo enrich
6. Prometheus counter++ , resp attacker

## Run Local (Backend/)
```
pip install -r requirements.txt
cp ../.env.example ../.env  # Set postgres URL
alembic upgrade head
uvicorn app.main:app --reload
```

## Test
```
# SQLi bait
curl 'http://localhost:8000/api/query?q=SELECT * FROM users WHERE id=1 OR 1=1--'

# Carding
curl -X POST http://localhost:8000/api/checkout -d 'card=4111111111111111&cvv=123'

# Admin (needs JWT)
curl http://localhost:8000/health ; curl http://localhost:8000/metrics

# Logs
tail -f attack_logs.json ; psql -d honeypot -c 'SELECT * FROM attack_logs ORDER BY created_at DESC LIMIT 5;'
```

**Docker:** `docker compose up`.

Roadmap extensions: ARQ worker ML jobs, Supabase RLS, CI pytest/ruff/mypy, fine-tune HF threat model.

Honeypot live!
