from django.contrib.auth import password_validation, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from src.users.serializers import UserSerializer, ProfileSerializer, UpdateProfileSerializer
from .serializers import PasswordResetSerializer, UpdatePasswordSerializer, RegisterSerializer
from .. import settings
from ..common.throttles import ForgotPasswordThrottle
from ..common.utils import send_welcome_mail
from ..users.models import User


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects.filter(email__iexact=email.lower()).first()

    if user and user.check_password(password):
        access = AccessToken.for_user(user)

        return Response({
            'access_token': str(access),
            'user': UserSerializer(user).data,
        })
    return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register(request: Request):
    request.data._mutable = True

    request.data.update({
        'username': request.data.get('email', None),
    })

    request.data._mutable = False

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        send_welcome_mail(serializer.instance)

        token = AccessToken.for_user(serializer.instance)

        return Response({
            'user': serializer.data,
            'access_token': str(token),
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@throttle_classes([ForgotPasswordThrottle])
def forgot_password(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email__iexact=email.lower())
    except User.DoesNotExist:
        return Response({"error": "Email not found!"}, status=status.HTTP_400_BAD_REQUEST)

    token = default_token_generator.make_token(user)

    reset_link = f"{settings.FRONTEND_DOMAIN}/{settings.FRONTEND_RESET_PASSWORD_TEMPLATE}".replace("<TOKEN>", token)

    subject = 'Password Reset'

    message = render_to_string(
        'password_reset_email.html',
        context={
            'reset_link': reset_link,
            'user': user,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [email],
        fail_silently=False,
        html_message=message
    )

    return Response({"message": "Password reset email sent!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    try:
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = User.objects.filter(email__iexact=email.lower()).first()

        if not user or not default_token_generator.check_token(user, serializer.data.get('token')):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        password_validation.validate_password(password, user)

        new_password = request.data.get('password')
        user.set_password(new_password)
        user.save()

        response = {
            "message": "Password updated successfully!",
            "access_token": str(AccessToken.for_user(user)),
            'user': UserSerializer(user).data,
        }

        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_profile(request):
    return Response(
        ProfileSerializer(request.user).data,
    )


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)

    if serializer.is_valid():
        if not request.data.get('profile_image'):
            serializer.validated_data['profile_image'] = request.user.profile_image

        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_password(request):
    serializer = UpdatePasswordSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        update_session_auth_hash(request, request.user)  # Keep user logged in after password change
        return Response({'message': 'Password updated successfully!'})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
