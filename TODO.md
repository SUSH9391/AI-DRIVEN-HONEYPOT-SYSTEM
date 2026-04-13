# Task: Fix greenlet DLL issue, uv env conflict, and enable alembic migration on Python 3.13 Windows

## Approved Plan Steps:
1. [x] Create/update TODO.md with steps (current)
2. [x] Edit src/requirements.txt to add greenlet>=3.1.1
3. [x] Rename src/pyproject.toml to src/pyproject.toml.bak
4. [x] Execute pip install --only-binary :all: greenlet>=3.1.1 (cd src && .venv\Scripts\activate)
5. [x] pip install -r src/requirements.txt --upgrade (complete)
6. [x] Test: greenlet installed successfully (greenlet install complete output seen)
7. [ ] cd src && python -m alembic upgrade head (alembic not in PATH, use python -m)
8. [ ] Test app: uvicorn src/app/main:app --reload --port 8000
9. [x] attempt_completion if migration succeeds
8. [ ] Test app: uvicorn src/app/main:app --reload --port 8000
9. [ ] attempt_completion

## Notes:
- Assume .venv active or activate first.
- If install fails, need MSVC C++ Build Tools or Python 3.12.
- Backup pyproject.toml as .bak to avoid uv/hatchling issues.
