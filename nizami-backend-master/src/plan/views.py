from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Plan
from src.subscription.models import UserSubscription
from src.plan.enums import Tier
from .serializers import ListPlanSerializer, CreateUpdatePlanSerializer
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
        return Response({"error": "plan_not_found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ListPlanSerializer(plan)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def admin_list(request: Request):
    queryset = Plan.objects.all().order_by('-created_at')

    paginator = PerPagePagination()
    page = paginator.paginate_queryset(queryset, request)

    serializer = ListPlanSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def admin_create(request: Request):
    serializer = CreateUpdatePlanSerializer(data=request.data)
    if serializer.is_valid():
        plan = serializer.save()
        return Response(ListPlanSerializer(plan).data, status=status.HTTP_201_CREATED)
    return Response({
        "error": "validation_error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def admin_update(request: Request, uuid):
    try:
        plan = Plan.objects.get(uuid=uuid)
    except Plan.DoesNotExist:
        return Response({"error": "plan_not_found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(ListPlanSerializer(plan).data)

    partial = request.method == 'PATCH'
    serializer = CreateUpdatePlanSerializer(plan, data=request.data, partial=partial)
    if serializer.is_valid():
        plan = serializer.save()
        return Response(ListPlanSerializer(plan).data)
    return Response({
        "error": "validation_error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
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
        return Response({"error": "plan_not_found"}, status=status.HTTP_404_NOT_FOUND)

    if plan.is_deleted:
        return Response({"error": "plan_already_deactivated"}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"error": "plan_already_activated"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if there's already an active plan with the same tier
    existing_active_plan = Plan.objects.filter(
        tier=plan.tier,
        is_deleted=False,
        is_active=True
    ).exclude(uuid=plan.uuid).first()

    if existing_active_plan:
        return Response({
            "error": "duplicate_tier_active",
            "message": f"Cannot activate plan '{plan.name}' because there is already an active plan with the same tier ({plan.tier}): '{existing_active_plan.name}'",
            "existing_plan": {
                "name": existing_active_plan.name,
                "tier": existing_active_plan.tier,
                "uuid": str(existing_active_plan.uuid)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    plan.is_deleted = False
    plan.save(update_fields=["is_deleted","updated_at"])
    return Response({"message": f"Plan successfully activated: {plan.name}"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def available_for_upgrade(request: Request):
    exclude_tiers = [Tier.BASIC]

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
