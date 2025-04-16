# Python imports
from typing import Dict

# External imports
from rest_framework import serializers

# App imports
from user.models import User

# Local imports
from .logger import UserLogger as Logger


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        )
        read_only_fields = ("id",)

    def validate(self, attrs: Dict[str, str]) -> Dict[str, str]:
        if attrs["password"] != attrs["confirm_password"]:
            Logger.info(
                {
                    "message": "Both password didn't match.",
                    "event": "signup_validate",
                    "user": attrs,
                }
            )
            raise serializers.ValidationError(
                {"password": "both password didn't match."}
            )
        return attrs

    def create(self, validated_data: Dict[str, str]) -> User:
        user = User(
            username=validated_data.get("email"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )
        user.save()
        user.set_password(validated_data.get("password"))
        user.save()
        Logger.info(
            {
                "message": "User created successfully.",
                "event": "signup_create",
                "user": user,
            }
        )
        return user


class SigninSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name")
        read_only_fields = ("id", "first_name", "last_name")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data: Dict[str, str]) -> Dict[str, str]:
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            Logger.info(
                {
                    "message": "Both password didn't match.",
                    "event": "reset_password_validate",
                }
            )
            raise serializers.ValidationError("Both password did not match ! ")

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
