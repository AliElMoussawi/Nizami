from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.common.permissions import IsAdminPermission
from src.common.viewsets import CreateViewSet
from src.user_requests.factory import LegalCompanyHandlerFactory
from src.user_requests.models import LegalAssistanceRequest
from src.user_requests.serializers import (
    CreateLegalAssistanceRequestSerializer,
    LegalAssistanceRequestSerializer,
    UpdateLegalAssistanceRequestStatusSerializer,
)


class CreateLegalAssistanceRequestViewSet(CreateViewSet):
    queryset = LegalAssistanceRequest.objects.all()
    input_serializer_class = CreateLegalAssistanceRequestSerializer
    output_serializer_class = LegalAssistanceRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def perform_create(self, serializer):
        """Create legal assistance request using factory pattern"""
        user = self.request.user
        chat_id = serializer.validated_data['chat_id']
        
        from src.chats.models import Chat
        try:
            chat = Chat.objects.get(id=chat_id, user=user)
        except Chat.DoesNotExist:
            raise Http404("Chat not found")
        
        # Check if a request already exists for this chat
        existing_request = LegalAssistanceRequest.objects.filter(
            user=user,
            chat=chat
        ).first()
        
        if existing_request:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'chat_id': ['A legal assistance request already exists for this chat.']
            })
        
        # Use factory to handle the request
        legal_assistance_request = LegalCompanyHandlerFactory.handle_legal_assistance_request(user, chat)
        serializer.instance = legal_assistance_request


class ListLegalAssistanceRequestsViewSet(ReadOnlyModelViewSet):
    queryset = LegalAssistanceRequest.objects.select_related('user', 'chat').all()
    serializer_class = LegalAssistanceRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def get_queryset(self):
        return self.queryset.order_by('-created_at_ts')


class UpdateLegalAssistanceRequestStatusViewSet(ModelViewSet):
    queryset = LegalAssistanceRequest.objects.all()
    serializer_class = UpdateLegalAssistanceRequestStatusSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def perform_update(self, serializer):
        """Update status and timestamps accordingly"""
        instance = serializer.instance
        new_status = serializer.validated_data['status']
        
        from src.user_requests.enums import LegalAssistanceRequestStatus
        
        if new_status == LegalAssistanceRequestStatus.IN_PROGRESS.value:
            instance.mark_in_progress()
        elif new_status == LegalAssistanceRequestStatus.CLOSED.value:
            instance.mark_closed()
        else:
            instance.status = new_status
            instance.save(update_fields=['status'])
