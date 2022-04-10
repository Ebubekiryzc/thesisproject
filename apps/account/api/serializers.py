from apps.account.models import User
from django.contrib import auth
from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    products_added_to_wishlist = serializers.StringRelatedField(
        read_only=True, many=True)

    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=4, write_only=True, )

    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            "email": {
                "validators": [
                    EmailValidator,
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="This email already exist!"
                    )
                ]
            }
        }

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                'Kullanıcı adı sadece rakamlardan oluşamaz.')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=4, write_only=True)
    email = serializers.EmailField(
        max_length=255, min_length=3, read_only=True)
    tokens = serializers.CharField(max_length=68, min_length=6, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed(
                "Geçersiz değer girdiniz. Lütfen tekrar deneyiniz.")
        if not user.is_active:
            raise AuthenticationFailed("Hesap aktif değil.")
        if not user.is_email_verified:
            raise AuthenticationFailed("Email onaylanmamış.")

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']
