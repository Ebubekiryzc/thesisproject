from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import generics, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.tasks import send_activation_email_task

from apps.account.models import User
from .serializers import LoginSerializer, RegisterSerializer, EmailVerificationSerializer, UserSerializer

from config import settings
import jwt


class UserView(mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = None


class RegisterView(mixins.CreateModelMixin,
                   GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    pagination_class = None

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            messages = serializer.errors
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        user_data = serializer.validated_data
        user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(self.request).domain
        relative_link = reverse('apps.account:email-verify')
        absolute_url = f"http://{current_site}{relative_link}?token={str(token)}"

        context = {
            "user": user.id,
            "link": absolute_url,
            "from_views": False
        }
        send_activation_email_task.delay(context)
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    pagination_class = None

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])

            id = payload['user_id']
            user = get_object_or_404(User, id=id)

            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
                return Response({'message': 'Email başarılı bir şekilde active edildi '}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Email zaten onaylanmış.'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activasyon kodu zaman aşımına uğradı'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Geçersiz aktivasyon kodu'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    pagination_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as errors:
            messages = serializer.errors
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)
