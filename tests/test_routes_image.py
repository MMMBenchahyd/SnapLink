import unittest
from unittest.mock import patch, Mock
import io
from app import app
from bson import ObjectId
from datetime import datetime, timezone

class TestImageRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test data and Flask test client"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'  # Add a secret key for session
        self.client = app.test_client(use_cookies=True)  # Enable cookies for session
        self.user_id = str(ObjectId())

        # Manually set up the session
        with self.client.session_transaction() as session:
            session['user_id'] = self.user_id

    @patch('models.User.User.search_id')
    @patch('models.image.Image.creating_by_objectid')
    def test_upload_image(self, mock_create, mock_user):
        """Test image upload"""
        mock_user.return_value = Mock(user_id=self.user_id)
        mock_image = Mock()
        mock_create.return_value = mock_image

        data = {
            'content': 'test.png',
            'file': (io.BytesIO(b"test content"), 'test.png')
        }
        response = self.client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)

    @patch('models.image.Image.find_by_img_id')
    def test_get_image(self, mock_find):
        """Test retrieving an image"""
        img_id = str(ObjectId())
        mock_image = Mock()
        mock_image.file_content = b"test content"
        mock_find.return_value = mock_image

        response = self.client.get(f'/image/{img_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"test content")

    @patch('models.image.Image.find_by_img_id')
    def test_retrieve_image(self, mock_find):
        """Test downloading an image"""
        img_id = str(ObjectId())
        mock_image = Mock()
        mock_image.file_content = b"test content"
        mock_image.filename = "test.png"
        mock_find.return_value = mock_image

        response = self.client.get(f'/api/retrieve/{img_id}')
        self.assertEqual(response.status_code, 200)
        
        # Check if the response is JSON
        response_data = response.get_json()
        self.assertIsNotNone(response_data)
        self.assertEqual(response_data['filename'], "test.png")
        self.assertEqual(response_data['content_type'], "image/png")

if __name__ == '__main__':
    unittest.main()