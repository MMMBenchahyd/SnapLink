import unittest
from unittest.mock import patch, Mock
import io
from app import app
from bson import ObjectId
from datetime import datetime, timezone

class TestImageRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.user_id = str(ObjectId())
        with self.client.session_transaction() as session:
            session['user_id'] = self.user_id

    def test_upload_image(self):
        """Test image upload"""
        with patch('models.User.User.search_id') as mock_user:
            mock_user.return_value = Mock(user_id=self.user_id)
            with patch('models.image.Image.creating_by_objectid') as mock_create:
                mock_image = Mock()
                mock_create.return_value = mock_image
                with patch('models.image.Image.save'):
                    data = {
                        'content': 'test.png',
                        'file': (io.BytesIO(b"test content"), 'test.png')
                    }
                    response = self.client.post('/upload',  # Ensure this matches your route
                        data=data,
                        content_type='multipart/form-data'
                    )
                    self.assertEqual(response.status_code, 302)
    
    def test_update_image(self):
        """Test image update"""
        img_id = str(ObjectId())
        with patch('models.image.Image.find_by_img_id') as mock_find:
            mock_image = Mock()
            mock_image.img_id = img_id
            mock_find.return_value = mock_image
            
            response = self.client.post(f'/update/{img_id}',
                data={'newname': 'updated.png'}
            )
            self.assertEqual(response.status_code, 302)
    
    def test_get_image(self):
        """Test retrieving an image"""
        img_id = str(ObjectId())
        with patch('models.image.Image.find_by_img_id') as mock_find:
            mock_image = Mock()
            mock_image.file_content = b"test content"
            mock_find.return_value = mock_image
            
            response = self.client.get(f'/image/{img_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, b"test content")

if __name__ == '__main__':
    unittest.main()