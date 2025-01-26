import unittest
from unittest.mock import patch, Mock
from app import app
from bson import ObjectId
from models.User import User  # Import the User class

class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test data and Flask test client"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'  # Add a secret key for session
        self.client = app.test_client(use_cookies=True)  # Enable cookies for session

    def test_home_page(self):
        """Test home page access"""
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        """Test successful registration"""
        with patch('models.User.User.find_by_username_or_email', return_value=None):
            with patch('models.User.User.find_by_email', return_value=None):
                with patch('models.User.User.save'):
                    response = self.client.post(
                        '/api/register',  # Updated to match the actual route
                        json={  # Updated to match the actual request format
                            'username': 'newuser',
                            'email': 'new@example.com',
                            'password': 'password123'
                        }
                    )
                    self.assertEqual(response.status_code, 201)  # Updated to match the actual response

    def test_register_existing_user(self):
        """Test registration with existing username/email"""
        mock_user = Mock(spec=User)
        with patch('models.User.User.find_by_username_or_email', return_value=mock_user):
            response = self.client.post(
                '/api/register',  # Updated to match the actual route
                json={  # Updated to match the actual request format
                    'username': 'existinguser',
                    'email': 'existing@example.com',
                    'password': 'password123'
                }
            )
            self.assertEqual(response.status_code, 400)

    def test_login_success_with_username(self):
        """Test successful login with username"""
        mock_user = Mock(spec=User)
        mock_user.user_id = str(ObjectId())
        mock_user.check_password.return_value = True

        with patch('models.User.User.find_by_username_or_email', return_value=mock_user):
            response = self.client.post(
                '/api/login',  # Updated to match the actual route
                json={  # Updated to match the actual request format
                    'username': 'testuser',
                    'password': 'password123'
                }
            )
            self.assertEqual(response.status_code, 200)  # Updated to match the actual response

    def test_login_success_with_email(self):
        """Test successful login with email"""
        mock_user = Mock(spec=User)
        mock_user.user_id = str(ObjectId())
        mock_user.check_password.return_value = True

        with patch('models.User.User.find_by_username_or_email', return_value=mock_user):
            response = self.client.post(
                '/api/login',  # Updated to match the actual route
                json={  # Updated to match the actual request format
                    'username': 'test@example.com',  # Using email in username field
                    'password': 'password123'
                }
            )
            self.assertEqual(response.status_code, 200)  # Updated to match the actual response

    def test_login_failure(self):
        """Test login with invalid credentials"""
        with patch('models.User.User.find_by_username_or_email', return_value=None):
            response = self.client.post(
                '/api/login',  # Updated to match the actual route
                json={  # Updated to match the actual request format
                    'username': 'nonexistent',
                    'password': 'wrongpass'
                }
            )
            self.assertEqual(response.status_code, 401)

    def test_logout(self):
        """Test logout functionality"""
        with self.client.session_transaction() as session:
            session['user_id'] = str(ObjectId())  # Simulate a logged-in user

        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_protected_route_redirect(self):
        """Test redirect to index when accessing protected route without authentication"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/index' in response.location)

if __name__ == '__main__':
    unittest.main()