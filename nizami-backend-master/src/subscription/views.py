from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.subscription.models import UserSubscription
from src.subscription.serializers import UserSubscriptionSerializer
from src.common.pagination import PerPagePagination
from src.common.utils import send_subscription_cancelled_email


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def history(request: Request):
    queryset = UserSubscription.objects.filter(user=request.user).order_by('-created_at')

    paginator = PerPagePagination()
    page = paginator.paginate_queryset(queryset, request)

    serializer = UserSubscriptionSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
# API called on login and refresh - returns the current subscription credits, expiry date and everything...
def current_subscription(request: Request):
    try:
        # Get subscription that hasn't expired yet (active or deactivated)
        sub = UserSubscription.objects.filter(
            user=request.user, 
            expiry_date__gte=timezone.now()
        ).latest('created_at')
        
    except UserSubscription.DoesNotExist:
        return Response({"error": "no_active_user_subscription"}, status=status.HTTP_404_NOT_FOUND)
    except UserSubscription.MultipleObjectsReturned:
        return Response({"error": "multiple_active_subscriptions_found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = UserSubscriptionSerializer(sub)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def latest(request: Request):
    latest_sub = UserSubscription.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not latest_sub:
        return Response({"error": "no_user_subscription"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSubscriptionSerializer(latest_sub)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deactivate(request: Request):
    try:
        sub = UserSubscription.objects.get(user=request.user, is_active=True)
    except UserSubscription.DoesNotExist:
        return Response({"error": "no_active_user_subscription"}, status=status.HTTP_404_NOT_FOUND)
    except UserSubscription.MultipleObjectsReturned:
        return Response({"error": "multiple_active_subscriptions_found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Check if subscription is already expired
    if sub.expiry_date < timezone.now():
        return Response({"error": "subscription_already_expired"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Deactivate subscription (will remain active until expiry date but won't auto-renew)
    sub.is_active = False
    sub.deactivated_at = timezone.now()
    sub.save() 

    try:
        send_subscription_cancelled_email(request.user, sub, sub.plan)
    except Exception as e:
        print(f"Failed to send subscription cancellation email: {e}")

    return Response({
        "message": f"Subscription to plan '{sub.plan.name}' has been cancelled",
        "expiry_date": sub.expiry_date,
        "note": "Your subscription will remain accessible until the expiry date"
    }, status=status.HTTP_200_OK)

