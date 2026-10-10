import os
import unittest

import auth


TEST_DATABASE = "test_users.db"


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        # Use a separate database for testing
        auth.DATABASE_NAME = TEST_DATABASE

        # Start with a clean test database
        if os.path.exists(TEST_DATABASE):
            os.remove(TEST_DATABASE)

        auth.create_user_table()

        # Create a test account
        auth.create_user("spn_engineer", "test-only-password")

    def tearDown(self):
        # Delete the test database after each test
        if os.path.exists(TEST_DATABASE):
            os.remove(TEST_DATABASE)

    def test_valid_login(self):
        self.assertTrue(
            auth.authenticate_user("spn_engineer", "test-only-password")
        )

    def test_wrong_password(self):
        self.assertFalse(
            auth.authenticate_user("spn_engineer", "wrong")
        )

    def test_unknown_user(self):
        self.assertFalse(
            auth.authenticate_user("unknown_user", "test-only-password")
        )

    def test_empty_username(self):
        self.assertFalse(
            auth.authenticate_user("", "test-only-password")
        )

    def test_empty_password(self):
        self.assertFalse(
            auth.authenticate_user("spn_engineer", "")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)