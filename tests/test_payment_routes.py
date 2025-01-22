import unittest
from unittest.mock import patch, Mock
from app import app

class TestPaymentRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('paypalrestsdk.Payment')
    def test_payment_creation(self, mock_payment):
        """Test PayPal payment creation"""
        mock_payment_instance = Mock()
        mock_payment_instance.create.return_value = True
        mock_payment_instance.links = [
            Mock(rel='approval_url', href='http://paypal.com/approve')
        ]
        mock_payment.return_value = mock_payment_instance

        response = self.client.get('/pay')
        self.assertEqual(response.status_code, 302)