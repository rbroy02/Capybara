"""Create a local account for the Sprint 2 authentication prototype."""
from getpass import getpass
from auth import create_user_table, create_user


def main():
    create_user_table()
    username = input("Choose a username: ").strip()
    password = getpass("Choose a password: ")
    confirm = getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match. No account was created.")
        return
    success, message = create_user(username, password)
    print(message)


if __name__ == "__main__":
    main()
