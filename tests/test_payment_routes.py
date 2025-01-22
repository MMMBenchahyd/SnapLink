import unittest
from unittest.mock import patch, Mock
from app import app

class TestPaymentRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()