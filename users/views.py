from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
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
        return Response({
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

        # Теперь возвращаем refresh прямо в теле ответа
        return Response({
            "user": user_data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CookieTokenRefreshView(TokenRefreshView):
    """
    Теперь этот класс работает стандартно: ожидает 'refresh' в теле POST-запроса
    """
    def post(self, request, *args, **kwargs):
        # Стандартный TokenRefreshView уже умеет брать 'refresh' из request.data
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # При использовании localStorage серверу не нужно удалять куки.
        # Просто подтверждаем выход.
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)