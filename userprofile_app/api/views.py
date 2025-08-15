from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from userprofile_app.models import UserProfile

from .serializers import ProfileSerializer, ProfilePatchSerializer, ProfileDetailsSerializer

class ProfileDetailView(APIView):
    """
    Retrieve or update a single user profile.

    GET /api/profiles/<pk>/:
        Returns the profile data for the given primary key.

        Response: 200 OK
            {
              "user": <int>,
              "username": "...",
              "first_name": "...",
              "last_name": "...",
              "file": "...",
              "location": "...",
              "tel": "...",
              "description": "...",
              "working_hours": "...",
              "type": "...",
              "email": "...",
              "created_at": "..."
            }

    PATCH /api/profiles/<pk>/:
        Partially updates the profile. Only the owner of the profile may
        update it (pk must equal the current user's id). Fields are validated
        and then saved using ProfilePatchSerializer.

        Responses:
            200 OK: returns the updated profile data
            403 Forbidden: if the current user does not own this profile
            404 Not Found: if the profile does not exist
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        Retrieve and return the profile identified by pk.
        """
        serializer = ProfileSerializer(UserProfile.objects.get(pk=pk), context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        """
        Partially update the profile identified by pk.

        Only the owner of the profile (current user's id equals pk) is allowed
        to perform the update. Other users receive a 403 response.
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        data = request.data.copy()

        if pk != request.user.id:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfilePatchSerializer(
            profile, data=data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(
                ProfilePatchSerializer(updated_profile, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessView(APIView):
    """
    List all profiles with type 'business'.

    GET /api/profiles/business/:
        Returns an array of business profiles. The endpoint requires
        authentication (IsAuthenticated).

        Response: 200 OK
            [
              { ...profile fields... },
              ...
            ]
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        business = UserProfile.objects.filter(type='business').distinct()
        serializer = ProfileDetailsSerializer(business, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        """
        Partially update the profile identified by pk.

        Only the owner of the profile (current user's id equals pk) is allowed
        to perform the update. Other users receive a 403 response.
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        data = request.data.copy()

        if pk != request.user.id:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfilePatchSerializer(
            profile, data=data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(
                ProfilePatchSerializer(updated_profile, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerView(APIView):
    """
    List all profiles with type 'customer'.

    GET /api/profiles/customers/:
        Returns an array of customer profiles. The endpoint requires
        authentication (IsAuthenticated).

        Response: 200 OK
            [
              { ...profile fields... },
              ...
            ]
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        customer = UserProfile.objects.filter(type='customer').distinct()
        serializer = ProfileDetailsSerializer(customer, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    def patch(self, request, pk):
        """
        Partially update the profile identified by pk.

        Only the owner of the profile (current user's id equals pk) is allowed
        to perform the update. Other users receive a 403 response.
        """
        profile = get_object_or_404(UserProfile, pk=pk)
        data = request.data.copy()

        if pk != request.user.id:
            return Response({"error": "You can only update your own profile."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProfilePatchSerializer(
            profile, data=data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            updated_profile = serializer.save()
            return Response(
                ProfilePatchSerializer(updated_profile, context={'request': request}).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)