import unittest
from unittest.mock import patch
from models.image import Image
from bson import ObjectId
from datetime import datetime, timezone

class TestImageModel(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.user_id = str(ObjectId())
        self.test_image = Image(
            uploaded_by=self.user_id,
            filename="test.png",
            file_content=b"test_content",
            img_id=str(ObjectId()),
            date_created=datetime.now(timezone.utc)
        )

    def test_image_creation(self):
        """Test image object creation"""
        self.assertEqual(self.test_image.filename, "test.png")
        self.assertEqual(self.test_image.uploaded_by, self.user_id)
        self.assertEqual(self.test_image.file_content, b"test_content")
        self.assertIsInstance(self.test_image.date_created, datetime)
        self.assertIsNotNone(self.test_image.img_id)

    def test_creating_by_objectid(self):
        """Test creating image using the factory method"""
        new_image = Image.creating_by_objectid(
            uploaded_by=self.user_id,
            filename="new.png",
            file_content=b"new_content"
        )
        self.assertEqual(new_image.filename, "new.png")
        self.assertEqual(new_image.uploaded_by, self.user_id)
        self.assertEqual(new_image.file_content, b"new_content")
        self.assertIsInstance(new_image.date_created, datetime)

    @patch('models.image.Image.find_by_img_id')
    def test_retrieve_nonexistent_image(self, mock_find):
        """Test retrieving a nonexistent image"""
        mock_find.return_value = None
        result = Image.find_by_img_id("nonexistent_id")
        self.assertIsNone(result)