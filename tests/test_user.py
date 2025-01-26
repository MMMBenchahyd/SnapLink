import unittest
from unittest.mock import patch, Mock
from models.User import User
from bson import ObjectId

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.test_user = User(
            username="testuser",
            email="test@example.com",
            user_id=str(ObjectId())
        )

    def test_set_password(self):
        """Test password hashing"""
        self.test_user.set_password("testpass")
        self.assertIsNotNone(self.test_user.password_hash)
        self.assertNotEqual(self.test_user.password_hash, "testpass")

    def test_check_password(self):
        """Test password verification"""
        password = "testpass"
        self.test_user.set_password(password)
        self.assertTrue(self.test_user.check_password(password))
        self.assertFalse(self.test_user.check_password("wrongpass"))

if __name__ == '__main__':
    unittest.main()