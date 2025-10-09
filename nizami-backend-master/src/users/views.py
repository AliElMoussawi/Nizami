from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.users.serializers import UserSerializer, UpdateUserPasswordSerializer, UpdateUserSerializer, \
    CreateUserSerializer, UpdateUserStatusSerializer
from .models import User
from ..common.mixins import ForceDatatablesFormatMixin
from ..common.permissions import IsAdminPermission


class ListUserViewSet(ForceDatatablesFormatMixin, ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    pagination_class = DatatablesPageNumberPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def filter_queryset(self, queryset):
        is_active = self.request.data.get('is_active', None)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        search_term = self.request.data.get('search_term', None)
        if search_term is not None:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(company_name__icontains=search_term)
            )

        return queryset


class CreateDeleteUserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]


class UpdateUserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=True, *args, **kwargs)


class UpdateUserStatusViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UpdateUserStatusSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]


class UpdateUserPasswordViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UpdateUserPasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]
