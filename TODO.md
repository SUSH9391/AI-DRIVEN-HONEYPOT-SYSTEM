# GitHub Repo Complete!

Repo force-pushed to https://github.com/SUSH9391/AI-DRIVEN-HONEYPOT-SYSTEM.git

Local Git setup:
- Init + initial commit (49d9799)
- Deprecated folders deleted
- Branch: main
- Remote: origin

Test honeypot:
```
cd Backend
pip install -r requirements.txt
cp .env.example .env  # edit DB etc.
alembic upgrade head
uvicorn app.main:app --reload
```

Visit http://localhost:8000 for Flask honeypot UI.

Done!

