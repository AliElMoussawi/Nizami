from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.subscription.models import UserSubscription
from src.subscription.serializers import UserSubscriptionSerializer, CreateUserSubscriptionSerializer, UpdateUserSubscriptionSerializer
from src.common.mixins import ForceDatatablesFormatMixin
from src.common.permissions import IsAdminPermission


class ListUserSubscriptionViewSet(ForceDatatablesFormatMixin, ReadOnlyModelViewSet):
    queryset = UserSubscription.objects.select_related('user', 'plan').all().order_by('-created_at')
    serializer_class = UserSubscriptionSerializer
    pagination_class = DatatablesPageNumberPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]
    lookup_field = 'uuid'

    def filter_queryset(self, queryset):
        is_active = self.request.data.get('is_active', None)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        search_term = self.request.data.get('search_term', None)
        if search_term is not None:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term) |
                Q(user__email__icontains=search_term) |
                Q(plan__name__icontains=search_term) |
                Q(uuid__icontains=search_term)
            )

        return queryset


class CreateUserSubscriptionViewSet(ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = CreateUserSubscriptionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        return UserSubscription.objects.none()  # Only allow create, not list/retrieve/update/delete


class UpdateUserSubscriptionViewSet(ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UpdateUserSubscriptionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]
    lookup_field = 'uuid'

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=True, *args, **kwargs)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def activate_subscription(request: Request, uuid):
    try:
        subscription = UserSubscription.objects.get(uuid=uuid)
    except UserSubscription.DoesNotExist:
        return Response({"error": "subscription_not_found"}, status=status.HTTP_404_NOT_FOUND)

    if subscription.is_active:
        return Response({"error": "subscription_already_active"}, status=status.HTTP_400_BAD_REQUEST)

    subscription.is_active = True
    subscription.deactivated_at = None
    subscription.save(update_fields=["is_active", "deactivated_at", "updated_at"])
    
    return Response({
        "message": f"Subscription successfully activated for user {subscription.user.email}",
        "subscription": UserSubscriptionSerializer(subscription).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def deactivate_subscription(request: Request, uuid):
    try:
        subscription = UserSubscription.objects.get(uuid=uuid)
    except UserSubscription.DoesNotExist:
        return Response({"error": "subscription_not_found"}, status=status.HTTP_404_NOT_FOUND)

    if not subscription.is_active:
        return Response({"error": "subscription_already_inactive"}, status=status.HTTP_400_BAD_REQUEST)

    subscription.is_active = False
    subscription.deactivated_at = timezone.now()
    subscription.save(update_fields=["is_active", "deactivated_at", "updated_at"])
    
    return Response({
        "message": f"Subscription successfully deactivated for user {subscription.user.email}",
        "subscription": UserSubscriptionSerializer(subscription).data
    }, status=status.HTTP_200_OK)


