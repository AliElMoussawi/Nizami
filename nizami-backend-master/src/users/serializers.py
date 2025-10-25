from rest_framework import serializers

from src.common.utils import send_welcome_with_password_message
from src.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'profile_image',
            'date_of_birth',
            'country',
            'job_title',
            'company_name',
            'role',
            'language',
            'date_joined',
            'is_active',
            'full_name',
        )

    id = serializers.IntegerField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    job_title = serializers.CharField(allow_null=True, allow_blank=True)
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'profile_image',
            'date_of_birth',
            'job_title',
            'company_name',
            'role',
            'date_joined',
        )

    id = serializers.IntegerField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    job_title = serializers.CharField(allow_null=True, allow_blank=True)

    def create(self, validated_data):
        password = User.objects.make_random_password(length=16)

        user = User.objects.create_user(
            username=validated_data['email'],
            role='user',
            password=password,
            country='sa',
            **validated_data,
        )

        send_welcome_with_password_message(user, password)

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined']


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'country', 'date_of_birth', 'profile_image', 'job_title', 'company_name', 'language']

    profile_image = serializers.ImageField(required=False, allow_null=True)


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'country',
            'date_of_birth',
            'profile_image',
            'job_title',
            'company_name',
            'language',
        ]

    profile_image = serializers.ImageField(required=False, allow_null=True)


class UpdateUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active']


class UpdateUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=1, write_only=True)

    def update(self, instance, validated_data):
        instance.set_password(raw_password=validated_data.get('new_password'))

        instance.save()

        return instance
