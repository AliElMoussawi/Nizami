
import logging
from typing import Optional, Dict, Any
from django.db import transaction

from ..interfaces import PaymentGatewayInterface
from ..enums import MoyasarPaymentStatus, PaymentSourceType
from ..repositories.moyasar_payment_repository import MoyasarPaymentRepository
from ..models import PaymentUserSubscription, UserPaymentSource, MoyasarPayment
from ..serializers.moyasar_serializers import (
    MoyasarInvoiceSerializer,
    MoyasarPaymentSerializer
)
from src.subscription.services import upgrade_user_subscription_user_id_and_plan_id
from src.common.generic_api_gateway import WebhookProcessingStatus, validate_and_log_response
from src.users.models import User
from src.common.utils import send_payment_success_email, send_payment_failure_email

logger = logging.getLogger(__name__)


@transaction.atomic
def store_user_payment_source(payment: MoyasarPayment) -> Optional[UserPaymentSource]:
    # Only process paid payments
    if payment.status != MoyasarPaymentStatus.PAID:
        logger.debug(f"Payment {payment.id} not paid (status: {payment.status})")
        return None
    
    # Check if payment has metadata with user_id
    if not payment.metadata or not payment.metadata.get('user_id'):
        logger.warning(f"Payment {payment.id} missing user_id in metadata")
        return None
    
    # Check if payment has a source with token
    if not payment.source or not payment.source.token:
        logger.debug(f"Payment {payment.id} has no tokenizable payment source")
        return None
    
    user_id = payment.metadata.get('user_id')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for payment {payment.id}")
        return None
    
    payment_source = payment.source
    token = payment_source.token
    
    # Check if this payment source already exists for user
    existing_user_source = UserPaymentSource.objects.filter(
        user=user,
        token=token
    ).first()
    
    if existing_user_source:
        logger.info(f"Payment source {token} already exists for user {user.id}")
        # Update is_active if needed
        if not existing_user_source.is_active:
            existing_user_source.is_active = True
            existing_user_source.is_default = True
            existing_user_source.save()
            logger.info(f"Reactivated payment source {token} for user {user.id}")
        return existing_user_source
    
    nickname = None
    if payment_source.number:
        company_or_type = payment_source.company or payment_source.type
        nickname = f"{company_or_type} •••• {payment_source.number[-4:]}"
    elif payment_source.company:
        nickname = payment_source.company
    
    user_payment_source = UserPaymentSource.objects.create(
        user=user,
        payment_source=payment_source,
        token=token,
        token_type=payment_source.type,
        is_default=True,
        is_active=True,
        nickname=nickname
    )
    
    logger.info(f"Created payment source {token} for user {user.id} (default: {user_payment_source.is_default})")
    return user_payment_source


@transaction.atomic
def create_subscription_from_payment(payment) -> Optional[Any]:
    if payment.status != MoyasarPaymentStatus.PAID or not payment.metadata:
        logger.debug(f"Payment {payment.id} not eligible for subscription creation (status: {payment.status})")
        return None
    
    user_id = payment.metadata.get('user_id')
    plan_id = payment.metadata.get('plan_id')
    
    if not user_id or not plan_id:
        logger.warning(f"Payment {payment.id} missing user_id or plan_id in metadata")
        return None
    
    # Check if subscription link already exists
    if hasattr(payment, 'subscription_link'):
        logger.info(f"Payment {payment.id} already linked to subscription")
        return payment.subscription_link
    
    try:
        # Create or upgrade subscription
        user_subscription = upgrade_user_subscription_user_id_and_plan_id(user_id, plan_id)
        
        # Create the link between payment and subscription
        payment_subscription_link = PaymentUserSubscription.objects.create(
            payment=payment,
            user_subscription=user_subscription
        )
        logger.info(f"Created subscription link: Payment {payment.id} -> Subscription {user_subscription.uuid}")
        return payment_subscription_link
        
    except Exception as e:
        logger.error(f"Failed to create subscription for payment {payment.id}: {str(e)}", exc_info=True)
        return None


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
        
        return invoice

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
        user_email: Optional[str] = None,
        user_id: Optional[str] = None,
        cart_id: Optional[str] = None,
        plan_id : Optional[str] = None
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
            user_email=user_email,
            user_id=user_id,
            cart_id=cart_id,
            plan_id=plan_id,
        )
        
        validated_data = validate_and_log_response(
            response,
            MoyasarPaymentSerializer,
            "payment creation",
            source="Payment Gateway"
        )
        
        payment = self.repository.save_payment(validated_data)
        
        logger.info(f"Payment created successfully: {validated_data.get('id')}")
        
        return payment
    
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
        
        # Store payment source if payment is successful
        store_user_payment_source(payment)
        
        # Create subscription from payment if eligible
        create_subscription_from_payment(payment)
        
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
    
    @transaction.atomic
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
            
            _ = self.repository.create_webhook_event(event_data=event_data)

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

            # Handle payment based on status
            if payment.status == MoyasarPaymentStatus.PAID:
                store_user_payment_source(payment)
                create_subscription_from_payment(payment)
                
                # Send payment success email
                try:
                    if payment.metadata and payment.metadata.get('user_id'):
                        user = User.objects.get(id=payment.metadata['user_id'])
                        send_payment_success_email(user, payment)
                except Exception as e:
                    logger.error(f"Failed to send payment success email: {e}")
                    
            elif payment.status == MoyasarPaymentStatus.FAILED:
                # Send payment failure email
                try:
                    if payment.metadata and payment.metadata.get('user_id'):
                        user = User.objects.get(id=payment.metadata['user_id'])
                        send_payment_failure_email(user, payment)
                except Exception as e:
                    logger.error(f"Failed to send payment failure email: {e}")
            
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
