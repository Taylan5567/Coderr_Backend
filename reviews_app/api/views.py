from .serializers import ReviewSerializer, ReviewUpdateSerializer
from reviews_app.models import Review
from rest_framework import filters, generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from userprofile_app.models import UserProfile
from offers_app.models import Offer




class ReviewsList(generics.ListCreateAPIView):
    """
    List and create reviews.

    GET:
        Returns a list of reviews. Supports ordering by "created_at", "rating",
        and "updated_at". You can filter the list with query parameters:

            - business_user_id: only reviews for this business user
            - reviewer_id: only reviews written by this reviewer

        Response: 200 OK
            [
              { ... review fields ... },
              ...
            ]

    POST:
        Creates a new review. The authenticated user must be a customer.
        The "reviewer" field is set automatically to the current user.

        Responses:
            201 Created: returns the created review
            400 Bad Request: invalid data
            403 Forbidden: not authenticated or not a customer
    """
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating', 'updated_at']
    def get_queryset(self):
        """
        Optionally filter the reviews by:
          - business_user_id (query param)
          - reviewer_id (query param)
        """
        queryset = Review.objects.all()

        business_user_id = self.request.query_params.get('business_user_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        reviewer_id = self.request.query_params.get('reviewer_id')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset

    def perform_create(self, serializer):
        """
        Set the reviewer to the current authenticated user when creating.
        """
        serializer.save(reviewer=self.request.user)

    def post(self, request, *args, **kwargs):
        """
        Create a new review.

        Requirements:
            - user must be authenticated AND must be of type 'customer'.

        Returns:
            201 with created review on success, or appropriate error response.
        """
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        
        if not request.user.is_authenticated or request.user.type != 'customer':
            return Response({"error": "You must be logged or be a customer to create a review."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single review.

    Permissions:
        - The user must be authenticated.

    PATCH:
        Partially update fields of your own review.

    DELETE:
        Permanently remove your own review.
    """
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    
    def patch(self, request, id):
        """
        Partially update a review.

        Only the user who created the review (reviewer) may update it.
        """
        review = get_object_or_404(Review, id=id)
        data = request.data.copy()
        serializer = ReviewSerializer(review, data=data, partial=True, context={'request': request})

        reviewer = review.reviewer

        if not reviewer.id == request.user.id:
            return Response({"error": "You can only update your own review."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save(reviewer=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        """
        Delete a review.

        Only the user who created the review (reviewer) may delete it.
        """
        review = get_object_or_404(Review, id=id)
        reviewer = review.reviewer

        if not reviewer.id == request.user.id:
            return Response({"error": "You can only delete your own review."}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class BaseInformationView(generics.ListAPIView):
    """
    Public endpoint that returns aggregated review and marketplace statistics.

    GET:
        Returns a JSON object with:
            - review_count: total number of reviews
            - average_count: average rating across all reviews (0 if none)
            - business_profile_count: number of users with type 'business'
            - offer_count: total number of offers

        Response: 200 OK
            {
              "review_count": <int>,
              "average_count": <float>,
              "business_profile_count": <int>,
              "offer_count": <int>
            }
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Compute and return aggregate metrics for reviews and marketplace entities.
        """
        review_count = Review.objects.count()
        average_count = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        business_count = UserProfile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()
        
        return Response({'review_count': review_count, 'average_rating': average_count, 'business_profile_count': business_count, 'offer_count': offer_count}, status=status.HTTP_200_OK)