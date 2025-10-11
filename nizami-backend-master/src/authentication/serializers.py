from rest_framework import serializers

from django.db import transaction
from src.users.models import User


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True)


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user

        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
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
            'password',
            'username',
        )

    id = serializers.IntegerField(read_only=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        with transaction.atomic():
            return User.objects.create_user(**validated_data)
