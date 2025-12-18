# accounts/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.http import JsonResponse

from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data

        # 1. Создаем объект ответа БЕЗ refresh в теле JSON
        response = JsonResponse({
            "user": user_data,
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

        # 2. Устанавливаем refresh_token в HttpOnly Cookie
        response.set_cookie(
            key='refresh_token', 
            value=str(refresh),
            httponly=True,   # ГЛАВНОЕ: JS не увидит эту куку
            secure=False,    # Поставьте True, если используете HTTPS (в продакшене обязательно)
            samesite='Lax',  # Защита от CSRF
            max_age=7 * 24 * 60 * 60 # Срок жизни (например, 7 дней)
        )
        
        return response
