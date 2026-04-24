## Summary
Pytest runs emit a DeprecationWarning from flask_session because the use_signer option is deprecated and will be removed in the next minor release.

## Warning output
```
flask_frontend/tests/test_auth.py: 4 warnings
flask_frontend/tests/test_dashboard.py: 2 warnings
flask_frontend/tests/test_environments.py: 2 warnings
flask_frontend/tests/test_sandbox.py: 4 warnings
  .../site-packages/flask_session/base.py:172: DeprecationWarning: The 'use_signer' option is deprecated and will be removed in the next minor release. Please update your configuration accordingly or open an issue.
```

## Source
SESSION_USE_SIGNER = True is set in:
- flask_frontend/config.py

## Suggested action
Review the flask-session changelog/docs to remove or replace the SESSION_USE_SIGNER setting before the next minor release.

