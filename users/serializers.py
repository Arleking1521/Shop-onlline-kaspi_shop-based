from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('phone', 'username', 'first_name', 'last_name', 'date_of_birth', 'address', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # важно: хеш
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        # authenticate ожидает keyword с именем USERNAME_FIELD (т.е. phone)
        user = authenticate(self.context['request'], phone=phone, password=password)
        if not user:
            raise serializers.ValidationError("Неверный номер телефона или пароль")
        if not user.is_active:
            raise serializers.ValidationError("Пользователь деактивирован")

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'image', 'phone', 'first_name', 'last_name'] # Только публичные данные