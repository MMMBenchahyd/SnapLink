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

    @patch('models.User.db.users.find_one')
    def test_find_by_username_or_email(self, mock_find):
        """Test finding user by username or email"""
        mock_find.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "fakehash",
            "user_id": str(ObjectId())
        }
        
        # Test finding by username
        user = User.find_by_username_or_email("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        
        # Test finding by email
        user = User.find_by_username_or_email("test@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

    @patch('models.User.db.users.find_one')
    def test_find_by_email(self, mock_find):
        """Test finding user by email"""
        mock_find.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "fakehash",
            "user_id": str(ObjectId())
        }
        user = User.find_by_email("test@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

if __name__ == '__main__':
    unittest.main()
