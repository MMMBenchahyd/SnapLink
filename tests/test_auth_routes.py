import unittest
from unittest.mock import patch, Mock
from app import app
from models.User import User
from bson import ObjectId

class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_register_get(self):
        """Test GET request to register page"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        """Test successful registration"""
        with patch('models.User.User.find_by_username_or_email', return_value=None):
            with patch('models.User.User.find_by_email', return_value=None):
                with patch('models.User.User.save'):
                    response = self.client.post('/register', data={
                        'username': 'newuser',
                        'email': 'new@example.com',
                        'password': 'password123'
                    })
                    self.assertEqual(response.status_code, 302)

    def test_register_existing_user(self):
        """Test registration with existing username/email"""
        mock_user = Mock(spec=User)
        with patch('models.User.User.find_by_username_or_email', return_value=mock_user):
            response = self.client.post('/register', data={
                'username': 'existinguser',
                'email': 'existing@example.com',
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 400)

    def test_login_success_with_username(self):
        """Test successful login with username"""
        mock_user = Mock(spec=User)
        mock_user.user_id = str(ObjectId())
        mock_user.check_password.return_value = True
        
        with patch('models.User.User.find_by_username_or_email', return_value=mock_user):
            response = self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302)

    def test_login_success_with_email(self):
        """Test successful login with email"""
        mock_user = Mock(spec=User)
        mock_user.user_id = str(ObjectId())
        mock_user.check_password.return_value = True
        
        with patch('models.User.User.find_by_username_or_email', return_value=mock_user):
            response = self.client.post('/login', data={
                'username': 'test@example.com',  # Using email in username field
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        """Test login with invalid credentials"""
        with patch('models.User.User.find_by_username_or_email', return_value=None):
            response = self.client.post('/login', data={
                'username': 'nonexistent',
                'password': 'wrongpass'
            })
            self.assertEqual(response.status_code, 401)

    def test_logout(self):
        """Test logout functionality"""
        with self.client.session_transaction() as session:
            session['user_id'] = str(ObjectId())
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn('user_id', session)

    def test_home_page(self):
        """Test home page access"""
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)

    def test_protected_route_redirect(self):
        """Test redirect to index when accessing protected route without authentication"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/index' in response.location)

if __name__ == '__main__':
    unittest.main()