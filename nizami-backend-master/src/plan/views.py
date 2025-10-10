from django.shortcuts import render
from django.contrib.auth import password_validation, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from .models import Plan
from .serializers import ListPlanSerializer
from src.common.permissions import IsAdminPermission
from src.common.pagination import PerPagePagination
from rest_framework.viewsets import ReadOnlyModelViewSet


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


