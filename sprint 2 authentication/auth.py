import sqlite3
import hashlib
import secrets
import hmac

DATABASE_NAME = "users.db"


# --------------------------------------------------
# Database setup
# --------------------------------------------------

def create_user_table():
    """
    Creates the users table if it does not already exist.
    """

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# Password security
# --------------------------------------------------

def hash_password(password, salt=None):
    """
    Converts a password into a secure hash.

    The real password is not stored in the database.
    """

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )

    return password_hash.hex(), salt


# --------------------------------------------------
# Create user
# --------------------------------------------------

def create_user(username, password):
    """
    Creates a user account.
    """

    if not username or not password:
        return False, "Username and password are required."

    password_hash, salt = hash_password(password)

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, salt)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, salt)
        )

        connection.commit()
        return True, "User created successfully."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    finally:
        connection.close()


# --------------------------------------------------
# Authenticate user
# --------------------------------------------------

def authenticate_user(username, password):
    """
    Checks whether the username and password are correct.
    """

    if not username or not password:
        return False

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT password_hash, salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()
    connection.close()

    if user is None:
        return False

    stored_hash, salt = user

    entered_hash, _ = hash_password(password, salt)

    return hmac.compare_digest(stored_hash, entered_hash)


# --------------------------------------------------
# Start database
# --------------------------------------------------

if __name__ == "__main__":
    create_user_table()

    print("Authentication database created successfully.")