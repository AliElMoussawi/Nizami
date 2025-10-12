from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from src.subscription.models import UserSubscription
from src.subscription.serializers import UserSubscriptionSerializer
from src.common.pagination import PerPagePagination


@api_view(['GET'])
def history(request: Request):
    queryset = UserSubscription.objects.filter(user=request.user).order_by('-created_at')

    paginator = PerPagePagination()
    page = paginator.paginate_queryset(queryset, request)

    serializer = UserSubscriptionSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def active(request: Request):
    try:
        sub = UserSubscription.objects.get(user=request.user, is_active=True)
    except UserSubscription.DoesNotExist:
        return Response({"error": "no_active_user_subscription"}, status=status.HTTP_404_NOT_FOUND)
    except UserSubscription.MultipleObjectsReturned:
        return Response({"error": "multiple_active_subscriptions_found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = UserSubscriptionSerializer(sub)
    return Response(serializer.data)


@api_view(['POST'])
def deactivate(request: Request):
    try:
        sub = UserSubscription.objects.get(user=request.user, is_active=True)
    except UserSubscription.DoesNotExist:
        return Response({"error": "no_active_user_subscription"}, status=status.HTTP_404_NOT_FOUND)
    except UserSubscription.MultipleObjectsReturned:
        return Response({"error": "multiple_active_subscriptions_found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if sub.expiry_date > timezone.now():
        return Response({"error": "subscription_already_expired"}, status=status.HTTP_400_BAD_REQUEST)
    sub.is_active = False
    sub.deactivated_at = timezone.now()
    sub.save() 

    return Response({"message": f"Subscription successfully deactivated to plan: {sub.plan.name}"}, status=status.HTTP_200_OK)

