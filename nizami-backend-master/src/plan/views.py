from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Plan
from src.subscription.models import UserSubscription
from src.plan.enums import Tier
from .serializers import ListPlanSerializer
from src.common.permissions import IsAdminPermission
from src.common.pagination import PerPagePagination


@api_view(['GET'])
@authentication_classes([])
def get(request: Request):
    queryset = Plan.objects.filter(is_deleted=False).order_by('-created_at')

    paginator = PerPagePagination()
    page = paginator.paginate_queryset(queryset, request)

    serializer = ListPlanSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@authentication_classes([])
def get_by_uuid(request: Request, uuid):
    try:
        plan = Plan.objects.get(uuid=uuid, is_deleted=False)
    except Plan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ListPlanSerializer(plan)
    return Response(serializer.data)

@api_view(['GET'])
def user_raw_plan(request: Request):
    try:
        sub = request.user.subscriptions.filter(is_active=True).select_related('plan').get()
    except UserSubscription.DoesNotExist:
        return Response({"error": "no_active_user_subscription"}, status=status.HTTP_404_NOT_FOUND)
    except UserSubscription.MultipleObjectsReturned:
        return Response({"error": "multiple_active_subscriptions_found"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serializer = ListPlanSerializer(sub.plan)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def deactivate(request: Request):
    plan_uuid = request.data.get('uuid')

    if not plan_uuid:
        return Response({"error": "uuid is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        plan = Plan.objects.get(uuid=plan_uuid)
    except Plan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

    if plan.is_deleted:
        return Response({"error": f"Plan already deactivated: {plan.name}"}, status=status.HTTP_400_BAD_REQUEST)

    plan.is_deleted = True
    plan.save(update_fields=["is_deleted", "updated_at"])
    return Response({"message": f"Plan successfully deactivated: {plan.name}"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def activate(request: Request):
    plan_uuid = request.data.get('uuid')

    if not plan_uuid:
        return Response({"error": "uuid is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        plan = Plan.objects.get(uuid=plan_uuid)
    except Plan.DoesNotExist:
        return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)

    if not plan.is_deleted:
        return Response({"error": f"Plan already activated: {plan.name}"}, status=status.HTTP_400_BAD_REQUEST)

    plan.is_deleted = False
    plan.save(update_fields=["is_deleted","updated_at"])
    return Response({"message": f"Plan successfully activated: {plan.name}"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def available_for_upgrade(request: Request):
    exclude_tiers = [Tier.BASIC]

    active_subscription = (
            UserSubscription.objects
            .filter(user=request.user, is_active=True)
            .select_related('plan').order_by()
            .first()
        )
    if active_subscription and active_subscription.plan and active_subscription.plan.tier:
        exclude_tiers.append(active_subscription.plan.tier)

    queryset = (
        Plan.objects
        .filter(is_deleted=False)
        .exclude(tier__in=exclude_tiers)
        .order_by('-created_at')
    )

    paginator = PerPagePagination()
    page = paginator.paginate_queryset(queryset, request)

    serializer = ListPlanSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
