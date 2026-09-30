# CSC-54 standalone security prototype

Install: `python3 -m pip install -r requirements.txt`

Run tests: `python3 -m unittest -v test_security.py`

The prototype provides engineer/reviewer permissions, scrypt password hashing, Fernet encryption for project payloads, and SQLite audit records. Generate a Fernet key once (`Fernet.generate_key()`), store it securely outside the database/repository, and back it up securely. **Do not generate a new key on every application startup**, or existing projects become unreadable.

This is not yet integrated into the main application. In particular, role arguments are trusted inputs to this prototype; production routes must derive roles from a verified authenticated session, not client-supplied values. Restrict audit log access, implement secure key management and recovery, and test authorization at each application endpoint before deployment. SQLite database metadata and audit records are not encrypted by Fernet; the project payload is encrypted. Use encrypted disk/database storage if the requirement includes all data at rest.
