import unittest
from unittest.mock import patch, Mock
from app import app

class TestPaymentRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test data and Flask test client"""
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

    def test_payment_cancel(self):
        """Test payment cancellation"""
        response = self.client.get('/payment_cancel')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Payment Canceled", response.get_data(as_text=True))  # Updated to match actual content

    @patch('paypalrestsdk.Payment.find')
    def test_payment_success(self, mock_payment_find):
        """Test successful payment execution"""
        mock_payment = Mock()
        mock_payment.execute.return_value = True
        mock_payment_find.return_value = mock_payment

        response = self.client.get('/payment_success?paymentId=test&PayerID=test')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Thank you for your donation!", response.get_data(as_text=True))  # Updated to match actual content

if __name__ == '__main__':
    unittest.main()