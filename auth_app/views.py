from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer
from django.contrib.auth import get_user_model

class RegistrationView(APIView):
    """
    API endpoint for user registration.
    
    POST: Registers a new user and returns an authentication token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user registration.

        Returns:
            201: User created successfully, returns token and user data.
            400: Validation failed.
            500: Internal server error.
        """
        try:
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                saved_account = serializer.save()
                token, _ = Token.objects.get_or_create(user=saved_account)

                data = {
                    'token': token.key,
                    'email': saved_account.email,
                    'username': saved_account.username,
                    'user_id': saved_account.id
                }
                return Response(data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(ObtainAuthToken):
    """
    API endpoint for user login using email and password.
    
    POST: Authenticates a user and returns an authentication token.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle user login via email and password.

        Returns:
            200: Login successful, returns token and user info.
            400: Email/password invalid or not provided.
            500: Internal server error.
        """
        try:
            data = request.data.copy()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return Response(
                    {'error': 'Username and password are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            User = get_user_model()

            try:
                user = User.objects.get(username=username)
                data['username'] = user.username
            except User.DoesNotExist:
                return Response(
                    {'error': 'User does not exist.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.serializer_class(
                data=data,
                context={'request': request}
            )

            if serializer.is_valid():
                user = serializer.validated_data['user']
                token, _ = Token.objects.get_or_create(user=user)

                return Response({
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.id
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
