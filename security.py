"""CSC-54 standalone security prototype. Requires cryptography."""
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from cryptography.fernet import Fernet

ROLES = {"engineer", "reviewer"}
PERMISSIONS = {"engineer": {"read", "write"}, "reviewer": {"read"}}

class SecurityService:
    def __init__(self, db_path, key):
        self.db_path = str(db_path)
        self.cipher = Fernet(key)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL, role TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY, encrypted_data BLOB NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL, username TEXT NOT NULL,
                    action TEXT NOT NULL, project_id TEXT,
                    outcome TEXT NOT NULL
                );
            """)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _audit(self, username, action, project_id, outcome):
        with self._connect() as db:
            db.execute("INSERT INTO audit_log (occurred_at, username, action, project_id, outcome) VALUES (?, ?, ?, ?, ?)",
                       (datetime.now(timezone.utc).isoformat(), username, action, project_id, outcome))

    def add_user(self, username, password, role):
        if role not in ROLES or not username.strip() or len(password) < 12:
            raise ValueError("Valid username, role and password of at least 12 characters required")
        salt = os.urandom(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        with self._connect() as db:
            db.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, salt, digest, role))

    def authenticate(self, username, password):
        with self._connect() as db:
            row = db.execute("SELECT salt, password_hash, role FROM users WHERE username = ?", (username,)).fetchone()
        valid = False
        if row:
            candidate = hashlib.scrypt(password.encode(), salt=row[0], n=2**14, r=8, p=1)
            valid = hmac.compare_digest(candidate, row[1])
        self._audit(username, "login", None, "success" if valid else "denied")
        return row[2] if valid else None

    def save_project(self, username, role, project_id, data):
        if role not in ROLES or "write" not in PERMISSIONS[role]:
            self._audit(username, "write", project_id, "denied")
            raise PermissionError("Write access denied")
        encrypted = self.cipher.encrypt(json.dumps(data).encode())
        with self._connect() as db:
            db.execute("INSERT INTO projects VALUES (?, ?) ON CONFLICT(project_id) DO UPDATE SET encrypted_data=excluded.encrypted_data",
                       (project_id, encrypted))
        self._audit(username, "write", project_id, "success")

    def read_project(self, username, role, project_id):
        if role not in ROLES or "read" not in PERMISSIONS[role]:
            self._audit(username, "read", project_id, "denied")
            raise PermissionError("Read access denied")
        with self._connect() as db:
            row = db.execute("SELECT encrypted_data FROM projects WHERE project_id = ?", (project_id,)).fetchone()
        self._audit(username, "read", project_id, "success" if row else "not_found")
        return json.loads(self.cipher.decrypt(row[0])) if row else None

    def audit_events(self):
        with self._connect() as db:
            return db.execute("SELECT occurred_at, username, action, project_id, outcome FROM audit_log ORDER BY id").fetchall()
