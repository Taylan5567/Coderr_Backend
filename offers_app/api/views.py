from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from offers_app.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferUpdateSerializer, OfferCreateSerializer, OneOfferDetailSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework import filters
from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError



class PageNumberSetPagination(PageNumberPagination):
    """
    Custom pagination class to set the page size to 5 and limit the maximum page size to 5.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5

class OfferListView(generics.ListCreateAPIView):
    """
    View for listing and creating offers.

    This view allows authenticated users to list and create offers.

    Attributes:
        queryset (QuerySet): The queryset of offers to retrieve.
        serializer_class (Serializer): The serializer class used for serialization.
        pagination_class (Pagination): The pagination class used for pagination.
        filter_backends (list): The list of filter backends used for filtering.
        search_fields (list): The list of fields to search for in offers.
        ordering_fields (list): The list of fields to order offers by.
    
    """
    permission_classes = [AllowAny]
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = PageNumberSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at', 'min_price']

    def get_serializer_class(self):
        """
        Determine the serializer class based on the request method.
        """
        return OfferCreateSerializer if self.request.method == 'POST' else OfferSerializer

    def get_queryset(self):
        """
        Get the queryset of offers based on query parameters.
        """
        queryset = Offer.objects.annotate(
            min_price=Min('details__price'),
            delivery_time_in_days=Min('details__delivery_time_in_days'),
        )

        queryset = queryset.annotate(min_price=Min('details__price'))

        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        min_price_param = self.request.query_params.get('min_price', None)
        if min_price_param:
            try:
                min_price_val = int(min_price_param)
            except:
                raise ValidationError({"min_price": "min_price has to be a number"})
            queryset = queryset.filter(min_price__gte=min_price_val)
        
        min_delivery_time_param = self.request.query_params.get('min_delivery_time', None)
        if min_delivery_time_param:
            try:
                min_delivery_time_val = int(min_delivery_time_param)
            except:
                raise ValidationError({"min_delivery_time": "min_delivery_time has to be a number"})
            queryset = queryset.filter(delivery_time_in_days__gte=min_delivery_time_val)
        
        return queryset.distinct()
    

    def get_permissions_classes(self,request):
        if request.method == 'POST':
            return [AllowAny()]
        elif request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsAuthenticated()]
        return super().get_permissions(request)

    def post(self, request):
        """
        Create a new offer.

        """
        user = request.user
        serializer = OfferCreateSerializer(data=request.data, context={'request': request})
        
        if not getattr(user, 'is_authenticated', False) or getattr(user, 'type', None) != 'business':
            return Response({"error": "Only business users can create offers."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferDetailsView(generics.RetrieveAPIView):
    """
    View for retrieving details of an offer.

    This view allows authenticated users to retrieve details of an offer.

    Attributes:
        queryset (QuerySet): The queryset of offers to retrieve.
        serializer_class (Serializer): The serializer class used for serialization.
        permission_classes (list): The list of permission classes used for authentication.
        lookup_url_kwarg (str): The name of the URL keyword argument used for the offer ID.
    
    """
    serializer_class = OfferSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'id' 

    def get_serializer_class(self):
        """
        Determine the serializer class based on the request method.
        """
        return OfferUpdateSerializer if self.request.method in ('PATCH', 'PUT') else OfferSerializer

    def get_queryset(self):
        """
        Get the queryset of offers based on query parameters.
        """
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            delivery_time_in_days=Min('details__delivery_time_in_days'),
        )    
    
    def patch(self, request, id):
        """
        Update an existing offer.

        """
        offer = get_object_or_404(Offer, id=id)
        user = request.user
        data = request.data.copy()

        is_owner = offer.user_id == user.id

        if not is_owner:
            return Response({"error": "You are not the owner of this offer."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OfferUpdateSerializer(offer, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        """
        Delete an existing offer.

        """
        offer = get_object_or_404(Offer, id=id)
        user = request.user
        data = request.data.copy()

        is_owner = offer.user_id == user.id

        if not is_owner:
            return Response({"error": "You are not the owner of this offer."}, status=status.HTTP_401_UNAUTHORIZED)

        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OneOfferDetailsView(generics.RetrieveAPIView):
    """
    View for retrieving details of a specific offer.

    This view allows authenticated users to retrieve details of a specific offer.

    Attributes:
        queryset (QuerySet): The queryset of offer details to retrieve.
        serializer_class (Serializer): The serializer class used for serialization.
        permission_classes (list): The list of permission classes used for authentication.
        lookup_field (str): The name of the field used for the offer detail ID.
        lookup_url_kwarg (str): The name of the URL keyword argument used for the offer detail ID.
    
    """
    permission_classes = [AllowAny]
    queryset = OfferDetail.objects.all()
    serializer_class = OneOfferDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        """
        Get the queryset of offer details based on query parameters.
        """
        queryset = super().get_queryset()
        return queryset
    
    