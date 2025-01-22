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

    @patch('paypalrestsdk.Payment.find')
    def test_payment_success(self, mock_payment_find):
        """Test successful payment execution"""
        mock_payment = Mock()
        mock_payment.execute.return_value = True
        mock_payment_find.return_value = mock_payment

        response = self.client.get('/payment_success?paymentId=test&PayerID=test')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Payment successful!", response.get_data(as_text=True))

    def test_payment_cancel(self):
        """Test payment cancellation"""
        response = self.client.get('/payment_cancel')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Payment canceled.", response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()