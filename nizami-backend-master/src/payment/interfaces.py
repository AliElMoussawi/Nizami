from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .enums import PaymentSourceType


class PaymentGatewayInterface(ABC):

    @abstractmethod
    def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def fetch_invoice(self, invoice_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def create_payment(
        self,
        payment_source_type: PaymentSourceType,
        given_id: str,
        amount: int,
        currency: str,
        description: str,
        callback_url: str,
        card_name: Optional[str] = None,
        card_number: Optional[str] = None,
        card_month: Optional[int] = None,
        card_year: Optional[int] = None,
        card_cvc: Optional[int] = None,
        statement_descriptor: Optional[str] = None,
        token: Optional[str] = None,
        save_card: bool = False,
        apply_coupon: bool = False,
        customer_email: Optional[str] = None,
        customer_id: Optional[str] = None,
        cart_id: Optional[str] = None
    ) -> Dict[str, Any]:
        pass

