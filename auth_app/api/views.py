from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from userprofile_app.models import UserProfile




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
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                user.set_password(serializer.validated_data['password'])
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
                
                data = {
                    'token': token.key,
                    'email': user.email,
                    'username': user.username,
                    'user_id': user.id,
                    'type': user.type
                }
                return Response(data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(ObtainAuthToken):
    """
    API endpoint for user login using email and password.
    
    POST: Authenticates a user and returns an authentication token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_200_OK)