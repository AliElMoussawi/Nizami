from http import HTTPStatus
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import IsValidMoyasarSignature
from .serializers.moyasar_serializers import (
    MoyasarWebhookSerializer,
    UserPaymentSourceSerializer,
    PaymentDetailSerializer,
)
from .services.moyasar_payment_service import get_moyasar_payment_service
from .models import UserPaymentSource, MoyasarPayment
from src.common.generic_api_gateway import WebhookProcessingStatus

import logging
logger = logging.getLogger(__name__)


class MoyasarWebhookView(APIView):
    permission_classes = (IsValidMoyasarSignature,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_service = get_moyasar_payment_service()

    @transaction.atomic
    def post(self, request, format=None):
        serializer = MoyasarWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            logger.info(f"Webhook payload validation failed: {serializer.errors}")
            return Response(
                {
                    "status": WebhookProcessingStatus.VALIDATION_ERROR.value,
                    "message": "Invalid webhook payload",
                    "errors": serializer.errors
                },
                status=HTTPStatus.OK
            )
        
        result = self.payment_service.process_webhook(event_data=serializer.validated_data)
        if result["status"] == WebhookProcessingStatus.SUCCESS.value:
            return Response(result, status=HTTPStatus.OK)
        elif result["status"] == WebhookProcessingStatus.DUPLICATE_EVENT.value:
            return Response(result, status=HTTPStatus.OK)
        elif result["status"] == WebhookProcessingStatus.INVALID_EVENT_TYPE.value:
            return Response(result, status=HTTPStatus.OK)
        else:
            return Response(result, status=HTTPStatus.INTERNAL_SERVER_ERROR)


class PaymentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = str(request.user.id)
        
        payments = MoyasarPayment.objects.filter(
            metadata__customer_id=user_id
        ).select_related('source', 'invoice').order_by('-created_at')
        
        serializer = PaymentDetailSerializer(payments, many=True)
        return Response(serializer.data, status=HTTPStatus.OK)


class PaymentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = get_object_or_404(MoyasarPayment, id=payment_id)
            serializer = PaymentDetailSerializer(payment)
            return Response(serializer.data, status=HTTPStatus.OK)
        
        except Exception as e:
            logger.error(f"Failed to retrieve payment: {str(e)}", exc_info=True)
            return Response(
                {"error": "Payment not found"},
                status=HTTPStatus.NOT_FOUND
            )


class SyncPaymentStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        payment_service = get_moyasar_payment_service()
        
        try:
            payment = payment_service.fetch_and_sync_payment(str(payment_id))
            payment_serializer = PaymentDetailSerializer(payment)
            return Response(payment_serializer.data, status=HTTPStatus.OK)
        
        except Exception as e:
            logger.error(f"Failed to sync payment status: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to sync payment status", "detail": str(e)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )


class UserPaymentSourceListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sources = UserPaymentSource.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('payment_source')
        
        serializer = UserPaymentSourceSerializer(sources, many=True)
        return Response(serializer.data, status=HTTPStatus.OK)


class PaymentSourceDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, source_id):
        try:
            source = get_object_or_404(
                UserPaymentSource,
                uuid=source_id,
                user=request.user
            )
            
            source.is_active = False
            source.save()
            
            return Response(
                {"message": "Payment source removed successfully"},
                status=HTTPStatus.OK
            )
        
        except Exception as e:
            logger.error(f"Failed to remove payment source: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to remove payment source"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    def patch(self, request, source_id):
        try:
            source = get_object_or_404(
                UserPaymentSource,
                uuid=source_id,
                user=request.user
            )
            
            if 'nickname' in request.data:
                source.nickname = request.data['nickname']
            
            if request.data.get('set_as_default'):
                source.is_default = True
            
            source.save()
            
            serializer = UserPaymentSourceSerializer(source)
            return Response(serializer.data, status=HTTPStatus.OK)
        
        except Exception as e:
            logger.error(f"Failed to update payment source: {str(e)}", exc_info=True)
            return Response(
                {"error": "Failed to update payment source"},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
