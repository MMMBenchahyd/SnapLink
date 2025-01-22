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

if __name__ == '__main__':
    unittest.main()