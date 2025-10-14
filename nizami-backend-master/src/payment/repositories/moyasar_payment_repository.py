import logging
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
from uuid import UUID

from ..models import MoyasarInvoice, MoyasarWebhookEvent, MoyasarPayment, MoyasarPaymentSource
from ..enums import MoyasarPaymentStatus
logger = logging.getLogger(__name__)


def make_json_serializable(data):
    """Recursively convert datetime and UUID objects to strings for JSON serialization."""
    if isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, UUID):
        return str(data)
    else:
        return data


class MoyasarPaymentRepository:
    @transaction.atomic
    def save_invoice(self, moyasar_data: Dict[str, Any]) -> MoyasarInvoice:
        invoice = MoyasarInvoice.objects.create(
            id=moyasar_data['id'],
            status=moyasar_data.get('status', ''),
            amount=moyasar_data.get('amount', 0),
            currency=moyasar_data.get('currency', ''),
            description=moyasar_data.get('description', ''),
            logo_url=moyasar_data.get('logo_url'),
            amount_format=moyasar_data.get('amount_format'),
            url=moyasar_data.get('url'),
            callback_url=moyasar_data.get('callback_url'),
            expired_at=moyasar_data.get('expired_at'),
            back_url=moyasar_data.get('back_url'),
            success_url=moyasar_data.get('success_url'),
            metadata=moyasar_data.get('metadata') or {}
        )
        
        # If invoice has payments in response, save them too
        if 'payments' in moyasar_data and moyasar_data['payments']:
            for payment_data in moyasar_data['payments']:
                self.save_payment(payment_data, invoice=invoice)
        
        logger.info(f"Invoice saved to database: {invoice.id}")
        return invoice
    
    @transaction.atomic
    def upsert_invoice(self, moyasar_data: Dict[str, Any]) -> MoyasarInvoice:
        invoice_id = moyasar_data['id']
        try:
            invoice = MoyasarInvoice.objects.get(id=invoice_id)
            
            invoice.status = moyasar_data.get('status', invoice.status)
            invoice.amount = moyasar_data.get('amount', invoice.amount)
            invoice.currency = moyasar_data.get('currency', invoice.currency)
            invoice.description = moyasar_data.get('description', invoice.description)
            invoice.logo_url = moyasar_data.get('logo_url', invoice.logo_url)
            invoice.amount_format = moyasar_data.get('amount_format', invoice.amount_format)
            invoice.url = moyasar_data.get('url', invoice.url)
            invoice.callback_url = moyasar_data.get('callback_url', invoice.callback_url)
            invoice.expired_at = moyasar_data.get('expired_at') or invoice.expired_at
            invoice.back_url = moyasar_data.get('back_url', invoice.back_url)
            invoice.success_url = moyasar_data.get('success_url', invoice.success_url)
            invoice.metadata = moyasar_data.get('metadata') or invoice.metadata or {}
            
            invoice.save()
            logger.info(f"Updated existing invoice: {invoice_id}")
            
            if 'payments' in moyasar_data and moyasar_data['payments']:
                for payment_data in moyasar_data['payments']:
                    self.upsert_payment(payment_data)
            
            return invoice
            
        except MoyasarInvoice.DoesNotExist:
            invoice = self.save_invoice(moyasar_data)
            logger.info(f"Created new invoice: {invoice_id}")
            return invoice
    
    @transaction.atomic
    def save_payment(
        self, 
        moyasar_data: Dict[str, Any],
        source: Optional[MoyasarPaymentSource] = None,
        invoice: Optional[MoyasarInvoice] = None
    ) -> MoyasarPayment:
        if source is None and 'source' in moyasar_data and moyasar_data['source']:
            source = self._save_or_update_payment_source(moyasar_data['source'])
        
        if invoice is None and 'invoice_id' in moyasar_data:
            try:
                invoice = MoyasarInvoice.objects.get(id=moyasar_data['invoice_id'])
            except MoyasarInvoice.DoesNotExist:
                logger.warning(f"Invoice {moyasar_data['invoice_id']} not found")
        
        payment = MoyasarPayment.objects.create(
            id=moyasar_data['id'],
            status=moyasar_data.get('status', ''),
            amount=moyasar_data.get('amount', 0),
            fee=moyasar_data.get('fee', 0),
            currency=moyasar_data.get('currency', ''),
            refunded=moyasar_data.get('refunded', 0),
            refunded_at=moyasar_data.get('refunded_at'),
            captured=moyasar_data.get('captured', 0),
            captured_at=moyasar_data.get('captured_at'),
            voided_at=moyasar_data.get('voided_at'),
            description=moyasar_data.get('description', ''),
            amount_format=moyasar_data.get('amount_format'),
            fee_format=moyasar_data.get('fee_format'),
            refunded_format=moyasar_data.get('refunded_format'),
            captured_format=moyasar_data.get('captured_format'),
            ip=moyasar_data.get('ip'),
            callback_url=moyasar_data.get('callback_url'),
            metadata=moyasar_data.get('metadata') or {},
            invoice=invoice,
            source=source
        )
        
        logger.info(f"Payment saved to database: {payment.id}")
        return payment
    
    
    @transaction.atomic
    def upsert_payment(self, moyasar_data: Dict[str, Any]) -> MoyasarPayment:
        payment_id = moyasar_data['id']
        try:
            payment: MoyasarPayment = MoyasarPayment.objects.get(id=payment_id)
            is_final_status = MoyasarPaymentStatus.is_final_status(payment.status)
            if is_final_status:
                return payment          
            if 'source' in moyasar_data and moyasar_data['source']:
                if payment.source:
                    self._update_payment_source(payment.source, moyasar_data['source'])
                else:
                    payment.source = self._save_or_update_payment_source(moyasar_data['source'])
            
            payment.status = moyasar_data.get('status', payment.status)
            payment.amount = moyasar_data.get('amount', payment.amount)
            payment.fee = moyasar_data.get('fee', payment.fee)
            payment.currency = moyasar_data.get('currency', payment.currency)
            payment.refunded = moyasar_data.get('refunded', payment.refunded)
            payment.refunded_at = moyasar_data.get('refunded_at') or payment.refunded_at
            payment.captured = moyasar_data.get('captured', payment.captured)
            payment.captured_at = moyasar_data.get('captured_at') or payment.captured_at
            payment.voided_at = moyasar_data.get('voided_at') or payment.voided_at
            payment.description = moyasar_data.get('description', payment.description)
            payment.amount_format = moyasar_data.get('amount_format', payment.amount_format)
            payment.fee_format = moyasar_data.get('fee_format', payment.fee_format)
            payment.refunded_format = moyasar_data.get('refunded_format', payment.refunded_format)
            payment.captured_format = moyasar_data.get('captured_format', payment.captured_format)
            payment.ip = moyasar_data.get('ip', payment.ip)
            payment.callback_url = moyasar_data.get('callback_url', payment.callback_url)
            payment.metadata = moyasar_data.get('metadata') or payment.metadata or {}
            
            payment.save()
            logger.info(f"Updated existing payment: {payment_id}")
            return payment
            
        except MoyasarPayment.DoesNotExist:
            payment = self.save_payment(moyasar_data)
            logger.info(f"Created new payment: {payment_id}")
            return payment
    
    def _save_or_update_payment_source(self, source_data: Dict[str, Any]) -> MoyasarPaymentSource:
        token = source_data.get('token')
        gateway_id = source_data.get('gateway_id')
        reference_number = source_data.get('reference_number')
        authorization_code = source_data.get('authorization_code')
        
        existing_source = None
        
        if token:
            existing_source = MoyasarPaymentSource.objects.filter(token=token).first()
            if existing_source:
                self._update_payment_source(existing_source, source_data)
                return existing_source
        
        if gateway_id and reference_number:
            existing_source = MoyasarPaymentSource.objects.filter(
                gateway_id=gateway_id,
                reference_number=reference_number
            ).first()
            if existing_source:
                self._update_payment_source(existing_source, source_data)
                return existing_source
        
        if authorization_code:
            existing_source = MoyasarPaymentSource.objects.filter(
                authorization_code=authorization_code
            ).first()
            if existing_source:
                self._update_payment_source(existing_source, source_data)
                return existing_source
        
        source = MoyasarPaymentSource.objects.create(
            type=source_data.get('type', ''),
            company=source_data.get('company'),
            name=source_data.get('name'),
            number=source_data.get('number'),
            gateway_id=gateway_id,
            reference_number=reference_number,
            token=token,
            message=source_data.get('message'),
            transaction_url=source_data.get('transaction_url'),
            response_code=source_data.get('response_code'),
            authorization_code=authorization_code,
            issuer_name=source_data.get('issuer_name'),
            issuer_country=source_data.get('issuer_country'),
            issuer_card_type=source_data.get('issuer_card_type'),
            issuer_card_category=source_data.get('issuer_card_category')
        )
        logger.info(f"Created new payment source - token: {token}, gateway_id: {gateway_id}")
        return source
    
    def _update_payment_source(self, source: MoyasarPaymentSource, source_data: Dict[str, Any]):
        source.type = source_data.get('type', source.type)
        source.company = source_data.get('company', source.company)
        source.name = source_data.get('name', source.name)
        source.number = source_data.get('number', source.number)
        source.gateway_id = source_data.get('gateway_id', source.gateway_id)
        source.reference_number = source_data.get('reference_number', source.reference_number)
        source.token = source_data.get('token', source.token)
        source.message = source_data.get('message', source.message)
        source.transaction_url = source_data.get('transaction_url', source.transaction_url)
        source.response_code = source_data.get('response_code', source.response_code)
        source.authorization_code = source_data.get('authorization_code', source.authorization_code)
        source.issuer_name = source_data.get('issuer_name', source.issuer_name)
        source.issuer_country = source_data.get('issuer_country', source.issuer_country)
        source.issuer_card_type = source_data.get('issuer_card_type', source.issuer_card_type)
        source.issuer_card_category = source_data.get('issuer_card_category', source.issuer_card_category)
        source.save()
        logger.info(f"Updated payment source: {source.uuid}")

    def check_duplicate_event(self, event_id: str) -> bool:
        """Check if webhook event was already processed."""
        return MoyasarWebhookEvent.objects.filter(event_id=event_id).exists()
    
    @transaction.atomic
    def create_webhook_event(self, event_data: Dict[str, Any]) -> MoyasarWebhookEvent:
        webhook_event = MoyasarWebhookEvent.objects.create(
            event_id=event_data['id'],
            event_type=event_data['type'],
            account_name=event_data.get('account_name'),
            live=event_data['live'],
            event_created_at=event_data['created_at'],
            data=make_json_serializable(event_data.get('data', {}))
        )
        
        logger.info(f"Webhook event saved to database: {webhook_event.event_id} ({webhook_event.event_type})")
        return webhook_event
