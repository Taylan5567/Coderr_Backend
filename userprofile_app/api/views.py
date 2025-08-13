from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from userprofile_app.models import UserProfile

from .serializers import ProfileSerializer, ProfilePatchSerializer, ProfileDetailsSerializer

class ProfileDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        serializer = ProfileSerializer(UserProfile.objects.get(pk=pk), context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
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
    permission_classes = [IsAuthenticated]
    def get(self, request):
        business = UserProfile.objects.filter(type='business').distinct()
        serializer = ProfileDetailsSerializer(business, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class CustomerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        customer = UserProfile.objects.filter(type='customer').distinct()
        serializer = ProfileDetailsSerializer(customer, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

