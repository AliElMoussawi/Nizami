from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Prompt
from .serializers import ListPromptSerializer, UpdatePromptSerializer
from ..common.permissions import IsAdminPermission


class ListPromptViewSet(ReadOnlyModelViewSet):
    queryset = Prompt.objects.all().order_by('created_at')
    serializer_class = ListPromptSerializer
    pagination_class = None
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]


class UpdatePromptViewSet(ModelViewSet):
    queryset = Prompt.objects.all()
    serializer_class = UpdatePromptSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]
