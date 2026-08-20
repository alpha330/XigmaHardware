from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from apps.payment.services.zarinpal import ZarinPalGateway


class ZarinPalGatewayTests(SimpleTestCase):
    def setUp(self):
        config = SimpleNamespace(
            effective_api_key='merchant-id',
            mode='test',
            name='ZarinPal',
            gateway_type='zarinpal',
        )
        self.gateway = ZarinPalGateway(config)

    @patch('apps.payment.services.zarinpal.requests.post')
    def test_create_payment_uses_default_tls_verification(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'data': {'code': 100, 'authority': 'authority-123'},
        }
        post.return_value = response

        result = self.gateway.create_payment(
            amount=10000,
            description='test payment',
            payer_name='Test User',
            payer_email='test@example.com',
            payer_mobile='09120000000',
            callback_url='https://example.com/callback',
        )

        self.assertTrue(result['success'])
        self.assertNotIn('verify', post.call_args.kwargs)
        response.raise_for_status.assert_called_once_with()

    @patch('apps.payment.services.zarinpal.requests.post')
    def test_verify_payment_returns_safe_failure_for_http_errors(self, post):
        post.side_effect = requests.ConnectionError('gateway unavailable')

        result = self.gateway.verify_payment('authority-123', 10000)

        self.assertFalse(result['success'])
        self.assertIn('gateway unavailable', result['error'])
