from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.chats.models import Chat
from src.common.permissions import IsAdminPermission
from src.common.viewsets import CreateViewSet
from src.user_requests.enums import LegalAssistanceRequestStatus
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
        user = self.request.user
        chat_id = serializer.validated_data['chat_id']
        
        try:
            chat = Chat.objects.get(id=chat_id, user=user)
        except Chat.DoesNotExist:
            raise Http404("Chat not found")
        
        existing_request = LegalAssistanceRequest.objects.filter(
            user=user,
            chat=chat
        ).first()
        
        if existing_request:
            raise ValidationError({
                'chat_id': ['A legal assistance request already exists for this chat.']
            })
        
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
        instance = serializer.instance
        new_status = serializer.validated_data['status']
        in_charge = serializer.validated_data.get('in_charge')
        
        if new_status == LegalAssistanceRequestStatus.IN_PROGRESS.value:
            instance.mark_in_progress(in_charge)
        elif new_status == LegalAssistanceRequestStatus.CLOSED.value:
            instance.mark_closed(in_charge)
        else:
            instance.status = new_status
            if in_charge:
                instance.in_charge = in_charge
            instance.save(update_fields=['status'] + (['in_charge'] if in_charge else []))
