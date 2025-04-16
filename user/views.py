# Django imports
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

# External imports
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

# Local imports
from .models import User
from .serializers import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    SigninSerializer,
    SignupSerializer,
)
from .utils import generate_token, is_otp_expired, send_email


class SignupViewSet(viewsets.ModelViewSet):
    serializer_class = SignupSerializer
    http_method_names = ["post"]


class SigninViewSet(viewsets.ModelViewSet):
    serializer_class = SigninSerializer
    http_method_names = ["post"]

    def login(self, request) -> Response:
        serializer = SigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            user = SigninSerializer(user)
            return Response(
                {"token": token.key, "data": user.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
            )

    def reset_password(self, request) -> Response:
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        password = serializer.validated_data["password"]

        user = get_object_or_404(User, email=email)

        if user.otp != otp and is_otp_expired(user.otp_expiration):
            return Response(
                {"error": "invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.save()
        return Response({"message": "password reset"}, status=status.HTTP_200_OK)

    def reset_request(self, request) -> Response:
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)

        otp, expiration_time = generate_token()
        user.otp = otp
        user.otp_expiration = expiration_time
        user.save()

        email_content = render_to_string("otp.html", {"user": user, "otp": otp})
        email_data = {
            "sender_email": settings.SENDER_EMAIL,
            "sender_password": settings.SENDER_PASSWORD,
            "receiver_email": user.email,
            "subject": "OTP Verification",
            "html": email_content,
        }

        success = send_email(email_data)
        if success:
            return Response(
                {"message": "OTP sent successfully!"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Failed to send OTP via email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
