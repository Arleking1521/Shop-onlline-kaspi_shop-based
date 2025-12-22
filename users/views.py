# accounts/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import generics

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            "user": {
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "image": user.image.url if user.image else None,
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

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ← чтобы менять аватар

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return JsonResponse(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True  # ← можно обновлять не все поля
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if refresh_token:
            mutable_data = request.data.copy()
            mutable_data['refresh'] = refresh_token
            serializer = self.get_serializer(data=mutable_data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        return Response({"detail": "Refresh token cookie missing"}, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token", path="/") 
        return response
