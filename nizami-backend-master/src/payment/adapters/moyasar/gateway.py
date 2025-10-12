from src import settings
from src.common.generic_api_gateway import APIGateway
from ...enums import PaymentSourceType
from ...interfaces import PaymentGatewayInterface


class MoyasarGateway(APIGateway, PaymentGatewayInterface):
    SOURCE = 'Moyasar-Payment-Gateway'
    def build_url(self, uri='') -> str:
        return f"{settings.MOYASAR_URL}{uri}"
    
    def get_auth(self):
        return (settings.MOYASAR_SECRET_KEY, '')

    def fetch_payment(self, payment_intent_id):
        fetch_payment_id_path = f"payments/{payment_intent_id}"
        fetch_payment_url = self.build_url(uri=fetch_payment_id_path)
        return self.send_request(fetch_payment_url, "GET")
    
    def fetch_invoice(self, invoice_id):
        fetch_invoice_path = f"invoices/{invoice_id}"
        fetch_invoice_url = self.build_url(uri=fetch_invoice_path)
        return self.send_request(fetch_invoice_url, "GET")

    def create_invoice(self, amount, currency, description, callback_url, success_url=None, back_url=None, expired_at=None, meta_data_user_id=None, meta_data_payment_id=None):
        invoice_path = "invoices"
        invoice_url = self.build_url(uri=invoice_path)
        
        # Build the payload
        payload = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "callback_url": callback_url,
        }
        
        # Add optional fields if provided
        if success_url:
            payload["success_url"] = success_url
        if back_url:
            payload["back_url"] = back_url
        if expired_at:
            payload["expired_at"] = expired_at
        
        # Add metadata if provided
        if meta_data_user_id or meta_data_payment_id:
            payload["metadata"] = {}
            if meta_data_user_id:
                payload["metadata"]["user_id"] = meta_data_user_id
            if meta_data_payment_id:
                payload["metadata"]["payment_id"] = meta_data_payment_id
        
        # Send the request and return response
        return self.send_request(invoice_url, "POST", data=payload)
    
    def create_payment(
        self,
        payment_source_type: PaymentSourceType,
        given_id: str,
        amount: int,
        currency: str,
        description: str,
        callback_url: str,
        # optional card or token fields
        card_name: str = None,
        card_number: str = None,
        card_month: int = None,
        card_year: int = None,
        card_cvc: int = None,
        statement_descriptor: str = None,
        token: str = None,
        save_card: bool = False,
        apply_coupon: bool = False,
        customer_email: str = None,
        customer_id: str = None,
        cart_id: str = None
        ):
        payment_path = "payments"
        payment_url = self.build_url(uri=payment_path)
        
        # Build source based on payment type
        if payment_source_type == PaymentSourceType.TOKEN:
            if not token:
                raise ValueError("Token is required for TOKEN payment source type")
            source = {
                "type": "token",
                "token": token
            }
        elif payment_source_type == PaymentSourceType.CREDIT_CARD:
            source = {
                "type": "creditcard",
                "name": card_name,
                "number": card_number,
                "month": card_month,
                "year": card_year,
                "cvc": card_cvc,
                "statement_descriptor": statement_descriptor,
                "3ds": True,
                "manual": False,
                "save_card": save_card
            }
        else:
            raise ValueError(f"The required payment source type is not implemented yet: {payment_source_type}")

        payload = {
            "given_id": given_id,
            "amount": amount,
            "currency": currency,
            "description": description,
            "callback_url": callback_url,
            "source": source,
            "metadata": {
                "cart_id": cart_id,
                "customer_email": customer_email,
                "customer_id": customer_id
            },
            "apply_coupon": apply_coupon
        }

        # Clean up metadata - remove None values
        payload["metadata"] = {k: v for k, v in payload["metadata"].items() if v is not None}
        
        return self.send_request(payment_url, "POST", data=payload)

    def get_invoice(self, id):
        invoice_path = "invoices"
        invoice_url = self.build_url(uri=f"{invoice_path}/{id}")
        return self.send_request(invoice_url)