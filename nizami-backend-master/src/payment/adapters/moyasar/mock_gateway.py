import uuid
from typing import Dict, Any, Optional
from ...interfaces import PaymentGatewayInterface
from ...enums import PaymentSourceType


class MockGateway(PaymentGatewayInterface):
    def __init__(self):
        self.fetch_payment_called = False
        self.fetch_invoice_called = False
        self.create_invoice_called = False
        self.create_payment_called = False
    
    def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        self.fetch_payment_called = True
        return {
            'id': payment_id,
            'status': 'paid',
            'amount': 10000,
            'currency': 'SAR',
            'fee': 150,
            'description': 'Mock payment',
            'metadata': {}
        }
    
    def fetch_invoice(self, invoice_id: str) -> Dict[str, Any]:
        self.fetch_invoice_called = True
        return {
            'id': invoice_id,
            'status': 'pending',
            'amount': 10000,
            'currency': 'SAR',
            'description': 'Mock invoice',
            'callback_url': 'https://mock.gateway.com/callback',
            'url': f'https://mock.gateway.com/invoice/{invoice_id}',
            'metadata': {}
        }
    
    def create_invoice(
        self,
        amount: int,
        currency: str,
        description: str,
        callback_url: str,
        success_url: Optional[str] = None,
        back_url: Optional[str] = None,
        expired_at: Optional[str] = None,
        meta_data_user_id: Optional[str] = None,
        meta_data_payment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        self.create_invoice_called = True
        return {
            'id': str(uuid.uuid4()),
            'status': 'pending',
            'amount': amount,
            'currency': currency,
            'description': description,
            'callback_url': callback_url,
            'url': 'https://mock.gateway.com/invoice/123',
            'metadata': {}
        }
    
    def create_payment(
        self,
        payment_source_type: PaymentSourceType,
        given_id: str,
        amount: int,
        currency: str,
        description: str,
        callback_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        self.create_payment_called = True
        return {
            'id': str(uuid.uuid4()),
            'status': 'initiated',
            'amount': amount,
            'currency': currency,
            'description': description,
            'callback_url': callback_url,
            'fee': 0,
            'metadata': {}
        }

