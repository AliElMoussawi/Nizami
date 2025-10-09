import os

from django.http import FileResponse, Http404
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from src import settings
from src.chats.models import Chat, Message, MessageFile
from src.chats.serializers import CreateChatSerializer, ListChatsSerializer, ListMessagesSerializer, \
    CreateMessageSerializer, CreateMessageFileSerializer, ListMessageFileSerializer, UpdateChatSerializer
from src.common.pagination import PerPagePagination, IDBasedPagination
from src.common.viewsets import CreateViewSet


class CreateChatViewSet(CreateViewSet):
    queryset = Chat.objects.all()
    input_serializer_class = CreateChatSerializer
    output_serializer_class = ListChatsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []


class DeleteChatViewSet(ModelViewSet):
    queryset = Chat.objects.all()
    input_serializer_class = CreateChatSerializer
    output_serializer_class = ListChatsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise Http404

        super().perform_destroy(instance)


class UpdateChatViewSet(ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = UpdateChatSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user.id:
            raise Http404

        super().perform_update(serializer)


class ListChatsViewSet(ReadOnlyModelViewSet):
    queryset = Chat.objects.all().order_by('-created_at')
    serializer_class = ListChatsSerializer
    pagination_class = PerPagePagination
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    filter_backends = [SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class RetrieveChatViewSet(ReadOnlyModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ListChatsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []

class ListMessagesViewSet(ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    pagination_class = IDBasedPagination
    serializer_class = ListMessagesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def filter_queryset(self, queryset):
        try:
            chat = Chat.objects.get(user=self.request.user, id=self.kwargs['chat_id'])
        except Chat.DoesNotExist:
            raise Http404

        return queryset.filter(chat_id=chat.id)


class CreateMessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = CreateMessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context['chat_id'] = self.kwargs.get('chat_id')
        context['user'] = self.request.user

        return context


class CreateMessageFileViewSet(CreateViewSet):
    queryset = MessageFile.objects.all()
    input_serializer_class = CreateMessageFileSerializer
    output_serializer_class = ListMessageFileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = []


class DownloadFileViewSet(ReadOnlyModelViewSet):
    queryset = MessageFile.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def retrieve(self, request, *args, **kwargs):
        doc = self.get_object()

        full_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)

        if os.path.exists(full_path):
            return FileResponse(open(full_path, 'rb'), as_attachment=True)

        raise Http404("File not found")
