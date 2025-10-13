
import logging
from typing import Optional, Dict, Any

from ..interfaces import PaymentGatewayInterface
from ..enums import PaymentSourceType
from ..repositories.moyasar_payment_repository import MoyasarPaymentRepository
from ..serializers.moyasar_serializers import (
    MoyasarInvoiceSerializer,
    MoyasarPaymentSerializer
)
from src.common.generic_api_gateway import WebhookProcessingStatus, validate_and_log_response

logger = logging.getLogger(__name__)


class PaymentService:
    
    def __init__(self, gateway: PaymentGatewayInterface):
        self.gateway = gateway
        self.repository = MoyasarPaymentRepository()
        logger.info(f"PaymentService initialized with gateway: {gateway.__class__.__name__}")
    
    def create_invoice(
        self,
        amount: int,
        currency: str,
        description: str,
        callback_url: str,
        success_url: Optional[str] = None,
        back_url: Optional[str] = None,
        expired_at: Optional[str] = None,
        user_id: Optional[str] = None,
        payment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        response = self.gateway.create_invoice(
            amount=amount,
            currency=currency,
            description=description,
            callback_url=callback_url,
            success_url=success_url,
            back_url=back_url,
            expired_at=expired_at,
            meta_data_user_id=user_id,
            meta_data_payment_id=payment_id
        )
        
        validated_data = validate_and_log_response(
            response,
            MoyasarInvoiceSerializer,
            "invoice creation",
            source="Payment Gateway"
        )
        
        invoice = self.repository.save_invoice(validated_data)
        
        logger.info(f"Invoice created successfully: {validated_data.get('id')}")
        
        return {
            'success': True,
            'invoice': invoice,
            'gateway_response': response
        }
    
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
        response = self.gateway.create_payment(
            payment_source_type=payment_source_type,
            given_id=given_id,
            amount=amount,
            currency=currency,
            description=description,
            callback_url=callback_url,
            card_name=card_name,
            card_number=card_number,
            card_month=card_month,
            card_year=card_year,
            card_cvc=card_cvc,
            statement_descriptor=statement_descriptor,
            token=token,
            save_card=save_card,
            apply_coupon=apply_coupon,
            customer_email=customer_email,
            customer_id=customer_id,
            cart_id=cart_id
        )
        
        validated_data = validate_and_log_response(
            response,
            MoyasarPaymentSerializer,
            "payment creation",
            source="Payment Gateway"
        )
        
        payment = self.repository.save_payment(validated_data)
        
        logger.info(f"Payment created successfully: {validated_data.get('id')}")
        
        return {
            'success': True,
            'payment': payment,
            'gateway_response': response
        }
    
    def fetch_and_sync_payment(self, payment_id: str) -> Dict[str, Any]:
        response = self.gateway.fetch_payment(payment_id)
        
        validated_data = validate_and_log_response(
            response,
            MoyasarPaymentSerializer,
            "payment fetch",
            source="Payment Gateway"
        )
        
        payment = self.repository.upsert_payment(validated_data)
        
        logger.info(f"Payment synced successfully: {payment_id}")
        
        return payment
    
    def fetch_and_sync_invoice(self, invoice_id: str) -> Dict[str, Any]:
        if not invoice_id:
            return None 
        response = self.gateway.fetch_invoice(invoice_id)
        
        validated_data = validate_and_log_response(
            response,
            MoyasarInvoiceSerializer,
            "invoice fetch",
            source="Payment Gateway"
        )
        
        invoice = self.repository.upsert_invoice(validated_data)
        
        logger.info(f"Invoice synced successfully: {invoice_id}")
        
        return invoice
    
    def process_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            is_duplicate = self.repository.check_duplicate_event(event_id=event_data["id"])
            if is_duplicate:
                logger.info(f"Duplicate webhook event received: {event_data['id']}")
                return {
                    "status": WebhookProcessingStatus.DUPLICATE_EVENT.value,
                    "message": f"Event {event_data['id']} already processed",
                    "event_id": event_data["id"]
                }
            
            webhook_event = self.repository.create_webhook_event(event_data=event_data)

            payment_data = event_data['data']
            
            invoice = None
            if payment_data.get('invoice_id'):
                invoice_id = payment_data['invoice_id']
                logger.info(f"Fetching invoice {invoice_id} from gateway")
                invoice = self.fetch_and_sync_invoice(invoice_id)
            
            payment = self.repository.upsert_payment(payment_data)
            
            if invoice and not payment.invoice:
                payment.invoice = invoice
                payment.save()
                logger.info(f"Linked invoice {invoice.id} to payment {payment.id}")

            logger.info(f"Webhook event processed successfully: {event_data['id']}")
            
            return {
                "status": WebhookProcessingStatus.SUCCESS.value,
                "message": f"Event {event_data['id']} processed successfully",
                "event_id": event_data["id"]
            }
            
        except ValueError as e:
            logger.error(f"Validation error processing webhook: {str(e)}")
            return {
                "status": WebhookProcessingStatus.VALIDATION_ERROR.value,
                "message": str(e),
                "event_id": event_data.get("id")
            }
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
            return {
                "status": WebhookProcessingStatus.PROCESSING_ERROR.value,
                "message": f"Error processing webhook: {str(e)}",
                "event_id": event_data.get("id")
            }
