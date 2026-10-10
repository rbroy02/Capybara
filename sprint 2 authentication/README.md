# Sprint 2 — Authentication Login Prototype

A standalone Python Tkinter + SQLite login prototype for the SPN pH Correction Skid Design Tool. This is **not yet integrated** with the team's React/Node.js application.

## Requirements
- Python 3 with Tkinter support (typically included in desktop Python installations)
- No additional Python packages required

## Run locally
Open a terminal in this folder, then run:

```bash
python3 setup_user.py
python3 app.py
```

The setup command asks you to create your own **local** username and password. It creates `users.db` on your computer; that file must not be committed to GitHub. The app uses that local account for login.

## Run tests

```bash
python3 -m unittest test_auth.py -v
```

Tests create and remove their own `test_users.db`. They use a test-only password and do not access your normal account database.

## Source files
- `app.py` — Tkinter login and logout interface
- `auth.py` — SQLite user storage and password verification
- `setup_user.py` — create a local login account
- `test_auth.py` — authentication unit tests
- `.gitignore` — excludes databases, cache and local environment files

## Scope and limitations
Educational prototype only. Do not use for production authentication or live industrial control. Authentication and access management need further security review and integration before deployment.
