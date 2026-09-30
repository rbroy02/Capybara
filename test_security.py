import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from security import SecurityService

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.service = SecurityService(Path(self.tmp.name) / 'test.db', Fernet.generate_key())
        self.service.add_user('alice', 'strong-password-123', 'engineer')
        self.service.add_user('bob', 'another-strong-pass-123', 'reviewer')

    def tearDown(self):
        self.tmp.cleanup()

    def test_engineer_authentication(self):
        self.assertEqual(self.service.authenticate('alice', 'strong-password-123'), 'engineer')

    def test_wrong_password_rejected(self):
        self.assertIsNone(self.service.authenticate('alice', 'wrong'))

    def test_engineer_can_write_and_reviewer_can_read(self):
        self.service.save_project('alice', 'engineer', 'P1', {'ph': 7.0})
        self.assertEqual(self.service.read_project('bob', 'reviewer', 'P1'), {'ph': 7.0})

    def test_reviewer_cannot_write(self):
        with self.assertRaises(PermissionError):
            self.service.save_project('bob', 'reviewer', 'P1', {'ph': 7.0})

    def test_data_encrypted_in_database(self):
        self.service.save_project('alice', 'engineer', 'P1', {'secret': 'unique-test-marker'})
        self.assertNotIn(b'unique-test-marker', (Path(self.tmp.name) / 'test.db').read_bytes())

    def test_audit_records_actor_action_and_time(self):
        self.service.authenticate('alice', 'wrong')
        events = self.service.audit_events()
        self.assertEqual(events[-1][1:3], ('alice', 'login'))
        self.assertEqual(events[-1][-1], 'denied')
        self.assertTrue(events[-1][0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
